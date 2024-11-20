"""General util funcs used by the package."""

import re
from datetime import datetime, timedelta, timezone

from eips.const import DOC_FILENAME_PATTERN


def doc_id_from_file(fname: str) -> int:
    """Get a document ID (EIP/ERC No.) from a filename."""
    match = re.fullmatch(DOC_FILENAME_PATTERN, fname)
    if match is None:
        return -1
    try:
        return int(match.group(2))
    except IndexError:
        return -1


def gitstamp_to_dt(timestamp: int, timezone_secs: int = 0) -> datetime:
    """Convert a git timestamp (and timezone in seconds) to a datetime object."""
    return datetime.fromtimestamp(
        timestamp,
        tz=timezone(timedelta(seconds=timezone_secs)),
    )
