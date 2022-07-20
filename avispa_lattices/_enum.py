from typing_extensions import Literal, get_args as literal_args
from typing import Tuple

f_glb_method = Literal['auto', 'GMeet', 'GMeet+', 'DMeet+', 'JMeet', 'CMeet',]
f_glb_methods: Tuple[str] = literal_args(f_glb_method)

random_poset_method = Literal['auto', 'p_threshold']
random_poset_methods: Tuple[str] = literal_args(random_poset_method)

random_lattice_method = Literal['auto', 'Czech']
random_lattice_methods: Tuple[str] = literal_args(random_lattice_method)

f_iter_method = Literal['auto', 'lub', 'all', 'monotones', 'lub_no_bottom']
f_iter_methods: Tuple[str] = literal_args(f_iter_method)

random_f_method = Literal['auto', 'arbitrary', 'monotone', 'lub', 'monotone_A',
                          'monotone_B']
random_f_methods: Tuple[str] = literal_args(random_f_method)