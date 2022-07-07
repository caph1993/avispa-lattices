from . import AL
import timeit
import numpy as np
'''
Run from parent folder with:
python3 -m avispa_lattices.test
'''


def test_M3():
    L = AL.Lattice.from_up_edges(5, [(0, 1), (0, 2), (0, 3), (1, 4), (2, 4),
                                     (3, 4)])
    assert L.is_poset
    assert L.is_lattice
    assert L.is_modular
    assert not L.is_distributive, L.show()
    return


def test_M5():
    L = AL.Lattice.from_up_edges(5, [(0, 1), (1, 2), (0, 3), (2, 4), (3, 4)])
    assert L.is_poset
    assert L.is_lattice
    assert not L.is_modular
    assert not L.is_distributive
    return


def test_generation_until_7():
    non_mod = []
    mod = []
    dist = []
    for L in AL.all_lattices(7):
        if L.is_distributive:
            dist.append(L)
        elif L.is_modular:
            mod.append(L)
        else:
            non_mod.append(L)

    assert len(dist) == 22
    assert len(mod) == 12
    assert len(non_mod) == 45


def test_generation_and_f_iteration():
    R = np.random.RandomState(12382332)
    seeds = R.randint(0, 2**32, size=100)
    lat_list = [AL.random_lattice(20, seed=s, mode='Czech') for s in seeds]
    for L in lat_list:
        assert L.is_poset
        assert L.is_lattice
        pass
    return


def test_f_glb_():
    R = np.random.RandomState(123976)
    L = AL.random_lattice(8, seed=R.randint(0, 2**32), mode='Czech')
    for f in L.f_iter():
        pass
    return


test_generation_and_f_iteration()
test_M3()
test_M5()
test_generation_until_7()
#assert 2 < timeit.timeit(lambda: test_generation_until_7(), number=3) < 5
