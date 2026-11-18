Scriptname SandboxRoom:LightingTerminalScript extends Terminal
{The Lighting terminal (1.2): item N sets every light in the room to N * Step percent. Each light is placed once per
level, under that level's enable-parent marker (Markers[N - 1]); this enables one marker and disables the others.
Current holds the level in percent, for the terminal's text.}

ObjectReference[] Property Markers Auto Const
Int Property Step = 20 Auto Const
GlobalVariable Property Current Auto Const

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	If auiMenuItemID < 1 || auiMenuItemID > Markers.Length
		Return
	EndIf
	; the new level first, so the room never goes dark in between
	Markers[auiMenuItemID - 1].Enable()
	int i = 0
	While i < Markers.Length
		If i != auiMenuItemID - 1
			Markers[i].Disable()
		EndIf
		i += 1
	EndWhile
	Current.SetValue(auiMenuItemID * Step)
	Debug.Trace("SandboxRoom lighting: " + auiMenuItemID * Step + "%")
EndEvent
