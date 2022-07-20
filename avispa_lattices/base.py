from __future__ import annotations
import functools
from typing import Any, Callable, Generic, Iterable, List, Optional, Sequence, Set, Tuple, Type, TypeVar, Union, cast, overload
import numpy as np

from .utils.methodtools import cached_property, cached_method
from .utils.algorithm_tarjan import Tarjan
from .utils.numpy_types import npBoolMatrix, npUInt64Matrix
from . import utils
from .utils.algorithm_floyd_warshall import floyd_warshall, transitive_closure
from .utils.methodtools import implemented_at
from .base_methods import validation, identity, graphs, interface, description, graphviz

from . import function_operations
from . import function_iteration
from . import base_methods as MD

from .base_methods.validation import PosetExceptions

Endomorphism = List[int]
PartialEndomorphism = Union[List[Optional[int]], List[None], Endomorphism]
_T = TypeVar('_T')


def _copy_as_type(self: Relation, cls: Type[_T], check=False) -> _T:
    kwargs = self.__dict__.copy()
    kwargs.pop('leq')
    kwargs.pop('labels', None)
    cpy = cls(self.leq, labels=self.labels, check=check, **kwargs)
    return cpy


def _lt_pairs(self: Relation):
    for i in range(self.n):
        for j in range(self.n):
            if self.leq[i, j] and i != j:
                yield i, j
    return


class Relation:
    '''
    Class for boolean relation matrices intended mostly for asserting that
    a matrix relation can be used with the fully featured parent classes:
    Poset and Lattice.

    The attribute name leq (less or equal) is missleading for arbitrary relations
    on purpose, because it is mostly used in parent classes.
    '''

    n: int
    leq: npBoolMatrix
    labels: Optional[Sequence[str]]

    MD = MD  # Provide access to library methods for all instances

    def __init__(self, leq: npBoolMatrix, check: bool,
                 labels: Optional[Sequence[str]] = None, **kwargs):
        self.n = len(leq)
        self.leq = leq
        self.labels = labels
        validation.validate_matrix_format(self)
        for k, v in kwargs.items():
            self.__dict__[k] = v
        if check:
            self.validate()
        return

    def validate(self):
        pass  # All binary matrices are valid relations

    @property
    def is_poset(self):
        method = lambda: self.as_poset(check=True) and None
        return validation.ValidationError.capture(method)

    @cached_method(maxsize=1)
    def assert_is_poset(self):
        self.as_poset(check=False)

    def as_poset(self, check: bool):
        return self.as_type(Poset, check=check)

    def as_type(self, cls: Type[_T], check=False) -> _T:
        if isinstance(self, cls):
            return self
        return _copy_as_type(self, cls, check=check)

    def try_type(self, cls: Type[_T]) -> Optional[_T]:
        try:
            return self.as_type(cls, check=True)
        except validation.ValidationError:
            return None

    def copy(self, check=False):
        return _copy_as_type(self, self.__class__, check=check)

    def reindex(self, rank: List[int], inverse=False):
        return identity.reindex(self, rank, inverse=inverse)

    @property
    def _labels(self):
        return self.labels or [f'{i}' for i in range(self.n)]

    def relabel(self, labels: Optional[Sequence[str]] = None):
        'copy of self with different labels'
        if labels == self.labels:
            return self
        if labels is not None:
            n = self.n
            m = len(labels)
            assert m == n, f'{m} labels found. Expected {n}'
            non = [l for l in labels if not isinstance(l, str)]
            assert not non, f'non-string label found: {non[0]}'
        Q = self.copy()
        Q.labels = labels
        return Q

    @classmethod
    def total(cls, n: int):
        'total order of n elements'
        G = [[i - 1] if i > 0 else [] for i in range(n)]
        return cls.from_children(G, check=False)

    '''
    @section
        Interface methods
    '''

    @classmethod
    def from_parents(cls, parents: List[List[int]], labels=None, check=True):
        'new instance from list: parents[i] = list of parents of i'
        children = interface.parents_to_children(parents)
        return cls.from_children(children, labels, check)

    @classmethod
    def from_children(cls, children: List[List[int]], labels=None, check=True):
        'new instance from list: children[i] = list of covers of i'
        leq, child, dist = interface.children_to_leq(children)
        leq.flags.writeable = False
        dist.flags.writeable = False
        return cls(leq, check=check, labels=labels, dist=dist, child=child,
                   children=children)

    @classmethod
    def from_down_edges(cls, n: int, edges: Iterable[Tuple[int, int]],
                        labels=None, check=True):
        'new instance of size n respecting all given relations (ancestor, descendant)'
        up_edges = [(j, i) for i, j in edges]
        return cls.from_up_edges(n, up_edges, labels, check)

    @classmethod
    def from_up_edges(cls, n: int, edges: Iterable[Tuple[int, int]],
                      labels=None, check=True):
        'new instance of size n respecting all given relations (descendant, ancestor)'
        leq = interface.up_edges_to_leq(n, edges)
        leq.flags.writeable = False
        return cls(leq, check=check, labels=labels)

    @classmethod
    def from_lambda(cls, elems: List[_T], f_leq: Callable[[_T, _T], bool],
                    labels=None, check=True):
        'new instance with: leq[i,j] = f_leq(elems[i], elems[j])'
        m = len(elems)
        leq = np.zeros((m, m), dtype=bool)
        for i in range(m):
            for j in range(m):
                leq[i, j] = f_leq(elems[i], elems[j])
        leq.flags.writeable = False
        return cls(leq, check=check, labels=labels)

    def _description(self):
        out = '\n'.join([
            f'Relation matrix:\n{self.leq.astype(int)}',
            f'Reflexive? {validation.is_reflexive(self),}',
            f'Antisymmetric? {validation.is_antisymmetric(self),}',
            f'Transitive? {validation.is_transitive(self),}',
        ])
        return out

    # def show(self, labels=None, save=None):
    #     'Display the relation using graphviz. Groups SCCs together'
    #     scc_components, scc_edges = self.scc_reduction()
    #     if labels is None:
    #         labels = [f'{i}' for i in range(self.n)]
    #     n = len(scc_components)
    #     labels = ['-'.join(labels[i] for i in I) for I in scc_components]
    #     return graphviz(n, edges=scc_edges, labels=labels, save=save)
    '''
    @section
        Graph operations
    '''

    def scc_reduction(self):
        n = self.n
        rel = self.leq
        G = [[] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if rel[i, j] and i != j:
                    G[i].append(j)
        return Tarjan(G).tarjan()

    def f_is_monotone(self, f: Endomorphism):
        for i, j in _lt_pairs(self):
            if not self.leq[f[i], f[j]]:
                return False
        return True


class Poset(Relation):
    '''
    Hashable object that represents an inmutable finite partial order.
    Uses a matrix and hashing is invariant under permutations.

    The main attributes (always present) are:
        n: size of the poset.
            The elements of the poset are range(n)
        leq: read only less-or-equal boolean nxn matrix:
            leq[i,j] is True if and only "i <= j" in the poset order
        
        labels: optional sequence of n strings. Only used for displaying
    '''

    def validate(self):
        super().validate()
        validation.assert_is_poset(self)

    def as_lattice(self, check: bool):
        return self.as_type(Lattice, check=check)

    @cached_method(maxsize=1)
    def assert_is_lattice(self):
        self.as_lattice(check=True)

    @property
    def is_lattice(self):
        return self.try_type(Lattice) is not None

    '''
    @section
        Methods for identity
    '''

    def __hash__(self):
        return self.hash

    @cached_property
    def hash(self):
        'hash number for this poset'
        return identity.hasher(sorted(self.hash_elems))

    @cached_property
    def hash_elems(self):
        'hash for each element of the poset w.r.t. the poset order'
        return identity._hash_elems(self, rounds=2, salt=0)

    def __eq__(self, other: Poset):
        'Equality up to isomorphism, i.e. up to reindexing'
        return identity.find_isomorphism(self, other) is not None

    @cached_property
    def hash(self):
        'hash number for this poset'
        return identity.hasher(sorted(self.hash_elems))

    @cached_property
    def canonical(self):
        rank = identity.canonical_rank(self)
        P = self.reindex(rank)
        P.labels = None
        return P

    '''
    @section
        Fundamental properties
    '''

    @cached_property
    def child(self) -> npBoolMatrix:
        '''
        nxn boolean matrix: transitive reduction of the poset.
        child[i,j] == True iff j covers i (with no elements inbetween)
        '''
        child = graphs.transitive_reduction(self.leq)
        child.flags.writeable = False
        return child

    @cached_property
    def children(self) -> List[List[int]]:
        ''' top-down adjoint list (j in G[i] iff i covers j)'''
        n = self.n
        child = self.child
        return [[j for j in range(n) if child[j, i]] for i in range(n)]

    @cached_property
    def parents(self) -> List[List[int]]:
        '''bottom-up adjoint list (j in G[i] iff j covers i)'''
        n = self.n
        child = self.child
        return [[j for j in range(n) if child[i, j]] for i in range(n)]

    @cached_property
    def dist(self) -> npUInt64Matrix:
        '''
        Matrix of shortest distance from i upwards to j through parents
        n represents infinity.
        '''
        return interface.child_to_dist(self.child)

    '''
    @section
        Display methods
    '''

    @implemented_at(graphviz.show)
    def show(self):
        ...

    def __repr__(self):
        return self.name

    @cached_property
    def name(self):
        return description.name(self)

    @cached_property
    def upside_down(self):
        geq = self.leq.T
        Q = self.__class__(geq, check=False, labels=self.labels,
                           upside_down=self)
        return Q

    @cached_property
    def toposort_bottom_up(self):
        return graphs.toposort_bottom_up(self)

    @cached_property
    def bottoms(self):
        return graphs.bottoms(self)

    @cached_property
    def tops(self):
        return graphs.tops(self)

    @implemented_at(function_iteration.f_iter_all_poset)
    def f_iter_all(self, *args, **kwargs):
        ...

    @implemented_at(function_iteration.f_iter_monotones_poset)
    def f_iter_monotones(self, *args, **kwargs):
        ...


class Lattice(Poset):

    def validate(self):
        super().validate()
        validation.assert_is_lattice(self)

    @cached_method(maxsize=1)
    def assert_is_distributive(self):
        validation.assert_is_distributive(self)

    @cached_method(maxsize=1)
    def assert_is_modular(self):
        validation.assert_is_modular(self)

    @property
    def is_distributive(self):
        try:
            self.assert_is_distributive()
        except validation.ValidationError:
            return False
        return True

    @property
    def is_modular(self):
        try:
            self.assert_is_modular()
        except validation.ValidationError:
            return False
        return True

    @cached_property
    def lub(self):
        'matrix of i lub j, i.e. i join j'
        n = self.n
        leq = self.leq
        lub_id = {tuple(leq[i, :]): i for i in range(n)}
        lub = np.zeros((n, n), int)
        for i in range(n):
            for j in range(n):
                above = tuple(leq[i, :] & leq[j, :])
                if above not in lub_id:
                    raise PosetExceptions.LUB_Inconsistency(i, j)
                lub[i, j] = lub_id[above]
        lub.flags.writeable = False
        return lub

    @property
    def glb(self):
        return self.upside_down.lub

    @cached_property
    def bottom(self):
        'unique bottom element of the Poset. Throws if not present'
        return validation.expect_unique_bottom(self)

    @cached_property
    def top(self):
        'unique top element of the Poset. Throws if not present'
        return validation.expect_unique_top(self)

    @cached_property
    def irreducibles(self):
        n = self.n
        children = self.children
        return tuple([i for i in range(n) if len(children[i]) == 1])

    @cached_property
    def irreducible_descendants(self):
        '''Irreducibles below x for each x'''
        Rn = range(self.n)
        I = self.irreducibles
        leq = self.leq
        return tuple([tuple([i for i in I if leq[i, x]]) for x in Rn])

    @cached_property
    def irreducible_components(self: Lattice):
        '''
        Components of join irreducibles in toposort order and children
        lists for each component
        '''
        n = self.n
        if n <= 1:  # no join irreducibles at all
            return (0, [], [])
        irr = self.irreducibles
        sub = graphs.subgraph(self, irr)
        subcomps = graphs.independent_components(sub)
        m = len(subcomps)
        irrcomps = [[irr[j] for j in subcomps[i]] for i in range(m)]
        m_topo, m_children = zip(
            *(graphs._toposort_children(self, irrcomps[i]) for i in range(m)))
        m_topo = cast(Tuple[List[int]], m_topo)
        m_children = cast(Tuple[List[List[int]]], m_children)
        return m, m_topo, m_children

    def lub_of_many(self, elems: Iterable[int]) -> int:
        return functools.reduce(
            lambda i, j: self.lub[i, j],
            elems,
            self.bottom,
        )

    def glb_of_many(self, elems: Iterable[int]) -> int:
        return functools.reduce(
            lambda i, j: self.glb[i, j],
            elems,
            self.top,
        )

    @implemented_at(function_operations.f_lub_pointwise)
    def f_lub(self, *args, **kwargs):
        ...

    @implemented_at(function_operations.f_glb_pointwise)
    def f_glb_pointwise(self, *args, **kwargs):
        ...

    @implemented_at(function_operations.f_glb)
    def f_glb(self, *args, **kwargs):
        ...

    @implemented_at(function_iteration.f_iter_all)
    def f_iter_all(self, *args, **kwargs):
        ...

    @implemented_at(function_iteration.f_iter_monotones)
    def f_iter_monotones(self, *args, **kwargs):
        ...

    @implemented_at(function_iteration.f_iter_lub)
    def f_iter_lub(self, *args, **kwargs):
        ...

    @implemented_at(function_iteration.f_is_lub)
    def f_is_lub(self, *args, **kwargs):
        ...

    @implemented_at(function_iteration.f_is_monotone)
    def f_is_monotone(self, *args, **kwargs):
        ...

    @implemented_at(function_iteration.f_assert_is_lub)
    def f_assert_is_lub(self, *args, **kwargs):
        ...

    @implemented_at(function_iteration.f_assert_is_monotone)
    def f_assert_is_monotone(self, *args, **kwargs):
        ...
