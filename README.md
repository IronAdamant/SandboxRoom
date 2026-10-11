# Sandbox Room

A Fallout 4 mod by Deadmansprice: a clinical testing facility reached by holotape. One interior cell built from
the game's high-tech (Mass Fusion) kit in the Institute's clean white finish, three storeys high, with Institute
ceiling lights.

**Main hall**
- **Crafting stations** along the north wall: weapons, armor, chemistry, cooking, power armor with **three empty
  power armor frames** beside it (plus the robot workbench and Nuka-Mixer with their DLC add-ons).
- **Storage**: signed sections of lab filing cabinets along the walls, each with a header sign, an Institute
  shelf and a label on every cabinet. The cabinets never run out: whatever you take is put straight back.
  - Weapons & Ammo: Ballistic Guns, Energy Weapons, Heavy Weapons, Melee Weapons, Explosives, Ammo
  - Apparel: Armor, Clothing, Headwear, Dogmeat Gear
  - Mods: Weapon Mods, Armor Mods
  - Power Armor (by the power armor station): Power Armor, Power Armor Mods
  - Aid: Medicine and Chems, Food, Drinks
  - Miscellaneous: Junk (with caps), Magazines, Bobbleheads
  - Each DLC add-on puts one cabinet per section it has items for into that section.
- **Target range** at the east end: a firing lane facing four bays walled off from each other, floor to ceiling,
  to contain blasts, with TARGET RANGE on the lane floor. Targets are holograms (the game's hologram effect),
  stand still (AI off) and come back 3 seconds after dying. Each bay's terminal picks the enemy (hologram human,
  super mutant or deathclaw: the room's own loot-free copies) and its health (game default, 100, 1,000, 10,000,
  100,000), or clears the bay.
  - Single target
  - Group of five, for area damage
  - Legendary target (Fallout 4's legendary enemies, which have one tier)
  - Target practice stands (the base game has no bullseye-circle model; these are its target cutouts)
- **Shooting galleries** over the firing lane at storeys 1 and 2, railed, looking down into the bays and the open
  hall. Stairs up from the hall side.

**Arena** (through the door under the ARENA sign in the hall's south wall)
- A lobby with the arena terminals in a labelled row (base game, then one per DLC add-on, each with an
  Enemies and a Legendaries submenu), and a door on each side of them into the arena. The doors open as you
  walk up to them.
- The arena: dirt ground, mounds, rock outcrops, boulders and dead trees; no buildings. Railed balconies at
  storeys 1 and 2 along its north wall.
- What the lobby terminals spawn lands at random spots across the arena with full AI, but stays frozen while you
  are outside the arena and wakes up as soon as you step through a door (and freezes again when you leave).

**Holotape**, added to your inventory once you leave Vault 111 (or right away on an existing save):
*Teleport In* saves your exact position and takes you to the room; inside, it offers *Teleport Out* instead,
which returns you there. Console: `coc SandboxRoom`.

## Plugins

All are ESL-flagged (no load-order slot). Install the main plugin, then the add-ons for the DLC you own.

| Plugin | Needs | Adds |
|---|---|---|
| `Sandbox Room.esp` | Fallout 4 | the hall, arena, stations, storage, target range, arena terminal, holotape |
| `Sandbox Room - Automatron.esp` | Automatron | DLC cabinets, robot workbench, arena terminal |
| `Sandbox Room - Far Harbor.esp` | Far Harbor | DLC cabinets, arena terminal |
| `Sandbox Room - Nuka-World.esp` | Nuka-World | DLC cabinets, Nuka-Mixer station, arena terminal |
| `Sandbox Room - Contraptions Workshop.esp` | Contraptions Workshop | DLC cabinets |
| `Sandbox Room - Vault-Tec Workshop.esp` | Vault-Tec Workshop | DLC cabinets |

Also ships: scripts `Scripts/SandboxRoom/*.pex` (no F4SE needed) and the signs
(`Meshes|Materials|Textures/SandboxRoom/Signs`).

## Layout

- `data/` - what ships, laid out like the game's `Data` folder.
- `source/User/SandboxRoom/` - Papyrus sources.
- `tools/xedit/scan.pas` - read-only scan of the official masters (items, workbenches, creature lists).
- `tools/build/make_spec.py` - **the design**: room layout, chest contents, spawn lists, DLC add-ons. Generates
  `work/spec.txt`.
- `tools/xedit/build.pas` - applies the spec with FO4Edit. Re-runnable: records and placed objects are found by
  editor ID and only created when missing. The spec is the source of truth for the layout: every build puts each
  object where the spec says and deletes placed objects and records the spec no longer has (so a move made by
  hand in the Creation Kit must be copied into the spec).
- `tools/build/signs.py` - makes the signs make_spec lists (`work/signs.json`): a vanilla poster model resized
  and remapped to a texture rendered with the sign's text, and its material. Installs them into `Data`.
- `tools/build/build.py` - spec + signs + FO4Edit run + copy to `data/`.
- `tools/build/compile.py` - compiles the scripts with the Creation Kit's Papyrus compiler (`--debug` keeps
  `Debug.Trace` lines, which release builds strip).
- `tools/build/papyrus_log.py on|off` - switches the game's Papyrus log on or off in `Fallout4Custom.ini`.
  Debugging in-game: `papyrus_log.py on`, `compile.py --debug`, play, read
  `Documents/My Games/Fallout4/Logs/Script/Papyrus.0.log`; afterwards `papyrus_log.py off` and a release
  `compile.py`. The door, arena, spawn terminal and target bay scripts log what they do.

## Building

Needs [AgentCreationKit](../AgentCreationKit) (runs FO4Edit unattended) and the Creation Kit (Papyrus compiler).

```
python tools/build/compile.py --game "D:/Steam/steamapps/common/Fallout 4"
python tools/build/build.py --ack "D:/Coding Projects/AgentCreationKit"
```

**Only save `Sandbox Room.esp` in the Creation Kit with nothing but it loaded** (its masters load on their own).
Saved with the add-ons loaded, its navmesh index picks up the DLC as masters; `build.py` refuses to finish if any
plugin has unexpected masters.

The navmesh is made in the Creation Kit (NavMesh > Generation > Recast, then Finalize Cell NavMeshes) with
`Sandbox Room.esp` as the active file. After any Creation Kit save, re-run `build.py`: it also resets the header's
next object ID, so new forms stay inside the ESL range.
