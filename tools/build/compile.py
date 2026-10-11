"""Compile the Papyrus sources in source/User with the Creation Kit's compiler into data/Scripts.

    python tools/build/compile.py --game "D:/Steam/steamapps/common/Fallout 4"            # every script
    python tools/build/compile.py --game "..." SandboxRoom:HolotapeScript                 # just these
    python tools/build/compile.py --game "..." --debug                                    # keep Debug.Trace

Compiles against the game's vanilla sources only (Data/Scripts/Source/Base), never F4SE's: the mod must work
without F4SE.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'source' / 'User'
OUTPUT = REPO / 'data' / 'Scripts'


def all_scripts() -> list[str]:
    return [':'.join(p.relative_to(SOURCE).with_suffix('').parts) for p in sorted(SOURCE.rglob('*.psc'))]


def compile_script(game: Path, name: str, debug: bool = False) -> Path:
    base = game / 'Data' / 'Scripts' / 'Source' / 'Base'
    compiler = game / 'Papyrus Compiler' / 'PapyrusCompiler.exe'
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([str(compiler), name, f'-i={SOURCE};{base}', f'-o={tmp}',
                            f'-f={base / "Institute_Papyrus_Flags.flg"}', '-quiet'] + ([] if debug else ['-release', '-final']),
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f'compile failed for {name}:\n{r.stdout}\n{r.stderr}')
        built = next(Path(tmp).rglob(name.split(':')[-1] + '.pex'))
        dest = OUTPUT.joinpath(*name.split(':')[:-1]) / built.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(built, dest)
        return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', required=True)
    ap.add_argument('--debug', action='store_true', help='keep Debug.Trace calls (release builds strip them)')
    ap.add_argument('scripts', nargs='*', help='script names with ":" namespaces; default: all of source/User')
    a = ap.parse_args()
    for name in a.scripts or all_scripts():
        print('compiled', compile_script(Path(a.game), name, a.debug).relative_to(REPO))


if __name__ == '__main__':
    main()
