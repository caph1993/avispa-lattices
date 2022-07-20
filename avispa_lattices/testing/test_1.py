from .. import AL
from . import viewer
from math import comb, factorial


def main():
    #print(*AL.Lattice.total(6).f_iter_monotones(), sep='\n')
    for n in range(8):
        L = AL.Lattice.total(n)
        expected = comb(2 * n - 1, n - 1) if n > 0 else 0
        found = sum(1 for _ in L.f_iter_monotones())
        assert expected == found, (n, expected, found)
        AL.function_iteration.test_f_iter_all_bottom(L)

    show = viewer.launch()
    L = AL.random_lattice(6, seed=42)
    i = 0
    for f in L.f_iter_lub():
        L.f_assert_is_lub(f)
        i += 1
        L.show(f, save=show / f'{i}.png')

    show = viewer.launch()
    for i in range(20):
        L = AL.random_lattice(i, seed=42)
        L.show(save=show / f'{i}.png')

    show = viewer.launch()
    for seed in range(30):
        L = AL.random_lattice(8, seed=seed)
        L.show(save=show / f'{seed}.png')
        (show / f'{seed}.txt').write_text(f'modular={L.is_modular}\n'
                                          f'distributive={L.is_distributive}\n')
        if L.is_distributive:
            L.assert_is_modular()
    #L.show()
    #print(L)
    # for f in L.f_iter_lub():
    #     print(f)
    # print(L.is_distributive)
    # for f in L.f_iter_monotones():
    #     print(f)
    #     break

    return


if __name__ == '__main__':
    main()