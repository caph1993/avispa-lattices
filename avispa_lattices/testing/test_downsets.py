from .. import AL
from ..lattice import downsets
import numpy as np
'''
Run from parent folder with:
python3 -m avispa_lattices.test
'''


def main():
    P = AL.Poset.from_up_edges(6, [(0, 1), (0, 2), (1, 3), (2, 3), (1, 5),
                                   (4, 2)])
    #print(downsets.count_downsets_for(P, 5))
    return


if __name__ == '__main__':
    main()