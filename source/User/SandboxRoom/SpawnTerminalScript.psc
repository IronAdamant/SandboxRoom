Scriptname SandboxRoom:SpawnTerminalScript extends Terminal
{A spawn terminal menu (or submenu). Two kinds of menu:
- a "how many" menu (CountSpawn set): menu item N spawns N of CountSpawn (1 to 10);
- a list menu (Spawns set): menu item N spawns one Spawns[N - 1].
The two utility items remove or kill everything this family of terminals has spawned.
Arena terminals (Zone set): each spawn lands at a random one of SpawnPoints and the zone tracks them, so they only
have AI while the player is inside the arena. Without a Zone, spawns land around SBR_ArenaMarker.}

Form[] Property Spawns Auto Const
{Leveled actor lists or actors, in menu order (item ID 1 = first entry).}
Form Property CountSpawn Auto Const
{"How many" menus: the leveled actor list or actor that items 1 to MaxCount spawn that many of.}
ObjectReference Property SBR_ArenaMarker Auto Const Mandatory
SandboxRoom:SpawnTrackerScript Property SBR_Main Auto Const Mandatory
ObjectReference[] Property SpawnPoints Auto Const
{Arena: where spawns may land (one picked at random for each spawn).}
SandboxRoom:ArenaZoneScript Property Zone Auto Const
{Arena: the zone that freezes and wakes the spawns.}
Faction Property ForceFaction Auto Const
{Spawns leave all their factions for this one (the hostile Brotherhood and Institute: always the player's enemies).}

int Property MaxCount = 10 AutoReadOnly
int Property MenuRemoveAll = 900 AutoReadOnly
int Property MenuKillAll = 901 AutoReadOnly

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	If auiMenuItemID == MenuRemoveAll
		If Zone
			Zone.RemoveAll()
		Else
			SBR_Main.RemoveAll()
		EndIf
	ElseIf auiMenuItemID == MenuKillAll
		If Zone
			Zone.KillAll()
		Else
			SBR_Main.KillAll()
		EndIf
	ElseIf CountSpawn && auiMenuItemID >= 1 && auiMenuItemID <= MaxCount
		int i = 0
		While i < auiMenuItemID
			SpawnOne(CountSpawn)
			i += 1
		EndWhile
	ElseIf Spawns && auiMenuItemID >= 1 && auiMenuItemID <= Spawns.Length
		SpawnOne(Spawns[auiMenuItemID - 1])
	EndIf
EndEvent

Function SpawnOne(Form akSpawn)
	ObjectReference point = SBR_ArenaMarker
	float spread = 300.0
	If SpawnPoints && SpawnPoints.Length > 0
		point = SpawnPoints[Utility.RandomInt(0, SpawnPoints.Length - 1)]
		spread = 150.0
	EndIf
	; Spread spawns out a little so a group does not stack on one point.
	ObjectReference spawned = point.PlaceAtMe(akSpawn, abForcePersist = true)
	spawned.MoveTo(point, Utility.RandomFloat(-spread, spread), Utility.RandomFloat(-spread, spread), 0.0)
	If ForceFaction
		Actor a = spawned as Actor
		a.RemoveFromAllFactions()
		a.AddToFaction(ForceFaction)
	EndIf
	Debug.Trace(self + " SandboxRoom spawn: placed " + spawned + " at " + point + " (zone " + Zone + ")")
	If Zone
		Zone.Track(spawned)
	Else
		SBR_Main.Track(spawned)
	EndIf
EndFunction
