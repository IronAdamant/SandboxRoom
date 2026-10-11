# Sandbox Room

A Fallout 4 mod by Deadmansprice: a clinical testing facility reached by holotape. One interior cell built from
the game's high-tech (Mass Fusion) kit in the Institute's clean white finish, three storeys high, with Institute
ceiling lights.

**Main hall**
- **Crafting stations** along the north wall: weapons, armor, chemistry, cooking, the Automatron robot workbench,
  the Nuka-World Nuka-Mixer, and power armor with **three empty power armor frames** beside it.
- **Storage**: signed sections of lab filing cabinets along the walls, each with a header sign, an Institute
  shelf and a label on every cabinet. The cabinets never run out: whatever you take is put straight back.
  - Weapons & Ammo: Ballistic Guns, Energy Weapons, Heavy Weapons, Melee Weapons, Explosives, Ammo
  - Apparel: Armor, Clothing, Headwear, Dogmeat Gear
  - Mods: Weapon Mods, Armor Mods
  - Power Armor (by the power armor station): Power Armor, Power Armor Mods
  - Aid: Medicine and Chems, Food, Drinks
  - Miscellaneous: Junk (with caps), Magazines, Bobbleheads
  - Each DLC (Automatron, Far Harbor, Nuka-World, Contraptions, Vault-Tec) has a labelled cabinet in every
    section it has items for.
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
- A lobby with the arena terminals in a labelled row (base game, Automatron, Far Harbor, Nuka-World; the DLC
  ones with an Enemies and a Legendaries submenu), and a door on each side of them into the arena. The doors open as you
  walk up to them.
- The arena: dirt ground, mounds, rock outcrops, boulders and dead trees; no buildings. Railed balconies at
  storeys 1 and 2 along its north wall.
- Pick an enemy on a lobby terminal, then how many (1 to 10). Each one lands at a random spot across the arena with full AI, but stays frozen while you
  are outside the arena and wakes up as soon as you step through a door (and freezes again when you leave).

**(Sandbox Room) Holotape**, added to your inventory a few seconds after you get the Pip-Boy (in Vault 111,
with an alternative-start mod, or right away on an existing save): *Teleport In* saves your exact position and takes you to the room; inside, it offers *Teleport Out*
instead, which returns you there with everything you carry. Everything in the room is free; playing fair is up
to you (save before teleporting in, and load that save if you don't want to keep what you took). Console:
`coc SandboxRoom`.

## Plugin

One ESL-flagged plugin, `Sandbox Room.esp` (no load-order slot). It requires Fallout 4 and five DLC: Automatron,
Far Harbor, Nuka-World, Contraptions Workshop and Vault-Tec Workshop (not Wasteland Workshop). Until 1.0 each DLC
had its own add-on plugin; the DLC content is now part of the main plugin (`make_spec.DLC_MASTERS`).

Also ships, packed in `Sandbox Room - Main.ba2` / `- Textures.ba2`: the scripts (no F4SE needed) and the signs.

## Layout

- `data/` - what ships, laid out like the game's `Data` folder.
- `source/User/SandboxRoom/` - Papyrus sources.
- `tools/xedit/scan.pas` - read-only scan of the official masters (items, workbenches, creature lists).
- `tools/build/make_spec.py` - **the design**: room layout, chest contents, spawn lists, DLC content. Generates
  `work/spec.txt`.
- `tools/xedit/build.pas` - applies the spec with FO4Edit. Re-runnable: records and placed objects are found by
  editor ID and only created when missing. The spec is the source of truth for the layout: every build puts each
  object where the spec says and deletes placed objects and records the spec no longer has (so a move made by
  hand in the Creation Kit must be copied into the spec).
- `tools/build/signs.py` - makes the signs make_spec lists (`work/signs.json`): a vanilla poster model resized
  and remapped to a texture rendered with the sign's text, and its material. Installs them into `Data`.
- `tools/build/build.py` - spec + signs + FO4Edit run + copy to `data/`.
- `tools/build/package.py --version X.Y.Z` - a release in `dist/`: the BA2 archives for PC and Xbox (`_xbox`
  names, as the Creation Kit's upload expects), and the Nexus zip. Release texts and the Bethesda.net steps are in
  `docs/release/`.
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

**Only save `Sandbox Room.esp` in the Creation Kit with nothing but it loaded** (its masters load on their own),
and close the Creation Kit before building: `build.py` refuses to run while it is open, and refuses to finish if
the plugin has masters other than Fallout 4 and the five DLC.

The navmesh is made in the Creation Kit (NavMesh > Generation > Recast, then Finalize Cell NavMeshes) with
`Sandbox Room.esp` as the active file. After any Creation Kit save, re-run `build.py`: it also resets the header's
next object ID, so new forms stay inside the ESL range.
