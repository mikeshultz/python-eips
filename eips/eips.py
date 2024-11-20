"""EIPs and ERCs ETL machinery."""

from abc import abstractmethod
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

from dulwich.objects import Commit as DulwichCommit
from dulwich.repo import Repo
from pydantic import ValidationError

from eips.const import DATA_PATH, ENCODING, IGNORE_FILES, REPO_DIR
from eips.enum import EIP1Category, EIP1Status, EIP1Type
from eips.git import ensure_repo_updated, git_commit_history, git_history
from eips.logging import get_logger
from eips.object import EIP, ERC, CommitHash, CommitRef, EIP1Document, EIPsStats, FlexId
from eips.util import doc_id_from_file, gitstamp_to_dt

log = get_logger(__name__)


def is_doc_file(f: Path) -> bool:
    """Is the given Path an design doc file?"""
    return f.name.endswith(".md") and f.name not in IGNORE_FILES


def filter_doc_files(fdir: Path) -> list[Path]:
    """Return a list of Ethereum design files in the given directory."""
    return list(filter(is_doc_file, fdir.iterdir()))


class EthereumDocs:
    """Ethereum Docs ETL machinery"""

    def __init__(
        self,
        freshness: timedelta | None,
        repo: str,
        workdir: Path,
    ):
        """Initialize an Ethereum design document object."""
        self.freshness = freshness
        self.repo = repo
        self.workdir = workdir
        self.repo_path = self.workdir.joinpath(REPO_DIR)
        self.docs_dir = self.repo_path.joinpath("docs")

        self._last_fetch: datetime = datetime(year=1970, month=1, day=1, tzinfo=UTC)
        self._current_commit: CommitHash | None = None

    def __getitem__(self, eip_id: int) -> EIP1Document | None:
        """Return an EIP-1 document by ID."""
        e = self.get(eip_id)
        return e[0] if len(e) else None

    def __len__(self) -> int:
        """Return the total number of documents."""
        return self.len()

    def __iter__(self) -> Iterator[EIP1Document]:
        """Iterate over all documents."""
        yield from self.get()

    @property
    def current_commit(self) -> CommitHash | None:
        """Return the current commit hash of the local document repo."""
        return self._current_commit

    @property
    def last_fetch(self) -> datetime:
        """Return the last time the repo was fetched."""
        return self._last_fetch

    @property
    def git_repo(self) -> Repo:
        """The Dulwich Git repo."""
        return Repo(str(self.repo_path))

    @property
    def _files(self) -> list[Path]:
        try:
            return filter_doc_files(self.docs_dir)
        except FileNotFoundError:
            return []

    def check(
        self,
        doc_id: FlexId | None = None,
        *,
        commit: CommitRef | None = None,
    ) -> bool:
        """Check if all documents are valid."""
        return all(doc.is_valid for doc in self.get(doc_id, commit=commit))

    @abstractmethod
    def get(
        self,
        doc_id: FlexId | None = None,
        *,
        commit: CommitRef | None = None,
    ) -> Sequence[EIP1Document]:
        """Return document(s) by ID(s)."""
        pass

    @abstractmethod
    def all(
        self, until_commit: CommitHash | None = None
    ) -> Iterator[tuple[DulwichCommit, EIP1Document]]:
        """Return history of EIP documents in reverse order until until_commit."""
        pass

    def _get_doc_commits(self, doc_id: int) -> Sequence[DulwichCommit]:
        subdir = self.docs_dir.relative_to(self.repo_path)
        return git_commit_history(
            self.repo_path, [str(subdir.joinpath(f"{doc_id}.md"))]
        )

    def _get_doc_history(self, doc_id: int) -> Sequence[DulwichCommit]:
        subdir = self.docs_dir.relative_to(self.repo_path)
        return git_history(self.repo_path, [str(subdir.joinpath(f"{doc_id}.md"))])

    def _get_doc(
        self,
        doc_id: FlexId | None = None,
        commit: CommitRef | None = None,
    ) -> list[Path]:
        if commit is not None:
            raise NotImplementedError("commit seeking not implemented")

        if doc_id is None or (isinstance(doc_id, list) and len(doc_id) == 0):
            # Return all docs
            return self._files
            # return [
            #     EIP.parse(current_commit, fil.read_text()) for fil in self._files
            # ]
        elif isinstance(doc_id, int):
            doc_id = [doc_id]

        assert isinstance(doc_id, list)

        def is_match(f: Path) -> bool:
            return doc_id_from_file(f.name) in doc_id

        return list(filter(is_match, self._files))

    def len(self) -> int:
        """Total EIPs in the repo"""
        return len(self._files)

    def commits(
        self, until_commit: CommitHash | None = None
    ) -> Iterator[DulwichCommit]:
        """Return a commits history for the repo."""
        for commit in git_commit_history(self.repo_path):
            if commit.id == until_commit:
                break
            yield commit

    def history(
        self, until_commit: CommitHash | None = None
    ) -> Iterator[DulwichCommit]:
        """Return the history for the repo."""
        for commit in git_history(self.repo_path):
            if commit.id == until_commit:
                break
            yield commit

    def logs(self) -> list[str]:
        """Return commit messages for the given EIP"""
        raise NotImplementedError("TODO")

    def repo_fetch(self) -> CommitHash:
        """Fetch (or clone) an EIPs repo"""
        self._last_fetch = datetime.now(tz=UTC)
        self._current_commit = ensure_repo_updated(self.repo_path, self.repo)
        return self._current_commit

    def stats(self, commit: CommitRef | None = None) -> EIPsStats:
        """Return some aggregate data based on EIP files"""
        categories: list[EIP1Category] = []
        statuses: list[EIP1Status] = []
        types: list[EIP1Type] = []

        for eip in self.get():
            if eip.category not in categories and eip.category is not None:
                categories.append(eip.category)
            if eip.status not in statuses:
                statuses.append(eip.status)
            if eip.type and eip.type not in types:
                types.append(eip.type)

        return EIPsStats(
            # TODO: Errors should be something real.
            errors=0,
            categories=categories,
            statuses=statuses,
            total=self.len(),
            types=types,
        )

    @property
    def _should_autofetch(self) -> bool:
        """Should the repo be automatically updated?"""
        if self.freshness is None:
            return False
        return (datetime.now(tz=UTC) - self.last_fetch) > self.freshness

    def _all(
        self, doc_class: type[EIP1Document], until_commit: CommitHash | None = None
    ) -> Iterator[tuple[DulwichCommit, EIP1Document]]:
        for entry in git_history(self.repo_path):
            commit_id = CommitHash(entry.commit.id.decode(ENCODING))
            if commit_id == until_commit:
                break

            def _changes():
                # flatten the changes
                for change in entry.changes():
                    if isinstance(change, list):
                        yield from change
                    else:
                        yield change

            for change in _changes():
                # Not additive, skip
                if not (change.new and change.new.path):
                    continue

                doc_id = doc_id_from_file(Path(change.new.path.decode(ENCODING)).name)

                # Not a design doc, skip
                if doc_id < 1:
                    continue

                # TODO: Handle deleted docs

                commit_time = gitstamp_to_dt(
                    entry.commit.commit_time, entry.commit.commit_timezone
                )
                try:
                    doc_body = self.git_repo.get_object(change.new.sha).data.decode(
                        ENCODING
                    )
                except UnicodeDecodeError as err:
                    raise err

                try:
                    yield (
                        entry.commit,
                        doc_class.parse(doc_id, commit_id, commit_time, doc_body),
                    )
                except ValidationError:
                    log.exception(
                        f"Failed to parse document (id: {doc_id})"
                        f" (commit: {commit_id})"
                    )


class EIPs(EthereumDocs):
    """EIPs ETL machinery"""

    def __init__(
        self,
        freshness: timedelta | None = timedelta(seconds=60),
        repo: str = "https://github.com/ethereum/EIPs.git",
        workdir: Path = Path(DATA_PATH).expanduser().resolve().joinpath("eips"),
    ):
        """Initialize an EIPs ETL processor."""
        super().__init__(freshness, repo, workdir)
        self.docs_dir = self.repo_path.joinpath("EIPS")

    def get(
        self,
        doc_id: FlexId | None = None,
        *,
        commit: CommitRef | None = None,
    ) -> Sequence[EIP]:
        """Return EIP(s) by ID(s)."""
        if self._should_autofetch:
            self.repo_fetch()

        # NOTE: the act of fetching above should ensure this is set
        assert self.current_commit

        # TODO: Update this for parse() changes
        return [
            EIP.parse(self.current_commit, fil.read_text())
            for fil in self._get_doc(doc_id, commit)
        ]

    def all(
        self, until_commit: CommitHash | None = None
    ) -> Iterator[tuple[DulwichCommit, EIP1Document]]:
        """Return all EIP(s) versions by ID(s)."""
        return self._all(EIP, until_commit)


class ERCs(EthereumDocs):
    """ERCs ETL machinery"""

    def __init__(
        self,
        freshness: timedelta | None = timedelta(seconds=60),
        repo: str = "https://github.com/ethereum/ERCs.git",
        workdir: Path = Path(DATA_PATH).expanduser().resolve().joinpath("ercs"),
    ):
        """Initialize an ERCs ETL processor."""
        super().__init__(freshness, repo, workdir)
        self.docs_dir = self.repo_path.joinpath("ERCS")

    def get(
        self,
        doc_id: FlexId | None = None,
        *,
        commit: CommitRef | None = None,
    ) -> Sequence[ERC]:
        """Return ERC(s) by ID(s)"""
        if self._should_autofetch:
            self.repo_fetch()

        # NOTE: the act of fetching above should ensure this is set
        assert self.current_commit

        # TODO: Update this for parse() changes
        return [
            ERC.parse(self.current_commit, fil.read_text())
            for fil in self._get_doc(doc_id, commit)
        ]

    def all(
        self, until_commit: CommitHash | None = None
    ) -> Iterator[tuple[DulwichCommit, EIP1Document]]:
        """Return all EIP(s) versions by ID(s)."""
        return self._all(ERC, until_commit)
