import local_avispa_lattices as AL


def test_M3():
    L = AL.Lattice.from_up_edges(5, [(0, 1), (0, 2), (0, 3), (1, 4), (2, 4),
                                     (3, 4)])
    assert L.is_poset
    assert L.is_lattice
    assert L.is_modular
    assert not L.is_distributive
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
    for L in AL.generation.iter_all_latices(7):
        if L.is_distributive:
            dist.append(L)
        elif L.is_modular:
            mod.append(L)
        else:
            non_mod.append(L)

    assert len(dist) == 22
    assert len(mod) == 12
    assert len(non_mod) == 45


test_M3()
test_M5()
test_generation_until_7()
