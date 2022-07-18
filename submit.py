from subprocess import check_output, run, PIPE
from pathlib import Path
import os, sys

work_dir = Path(__file__).absolute().parent
os.chdir(work_dir)


def info():
    p = run('python3 setup.py --name', shell=True, stdout=PIPE, check=True)
    name = p.stdout.decode().strip()
    p = run('python3 setup.py --version', shell=True, stdout=PIPE, check=True)
    version = p.stdout.decode().strip()
    check = version.replace('.', '').isdigit()
    assert check, f'v{version} Must be numerical (security check)'
    assert ' ' not in name, f'"{name}" must not have spaces (security check)'
    return name, version


def submit():
    run('rm ./dist/*', shell=True, check=False, stderr=PIPE)
    run('python3 setup.py check', shell=True, check=True)
    run('python3 setup.py sdist', shell=True, check=True)
    run('twine upload dist/*', shell=True, check=True, stdin=sys.stdin)
    return


name, version = info()
print(name, version)

# p = run(
#     [sys.executable, '-m', 'pip-missing-reqs', work_dir / name],
#     check=True,
#     capture_output=True,
# )
# requirements = p.stdout.decode()
# print('Updating requirements...')
# with open(work_dir / 'requirements.txt', 'w') as f:
#     f.write(requirements)
# print(requirements)

submit()

run('git add .', shell=True, check=True)
run(f'git commit -m "v{version} of {name}"', shell=True, check=True)
run('git push', shell=True, check=True)

run(f'pip3 install --upgrade {name}', shell=True, check=True)
run(f'pip3 install --upgrade {name}', shell=True, check=True)
