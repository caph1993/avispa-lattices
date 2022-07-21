from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, List, Optional, Tuple
import numpy as np
from ..utils.random_state import random_state
from ..function_operations import fix_f_naive
from .. import _enum as AL_enum
from .._function_types import Endomorphism

if TYPE_CHECKING:
    from .lattice import Lattice as _Lattice, Poset as _Poset, Relation as _Relation


def random_f_arbitrary(_: _Relation, seed=None):
    n = _.n
    R = random_state(seed)
    f: Endomorphism = list(R.randint(0, n, n))
    return f


def random_f_monotone(P: _Poset, seed=None):
    f = random_f_arbitrary(P, seed=seed)
    topo = P.toposort_bottom_up
    rank = np.argsort(topo)
    f[:] = [f[i] for i in np.argsort(rank[f])]
    P.f_assert_is_monotone(f)
    return f


def random_f_monotone_A(L: _Lattice, seed=None,
                        _max_arbitrary_fi: Optional[int] = None):
    R = random_state(seed)
    f: Endomorphism = [-1] * L.n
    n_above = L.leq.sum(axis=1)
    p_above = n_above / n_above.sum()
    elems = np.arange(L.n)
    f[:] = R.choice(elems, L.n, p=p_above)
    if _max_arbitrary_fi is not None and _max_arbitrary_fi < L.n:
        for i in R.choice(elems, L.n - _max_arbitrary_fi):
            f[i] = L.bottom
    f[L.bottom] = L.bottom
    for i in L.toposort_bottom_up:
        min_fi = L.lub_of_many(f[k] for k in L.children[i])
        f[i] = L.lub[f[i], min_fi]
    return f


def random_f_monotone_B(L: _Lattice, seed=None):
    R = random_state(seed)
    f: Endomorphism = [-1] * L.n
    n_above = L.leq.sum(axis=1)
    p_above = n_above / n_above.sum()
    elems = np.arange(L.n)
    for i in L.irreducibles:
        f[i] = R.choice(elems, 1, p=p_above)[0]
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


def random_f_lub(L: _Lattice, seed: Optional[int] = None, complexity_budget=5):
    f = _random_f_preserving_lub(L, seed=seed)
    if complexity_budget == 0:
        return f
    # Prefer complex functions
    R = random_state(seed)
    seeds = R.randint(0, np.iinfo(np.int32).max, complexity_budget)
    for seed in seeds:
        new_f = _random_f_preserving_lub(L, seed=seed)
        if len(set(f)) < len(set(new_f)):
            f = new_f
    return f


def _random_f_preserving_lub(L: _Lattice, seed: Optional[int] = None):
    R = random_state(seed)
    n_above = L.leq.sum(axis=1)
    p_above = n_above / n_above.sum()
    elems = np.arange(L.n)
    f: Endomorphism = [L.bottom] * L.n
    I = np.array(L.irreducibles)
    for i, fi in zip(I, R.choice(elems, len(I), p=p_above)):
        f[i] = fi
    return fix_f_naive(L, f)


def random_f(L: _Lattice, seed: Optional[int] = None,
             method: AL_enum.random_f_method = 'auto', **kwargs):
    if method == 'auto':
        method = 'arbitrary'
    if method == 'monotone':
        method = 'monotone_A'
    f: Endomorphism
    if method == 'arbitrary':
        R = random_state(seed)
        f = list(R.randint(0, L.n, L.n))
    elif method == 'lub':
        f = random_f_lub(L, seed=seed, **kwargs)
    elif method == 'monotone_A':
        f = random_f_monotone_A(L, seed=seed, **kwargs)
    elif method == 'monotone_B':
        f = random_f_monotone_B(L, seed=seed, **kwargs)
    else:
        raise NotImplementedError(f'{method} not in {AL_enum.random_f_methods}')
    return f


random_f.methods = AL_enum.random_f_methods