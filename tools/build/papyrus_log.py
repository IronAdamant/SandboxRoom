"""Switch the game's Papyrus script log on or off, for debugging the mod's scripts in-game.

    python tools/build/papyrus_log.py on     # then: python tools/build/compile.py --game "..." --debug
    python tools/build/papyrus_log.py off    # then: python tools/build/compile.py --game "..."  (release)
    python tools/build/papyrus_log.py        # show the current state

"on" adds a [Papyrus] section to Fallout4Custom.ini; "off" removes exactly that section again, leaving the rest
of the file alone. The log is written to Documents/My Games/Fallout4/Logs/Script/Papyrus.0.log (the newest
session; older ones are Papyrus.1.log and up). Debug.Trace lines only appear with scripts compiled with --debug:
release builds strip them.
"""
from __future__ import annotations

import sys
from pathlib import Path

INI = Path.home() / 'Documents' / 'My Games' / 'Fallout4' / 'Fallout4Custom.ini'
SECTION = ['[Papyrus]', 'bEnableLogging=1', 'bEnableTrace=1', 'bLoadDebugInformation=1']


def strip(lines: list[str]) -> list[str]:
    """The ini without its [Papyrus] section (header and keys up to the next section)."""
    out, skipping = [], False
    for line in lines:
        if line.strip().startswith('['):
            skipping = line.strip().lower() == '[papyrus]'
        if not skipping:
            out.append(line)
    return out


def main():
    lines = INI.read_text(encoding='utf8').splitlines() if INI.exists() else []
    on = any(l.strip().lower() == '[papyrus]' for l in lines)
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    if arg == 'on':
        INI.write_text('\n'.join(strip(lines) + SECTION) + '\n', encoding='utf8')
        print(f'Papyrus logging on ({INI})')
    elif arg == 'off':
        INI.write_text('\n'.join(strip(lines)) + '\n', encoding='utf8')
        print(f'Papyrus logging off ({INI})')
    else:
        print(f'Papyrus logging is {"on" if on else "off"} ({INI}); usage: papyrus_log.py on|off')


if __name__ == '__main__':
    main()
