import numpy as np
from .numpy_types import npBoolMatrix, npUInt64Matrix


def floyd_warshall(adj: npBoolMatrix, infinity: int) -> npUInt64Matrix:
    'Compute all pairs shortest distances using Floyd-Warshall algorithm'
    dist: npUInt64Matrix
    dist = adj.astype(np.uint64)  # type:ignore
    dist[~adj] = infinity
    dist[np.diag_indices_from(dist)] = 0
    for k in range(len(dist)):
        np.minimum(dist, dist[:, k, None] + dist[None, k, :], out=dist)
    return dist


def transitive_closure(leq: npBoolMatrix):
    n = len(leq)
    dist = floyd_warshall(leq, infinity=n)
    rel: npBoolMatrix = (dist < n)
    return rel