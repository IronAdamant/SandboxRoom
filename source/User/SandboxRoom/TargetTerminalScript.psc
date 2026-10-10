Scriptname SandboxRoom:TargetTerminalScript extends Terminal
{The terminal in front of a target bay. Items 1-9 pick the target type, 10-14 the health, 20 clears the bay.}

SandboxRoom:TargetBayScript Property SBR_Bay Auto Const Mandatory

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	If auiMenuItemID >= 1 && auiMenuItemID <= 9
		SBR_Bay.SetType(auiMenuItemID - 1)
	ElseIf auiMenuItemID == 10
		SBR_Bay.SetHealth(0.0)
	ElseIf auiMenuItemID == 11
		SBR_Bay.SetHealth(100.0)
	ElseIf auiMenuItemID == 12
		SBR_Bay.SetHealth(1000.0)
	ElseIf auiMenuItemID == 13
		SBR_Bay.SetHealth(10000.0)
	ElseIf auiMenuItemID == 14
		SBR_Bay.SetHealth(100000.0)
	ElseIf auiMenuItemID == 20
		SBR_Bay.Clear()
	EndIf
EndEvent
