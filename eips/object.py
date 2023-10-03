from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict
from typing_extensions import Self  # Support addded in 3.11

from eips.enum import EIPCategory, EIPStatus, EIPType
from eips.parsing import pluck_headers


class CommitHash(str):
    """Git commit hash"""

    def __new__(cls, value: str) -> Self:
        if len(value) not in (7, 40):
            raise ValueError(f"Invalid commit ref {value}")
        return str.__new__(cls, value[:7])

    def __repr__(self) -> str:
        return f"CommitHash(value={self.__str__()!r})"


CommitRef = Union[CommitHash, str]
FlexId = Union[int, List[int]]


class EIP(BaseModel):
    """EIP"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    eip_id: int
    eip_type: EIPType
    title: str
    # EIP-1 says "should" in one part and "must" when describing order for description
    description: str = ""
    body: str
    author: List[str]
    eip_status: EIPStatus
    created: datetime

    updated: Optional[str] = None
    discussions_to: Optional[str] = None
    review_period_end: Optional[str] = None
    category: Optional[EIPCategory] = None
    requires: Optional[List[int]] = None
    replaces: Optional[List[int]] = None
    superseded_by: Optional[List[int]] = None
    resolution: Optional[str] = None
    commit: Optional[CommitHash] = None

    @property
    def headers(self) -> Dict[str, Any]:
        return self.model_dump(exclude={"body"})

    @property
    def is_valid(self) -> bool:
        # TODO: Implement validity/error check according to EIP-1 (and look for parse
        # errors)
        return True

    @classmethod
    def parse(cls, commit: CommitHash, raw_text: str) -> "EIP":
        headers, body = pluck_headers(raw_text)

        return EIP.model_validate(
            {
                **headers,
                "body": body,
                "commit": commit,
            }
        )


class EIPsStats(BaseModel):
    """General aggregate stats for all EIPs"""

    errors: int
    categories: List[EIPCategory]
    statuses: List[EIPStatus]
    total: int
    types: List[EIPType]
