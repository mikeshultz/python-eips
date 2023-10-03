import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from dateutil.parser import parse as dateutil_parse

from eips.enum import EIPCategory, EIPStatus, EIPType
from eips.logging import getLogger

HeaderValueType = Optional[
    Union[datetime, EIPCategory, EIPStatus, EIPType, List[int], str]
]
HeadersType = Dict[str, HeaderValueType]


# Ref: https://www.w3.org/Protocols/rfc822/3_Lexical.html#z1
RFC_822_HEADER = (
    r'^([\w\-]+)\: ([\w\s\number\/\:\?\.\,;@&\*<>\[\]\(\)’\'"`_\^\-\—\+=]*)$'
)
HEADER_MAPPING = {
    "eip": "eip_id",
    "status": "eip_status",
    "type": "eip_type",
}

log = getLogger(__name__)
header_translators = {
    "author": lambda v: list(map(lambda x: x.strip(), v.split(","))),
    "category": lambda v: EIPCategory.get_by_val(v),
    "eip_status": lambda v: EIPStatus.get_by_val(v),
    "eip_type": lambda v: EIPType.get_by_val(v),
    # TODO: Vsauce, fragile lambdas here
    "created": lambda v: dateutil_parse(v),
    "requires": lambda v: list(map(lambda x: int(x.strip()), v.split(","))),
}


def normalize_header(name: str) -> str:
    return name.replace("-", "_").strip().lower()


def normalize_header_line(name: str) -> str:
    """Replace known weird characters with less weird characters

    Note: This isn't a security measure, it just eases parsing with seen chars.  It might
    be worth just allowing all unicode in the regex, but for now being defensive and
    failing is a bit of an alerting mechanism.
    """
    return (
        name
        # Weird quotes
        .replace("“", '"').replace("”", '"')
        # Zero width non-joiner or whatever
        .replace("\u200c", " ")
        # Basic cleanup
        .strip()
    )


def pluck_headers(eip_text: str) -> Tuple[HeadersType, str]:
    """Remove and return the RFC 822 headers from EIP text"""

    lines = eip_text.split("\n")
    line_count = 0
    headers: HeadersType = {}
    found_end = False

    assert lines[0] == "---", "EIP Appears to be malformed"

    for ln in lines[1:]:
        line_count += 1
        if ln.startswith("---"):
            found_end = True
            break
        matches = re.fullmatch(RFC_822_HEADER, normalize_header_line(ln))
        if not matches or len(matches.groups()) != 2:
            # TODO: Need to store this somewhere for later reference instead of just logging
            log.warn(f"EIP header line parse failed: {ln}")
        else:
            normal_header = normalize_header(matches.group(1))
            # Translating to EIP object
            hkey = HEADER_MAPPING.get(normal_header, normal_header)

            hval: HeaderValueType
            if hkey in header_translators:
                hval = header_translators[hkey](matches.group(2))
            else:
                hval = matches.group(2)

            headers[hkey] = hval

    if not found_end:
        raise SyntaxError("EIP Appears to be malformed.  Did not find end of headers")

    return (headers, "\n".join(lines[line_count + 1 :]))
