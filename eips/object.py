"""Data models for EIP1 documents."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict
from typing_extensions import Self  # Support addded in 3.11

from eips.enum import DocumentType, EIP1Category, EIP1Status, EIP1Type
from eips.parsing import pluck_headers


class CommitHash(str):
    """Git commit hash"""

    def __new__(cls, value: str) -> Self:
        """Create and validate a new CommitHash instance."""
        if len(value) not in (7, 40):
            raise ValueError(f"Invalid commit ref {value}")
        return str.__new__(cls, value[:7])

    def __repr__(self) -> str:
        """Return a string representation of the CommitHash."""
        return f"CommitHash(value={self.__str__()!r})"


CommitRef = CommitHash | str
FlexId = int | List[int]


class EIP1Document(BaseModel):
    """An Ethereum design document (EIP or ERC)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    # EIP-1 says "should" in one part and "must" when describing order for description
    description: str = ""
    body: str
    status: EIP1Status

    # Optionals
    created: datetime | None = None
    title: str | None = None
    author: List[str] | None = None
    type: EIP1Type | None = None
    updated: Optional[str] = None
    discussions_to: Optional[str] = None
    review_period_end: Optional[str] = None
    category: Optional[EIP1Category] = None
    requires: Optional[List[int]] = None
    replaces: Optional[List[int]] = None
    superseded_by: Optional[List[int]] = None
    resolution: Optional[str] = None
    commit: Optional[CommitHash] = None

    @property
    def headers(self) -> Dict[str, Any]:
        """Return all headers as a dictionary."""
        return self.model_dump(exclude={"body"})

    @property
    def is_valid(self) -> bool:
        """Check if the document is valid according to EIP-1."""
        # TODO: Implement validity/error check according to EIP-1 (and look for parse
        # errors)
        return True

    @classmethod
    def parse(cls, commit: CommitHash, raw_text: str) -> Self:
        """Parse a raw EIP1 document text into EIP1Document object."""
        headers, body = pluck_headers(raw_text)

        return cls.model_validate(
            {
                **headers,
                "body": body,
                "commit": commit,
            }
        )


class EIP(EIP1Document):
    """Ethereum Improvement Proposal.

    EIPs are used to describe protocol level standards.
    """

    document_type: DocumentType = DocumentType.EIP


class ERC(EIP1Document):
    """Ethereum Request for Comment.

    ERCs are used to describe application level standards.
    """

    document_type: DocumentType = DocumentType.ERC


class EIPsStats(BaseModel):
    """General aggregate stats for all EIPs"""

    errors: int
    categories: List[EIP1Category]
    statuses: List[EIP1Status]
    total: int
    types: List[EIP1Type]
