from __future__ import annotations
from typing import List, Optional, Union, cast

Endomorphism = List[int]
PartialEndomorphism = Endomorphism


def partial_endomorphism(n: int):
    return cast(PartialEndomorphism, [None] * n)