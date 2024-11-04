"""Enum definitions for eips package."""

from enum import Enum

from typing_extensions import Self  # Support addded in 3.11


class EIP1Status(str, Enum):
    """EIP-1 Statuses."""

    LIVING = "Living"
    IDEA = "Idea"
    DRAFT = "Draft"
    REVIEW = "Review"
    LAST_CALL = "Last Call"
    FINAL = "Final"
    STAGNANT = "Stagnant"
    WITHDRAWN = "Withdrawn"

    # TODO: Old statuses?  Not (currently) reflected in EIP-1
    ACCEPTED = "Accepted"
    ACTIVE = "Active"
    DEFERRED = "Deferred"
    REJECTED = "Rejected"
    SUPERSEDED = "Superseded"

    # Basically doesn't exist now
    MOVED = "Moved"

    @classmethod
    def get_by_val(cls, v: str) -> Self | None:
        """Get an EIP1Status by value."""
        if not v:
            return None
        for attr in list(cls):
            str_attr = str(attr).split(".")[1]
            attr_v = getattr(cls, str_attr).value
            if attr_v == v or v in attr_v:
                return cls[str_attr]
        return None


class EIP1Type(str, Enum):
    """EIP-1 Types."""

    STANDARDS = "Standards Track"
    INFORMATIONAL = "Informational"
    META = "Meta"

    @classmethod
    def get_by_val(cls, v: str) -> Self | None:
        """Get an EIP1Type by value."""
        if not v:
            return None
        for attr in list(cls):
            str_attr = str(attr).split(".")[1]
            attr_v = getattr(cls, str_attr).value
            if attr_v == v or v in attr_v:
                return cls[str_attr]
        return None


class EIP1Category(str, Enum):
    """EIP-1 Categories."""

    CORE = "Core"
    NETWORKING = "Networking"
    INTERFACE = "Interface"
    ERC = "ERC"

    @classmethod
    def get_by_val(cls, v: str) -> Self | None:
        """Get an EIP1Category by value."""
        if not v:
            return None
        for attr in list(cls):
            str_attr = str(attr).split(".")[1]
            attr_v = getattr(cls, str_attr).value
            if attr_v == v or v in attr_v:
                return cls[str_attr]
        return None


class DocumentType(str, Enum):
    """EIP-1 document types."""

    EIP = "EIP"
    ERC = "ERC"
