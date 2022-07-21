from .. import AL


def main():
    L = AL.Lattice.from_up_edges(5, [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 4),
        (2, 4),
        (3, 4),
    ])
    vpath = AL.new_visualizer('f_iter_monotones')
    for f in list(L.f_iter_monotones()):
        png, txt = next(vpath)
        L.f_assert_is_monotone(f)
        L.show(f, save=png)
        txt.write_text(f'{f}\n')

    vpath = AL.new_visualizer('f_iter_lub')
    for f in list(L.f_iter_lub()):
        png, txt = next(vpath)
        L.f_assert_is_lub(f)
        L.show(f, save=png)
        txt.write_text(f'{f}\n')


if __name__ == '__main__':
    main()