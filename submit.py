from typing import List, Literal
from setup import find_packages, ConstantPyFile
from subprocess import check_output, run, PIPE
from pathlib import Path
import os, sys

work_dir = Path(__file__).absolute().parent


def main():
    '''
    1. Set the new VERSION in package_info (also REQUIREMENTS, etc.)
    2. Submit the package to PyPI
    3. Commit the changes to the package_info.py file
    4. Reinstall the package locally
    '''
    os.chdir(work_dir)

    VERSION = '3.0.25'
    PACKAGES = find_packages()
    REQUIREMENTS = find_requirements()

    ConstantPyFile('VERSION').write(VERSION)
    ConstantPyFile('REQUIREMENTS').write('\n'.join(REQUIREMENTS))
    ConstantPyFile('PACKAGES').write('\n'.join(PACKAGES))

    name, version = info_from_setup()
    print(name, version)

    assert version == VERSION

    run('rm ./dist/*', shell=True, check=False, stderr=PIPE)
    run('python3 setup.py check', shell=True, check=True)
    run('python3 setup.py sdist', shell=True, check=True)

    print('---')
    print(*PACKAGES, sep='\n', end='\n---\n')
    print(*REQUIREMENTS, sep='\n', end='\n---\n')
    print(VERSION)

    run('twine upload dist/*', shell=True, check=True, stdin=sys.stdin)

    run('git add .', shell=True, check=True)
    run(f'git commit -m "v{version} of {name}"', shell=True, check=True)
    run('git push', shell=True, check=True)

    run(f'pip3 install --upgrade {name}', shell=True, check=True)
    run(f'pip3 install --upgrade {name}', shell=True, check=True)


def info_from_setup():
    p = run('python3 setup.py --name', shell=True, stdout=PIPE, check=True)
    name = p.stdout.decode().strip()
    p = run('python3 setup.py --version', shell=True, stdout=PIPE, check=True)
    version = p.stdout.decode().strip()
    check = version.replace('.', '').isdigit()
    assert check, f'v{version} Must be numerical (security check)'
    assert ' ' not in name, f'"{name}" must not have spaces (security check)'
    return name, version



def find_requirements() -> List[str]:
    p = run(['pipreqs', '--mode', 'no-pin', '--print', 'avispa_lattices'],
            cwd=work_dir, capture_output=True)
    return p.stdout.decode().strip().splitlines()


if __name__ == '__main__':
    main()
