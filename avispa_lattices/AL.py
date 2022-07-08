from ._version import VERSION

# Classes and functions
from .base import Lattice, Poset, Relation
from .base_generation.exhaustive import all_lattices
from .base_generation.random import lattice as random_lattice
from .base_generation.random import poset as random_poset
from .functional import f_lub, f_glb, f_iter

# Modules
from . import functional
from .base_methods import validation, graphviz
from .base_generation import random, exhaustive

# from typing import TYPE_CHECKING, Iterable, Callable, List, Optional, Union, cast
# if TYPE_CHECKING:
#     from .base import Endomorphism
