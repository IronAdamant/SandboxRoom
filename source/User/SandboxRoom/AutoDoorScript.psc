Scriptname SandboxRoom:AutoDoorScript extends ObjectReference
{A sliding door that opens by itself while the player is within Range of it, from either side, and closes again
when the player walks away. Polling starts however the door comes into play: first attached (OnInit), its 3D
loaded (OnLoad, also after loading a save made in the room), or its cell attached.}

float Property Range = 320.0 Auto Const
float Property PollInterval = 0.25 Auto Const

Event OnInit()
	StartPolling("init")
EndEvent

Event OnLoad()
	StartPolling("load")
EndEvent

Event OnCellAttach()
	StartPolling("cell attach")
EndEvent

Event OnCellDetach()
	CancelTimer()
EndEvent

Function StartPolling(string why)
	Debug.Trace(self + " SandboxRoom auto door: polling (" + why + ")")
	StartTimer(PollInterval)
EndFunction

Event OnTimer(int aiTimerID)
	Actor player = Game.GetPlayer()
	If player.GetParentCell() != GetParentCell()
		Return  ; OnCellAttach / OnLoad start polling again when the player is back
	EndIf
	bool near = player.GetDistance(self) < Range
	int openState = GetOpenState()  ; 1 open, 2 opening, 3 closed, 4 closing
	If near && (openState == 3 || openState == 4)
		Debug.Trace(self + " SandboxRoom auto door: opening")
		SetOpen(true)
	ElseIf !near && (openState == 1 || openState == 2)
		SetOpen(false)
	EndIf
	StartTimer(PollInterval)
EndEvent
