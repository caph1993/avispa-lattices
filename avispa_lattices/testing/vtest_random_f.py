from collections import Counter

import numpy as np
from .. import AL
from math import comb, factorial


def main():
    #main_lub()
    uniformity_lub_6()
    uniformity_monotone_6()


def main_monotone():
    AL.random.seed(0)
    vpath = AL.new_visualizer('random_f_monotone')
    L = AL.random_lattice(10)
    for i in range(100):
        f = L.random_f_monotone()
        png, txt = next(vpath)
        L.show(f, save=png)
        txt.write_text(f'{f}\n')
        L.f_assert_is_monotone(f)
    return


def main_lub():
    AL.random.seed(0)
    vpath = AL.new_visualizer('random_f_lub')
    L = AL.random_lattice(10)
    for i in range(100):
        f = L.random_f_lub()
        png, txt = next(vpath)
        L.show(f, save=png)
        txt.write_text(f'{f}\n')
        L.f_assert_is_monotone(f)
    return


def uniformity_monotone_7():
    AL.random.seed(0)
    L = AL.random_lattice(7)
    all_monotones = list(L.f_iter_monotones())
    n = len(all_monotones)
    print(n)
    all_monotones = set(map(tuple, all_monotones))
    assert n == len(all_monotones)

    found = [L.random_f_monotone() for _ in range(n)]
    found = set(map(tuple, found))
    m = len(found)

    expected = n * (1 - (1 - (1. / n))**n)
    print(expected)
    print(m)
    assert m >= expected / 2, f'The algorithm produces too few "random" examples. Expected at least {expected} unique functions, but found {m}.'
    # for i in range(100):
    #     f = L.random_f_monotone()
    #     png, txt = next(vpath)
    #     L.show(f, save=png)
    #     txt.write_text(f'{f}\n')
    #     L.f_assert_is_monotone(f)


def uniformity_monotone_6():
    AL.random.seed(0)
    for seed in range(5):
        L = AL.random_lattice(6)
        all_monotones = list(L.f_iter_monotones())
        n = len(all_monotones)
        all_monotones = set(map(tuple, all_monotones))
        assert n == len(all_monotones)

        N = 3 * n
        found = [tuple(L.random_f_monotone()) for _ in range(N)]
        s_found = set(found)
        m = len(s_found)

        expected = int(n * (1 - (1 - (1. / N))**N))
        print(f'totality:{n}. expected: {expected}, found: {m}')

        # vpath = AL.new_visualizer(f'random_f_monotone_6_seed_{seed}')
        # cnt = Counter(found)
        # _aux = zip(cnt.values(), np.random.random(len(cnt)), cnt.keys())
        # for times, _, key in sorted(_aux, reverse=True)[:20]:
        #     png, txt = next(vpath)
        #     with open(txt, 'w') as txt:
        #         txt.write(f'{key}\n')
        #         L.show([*key], save=png)
        #         print(f'{key}', file=txt)
        #         print(f'appears {times} times', file=txt)

        assert m >= expected / 2, f'The algorithm produces too few "random" examples. Expected at least {expected} unique functions, but found {m}.'


def uniformity_lub_6():
    AL.random.seed(0)
    for seed in range(5):
        L = AL.random_lattice(6)
        all_lubs = list(L.f_iter_lub())
        n = len(all_lubs)
        all_lubs = set(map(tuple, all_lubs))
        assert n == len(all_lubs)

        N = 3 * n
        found = [tuple(L.random_f_lub()) for _ in range(N)]
        s_found = set(found)
        m = len(s_found)

        expected = int(n * (1 - (1 - (1. / N))**N))
        print(f'totality:{n}. expected: {expected}, found: {m}')

        vpath = AL.new_visualizer(f'random_f_lub_6_seed_{seed}')
        cnt = Counter(found)
        _aux = zip(cnt.values(), np.random.random(len(cnt)), cnt.keys())
        for times, _, key in sorted(_aux, reverse=True)[:20]:
            png, txt = next(vpath)
            with open(txt, 'w') as txt:
                txt.write(f'{key}\n')
                L.show([*key], save=png)
                print(f'{key}', file=txt)
                print(f'appears {times} times', file=txt)
                L.f_assert_is_lub([*key])
        assert m >= expected / 2, f'The algorithm produces too few "random" examples. Expected at least {expected} unique functions, but found {m}.'


if __name__ == '__main__':
    main()