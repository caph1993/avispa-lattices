from packaging.version import parse
from inspect import getsourcefile, getattr_static, getsourcelines
from typing import List, Optional
from . import _VERSION
from . import _REQUIREMENTS
from . import _PACKAGES

assert _VERSION.__doc__
assert _REQUIREMENTS.__doc__
assert _PACKAGES.__doc__
VERSION: str = _VERSION.__doc__.strip()
REQUIREMENTS: List[str] = _REQUIREMENTS.__doc__.strip().splitlines()
PACKAGES: List[str] = _PACKAGES.__doc__.strip().splitlines()

GITHUB = 'https://github.com/caph1993/avispa-lattices'
PYPI = 'https://pypi.org/project/avispa-lattices'
FOLDER_NAME = 'avispa_lattices'


def github(library_object, property: Optional[str] = None):

    if property is not None:
        library_object = getattr_static(library_object, property)
        if hasattr(library_object, '_method'):
            library_object = library_object._method

    file_path = getsourcefile(library_object)
    if file_path is not None:
        _, line_number = getsourcelines(library_object)
        i = file_path.find(f'/{FOLDER_NAME}/')
        if i != -1:
            file_path = file_path[i:]
            return f'{GITHUB}/tree/master{file_path}#L{line_number}'
    return None


def version_is_at_least(a: str):
    version_a = parse(a)
    return parse(VERSION) >= version_a
