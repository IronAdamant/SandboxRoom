Scriptname SandboxRoom:RelockScript extends ObjectReference
{Hack and Lock Practice: a chest or terminal that locks itself again, at its level, after it has been picked or hacked:
as soon as the player closes the chest or leaves the terminal, or, if it is left alone unopened, a little later.}

int Property LockLevel auto const
{The level to lock it at: 25 Novice, 50 Advanced, 75 Expert, 100 Master}
float Property RelockDelay = 15.0 auto const
{Seconds after a chest was picked before it locks again on its own, if it is never opened}
float Property TerminalPoll = 2.0 auto const
{A hacked terminal: how often to check whether the player has left it}

Event OnLoad()
	Debug.Trace(self + " RelockScript OnLoad: locked " + IsLocked() + " at " + GetLockLevel())
	Relock()  ; one left unlocked when the player last left the room
EndEvent

Event OnClose(ObjectReference akActionRef)
	Debug.Trace(self + " RelockScript OnClose")
	Relock()  ; a chest, closed after picking it
EndEvent

Event OnExitFurniture(ObjectReference akActionRef)
	Debug.Trace(self + " RelockScript OnExitFurniture")
	Relock()  ; a terminal, left after hacking it
EndEvent

Event OnLockStateChanged()
	Debug.Trace(self + " RelockScript OnLockStateChanged: locked " + IsLocked())
	If !IsLocked()
		If IsTerminal()
			StartTimer(TerminalPoll)  ; hacked: lock it again once the player has stepped away
		Else
			StartTimer(RelockDelay)  ; picked, then maybe never opened
		EndIf
	EndIf
EndEvent

Event OnTimer(int aiTimerID)
	; a terminal stays reserved by the player after use, so ask whether anyone is actually at it
	bool inUse = IsFurnitureInUse(true)
	Debug.Trace(self + " RelockScript OnTimer: in use " + inUse)
	If inUse
		StartTimer(TerminalPoll)
	Else
		Relock()
	EndIf
EndEvent

bool Function IsTerminal()
	Return GetBaseObject() as Terminal
EndFunction

Function Relock()
	If !IsLocked()
		SetLockLevel(LockLevel)
		Lock()
		Debug.Trace(self + " RelockScript locked again: locked " + IsLocked() + " at " + GetLockLevel())
	EndIf
EndFunction
