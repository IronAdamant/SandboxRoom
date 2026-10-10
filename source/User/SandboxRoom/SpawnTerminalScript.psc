Scriptname SandboxRoom:SpawnTerminalScript extends Terminal
{A spawn terminal menu (or submenu). Menu item N spawns Spawns[N - 1] at the arena marker; the two utility items
remove or kill everything the terminals have spawned. Every spawn terminal shares one tracker on the main quest.}

Form[] Property Spawns Auto Const
{Leveled actor lists or actors, in menu order (item ID 1 = first entry).}
ObjectReference Property SBR_ArenaMarker Auto Const Mandatory
SandboxRoom:SpawnTrackerScript Property SBR_Main Auto Const Mandatory

int Property MenuRemoveAll = 900 AutoReadOnly
int Property MenuKillAll = 901 AutoReadOnly

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	If auiMenuItemID == MenuRemoveAll
		SBR_Main.RemoveAll()
	ElseIf auiMenuItemID == MenuKillAll
		SBR_Main.KillAll()
	ElseIf Spawns && auiMenuItemID >= 1 && auiMenuItemID <= Spawns.Length
		; Spread spawns out a little so a group does not stack on one point.
		ObjectReference spawned = SBR_ArenaMarker.PlaceAtMe(Spawns[auiMenuItemID - 1], abForcePersist = true)
		spawned.MoveTo(SBR_ArenaMarker, Utility.RandomFloat(-300.0, 300.0), Utility.RandomFloat(-300.0, 300.0), 0.0)
		SBR_Main.Track(spawned)
	EndIf
EndEvent
