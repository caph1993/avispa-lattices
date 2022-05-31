from typing import List
import sys

sys.setrecursionlimit(10**6)


class Tarjan(list):
    vis: List[int]
    low: List[int]
    stack: List[int]
    in_stack: List[int]
    sccs: List[List[int]]
    vis_cnt: int

    def tarjan(self):
        G = self
        n = len(G)
        G.vis, G.low = [-1] * n, [0] * n
        G.stack, G.in_stack = [], [0] * n
        G.vis_cnt = 0
        G.sccs = []
        for i in range(n):
            if G.vis[i] == -1:
                G.dfs(i)
        invV = [-1] * n
        for i, scc in enumerate(G.sccs):
            for j in scc:
                invV[j] = i
        sccE = set()
        for i in range(n):
            for j in G[i]:
                sccE.add((invV[i], invV[j]))
        sccE = list(sccE)
        return G.sccs, sccE

    def dfs(self, i):
        G = self
        G.vis[i] = G.low[i] = G.vis_cnt
        G.vis_cnt += 1
        G.stack.append(i)
        G.in_stack[i] = 1
        for j in G[i]:
            if G.vis[j] == -1:
                G.dfs(j)
                G.low[i] = min(G.low[i], G.low[j])
            elif G.in_stack[j]:
                G.low[i] = min(G.low[i], G.vis[j])
        if G.low[i] == G.vis[i]:
            scc = []
            s = G.stack
            while s[-1] != i:
                scc.append(s.pop())
            scc.append(s.pop())
            for x in scc:
                G.in_stack[x] = 0
            G.sccs.append(scc)
        return
