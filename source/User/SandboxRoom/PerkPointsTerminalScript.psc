Scriptname SandboxRoom:PerkPointsTerminalScript extends Terminal
{Perks & Stats: the Perk Points terminal. Item N (1 to 99) adds N unspent perk points; item 100 + N takes N away.
The vanilla game has no way to read the number of unspent points, so taking away more than there are is not
prevented.}

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	If auiMenuItemID >= 1 && auiMenuItemID < 100
		Game.AddPerkPoints(auiMenuItemID)
		Debug.Notification("Perk points: +" + auiMenuItemID)
	ElseIf auiMenuItemID > 100 && auiMenuItemID < 200
		Game.AddPerkPoints(100 - auiMenuItemID)
		Debug.Notification("Perk points: -" + (auiMenuItemID - 100))
	EndIf
EndEvent
