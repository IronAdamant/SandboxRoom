Scriptname SandboxRoom:ArenaZoneScript extends ObjectReference
{The AI arena, on a marker inside it. Keeps what the lobby terminals spawn there frozen (AI off) while the player
is outside the arena's walls, and awake while the player is inside. Checks the player's position every
PollInterval seconds while the room is loaded; polling starts when the script is first attached (OnInit) and
whenever the room's cell attaches.}

float Property MinX Auto Const Mandatory
float Property MaxX Auto Const Mandatory
float Property MinY Auto Const Mandatory
float Property MaxY Auto Const Mandatory
float Property PollInterval = 0.5 Auto Const

bool inside = false
ObjectReference[] spawned

Event OnInit()
	Debug.Trace(self + " SandboxRoom arena zone: polling (init)")
	StartTimer(PollInterval)
EndEvent

Event OnCellAttach()
	Debug.Trace(self + " SandboxRoom arena zone: polling (cell attach)")
	StartTimer(PollInterval)
EndEvent

Event OnCellDetach()
	CancelTimer()
EndEvent

Event OnTimer(int aiTimerID)
	Actor player = Game.GetPlayer()
	If player.GetParentCell() != GetParentCell()
		Return  ; the player left the room: OnCellAttach starts polling again on the way back
	EndIf
	bool now = PlayerInside()
	If now != inside
		inside = now
		Debug.Trace(self + " SandboxRoom arena zone: player inside = " + inside)
		ApplyAI()
	EndIf
	StartTimer(PollInterval)
EndEvent

bool Function PlayerInside()
	Actor player = Game.GetPlayer()
	float px = player.GetPositionX()
	float py = player.GetPositionY()
	Return player.GetParentCell() == GetParentCell() && px > MinX && px < MaxX && py > MinY && py < MaxY
EndFunction

; A new spawn: remembered, and frozen or awake to match where the player is.
Function Track(ObjectReference akRef)
	If spawned == None
		spawned = new ObjectReference[0]
	EndIf
	If spawned.Length >= 128
		spawned.Remove(0)  ; Papyrus arrays stop at 128: forget the oldest (it stays in the world)
	EndIf
	spawned.Add(akRef)
	inside = PlayerInside()
	Debug.Trace(self + " SandboxRoom arena zone: tracking " + akRef + ", player inside = " + inside)
	Actor a = akRef as Actor
	If a
		a.EnableAI(inside)
	EndIf
EndFunction

Function ApplyAI()
	int i = 0
	While spawned && i < spawned.Length
		Actor a = spawned[i] as Actor
		If a && !a.IsDead()
			a.EnableAI(inside)
		EndIf
		i += 1
	EndWhile
EndFunction

Function RemoveAll()
	int i = 0
	While spawned && i < spawned.Length
		If spawned[i]
			spawned[i].Disable()
			spawned[i].Delete()
		EndIf
		i += 1
	EndWhile
	spawned = new ObjectReference[0]
EndFunction

Function KillAll()
	int i = 0
	While spawned && i < spawned.Length
		Actor a = spawned[i] as Actor
		If a && !a.IsDead()
			a.EnableAI(true)  ; a frozen actor does not ragdoll
			a.Kill()
		EndIf
		i += 1
	EndWhile
EndFunction
