# Uploading to Bethesda.net (PC and Xbox)

Everything is built by `python tools/build/package.py --version X.Y.Z` into `dist/`:

| Folder | What | Use |
|---|---|---|
| `dist/PC/` | the six plugins + `Sandbox Room - Main.ba2` / `- Textures.ba2` (PC formats) | the PC upload |
| `dist/Xbox/` | the six plugins + the same two archives in Xbox formats (XBoxDDS textures, Xbox compression) | the Xbox upload |
| `dist/Sandbox Room X.Y.Z.zip` | FOMOD installer | Nexus |

The archives belong to `Sandbox Room.esp`; the DLC add-on plugins have no assets of their own (they use the main
mod's scripts and signs), so each add-on is uploaded as its own plugin with Sandbox Room as a requirement.

## Steps (Creation Kit)

1. Copy the plugin and its archives for the platform into `Fallout 4\Data` (the archives replace the loose files:
   move the loose `Scripts\SandboxRoom`, `Meshes|Materials|Textures\SandboxRoom` folders out first, or the CK will
   pack/see those instead).
2. Creation Kit > File > Data: tick only the plugin being uploaded, set it as the active file, OK.
3. File > Upload Plugin and Archive to Bethesda.net. Log in, create the mod entry (title, description from
   `bethesda_net_description.txt`, screenshots), choose the platform (PC or Xbox One), and point it at the plugin
   and that platform's archives.
4. Add-ons: repeat per add-on plugin (no archives), and list Sandbox Room and the DLC as requirements.
5. Bethesda.net shows content warnings for mods with scripts; that is expected.

Not possible: PlayStation (Sony does not allow mods with their own scripts or assets).
