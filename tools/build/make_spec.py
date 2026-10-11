"""Generate the build spec (work/spec.txt) for tools/xedit/build.pas from the game data scan (work/scan/*.tsv).

    python tools/build/make_spec.py

Everything about the room lives here: layout, chest contents, spawn lists and the DLC add-ons.
Coordinates are game units (about 1.4 cm each); +X is east, +Y north. One interior cell:

    main hall (X0..X1, Y0..Y1), three storeys:  west: stations (north wall), entry point, and the storage
                                                sections (signed rows of filing cabinets along the walls); then
                                                the firing lane with galleries at storeys 1 and 2; east: four
                                                walled target bays with holographic targets
    lobby (south of the hall, through a door):  the arena terminals
    arena (south of the lobby, two doors):      terrain; spawns wake up while the player is inside

Signs are generated models (tools/build/signs.py renders their textures): make_spec records every sign it places
in work/signs.json.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCAN = REPO / 'work' / 'scan'
SPEC = REPO / 'work' / 'spec.txt'
SIGNS_JSON = REPO / 'work' / 'signs.json'

MAIN = 'Sandbox Room.esp'
AUTHOR = 'Deadmansprice'
DESCRIPTION = ('Sandbox Room: a testing facility reached by holotape. Refilling storage, crafting stations, a target '
               'range with holographic targets and an arena whose enemies wake when you walk in.')
CELL = 'SandboxRoom'  # the CK drops underscores from cell editor IDs; also the coc name

# The kit: Fallout 4's high-tech interior pieces (Mass Fusion) in the Institute's clean white finish. Everything sits
# on a 256 grid; a wall piece fills the -X edge of its cell, one storey per tier (Mid02 0-256, Mid 256-512,
# Top 512-752). Floors are slabs with their top at the placed height; seen from below they make the ceiling.
G = 256
WALL_TIERS = ('Mid02', 'Mid', 'Top')
WALL_TOP, H1, H2 = 752, 256, 512           # ceiling height, gallery decks at storeys 1 and 2
STAIRS_TOP_END = 64                        # HitExtIntStairs1Story01: its top platform (z 256) ends at local y 64
SWAP = 'swap=@HitInstituteThemeSwap01'
FLOOR_BASE = '@HitFloorSolidFull01'
LIGHT_BASE, LIGHT_RADIUS = '@InstituteLightWhite01NS', 1100

# Main hall bounds. West to east: crafting and chests, the open arena (ARENA_X to LANE_X), the firing lane under
# the galleries (LANE_X to BAY_X) and the target bays (BAY_X to X1).
X0, X1, Y0, Y1 = -1536, 4608, -1024, 1024
ARENA_X, LANE_X, BAY_X = 1024, 2560, 3072
HALL_DOOR_X = 640                          # the door in the hall's south wall, to the lobby
DOOR_SILL_LIFT = 1                         # doorway wall pieces sit this far up, see wall_ring()

# The wing: lobby (terminals), then the AI arena through a door on each side of them.
LX0, LX1, LY0, LY1 = -256, 1536, -1536, -1024
AX0, AX1, AY0, AY1 = -1536, 4608, -5632, -1536
WING_DOORS_X = [128, 1152]
AI_TERMINAL_Y = LY0 + 106                  # against the lobby's south wall, facing the hall door
AI_TERMINAL_X = 310                        # base game's; the add-ons' follow at 220 apart (Dlc.ai_terminal_x),
                                           # the row centred on the hall door between the two arena doors
BALCONY_X0, BALCONY_X1 = -1024, 3072       # arena balconies along its north wall, two cells deep
ARENA_SPAWNS = [(0, -2700), (1500, -2550), (3000, -2700), (600, -3700), (2300, -3700), (3700, -3600),
                (-700, -3500), (1500, -4500), (2900, -4800)]
# (base, x, y, z, rotation): mounds, outcrops, boulders and dead trees; the spawn points stay in the open
TERRAIN = [
    ('RockCliff07', -1300, -5300, -300, 45), ('QryMoundRocksTall03dirtyALL', 4100, -5200, -40, 200),
    ('QryMoundLargeGravel01dirtyALL', 1400, -5250, -60, 10), ('QryMoundRocksTall01dirtyALL', -200, -4600, -40, 0),
    ('QryMoundRocksTall03dirtyALL', 4000, -3000, -40, 90), ('QryMoundRocksMed01dirtyALL', 800, -3000, 0, 30),
    ('QryMoundRocksMed03dirtyALL', 2600, -3100, 0, 120), ('QryMoundRocksLow01dirtyALL', -1000, -2500, 0, 0),
    ('QryMoundRocksLow04dirtyALL', 2200, -4300, 0, 60), ('CaveMoundDirtHill02', 3000, -4300, 0, 0),
    ('RockBlastedForestBoulder01', 1900, -2900, 40, 15), ('RockBlastedForestBoulder02', 300, -4300, 50, 70),
    ('RockBlastedForestBoulder03', 3600, -2400, 40, 160),
    ('TreeBlastedForestDestroyedUpright03', 1000, -4100, -120, 0),
    ('TreeBlastedForestDestroyedStump01', 2700, -2500, 0, 0), ('TreeBlastedForestDestroyedStump02', -800, -3900, 0, 0),
    ('TreeBlastedForestDestroyedFallen01', 3500, -4000, 0, 70),
    ('TreeBlastedForestDestroyedFallen03', 500, -2300, 0, 30), ('TreeBlastedForestDestroyedStump03', 4300, -2400, 0, 0),
    ('QryRockM01dirtyALL', 1200, -3600, 0, 0), ('QryRockM03dirtyALL', 2900, -3800, 0, 50),
    ('QryRockM04dirtyALL', -300, -3200, 0, 100), ('RockBoulder02_GS', 2000, -2400, 0, 0),
    ('RockBoulder03_GS', 4200, -4400, 0, 0), ('QryMoundRocksSmall04dirtyALL', 1700, -3300, 0, 0),
    ('QryMoundRocksSmall02dirtyALL', 4300, -3500, 0, 0), ('CaveMoundRocksMed01', -1100, -3000, 0, 0),
]

# Target bays, south to north, each BAY_WIDTH wide. Targets stand BAY_TARGET_DEPTH into the bay. Every target
# shows the game's hologram effect (Shaun's, in the Institute). The single and group bays use the room's own
# hologram targets (HOLO_TARGETS: copies of the game's enemy templates, without loot); the legendary bay uses the
# game's legendary enemies.
BAY_WIDTH, BAY_TARGET_DEPTH = 512, 700
HOLOGRAM_SHADER = '@SBR_HologramFXS'
# The hologram: a copy of the power armor targeting highlight (an additive glow over the solid model, with scan
# lines scrolling across it) without its orange gradient, coloured blue and kept on. Shaun's hologram shader
# subtracts instead, which washes models out to white or erases them.
HOLOGRAM_FIELDS = {
    'Fill/Texture Effect - Color Key 1': (40, 120, 255), 'Fill/Texture Effect - Color Key 2': (80, 170, 255),
    'Fill/Texture Effect - Color Key 3': (40, 120, 255), 'Edge Effect - Color': (120, 210, 255),
}
HOLOGRAM_VALUES = {
    'Fill/Texture Effect - Presistent Alpha Ratio': 0.45, 'Fill/Texture Effect - Full Alpha Ratio': 0.45,
    'Edge Effect - Persistent Alpha Ratio': 0.9, 'Edge Effect - Full Alpha Ratio': 1.0, 'Edge Effect - Fall Off': 1.5,
    'Fill/Texture Effect - Alpha Pulse Amplitude': 0.1,
    # flags: the targeting highlight's, without "Membrane Grayscale Color/Alpha" (they take the gradient's colour)
    'Flags': '000100010001000111',
}
HOLO_XP_OFFSET = -100                      # target kills give no XP
HOLO_TARGETS = [('SBR_HoloHuman', 'EncRaider01Template', 'Hologram Human'),
                ('SBR_HoloSuperMutant', 'EncSuperMutantTemplate', 'Hologram Super Mutant'),
                ('SBR_HoloDeathclaw', 'EncDeathclaw01Template', 'Hologram Deathclaw')]
BAYS = [
    {'key': 'Single', 'title': 'Single target', 'count': 1,
     'types': [('Human', 'SBR_HoloHuman'), ('Super mutant', 'SBR_HoloSuperMutant'),
               ('Deathclaw', 'SBR_HoloDeathclaw')]},
    {'key': 'Group', 'title': 'Group of five (area damage)', 'count': 5,
     'types': [('Humans', 'SBR_HoloHuman'), ('Super mutants', 'SBR_HoloSuperMutant'),
               ('Deathclaws', 'SBR_HoloDeathclaw')]},
    {'key': 'Legendary', 'title': 'Legendary target', 'count': 1,
     'types': [('Legendary human', 'LCharRaiderLegendary'),
               ('Legendary super mutant', 'LCharSuperMutantAllLegendary'),
               ('Legendary deathclaw', 'LCharDeathclawLegendary')]},
    {'key': 'Circles', 'title': 'Target circles', 'count': 0, 'types': []},
]
HEALTH_LABELS = ['game default', '100', '1,000', '10,000', '100,000']  # menu items 10-14
PA_FRAMES_X = [620, 760, 900]              # beside the power armor station

# Z rotations that turn furniture and containers so their front (the side the player uses, local -Y) faces a
# direction. Checked in the Creation Kit: at 0 the player marker is on the south side. Heading markers are
# different: their arrow is local +Y, so a marker at 90 points east.
FACE_SOUTH, FACE_WEST, FACE_NORTH, FACE_EAST = 0, 90, 180, 270
FACE_WEST_MARKER = 270  # for things whose front is local +Y (heading markers, the target stands)
FACE = {'S': FACE_SOUTH, 'W': FACE_WEST, 'N': FACE_NORTH, 'E': FACE_EAST}
# Signs show their text on local +X; the Institute wall shelf sticks out towards local +Y.
SIGN_RZ = {'E': 0, 'S': 90, 'W': 180, 'N': 270}
SHELF_RZ = {'N': 0, 'E': 90, 'S': 180, 'W': 270}

# Storage: each section is a row of cabinets against a wall, read left to right by a player facing the wall:
# base game categories first, then one cabinet per add-on that has items of the section. Over the row: a header
# sign on the wall, an Institute shelf under it, and a label on top of each cabinet.
# Walls: (direction the row faces, axis the row runs along, step direction along that axis, wall coordinate).
WALLS = {'S': ('N', 'x', -1, Y0), 'N': ('S', 'x', 1, Y1), 'W': ('E', 'y', 1, X0)}
WALL_FACE = 32                             # the kit's wall pieces are 32 deep (36 at the top tier)
CABINET = '@HighTechFilingCabinet01ACleanTall'  # 56 x 56 x 125, drawers at the front (local -Y)
CABINET_DEPTH, CABINET_TOP, SLOT_PITCH = 56, 125, 76
LABEL_W, LABEL_H = 64, 16                  # cabinet labels; textures 512 x 128
HEADER_W, HEADER_H, HEADER_Z = 448, 112, 300  # section headers; textures 1024 x 256
SHELF_W, SHELF_Z = 130, 190                # InstituteShelfA01
AI_SIGN_Z = 330                            # over the hall's door to the lobby (the door frame tops out near 250)

# (key, header text, wall, centre along the wall, base game cabinets in order)
SECTIONS = [
    ('Weapons', 'WEAPONS & AMMO', 'S', -880,
     ['Ballistic Guns', 'Energy Weapons', 'Heavy Weapons', 'Melee Weapons', 'Explosives', 'Ammo']),
    ('Apparel', 'APPAREL', 'S', -6, ['Armor', 'Clothing', 'Headwear', 'Dogmeat Gear']),
    ('Mods', 'MODS', 'S', 1100, ['Weapon Mods', 'Armor Mods']),
    ('PowerArmor', 'POWER ARMOR', 'N', 1250, ['Power Armor', 'Power Armor Mods']),
    ('Aid', 'AID', 'W', 520, ['Medicine and Chems', 'Food', 'Drinks']),
    ('Misc', 'MISCELLANEOUS', 'W', -380, ['Junk', 'Magazines', 'Bobbleheads']),
]
# Add-on cabinet names per section ("Far Harbor Weapons and Ammo").
DLC_SECTION_NAMES = {'Weapons': 'Weapons and Ammo', 'Apparel': 'Apparel', 'Mods': 'Mods',
                     'PowerArmor': 'Power Armor', 'Aid': 'Aid', 'Misc': 'Miscellaneous'}


@dataclass
class Item:
    file: str
    oid: str          # object ID without the load-order byte
    sig: str
    edid: str
    name: str
    flags: int
    model: str
    keywords: set
    components: int

    @property
    def token(self) -> str:
        return f'{self.file}:{self.oid}'


def load_items() -> list[Item]:
    out = []
    with open(SCAN / 'items.tsv', encoding='utf8', errors='replace') as f:
        for r in csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
            r += [''] * (13 - len(r))
            out.append(Item(r[0], r[1][2:], r[2], r[3], r[4].strip(), int(r[5] or '0', 16), r[8],
                            set(filter(None, r[9].split(','))), int(r[10] or 0)))
    return out


SKIP_WORDS = ('test', 'dummy', 'donotuse', 'do not use', 'unused', 'debug', 'zzz', 'cut ')


def usable(i: Item) -> bool:
    text = (i.edid + ' ' + i.name).lower()
    return bool(i.name) and not i.flags & 0x4 and not any(w in text for w in SKIP_WORDS)


AMMO_COUNTS = {'AmmoFusionCore': 10, 'AmmoFatManMiniNuke': 25, 'AmmoMissile': 50, 'AmmoCannonBall': 25,
               'AmmoAlienBlaster': 500, 'AmmoFlamerFuel': 2000}


EXPLOSIVE_TYPES = {'WeaponTypeGrenade', 'WeaponTypeMine', 'WeaponTypeThrown', 'WeaponTypePulseGrenade',
                   'WeaponTypePulseMine'}
MELEE_TYPES = {'WeaponTypeMelee1H', 'WeaponTypeMelee2H', 'WeaponTypeUnarmed', 'WeaponTypeHandToHand'}
ENERGY_TYPES = {'WeaponTypeLaser', 'WeaponTypePlasma', 'WeaponTypeAlienBlaster', 'WeaponTypeGammaGun',
                'WeaponTypeGaussRifle', 'WeaponTypeCryolator', 'modskill_EnergyGuns', 'dn_weap_EnergyGun'}
CHEM_TYPES = {'ObjectTypeChem', 'ObjectTypeStimpak', 'ObjectTypeSyringerAmmo', 'ChemTypeStealthBoy'}
DRINK_TYPES = {'ObjectTypeDrink', 'ObjectTypeNukaCola', 'ObjectTypeAlcohol', 'ObjectTypeWater',
               'ObjectTypeCaffeinated'}
HEAD_TYPES = {'ArmorTypeHat', 'ArmorTypeHelmet', 'ArmorBodyPartHead', 'ArmorBodyPartEyes'}


def chest_of(i: Item) -> tuple[str, int] | None:
    """Which cabinet category an item goes in (see SECTIONS), and how many of it."""
    kw = i.keywords
    if i.sig == 'WEAP':
        if not i.model or i.edid.startswith(('Unarmed', 'Workshop', 'Turret')):
            return None
        if kw & EXPLOSIVE_TYPES or any(w in i.name for w in ('Grenade', 'Mine')):
            return 'Explosives', 1
        if kw & MELEE_TYPES:
            return 'Melee Weapons', 1
        if 'WeaponTypeHeavyGun' in kw:
            return 'Heavy Weapons', 1
        if kw & ENERGY_TYPES:
            return 'Energy Weapons', 1
        return 'Ballistic Guns', 1
    if i.sig == 'AMMO':
        return 'Ammo', AMMO_COUNTS.get(i.edid, 500)
    if i.sig == 'ARMO':
        if i.edid.lower().startswith(('skin', 'naked')):
            return None
        if 'ArmorTypePower' in kw:
            return 'Power Armor', 1
        if 'ClothingDogmeat' in kw:
            return 'Dogmeat Gear', 1
        if kw & HEAD_TYPES:
            return 'Headwear', 1
        if {'ObjectTypeArmor', 'ObjectTypeArmorLeg'} & kw or any(k.startswith('ma_armor') and 'lining' not in k.lower()
                                                                  for k in kw):
            return 'Armor', 1
        return 'Clothing', 1
    if i.sig == 'ALCH':
        if not i.model:
            return None
        if kw & CHEM_TYPES:
            return 'Medicine and Chems', 10
        return ('Drinks', 10) if kw & DRINK_TYPES else ('Food', 10)
    if i.sig == 'BOOK':
        return ('Magazines', 1) if 'PerkMagKeyword' in kw else None
    if i.sig == 'MISC':
        if 'ObjectTypeLooseMod' in kw:
            e = i.edid.lower()
            if e.startswith('miscmod_pa_'):
                return 'Power Armor Mods', 5
            if e.startswith(('miscmod_mod_armor', 'miscmod_mod_clothes')) or 'Armor' in i.name:
                return 'Armor Mods', 5
            return 'Weapon Mods', 5
        if i.edid.lower().startswith('bobblehead'):
            return 'Bobbleheads', 1
        if i.edid == 'Caps001':
            return 'Junk', 25000
        if i.components:
            return 'Junk', 25
    return None


SECTION_OF = {cat: key for key, _, _, _, cats in SECTIONS for cat in cats}


def key_of(name: str) -> str:
    return ''.join(c for c in name if c.isalnum())


@dataclass
class Dlc:
    key: str           # short name used in editor IDs
    title: str         # player-facing name, also the plugin suffix
    master: str
    ai_terminal_x: int  # slot in the lobby's row of AI arena terminals (0: no spawns)
    stations: list = field(default_factory=list)   # (base token, x, rotation) along the north wall
    spawns: list = field(default_factory=list)     # (menu text, leveled list editor ID)


DLCS = [
    Dlc('Automatron', 'Automatron', 'DLCRobot.esm', AI_TERMINAL_X + 220,
        stations=[('@WorkbenchRobot', 100, FACE_SOUTH)],
        spawns=[('Rust Devil robot', 'DLC01LCharBotRaiderBot_Random'),
                ('Rust Devil assaultron', 'DLC01LCharBotRaiderAssaultron'),
                ('Rust Devil sentry bot', 'DLC01LCharBotRaiderSentry'),
                ('Rust Devil protectron', 'DLC01LCharBotRaiderProtectron'),
                ('Mechanist robobrain', 'DLC01LCharMechRoboBrain'),
                ('Mechanist assaultron', 'DLC01LCharMechAssaultron'),
                ('Mechanist sentry bot', 'DLC01LCharMechSentry'),
                ('Mechanist eyebot', 'DLC01LCharMechEyebot'),
                ('Mechanist protectron', 'DLC01LCharMechProtectron'),
                ('Mechanist Mr. Handy', 'DLC01LCharMechMrHandy'),
                ('Legendary robobrain', 'DLC01LCharMechRoboBrainLegendary'),
                ('Legendary sentry bot', 'DLC01LCharMechSentryLegendary'),
                ('Legendary Rust Devil', 'DLC01_LCharRaiderLegendary')]),
    Dlc('FarHarbor', 'Far Harbor', 'DLCCoast.esm', AI_TERMINAL_X + 440,
        spawns=[('Fog crawler', 'DLC03_LCharFogCrawler'),
                ('Gulper', 'DLC03_LCharGulper'),
                ('Angler', 'DLC03_LCharAngler'),
                ('Hermit crab', 'DLC03_LCharHermitCrab'),
                ('Trapper', 'DLC03_LCharTrapper'),
                ('Wolf', 'DLC03_LCharWolf'),
                ('Island feral ghoul', 'DLC03_LCharFeralGhoul'),
                ('Island yao guai', 'DLC03_LCharYaoGuai'),
                ('Island radstag', 'DLC03_LCharRadStag'),
                ('Island mirelurk', 'DLC03_LCharMirelurkCrab'),
                ('Legendary fog crawler', 'DLC03_LCharFogCrawlerLegendary'),
                ('Legendary gulper', 'DLC03_LCharGulperLegendary'),
                ('Legendary angler', 'DLC03_LCharAnglerLegendary'),
                ('Legendary trapper', 'DLC03_LCharTrapperLegendary')]),
    Dlc('NukaWorld', 'Nuka-World', 'DLCNukaWorld.esm', AI_TERMINAL_X + 660,
        stations=[('@DLC04_WorkbenchSodaMachine_Freestanding_Quantum', -1380, FACE_SOUTH)],
        spawns=[('Disciple', 'DLC04_LCharRaiderDisciple'),
                ('Operator', 'DLC04_LCharRaiderOperator'),
                ('Pack member', 'DLC04_LCharRaiderPack'),
                ('Nukalurk', 'DLC04_LCharNukalurkAll'),
                ('Cave cricket', 'DLC04_LCharCaveCricket'),
                ('Bloodworm', 'DLC04_LCharBloodworm'),
                ('Rad ant', 'DLC04_LCharRadAnt'),
                ('Rad rat', 'DLC04_LCharRadRat'),
                ('Bloatfly swarm', 'DLC04_LCharSwarm'),
                ('Nukatron', 'DLC04_LCharNukatron'),
                ('Galactic Zone assaultron', 'DLC04LCharSpaceAssaultron'),
                ('Galactic Zone sentry bot', 'DLC04LCharSpaceSentryBot'),
                ('Legendary Disciple', 'DLC04_LCharGangDiscipleLegendary'),
                ('Legendary Operator', 'DLC04_LCharGangOperatorLegendary'),
                ('Legendary Pack member', 'DLC04_LCharGangPackLegendary'),
                ('Legendary cave cricket', 'DLC04_LCharCaveCricketLegendary')]),
    Dlc('Contraptions', 'Contraptions Workshop', 'DLCworkshop02.esm', 0),
    Dlc('VaultTec', 'Vault-Tec Workshop', 'DLCworkshop03.esm', 0),
]

# Base game spawn menus: submenu title -> [(menu text, leveled list)]
SPAWN_MENUS = {
    'Humans': [('Raider', 'LCharRaiderMixedEquipment'), ('Gunner', 'LCharGunnerMixedWeapons'),
               ('Triggerman', 'LCharTriggerman'), ('Children of Atom', 'LCharChildrenofAtom'),
               ('Scavenger', 'LCharScavenger'), ('Brotherhood of Steel (hostile)', 'LCharHostileBOS'),
               ('Institute (hostile)', 'LCharHostileINST')],
    'Synths and Robots': [('Synth', 'LCharSynth'), ('Synth courser', 'LCharSynthCourser'),
                          ('Protectron', 'LCharProtectron'), ('Assaultron', 'LCharAssaultron'),
                          ('Sentry bot', 'LCharSentryBot'), ('Mr. Gutsy', 'LCharMrGutsy'),
                          ('Mr. Handy', 'LCharMrHandy_Random')],
    'Super Mutants': [('Super mutant', 'LCharSupermutantMixedWeapons'), ('Behemoth', 'LCharSMBehemoth'),
                      ('Mutant hound', 'LCharMutantHound')],
    'Creatures': [('Deathclaw', 'LCharDeathclaw'), ('Feral ghoul', 'LCharFeralGhoul'),
                  ('Glowing one', 'LCharFeralGhoulGlowingOne'), ('Mirelurk', 'LCharMirelurkAll'),
                  ('Mirelurk king', 'LCharMirelurkKing'), ('Mirelurk queen', 'LCharMirelurkQueen'),
                  ('Radscorpion', 'LCharRadScorpion'), ('Yao guai', 'LCharYaoGuai'),
                  ('Mole rat', 'LCharMolerat'), ('Bloatfly', 'LCharBloatfly'), ('Bloodbug', 'LCharBloodbug'),
                  ('Stingwing', 'LCharStingwing'), ('Radroach', 'LCharRadroach'), ('Radstag', 'LCharRadStag'),
                  ('Vicious dog', 'LCharViciousDog')],
    'Legendaries': [('Legendary raider', 'LCharRaiderLegendary'), ('Legendary gunner', 'LCharGunnerLegendary'),
                    ('Legendary synth', 'LCharSynthLegendary'),
                    ('Legendary super mutant', 'LCharSuperMutantAllLegendary'),
                    ('Legendary deathclaw', 'LCharDeathclawLegendary'),
                    ('Legendary feral ghoul', 'LCharFeralGhoulLegendary'),
                    ('Legendary mirelurk', 'LCharMirelurkAllLegendary'),
                    ('Legendary radscorpion', 'LCharRadScorpionLegendary'),
                    ('Legendary yao guai', 'LCharYaoGuaiLegendary')],
}

# Base game crafting stations along the north wall, facing into the room: (base, x, rotation). The Automatron
# robot workbench (add-on) goes at 100, the power armor frames beside the power armor station. The power armor
# station's working side is its local +Y, so it turns the other way from the rest (checked in game).
STATIONS = [('@workbenchWeaponsA', -1150, FACE_SOUTH), ('@WorkbenchArmorA', -850, FACE_SOUTH),
            ('@WorkbenchChemistryA', -550, FACE_SOUTH), ('@WorkbenchCookingStove', -250, FACE_SOUTH),
            ('@WorkbenchPowerArmor', 450, FACE_NORTH)]

MENU_REMOVE_ALL, MENU_KILL_ALL = 900, 901
SPAWN_COUNT_MAX = 10                       # arena "how many" menus offer 1 to this many (SpawnTerminalScript.MaxCount)

# The holotape's header: what it does, and the honour system for whatever is taken from the room.
HOLOTAPE_WELCOME = (
    'SANDBOX ROOM\n'
    'TELEPORT IN: saves where you are and takes you to the Sandbox Room.\n'
    'TELEPORT OUT: takes you back to exactly where you were, with everything you are carrying.\n'
    'Everything in the room is free and never runs out. Playing fair is up to you: save before you teleport in, '
    'and load that save if you do not want to keep what you took.')

SIGNS: dict = {}  # model name -> text, kind and size; written to work/signs.json for signs.py


class Spec:
    def __init__(self):
        self.lines: list[str] = []
        self.file = ''
        self.made: set = set()

    def op(self, *fields):
        self.lines.append(' | '.join(str(f) for f in fields))

    def comment(self, text):
        self.lines += ['', '# ' + text]

    def ref(self, edid, base, x, y, z=0, rz=0, persistent=False, opts=''):
        opts = ' '.join(filter(None, ['persistent' if persistent else '', opts]))
        self.op('ref', edid, CELL, base, f'{x} {y} {z}', f'0 0 {rz}', opts or '-')

    def chest(self, edid, name, items):
        """An infinite chest (a filing cabinet): whatever is taken is put back."""
        self.op('copy', CABINET, edid)
        self.op('set', edid, 'FULL', name)
        self.op('items', edid, ' ; '.join(f'{i.token}*{n}' for i, n in items))
        self.op('set', edid, r'DATA\Flags', '0')  # no respawn
        self.op('script', edid, 'SandboxRoom:InfiniteChestScript')

    def sign(self, text: str, kind: str) -> str:
        """The static for a sign showing text, made once per plugin; returns its token. Kinds: 'Label' and 'Header'
        stand upright facing local +X; 'Floor' (header-sized) lies flat, read from local -X. The model and texture
        are generated by signs.py from work/signs.json."""
        w, h = (LABEL_W, LABEL_H) if kind == 'Label' else (HEADER_W, HEADER_H)
        name = kind + key_of(text)
        edid = 'SBR_Sign' + name
        SIGNS[name] = {'text': text, 'kind': kind, 'width': w, 'height': h}
        if (self.file, edid) not in self.made:
            self.made.add((self.file, edid))
            self.op('new', 'STAT', edid)
            self.op('set', edid, r'Model\MODL', f'SandboxRoom\\Signs\\{name}.nif')
            bounds = (-h // 2, -w // 2, -1, h // 2, w // 2, 1) if kind == 'Floor' else (-1, -w // 2, -h // 2, 1, w // 2, h // 2)
            for axis, v in zip(('X1', 'Y1', 'Z1', 'X2', 'Y2', 'Z2'), bounds):
                self.op('set', edid, f'OBND\\{axis}', v)
        return '@' + edid

    def file_op(self, name):
        self.file = name
        self.op('file', name)

    def terminal(self, edid, name, welcome):
        self.op('copy', '@VRWorkshopShared_VRTerminalConsoleTallOn', edid)
        for path in ('VMAD', 'Body Text', 'BSIZ'):
            self.op('remove', edid, path)
        self.op('set', edid, r'Record Header\Record Flags', '0')  # the template's flags are unexplained
        self.op('menuclear', edid)
        self.op('set', edid, 'FULL', name)
        self.op('set', edid, 'WNAM', welcome.replace('\n', '\\n'))  # one spec line per operation

    def spawn_script(self, edid, spawns=(), ai_arena=False, count_spawn=''):
        """count_spawn: a "how many" menu for this leveled list (items 1 to SPAWN_COUNT_MAX spawn that many)."""
        sc = 'SandboxRoom:SpawnTerminalScript'
        self.op('script', edid, sc)
        self.op('prop', edid, sc, 'SBR_ArenaMarker', 'Object', '@SBR_ArenaMarker')
        self.op('prop', edid, sc, 'SBR_Main', 'Object', '@SBR_Main')
        if ai_arena:
            self.op('prop', edid, sc, 'SpawnPoints', 'Array of Object',
                    ','.join(f'@SBR_ArenaSpawn{k}' for k in range(len(ARENA_SPAWNS))))
            self.op('prop', edid, sc, 'Zone', 'Object', '@SBR_ArenaZone')
        if count_spawn:
            self.op('prop', edid, sc, 'CountSpawn', 'Object', '@' + count_spawn)
            for n in range(1, SPAWN_COUNT_MAX + 1):
                self.op('menu', edid, n, f'Spawn {n}', '-', '-')
        if spawns:
            self.op('prop', edid, sc, 'Spawns', 'Array of Object',
                    ','.join('@' + lvln for _, lvln in spawns))
        for n, (text, _) in enumerate(spawns, 1):
            self.op('menu', edid, n, text, '-', '-')


def wall_ring(s: Spec, prefix: str, x0: int, x1: int, y0: int, y1: int, doors: dict | None = None):
    """Three storeys of high-tech wall around the room x0..x1, y0..y1 (multiples of 256), facing inwards, with
    rounded inner corners. doors: side ('N', 'S', 'E', 'W') -> x or y centres of cells whose ground storey gets
    the large door opening (the door itself is placed separately, see door())."""
    doors = doors or {}
    xs = range(x0 + G // 2, x1, G)
    ys = range(y0 + G // 2, y1, G)
    sides = {'W': [(x0 + G // 2, y, 0) for y in ys[1:-1]], 'E': [(x1 - G // 2, y, 180) for y in ys[1:-1]],
             'N': [(x, y1 - G // 2, 90) for x in xs[1:-1]], 'S': [(x, y0 + G // 2, 270) for x in xs[1:-1]]}
    for side, cells in sides.items():
        for k, (x, y, rz) in enumerate(cells):
            opening = (x if side in 'NS' else y) in doors.get(side, ())
            for tier in WALL_TIERS:
                piece = 'WallExLg01' if opening and tier == 'Mid02' else 'Wall01'
                # the door opening's sill lies at floor height and flickers against the floor (z-fighting): lift
                # the piece a unit; its top tucks into the storey above
                z = DOOR_SILL_LIFT if piece == 'WallExLg01' else 0
                s.ref(f'{prefix}{side}{k}_{tier}', f'@HitLgRm{tier}{piece}', x, y, z, rz=rz, opts=SWAP)
    corners = {'NW': (xs[0], ys[-1], 0), 'NE': (xs[-1], ys[-1], 90), 'SE': (xs[-1], ys[0], 180),
               'SW': (xs[0], ys[0], 270)}
    for name, (x, y, rz) in corners.items():
        for tier in WALL_TIERS:
            s.ref(f'{prefix}{name}_{tier}', f'@HitLgRm{tier}CorIn01', x, y, rz=rz, opts=SWAP)


def divider(s: Spec, prefix: str, y: int, x0: int, x1: int):
    """A full-height wall along the X axis at y, finished on both faces (the kit's walls are one-sided). Its x0 end
    is open to the room, so outer-corner blocks (32 square, finished on two faces) close the hollow edge: they sit
    in the cells just past the end, in the corner touching the wall's back line. The x1 end runs into a wall."""
    for k, x in enumerate(range(x0 + G // 2, x1, G)):
        for tier in WALL_TIERS:
            s.ref(f'{prefix}_{k}N_{tier}', f'@HitLgRm{tier}Wall01', x, y + G // 2, rz=270, opts=SWAP)
            s.ref(f'{prefix}_{k}S_{tier}', f'@HitLgRm{tier}Wall01', x, y - G // 2, rz=90, opts=SWAP)
    for tier in WALL_TIERS:
        s.ref(f'{prefix}_EndN_{tier}', f'@HitLgRm{tier}CorOut01', x0 - G // 2, y + G // 2, rz=180, opts=SWAP)
        s.ref(f'{prefix}_EndS_{tier}', f'@HitLgRm{tier}CorOut01', x0 - G // 2, y - G // 2, rz=90, opts=SWAP)


def door(s: Spec, edid: str, x: int, y: int, along_x: bool):
    """A sliding high-tech door in a large wall opening on the line between two rooms' walls. AutoDoorScript opens
    it as the player approaches from either side; it can also be opened by hand (and by NPCs)."""
    s.ref(edid, '@HitDoorLg01', x, y, rz=0 if along_x else 90, opts=SWAP)
    s.op('script', edid, 'SandboxRoom:AutoDoorScript')


def slab_grid(s: Spec, prefix: str, x0: int, x1: int, y0: int, y1: int, z: int, big: bool, base=FLOOR_BASE,
              opts=SWAP):
    """Floor (or, seen from below, ceiling) slabs covering x0..x1, y0..y1 with their top at z. big: 512 tiles
    (the 256 slab at scale 2, a quarter of the references)."""
    step = 2 * G if big else G
    for i, x in enumerate(range(x0 + step // 2, x1, step)):
        for j, y in enumerate(range(y0 + step // 2, y1, step)):
            s.ref(f'{prefix}_{i}_{j}', base, x, y, z, opts=(opts + ' scale=2') if big else opts)


def ceiling(s: Spec, prefix: str, x0: int, x1: int, y0: int, y1: int, lights: list):
    """Ceiling slabs over the top storey, and Institute ceiling lights at the given (x, y) points."""
    big = (x1 - x0) % (2 * G) == 0 and (y1 - y0) % (2 * G) == 0
    slab_grid(s, prefix + 'Ceiling', x0, x1, y0, y1, WALL_TOP + (2 * 32 if big else 32), big)
    for k, (x, y) in enumerate(lights):
        s.ref(f'{prefix}Lamp_{k}', '@InsLightFixture02', x, y, WALL_TOP)
        s.ref(f'{prefix}Light_{k}', LIGHT_BASE, x, y, WALL_TOP - 60, opts=f'radius={LIGHT_RADIUS}')


def light(s: Spec, edid: str, x: int, y: int, z: int, radius: int = LIGHT_RADIUS):
    """A light under a gallery deck, with its fixture on the deck's underside."""
    s.ref(edid + 'Lamp', '@InsLightFixture02', x, y, z)
    s.ref(edid, LIGHT_BASE, x, y, z - 40, opts=f'radius={radius}')


EDGE_RZ = {'S': 0, 'W': 90, 'N': 180, 'E': 270}  # turns a deck edge piece (made for the cell's south edge)


def deck(s: Spec, prefix: str, cells: list, z: int, rails: list):
    """A gallery deck: slabs on 256 cells (centre points) with their top at z, and an edge trim and handrail
    on each (cell, side) in rails."""
    for k, (x, y) in enumerate(cells):
        s.ref(f'{prefix}_{k}', FLOOR_BASE, x, y, z, opts=SWAP)
    for k, ((x, y), side) in enumerate(rails):
        s.ref(f'{prefix}Edge_{k}', '@HitFloorEdgeStraight01', x, y, z, rz=EDGE_RZ[side], opts=SWAP)
        s.ref(f'{prefix}Rail_{k}', '@HitFloorRailStraight01', x, y, z, rz=EDGE_RZ[side], opts=SWAP)


def stairs(s: Spec, edid: str, top_x: int, top_y: int, z: int, climbs: str):
    """One storey of lobby stairs whose top meets a deck edge at (top_x, top_y), height z; climbs: the compass
    direction of the climb (the piece climbs towards its local +Y). Measured from its model: steps of about 23
    up and 28 along, the last one at local y 5..32 and z 233, then the top platform at z 256 from y 33 to
    STAIRS_TOP_END. So the piece goes STAIRS_TOP_END back from the edge: its platform ends flush with the deck."""
    rz = {'N': 0, 'E': 90, 'S': 180, 'W': 270}[climbs]
    dx, dy = {'N': (0, 1), 'E': (1, 0), 'S': (0, -1), 'W': (-1, 0)}[climbs]
    s.ref(edid, '@HitExtIntStairs1Story01', top_x - dx * STAIRS_TOP_END, top_y - dy * STAIRS_TOP_END, z, rz=rz)


def cells(x0: int, x1: int, y0: int, y1: int) -> list:
    return [(x, y) for x in range(x0 + G // 2, x1, G) for y in range(y0 + G // 2, y1, G)]


def hall(s: Spec):
    s.comment('the main hall: an interior cell (no sky), high-tech walls in the Institute finish, three storeys')
    s.op('new', 'CELL', CELL)  # xEdit cannot copy a cell as new, so build it from scratch
    s.op('set', CELL, 'FULL', 'Sandbox Room')
    s.op('set', CELL, 'DATA', '1')  # Is Interior (the sky and sky lighting of the first versions are gone)
    s.op('set', CELL, 'XCIM', '@InstituteImageSpaceF4New')
    s.op('set', CELL, 'LTMP', '@InstituteLightingTemplateNew')
    slab_grid(s, 'SBR_Floor', X0, X1, Y0, Y1, 0, big=True)
    wall_ring(s, 'SBR_Hall', X0, X1, Y0, Y1, doors={'S': [HALL_DOOR_X]})
    door(s, 'SBR_WingDoor', HALL_DOOR_X, Y0, along_x=True)
    lights = [(x, y) for x in range(X0 + 384, LANE_X, 768) for y in (-512, 512)]
    lights += [(LANE_X + G, -512), (LANE_X + G, 512)]
    lights += [(BAY_X + 768, Y0 + BAY_WIDTH * n + BAY_WIDTH // 2) for n in range(len(BAYS))]
    ceiling(s, 'SBR_Hall', X0, X1, Y0, Y1, lights)
    s.comment('markers: arrival point, return point (moved by the holotape), arena spawn point, coc target')
    s.ref('SBR_EntryMarker', '@XMarkerHeading', X0 + 450, 0, rz=90, persistent=True)
    s.ref('SBR_ReturnMarker', '@XMarkerHeading', X0 + 450, 200, persistent=True)
    s.ref('SBR_ArenaMarker', '@XMarkerHeading', (ARENA_X + LANE_X) // 2, -200, rz=270, persistent=True)
    s.ref('SBR_COCMarker', '@COCMarkerHeading', X0 + 450, -100, rz=90)


def hall_galleries(s: Spec):
    s.comment('shooting galleries over the firing lane at storeys 1 and 2, railed towards the bays (east) and '
              'the open arena (west). Stairs from the arena: ground -> storey 1 lands on a landing by the north '
              'wall, storey 1 -> 2 climbs from that landing')
    lane = cells(LANE_X, BAY_X, Y0, Y1)
    landing = cells(LANE_X - 2 * G, LANE_X, Y1 - 2 * G, Y1)
    east = [((x, y), 'E') for x, y in lane if x > LANE_X + G]
    west = [((x, y), 'W') for x, y in lane if x < LANE_X + G]
    stair1_y, stair2_y = Y1 - 2 * G + 128 + 2, Y1 - 154
    deck(s, 'SBR_Gallery1', lane + landing, H1,
         east + [c for c in west if c[0][1] < Y1 - 2 * G] +
         [((x, y), 'S') for x, y in landing if y < Y1 - G] + [((x, y), 'W') for x, y in landing
                                                               if x < LANE_X - G and y > Y1 - G])
    deck(s, 'SBR_Gallery2', lane, H2, east + [c for c in west if c[0][1] < Y1 - G])
    stairs(s, 'SBR_GalleryStairs1', LANE_X - 2 * G, stair1_y, 0, 'E')
    stairs(s, 'SBR_GalleryStairs2', LANE_X, stair2_y, H1, 'E')
    for n, y in enumerate((-640, 0, 640)):
        light(s, f'SBR_LaneLight{n}', LANE_X + G, y, H1 - 32, 700)
        light(s, f'SBR_Gallery1Light{n}', LANE_X + G, y, H2 - 32, 700)


def target_range(s: Spec):
    s.comment('target range: four bays walled off from each other, floor to ceiling, to contain blasts')
    for k, y in enumerate(range(Y0 + BAY_WIDTH, Y1, BAY_WIDTH)):
        divider(s, f'SBR_BayWall{k}', y, BAY_X, X1)
    for t in (1, 2, 3):
        stand = f'SBR_TargetStand0{t}'
        s.op('new', 'STAT', stand)  # static copies of the target stands, so they never fall over
        s.op('set', stand, 'Model\\MODL', f'Props\\TargetPractice\\50sTargetPractice0{t}.nif')
        for axis, v in zip(('X1', 'Y1', 'Z1', 'X2', 'Y2', 'Z2'), (-36, -31, 0, 30, 2, 129)):
            s.op('set', stand, f'OBND\\{axis}', v)
    s.op('copy', '@DetectLifePATargetFXS', HOLOGRAM_SHADER[1:])
    s.op('remove', HOLOGRAM_SHADER[1:], 'NAM8')  # the orange gradient
    for name, rgb in HOLOGRAM_FIELDS.items():
        for channel, v in zip(('Red', 'Green', 'Blue'), rgb):
            s.op('set', HOLOGRAM_SHADER[1:], f'DNAM\\Data\\{name}\\{channel}', v)
    for name, v in HOLOGRAM_VALUES.items():
        s.op('set', HOLOGRAM_SHADER[1:], f'DNAM\\Data\\{name}', v)
    for edid, template, name in HOLO_TARGETS:
        s.op('copy', '@' + template, edid)
        s.op('set', edid, 'FULL', name)
        s.op('remove', edid, 'INAM')  # no death loot
        s.op('set', edid, r'ACBS\XP Value Offset', HOLO_XP_OFFSET)
    s.comment('a TARGET RANGE sign on the floor of the firing lane, read walking towards the bay terminals')
    s.ref('SBR_FloorTargetRange', s.sign('TARGET RANGE', 'Floor'), (LANE_X + BAY_X) // 2 - 40, 0, 1)
    for n, bay in enumerate(BAYS):
        y0 = Y0 + BAY_WIDTH * n
        cy = y0 + BAY_WIDTH // 2
        key = bay['key']
        if not bay['types']:
            # target stands at three distances, three across
            for d, depth in enumerate((400, 800, 1250)):
                for c, dy in enumerate((-150, 0, 150)):
                    s.ref(f'SBR_Bay{key}Stand_{d}_{c}', f'@SBR_TargetStand0{c + 1}', BAY_X + depth, cy + dy,
                          rz=FACE_WEST_MARKER)
            continue
        ctl, sc = f'SBR_Bay{key}Marker', 'SandboxRoom:TargetBayScript'
        s.ref(ctl, '@XMarkerHeading', BAY_X + BAY_TARGET_DEPTH, cy, rz=FACE_WEST_MARKER, persistent=True)
        s.op('script', ctl, sc)
        s.op('prop', ctl, sc, 'TargetTypes', 'Array of Object', ','.join('@' + l for _, l in bay['types']))
        s.op('prop', ctl, sc, 'TargetCount', 'Int32', bay['count'])
        s.op('prop', ctl, sc, 'Health', 'Object', '@Health')
        s.op('prop', ctl, sc, 'Aggression', 'Object', '@Aggression')
        s.op('prop', ctl, sc, 'Confidence', 'Object', '@Confidence')
        s.op('prop', ctl, sc, 'DamageResist', 'Object', '@DamageResist')
        s.op('prop', ctl, sc, 'EnergyResist', 'Object', '@EnergyResist')
        s.op('prop', ctl, sc, 'Hologram', 'Object', HOLOGRAM_SHADER)
        term = f'SBR_Bay{key}Terminal'
        s.terminal(term, f'Target Bay: {bay["title"]}', f'SANDBOX ROOM TARGET RANGE\n{bay["title"]}\n'
                   'Targets stand still and come back a few seconds after dying.')
        for i, (text, _) in enumerate(bay['types'], 1):
            s.op('menu', term, i, f'Target: {text}', '-', '-')
        for i, text in enumerate(HEALTH_LABELS, 10):
            s.op('menu', term, i, f'Health: {text}', '-', '-')
        s.op('menu', term, 15, 'Armor: game default', '-', '-')
        s.op('menu', term, 16, 'Armor: none (health = damage taken)', '-', '-')
        s.op('menu', term, 20, 'Clear the bay', '-', '-')
        s.op('script', term, 'SandboxRoom:TargetTerminalScript')
        s.op('prop', term, 'SandboxRoom:TargetTerminalScript', 'SBR_Bay', 'Object', '@' + ctl)
        s.ref(term + 'Ref', '@' + term, BAY_X - 70, y0 + 90, rz=FACE_WEST)
        label(s, term + 'Label', bay['title'].split(' (')[0], BAY_X - 70, y0 + 90, 'W', 127, 34)


def wing(s: Spec):
    s.comment('the wing south of the hall: a lobby with the arena terminals, then the AI arena through a door on '
              'each side of them. Mobs there have AI only while the player is inside the arena')
    wall_ring(s, 'SBR_Lobby', LX0, LX1, LY0, LY1, doors={'N': [HALL_DOOR_X], 'S': WING_DOORS_X})
    slab_grid(s, 'SBR_LobbyFloor', LX0, LX1, LY0, LY1, 0, big=False)
    ceiling(s, 'SBR_Lobby', LX0, LX1, LY0, LY1, [(x, (LY0 + LY1) // 2) for x in range(LX0 + 384, LX1, 512)])

    wall_ring(s, 'SBR_Arena', AX0, AX1, AY0, AY1, doors={'N': WING_DOORS_X})
    for n, x in enumerate(WING_DOORS_X):
        door(s, f'SBR_ArenaDoor{n}', x, AY1, along_x=True)
    slab_grid(s, 'SBR_ArenaBase', AX0, AX1, AY0, AY1, 0, big=True)
    for i, x in enumerate(range(AX0 + 256, AX1, 512)):
        for j, y in enumerate(range(AY0 + 256, AY1, 512)):
            s.ref(f'SBR_ArenaDirt_{i}_{j}', '@QryFloor01dirtyALL', x, y, 1)
    ceiling(s, 'SBR_Arena', AX0, AX1, AY0, AY1,
            [(x, y) for x in range(AX0 + 512, AX1, 1024) for y in range(AY0 + 512, AY1, 1024)])

    s.comment('arena balconies along the north wall at storeys 1 and 2; storey 1 has a landing at the east end '
              'for the stairs up to storey 2')
    b0, b1, depth = BALCONY_X0, BALCONY_X1, AY1 - 2 * G
    span = cells(b0, b1, depth, AY1)
    landing = cells(b1, b1 + 2 * G, depth, AY1)
    stair_y = AY1 - 154
    south = [((x, y), 'S') for x, y in span + landing if y < depth + G]
    deck(s, 'SBR_Balcony1', span + landing, H1,
         south + [((x, y), 'W') for x, y in span if x < b0 + G and y < AY1 - G] +
         [((x, y), 'E') for x, y in landing if x > b1 + G])
    deck(s, 'SBR_Balcony2', span, H2,
         [c for c in south if c[0][0] < b1] + [((x, y), 'W') for x, y in span if x < b0 + G] +
         [((x, y), 'E') for x, y in span if x > b1 - G and y < AY1 - G])
    stairs(s, 'SBR_BalconyStairs1', b0, stair_y, 0, 'E')
    stairs(s, 'SBR_BalconyStairs2', b1, stair_y, H1, 'W')
    for n, x in enumerate(range(b0 + 512, b1, 1024)):
        light(s, f'SBR_BalconyLight{n}', x, depth + G, H1 - 32, 700)
        light(s, f'SBR_Balcony1Light{n}', x, depth + G, H2 - 32, 700)

    s.comment('the arena floor: dirt, mounds, rock outcrops and dead trees around open ground (no buildings)')
    for k, (base, x, y, z, rz) in enumerate(TERRAIN):
        s.ref(f'SBR_Terrain_{k}', '@' + base, x, y, z, rz=rz)

    s.comment('arena spawn points and the zone that switches the spawns\' AI on while the player is inside')
    for k, (x, y) in enumerate(ARENA_SPAWNS):
        s.ref(f'SBR_ArenaSpawn{k}', '@XMarkerHeading', x, y, 16, rz=k * 40 % 360, persistent=True)
    zone, zs = 'SBR_ArenaZone', 'SandboxRoom:ArenaZoneScript'
    s.ref(zone, '@XMarkerHeading', (AX0 + AX1) // 2, (AY0 + AY1) // 2, 16, persistent=True)
    s.op('script', zone, zs)
    for prop, v in (('MinX', AX0), ('MaxX', AX1), ('MinY', AY0), ('MaxY', AY1)):
        s.op('prop', zone, zs, prop, 'Float', v)


INWARD = {'N': (0, 1), 'S': (0, -1), 'E': (1, 0), 'W': (-1, 0)}  # unit vector of a facing


def along_wall(wall: str, along: float, out: float) -> tuple[int, int]:
    """A point `along` the wall's run axis and `out` units into the room from the wall line."""
    facing, axis, _, line = WALLS[wall]
    dx, dy = INWARD[facing]
    return (round(line + dx * out), round(along)) if axis == 'y' else (round(along), round(line + dy * out))


def label(s: Spec, edid: str, text: str, x: int, y: int, facing: str, top: int, front: int):
    """A label sign standing on top of a cabinet or terminal (top: its height; front: centre to front edge)."""
    dx, dy = INWARD[facing]
    s.ref(edid, s.sign(text, 'Label'), x + dx * (front - 6), y + dy * (front - 6), top + LABEL_H // 2 + 1,
          rz=SIGN_RZ[facing])


def header(s: Spec, edid: str, text: str, wall: str, centre: int, length: int, shelf=True):
    """A section header on the wall, with an Institute shelf under it as long as the section."""
    facing = WALLS[wall][0]
    x, y = along_wall(wall, centre, WALL_FACE + 1)
    s.ref(edid, s.sign(text, 'Header'), x, y, HEADER_Z, rz=SIGN_RZ[facing])
    if shelf:
        n = max(1, -(-length // SHELF_W))
        for k in range(n):
            sx, sy = along_wall(wall, centre + (k - (n - 1) / 2) * SHELF_W, WALL_FACE)
            s.ref(f'{edid}Shelf_{k}', '@InstituteShelfA01', sx, sy, SHELF_Z, rz=SHELF_RZ[facing])


def dlc_items(chests: dict, d: Dlc, section: str) -> list:
    cats = next(c for k, _, _, _, c in SECTIONS if k == section)
    return [x for cat in cats for x in chests.get((d.master, cat), [])]


def section_slots(key: str, chests: dict) -> list:
    """The cabinets of a section, left to right: ('base', category), then ('dlc', Dlc)."""
    cats = next(c for k, _, _, _, c in SECTIONS if k == key)
    return ([('base', c) for c in cats if chests.get(('Fallout4.esm', c))] +
            [('dlc', d) for d in DLCS if dlc_items(chests, d, key)])


def slot_place(key: str, chests: dict, slot) -> tuple[int, int, str]:
    """Where a slot's cabinet stands: x, y and the facing of its front."""
    _, _, wall, centre, _ = next(sec for sec in SECTIONS if sec[0] == key)
    slots = section_slots(key, chests)
    k = slots.index(slot)
    facing, _, step, _ = WALLS[wall]
    x, y = along_wall(wall, centre + step * (k - (len(slots) - 1) / 2) * SLOT_PITCH,
                      WALL_FACE + CABINET_DEPTH // 2 + 2)
    return x, y, facing


def cabinet(s: Spec, edid: str, name: str, items: list, place, text: str):
    x, y, facing = place
    s.chest(edid, name, items)
    s.ref(edid + 'Ref', '@' + edid, x, y, rz=FACE[facing])
    label(s, edid + 'Label', text, x, y, facing, CABINET_TOP, CABINET_DEPTH // 2)


def spawn_terminal(s: Spec, prefix: str, title: str, welcome: str, menus: dict, x: int, y: int, text: str):
    """An arena spawn terminal in the lobby: a submenu per group, plus kill/remove everything it spawned."""
    top = prefix + 'Terminal'
    s.terminal(top, title, f'{title.upper()}\n{welcome}')
    for n, (group, spawns) in enumerate(menus.items(), 1):
        sub = prefix + 'Menu_' + key_of(group)
        s.terminal(sub, title, f'{title.upper()}\n{group}: pick an enemy, then how many.')
        for i, (enemy, lvln) in enumerate(spawns, 1):
            count = prefix + 'Count_' + key_of(enemy)
            s.terminal(count, title, f'{title.upper()}\n{enemy}: how many? Each lands at a random spot in the arena.')
            s.spawn_script(count, (), True, lvln)
            s.op('menu', sub, i, enemy, '@' + count, '-')
        s.op('menu', top, n, group, '@' + sub, '-')
    s.op('menu', top, MENU_KILL_ALL, 'Kill everything spawned', '-', '-')
    s.op('menu', top, MENU_REMOVE_ALL, 'Remove everything spawned', '-', '-')
    s.spawn_script(top, (), True)
    s.ref(top + 'Ref', '@' + top, x, y, rz=FACE_NORTH)
    label(s, top + 'Label', text, x, y, 'N', 127, 34)


def storage(s: Spec, chests: dict):
    s.comment('storage: signed sections of filing cabinets along the walls (see SECTIONS); whatever is taken from '
              'a cabinet is put straight back. The add-on plugins fill their own slots')
    for key, text, wall, centre, _ in SECTIONS:
        slots = section_slots(key, chests)
        header(s, f'SBR_Header{key}', text, wall, centre, len(slots) * SLOT_PITCH)
        for slot in slots:
            kind, what = slot
            if kind == 'base':
                cabinet(s, 'SBR_Cab_' + key_of(what), what, chests[('Fallout4.esm', what)],
                        slot_place(key, chests, slot), what)


def main_plugin(s: Spec, chests: dict):
    s.file_op(MAIN)
    s.op('master', 'Fallout4.esm')
    s.op('header', 'CNAM', AUTHOR)
    s.op('header', 'SNAM', DESCRIPTION)
    hall(s)
    hall_galleries(s)
    target_range(s)
    wing(s)

    s.comment('crafting stations (north wall, facing into the room), the power armor frames by their station')
    for n, (base, x, rz) in enumerate(STATIONS):
        s.ref(f'SBR_Station_{n}', base, x, Y1 - 200, rz=rz)
    for n, x in enumerate(PA_FRAMES_X):
        s.ref(f'SBR_PowerArmorFrame_{n}', '@PowerArmorFrameFurnitureNoCore', x, Y1 - 190, rz=FACE_SOUTH)

    storage(s, chests)

    s.comment('globals, holotape and the quest that hands it out after Vault 111')
    s.op('new', 'GLOB', 'SBR_ReturnSaved')
    s.op('set', 'SBR_ReturnSaved', 'FNAM', 'Short')
    s.op('set', 'SBR_ReturnSaved', 'FLTV', '0')

    s.comment('the holotape: teleport in (remembering where the player was) and back out')
    s.terminal('SBR_HolotapeTerminal', 'Sandbox Room', HOLOTAPE_WELCOME)
    s.op('menu', 'SBR_HolotapeTerminal', 1, 'Teleport In', '-', f'GetInCell:@{CELL}:0')
    s.op('menu', 'SBR_HolotapeTerminal', 2, 'Teleport Out', '-', f'GetInCell:@{CELL}:1')

    s.op('new', 'NOTE', 'SBR_Holotape')
    for path, value in (('OBND\\X1', '-3'), ('OBND\\Y1', '-3'), ('OBND\\X2', '3'), ('OBND\\Y2', '3'),
                        ('OBND\\Z2', '1'), ('PTRN', '@MiscHolotape'), ('FULL', '(Sandbox Room) Holotape'),
                        ('Model\\MODL', 'Props\\Holotape_Prop.nif'), ('YNAM', '@ITMHolotapeUp'),
                        ('ZNAM', '@ITMHolotapeDown'), ('DNAM', 'Terminal'), ('SNAM\\Terminal', '@SBR_HolotapeTerminal')):
        s.op('set', 'SBR_Holotape', path, value)
    s.op('script', 'SBR_HolotapeTerminal', 'SandboxRoom:HolotapeScript')
    for prop, value in (('SBR_EntryMarker', '@SBR_EntryMarker'), ('SBR_ReturnMarker', '@SBR_ReturnMarker'),
                        ('SBR_ReturnSaved', '@SBR_ReturnSaved')):
        s.op('prop', 'SBR_HolotapeTerminal', 'SandboxRoom:HolotapeScript', prop, 'Object', value)

    s.op('new', 'QUST', 'SBR_Main')
    s.op('set', 'SBR_Main', 'FULL', 'Sandbox Room')
    s.op('set', 'SBR_Main', 'DNAM\\Flags', '1')  # Start Game Enabled
    s.op('script', 'SBR_Main', 'SandboxRoom:GiveHolotapeScript')
    s.op('prop', 'SBR_Main', 'SandboxRoom:GiveHolotapeScript', 'SBR_Holotape', 'Object', '@SBR_Holotape')
    s.op('prop', 'SBR_Main', 'SandboxRoom:GiveHolotapeScript', 'MQ102', 'Object', '@MQ102')
    s.op('script', 'SBR_Main', 'SandboxRoom:SpawnTrackerScript')

    s.comment('arena: an "ARENA" sign over the hall\'s door to the lobby; in the lobby the terminals stand in a '
              'row against its south wall, base game first, then one per add-on (placed by the add-on plugins)')
    s.ref('SBR_HeaderAIArena', s.sign('ARENA', 'Header'), HALL_DOOR_X, Y0 + WALL_FACE + 1, AI_SIGN_Z,
          rz=SIGN_RZ['N'])
    spawn_terminal(s, 'SBR_AISpawn', 'Sandbox Room Arena',
                   'Spawns wake up when you enter the arena and freeze when you leave.', SPAWN_MENUS,
                   AI_TERMINAL_X, AI_TERMINAL_Y, 'Base Game')
    s.op('prune', CELL, 'SBR_')
    s.op('prunerecords', 'SBR_')


def dlc_plugin(s: Spec, d: Dlc, chests: dict):
    s.file_op(f'Sandbox Room - {d.title}.esp')
    s.op('master', 'Fallout4.esm')
    s.op('master', d.master)
    s.op('master', MAIN)
    s.op('header', 'CNAM', AUTHOR)
    s.op('header', 'SNAM', f'Sandbox Room add-on for {d.title}: its items in the storage cabinets'
                           + (', its enemies on an arena terminal' if d.spawns else '')
                           + (', its crafting station' if d.stations else '') + '. Needs Sandbox Room.esp.')
    short = d.title.replace(' Workshop', '')
    s.comment(f'{d.title}: a cabinet in each storage section it has items for, its crafting station and spawns')
    for key, *_ in SECTIONS:
        if dlc_items(chests, d, key):
            name = DLC_SECTION_NAMES[key]
            cabinet(s, f'SBR_{d.key}_Cab_{key}', f'{short} {name}', dlc_items(chests, d, key),
                    slot_place(key, chests, ('dlc', d)), short)
    for n, (base, x, rz) in enumerate(d.stations):
        s.ref(f'SBR_{d.key}_Station_{n}', base, x, Y1 - 200, rz=rz)
    if d.spawns:
        menus = {'Enemies': [sp for sp in d.spawns if not sp[0].startswith('Legendary')],
                 'Legendaries': [sp for sp in d.spawns if sp[0].startswith('Legendary')]}
        spawn_terminal(s, f'SBR_{d.key}_AISpawn', f'Sandbox Room Arena: {d.title}', d.title,
                       {g: sp for g, sp in menus.items() if sp}, d.ai_terminal_x, AI_TERMINAL_Y, short)
    s.op('prune', CELL, 'SBR_')
    s.op('prunerecords', 'SBR_')


def main():
    chests: dict = {}
    for i in load_items():
        if usable(i) and (where := chest_of(i)):
            chests.setdefault((i.file, where[0]), []).append((i, where[1]))
    s = Spec()
    s.lines.append('# Generated by tools/build/make_spec.py - do not edit by hand')
    main_plugin(s, chests)
    for d in DLCS:
        dlc_plugin(s, d, chests)
    SPEC.write_text('\n'.join(s.lines) + '\n', encoding='utf8')
    SIGNS_JSON.write_text(json.dumps(SIGNS, indent=1), encoding='utf8')
    for (f, name), items in sorted(chests.items()):
        print(f'{f:20} {name:28} {len(items)}')
    print(f'{SPEC.relative_to(REPO)}: {len(s.lines)} lines, {len(SIGNS)} signs')


if __name__ == '__main__':
    main()
