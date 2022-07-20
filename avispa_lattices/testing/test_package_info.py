from .. import AL


def main():
    assert AL.github(AL) is not None
    assert AL.github(AL.Lattice) is not None
    L = AL.random_lattice(6, seed=42)
    assert AL.github(L) is not None
    assert AL.github(L) == AL.github(AL.Lattice)
    return


if __name__ == '__main__':
    main()