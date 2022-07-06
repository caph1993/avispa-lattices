from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import Lattice, Poset, Relation
from typing import Sequence, Tuple


def describe(P: Poset):
    print('Relation matrix:')
    print(P.leq.astype(int))
    print('Covers:', P)
    print(f'Lattice? {P.is_lattice}')
    if P.is_lattice:
        pass
        # print(f'Distributive? {P.is_distributive}')
    # else:
    #     print(f'# bottoms: {len(bottoms(P))}')
    #     print(f'# tops: {len(tops(P))}')
    P.show()
    return


def name(self: Poset):
    'Compact and readable representation of self based on parents'
    if not hasattr(self, 'n'):
        return f'Uninitialized {self.__class__.__name__}'
    n = self.n
    P = self.parents
    topo = self.toposort_bottom_up
    Pstr = lambda i: ','.join(map(str, P[i]))
    it = (f'{i}<-{Pstr(i)}' for i in topo if P[i])
    name = ' : '.join([f'{n}', *it])
    labels = ''
    if self.labels != tuple(range(n)):
        labels = ', '.join(self._labels)
        labels = f' with labels {labels}'
    return f'P({name}){labels}'