"""EIP1 document parsing utilities."""

import re
from datetime import datetime
from typing import TypeAlias

from dateutil.parser import ParserError as DateutilParserError
from dateutil.parser import parse as dateutil_parse

from eips.enum import EIP1Category, EIP1Status, EIP1Type
from eips.logging import get_logger

HeaderValueType: TypeAlias = (
    datetime | EIP1Category | EIP1Status | EIP1Type | list[int] | str
)
OptionalHeaderValueType: TypeAlias = HeaderValueType | None
HeadersType: TypeAlias = dict[str, OptionalHeaderValueType]


# Ref: https://www.w3.org/Protocols/rfc822/3_Lexical.html#z1
RFC_822_HEADER = (
    r'^([\w\-]+)\: ([\w\s\number\/\:\?\.\,;@&\*<>\[\]\(\)’\'"`_\^\-\—\+=]*)$'  # noqa: RUF001
)
HEADER_MAPPING = {
    "eip": "id",
    # "status": "eip_status",
    # "type": "eip_type",
}

log = get_logger(__name__)


class ParseError(Exception):
    """Error parsing a document."""


class HeaderParseError(ParseError):
    """Error parsing a header line."""


def normalize_date(date: str) -> datetime:
    """Normalize a date header to handle unusual cases.

    This was specifically created to handle some EIPs that for whatever reason have a
    list of dates for `updated`. We'll parse them all and select the most recent.
    """
    return dateutil_parse(sorted([d.strip() for d in date.split(",")])[-1])


def normalize_id_list(list_string: str) -> list[int]:
    """Normalize ID lists referecing other documents.

    NOTE: This skips invali values.
    """
    if not list_string:
        return list()

    tvals = [x.strip() for x in list_string.split(",")]
    valids = filter(lambda x: x.isdigit(), tvals)
    return list(map(int, valids))


def normalize_header(name: str) -> str:
    """Normalize header name to snake_case."""
    return name.replace("-", "_").strip().lower()


def normalize_header_line(name: str) -> str:
    """Replace known weird characters with less weird characters

    Note: This isn't a security measure, it just eases parsing with known chars.  It
    might be worth just allowing all unicode in the regex, but for now being defensive
    and failing is a bit of an alerting mechanism.
    """
    return (
        name
        # Weird quotes
        .replace("“", '"')
        .replace("”", '"')
        # Zero width non-joiner or whatever
        .replace("\u200c", " ")
        # Basic cleanup
        .strip()
    )


def pluck_headers(eip_text: str) -> tuple[HeadersType, str]:
    """Remove and return the RFC 822 headers from EIP text."""
    lines = eip_text.split("\n")
    line_count = 0
    headers: HeadersType = {}
    found_end = False

    if lines[0] != "---":
        raise HeaderParseError("Header RFC-822 delimiter (---) not found")

    for ln in lines[1:]:
        line_count += 1
        if ln.startswith("---"):
            found_end = True
            break
        matches = re.fullmatch(RFC_822_HEADER, normalize_header_line(ln))
        if not matches or len(matches.groups()) != 2:
            # TODO: Need to store this somewhere for later reference instead of just
            #       logging.
            log.warning(f"EIP header line parse failed: {ln}")
        else:
            normal_header = normalize_header(matches.group(1))
            # Translating to EIP object
            hkey = HEADER_MAPPING.get(normal_header, normal_header)

            hval: OptionalHeaderValueType = None
            if hkey in header_translators:
                raw_val = matches.group(2)
                try:
                    hval = header_translators[hkey](raw_val)
                except DateutilParserError as err:
                    raise ParseError(f"Failed to parse header date {raw_val}: {err}")
            else:
                hval = matches.group(2)

            headers[hkey] = hval

    if not found_end:
        raise SyntaxError("EIP Appears to be malformed.  Did not find end of headers")

    return (headers, "\n".join(lines[line_count + 1 :]))


header_translators = {
    "author": lambda v: list(map(lambda x: x.strip(), v.split(","))),
    "category": lambda v: EIP1Category.get_by_val(v),
    "status": lambda v: EIP1Status.get_by_val(v),
    "type": lambda v: EIP1Type.get_by_val(v),
    # TODO: Vsauce, fragile lambdas here
    "created": lambda v: dateutil_parse(v),
    "updated": lambda v: normalize_date(v),
    "requires": normalize_id_list,
    "replaces": normalize_id_list,
    "superseded_by": normalize_id_list,
}
