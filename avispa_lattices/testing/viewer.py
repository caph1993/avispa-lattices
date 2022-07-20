from pathlib import Path
import random
import traceback
import platform, subprocess, webbrowser
from tempfile import TemporaryDirectory
from typing import Any, Iterable, List, Optional, Union, cast
import argparse, glob, re, sys
from subprocess import Popen
import PySimpleGUI as sg
from PIL import Image


def open_file(path: Path):
    if platform.system() == "Windows":
        webbrowser.open(str(path))
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
    return


__all__ = ['launch']
TMP_PREFIX = '-tmp-viewer-'


def naturally_sorted(l: Iterable[Path]):

    def atoi(text: str):
        try:
            return (float(text), text)
        except ValueError:
            return (0, text)

    def natural_keys(text: Path):
        re_float = r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)'
        return [atoi(c) for c in re.split(re_float, str(text))]

    return sorted(l, key=natural_keys)


def main():
    sg.set_options(font=("monospace", "12"))
    sg.theme('dark')

    parser = argparse.ArgumentParser(
        prog=None,
        description='Display images of current directory in a GUI with slider',
    )
    parser.parse_args()
    try:
        with open('stdout.log', 'w') as f, open('stderr.log', 'w') as g:
            sys.stdout = f
            sys.stderr = g
            main_GUI()
    except Exception as e:
        sg.popup_error(f'{e}\n\n{traceback.format_exc()}')
    finally:
        cwd = Path('.').absolute()
        if cwd.name.startswith(TMP_PREFIX):
            try:
                for f in cwd.iterdir():
                    f.unlink()
                cwd.rmdir()
            except:
                pass
    return


def main_GUI():
    cwd = Path('.').absolute()
    layout = [
        [
            sg.Text('Scanning'),
            sg.Text(cwd),
            sg.Text('-', key='running', background_color='gray'),
        ],
        [
            sg.Slider(
                range=(0, 0),
                default_value=0,
                key='slider',
                orientation='h',
                enable_events=True,
            ),
            sg.Button('Open folder', key='cwd'),
            sg.Text('', key='filename'),
        ],
        [sg.Image(source=None, key='image')],
        [sg.Multiline(key='txt', size=(40, 10), disabled=True)],
    ]
    location = (random.randint(-50, 50), random.randint(-50, 50))
    window = sg.Window('Image viewer', layout, relative_location=location,
                       return_keyboard_events=True)
    files: List[Path] = []
    gmtime = 0.0
    txt_gmtime = 0.0
    running = '...  '
    running_seq = {
        '...  ': ' ... ',
        ' ... ': '  ...',
        '  ...': '.  ..',
        '.  ..': '..  .',
        '..  .': '...  ',
    }
    timeout = 250
    while True:
        event, values = window.read(timeout=timeout)
        if event == sg.WIN_CLOSED:
            break
        elif event == 'cwd':
            open_file(cwd)
            continue
        running = running_seq[running]
        window['running'].update(running)
        idx = int(values['slider'])
        prev_files = files
        files = naturally_sorted(Path(f) for f in glob.glob('*.png'))
        prev_timeout = timeout
        timeout = prev_timeout * 0.8
        if event.startswith('Left'):
            idx = max(0, idx - 1)
            event = 'slider'
            window['slider'].update(value=idx)
        elif event.startswith('Right'):
            idx = min(idx + 1, len(files) - 1)
            event = 'slider'
            window['slider'].update(value=idx)

        if len(files) == 0:
            window['image'].update(source=None)
            window['filename'].update('')
            window['slider'].update(range=(0, 0))
            window['slider'].update(value=0)
        elif files != prev_files or idx >= len(files):
            if idx == max(0, len(prev_files) - 1) or idx >= len(files):
                i = len(files) - 1
            else:
                i = idx
            try:
                Image.open(files[i])
                window['image'].update(source=f'{files[i]}')
                window['filename'].update(f'{files[i].name}')
            except:
                print(traceback.format_exc())
                files = prev_files
            else:
                window['slider'].update(range=(0, len(files) - 1))
                window['slider'].update(value=i)
        elif event == 'slider':
            try:
                Image.open(files[idx])
                window['image'].update(source=f'{files[idx]}')
                window['filename'].update(f'{files[idx].name}')
            except:
                print(traceback.format_exc())
                files = prev_files
        elif idx < len(files) and files[idx].stat().st_mtime != gmtime:
            gmtime = files[idx].stat().st_mtime
            try:
                window['image'].update(source=None)
                window['image'].update(source=f'{files[idx]}')
                window['filename'].update(f'{files[idx].name}')
            except:
                files = prev_files
        else:
            timeout = prev_timeout / 0.9
        timeout = max(80, min(timeout, 3000))

        if idx < len(files):
            txt_file = files[idx].parent / (files[idx].stem + '.txt')
            if txt_file.is_file():
                prev_txt_gmtime = txt_gmtime
                txt_gmtime = txt_file.stat().st_mtime
                if txt_gmtime != prev_txt_gmtime:
                    with txt_file.open('r') as f:
                        window['txt'].update(f.read())
            else:
                window['txt'].update('')
    return


def launch(tmp_dir: Optional[Path] = None):
    if tmp_dir is None:
        tmp_dir = Path(TemporaryDirectory(prefix=TMP_PREFIX).name)
        tmp_dir.mkdir(exist_ok=True)

    Popen([sys.executable, __file__], cwd=tmp_dir)
    return tmp_dir


if __name__ == '__main__':
    main()