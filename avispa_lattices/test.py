from statistics import median_high
from . import AL
import timeit
import numpy as np
'''
Run from parent folder with:
python3 -m avispa_lattices.test
'''

print(AL.package_info.REQUIREMENTS)
print(AL.package_info.PACKAGES)


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
    for L in AL.iter_all_lattices(7):
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
    seeds = R.randint(0, np.iinfo(np.int32).min, size=100)
    lat_list = [AL.random_lattice(20, seed=s, method='Czech') for s in seeds]
    for L in lat_list:
        assert L.is_poset
        assert L.is_lattice
        pass
    return


L = AL.random_lattice(6, seed=42)
#help(L.f_iter)
print(L.f_iter.methods)
print(L.f_glb.methods)
print(AL.random_lattice.methods)
print(AL.random_poset.methods)
print(AL.enum.f_iter_methods)
L.show()
# for f in L.f_iter('all', n=3):
#     print(f)
# for f in L.f_iter('monotones', n=3):
#     print(f)
#     L.show(f)
F = [f for f in L.f_iter('lub', n=30)]
print(F[0], F[10], F[20], sep='\n')
AL.graphviz.COLORS_CYCLE = ['darkblue', 'darkgreen', 'darkorange', 'darkred']
L.show(F[0], F[10], L.f_lub(F[0], F[10]))
L.show(F[0], F[10], L.f_lub(F[0], F[10]), L.f_glb(F[0], F[10]))
L.show(F[0], F[10], L.f_lub(F[0], F[10]),
       L.f_glb(F[0], F[10], method='pointwise'))


def test_f_glb():
    R = np.random.RandomState(123976)
    #P = AL.random_poset
    L = AL.random_lattice(5, seed=R.randint(0,
                                            np.iinfo(np.int32).max),
                          method='Czech')
    L.show()
    print(L.is_distributive)
    # for f in L.f_iter(method='monotones'):
    #     print(f)
    for f in L.f_iter():
        print(f)
        print('HEY')
    return


test_f_glb()
# test_generation_and_f_iteration()
# test_M3()
# test_M5()
# test_generation_until_7()
#assert 2 < timeit.timeit(lambda: test_generation_until_7(), number=3) < 5
