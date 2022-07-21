from .. import AL
from math import comb, factorial


def main():
    #main_lub()
    uniformity_monotone()


def main_monotone():
    vpath = AL.new_visualizer('random_f_monotone')
    L = AL.random_lattice(10, seed=42)
    for i in range(100):
        f = L.random_f_monotone()
        png, txt = next(vpath)
        L.show(f, save=png)
        txt.write_text(f'{f}\n')
        L.f_assert_is_monotone(f)
    return


def main_lub():
    vpath = AL.new_visualizer('random_f_lub')
    L = AL.random_lattice(10, seed=42)
    for i in range(100):
        f = L.random_f_lub()
        png, txt = next(vpath)
        L.show(f, save=png)
        txt.write_text(f'{f}\n')
        L.f_assert_is_monotone(f)
    return


def uniformity_monotone():
    L = AL.random_lattice(7, seed=42)
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


if __name__ == '__main__':
    main()