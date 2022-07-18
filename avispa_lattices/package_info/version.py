from typing import Optional
from packaging.version import parse
from . import _VERSION

assert _VERSION.__doc__

VERSION: str = _VERSION.__doc__


def version_is_at_least(a: str, b: Optional[str] = None):
    version_a = parse(a)
    version_b = parse(VERSION) if b is None else parse(b)
    return version_a >= version_b
