from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, List, Optional, Tuple
import numpy as np
from ..package_info import version_is_at_least
from ..utils.algorithm_floyd_warshall import transitive_closure
from . import czech_algorithm
from ..utils.random_state import random_state
from ..lattice.lattice import Lattice, Poset, Relation
from ..function_operations import fix_f_naive
from .. import _enum as AL_enum
from .._function_types import Endomorphism


def random_poset(n: int, seed: Optional[int] = None,
                 method: AL_enum.random_poset_method = 'auto', **kwargs):
    if method == 'auto':
        method = 'p_threshold'

    if method == 'p_threshold':
        return random_poset_p(n, seed=seed, **kwargs)
    raise NotImplementedError(f'{method} not in {AL_enum.random_poset_method}')


random_poset.methods = AL_enum.random_poset_methods


def random_poset_p(n: int, p: float, seed: Optional[int] = None):
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
    The original algorithm had three errors and was modified in this
    library to fix them. See help(AL.)
    '''
    mat = czech_algorithm.random_lattice(n, seed)
    child = (mat <= np.arange(n)[None, :])
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


def random_lattice(n: int, seed: Optional[int] = None,
                   method: AL_enum.random_lattice_method = 'auto', **kwargs):
    if method == 'auto':
        if version_is_at_least('3.0.6'):
            method = 'Czech'
        else:
            method = 'Czech'
    if method == 'Czech':
        return random_lattice_czech(n, seed, **kwargs)
    raise NotImplementedError(
        f'{method} not in {AL_enum.random_lattice_methods}')


random_lattice.methods = AL_enum.random_lattice_methods
