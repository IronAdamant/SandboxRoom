"""Build every Sandbox Room plugin in the game's Data folder, then copy them into data/.

    python tools/build/build.py --ack "D:/Coding Projects/AgentCreationKit"

Steps: regenerate work/spec.txt and the sign assets (installed into Data), run tools/xedit/build.pas through AgentCreationKit's unattended xEdit runner
(loading the add-ons that already exist so they are updated, not recreated), copy the plugins to data/.
Safe to re-run: see build.pas. Requires work/scan/*.tsv from tools/xedit/scan.pas.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1].parent
sys.path.insert(0, str(Path(__file__).parent))
import make_spec  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True, help='AgentCreationKit checkout')
    ap.add_argument('--game', default='D:/Steam/steamapps/common/Fallout 4')
    a = ap.parse_args()
    sys.path.insert(0, a.ack)
    refuse_if_ck_running()
    make_spec.main()
    import signs
    signs.install(signs.build(a.ack, Path(a.game)), Path(a.game))
    print('signs made and installed')
    data = Path(a.game) / 'Data'
    addons = [f'Sandbox Room - {d.title}.esp' for d in make_spec.DLCS]
    cmd = [sys.executable, '-m', 'ack', 'xedit', 'run', str(REPO / 'tools' / 'xedit' / 'build.pas'), make_spec.MAIN,
           '--save', '--timeout', '900', '--param', f'SPEC={make_spec.SPEC}']
    for name in addons:
        if (data / name).exists():
            cmd += ['--also-load', name]
    r = subprocess.run(cmd, cwd=a.ack, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0 or 'done in' not in r.stdout:
        raise SystemExit('xEdit run failed')
    run_dir = sorted(Path(a.ack, 'private', 'runs').glob('*-build'))[-1]
    result = (run_dir / 'result.txt').read_text(encoding='utf8').splitlines()
    print(result[0])
    for line in result:
        if line.startswith('ERROR'):
            print(' ', line)
    check_masters(data)
    for name in [make_spec.MAIN] + addons:
        shutil.copy(data / name, REPO / 'data' / name)
    print('copied plugins to data/')


def refuse_if_ck_running() -> None:
    """A Creation Kit left open holds its own copy of the plugins: one save from it (a stray Ctrl+S) writes that
    stale copy over the build. Close it first."""
    r = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq CreationKit.exe', '/NH'], capture_output=True, text=True)
    if 'CreationKit.exe' in r.stdout:
        raise SystemExit('the Creation Kit is running: close it (without saving) before building')


def check_masters(data: Path) -> None:
    """Each plugin may only need Fallout 4, its own DLC and the main plugin. Saving the main plugin in the
    Creation Kit while the add-ons (and so the DLC) are loaded makes its navmesh index (NAVI) pick up DLC entries
    and DLC masters, which would make the base plugin require every DLC."""
    from ack.plugin import Plugin
    allowed = {make_spec.MAIN: ['Fallout4.esm']}
    for d in make_spec.DLCS:
        allowed[f'Sandbox Room - {d.title}.esp'] = ['Fallout4.esm', d.master, make_spec.MAIN]
    for name, masters in allowed.items():
        got = Plugin.load(data / name).masters
        if got != masters:
            raise SystemExit(f'{name} has masters {got}, expected {masters}')
    print('masters OK')


if __name__ == '__main__':
    main()
