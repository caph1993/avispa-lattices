from statistics import median_high
from .. import AL
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


def test_generation_and_f_iteration():
    AL.random.seed(12382332)
    lat_list = [AL.random_lattice(20) for _ in range(30)]
    for L in lat_list:
        assert L.is_poset
        assert L.is_lattice
        pass
    return


vpath = AL.new_visualizer()
L = AL.random_lattice(6, seed=42)
#help(L.f_iter)
print(L.f_iter_lub)
print(AL.github(L.f_iter_lub))
print(L.f_glb.methods)
print(AL.random_lattice.methods)
print(AL.random_poset.methods)
#print(AL.enum.f_iter_methods)
png, txt = next(vpath)
L.show(save=png)

# for f in L.f_iter('all', n=3):
#     print(f)
# for f in L.f_iter('monotones', n=3):
#     print(f)
#     L.show(f)
F = [f for f in L.f_iter_lub()]
print(F[0], F[10], F[20], sep='\n')
custom_color_cycle = ['darkblue', 'darkgreen', 'darkorange', 'darkred']

png, txt = next(vpath)
L.show(F[0], F[10], L.f_lub(F[0], F[10]), save=png,
       colors_cycle=custom_color_cycle)

png, txt = next(vpath)
L.show(F[0], F[10], L.f_lub(F[0], F[10]), L.f_glb(F[0], F[10]), save=png,
       colors_cycle=custom_color_cycle)

png, txt = next(vpath)
L.show(F[0], F[10], L.f_lub(F[0], F[10]), L.f_glb_pointwise(F[0], F[10]),
       save=png, colors_cycle=custom_color_cycle)


def test_f_glb():
    AL.random.seed(123976)
    #P = AL.random_poset
    L = AL.random_lattice(5)
    L.show()
    print(L.is_distributive)
    # for f in L.f_iter(method='monotones'):
    #     print(f)
    for f in L.f_iter_lub():
        print(f)
        print('HEY')
    return


#test_f_glb()
# test_generation_and_f_iteration()
# test_M3()
# test_M5()
# test_generation_until_7()
#assert 2 < timeit.timeit(lambda: test_generation_until_7(), number=3) < 5
