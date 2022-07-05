from __future__ import annotations
import functools
from typing import Any, Callable, Generic, Iterable, List, Optional, Sequence, Set, Tuple, Type, TypeVar, Union, cast, overload
import numpy as np
import itertools
from .utils.methodtools import cached_property, cached_method
from .utils.algorithm_tarjan import Tarjan
from .utils.numpy_types import npBoolMatrix, npUInt64Matrix
from .utils.algorithm_floyd_warshall import floyd_warshall
from .utils.methodtools import implemented_at
from . import base_methods as MD
from .base_methods.validation import PosetExceptions

Endomorphism = List[int]
PartialEndomorphism = Union[List[Optional[int]], List[None], Endomorphism]
_T = TypeVar('_T')


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

    MD = MD

    # validation = validation
    # graph = graphs
    # graphviz = graphviz
    # description = description

    def __init__(self, leq: npBoolMatrix, check: bool,
                 labels: Optional[Sequence[str]] = None, **kwargs):
        self.n = len(leq)
        self.leq = leq
        self.labels = labels
        MD.validation.validate_matrix_format(self)
        for k, v in kwargs.items():
            self.__dict__[k] = v
        if check:
            self.validate()
        return

    def validate(self):
        pass  # All binary matrices are valid relations

    @cached_property
    def is_poset(self):
        method = lambda: self.as_poset(check=True)
        return MD.validation.ValidationError.capture(method)

    def as_poset(self, check: bool):
        return self.copy_as(Poset, check=check)

    def copy(self, check=False):
        return self.copy_as(self.__class__, check=check)

    def copy_as(self, cls: Type[_T], check=False) -> _T:
        kwargs = self.__dict__.copy()
        kwargs.pop('leq')
        kwargs.pop('labels', None)
        cpy = cls(self.leq, labels=self.labels, check=check, **kwargs)
        return cpy

    def copy_if(self, cls: Type[_T]) -> Optional[_T]:
        try:
            return self.copy_as(cls, check=True)
        except MD.validation.ValidationError:
            return None

    def reindex(self, rank: List[int], inverse=False):
        return MD.identity.reindex(self, rank, inverse=inverse)

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
    @implemented_at(MD.interface.from_parents)
    def from_parents(cls, *args, **kwargs):
        ...

    @classmethod
    @implemented_at(MD.interface.from_children)
    def from_children(cls, *args, **kwargs):
        ...

    @classmethod
    @implemented_at(MD.interface.from_down_edges)
    def from_down_edges(cls, *args, **kwargse):
        ...

    @classmethod
    @implemented_at(MD.interface.from_up_edges)
    def from_up_edges(cls, *args, **kwargse):
        ...

    @classmethod
    @implemented_at(MD.interface.from_lambda)
    def from_lambda(cls, *args, **kwargs):
        ...

    # def describe(self):
    #     self.show()
    #     print('Relation matrix:')
    #     print(self.leq.astype(int))
    #     print('Reflexive?', self.is_reflexive)
    #     print('Antisymmetric?', self.is_antisymmetric)
    #     print('Transitive?', self.is_transitive)
    #     return

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

    def transitive_closure(self):
        dist = floyd_warshall(self.leq, infinity=self.n)
        rel = (dist < len(dist))
        rel.flags.writeable = False
        return self.__class__(rel, check=False)

    def __lt_pairs(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.leq[i, j] and i != j:
                    yield i, j

    def f_is_monotone(self, f: Endomorphism):
        for i, j in self.__lt_pairs():
            if not self.leq[f[i], f[j]]:
                return False
        return True


class Poset(Relation):
    '''
    Hashable object that represents an inmutable finite partial order.
    Uses a matrix and hashing is invariant under permutations.

    Run print(Poset.usage) for details and usage examples.

    The main attributes (always present) are:
        n: size of the poset.
            The elements of the poset are range(n)
        leq: read only less-or-equal boolean nxn matrix:
            leq[i,j] is True if and only "i <= j" in the poset order
        
        labels: optional sequence of n strings. Only used for displaying
        _idx: optional permutation of 1..n (not the identity).
    '''

    def validate(self):
        super().validate()
        MD.validation.assert_is_poset(self)

    @cached_property
    def is_lattice(self):
        return self.copy_if(Lattice) is not None

    '''
    @section
        Methods for identity
    '''

    def __hash__(self):
        return self.hash

    @cached_property
    def hash(self):
        'hash number for this poset'
        return MD.identity.hasher(sorted(self.hash_elems))

    @cached_property
    def hash_elems(self):
        'hash for each element of the poset w.r.t. the poset order'
        return MD.identity._hash_elems(self, rounds=2, salt=0)

    def __eq__(self, other: Poset):
        'Equality up to isomorphism, i.e. up to reindexing'
        return MD.identity.find_isomorphism(self, other) is not None

    @cached_property
    def hash(self):
        'hash number for this poset'
        return MD.identity.hasher(sorted(self.hash_elems))

    @cached_property
    def canonical(self):
        rank = MD.identity.canonical_rank(self)
        P = self.reindex(rank)
        P.labels = None
        return P

    # __graph = methods_directory.GraphMethods
    # __testing = methods_directory.TestingMethods
    # __generation = methods_directory.GenerationMethods
    # __endomorphism = methods_directory.EndomorphismMethods
    # __initialization = methods_directory.InitializationMethods
    # __binary_operator = methods_directory.BinaryOperatorMethods
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
        child = MD.graphs.transitive_reduction(self.leq)
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
        return MD.graphs.child_to_dist(self.child, assume_poset=True)

    '''
    @section
        Display methods
    '''

    @implemented_at(MD.graphviz.show)
    def show(self):
        ...

    def __repr__(self):
        return self.name

    @cached_property
    def name(self):
        return MD.description.name(self)

    @cached_property
    def upside_down(self):
        geq = self.leq.T
        Q = self.__class__(geq, check=False, labels=self.labels,
                           upside_down=self)
        return Q

    @cached_property
    def toposort_bottom_up(self):
        return MD.graphs.toposort_bottom_up(self)

    @cached_property
    def bottoms(self):
        return MD.graphs.bottoms(self)

    @cached_property
    def tops(self):
        return MD.graphs.tops(self)


class Lattice(Poset):

    def validate(self):
        super().validate()
        MD.validation.assert_is_lattice(self)

    @cached_property
    def is_distributive(self):
        return self.copy_if(DistributiveLattice) is not None

    @cached_property
    def is_modular(self):
        return self.copy_if(ModularLattice) is not None

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
        bottoms = MD.graphs.bottoms(self)
        return MD.validation.expect_unique_bottom(bottoms)

    @cached_property
    def top(self):
        'unique top element of the Poset. Throws if not present'
        tops = MD.graphs.tops(self)
        return MD.validation.expect_unique_top(tops)

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
        components of join irreducibles in toposort order and children
        lists for each component
        '''
        n = self.n
        if n <= 1:  # no join irreducibles at all
            return (0, [], [])
        graphs = self.MD.graphs
        irr = self.irreducibles
        sub = graphs.subgraph(self, irr)
        subcomps = graphs.independent_components(sub)
        m = len(subcomps)
        irrcomps = [[irr[j] for j in subcomps[i]] for i in range(m)]
        m_topo, m_children = zip(*(
            MD.graphs._toposort_children(self, irrcomps[i]) for i in range(m)))
        m_topo = cast(Tuple[List[int]], m_topo)
        m_children = cast(Tuple[List[List[int]]], m_children)
        return m, m_topo, m_children

    def lub_of_many(self, elems: Iterable[int]) -> int:
        return functools.reduce(
            function=lambda i, j: self.lub[i, j],
            sequence=elems,
            initial=self.bottom,
        )

    def glb_of_many(self, elems: Iterable[int]) -> int:
        return functools.reduce(
            function=lambda i, j: self.glb[i, j],
            sequence=elems,
            initial=self.top,
        )


class DistributiveLattice(Lattice):

    def validate(self):
        super().validate()
        MD.validation.assert_is_distributive(self)


class ModularLattice(Lattice):

    def validate(self):
        super().validate()
        MD.validation.assert_is_modular(self)

    # def f_preserves_lub(self, f: Endomorphism):
    #     return all(f[self.lub[i, j]] == self.lub[f[i], f[j]]
    #                for i in range(self.n)
    #                for j in range(self.n))

    # def f_lub(self, f: Endomorphism, g: Endomorphism) -> Endomorphism:
    #     return [self.lub[f[i], g[i]] for i in range(self.n)]

    # def f_glb_pointwise(self, f: Endomorphism, g: Endomorphism) -> Endomorphism:
    #     return [self.glb[f[i], g[i]] for i in range(self.n)]

    # def f_glb(self, f: Endomorphism, g: Endomorphism) -> Endomorphism:
    #     return self.f_preserving_lub(self.f_glb_pointwise(f, g))

    # def f_preserving_lub(self, f: Endomorphism,
    #                      budget: Optional[int] = None) -> Endomorphism:
    #     '''
    #     The famous algorithm that fixes iteratively the pairs of
    #     elements in the lattice that fail to satisfy the LUB axiom
    #     '''
    #     lub = self.lub
    #     leq = self.leq
    #     it = itertools.count() if budget is None else range(budget)
    #     for _ in it:
    #         f_prev = f.copy()
    #         for i in range(self.n):
    #             for j in range(self.n):
    #                 k = lub[i, j]
    #                 fi_lub_fj = lub[f[i], f[j]]
    #                 if fi_lub_fj == f[k]:
    #                     pass
    #                 elif leq[f[k], fi_lub_fj]:
    #                     f[k] = fi_lub_fj
    #                 else:
    #                     f[i] = lub[f[i], f[k]]
    #                     f[j] = lub[f[j], f[k]]
    #         if f == f_prev:
    #             break
    #     return f
