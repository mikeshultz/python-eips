from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from typing import Generator

import pytest

from eips.eips import EIPs


@pytest.fixture(scope="session")
def workdir() -> Generator[Path, None, None]:
    wdir = Path(mkdtemp(prefix="eips-test-")).expanduser().resolve()
    yield wdir

    # cleanup
    rmtree(wdir, ignore_errors=True)


@pytest.fixture
def eips(workdir: Path) -> EIPs:
    return EIPs(
        workdir=workdir,
    )
