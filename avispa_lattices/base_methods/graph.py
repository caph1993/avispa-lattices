from __future__ import annotations
from functools import lru_cache
from typing import TYPE_CHECKING, List, Optional, Sequence, Union, cast
if TYPE_CHECKING:
    from ..base import Lattice, Poset, Relation

import numpy as np
from ..utils.numpy_types import npBoolMatrix, npUInt64Matrix
from collections import deque


def floyd_warshall(adj: npBoolMatrix, infinity: int) -> npUInt64Matrix:
    'Compute all pairs shortest distances using Floyd-Warshall algorithm'
    dist: npUInt64Matrix
    dist = adj.astype(np.uint64)  # type:ignore
    dist[~adj] = infinity
    dist[np.diag_indices_from(dist)] = 0
    for k in range(len(dist)):
        np.minimum(dist, dist[:, k, None] + dist[None, k, :], out=dist)
    return dist


def heights(self: Poset):
    'Array of distance from i down to any bottom'
    dist = self.dist
    bottoms = self.bottoms
    return list(np.min([dist[i, :] for i in bottoms], axis=0))


def depths(self: Poset):
    'Array of distance from any top down to i'
    dist = self.dist
    tops = self.tops
    return list(np.min([dist[:, i] for i in tops], axis=0))


def height(self: Poset):
    return max(heights(self))


def _parse_domain(n: int, domain: Sequence[int] | Sequence[bool]) -> List[int]:
    assert len(domain) <= n, f'Invalid domain: {domain}'
    if len(domain) == n > 0:
        if isinstance(domain[0], bool):
            domain = [i for i in range(n) if domain[i]]
    else:
        assert len(set(domain)) == len(domain), f'Invalid domain: {domain}'
    return domain  # type:ignore


def subgraph(P: Poset, domain: Sequence[int] | Sequence[bool]):
    domain = _parse_domain(P.n, domain)
    m = len(domain)
    leq = P.leq
    sub = np.zeros((m, m), dtype=bool)
    for i in range(m):
        for j in range(m):
            sub[i, j] = leq[domain[i], domain[j]]
    sub.flags.writeable = False
    P_labels = P._labels
    labels = tuple(P_labels[i] for i in domain)
    return P.__class__(sub, check=False, labels=labels)


def toposort_bottom_up(P: Poset):
    n = P.n
    G = P.parents
    child = P.child
    indeg = [child[:, i].sum() for i in range(n)]
    topo: List[int] = []
    q = deque([i for i in range(n) if indeg[i] == 0])
    while q:
        u = q.popleft()
        topo.append(u)
        for v in G[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    assert len(topo) == n, f'Not antisymmetric, cycle found'
    return topo


def toporank(self: Poset):
    return tuple(inverse_permutation(self.toposort_bottom_up))


def inverse_permutation(perm: Sequence[int], check=False):
    n = len(perm)
    if check:
        assert set(perm) == set(range(n)), f'Invalid permutation {perm}'
    rank = [-1] * n
    for i in range(n):
        rank[perm[i]] = i
    return rank


def independent_components(self: Poset):
    'Graph components if all edges were bidirectional'
    n = self.n
    cmp = self.leq | self.leq.T
    G = [[j for j in range(n) if cmp[i, j]] for i in range(n)]
    color = np.ones(n, dtype=int) * -1

    def component(i: int):
        q = deque([i])
        found = []
        while q:
            u = q.popleft()
            for v in G[u]:
                if color[v] != color[u]:
                    color[v] = color[u]
                    q.append(v)
            found.append(u)
        return found

    comps: List[List[int]] = []
    for i in range(n):
        if color[i] == -1:
            color[i] = len(comps)
            comps.append(component(i))
    return comps


def transitive_reduction(leq: npBoolMatrix):
    ''''
    Compute in O(n^3) the transitive reduction of the given relation
    Assuming that it is a poset
    The output relation is also known as "Hasse diagram"
    '''
    lt = leq.copy()
    lt[np.diag_indices_from(lt)] = False
    any_inbetween = np.matmul(lt, lt)
    child = lt & ~any_inbetween
    return cast(npBoolMatrix, child)


def bottoms(self: Poset):
    'bottom elements of the poset'
    n = self.n
    nleq = self.leq.sum(axis=0)
    return [i for i in range(n) if nleq[i] == 1]


def non_bottoms(self: Poset):
    'non-bottom elements of the poset'
    n = self.n
    nleq = self.leq.sum(axis=0)
    return [i for i in range(n) if nleq[i] > 1]


def tops(self: Poset):
    'top elements of the poset'
    n = self.n
    nleq = self.leq.sum(axis=0)
    return [i for i in range(n) if nleq[i] == n]


def non_tops(self: Poset):
    'non-top elements of the poset'
    n = self.n
    nleq = self.leq.sum(axis=0)
    return [i for i in range(n) if nleq[i] < n]


def _toposort_children(self: Poset, domain: Optional[Sequence[int]]):
    'Compute a toposort for domain and the children lists filtered for domain'
    'j in out.children[i] iff j in out.topo and j is children of out.topo[i]'
    n = self.n
    D = range(n) if domain is None else domain
    topo = [i for i in self.toposort_bottom_up if i in D]
    sub = self.MD.graphs.subgraph(self, topo)
    children = [[topo[j] for j in l] for l in sub.children]
    return topo, children