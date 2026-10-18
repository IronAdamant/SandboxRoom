Scriptname SandboxRoom:ArenaZoneScript extends ObjectReference
{The AI arena, on a marker inside it. Keeps what the lobby terminals spawn there frozen (AI off) while the player
is outside the arena's walls, and awake while the player is inside. Checks the player's position every
PollInterval seconds while the room is loaded; polling starts when the script is first attached (OnInit) and
whenever the room's cell attaches.
Rounds: the player cannot die in the arena (SafetyNetScript keeps them essential while inside). Going down ends the
round: every enemy still standing freezes, healed, at a random spawn point, and the player is healed. Once they are
up, a countdown of CountdownSeconds runs with everything still frozen: time to leave, or to get ready; then the next
round starts. Leaving the arena for the lobby ends it all (spawns frozen, protection off, the knockout count back to
0).}

float Property MinX Auto Const Mandatory
float Property MaxX Auto Const Mandatory
float Property MinY Auto Const Mandatory
float Property MaxY Auto Const Mandatory
float Property PollInterval = 0.5 Auto Const
SandboxRoom:SafetyNetScript Property SafetyNet Auto Const Mandatory
ObjectReference[] Property SpawnPoints Auto Const Mandatory
{Where the enemies go back to when a round resets (one picked at random for each).}
ActorValue Property Health Auto Const Mandatory
ActorValue Property Rads Auto Const Mandatory
float Property CountdownSeconds = 13.0 Auto Const
{After a knockout, once the player is up: seconds before the enemies wake for the next round.}

float Property RestoreAll = 100000.0 AutoReadOnly  ; more than any health or radiation
float Property RespawnSpread = 150.0 AutoReadOnly   ; enemies land this far around their spawn point
float Property UpPoll = 0.25 AutoReadOnly           ; how often to check whether the downed player is up again
int Property UpMaxPolls = 60 AutoReadOnly           ; carry on anyway after this many checks (15 seconds)
int Property MessageAfter = 2 AutoReadOnly          ; seconds into the countdown: the knockout camera can outlast
                                                    ; the bleedout, and a message sent while it hides the HUD is lost
int Property PollTimer = 0 AutoReadOnly
int Property UpTimer = 1 AutoReadOnly
int Property CountdownTimer = 2 AutoReadOnly
int Property Fighting = 0 AutoReadOnly
int Property Down = 1 AutoReadOnly
int Property Countdown = 2 AutoReadOnly

bool inside = false
ObjectReference[] spawned
int round = 0                ; Fighting, Down or Countdown (only matters while the player is inside)
float roundStart
int knockouts                ; since the player came into the arena
int lastRound                ; seconds
int upPolls
int countdownLeft

Event OnInit()
	Debug.Trace(self + " SandboxRoom arena zone: polling (init)")
	StartTimer(PollInterval)
EndEvent

Event OnCellAttach()
	Debug.Trace(self + " SandboxRoom arena zone: polling (cell attach)")
	StartTimer(PollInterval)
EndEvent

Event OnCellDetach()
	CancelTimer(PollTimer)
	Leave()  ; e.g. teleported out from inside the arena
EndEvent

Event OnTimer(int aiTimerID)
	If aiTimerID == UpTimer
		WhenUp()
		Return
	ElseIf aiTimerID == CountdownTimer
		Tick()
		Return
	EndIf
	Actor player = Game.GetPlayer()
	If player.GetParentCell() != GetParentCell()
		Leave()
		Return  ; the player left the room: OnCellAttach starts polling again on the way back
	EndIf
	bool now = PlayerInside()
	If now && !inside
		Enter()
	ElseIf !now && inside
		Leave()
	EndIf
	StartTimer(PollInterval)
EndEvent

bool Function PlayerInside()
	Actor player = Game.GetPlayer()
	float px = player.GetPositionX()
	float py = player.GetPositionY()
	Return player.GetParentCell() == GetParentCell() && px > MinX && px < MaxX && py > MinY && py < MaxY
EndFunction

; Into the arena: the spawns wake, the player is protected, and a round starts.
Function Enter()
	inside = true
	Debug.Trace(self + " SandboxRoom arena zone: player inside")
	SafetyNet.SetArena(true)
	knockouts = 0
	StartRound()
EndFunction

; Out of the arena (into the lobby, or out of the room): everything stops.
Function Leave()
	CancelTimer(UpTimer)
	CancelTimer(CountdownTimer)
	If !inside
		Return
	EndIf
	inside = false
	Debug.Trace(self + " SandboxRoom arena zone: player outside")
	SetAI(false)
	SafetyNet.SetArena(false)
EndFunction

Function StartRound()
	round = Fighting
	roundStart = Utility.GetCurrentRealTime()
	SetAI(true)
EndFunction

; The player went down in the arena (from SafetyNetScript): the round is over and resets.
Function Knockout()
	If !inside || round == Down
		Return
	EndIf
	Actor player = Game.GetPlayer()
	int seconds = (Utility.GetCurrentRealTime() - roundStart) as int
	If round == Fighting
		knockouts += 1
		lastRound = seconds
	EndIf
	Debug.Trace(self + " SandboxRoom arena zone: knockout after " + seconds + " s")
	round = Down
	CancelTimer(CountdownTimer)
	ResetEnemies()
	player.ResetHealthAndLimbs()
	player.RestoreValue(Health, RestoreAll)
	upPolls = 0
	StartTimer(UpPoll, UpTimer)
EndFunction

; Every enemy still standing: frozen, out of combat, healed, back at a random spawn point. An actor with its AI off
; that is only moved stays drawn where it was until its AI is back (it then snaps over, mid-pose), so it is taken
; out of the world for the move and put back, which also redraws it standing.
Function ResetEnemies()
	int i = 0
	While spawned && i < spawned.Length
		Actor a = spawned[i] as Actor
		If a && !a.IsDead()
			a.EnableAI(false)
			a.StopCombat()
			a.Disable()
			ObjectReference point = SpawnPoints[Utility.RandomInt(0, SpawnPoints.Length - 1)]
			a.MoveTo(point, Utility.RandomFloat(-RespawnSpread, RespawnSpread), Utility.RandomFloat(-RespawnSpread, RespawnSpread), 0.0)
			a.Enable()
			a.ResetHealthAndLimbs()
		EndIf
		i += 1
	EndWhile
EndFunction

Function WhenUp()
	Actor player = Game.GetPlayer()
	If player.IsBleedingOut() && upPolls < UpMaxPolls
		upPolls += 1
		StartTimer(UpPoll, UpTimer)
		Return
	EndIf
	player.ResetHealthAndLimbs()
	player.RestoreValue(Health, RestoreAll)
	player.RestoreValue(Rads, RestoreAll)
	round = Countdown
	countdownLeft = CountdownSeconds as int
	Debug.Trace(self + " SandboxRoom arena zone: up after " + upPolls + " checks")
	StartTimer(1.0, CountdownTimer)
EndFunction

Function Tick()
	countdownLeft -= 1
	If countdownLeft <= 0
		Debug.Notification("Fight!")
		StartRound()
		Return
	EndIf
	If countdownLeft == (CountdownSeconds as int) - MessageAfter
		Debug.Trace(self + " SandboxRoom arena zone: knockout message")
		Debug.Notification("Knockout #" + knockouts + " after " + lastRound + " seconds. Next round in " + countdownLeft + " seconds: leave the arena to stop.")
	ElseIf countdownLeft == 5 || countdownLeft <= 3
		Debug.Notification(countdownLeft + "...")
	EndIf
	StartTimer(1.0, CountdownTimer)
EndFunction

; A new spawn: remembered, and frozen or awake to match the player and the round.
Function Track(ObjectReference akRef)
	If spawned == None
		spawned = new ObjectReference[0]
	EndIf
	If spawned.Length >= 128
		spawned.Remove(0)  ; Papyrus arrays stop at 128: forget the oldest (it stays in the world)
	EndIf
	spawned.Add(akRef)
	Debug.Trace(self + " SandboxRoom arena zone: tracking " + akRef + ", player inside = " + inside)
	Actor a = akRef as Actor
	If a
		a.EnableAI(inside && round == Fighting)
	EndIf
EndFunction

Function SetAI(bool abOn)
	int i = 0
	While spawned && i < spawned.Length
		Actor a = spawned[i] as Actor
		If a && !a.IsDead()
			a.EnableAI(abOn)
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
