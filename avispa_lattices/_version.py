from typing import Optional
from typing_extensions import Literal
from packaging.version import parse

VERSION = '3.0.12'


def version_cmp(a: str, b: Optional[str] = None) -> Literal[0, -1, 1]:
    if b is None:
        b = VERSION
    A = parse(a)
    B = parse(b)
    if A == B:
        return 0
    if A < B:
        return -1
    return 1


def version_is_at_least(a: str):
    return version_cmp(a) <= 0
