"""Package a release: the PC BA2 archives and the Nexus zip.

    python tools/build/package.py --version 1.0.0 [--game "D:/Steam/steamapps/common/Fallout 4"]

Fallout 4 loads "<plugin> - Main.ba2" and "<plugin> - Textures.ba2" beside a plugin by themselves, so every loose
file the mod needs goes into the plugin's two archives:
    Sandbox Room - Main.ba2      Scripts (compiled, plus sources), sign models and materials   (General)
    Sandbox Room - Textures.ba2  sign textures                                                 (DDS)
No Xbox archives: Archive2's XBoxDDS format keeps the textures in the PC layout (1.0.0 shipped them so, and Xbox
players reported pink signs). The Creation Kit's Generate makes them at upload; tools/build/check_xbox.py checks
them (docs/release/BETHESDA_NET.md).
Output in dist/:
    PC/      Sandbox Room.esp + the PC archives          (Bethesda.net PC upload)
    Sandbox Room <version>.zip   for Nexus: a FOMOD installer (Vortex, Mod Organizer 2) offering
        00 Packed (Next-Gen)/       the plugin and the PC archives
        01 Loose Files (Old-Gen)/   the plugin and the same files loose
      plus the readme. Archive2 writes BA2 version 8, which only the next-gen game (1.10.980+) reads; the old-gen
      game (1.10.163) reads version 1 only, so its players need the loose files. Manual installs copy the contents
      of one folder into Data.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / 'data'
DIST = REPO / 'dist'
MAIN = 'Sandbox Room.esp'
README = REPO / 'docs' / 'release' / 'Sandbox Room - Readme.txt'
AUTHOR = 'Deadmansprice'
PACKED = '00 Packed (Next-Gen)'
LOOSE = '01 Loose Files (Old-Gen)'
OPTIONS = (  # (folder, installer name, installer description)
    (PACKED, 'Packed (Next-Gen)',
     'For the current game (next-gen update, 1.10.980 or later). The plugin with its two BA2 archives. Recommended.'),
    (LOOSE, 'Loose Files (Old-Gen)',
     'For the old-gen game (1.10.163, before the 2024 next-gen update), which cannot read the packed archives. '
     'The plugin with loose scripts, meshes, materials and textures. Also works on next-gen.'),
)


def fomod_info(version: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<fomod>
  <Name>Sandbox Room</Name>
  <Author>{AUTHOR}</Author>
  <Version>{escape(version)}</Version>
  <Description>A testing facility reached by holotape: crafting stations, never-empty cabinets, a target range, an arena and a Perks &amp; Stats room.</Description>
</fomod>
'''


def fomod_config() -> str:
    plugins = ''.join(f'''
          <plugin name="{escape(name)}">
            <description>{escape(desc)}</description>
            <files><folder source="{escape(folder)}" destination="" priority="0"/></files>
            <typeDescriptor><type name="{'Recommended' if folder == PACKED else 'Optional'}"/></typeDescriptor>
          </plugin>''' for folder, name, desc in OPTIONS)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
  <moduleName>Sandbox Room</moduleName>
  <installSteps order="Explicit">
    <installStep name="Game version">
      <optionalFileGroups order="Explicit">
        <group name="Which Fallout 4 do you have?" type="SelectExactlyOne">
          <plugins order="Explicit">{plugins}
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
  </installSteps>
</config>
'''


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
    out = DIST / 'PC'
    archive2(game, root, ['Scripts', 'Meshes', 'Materials'], out / 'Sandbox Room - Main.ba2', 'General', 'Default')
    archive2(game, root, ['Textures'], out / 'Sandbox Room - Textures.ba2', 'DDS', 'Default')
    shutil.copy(DATA / MAIN, out / MAIN)
    zpath = DIST / f'Sandbox Room {a.version}.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('fomod/info.xml', fomod_info(a.version))
        z.writestr('fomod/ModuleConfig.xml', fomod_config())
        for name in (MAIN, 'Sandbox Room - Main.ba2', 'Sandbox Room - Textures.ba2'):
            z.write(DIST / 'PC' / name, f'{PACKED}/{name}')
        z.write(DATA / MAIN, f'{LOOSE}/{MAIN}')
        for f in sorted(root.rglob('*')):
            if f.is_file():
                z.write(f, f'{LOOSE}/{f.relative_to(root).as_posix()}')
        z.write(README, 'Sandbox Room - Readme.txt')
    shutil.rmtree(tmp)
    for f in sorted(DIST.rglob('*')):
        if f.is_file():
            print(f'{f.relative_to(DIST)}  {f.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
