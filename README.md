# Sandbox Room

A Fallout 4 mod by Deadmansprice: a clinical, Institute-walled testing room under an open sky, reached by holotape.

- **Crafting stations** along the north wall: weapons, armor, chemistry, cooking, power armor (plus the robot
  workbench and Nuka-Mixer with their DLC add-ons).
- **Item chests** along the south wall that never run out: whatever you take is put straight back.
  Weapons, Ammo, Apparel, Power Armor, Weapon Mods, Armor Mods, Aid, Junk (with caps), Magazines and Bobbleheads.
- **Arena** at the east end: a terminal spawns enemies there (humans, synths and robots, super mutants,
  creatures, legendaries), and can kill or remove everything it spawned.
- **Target range** past the arena: a firing lane facing four bays walled off from each other to contain blasts.
  Targets stand still (AI off) and come back 3 seconds after dying. Each bay's terminal picks the enemy (human,
  super mutant, deathclaw) and its health (game default, 100, 1,000, 10,000, 100,000), or clears the bay.
  - Single target
  - Group of five, for area damage
  - Legendary target (Fallout 4's legendary enemies, which have one tier)
  - Target practice stands (the base game has no bullseye-circle model; these are its target cutouts)
- **Three empty power armor frames** on the south wall.
- **Holotape**, added to your inventory once you leave Vault 111 (or right away on an existing save):
  *Teleport In* saves your exact position and takes you to the room; inside, it offers *Teleport Out* instead,
  which returns you there. Console: `coc SandboxRoom`.

## Plugins

All are ESL-flagged (no load-order slot). Install the main plugin, then the add-ons for the DLC you own.

| Plugin | Needs | Adds |
|---|---|---|
| `Sandbox Room.esp` | Fallout 4 | the room, stations, 9 chests, spawn terminal, holotape |
| `Sandbox Room - Automatron.esp` | Automatron | DLC item chest, robot workbench, spawn terminal |
| `Sandbox Room - Far Harbor.esp` | Far Harbor | DLC item chest, spawn terminal |
| `Sandbox Room - Nuka-World.esp` | Nuka-World | DLC item chest, Nuka-Mixer station, spawn terminal |
| `Sandbox Room - Contraptions Workshop.esp` | Contraptions Workshop | DLC item chest |
| `Sandbox Room - Vault-Tec Workshop.esp` | Vault-Tec Workshop | DLC item chest |

Scripts: `Scripts/SandboxRoom/*.pex` (no F4SE needed).

## Layout

- `data/` - what ships, laid out like the game's `Data` folder.
- `source/User/SandboxRoom/` - Papyrus sources.
- `tools/xedit/scan.pas` - read-only scan of the official masters (items, workbenches, creature lists).
- `tools/build/make_spec.py` - **the design**: room layout, chest contents, spawn lists, DLC add-ons. Generates
  `work/spec.txt`.
- `tools/xedit/build.pas` - applies the spec with FO4Edit. Re-runnable: records and placed objects are found by
  editor ID and only created when missing, and objects keep their position once placed, so anything moved by hand
  in the Creation Kit stays put.
- `tools/build/build.py` - spec + FO4Edit run + copy to `data/`.
- `tools/build/compile.py` - compiles the scripts with the Creation Kit's Papyrus compiler.

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
