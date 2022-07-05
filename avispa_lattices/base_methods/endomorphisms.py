from __future__ import annotations
import functools
import itertools
from typing import TYPE_CHECKING, Callable, Iterable, List, Optional, Union, cast
from collections import deque

if TYPE_CHECKING:
    from ..base import Lattice, Poset, Relation, Endomorphism, PartialEndomorphism, DistributiveLattice

import numpy as np


def f_glb_pointwise(L: Lattice,
                    functions: Iterable[Endomorphism]) -> Endomorphism:
    '''
    Pointwise greatest lower bound of a set of functions.

    This implementation avoids computing the default every
    time and supports comprehensions as input.
    '''
    try:
        first, *functions = functions
    except ValueError:
        h = [L.top] * L.n
        h[L.bottom] = L.bottom
        return h
    h = functools.reduce(
        function=lambda f, g: [L.glb[f[i], g[i]] for i in range(L.n)],
        sequence=functions,
        initial=first,
    )
    return h


def f_lub_pointwise(L: Lattice,
                    functions: Iterable[Endomorphism]) -> Endomorphism:
    '''
    Pointwise lowest upper bound of a set of functions.

    This implementation avoids computing the default every
    time and supports comprehensions as input.
    '''
    try:
        first, *functions = functions
    except ValueError:
        return [L.bottom] * L.n
    h = functools.reduce(
        function=lambda f, g: [L.lub[f[i], g[i]] for i in range(L.n)],
        sequence=functions,
        initial=first,
    )
    return h


def GMeet_naive(L: Lattice, functions: Iterable[Endomorphism]) -> Endomorphism:
    """
    Greatest lower bound of a set of lub-functions.

    Algorithm 2 in "Counting and Computing Join-Endomorphisms in Lattices (Revisited)*"
    """
    h = f_glb_pointwise(L, functions)
    h = fix_f_naive(L, h)
    return h


def fix_f_naive(L: Lattice, f: Endomorphism,
                budget: Optional[int] = None) -> Endomorphism:
    '''
    Compute the "first" function h below f that is a space function
    by fixing iteratively the pairs of elements in the lattice that
    fail to satisfy the LUB axiom

    ... The complexity is, I think, O(n^4). Needs to be checked.
    '''
    lub = L.lub
    leq = L.leq
    it = itertools.count() if budget is None else range(budget)
    f_prev = f = f.copy()
    for _ in it:
        for i in range(L.n):
            for j in range(L.n):
                k = lub[i, j]
                fi_lub_fj = lub[f[i], f[j]]
                if fi_lub_fj == f[k]:
                    pass
                elif leq[f[k], fi_lub_fj]:
                    f[k] = fi_lub_fj
                else:
                    f[i] = lub[f[i], f[k]]
                    f[j] = lub[f[j], f[k]]
        if f == f_prev:
            break
        f_prev = f.copy()
    return f


def DMeet_plus(L: DistributiveLattice,
               *functions: Endomorphism) -> Endomorphism:
    """
    Greatest lower bound of a set of lub-functions in O(n*m).
        n = L.n
        m = len(functions)
    
    This implementation takes advantage of the join irreducible
    elements to reduce the number of operations.
    It is explained in "Counting and Computing Join-Endomorphisms in Lattices (Revisited)*"

    Adapted from the implementation delta_plus_jies at:
        https://github.com/Sirquini/delta/blob/master/delta.py
    """
    n = L.n
    if len(functions) <= 1:
        return f_glb_pointwise(L, functions)
    covers = L.children

    h: PartialEndomorphism = [None for _ in range(n)]
    h[L.bottom] = L.bottom
    for j in L.irreducibles:
        h[j] = L.glb_of_many(fn[j] for fn in functions)

    work = deque(range(n))
    while work:
        x = work.popleft()
        if h[x] is not None:
            continue
        assert len(covers[x]) >= 2, \
            'Invariant violated: "If x has at most 1 cover then h[x] != None"'
        i, j = covers[x]
        if h[i] is None or h[j] is None:
            if h[i] is None:
                work.append(i)
            if h[j] is None:
                work.append(j)
            work.append(x)
        else:
            h[x] = L.lub[h[i], h[j]]
    h = cast(Endomorphism, h)
    return h


# def f_lub(self, f: Endomorphism, g: Endomorphism) -> Endomorphism:
#     return [self.lub[f[i], g[i]] for i in range(self.n)]

# def f_glb(self, f: Endomorphism, g: Endomorphism) -> Endomorphism:
#     return self.f_preserving_lub(self.f_glb_pointwise(f, g))
