from datetime import datetime

from _const import TEST_EIP_HEADER
from eips.enum import EIPCategory, EIPStatus, EIPType
from eips.object import EIP, CommitHash


def test_parse_eip() -> None:
    eip = EIP.parse(CommitHash("abc0def"), TEST_EIP_HEADER)
    assert eip.eip_id == 4200
    assert eip.title == "EOF - Static relative jumps"
    assert (
        eip.discussions_to
        == "https://ethereum-magicians.org/t/eip-3920-static-relative-jumps/7108"
    )
    assert eip.eip_status == EIPStatus.REVIEW
    assert eip.eip_type == EIPType.STANDARDS
    assert eip.category == EIPCategory.CORE
    assert eip.created == datetime(year=2021, month=7, day=16)

    assert eip.requires is not None
    assert len(eip.requires) == 2
    assert 3540 in eip.requires
    assert 3670 in eip.requires
