from setuptools import setup, find_packages
from typing import List
import ast
from pathlib import Path

work_dir = Path(__file__).parent
package_dir = work_dir / 'avispa_lattices'
pkg_info_dir = package_dir / 'package_info'


class ConstantPyFile:

    def __init__(self, key: str):
        assert key == key.upper(), f'{key} must be upper case'
        self.path = package_dir / 'package_info' / f'_{key}.py'

    def read(self) -> str:
        if not self.path.exists():
            self.write('0.0.0')
        return ast.literal_eval(self.path.read_text()).strip()

    def write(self, text: str):
        text = f"'''\n{text}\n'''"
        ast.literal_eval(text)  # Check that text can be quoted
        return self.path.write_text(text)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.path})'


VERSION: str = ConstantPyFile('VERSION').read()
REQUIREMENTS: List[str] = ConstantPyFile('REQUIREMENTS').read().splitlines()

if __name__ == '__main__':
    setup(
        name='avispa-lattices',
        version=VERSION,
        description='Toolbox for finite lattices',
        url='https://github.com/caph1993/avispa-lattices',
        author='Carlos Pinzón',
        author_email='caph1993@gmail.com',
        license='MIT',
        packages=find_packages(),
        install_requires=REQUIREMENTS,
        classifiers=[
            'Development Status :: 1 - Planning',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
        ],
    )