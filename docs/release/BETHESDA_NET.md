# Uploading to Bethesda.net (PC and Xbox)

Everything is built by `python tools/build/package.py --version X.Y.Z` into `dist/`:

| Folder | What | Use |
|---|---|---|
| `dist/PC/` | `Sandbox Room.esp` + `Sandbox Room - Main.ba2` / `- Textures.ba2` | the PC upload |
| `dist/Xbox/` | `Sandbox Room.esp` + `Sandbox Room - Main_xbox.ba2` / `- Textures_xbox.ba2` (XBoxDDS, Xbox compression) | the Xbox upload |
| `dist/Sandbox Room X.Y.Z.zip` | the plugin, the PC archives and the readme | Nexus |

One plugin (since 1.0): it requires all five DLC (Automatron, Far Harbor, Nuka-World, Contraptions Workshop,
Vault-Tec Workshop). One creation carries both platforms.

## Steps (Creation Kit)

1. Put the plugin and all four archives (PC and `_xbox`) in `Fallout 4\Data`, and take the loose
   `Scripts\SandboxRoom`, `Meshes|Materials|Textures\SandboxRoom` folders out (the CK would see those instead).
2. Creation Kit > File > Data: tick only `Sandbox Room.esp`, set it as the active file, OK. Never save.
3. File > Upload Plugin and Archive to Bethesda.net > the Sandbox Room creation (Edit Creation, or Create New).
   Text: `bethesda_net_description_1000.txt` (1,000 characters max); categories Cheats, Gameplay, Utilities,
   Load Order Neutral.
4. Select Data To Upload: PC and Xbox ticked, plugin `Sandbox Room.esp`, "Upload as Light Master" UNticked
   (it is already a light plugin through its ESL flag), Include Archives ticked. The Xbox archives are found by
   their `_xbox` names; if Generate is used instead, its file list must be the 122 files of
   `Scripts\SandboxRoom`, `Meshes|Materials|Textures\SandboxRoom` and nothing from vanilla (it adds
   `Form.pex`, `ObjectReference.pex`, `ScriptObject.pex`: remove them).
5. On the website: requirements = the five DLC; version notes; tagline (180 characters max).

Not possible: PlayStation (Sony does not allow mods with their own scripts or assets).
