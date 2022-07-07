from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Literal, Optional, Tuple
import typing
import numpy as np
from .._version import version_is_at_least
from ..utils.algorithm_floyd_warshall import transitive_closure
from ..utils import algorithm_random_poset_czech
from ..utils.random_state import random_state
from ..base import Lattice, Poset, Endomorphism


def random_poset(n: int, p: float, seed: Optional[int] = None):
    '''
    Generates a random poset.
    All posets (modulo labels) have positive probability of being generated.
    If p is close to 0, the poset is very sparse.
    If p is close to 1, the poset is very dense.
    '''
    R = random_state(seed)
    leq = np.zeros((n, n), dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            if R.random() < p:
                leq[i, j] = 1
    for i in range(n):
        leq[i, i] = 1
    leq = transitive_closure(leq)
    leq.flags.writeable = False
    return Poset(leq, check=True)


def random_lattice_czech(n: int, seed: Optional[int] = None):
    '''
    Description: http://ka.karlin.mff.cuni.cz/jezek/093/random.pdf
    '''
    lub = algorithm_random_poset_czech.random_lattice(n, seed)
    child = (lub <= np.arange(n)[None, :])
    leq = transitive_closure(child)
    leq.flags.writeable = False
    L = Lattice(leq, check=False)
    if len(L.bottoms) >= 2:  # Collapse bottoms
        bot = L.bottoms[0]
        leq.flags.writeable = True
        leq[bot, :] = True
        leq.flags.writeable = False
        L = Lattice(leq, check=False)
    return L


_random_lattice_mode = Literal['auto', 'Czech']
_random_lattice_modes: Tuple[str] = typing.get_args(_random_lattice_mode)


def random_lattice(n: int, seed: Optional[int] = None,
                   mode: _random_lattice_mode = 'auto', **kwargs):
    if mode == 'auto':
        if version_is_at_least('3.0.6'):
            mode = 'Czech'
        else:
            mode = 'Czech'

    if mode == 'Czech':
        return random_lattice_czech(n, seed, **kwargs)
    raise NotImplementedError(f'{mode} not in {_random_lattice_modes}')


def random_f_monotone_A(L: Lattice, seed=None,
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


def random_f_monotone_B(L: Lattice, seed=None):
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


def random_f_preserving_lub(L: Lattice, seed: Optional[int] = None,
                            complexity_budget=5):
    f = _random_f_preserving_lub(L, seed=seed)
    if complexity_budget == 0:
        return f
    # Prefer complex functions
    R = random_state(seed)
    seeds = R.randint(0, 2**32, complexity_budget)
    for seed in seeds:
        new_f = _random_f_preserving_lub(L, seed=seed)
        if len(set(f)) < len(set(new_f)):
            f = new_f
    return f


def _random_f_preserving_lub(L: Lattice, seed: Optional[int] = None):
    R = random_state(seed)
    n_above = L.leq.sum(axis=1)
    p_above = n_above / n_above.sum()
    elems = np.arange(L.n)
    f: Endomorphism = [L.bottom] * L.n
    I = np.array(L.irreducibles)
    for i, fi in zip(I, R.choice(elems, len(I), p=p_above)):
        f[i] = fi
    return L.MD.endomorphisms.fix_f_naive(L, f)
