from datetime import timedelta
from pathlib import Path

import pytest

from eips.eips import REPO_DIR, EIPs, filter_eip_files
from eips.enum import EIPCategory, EIPStatus, EIPType


def test_eips() -> None:
    freshness = timedelta(seconds=4)
    repo = "http://nowhere.com/nothing.git"
    update_on_fetch = True
    workdir = Path("/tmp/nowhere").expanduser().resolve()

    eips = EIPs(
        freshness=freshness,
        repo=repo,
        update_on_fetch=update_on_fetch,
        workdir=workdir,
    )

    assert eips.freshness == freshness
    assert eips.repo == repo
    assert eips.update_on_fetch is update_on_fetch
    assert eips.workdir == workdir


def test_eips_fetch(eips: EIPs, workdir: Path) -> None:
    orig_count = len(list(workdir.iterdir()))
    assert orig_count == 0
    assert eips.repo_fetch()
    assert len(list(workdir.iterdir())) > orig_count


def test_eips_parse_repo(eips: EIPs, workdir: Path) -> None:
    eips_path = workdir.joinpath(REPO_DIR).joinpath("EIPS")
    eips.repo_fetch()
    print("ttt eips_path.iterdir()", list(eips_path.iterdir()))
    eip_files = filter_eip_files(eips_path)
    print("ttttt eip_files:", eip_files)
    assert len(eip_files) > 0
    assert len(eips) == len(eip_files)
    eip_4626 = eips[4626]
    assert eip_4626 is not None
    assert eip_4626.eip_id == 4626

    for eip in eips:
        assert eip.eip_id > 0
        assert eip.is_valid


def test_eips_stats(eips: EIPs, workdir: Path) -> None:
    stats = eips.stats()
    assert stats.total >= 686
    assert len(stats.categories) <= len(EIPCategory)
    assert len(stats.statuses) <= len(EIPStatus)
    assert len(stats.types) <= len(EIPType)
    assert stats.errors == 0
