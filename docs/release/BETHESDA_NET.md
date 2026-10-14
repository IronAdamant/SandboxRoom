# Uploading to Bethesda.net (PC and Xbox)

The PC files are built by `python tools/build/package.py --version X.Y.Z` into `dist/`; the Xbox archives are made
by the Creation Kit's Generate at upload:

| Folder | What | Use |
|---|---|---|
| `dist/PC/` | `Sandbox Room.esp` + `Sandbox Room - Main.ba2` / `- Textures.ba2` | the PC upload |
| (Creation Kit) | `Sandbox Room - Main_xbox.ba2` / `- Textures_xbox.ba2`, from Generate | the Xbox upload |
| `dist/Sandbox Room X.Y.Z.zip` | the plugin, the PC archives and the readme | Nexus |

One plugin (since 1.0): it requires all five DLC (Automatron, Far Harbor, Nuka-World, Contraptions Workshop,
Vault-Tec Workshop). One creation carries both platforms.

## Steps (Creation Kit)

1. Put the plugin and the PC archives from `dist/PC/` in `Fallout 4\Data`, with the loose `Scripts\SandboxRoom`,
   `Meshes|Materials|Textures\SandboxRoom` folders there too (`build.py` installs them): Generate packs the Xbox
   archives from them. Delete any old `_xbox` archives from `Data`.
2. Creation Kit > File > Data: tick only `Sandbox Room.esp`, set it as the active file, OK. Never save.
3. File > Upload Plugin and Archive to Bethesda.net > the Sandbox Room creation (Edit Creation, or Create New).
   Text: `bethesda_net_description_1000.txt` (1,000 characters max); categories Cheats, Gameplay, Utilities,
   Load Order Neutral.
4. Select Data To Upload: PC and Xbox ticked, plugin `Sandbox Room.esp`, "Upload as Light Master" UNticked
   (it is already a light plugin through its ESL flag), Include Archives ticked.
   **Xbox: always Generate.** Never upload `_xbox` archives made with Archive2: its XBoxDDS format keeps the
   textures in the PC layout, which the console cannot use (1.0.0 shipped those; Xbox players reported pink signs).
   Generate tiles them for the console. Its file list must be the 122 files of `Scripts\SandboxRoom`,
   `Meshes|Materials|Textures\SandboxRoom` and nothing from vanilla (it adds `Form.pex`, `ObjectReference.pex`,
   `ScriptObject.pex`: remove them).
5. Before uploading, check the generated archives: `python tools/build/check_xbox.py` (looks in the game's
   `Data`; `--dir` for another folder). It lists missing or extra files and any texture still in the PC layout;
   upload only when it prints "Xbox archives OK".
6. On the website: requirements = the five DLC; version notes; tagline (180 characters max).

Not possible: PlayStation (Sony does not allow mods with their own scripts or assets).
