import numpy as np
from .random_state import random_state


def random_lattice(n: int, seed=None):
    '''
    Description:
    
        http://ka.karlin.mff.cuni.cz/jezek/093/random.pdf
    
    This algorihtm works after fixing three issues:
    
        1. k might be zero when rnd(k) is called
           (fixed with k = max(k,1))
        2. u might be undefined at range(u)
           (fixed with u = 1)
        3. The output guarantees unique lub for each pair
           but not unique bottom element
           (fixed in Poset class)
    '''
    R = random_state(seed=seed)
    J = np.zeros((n, n), dtype=int) - 1
    for i in range(n):
        J[i, i] = i

    M = np.zeros((n,), dtype=np.int64)
    Q = np.zeros((n,), dtype=np.int64)

    rnd = lambda k: R.randint(0, k)

    def S(i: int):
        return max(2, int(np.ceil(np.sqrt(i))))

    def FindMax(i: int):
        k = 0
        for j in range(i):
            s = 1
            for a in range(i):
                if a != j and J[a, j] == a:
                    s = 0
            if s != 0:
                M[k] = j
                k += 1
        k = max(k, 1)  # This line did not exist
        a = rnd(k)
        a += 1
        for j in range(k):
            Q[j] = 0
        for s in range(a):
            j = rnd(k)
            if Q[j]:
                s -= 1
            else:
                Q[j] = 1
        return k

    def Work(i):
        if i == n - 1:
            for j in range(n):
                for l in range(n):
                    if J[j, l] == -1:
                        J[j, l] = n - 1
            return
        q = S(n - i)
        if i == 1:
            u = 1
            M[0] = 0
            Q[0] = 1
        elif rnd(q) == 0:
            u = FindMax(i)
        else:  # This case did not exist
            u = 1

        for j in range(u):
            if Q[j]:
                J[M[j], i] = i
                J[i, M[j]] = i
        w = 1
        while w:
            w = 0
            for j in range(i):
                if (J[j, i] == i):
                    for s in range(i):
                        if J[s, j] == j and J[s, i] != i:
                            w = 1
                            J[s, i] = i
                            J[i, s] = i
            for j in range(i):
                if (J[j, i] == i):
                    for l in range(i):
                        if J[l, i] == i:
                            s = J[j, l]
                            if s != -1 and J[s, i] != i:
                                w = 1
                                J[s, i] = i
                                J[i, s] = i
        for j in range(i):
            if J[j, i] == i:
                for l in range(i):
                    if J[l, i] == i and J[j, l] == -1:
                        J[j, l] = i
                        J[l, j] = i
        return

    for i in range(n):
        Work(i)

    return J