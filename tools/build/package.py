"""Package a release: BA2 archives for PC and Xbox, and the Nexus zip (a FOMOD installer).

    python tools/build/package.py --version 1.0.0 [--game "D:/Steam/steamapps/common/Fallout 4"]

Fallout 4 loads "<plugin> - Main.ba2" and "<plugin> - Textures.ba2" beside a plugin by themselves, so every loose
file the mod needs goes into the main plugin's two archives (the DLC add-ons use the same scripts and signs, so
they need none of their own):
    Sandbox Room - Main.ba2      Scripts (compiled, plus sources), sign models and materials   (General)
    Sandbox Room - Textures.ba2  sign textures                                                 (DDS)
Output in dist/:
    PC/      the plugins and the PC archives: what Bethesda.net's PC upload takes
    Xbox/    the plugins and the Xbox archives (XBoxDDS textures, Xbox compression)
    Sandbox Room <version>.zip   for Nexus: a FOMOD that installs the core files and ticks the add-ons of the DLC
                                 the player has
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
ADDONS = [('Automatron', 'DLCRobot.esm'), ('Far Harbor', 'DLCCoast.esm'), ('Nuka-World', 'DLCNukaWorld.esm'),
          ('Contraptions Workshop', 'DLCworkshop02.esm'), ('Vault-Tec Workshop', 'DLCworkshop03.esm')]


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


def fomod(version: str) -> tuple[str, str]:
    info = f"""<fomod>
  <Name>Sandbox Room</Name>
  <Author>Deadmansprice</Author>
  <Version>{version}</Version>
  <Description>A testing facility reached by holotape: refilling storage, crafting stations, a target range with holographic targets and an arena whose enemies wake when you walk in.</Description>
  <Groups><element>Gameplay</element></Groups>
</fomod>
"""
    plugins = []
    for title, master in ADDONS:
        plugins.append(f"""          <plugin name="{title}">
            <description>Adds {title}'s items to the storage cabinets (and its enemies, station or both where it has them). Needs the {title} DLC.</description>
            <files><folder source="Add-ons\\{title}" destination="" priority="0"/></files>
            <typeDescriptor>
              <dependencyType>
                <defaultType name="Optional"/>
                <patterns>
                  <pattern><dependencies operator="And"><fileDependency file="{master}" state="Active"/></dependencies><type name="Recommended"/></pattern>
                  <pattern><dependencies operator="And"><fileDependency file="{master}" state="Missing"/></dependencies><type name="NotUsable"/></pattern>
                </patterns>
              </dependencyType>
            </typeDescriptor>
          </plugin>""")
    config = f"""<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
  <moduleName>Sandbox Room</moduleName>
  <requiredInstallFiles>
    <folder source="Core" destination=""/>
  </requiredInstallFiles>
  <installSteps order="Explicit">
    <installStep name="DLC add-ons">
      <optionalFileGroups order="Explicit">
        <group name="Add-ons for the DLC you own (each needs its DLC)" type="SelectAny">
          <plugins order="Explicit">
{chr(10).join(plugins)}
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
  </installSteps>
</config>
"""
    return info, config


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
    plugins = [MAIN] + [f'Sandbox Room - {t}.esp' for t, _ in ADDONS]
    for platform, tex_fmt, comp in (('PC', 'DDS', 'Default'), ('Xbox', 'XBoxDDS', 'XBox')):
        out = DIST / platform
        archive2(game, root, ['Scripts', 'Meshes', 'Materials'], out / 'Sandbox Room - Main.ba2', 'General', comp)
        archive2(game, root, ['Textures'], out / 'Sandbox Room - Textures.ba2', tex_fmt, comp)
        for p in plugins:
            shutil.copy(DATA / p, out / p)
    # Nexus zip: FOMOD layout
    zpath = DIST / f'Sandbox Room {a.version}.zip'
    info, config = fomod(a.version)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('fomod/info.xml', info)
        z.writestr('fomod/ModuleConfig.xml', config)
        for name in (MAIN, 'Sandbox Room - Main.ba2', 'Sandbox Room - Textures.ba2'):
            z.write(DIST / 'PC' / name, f'Core/{name}')
        for title, _ in ADDONS:
            name = f'Sandbox Room - {title}.esp'
            z.write(DATA / name, f'Add-ons/{title}/{name}')
        z.write(REPO / 'docs' / 'release' / 'Sandbox Room - Readme.txt', 'Core/Sandbox Room - Readme.txt')
    shutil.rmtree(tmp)
    for f in sorted(DIST.rglob('*')):
        if f.is_file():
            print(f'{f.relative_to(DIST)}  {f.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
