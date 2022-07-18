from setuptools import setup, find_packages
from pathlib import Path
import re

work_dir = Path(__file__).parent
with open(work_dir / 'avispa_lattices' / '_version.py', 'r') as f:
    VERSION = re.search(r'^VERSION *= *\'(.*)\'$', f.read(), re.M)
    assert VERSION is not None
    VERSION = VERSION.group(1)

setup(
    name='avispa-lattices',
    version=VERSION,
    description='Toolbox for finite lattices',
    url='https://github.com/caph1993/avispa-lattices',
    author='Carlos Pinzón',
    author_email='caph1993@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'typing-extensions',
        'pillow',
        'ipython',
        'xxhash',
        'pydotplus',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)