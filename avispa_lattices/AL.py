from ._version import VERSION

# Classes and functions
from .base import Poset, Relation, Lattice
from .base_generation.exhaustive import all_lattices
from .base_generation.random import lattice as random_lattice

# Modules
from . import flags
from .base_methods import endomorphisms, validation
from .base_generation import random, exhaustive

# from typing import TYPE_CHECKING, Iterable, Callable, List, Optional, Union, cast
# if TYPE_CHECKING:
#     from .base import Endomorphism
