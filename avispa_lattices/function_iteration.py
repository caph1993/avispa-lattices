from __future__ import annotations
from functools import reduce
from optparse import Option
from typing import TYPE_CHECKING, Any, Generator, Iterable, Iterator, Optional, Tuple, Union, cast, List, Sequence
from typing_extensions import Literal, get_args as literal_args
from ._function_types import PartialEndomorphism, Endomorphism, partial_endomorphism
from .utils.iterators import product_list
from itertools import islice
from . import _enum as AL_enum
from .base_methods.validation import ValidationError

if TYPE_CHECKING:
    from . import Poset, Lattice

# @section: Poset iteration


def f_iter_all_poset(P: Poset, in_place: bool = False):
    'all endomorphisms'
    out = product_list(range(P.n), repeat=P.n)
    yield from post(out, in_place)


def post(iterator: Iterable[Endomorphism],
         in_place: bool) -> Iterator[Endomorphism]:
    if in_place:
        yield from iterator
    else:
        yield from (f.copy() for f in iterator)


def count_f_all(P: Poset):
    return P.n**P.n


class F_NotMonotone(ValidationError):
    _message = 'f does not preserve order'


def f_assert_is_monotone(P: Poset, f, domain: Optional[Sequence[int]] = None):
    'check if f is monotone over domain'
    n = P.n
    domain = range(n) if domain is None else domain
    leq = P.leq
    for i in domain:
        for j in domain:
            if leq[i, j] and not leq[f[i], f[j]]:
                raise F_NotMonotone(P, f'{f}, {i} {j}')
    return


def f_is_monotone(P: Poset, f, domain: Optional[Sequence[int]] = None):
    'check if f is monotone over domain'
    n = P.n
    domain = range(n) if domain is None else domain
    leq = P.leq
    for i in domain:
        for j in domain:
            if leq[i, j] and not leq[f[i], f[j]]:
                return False
    return True


def f_iter_monotones_poset(P: Poset, in_place: bool = False):
    'all monotone functions'
    for f in f_iter_all_poset(P, in_place):
        if f_is_monotone(P, f):
            yield f
    return


# @section: all endomorphisms and bottom-endomorphism of a poset


def f_iter_all(L: Lattice, bottom_to_bottom: bool = False,
               in_place: bool = False):
    'all endomorphisms f with f[bottom]=bottom'
    n = L.n
    if n == 0:
        return
    if not in_place:
        yield from post(f_iter_all(L, bottom_to_bottom, in_place=True),
                        in_place)
        return
    if bottom_to_bottom:
        options = [range(n) if i != L.bottom else [i] for i in range(n)]
        for f in product_list(*options):
            yield f
    else:
        yield from f_iter_all_poset(L, in_place)


def count_f_all_bottom(L: Lattice):
    return L.n**(L.n - 1)


def test_f_iter_all_bottom(L: Lattice):
    if L.n == 0:
        return
    bot = L.bottom
    expected = set(tuple(f) for f in f_iter_all_poset(L) if f[bot] == bot)
    found = set(tuple(f) for f in f_iter_all(L, bottom_to_bottom=True))
    assert expected == found, (expected.difference(found),
                               found.difference(expected))
    return


# @section: all monotones and bottom-monotones of a poset (bruteforce)
# def f_iter_monotones_bottom_bruteforce(self: Lattice, in_place: bool = False):
#     'all monotone functions with f[bottom]=bottom'
#     return

# @section: all monotones and bottom-monotones of a lattice


def f_iter_monotones(L: Lattice, bottom_to_bottom: bool = False,
                     in_place: bool = False):
    'all monotone functions'
    if not in_place:
        yield from _cast(f_iter_monotones(L, bottom_to_bottom, in_place=True))
        return
    # Shortcuts
    n = L.n
    leq = L.leq
    topo = L.toposort_bottom_up
    children = L.children
    lub_of_many = L.lub_of_many
    if n == 0:
        return
    f = partial_endomorphism(n)
    geq_list = [[j for j in topo if leq[i, j]] for i in range(n)]

    def backtrack(i) -> Iterator[Endomorphism]:
        'f[topo[j]] is fixed for all j<i. Backtrack f[topo[k]] for all k>=i, k<m'
        if i == n:
            yield f
            return

        for k in geq_list[lub_of_many(f[x] for x in children[topo[i]])]:
            f[topo[i]] = k
            yield from backtrack(i + 1)

    if bottom_to_bottom:
        f[L.bottom] = L.bottom
        assert L.bottom == topo[0]
        yield from backtrack(1)
    else:
        yield from backtrack(0)


def _cast(it: Iterator[PartialEndomorphism]):
    return cast(Iterator[Endomorphism], it)


def _f_iter_monotones_restricted(
    self: Lattice,
    f: PartialEndomorphism,
    topo: List[int],
    children: List[List[int]],
    geq_list: List[List[int]],
) -> Iterator[PartialEndomorphism]:
    '''
    Generate all monotone functions f : domain -> L,
    padding non-domain with None
    Returns sequentially the same object modified in place
    '''
    m = len(topo)
    set_lub = self.lub_of_many
    _f: Endomorphism = f  # type: ignore

    for i in range(self.n):
        assert i in topo
        assert i not in children[i]

    def backtrack(i):
        'f[topo[j]] is fixed for all j<i. Backtrack f[topo[k]] for all k>=i, k<m'
        if i == m:
            yield f
            return

        min_value = set_lub(_f[x] for x in children[topo[i]])
        for k in geq_list[min_value]:
            f[topo[i]] = k
            yield from backtrack(i + 1)

    yield from backtrack(0)


'''
@section
    "Irreducible-functions" of a lattice
'''


def f_iter_irreducibles_monotone(self: Lattice, bottom_to_bottom: bool = False):
    'all functions given by f[non_irr]=lub(f[irreducibles] below non_irr)'
    if bottom_to_bottom:
        yield from f_iter_irreducibles_monotone_bottom(self)
    else:
        yield from f_iter_irreducibles_monotone_no_bottom(self)


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
    for f in f_iter_irreducibles_monotone_bottom(self,):
        _glb_f = (lambda acum, b: glb[acum, f[b]])
        glb_f = lambda elems: reduce(_glb_f, elems, self.top)
        for i in below[glb_f(irreducibles)]:
            f[bottom] = i
            yield f


def f_iter_irreducibles_monotone_bottom(
        self: Lattice) -> Iterable[Endomorphism]:
    'all functions given by f[non_irr]=lub(f[irreducibles] below non_irr)'
    if self.n == 0:
        return
    n = self.n
    leq = self.leq
    geq_list = [[j for j in range(n) if leq[i, j]] for i in range(n)]
    m, m_topo, m_children = self.irreducible_components
    f = partial_endomorphism(n)

    _iter = _f_iter_monotones_restricted

    def backtrack(i):
        if i == m:
            yield f
        else:
            it = _iter(self, f, m_topo[i], m_children[i], geq_list)
            for _ in it:
                yield from backtrack(i + 1)

    funcs = backtrack(0)
    yield from _cast(_extrapolate_funcs(self, funcs, self.irreducibles))


def _extrapolate_funcs(self: Lattice, funcs: Iterable[PartialEndomorphism],
                       domain: Iterable[int]):
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


'''
@section
    bottom-lub-functions of a distributive lattice
'''


def f_iter_lub_distributive(self: Lattice, bottom_to_bottom: bool = True):
    'all functions that preserve lubs for sets'
    yield from f_iter_irreducibles_monotone(self, bottom_to_bottom)


def count_f_lub_distributive(L: Lattice, check: bool = False):
    '''
    This function assumes that L is distributive
    '''
    if L.n == 0:
        return 0
    if check:
        assert L.is_distributive
    n = L.n
    leq = L.leq
    geq_list = [[j for j in range(n) if leq[i, j]] for i in range(n)]
    m, m_topo, m_children = L.irreducible_components
    f = partial_endomorphism(n)

    def num(i: int):
        'num of monotone functions restricted to domain k_topo[i]'
        it = _f_iter_monotones_restricted(L, f, m_topo[i], m_children[i],
                                          geq_list)
        return sum(1 for _ in it)

    k_independent = [num(k) for k in range(m)]
    return reduce(lambda a, b: a * b, k_independent, 1)


def f_is_lub_of_irreducibles(self: Lattice, f):
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


'''
@section
    Methods for endomorphisms that preserve lub
'''


def f_iter_lub(self: Lattice, bottom_to_bottom: bool = True):
    if self.is_distributive:
        yield from f_iter_lub_distributive(self, bottom_to_bottom)
    else:
        yield from f_iter_lub_bruteforce(self, bottom_to_bottom)
    return


def f_iter_lub_bruteforce(self: Lattice, bottom_to_bottom: bool = True):
    'all space functions. Throws if no bottom'
    for f in f_iter_monotones(self, bottom_to_bottom):
        if f_is_lub(self, f, bottom_to_bottom=bottom_to_bottom):
            yield f
    return


class F_NotLUB(ValidationError):
    _message = 'f does not preserve lub'


def f_assert_is_lub(self: Lattice, f: Endomorphism, bottom_to_bottom=True,
                    domain=None):
    '''

    check if f preserves lubs for all pairs:
        f[lub[i,j]]=lub[f[i],f[j]]
    and optionally (yes by default) that
        f[bottom]=bottom
    '''
    n = self.n
    if bottom_to_bottom:
        # Small outlier cases
        if n == 0 or (domain is not None and len(domain) <= 1):
            return
        # Check bottom
        bot = self.bottom
        if f[bot] != bot or (domain is not None and bot not in domain):
            raise F_NotLUB(self, f'f[bottom] = f[{bot}] != {bot} = bottom')
    # Check all pairs
    lub = self.lub
    domain = range(n) if domain is None else domain
    for i in domain:
        for j in domain:
            if f[lub[i, j]] != lub[f[i], f[j]]:
                raise F_NotLUB(
                    self,
                    f'f[lub[{i},{j}]] = f[{lub[i,j]}] = {f[lub[i,j]]} != {lub[f[i],f[j]]} = lub[{f[i]},{f[j]}] = lub[f[{i}],f[{j}]]'
                )
    return


def f_is_lub(self: Lattice, f: Endomorphism, bottom_to_bottom=True,
             domain=None):
    '''
    check if f preserves lubs for all pairs:
        f[lub[i,j]]=lub[f[i],f[j]]
    and optionally (yes by default) that
        f[bottom]=bottom
    '''
    try:
        f_assert_is_lub(self, f, bottom_to_bottom, domain)
    except F_NotLUB:
        return False
    return True


def f_iter_lub_no_bottom(self: Lattice):
    'all functions that statisfy f_is_lub'
    it = f_iter_irreducibles_monotone_no_bottom(self,)
    if self.is_distributive:
        yield from it
    else:
        for f in it:
            if f_is_lub(self, f, bottom_to_bottom=False):
                yield f
