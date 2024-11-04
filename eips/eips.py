"""EIPs and ERCs ETL machinery."""

from abc import abstractmethod
from collections.abc import Iterator, Sequence
from datetime import timedelta
from pathlib import Path

from eips.const import DATA_PATH, IGNORE_FILES, REPO_DIR
from eips.enum import EIP1Category, EIP1Status, EIP1Type
from eips.git import ensure_repo_updated
from eips.logging import get_logger
from eips.object import EIP, ERC, CommitHash, CommitRef, EIP1Document, EIPsStats, FlexId
from eips.util import doc_id_from_file

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
        freshness: timedelta,
        repo: str,
        update_on_fetch: bool,
        workdir: Path,
    ):
        """Initialize an Ethereum design document object."""
        self.freshness = freshness
        self.repo = repo
        self.update_on_fetch = update_on_fetch
        self.workdir = workdir
        self.repo_path = self.workdir.joinpath(REPO_DIR)
        self.docs_dir = self.repo_path.joinpath("docs")

    def __getitem__(self, eip_id: int) -> EIP1Document | None:
        """Return an EIP-1 document by ID."""
        e = self.get(eip_id)
        print("-__getitem__ e:", e)
        return e[0] if len(e) else None

    def __len__(self) -> int:
        """Return the total number of documents."""
        return self.len()

    def __iter__(self) -> Iterator[EIP1Document]:
        """Iterate over all documents."""
        yield from self.get()

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

    def logs(self) -> list[str]:
        """Return commit messages for the given EIP"""
        raise NotImplementedError("TODO")

    def repo_fetch(self) -> CommitHash:
        """Fetch (or clone) an EIPs repo"""
        return ensure_repo_updated(self.repo_path, self.repo)

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
            errors=0,
            categories=categories,
            statuses=statuses,
            total=self.len(),
            types=types,
        )


class EIPs(EthereumDocs):
    """EIPs ETL machinery"""

    def __init__(
        self,
        freshness: timedelta = timedelta(seconds=60),
        repo: str = "https://github.com/ethereum/EIPs",
        update_on_fetch: bool = False,
        workdir: Path = Path(DATA_PATH).expanduser().resolve().joinpath("eips"),
    ):
        """Initialize an EIPs ETL processor."""
        super().__init__(freshness, repo, update_on_fetch, workdir)
        self.docs_dir = self.repo_path.joinpath("EIPS")
        print("----------docs_dir", self.docs_dir)

    def get(
        self,
        doc_id: FlexId | None = None,
        *,
        commit: CommitRef | None = None,
    ) -> Sequence[EIP]:
        """Return EIP(s) by ID(s)."""
        current_commit = self.repo_fetch()
        return [
            EIP.parse(current_commit, fil.read_text())
            for fil in self._get_doc(doc_id, commit)
        ]


class ERCs(EthereumDocs):
    """ERCs ETL machinery"""

    def __init__(
        self,
        freshness: timedelta = timedelta(seconds=60),
        repo: str = "https://github.com/ethereum/ERCs",
        update_on_fetch: bool = False,
        workdir: Path = Path(DATA_PATH).expanduser().resolve().joinpath("ercs"),
    ):
        """Initialize an ERCs ETL processor."""
        super().__init__(freshness, repo, update_on_fetch, workdir)
        self.docs_dir = self.repo_path.joinpath("ERCS")

    def get(
        self,
        doc_id: FlexId | None = None,
        *,
        commit: CommitRef | None = None,
    ) -> Sequence[ERC]:
        """Return ERC(s) by ID(s)"""
        current_commit = self.repo_fetch()
        return [
            ERC.parse(current_commit, fil.read_text())
            for fil in self._get_doc(doc_id, commit)
        ]
