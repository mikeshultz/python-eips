import re

from eips.const import EIP_FILENAME_PATTERN


def eip_id_from_file(fname: str) -> int:
    """Get an EIP ID from a filename"""
    match = re.fullmatch(EIP_FILENAME_PATTERN, fname)
    if match is None:
        return -1
    try:
        return int(match.group(1))
    except IndexError:
        return -1
