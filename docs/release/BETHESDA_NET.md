# Uploading to Bethesda.net (PC and Xbox)

Platforms: **PC and Xbox only.** No PlayStation: Sony does not allow mods with their own scripts or assets, and this
mod is built on both (a PlayStation version would be an empty building).

The PC files are built by `python tools/build/package.py --version X.Y.Z` into `dist/`; the Xbox archives are made
by the Creation Kit's Generate at upload:

| Folder | What | Use |
|---|---|---|
| `dist/PC/` | `Sandbox Room.esp` + `Sandbox Room - Main.ba2` / `- Textures.ba2` | the PC upload |
| (Creation Kit) | `Sandbox Room - Main_xbox.ba2` / `- Textures_xbox.ba2`, from Generate | the Xbox upload |
| `dist/Sandbox Room X.Y.Z.zip` | FOMOD installer: packed (next-gen) or loose (old-gen) files, and the readme | Nexus |

One plugin (since 1.0): it requires all five DLC (Automatron, Far Harbor, Nuka-World, Contraptions Workshop,
Vault-Tec Workshop). One creation carries both platforms.

## Texts (docs/release/)

| File | Where it goes | Limit |
|---|---|---|
| `bethesda_net_description_1000.txt` | the creation's description (Creation Kit upload) | 1,000 characters |
| `bethesda_net_description_10000.txt` | the full description on the website | 10,000 characters |
| `bethesda_net_tagline_180.txt` | the tagline (website) | 180 characters |
| `bethesda_net_version_notes.txt` | the version / release notes | |
| `CHANGELOG.md` | the full changelog, for reference | |

## Steps (Creation Kit)

1. `Fallout 4\Data` must hold the plugin and the PC archives from `dist/PC/`, plus the loose
   `Scripts\SandboxRoom` (release builds: `compile.py` without `--debug`) and `Meshes|Materials|Textures\SandboxRoom`
   folders (`build.py` installs the sign files): Generate packs the Xbox archives from the loose files. Delete any
   old `_xbox` archives from `Data`, and any `Scripts\Source\User\SandboxRoom` folder.
2. Close the game. Creation Kit > File > Data: tick only `Sandbox Room.esp`, set it as the active file, OK.
   **Never save** (if asked on closing, answer No).
3. File > Upload Plugin and Archive to Bethesda.net > the Sandbox Room creation (Edit Creation, or Create New).
   Text: `bethesda_net_description_1000.txt`; categories Cheats, Gameplay, Utilities, Load Order Neutral.
4. Select Data To Upload: PC and Xbox ticked, plugin `Sandbox Room.esp`, "Upload as Light Master" UNticked
   (it is already a light plugin through its ESL flag), Include Archives ticked.
   **Xbox: always Generate.** Never upload `_xbox` archives made with Archive2: its XBoxDDS format keeps the
   textures in the PC layout, which the console cannot use (1.0.0 shipped those; Xbox players reported pink signs).
   Generate tiles them for the console. Its file list must be the **170 files** (1.1.0) of `Scripts\SandboxRoom`
   (18), `Meshes\SandboxRoom` (50), `Materials\SandboxRoom` (50) and `Textures\SandboxRoom` (52), and nothing from
   vanilla (it adds `Form.pex`, `ObjectReference.pex`, `ScriptObject.pex`: remove them). Or import
   `dist/Sandbox Room X.Y.Z Xbox.achlist`, which is exactly that list.
5. Before uploading, check the generated archives: `python tools/build/check_xbox.py` (looks in the game's
   `Data`; `--dir` for another folder). It lists missing or extra files and any texture still in the PC layout;
   upload only when it prints "Xbox archives OK".
6. On the website: version 1.1.0; requirements = the five DLC; tagline from `bethesda_net_tagline_180.txt`;
   version notes from `bethesda_net_version_notes.txt`; platforms PC and Xbox.
7. Afterwards, delete the `_xbox` archives from `Data` (the PC game does not need them).
