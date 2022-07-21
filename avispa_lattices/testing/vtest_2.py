from .. import AL
from math import comb, factorial


def main():
    vpath = AL.new_visualizer('random_f_monotone')
    L = AL.random_lattice(6, seed=42)
    for i in range(10):
        f = L.random_f_monotone()
        png, txt = next(vpath)
        L.f_assert_is_monotone(f)
        L.show(f, save=png)
        txt.write_text(f'{f}\n')
    return


if __name__ == '__main__':
    main()