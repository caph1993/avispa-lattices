from __future__ import annotations
from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from ..base import Lattice, Poset, Relation, DistributiveLattice

import numpy as np


class ValidationError(AssertionError):

    _message = 'Validation failed'

    @classmethod
    def assert_false(cls, why_false: str):
        if why_false:
            raise cls(why_false)

    @classmethod
    def capture(cls, method: Callable):
        try:
            method()
        except ValidationError:
            return False
        return True


# Not poset
class MatrixFormatError(ValidationError):
    _message = 'Given matrix relation has incorrect format'


def validate_matrix_format(R: Relation):
    rel = R.leq
    try:
        shape = tuple(rel.shape)
        assert len(shape) == 2, f'Shape {shape} found'
        n = shape[0]
        assert shape == (n, n), f'Shape {shape} found'
        assert rel.dtype == bool, f'Dtype {rel.dtype} found'
        assert rel.flags.writeable == False, 'flags.writeable is True'
    except AssertionError as e:
        message = ''.join([
            'The relation matrix must be a 2-dimensional boolean numpy array',
            ', squared and read-only (i.e. rel.flags.writeable = False).',
            f'\n{e}'
        ])
        raise MatrixFormatError(message)
    R.n = rel.shape[0]
    R.leq = rel
    return


class NotPosetError(ValidationError):
    _message = 'Given relation is not a poset'


class NotTransitive(NotPosetError):
    _message = 'Given relation is not transitive'


class NotReflexive(NotPosetError):
    _message = 'Given relation is not reflexive (i<=i)'


class NotAntisymmetric(NotPosetError):
    _message = ('Given relation is not antisymmetric '
                '(antisymmetry: i<=j and j<=i imply j=i)\n'
                'There is a cycle')


def assert_is_reflexive(R: Relation):
    rel = R.leq
    I, = np.where(~rel[np.diag_indices_from(rel)])
    why = I.size and f'Not reflexive: rel[{I[0]},{I[0]}] is False'
    NotReflexive.assert_false(why)


def assert_is_antisymmetric(R: Relation):
    rel = R.leq
    eye = np.identity(R.n, dtype=np.bool_)
    I, J = np.where(rel & rel.T & ~eye)
    why = I.size and f'Not antisymmetric: cycle {I[0]}<={I[1]}<={I[0]}'
    NotAntisymmetric.assert_false(why)


def assert_is_transitive(R: Relation):
    rel = R.leq
    rel2 = np.matmul(rel, rel)
    I, J = np.where(((~rel) & rel2))
    why = I.size and (
        f'Not transitive: rel[{I[0]},{J[0]}] is False but there is a path')
    NotTransitive.assert_false(why)


def is_reflexive(R: Relation):
    method = lambda: assert_is_reflexive(R)
    return ValidationError.capture(method)


def is_antisymmetric(R: Relation):
    method = lambda: assert_is_antisymmetric(R)
    return ValidationError.capture(method)


def is_transitive(R: Relation):
    method = lambda: assert_is_transitive(R)
    return ValidationError.capture(method)


def assert_is_poset(P: Poset):
    assert_is_reflexive(P)
    assert_is_antisymmetric(P)
    assert_is_transitive(P)
    return


class NoBottoms(NotTransitive):
    pass


class NoTops(NotTransitive):
    pass


# Not lattice
class NotLattice(ValidationError):
    _message = 'Given poset is not a lattice'


class LUB_Inconsistency(ValidationError):

    def __init__(self, i: int, j: int):
        self.args = (i, j)


def assert_is_lattice(L: Lattice):
    if L.n == 0:
        return
    try:  # check if duck says quack
        L.bottom
        L.top
        L.lub
        return
    except LUB_Inconsistency as e:
        i, j = e.args
    # Find the error and explain it to the user
    n = L.n
    leq = L.leq
    above = [k for k in range(n) if leq[i, k] and leq[j, k]]
    below = [k for k in range(n) if leq[k, i] and leq[k, j]]
    try:
        assert above, f'Not a lattice: {i} lub {j} => (no common ancestor)'
        assert below, f'Not a lattice: {i} glb {j} => (no common descendant)'
        lub = min(above, key=lambda k: sum(leq[:, k]))
        glb = max(below, key=lambda k: sum(leq[:, k]))
        for x in above:
            assert leq[lub, x], f'Not a lattice: {i} lub {j} => {lub} or {x}'
        for x in below:
            assert leq[x, glb], f'Not a lattice: {i} glb {j} => {glb} or {x}'
        assert False, 'Unkown reason'
    except AssertionError as e:
        raise NotLattice(e)


class NotComplete(NotLattice):  # Because all finite lattices are complete
    _message = 'Given poset is not complete'


class NotUniqueBottom(NotComplete):
    _message = 'Given poset has multiple bottom elements'


class NotUniqueTop(NotComplete):
    _message = 'Given poset has multiple top elements'


def expect_unique_bottom(bottoms: List[int]):
    if not bottoms:
        raise NoBottoms()
    if len(bottoms) > 1:
        hook = lambda: f'Multiple bottoms found: {bottoms}'
        raise NotUniqueBottom(hook)
    return bottoms[0]


def expect_unique_top(tops: List[int]):
    if not tops:
        raise NoTops()
    if len(tops) > 1:
        hook = lambda: f'Multiple tops found: {tops}'
        raise NotUniqueTop(hook)
    return tops[0]


class NotDistributive(ValidationError):
    _message = 'Given lattice is not distributive'


def assert_is_distributive(self: DistributiveLattice):
    'Find i, j, k that violate distributivity. None otherwise'
    n = self.n
    lub = self.lub
    glb = self.glb
    for i in range(n):
        diff = glb[i, lub] != lub[np.ix_(glb[i, :], glb[i, :])]
        if diff.any():
            j, k = next(zip(*np.where(diff)))  # type:ignore
            raise NotDistributive(
                f'Non distributive lattice:\n'
                f'{i} glb ({j} lub {k}) = {i} glb {lub[j,k]} = '
                f'{glb[i,lub[j,k]]} != {lub[glb[i,j],glb[i,k]]} = '
                f'{glb[i,j]} lub {glb[i,k]} = ({i} glb {j}) lub ({i} glb {k})')
    return


class NotModular(ValidationError):
    _message = 'Given lattice is not distributive'


class RelationExceptions:
    MatrixFormatError = MatrixFormatError
    NotPosetError = NotPosetError
    NotTransitive = NotTransitive
    NotReflexive = NotReflexive
    NotAntisymmetric = NotAntisymmetric


class PosetExceptions:
    NotPosetError = NotPosetError
    NotTransitive = NotTransitive
    NotReflexive = NotReflexive
    NotAntisymmetric = NotAntisymmetric
    NotLattice = NotLattice
    LUB_Inconsistency = LUB_Inconsistency
    NotUniqueBottom = NotUniqueBottom
    NotUniqueTop = NotUniqueTop
    NotComplete = NotComplete
    NotDistributive = NotDistributive
    NoBottoms = NoBottoms
    NoTops = NoTops
    NotModular = NotModular


# def lub_of_set(L: Lattice, *elems: int) -> int:
#     if not elems:
#         return L.bottom
#     lub = L.lub
#     acum = elems[0]
#     for elem in elems[1:]:
#         acum = lub[acum, elem]
#     return acum

# def glb_of_set(L: Lattice, *elems: int) -> int:
#     if not elems:
#         return L.top
#     glb = L.glb
#     acum = elems[0]
#     for elem in elems[1:]:
#         acum = glb[acum, elem]
#     return acum
