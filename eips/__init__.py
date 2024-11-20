"""The `eips` package.

This package provides a simple interface to the Ethereum Improvement Proposals (EIP) and
Ethereum Requests for Comment (ERC) data.
"""

from importlib.metadata import metadata

from eips.eips import EIPs, ERCs

meta = metadata("eips")

__all__ = [
    "EIPs",
    "ERCs",
]
__version__ = meta["Version"]
__author__ = meta["Author-email"].split("<")[0].strip()
__email__ = meta["Author-email"]
