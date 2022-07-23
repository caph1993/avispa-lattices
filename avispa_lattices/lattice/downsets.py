from __future__ import annotations
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Optional, Tuple, TypeVar
from typing_extensions import Protocol
import numpy as np
# from ..function_operations import fix_f_naive, fix_f_naive_upwards
from ..utils import _enum as AL_enum
from ..utils._function_types import Endomorphism, partial_endomorphism

if TYPE_CHECKING:
    from .lattice import Lattice as _Lattice, Poset as _Poset, Relation as _Relation

if False:

    def random_downset(P: _Poset):
        for top in P.tops:
            pass
        return

    def collapse_top_downset(P: _Poset, top: int):
        'Assumes top is in P.tops'
        leq = P.leq.copy()
        assert top in P.tops
        mask = (~P.leq[:, top]) | (np.arange(P.n) == top)
        idx = np.flatnonzero(mask)
        i_top = next(i for i, j in enumerate(idx) if j == top)
        new_leq = leq[mask, :][:, mask]
        new_leq[:, i_top] = False
        for i, j in enumerate(idx):
            new_leq[i_top, i] = np.any(leq[leq[:, top], j])
        new_leq.flags.writeable = False
        return i_top, P.__class__(new_leq, check=False)

    def deleting(P: _Poset, i: int):
        mask = (np.arange(P.n) != i)
        return P.__class__(P.leq[mask, mask], check=False)

    from ..visualization.gui import new_visualizer

    vpath = new_visualizer()

    def count_downsets_for(P: _Poset, top: int) -> Tuple[int, int]:
        'Assumes top is in P.tops and P has only one component'
        assert "P has only one component"
        png, txt = next(vpath)
        P.show(save=png)
        with open(txt, "w") as f:
            print(f'tops={P.tops}', file=f)
            print(f'top={top}', file=f)
        assert top in P.tops
        if P.n == 1:
            contaning = 1
            total = 2
            return contaning, total
        i, Q = collapse_top_downset(P, top)
        containing, _ = count_downsets_for(Q, i)
        Q = deleting(P, top)
        arbitrary_top = Q.tops[0]
        _, total = count_downsets_for(Q, arbitrary_top)
        total += containing
        with open(txt, "a") as f:
            print(f'containing={containing}', file=f)
            print(f'total={total}', file=f)
        return containing, total