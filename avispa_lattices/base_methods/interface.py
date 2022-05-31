from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, List, Tuple, Type, TypeVar, Union, cast
import numpy as np

from ..utils.numpy_types import npBoolMatrix, npUInt64Matrix

if TYPE_CHECKING:
    from ..base import Poset, Relation, Lattice
    CLS = TypeVar('CLS', type[Poset], type[Relation], type[Lattice])


def from_parents(cls: CLS, parents, labels=None, check=True):
    'create Poset from list: parents[i] = list of parents of i'
    children = cls.MD.graphs.parents_to_children(parents)
    return cls.from_children(children, labels, check)


def from_children(cls: CLS, children: List[List[int]], labels=None, check=True):
    'create Poset from list: children[i] = list of covers of i'
    n = len(children)
    child = np.zeros((n, n), dtype=bool)
    for pa in range(n):
        for ch in children[pa]:
            child[ch, pa] = True
    child.flags.writeable = False
    dist = cls.MD.graphs.child_to_dist(child, assume_poset=True)
    dist.flags.writeable = False
    leq = dist < n
    leq.flags.writeable = False
    return cls(leq, check, labels=labels, child=child, dist=dist)


def from_down_edges(cls: CLS, n, edges: Iterable[Tuple[int, int]], labels=None,
                    check=True):
    'create Poset of size n respecting all given relations (ancestor, descendant)'
    return cls.from_up_edges(n, [(j, i) for i, j in edges], labels, check)


def from_up_edges(cls: CLS, n, edges: Iterable[Tuple[int, int]], labels=None,
                  check=True):
    'create Poset of size n respecting all given relations (descendant, ancestor)'
    leq = np.zeros((n, n), dtype=bool)
    leq[np.diag_indices_from(leq)] = True
    for des, anc in edges:
        leq[des, anc] = True
    leq.flags.writeable = False
    R = cls(leq, check=False, labels=labels)
    R = R.transitive_closure()  # type: ignore
    #R = R.transitive_closure()
    P = R.copy(cls=cls, check=check)
    return P


def from_lambda(cls: CLS, elems, f_leq, labels=None, check=True):
    'create Poset with: leq[i,j] = f_leq(elems[i], elems[j])'
    m = len(elems)
    leq = np.zeros((m, m), dtype=bool)
    for i in range(m):
        for j in range(m):
            leq[i, j] = f_leq(elems[i], elems[j])
    leq.flags.writeable = False
    P = cls(leq, check=check, labels=labels)
    return P