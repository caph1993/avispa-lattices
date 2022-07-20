from packaging.version import parse
from inspect import getsourcefile, getattr_static, getsourcelines, isclass, ismodule
from typing import Any, List, Optional, Type
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


def github(library_object=None, property: Optional[str] = None):

    if library_object is None:
        return GITHUB

    if property is not None:
        library_object = getattr_static(library_object, property)
        if hasattr(library_object, '_method'):
            library_object = library_object._method

    def get_url(obj):
        try:
            file_path = getsourcefile(obj)
            assert file_path is not None
            _, line_number = getsourcelines(obj)
            i = file_path.find(f'/{FOLDER_NAME}/')
            assert i != -1
            file_path = file_path[i:]
            return f'{GITHUB}/tree/master{file_path}#L{line_number}'
        except (TypeError, AssertionError):
            return None

    url = get_url(library_object)
    if url is None and not isclass(library_object):
        url = get_url(library_object.__class__)
    return url


def version_is_at_least(a: str):
    version_a = parse(a)
    return parse(VERSION) >= version_a


def check_external_dependencies():
    import pydotplus
    import warnings
    if pydotplus.find_graphviz() is None:
        warnings.warn(
            'Graphviz was not found, you will not be able to display lattices graphically.\n'
            'Install graphviz from https://www.graphviz.org/download/.\n'
            'After installation, make sure that graphviz is in your PATH, and if you are using Jupyter, restart the Jupyter server completely to reload the PATH inside all your notebooks.\n'
        )