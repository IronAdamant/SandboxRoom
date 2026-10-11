"""Package a release: BA2 archives for PC and Xbox, and the Nexus zip.

    python tools/build/package.py --version 1.0.0 [--game "D:/Steam/steamapps/common/Fallout 4"]

Fallout 4 loads "<plugin> - Main.ba2" and "<plugin> - Textures.ba2" beside a plugin by themselves, so every loose
file the mod needs goes into the plugin's two archives:
    Sandbox Room - Main.ba2      Scripts (compiled, plus sources), sign models and materials   (General)
    Sandbox Room - Textures.ba2  sign textures                                                 (DDS)
The Creation Kit's Bethesda.net upload looks for the Xbox versions as "<plugin> - Main_xbox.ba2" and
"- Textures_xbox.ba2" (XBoxDDS textures, Xbox compression).
Output in dist/:
    PC/      Sandbox Room.esp + the PC archives          (Bethesda.net PC upload)
    Xbox/    Sandbox Room.esp + the _xbox archives       (Bethesda.net Xbox upload: copy beside the plugin in Data)
    Sandbox Room <version>.zip   for Nexus: the plugin, the PC archives and the readme, laid out as Data
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / 'data'
DIST = REPO / 'dist'
MAIN = 'Sandbox Room.esp'


def stage(tmp: Path) -> Path:
    """The loose files laid out as a Data folder."""
    root = tmp / 'Data'
    shutil.copytree(DATA / 'Scripts' / 'SandboxRoom', root / 'Scripts' / 'SandboxRoom')
    shutil.copytree(REPO / 'source' / 'User' / 'SandboxRoom', root / 'Scripts' / 'Source' / 'User' / 'SandboxRoom')
    for kind in ('Meshes', 'Materials', 'Textures'):
        shutil.copytree(DATA / kind / 'SandboxRoom', root / kind / 'SandboxRoom')
    return root


def archive2(game: Path, root: Path, folders: list[str], out: Path, fmt: str, compression: str) -> None:
    exe = game / 'Tools' / 'Archive2' / 'Archive2.exe'
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([str(exe), ','.join(str(root / f) for f in folders), f'-create={out}', f'-root={root}',
                        f'-format={fmt}', f'-compression={compression}', '-quiet'], capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        raise SystemExit(f'Archive2 failed for {out.name}:\n{r.stdout}\n{r.stderr}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', required=True)
    ap.add_argument('--game', default='D:/Steam/steamapps/common/Fallout 4')
    a = ap.parse_args()
    game = Path(a.game)
    if DIST.exists():
        shutil.rmtree(DIST)
    tmp = DIST / '_stage'
    root = stage(tmp)
    for platform, suffix, tex_fmt, comp in (('PC', '', 'DDS', 'Default'), ('Xbox', '_xbox', 'XBoxDDS', 'XBox')):
        out = DIST / platform
        archive2(game, root, ['Scripts', 'Meshes', 'Materials'], out / f'Sandbox Room - Main{suffix}.ba2', 'General', comp)
        archive2(game, root, ['Textures'], out / f'Sandbox Room - Textures{suffix}.ba2', tex_fmt, comp)
        shutil.copy(DATA / MAIN, out / MAIN)
    zpath = DIST / f'Sandbox Room {a.version}.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in (MAIN, 'Sandbox Room - Main.ba2', 'Sandbox Room - Textures.ba2'):
            z.write(DIST / 'PC' / name, name)
        z.write(REPO / 'docs' / 'release' / 'Sandbox Room - Readme.txt', 'Sandbox Room - Readme.txt')
    shutil.rmtree(tmp)
    for f in sorted(DIST.rglob('*')):
        if f.is_file():
            print(f'{f.relative_to(DIST)}  {f.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
