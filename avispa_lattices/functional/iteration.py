from __future__ import annotations
from functools import reduce
from optparse import Option
from typing import TYPE_CHECKING, Any, Iterable, Optional, Tuple, cast, List, Sequence
from typing_extensions import Literal, get_args as literal_args
from ._types import PartialEndomorphism, Endomorphism

if TYPE_CHECKING:
    from .. import Poset, Lattice

from ..utils.iterators import product_list
from itertools import islice
from .. import _enum as AL_enum


def f_iter(L: Lattice, method: AL_enum.f_iter_method = 'auto',
           n: Optional[int] = None, in_place=False):
    '''
    Iterator of endomorphisms over a given lattice.
    method can be:
        'all': all endomorphisms
        'monotones': all monotone endomorphisms
        'lub': all join-endomorphisms, i.e. endomorphisms that preserve least-upper-bounds.
        'lub_no_bottom': all endomorphisms that preserve lub but without the constraint f[bottom]=bottom.
        'auto': (default) defaults to "lub"

    if in_place is True (faster, but advanced), the iterator will succesively yield the same endomorphism object with entries modified
    '''
    if method == 'auto':
        method = 'lub'
    return islice((cast(Endomorphism, f.copy()) for f in _f_iter(L, method)), n)


f_iter.methods = AL_enum.f_iter_methods


def _f_iter(L: Lattice, method: AL_enum.f_iter_method):
    if method == 'lub' and L.is_distributive:
        yield from f_iter_lub_distributive(L)
    elif method == 'lub':
        for f in f_iter_monotone(L):
            if f_is_lub(L, f):
                yield f
    elif method == 'all':
        yield from f_iter_all(L)
    elif method == 'monotones':
        yield from f_iter_monotone_no_bottom(L)
    elif method == 'lub_no_bottom':
        for f in f_iter_monotone_no_bottom(L):
            if f_is_lub_no_bottom(L, f):
                yield f
    else:
        raise NotImplementedError(f'"{method}" not in {AL_enum.f_iter_methods}')


_f_iter.methods = AL_enum.f_iter_methods


def f_iter_lub_distributive(self: Lattice):
    'all functions that preserve lubs for sets'
    yield from f_iter_irreducibles_monotone(self)


def f_iter_all(self: Poset):
    'all endomorphisms'
    return product_list(range(self.n), repeat=self.n)


def num_f_all(self: Poset):
    return self.n**self.n


def f_iter_all_bottom(self: Lattice):
    'all endomorphisms f with f[bottom]=bottom'
    n = self.n
    if n > 0:
        options = [range(n) if i != self.bottom else [i] for i in range(n)]
        for f in product_list(*options):
            yield f
    return


def num_f_all_bottom(self: Poset):
    return self.n**(self.n - 1)


def f_is_monotone(self: Poset, f, domain=None):
    'check if f is monotone over domain'
    n = self.n
    domain = range(n) if domain is None else domain
    leq = self.leq
    for i in domain:
        for j in domain:
            if leq[i, j] and not leq[f[i], f[j]]:
                return False
    return True


def f_iter_monotone_bruteforce(self: Poset):
    'all monotone functions'
    for f in f_iter_all(self):
        if f_is_monotone(self, f):
            yield f
    return


def f_iter_monotone_bottom_bruteforce(self: Lattice):
    'all monotone functions with f[bottom]=bottom'
    for f in f_iter_all_bottom(self,):
        if f_is_monotone(self, f):
            yield f
    return


def f_iter_monotone_no_bottom(self: Lattice):
    'all monotone functions'
    f: PartialEndomorphism = [None] * self.n
    yield from f_iter_monotone_restricted(self, _f=f)


def f_iter_lub_bruteforce(self: Lattice):
    'all space functions. Throws if no bottom'
    for f in f_iter_monotone(self,):
        if f_is_lub_no_bottom(self, f):
            yield f
    return


def f_iter_monotone_restricted(self: Lattice, domain=None,
                               _f: Optional[PartialEndomorphism] = None):
    'generate all monotone functions f : domain -> self, padding non-domain with None'
    n = self.n
    leq = self.leq
    geq_list = [[j for j in range(n) if leq[i, j]] for i in range(n)]
    f: PartialEndomorphism = [None for i in range(n)] if _f is None else _f
    topo, children = self.MD.graphs._toposort_children(self, domain)
    yield from _f_iter_monotone_restricted(self, f, topo, children, geq_list)


def _f_iter_monotone_restricted(
    self: Lattice,
    f: PartialEndomorphism,
    topo: List[int],
    children,
    geq_list: List[List[int]],
):
    m = len(topo)
    lub_f = self.lub_of_many

    def backtrack(i):
        'f[topo[j]] is fixed for all j<i. Backtrack f[topo[k]] for all k>=i, k<m'
        if i == m:
            yield f
        else:
            for k in geq_list[lub_f(children[i])]:
                f[topo[i]] = k  # type:ignore
                yield from backtrack(i + 1)

    yield from backtrack(0)


def f_iter_monotone(self: Lattice):
    'all monotone functions with f[bottom]=bottom'
    if self.n == 0:
        return
    f = cast(List[int], [None] * self.n)
    f[self.bottom] = self.bottom
    domain = [i for i in range(self.n) if i != self.bottom]
    yield from f_iter_monotone_restricted(self, domain=domain, _f=f)


def _interpolate_funcs(self: Lattice, funcs, domain) -> Iterable[List[int]]:
    'extend each f in funcs outside domain using f[j]=lub(f[i] if i<=j and i in domain)'
    n = self.n
    lub = self.lub
    leq = self.leq
    bot = self.bottom
    no_domain = [i for i in range(n) if i not in domain]
    dom_leq = [[i for i in domain if leq[i, j]] for j in range(n)]
    lub_f = (lambda a, b: lub[a, b])
    for f in funcs:
        for j in no_domain:
            f[j] = reduce(lub_f, (f[x] for x in dom_leq[j]), bot)
        yield f


def f_iter_irreducibles_monotone(self: Lattice) -> Iterable[List[int]]:
    'all functions given by f[non_irr]=lub(f[irreducibles] below non_irr)'
    if self.n == 0:
        return
    n = self.n
    leq = self.leq
    geq_list = [[j for j in range(n) if leq[i, j]] for i in range(n)]
    m, m_topo, m_children = self.irreducible_components
    f = [None for i in range(n)]
    f = cast(PartialEndomorphism, f)

    def backtrack(i):
        if i == m:
            yield f
        else:
            it = _f_iter_monotone_restricted(
                self,
                f,
                m_topo[i],
                m_children[i],
                geq_list,
            )
            for _ in it:
                yield from backtrack(i + 1)

    funcs = backtrack(0)
    yield from _interpolate_funcs(self, funcs, self.irreducibles)


def f_iter_irreducibles_monotone_no_bottom(self: Lattice):
    'all functions given by f[non_irr]=lub(f[irreducibles] below non_irr) and'
    'f[bottom] = any below or equal to glb(f[irreducibles])'
    n = self.n
    if n == 0:
        return
    glb = self.glb
    leq = self.leq
    below = [[i for i in range(n) if leq[i, j]] for j in range(n)]
    bottom = self.bottom
    irreducibles = self.irreducibles
    for f in f_iter_irreducibles_monotone(self,):
        _glb_f = (lambda acum, b: glb[acum, f[b]])
        glb_f = lambda elems: reduce(_glb_f, elems, self.top)
        for i in below[glb_f(irreducibles)]:
            f[bottom] = i
            yield f


'''
@section
    Methods for endomorphisms that preserve lub
'''


def f_is_lub(self: Lattice, f, domain=None):
    '''
    check if f preserves lubs for sets:
        f_is_lub_no_bottom and f[bottom]=bottom.
    Throws if no bottom
    '''
    n = self.n
    # Small outlier cases
    if n == 0 or (domain is not None and len(domain) <= 1):
        return True
    # Check bottom
    bot = self.bottom
    if f[bot] != bot or (domain is not None and bot not in domain):
        return False
    # Check the rest
    return f_is_lub_no_bottom(self, f, domain)


def f_is_lub_no_bottom(L: Lattice, f, domain=None):
    '''
    check if f preserves lubs for all pairs:
        f[lub[i,j]]=lub[f[i],f[j]]
    '''
    n = L.n
    lub = L.lub
    domain = range(n) if domain is None else domain
    for i in domain:
        for j in domain:
            if f[lub[i, j]] != lub[f[i], f[j]]:
                return False
    return True


def f_iter_lub_no_bottom_bruteforce(self: Lattice):
    'all functions that statisfy f_is_lub_no_bottom'
    for f in f_iter_monotone_no_bottom(self,):
        if f_is_lub_no_bottom(self, f):
            yield f
    return


def f_iter_lub_no_bottom(self: Lattice):
    'all functions that statisfy f_is_lub'
    it = f_iter_irreducibles_monotone_no_bottom(self,)
    if self.is_distributive:
        yield from it
    else:
        for f in it:
            if f_is_lub_no_bottom(self, f):
                yield f


def num_f_lub_no_bottom(self: Lattice):
    return count_f_lub_no_bottom_bruteforce(self,)


def count_f_lub_no_bottom_bruteforce(self: Lattice):
    return sum(1 for f in f_iter_lub_no_bottom(self,))


# def num_f_lub(self: Lattice):
#     return count_f_lub(self,)

# def count_f_lub(self: Lattice):
#     if self.is_distributive:
#         num = count_f_lub_distributive(self)
#     else:
#         num = count_f_lub_non_distributive(self)
#     return num

# def count_f_lub_non_distributive(self: Lattice):
#     return sum(1 for f in f_iter_lub(self,))


def f_is_lub_of_irreducibles(self: Lattice, f, domain=None):
    '''
    check if f satisfies for all x in range(n) that
        f(x) == self.set_lub(*[f[i] for i in I(x)])
    where
        I(x) = list of irreducibles below (leq) x
    '''
    n = self.n
    set_lub = self.lub_of_many
    I = self.irreducible_descendants
    for a in range(n):
        if f[a] != set_lub(I[a]):
            return False
    return True


def count_f_lub_distributive(L: Lattice):
    '''
    This function assumes that your lattice is distributive
    '''
    if L.n == 0:
        return 0
    n = L.n
    leq = L.leq
    geq_list = [[j for j in range(n) if leq[i, j]] for i in range(n)]
    m, m_topo, m_children = L.irreducible_components
    f = [None for _ in range(n)]

    f = cast(PartialEndomorphism, f)

    def num(i: int):
        'num of monotone functions restricted to domain k_topo[i]'
        it = _f_iter_monotone_restricted(
            L,
            f,
            m_topo[i],
            m_children[i],
            geq_list,
        )
        return sum(1 for _ in it)

    k_independent = [num(k) for k in range(m)]
    return reduce(lambda a, b: a * b, k_independent, 1)