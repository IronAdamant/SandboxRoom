# Uploading to Nexus Mods

One file per version: `dist/Sandbox Room X.Y.Z.zip`, made by `python tools/build/package.py --version X.Y.Z`. It is
a FOMOD installer (Vortex, Mod Organizer 2) that keeps both ways of installing:

| Option | What | For |
|---|---|---|
| `00 Packed (Next-Gen)` | `Sandbox Room.esp` + `Sandbox Room - Main.ba2` / `- Textures.ba2` | the current game (1.10.980+), recommended |
| `01 Loose Files (Old-Gen)` | `Sandbox Room.esp` + loose `Scripts`, `Meshes`, `Materials`, `Textures` | the old-gen game (1.10.163), which cannot read the packed archives; also works on next-gen |

Plus `Sandbox Room - Readme.txt` at the top. Manual installs copy the contents of one option folder into `Data`.

## Texts (docs/release/)

| File | Where it goes | Limit |
|---|---|---|
| `nexus_file_description.txt` | the uploaded file's description | 255 characters (the form cuts off the rest) |
| `nexus_summary_350.txt` | the mod's brief overview (summary) | 350 characters |
| `nexus_description.bbcode` | the mod page's description (paste into the BBCode / source view) | |
| `bethesda_net_version_notes.txt` | the changelog entry for the version (the same notes as Bethesda.net) | |
| `CHANGELOG.md` | the full changelog, for reference | |

## Steps

1. Mod page > Manage (Edit mod) > **Files** > Add a file:
   - File: `dist/Sandbox Room X.Y.Z.zip`
   - Name: `Sandbox Room`, version `X.Y.Z`, category **Main Files**
   - Description: `nexus_file_description.txt`
   - Tick "Update mod version" (or set the mod's version to X.Y.Z in the mod details).
   - Remove the "Mod manager download" option only if you want to; leave it on (the zip is a FOMOD).
2. The previous version's file: edit it and move it to **Old Versions** (or Archived), so only the new one is under
   Main Files. Do not delete it: players on old saves sometimes need it.
3. **Changelog**: add an entry for X.Y.Z with the lines of `bethesda_net_version_notes.txt` (without its first line,
   the version number).
4. **Description**: replace the mod page description with `nexus_description.bbcode`, and the summary with
   `nexus_summary_350.txt` if it changed.
5. Requirements on the mod page stay the same: the five DLC (Automatron, Far Harbor, Nuka-World, Contraptions
   Workshop, Vault-Tec Workshop); no F4SE.
6. Download the new file once from the page and open it in your mod manager: the installer should offer the two
   options (Packed recommended).
