from inspect import getsourcefile, getattr_static, getsourcelines
from types import ModuleType
from typing import Optional, Union

GITHUB = 'https://github.com/caph1993/avispa-lattices'
PYPI = 'https://pypi.org/project/avispa-lattices'


def github(library_object, property: Optional[str] = None):

    if property is not None:
        library_object = getattr_static(library_object, property)
        if hasattr(library_object, '_method'):
            library_object = library_object._method

    s = getsourcefile(library_object)
    if s is not None:
        _, line_number = getsourcelines(library_object)
        i = s.find('/avispa_lattices/')
        if i != -1:
            s = s[i:]
            return f'{GITHUB}/tree/master{s}#L{line_number}'
    return None
