from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator, List, Optional

from eips.const import EIPS_DIR, IGNORE_FILES, REPO_DIR
from eips.enum import EIPCategory, EIPStatus, EIPType
from eips.git import ensure_repo_updated
from eips.logging import getLogger
from eips.object import EIP, CommitHash, CommitRef, EIPsStats, FlexId
from eips.util import eip_id_from_file

log = getLogger(__name__)
is_eip_file = lambda f: f.name.endswith(".md") and f.name not in IGNORE_FILES
filter_eip_files = lambda fdir: list(filter(is_eip_file, fdir.iterdir()))


class EIPs:
    """EIPs ETL machinery"""

    def __init__(
        self,
        freshness: timedelta = timedelta(seconds=60),
        repo: str = "https://github.com/ethereum/EIPs",
        update_on_fetch: bool = False,
        workdir: Path = Path("~/.config/eips").expanduser().resolve(),
    ):
        self.commit: Optional[CommitRef] = None
        self.freshness = freshness
        self.repo = repo
        self.update_on_fetch = update_on_fetch
        self.workdir = workdir
        self.repo_path = self.workdir.joinpath(REPO_DIR)

    def __getitem__(self, eip_id: int) -> Optional[EIP]:
        e = self.get(eip_id)
        print("-__getitem__ e:", e)
        return e[0] if len(e) else None

    def __len__(self) -> int:
        return self.len()

    def __iter__(self) -> Iterator[EIP]:
        for x in self.get():
            yield x

    @property
    def _eip_files(self) -> List[Path]:
        try:
            return filter_eip_files(self.repo_path.joinpath(EIPS_DIR))
        except FileNotFoundError:
            return []

    def _set_meta(self, updated: Optional[datetime] = None) -> None:
        """Set the metadata for this repo."""
        ...

    def check(
        self,
        eip_id: Optional[FlexId] = None,
        commit: Optional[CommitRef] = None,
    ) -> bool:
        return all(eip.is_valid for eip in self.get(eip_id, commit))

    def get(
        self,
        eip_id: Optional[FlexId] = None,
        commit: Optional[CommitRef] = None,
    ) -> List[EIP]:
        """Return EIP(s) by ID"""
        if commit is not None:
            raise NotImplementedError("commit seeking not implemented")

        current_commit = self.repo_fetch()

        if eip_id is None or (isinstance(eip_id, list) and len(eip_id) == 0):
            # Return all EIPs
            return [
                EIP.parse(current_commit, fil.read_text()) for fil in self._eip_files
            ]
        elif isinstance(eip_id, int):
            eip_id = [eip_id]

        assert isinstance(eip_id, list)

        is_match = lambda f: eip_id_from_file(f.name) in eip_id
        filtered_files = filter(is_match, self._eip_files)

        return [EIP.parse(current_commit, fil.read_text()) for fil in filtered_files]

    def len(self) -> int:
        """Total EIPs in the repo"""
        return len(self._eip_files)

    def logs(self) -> List[str]:
        """Return commit messages for the given EIP"""
        raise NotImplementedError("TODO")

    def repo_fetch(self) -> CommitHash:
        """Fetch (or clone) an EIPs repo"""
        return ensure_repo_updated(self.repo_path, self.repo)

    def stats(self, commit: Optional[CommitRef] = None) -> EIPsStats:
        """Return some aggregate data based on EIP files"""
        categories: List[EIPCategory] = []
        statuses: List[EIPStatus] = []
        types: List[EIPType] = []

        for eip in self.get():
            if eip.category not in categories and eip.category is not None:
                categories.append(eip.category)
            if eip.eip_status not in statuses:
                statuses.append(eip.eip_status)
            if eip.eip_type not in types:
                types.append(eip.eip_type)

        return EIPsStats(
            errors=0,
            categories=categories,
            statuses=statuses,
            total=self.len(),
            types=types,
        )
