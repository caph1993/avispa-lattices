from .. import AL


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
    assert len(mod) == 12, len(mod)
    assert len(non_mod) == 45


if __name__ == '__main__':
    test_generation_until_7()
