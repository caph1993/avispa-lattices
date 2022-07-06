from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, List, Tuple, Type, TypeVar, Union, cast
import numpy as np

from ..utils.algorithm_floyd_warshall import transitive_closure, floyd_warshall
from ..utils.numpy_types import npBoolMatrix, npUInt64Matrix


def parents_to_children(parents: List[List[int]]):
    n = len(parents)
    children = [[] for _ in range(n)]
    for ch in range(n):
        for pa in parents[ch]:
            children[pa].append(ch)
    return children


def child_to_dist(child: npBoolMatrix):
    'Compute all pairs shortest distances using Floyd-Warshall algorithm'
    # To do: use toposort or repeated dijsktra if assume_poset==True
    dist = floyd_warshall(child, infinity=child.shape[0])
    return dist


def children_to_leq(children: List[List[int]]):
    n = len(children)
    child = np.zeros((n, n), dtype=bool)
    for pa in range(n):
        for ch in children[pa]:
            child[ch, pa] = True
    dist = child_to_dist(child)
    leq = dist < n
    leq.flags.writeable = False
    dist.flags.writeable = False
    return leq, child, dist


def up_edges_to_leq(n, edges: Iterable[Tuple[int, int]]):
    'create Poset of size n respecting all given relations (descendant, ancestor)'
    leq = np.zeros((n, n), dtype=bool)
    leq[np.diag_indices_from(leq)] = True
    for des, anc in edges:
        leq[des, anc] = True
    leq = transitive_closure(leq)
    leq.flags.writeable = False
    return leq