Scriptname SandboxRoom:SpawnTerminalScript extends Terminal
{A spawn terminal menu (or submenu). Menu item N spawns Spawns[N - 1]; the two utility items remove or kill
everything this family of terminals has spawned.
Hall terminals: spawns land around the arena marker and every hall terminal shares one tracker on the main quest.
AI arena terminals (Zone set): spawns land at a random one of SpawnPoints and the zone tracks them, so they only
have AI while the player is inside the arena.}

Form[] Property Spawns Auto Const
{Leveled actor lists or actors, in menu order (item ID 1 = first entry).}
ObjectReference Property SBR_ArenaMarker Auto Const Mandatory
SandboxRoom:SpawnTrackerScript Property SBR_Main Auto Const Mandatory
ObjectReference[] Property SpawnPoints Auto Const
{AI arena: where spawns may land (one picked at random each time).}
SandboxRoom:ArenaZoneScript Property Zone Auto Const
{AI arena: the zone that freezes and wakes the spawns.}

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
	ElseIf !Spawns || auiMenuItemID < 1 || auiMenuItemID > Spawns.Length
		Debug.Trace(self + " SandboxRoom spawn: item " + auiMenuItemID + " has no spawn (" + Spawns + ")")
	Else
		ObjectReference point = SBR_ArenaMarker
		float spread = 300.0
		If SpawnPoints && SpawnPoints.Length > 0
			point = SpawnPoints[Utility.RandomInt(0, SpawnPoints.Length - 1)]
			spread = 150.0
		EndIf
		; Spread spawns out a little so a group does not stack on one point.
		ObjectReference spawned = point.PlaceAtMe(Spawns[auiMenuItemID - 1], abForcePersist = true)
		spawned.MoveTo(point, Utility.RandomFloat(-spread, spread), Utility.RandomFloat(-spread, spread), 0.0)
		Debug.Trace(self + " SandboxRoom spawn: item " + auiMenuItemID + " placed " + spawned + " at " + point + " (zone " + Zone + ")")
		If Zone
			Zone.Track(spawned)
		Else
			SBR_Main.Track(spawned)
		EndIf
	EndIf
EndEvent
