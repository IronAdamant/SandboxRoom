Scriptname SandboxRoom:PerkPointsTerminalScript extends Terminal
{Perks & Stats: the Perk Points terminal. Item N (1 to 99) adds N unspent perk points. There is no taking them away:
the game ignored negative amounts in 1.1 testing, and it has no way to read or set the count.}

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	If auiMenuItemID >= 1 && auiMenuItemID < 100
		Game.AddPerkPoints(auiMenuItemID)
		Debug.Notification("Perk points: +" + auiMenuItemID)
	EndIf
EndEvent
