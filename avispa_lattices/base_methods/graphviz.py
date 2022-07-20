from __future__ import annotations
import itertools
from typing import TYPE_CHECKING, Dict, List, Optional, cast

if TYPE_CHECKING:
    from .._function_types import PartialEndomorphism
    from ..base import Lattice, Poset, Relation
from typing import Sequence, Tuple


def graphviz(
    n: int,
    edges: Sequence[Tuple[int, int]],
    labels: Sequence[str],
    extra_edges: List[Tuple[str, List[Tuple[int, int]]]] = [],
    save: Optional[str] = None,
):
    'Show graph using graphviz. blue edges are extra edges'
    from pydotplus import graph_from_edges
    from pydotplus.graphviz import Node, Edge

    black_color = '#aaaaaa'

    g = graph_from_edges([], directed=True)
    g.set_rankdir('TB')  # type:ignore
    for i in range(n):
        style = {
            'margin': 0,
            'width': 0.35,
            'shape': 'circle',
        }
        g.add_node(Node(i, label=f'"{labels[i]}"', **style))

    for i, j in edges:
        style = {
            'dir': 'none',
            'color': black_color,
            'arrowsize': 0.5,
        }
        g.add_edge(Edge(i, j, **style))

    for color, color_edges in extra_edges:
        style = {
            'color': color,
            'constraint': 'false',
            'arrowsize': 0.65,
        }
        for i, j in color_edges:
            g.add_edge(Edge(i, j, **style))

    png = g.create_png()  # type:ignore

    if save is None:
        import builtins
        if hasattr(builtins, '__IPYTHON__'):
            from IPython.display import display
            from IPython.display import Image
            img = Image(png)
            display(img)
        else:
            from io import BytesIO
            from PIL import Image
            img = Image.open(BytesIO(png))
            img.show()
    else:
        with open(save, 'wb') as f:
            f.write(png)
    return


COLORS_CYCLE = ['darkgreen', 'darkblue', 'darkred', 'darkorange', 'darkviolet']


def show(P: Poset, *functions: PartialEndomorphism, method='auto', labels=None,
         save=None):
    '''
    Use graphviz to display or save P as a Hasse diagram.
    The argument "method" (string) only affects visualization
    of the endomorphisms [f1, f2, ...] (if given). It can be
        - arrows: blue arrow from each node i to f[i]
        - labels: replace the label i of each node with f[i]
        - labels_bottom: (no label at i if f[i]=bottom)
        - arrows_bottom: (no arrow at i if f[i]=bottom)
        - auto: 'arrows_bottom' if P is a lattice and f preserves lub. 'arrows' otherwise.
    Hidding bottom is only allowed if P.bottom makes sense.
    '''
    methods = ('auto', 'labels', 'arrows', 'labels_bottom', 'arrows_bottom')
    assert method in methods, f'Unknown method "{method}"'

    L = P.as_lattice(check=False)
    if method == 'auto' and functions:
        method = 'arrows'
    n = P.n
    child = P.child
    extra_edges = []
    enabled = not method.endswith('_bottom')
    ok = lambda fi: enabled or fi != L.bottom
    f_edges = lambda f: [(i, int(f[i]))
                         for i in range(n)
                         if f[i] != None and ok(f[i])]
    if labels is None:
        labels = P._labels

    if functions and method.startswith('labels'):
        assert len(
            functions) == 1, 'Only one function is allowed for method="labels"'

        gr = [[] for _ in range(n)]
        for i, fi in f_edges(functions[0]):
            gr[fi].append(i)
        labels = [','.join(map(str, l)) for l in gr]

    colors = itertools.cycle(COLORS_CYCLE)

    for f in functions:
        extra_edges.append((next(colors), f_edges(f)))

    edges = [(i, j) for i in range(n) for j in range(n) if child[j, i]]
    graphviz(n, edges, labels=labels, extra_edges=extra_edges, save=save)
    return
