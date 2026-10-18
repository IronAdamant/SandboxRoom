"""Check the Xbox archives the Creation Kit generated, before uploading them.

    python tools/build/check_xbox.py [--dir "D:/Steam/steamapps/common/Fallout 4/Data"]

The Xbox archives must come from the Creation Kit's Generate (Upload Plugin and Archive to Bethesda.net): it tiles
the textures for the console. Archive2's XBoxDDS format does not: it keeps the PC layout (tile mode 8), which is
what 1.0.0 shipped to Xbox (Xbox players reported pink signs). Checked here:
    Sandbox Room - Main_xbox.ba2      every script, sign model and material in data/, and no vanilla scripts;
                                      each script identical to data/ (archives generated before a rebuild are stale)
    Sandbox Room - Textures_xbox.ba2  every sign texture in data/, none in the PC layout
"""
from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / 'data'
PC_TILE_MODE = 8           # what Archive2 writes for PC, and for XBoxDDS; the CK's Xbox textures have 13


def read_ba2(path: Path, contents: dict | None = None) -> tuple[bytes, dict[str, int | None]]:
    """The archive type (GNRL or DX10) and its files: normalised path -> tile mode (None for GNRL). contents, if
    given, receives a GNRL archive's file contents by path."""
    b = path.read_bytes()
    magic, ver, typ, n, names_at = struct.unpack('<4sI4sIQ', b[:24])
    if magic != b'BTDX':
        raise SystemExit(f'{path.name}: not a BA2 archive')
    o, tiles, blobs = 24, [], []
    for _ in range(n):
        if typ == b'GNRL':
            tiles.append(None)
            offset, packed, size = struct.unpack('<QII', b[o + 16:o + 32])
            blob = b[offset:offset + (packed or size)]
            blobs.append(zlib.decompress(blob) if packed else blob)
            o += 36
        else:
            chunks, tile = b[o + 13], b[o + 23]
            tiles.append(tile)
            o += 24 + 24 * chunks
    files = {}
    for k, tile in enumerate(tiles):
        size = struct.unpack('<H', b[names_at:names_at + 2])[0]
        name = b[names_at + 2:names_at + 2 + size].decode().replace('\\', '/').lower()
        files[name] = tile
        if contents is not None and blobs:
            contents[name] = blobs[k]
        names_at += 2 + size
    return typ, files


def expected(kinds: tuple[str, ...], suffix: str = '') -> set[str]:
    return {f.relative_to(DATA).as_posix().lower() for kind in kinds for f in (DATA / kind / 'SandboxRoom').rglob('*')
            if f.is_file() and f.name.lower().endswith(suffix)}


def check(path: Path, typ_wanted: bytes, want: set[str]) -> list[str]:
    if not path.exists():
        return [f'{path.name}: missing']
    contents: dict = {}
    typ, files = read_ba2(path, contents)
    problems = [f'{path.name}: {typ.decode()} archive, expected {typ_wanted.decode()}'] if typ != typ_wanted else []
    problems += [f'{path.name}: stale (differs from data/, generate again): {f}' for f in sorted(want & contents.keys())
                 if f.endswith('.pex') and contents[f] != (DATA / f).read_bytes()]
    problems += [f'{path.name}: missing {f}' for f in sorted(want - files.keys())]
    problems += [f'{path.name}: not part of the mod: {f}' for f in sorted(files.keys() - want)
                 if not f.startswith('scripts/source/user/sandboxroom/')]  # the script sources are harmless
    problems += [f'{path.name}: PC layout (not tiled for Xbox): {f}' for f, tile in sorted(files.items())
                 if tile == PC_TILE_MODE]
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='D:/Steam/steamapps/common/Fallout 4/Data',
                    help='folder holding the generated _xbox archives')
    d = Path(ap.parse_args().dir)
    problems = (check(d / 'Sandbox Room - Main_xbox.ba2', b'GNRL',
                      expected(('Scripts',), '.pex') | expected(('Meshes', 'Materials')))
                + check(d / 'Sandbox Room - Textures_xbox.ba2', b'DX10', expected(('Textures',))))
    for p in problems:
        print(p)
    if problems:
        raise SystemExit(f'{len(problems)} problem(s): do not upload these Xbox archives')
    print('Xbox archives OK: all files present, textures tiled for Xbox')


if __name__ == '__main__':
    main()
