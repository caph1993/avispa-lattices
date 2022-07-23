from __future__ import annotations
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Optional, Tuple, TypeVar
from typing_extensions import Protocol
import numpy as np
from ..utils.random_state import AL_random
from ..function_operations import fix_f_naive
from ..utils import _enum as AL_enum
from ..utils._function_types import Endomorphism, partial_endomorphism

if TYPE_CHECKING:
    from .lattice import Lattice as _Lattice, Poset as _Poset, Relation as _Relation


def random_f_arbitrary(_: _Relation) -> Endomorphism:
    n = _.n
    f: Endomorphism = list(AL_random.randint(0, n, n))
    return f


def random_f_monotone_poset(P: _Poset) -> Endomorphism:
    raise NotImplementedError()


def random_f_monotone(L: _Lattice, **kwargs) -> Endomorphism:
    return random_f_monotone_C(L, **kwargs)


def random_f_monotone_A(L: _Lattice, _max_arbitrary_fi: Optional[int] = None):
    f: Endomorphism = [-1] * L.n
    n_above = L.leq.sum(axis=1)
    p_above = n_above / n_above.sum()
    elems = np.arange(L.n)
    f[:] = AL_random.choice(elems, L.n, p=p_above)
    if _max_arbitrary_fi is not None and _max_arbitrary_fi < L.n:
        for i in AL_random.choice(elems, L.n - _max_arbitrary_fi):
            f[i] = L.bottom
    f[L.bottom] = L.bottom
    for i in L.toposort_bottom_up:
        min_fi = L.lub_of_many(f[k] for k in L.children[i])
        f[i] = L.lub[f[i], min_fi]
    return f


def random_f_monotone_B(L: _Lattice):
    f: Endomorphism = [-1] * L.n
    n_above = L.leq.sum(axis=1)
    p_above = n_above / n_above.sum()
    elems = np.arange(L.n)
    for i in L.irreducibles:
        f[i] = AL_random.choice(elems, 1, p=p_above)[0]
    f[L.bottom] = L.bottom
    for i in L.toposort_bottom_up:
        min_fi = L.lub_of_many(f[k] for k in L.children[i])
        assert all(f[k] != -1 for k in L.children[i])
        if f[i] != -1:
            f[i] = L.lub[f[i], min_fi]
        else:
            f[i] = min_fi
    assert L.f_is_monotone(f)
    return f


def random_f_monotone_C(L: _Lattice, bottom_to_bottom: bool = False, _prob=0.4):
    f = L.f_bottom()
    n_above = L.leq.sum(axis=1)
    start = 1 if bottom_to_bottom else 0
    done = False

    def run():
        nonlocal done
        for i in L.toposort_bottom_up[start:]:
            f[i] = L.lub_of_many(f[k] for k in L.children[i])
            while AL_random.random() < _prob and L.parents[f[i]]:
                pa = L.parents[f[i]]
                p = n_above[pa]
                f[i] = AL_random.choice(pa, p=p / p.sum())
        done = f != L.f_bottom() and f != L.f_top()
        if not done and AL_random.random() < 1 / L.n:
            done = True
        return

    while not done:
        run()
    #assert L.f_is_monotone(f)
    return f


random_f_monotone.method_A = random_f_monotone_A
random_f_monotone.method_B = random_f_monotone_B
random_f_monotone.method_C = random_f_monotone_C


def random_f_lub(L: _Lattice, **kwargs):
    return random_f_lub_B(L, **kwargs)


def random_f_lub_B(L: _Lattice):
    f = L.random_f_monotone(bottom_to_bottom=True, _prob=0.7)
    return fix_f_naive(L, f)


def random_f_lub_A(L: _Lattice, complexity_budget=5):
    f = _random_f_preserving_lub(L)
    if complexity_budget == 0:
        return f
    # Prefer complex functions
    seeds = AL_random.randint32(complexity_budget)
    for seed in seeds:
        new_f = _random_f_preserving_lub(L)
        if len(set(f)) < len(set(new_f)):
            f = new_f
    return f


def _random_f_preserving_lub(L: _Lattice):
    n_above = L.leq.sum(axis=1)
    p_above = n_above / n_above.sum()
    elems = np.arange(L.n)
    f: Endomorphism = [L.bottom] * L.n
    I = np.array(L.irreducibles)
    for i, fi in zip(I, AL_random.choice(elems, len(I), p=p_above)):
        f[i] = fi
    return fix_f_naive(L, f)
