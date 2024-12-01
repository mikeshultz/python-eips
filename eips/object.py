"""Data models for EIP1 documents."""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypeAlias

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self  # Support addded in 3.11

from eips.enum import DocumentType, EIP1Category, EIP1Status, EIP1Type
from eips.parsing import ParseError, pluck_headers


class CommitHash(str):
    """Git commit hash"""

    def __new__(cls, value: str) -> Self:
        """Create and validate a new CommitHash instance."""
        if len(value) not in (7, 40):
            raise ValueError(f"Invalid commit ref {value}")
        return str.__new__(cls, value)

    def __repr__(self) -> str:
        """Return a string representation of the CommitHash."""
        return f"CommitHash(value={self.__str__()!r})"


CommitRef: TypeAlias = CommitHash | str
FlexId: TypeAlias = int | list[int]


class EIP1Document(BaseModel):
    """An Ethereum design document (EIP or ERC)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    document_type: DocumentType

    id: int
    # EIP-1 says "should" in one part and "must" when describing order for description
    description: str = ""
    body: str
    status: EIP1Status

    # Optionals
    created: datetime | None = None
    title: str | None = None
    author: list[str] | None = None
    type: EIP1Type | None = None
    updated: datetime | None = None
    discussions_to: str | None = None
    review_period_end: str | None = None
    category: EIP1Category | None = None
    requires: list[int] | None = None
    replaces: list[int] | None = None
    superseded_by: list[int] | None = None
    resolution: str | None = None
    commit: CommitHash | None = None
    commit_time: datetime | None = None

    errors: list[str] = Field(default_factory=list)

    @property
    def headers(self) -> dict[str, Any]:
        """Return all headers as a dictionary."""
        return self.model_dump(exclude={"body"})

    @property
    def is_valid(self) -> bool:
        """Check if the document is valid according to EIP-1."""
        # TODO: Implement validity/error check according to EIP-1 (and look for parse
        # errors)
        return True

    @classmethod
    def parse(
        cls, doc_id: int, commit: CommitHash, commit_time: datetime, raw_text: str
    ) -> Self:
        """Parse a raw EIP1 document text into EIP1Document object."""
        errors: list[str] = list()

        try:
            headers, body, parse_errors = pluck_headers(raw_text)

            if parse_errors:
                errors.extend(parse_errors)
        except ParseError as err:
            headers = {}
            body = ""
            errors.append(str(err))
            headers["status"] = EIP1Status.ERROR

        return cls.model_validate(
            {
                "id": doc_id,  # NOTE: this may be overridden by headers
                **headers,
                "body": body,
                "commit": commit,
                "commit_time": commit_time,
                "errors": errors,
            }
        )

    def __repr__(self):
        """Return a string representation of the EIP1Document."""
        return str(self)

    def __str__(self):
        """Return a string representation of the EIP1Document."""
        return (
            f"<{self.document_type.name} {self.id}: {self.title or self.description}>"
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
    categories: list[EIP1Category]
    statuses: list[EIP1Status]
    total: int
    types: list[EIP1Type]
