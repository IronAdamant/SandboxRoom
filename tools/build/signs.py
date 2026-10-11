"""Make the sign models, materials and textures listed in work/signs.json (written by make_spec.py) into data/,
and install them into the game's Data folder.

    python tools/build/signs.py --ack "D:/Coding Projects/AgentCreationKit" [--game "D:/.../Fallout 4"]

A sign is a copy of a vanilla poster model (one flat rectangle facing local +X; floor signs lie face up) resized to the sign and mapped to
the whole of its own texture, with its collision switched off, pointing at its own material (a copy of the
poster's) that points at its own texture: the sign's text rendered here, saved as DXT1 with mipmaps.
"""
from __future__ import annotations

import argparse
import io
import json
import shutil
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
SIGNS_JSON = REPO / 'work' / 'signs.json'
OUT = REPO / 'data'
POSTER_NIF = r'Meshes\Interiors\Vault\Vault111\SetDressing\V111SafetyPoster01.nif'
POSTER_BGSM = r'Materials\Interiors\Vault\Vault111\V111Signs01.BGSM'
POSTER_TEXTURES = ('Interiors/Vault/Vault111/V111Signs01_d.dds', 'Interiors/Vault/Vault111/V111Signs01_n.dds',
                   'Interiors/Vault/Vault111/V111Signs01_s.dds')
TEX_DIR = 'SandboxRoom/Signs/'
FONT = 'C:/Windows/Fonts/bahnschrift.ttf'
# Lab signage: white text on dark slate, a thin cyan frame; headers get a cyan bar along the bottom.
BACK, TEXT, ACCENT = (24, 34, 44), (236, 242, 246), (64, 196, 230)
TEXTURE_SIZE = {'Label': (512, 128), 'Header': (1024, 256), 'Floor': (1024, 256)}


def render(text: str, kind: str) -> Image.Image:
    w, h = TEXTURE_SIZE[kind]
    im = Image.new('RGB', (w, h), BACK)
    d = ImageDraw.Draw(im)
    edge = h // 16
    d.rectangle([edge, edge, w - 1 - edge, h - 1 - edge], outline=ACCENT, width=max(2, h // 40))
    if kind != 'Label':
        d.rectangle([edge * 3, h - edge * 4, w - 1 - edge * 3, h - edge * 3], fill=ACCENT)
    size = int(h * 0.55)
    while True:
        font = ImageFont.truetype(FONT, size)
        try:
            font.set_variation_by_name('Bold')
        except (OSError, ValueError):
            pass
        box = d.textbbox((0, 0), text, font=font)
        if box[2] - box[0] <= w - 8 * edge or size < 12:
            break
        size -= 2
    tw, th = box[2] - box[0], box[3] - box[1]
    shift = -edge if kind != 'Label' else 0
    d.text(((w - tw) / 2 - box[0], (h - th) / 2 - box[1] + shift), text, font=font, fill=TEXT)
    return im


def dds_dxt1(im: Image.Image) -> bytes:
    """DXT1 with a full mip chain (Pillow writes one level; the levels are joined under one header)."""
    levels, cur = [], im.convert('RGBA')
    while True:
        buf = io.BytesIO()
        cur.save(buf, format='DDS', pixel_format='DXT1')
        data = buf.getvalue()
        levels.append(data)
        if cur.width <= 4 or cur.height <= 4:
            break
        cur = cur.resize((cur.width // 2, cur.height // 2), Image.LANCZOS)
    head = bytearray(levels[0][:128])
    flags, = struct.unpack_from('<I', head, 8)
    struct.pack_into('<I', head, 8, flags | 0x20000)            # DDSD_MIPMAPCOUNT
    struct.pack_into('<I', head, 28, len(levels))
    caps, = struct.unpack_from('<I', head, 108)
    struct.pack_into('<I', head, 108, caps | 0x400008)          # DDSCAPS_COMPLEX | DDSCAPS_MIPMAP
    return bytes(head) + b''.join(level[128:] for level in levels)


def replace_sized(data: bytes, old: str, new: str, prefix_extra: int) -> bytes:
    """Replace one uint32-length-prefixed string (prefix_extra: 1 when the length counts a trailing NUL)."""
    o, n = old.encode('latin1'), new.encode('latin1')
    k = data.find(o)
    assert k >= 4 and struct.unpack_from('<I', data, k - 4)[0] == len(o) + prefix_extra, old
    tail = data[k + len(o):]
    return data[:k - 4] + struct.pack('<I', len(n) + prefix_extra) + n + tail


def make_material(template: bytes, name: str) -> bytes:
    d = template
    for old, new in zip(POSTER_TEXTURES, (f'{TEX_DIR}{name}_d.dds', f'{TEX_DIR}Flat_n.dds', f'{TEX_DIR}Matte_s.dds')):
        d = replace_sized(d, old, new, 1)
    return d


def make_model(template: bytes, name: str, width: float, height: float, ack, floor: bool = False) -> bytes:
    """floor: lay the sign flat, face up, its text read by someone facing +X (the top of the text towards +X)."""
    nif = ack.Nif(template)
    d = nif.data
    for i, typ, start, end in nif.block_ranges():
        if typ == 'NiNode' and i == 0:
            struct.pack_into('<i', d, start + 72, -1)            # no collision object
        if typ == 'BSXFlags':
            v, = struct.unpack_from('<I', d, start + 4)
            struct.pack_into('<I', d, start + 4, v & ~0x2)       # no Havok
        if typ == 'BSTriShape':
            p = start
            _, ne = struct.unpack_from('<iI', d, p)
            p += 8 + 4 * ne + 4 + 4 + 12 + 36 + 4 + 4
            struct.pack_into('<4f', d, p, 0.0, 0.0, 0.0, float(np.hypot(width, height) / 2))  # bounding sphere
            p += 16 + 12
            desc, = struct.unpack_from('<Q', d, p)
            p += 8
            _, nv, _ = struct.unpack_from('<IHI', d, p)
            p += 10
            vsize, uvo = (desc & 0xF) * 4, ((desc >> 8) & 0xF) * 4
            assert nv == 4 and not (desc >> 44) & (1 << 10), 'expected the poster: 4 half-precision vertices'
            for v in range(nv):
                b = p + v * vsize
                x, y, z, bt = np.frombuffer(bytes(d[b:b + 8]), dtype='<f2')
                if floor:
                    # text left (u = 0) to the north, top (v = 0) to the east; normal straight up
                    pos = np.array([np.sign(z) * height / 2, -np.sign(y) * width / 2, 0.0, bt], dtype='<f2')
                    d[b + 12:b + 15] = bytes((128, 128, 255))
                else:
                    pos = np.array([0.0, np.sign(y) * width / 2, np.sign(z) * height / 2, bt], dtype='<f2')
                d[b:b + 8] = pos.tobytes()
                uv = np.array([0.0 if y < 0 else 1.0, 0.0 if z > 0 else 1.0], dtype='<f2')
                d[b + uvo:b + uvo + 4] = uv.tobytes()
    # header strings: the material path and the node names
    p = nif.sizes_offset + 4 * nif.num_blocks
    ns, _ = struct.unpack_from('<II', d, p)
    q = p + 8
    for _ in range(ns):
        q += 4 + struct.unpack_from('<I', d, q)[0]
    strings = []
    for s in nif.strings:
        if s.lower().endswith('.bgsm'):
            s = f'Materials\\SandboxRoom\\Signs\\{name}.BGSM'
        elif s.startswith('V111SafetyPoster01'):
            s = s.replace('V111SafetyPoster01', 'SBRSign' + name)
        strings.append(s.encode('latin1'))
    table = struct.pack('<II', ns, max(len(s) for s in strings)) + b''.join(
        struct.pack('<I', len(s)) + s for s in strings)
    return bytes(d[:p]) + table + bytes(d[q:])


def build(ack_dir: str, game: Path) -> list[Path]:
    sys.path.insert(0, ack_dir)
    import ack.nif as ack_nif
    from ack.archive import extract_general
    signs = json.loads(SIGNS_JSON.read_text(encoding='utf8'))
    data = game / 'Data'
    with tempfile.TemporaryDirectory() as tmp:
        extract_general(str(data / 'Fallout4 - Meshes.ba2'), [POSTER_NIF], tmp)
        extract_general(str(data / 'Fallout4 - Materials.ba2'), [POSTER_BGSM], tmp)
        nif_t = Path(tmp, *POSTER_NIF.split('\\')).read_bytes()
        bgsm_t = Path(tmp, *POSTER_BGSM.split('\\')).read_bytes()
    meshes, mats, texs = (OUT / 'Meshes' / 'SandboxRoom' / 'Signs', OUT / 'Materials' / 'SandboxRoom' / 'Signs',
                          OUT / 'Textures' / 'SandboxRoom' / 'Signs')
    for folder in (meshes, mats, texs):
        if folder.exists():
            shutil.rmtree(folder)  # generated: signs taken out of the layout go too
        folder.mkdir(parents=True)
    (texs / 'Flat_n.dds').write_bytes(dds_dxt1(Image.new('RGB', (16, 16), (128, 128, 255))))
    (texs / 'Matte_s.dds').write_bytes(dds_dxt1(Image.new('RGB', (16, 16), (24, 40, 0))))
    for name, sign in signs.items():
        (meshes / f'{name}.nif').write_bytes(make_model(nif_t, name, sign['width'], sign['height'], ack_nif,
                                                                 floor=sign['kind'] == 'Floor'))
        (mats / f'{name}.BGSM').write_bytes(make_material(bgsm_t, name))
        (texs / f'{name}_d.dds').write_bytes(dds_dxt1(render(sign['text'], sign['kind'])))
    return [meshes, mats, texs]


def install(folders: list[Path], game: Path) -> None:
    for folder in folders:
        dest = game / 'Data' / folder.relative_to(OUT)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(folder, dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ack', required=True, help='AgentCreationKit checkout')
    ap.add_argument('--game', default='D:/Steam/steamapps/common/Fallout 4')
    a = ap.parse_args()
    folders = build(a.ack, Path(a.game))
    install(folders, Path(a.game))
    print(f'{len(json.loads(SIGNS_JSON.read_text(encoding="utf8")))} signs made and installed')


if __name__ == '__main__':
    main()
