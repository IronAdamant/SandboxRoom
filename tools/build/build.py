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
    make_spec.main()
    import signs
    signs.install(signs.build(a.ack, Path(a.game)), Path(a.game))
    print('signs made and installed')
    data = Path(a.game) / 'Data'
    addons = []  # one plugin since 1.0: the DLC content is in Sandbox Room.esp
    cmd = [sys.executable, '-m', 'ack', 'xedit', 'run', str(REPO / 'tools' / 'xedit' / 'build.pas'), make_spec.MAIN,
           '--save', '--timeout', '900', '--param', f'SPEC={make_spec.SPEC}']
    for name in addons:
        if (data / name).exists():
            cmd += ['--also-load', name]
    r = subprocess.run(cmd, cwd=a.ack, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0 or 'done in' not in r.stdout:
        # ack refuses a saving run while a Creation Kit that could save over the plugin is open (a stale CK save
        # once overwrote a build): close it with python -m ack ck close, or by hand without saving
        raise SystemExit('xEdit run failed')
    run_dir = sorted(Path(a.ack, 'private', 'runs').glob('*-build'))[-1]
    result = (run_dir / 'result.txt').read_text(encoding='utf8').splitlines()
    print(result[0])
    for line in result:
        if line.startswith('ERROR'):
            print(' ', line)
    check_masters(data)
    check_errors(a.ack)
    for name in [make_spec.MAIN] + addons:
        shutil.copy(data / name, REPO / 'data' / name)
    print('copied plugins to data/')


def check_masters(data: Path) -> None:
    """The plugin needs exactly Fallout 4 and the DLC in DLC_MASTERS, in load order: nothing else (a Creation Kit
    save with other plugins loaded can add masters through the navmesh index, NAVI)."""
    from ack.plugin import Plugin
    allowed = {make_spec.MAIN: ['Fallout4.esm'] + make_spec.DLC_MASTERS}
    for name, masters in allowed.items():
        got = Plugin.load(data / name).masters
        if got != masters:
            raise SystemExit(f'{name} has masters {got}, expected {masters}')
    print('masters OK')


def check_errors(ack: str) -> None:
    """xEdit's Check for Errors over the built plugin: a record xEdit wrote wrongly (1.1: removing a script property
    in place left the arena zone's script data corrupt) fails the build instead of the game."""
    r = subprocess.run([sys.executable, '-m', 'ack', 'xedit', 'run', 'check_errors', make_spec.MAIN, '--timeout', '900'],
                       cwd=ack, capture_output=True, text=True)
    run_dir = sorted(Path(ack, 'private', 'runs').glob('*-check_errors'))[-1]
    report = (run_dir / 'errors.txt').read_text(encoding='utf8', errors='replace') if r.returncode == 0 else r.stdout
    print(report.splitlines()[0] if report else 'check_errors: no report')
    if r.returncode != 0 or ' 0 with errors' not in report.splitlines()[0]:
        print(report)
        raise SystemExit('the plugin has records with errors (xEdit Check for Errors)')


if __name__ == '__main__':
    main()
