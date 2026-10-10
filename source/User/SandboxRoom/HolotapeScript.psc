Scriptname SandboxRoom:HolotapeScript extends Terminal
{The Sandbox Room holotape: teleport into the room and back out to where the player was.
The menu only shows the option that applies (conditions on the player's current cell).}

ObjectReference Property SBR_EntryMarker Auto Const Mandatory
{Where the player arrives in the room.}
ObjectReference Property SBR_ReturnMarker Auto Const Mandatory
{Moved to the player just before teleporting in, so it remembers their position, rotation, cell and worldspace.}
GlobalVariable Property SBR_ReturnSaved Auto Const Mandatory
{1 once a return point has been saved.}

int Property MenuTeleportIn = 1 AutoReadOnly
int Property MenuTeleportOut = 2 AutoReadOnly

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	Actor player = Game.GetPlayer()
	If auiMenuItemID == MenuTeleportIn
		SBR_ReturnMarker.MoveTo(player)
		SBR_ReturnSaved.SetValue(1)
		player.MoveTo(SBR_EntryMarker)
	ElseIf auiMenuItemID == MenuTeleportOut
		If SBR_ReturnSaved.GetValue() == 1
			player.MoveTo(SBR_ReturnMarker)
		Else
			; Got here without the holotape (e.g. the console's coc), so there is nowhere to go back to.
			Debug.Notification("Sandbox Room: no return point saved. Use Teleport In from outside first.")
		EndIf
	EndIf
EndEvent
