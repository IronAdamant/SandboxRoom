Scriptname SandboxRoom:HolotapeScript extends Terminal
{The Sandbox Room holotape: teleport into the room and back out to where the player was, and the safety net
(SafetyNetScript) on or off. The menu only shows the options that apply (conditions on the player's current cell
and on SBR_SafetyNet). Companions come along at once (the game's follow behaviour would only bring them a while
later).}

ObjectReference Property SBR_EntryMarker Auto Const Mandatory
{Where the player arrives in the room.}
ObjectReference Property SBR_ReturnMarker Auto Const Mandatory
{Moved to the player just before teleporting in, so it remembers their position, rotation, cell and worldspace.}
GlobalVariable Property SBR_ReturnSaved Auto Const Mandatory
{1 once a return point has been saved.}
SandboxRoom:SafetyNetScript Property SafetyNet Auto Const Mandatory

int Property MenuTeleportIn = 1 AutoReadOnly
int Property MenuTeleportOut = 2 AutoReadOnly
int Property MenuSafetyNetOn = 3 AutoReadOnly
int Property MenuSafetyNetOff = 4 AutoReadOnly

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	Actor player = Game.GetPlayer()
	If auiMenuItemID == MenuTeleportIn
		SBR_ReturnMarker.MoveTo(player)
		SBR_ReturnSaved.SetValue(1)
		player.MoveTo(SBR_EntryMarker)
		BringFollowers()
	ElseIf auiMenuItemID == MenuTeleportOut
		If SBR_ReturnSaved.GetValue() == 1
			player.MoveTo(SBR_ReturnMarker)
			BringFollowers()
		Else
			; Got here without the holotape (e.g. the console's coc), so there is nowhere to go back to.
			Debug.Notification("Sandbox Room: no return point saved. Use Teleport In from outside first.")
		EndIf
	ElseIf auiMenuItemID == MenuSafetyNetOn
		SafetyNet.SetSafetyNet(true)
	ElseIf auiMenuItemID == MenuSafetyNetOff
		SafetyNet.SetSafetyNet(false)
	EndIf
EndEvent

; The player's companions (Dogmeat too) to the player, as the game's VR Workshop travel does. One told to wait
; comes too: the game brings it along regardless (skipping it here made no difference in testing).
Function BringFollowers() global
	Actor player = Game.GetPlayer()
	Actor[] followers = Game.GetPlayerFollowers()
	int i = 0
	While i < followers.Length
		If followers[i] && !followers[i].IsDead()
			followers[i].MoveTo(player)
		EndIf
		i += 1
	EndWhile
EndFunction
