from __future__ import annotations
from fractions import Fraction
import itertools
from typing import TYPE_CHECKING, Iterable, Iterator, List, Optional, Sequence, Tuple, TypeVar, Union, cast

from avispa_lattices import base
if TYPE_CHECKING:
    from ..base import Lattice, Poset, Relation
    T_Relation = TypeVar('T_Relation', Relation, Poset, Lattice)

from math import factorial
from collections import deque
import numpy as np
from ..utils.numpy_types import npUInt64Matrix, npInt64Array
import xxhash
from .graph import heights

Ints = Union[Sequence[int], npInt64Array]


def hasher(ints: Sequence[int]):
    '''
    Fast numeric hashing function that is consistent across runs.
    Independent of PYTHONHASHSEED unlike Python's hash.
    The output space is range(2**63), i.e. 1e18 approximately 
    '''
    uint64hash = xxhash.xxh64_intdigest(str(ints)[1:-1])
    int64hash = uint64hash >> 1  # Prevent overflow
    return int64hash


def _hash(P: Poset, rounds: int):
    elems = _hash_elems(P, rounds=rounds, salt=0)
    return hasher(sorted(elems))


def _hash_elems(P: Poset, rounds: int, salt: int):
    mat: npUInt64Matrix = P.leq.astype(np.int64)
    with np.errstate(over='ignore'):
        H = hash_perm_invariant(P, salt + mat)
        for repeat in range(rounds):
            mat += np.matmul(H[:, None], H[None, :])
            H = hash_perm_invariant(P, salt + mat)
    return cast(npInt64Array, H)


def hash_perm_invariant(P: Poset, mat: npUInt64Matrix):
    h = lambda l: hasher(sorted(l))
    a = [hasher((h(mat[:, i]), h(mat[i, :]))) for i in range(P.n)]
    return np.array(a, dtype=int)


def find_isomorphism(P: Poset, other: Poset):
    # Quick check:
    if P.n != other.n or hash(P) != hash(other):
        return None

    # Find the isomorphism
    n = P.n
    A = P.leq
    B = other.leq
    IJ = [(i, j) for i in range(n) for j in range(n)]

    def is_isomorphism(f):
        return all(A[i, j] == B[f[i], f[j]] for i, j in IJ)

    Ah = P.hash_elems
    Bh = other.hash_elems
    total, it = isomorphism_candidates(Ah, Bh)
    if total > n**2:
        # Try to hash more deeply to separate
        AAh = Ah + _hash_elems(P, rounds=4, salt=1)
        BBh = Bh + _hash_elems(other, rounds=4, salt=1)
        total, it = isomorphism_candidates(AAh, BBh)

    f: List[int]
    for f in it:
        if is_isomorphism(f):
            return f
    return None


def reindex(P: T_Relation, f, inverse=False, reset_labels=False) -> T_Relation:
    'Reindexed copy of P such that i is to P as f[i] to out'
    'If inverse==True, then f[i] is to P as i to out'
    n = P.n
    assert len(f) == n and sorted(set(f)) == list(
        range(n)), f'Invalid permutation {f}'
    if inverse:
        inv = [0] * n
        for i in range(n):
            inv[f[i]] = i
        f = inv
    leq = P.leq
    out = np.zeros_like(leq)
    for i in range(n):
        for j in range(n):
            out[f[i], f[j]] = leq[i, j]
    out.flags.writeable = False
    out_labels: Optional[Sequence[str]]
    if reset_labels:
        out_labels = None
    else:
        P_labels = P._labels
        out_labels = ['' for i in range(n)]
        for i in range(n):
            out_labels[f[i]] = P_labels[i]
        out_labels = tuple(out_labels)
    return P.__class__(out, False, labels=out_labels)


def canonical_rank_OLD(P: Poset):
    'equivalent poset with enumerated labels and stable order'
    n = P.n
    group_by = {h: [] for h in range(n)}
    h = heights(P)
    for i in range(n):
        group_by[h[i]].append(i)
    pa = P.parents
    ch = P.children
    nleq = P.leq.sum(axis=0)
    ngeq = P.leq.sum(axis=1)
    order = list(zip(nleq, -ngeq, P.hash_elems, P._labels, range(n)))

    def key(i):
        t = tuple(sorted((rank[i] for i in ch[i])))
        return (t, len(pa[i]), order[i])

    topo = []
    rank = [-1] * n
    for h in range(n):
        for i in sorted(group_by[h], key=key):
            rank[i] = len(topo)
            topo.append(i)
    return rank


def canonical_rank(P: Poset):
    'equivalent poset with enumerated labels and stable order'
    n = P.n
    pa = P.parents
    ch = P.children
    nleq = P.leq.sum(axis=0)
    ngeq = P.leq.sum(axis=1)
    nchild = P.child.sum(axis=0)
    vis = set()

    _base_score = [Fraction(nleq[i] + 1, ngeq[i] + 1) for i in range(n)]
    base_score = list(zip(_base_score, -nchild, P.hash_elems))

    last = 0
    rank = [-1] * n
    pa_rank = [n] * n
    vis = set()
    next_layer = set()
    for i in range(n):
        if len(ch[i]) == 0:
            if i not in vis:
                next_layer.add(i)
                vis.add(i)

    while next_layer:
        layer = next_layer
        # Compute ranks
        for i in sorted(layer, key=lambda i: (pa_rank[i], base_score[i])):
            rank[i] = last
            last += 1
        # Compute next_layer
        next_layer = set()
        for i in layer:
            for j in pa[i]:
                if j not in vis:
                    next_layer.add(j)
                    vis.add(j)
                pa_rank[j] = min(pa_rank[j], rank[i])
    return rank


def isomorphism_candidates(hashesA: Ints, hashesB: Ints,
                           out=None) -> Tuple[int, Iterable[List[int]]]:
    '''
    Total number and iterator of all injective and surjective mappings
        f from range(n) to range(n)
    such that
        all(hashesA[i] == hashesB[f[i]] for i in range(n))
    where n = len(hashesA) = len(hashesB).
    '''
    n = len(hashesA)
    if len(hashesA) != len(hashesB):
        return 0, iter([])
    if out is not None:
        assert len(out) == n, f'Incompatible output shape'

    out = [None] * n if out is None else out
    out = cast(List[int], out)

    if sorted(hashesA) != sorted(hashesB):
        return 0, iter([])
    total = 1

    empty = lambda: cast(List[int], [])
    groups = {v: (empty(), empty()) for v in [*hashesA, *hashesB]}
    for i, v in enumerate(hashesA):
        groups[v][0].append(i)
    for i, v in enumerate(hashesB):
        groups[v][1].append(i)

    groups = [*groups.values()]
    for idxA, idxB in groups:
        if len(idxA) != len(idxB):
            return 0, iter([])
        total *= factorial(len(idxA))

    m = len(groups)

    def backtrack(group_i):
        if group_i == m:
            yield out
        else:
            gA, gB = groups[group_i]
            for gBperm in itertools.permutations(gB):
                for i, j in zip(gA, gBperm):
                    out[i] = j
                yield from backtrack(group_i + 1)

    return total, backtrack(0)
