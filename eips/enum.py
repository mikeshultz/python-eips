from enum import Enum
from typing import Dict, List, Optional, Self


class EIPStatus(str, Enum):
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

    @classmethod
    def get_by_val(cls, v: str) -> Optional[Self]:
        if not v:
            return None
        for attr in list(cls):
            str_attr = str(attr).split(".")[1]
            attr_v = getattr(cls, str_attr).value
            if attr_v == v or v in attr_v:
                return cls[str_attr]
        return None


class EIPType(str, Enum):
    STANDARDS = "Standards Track"
    INFORMATIONAL = "Informational"
    META = "Meta"

    @classmethod
    def get_by_val(cls, v: str) -> Optional[Self]:
        if not v:
            return None
        for attr in list(cls):
            str_attr = str(attr).split(".")[1]
            attr_v = getattr(cls, str_attr).value
            if attr_v == v or v in attr_v:
                return cls[str_attr]
        return None


class EIPCategory(str, Enum):
    CORE = "Core"
    NETWORKING = "Networking"
    INTERFACE = "Interface"
    ERC = "ERC"

    @classmethod
    def get_by_val(cls, v: str) -> Optional[Self]:
        if not v:
            return None
        for attr in list(cls):
            str_attr = str(attr).split(".")[1]
            attr_v = getattr(cls, str_attr).value
            if attr_v == v or v in attr_v:
                return cls[str_attr]
        return None
