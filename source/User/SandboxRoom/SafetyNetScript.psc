Scriptname SandboxRoom:SafetyNetScript extends Quest
{Keeps the player from dying, in one place. Two things ask for it: the arena, while the player is inside it
(ArenaZoneScript), and the holotape's safety net, anywhere while it is on. While either does, the player is
essential: going down puts them in bleedout instead of killing them, and this script decides what happens then.
In the arena the round resets (ArenaZoneScript.Knockout). Anywhere else, with the safety net on, the player is
healed and, once back on their feet (the game will not move a downed player), brought to the Sandbox Room; from
outside the room Teleport Out then takes them back to where they fell. A player made essential by something else
is never made mortal here.}

GlobalVariable Property SBR_SafetyNet Auto Const Mandatory
{1 while the safety net is on (the holotape menu offers "turn on" or "turn off" from it).}
SandboxRoom:ArenaZoneScript Property Zone Auto Const Mandatory
Cell Property SandboxRoom Auto Const Mandatory
ObjectReference Property SBR_EntryMarker Auto Const Mandatory
{Where a player caught by the safety net is brought: the room's arrival point.}
ObjectReference Property SBR_ReturnMarker Auto Const Mandatory
GlobalVariable Property SBR_ReturnSaved Auto Const Mandatory
ActorValue Property Health Auto Const Mandatory
ActorValue Property Rads Auto Const Mandatory

float Property RestoreAll = 100000.0 AutoReadOnly  ; more than any health or radiation
float Property RescuePoll = 0.25 AutoReadOnly       ; how often to check whether the downed player is up again
int Property RescueMaxPolls = 60 AutoReadOnly       ; move them anyway after this many checks (15 seconds)
float Property SettleDelay = 2.0 AutoReadOnly       ; up, then this long before the move: moved mid get-up, the
                                                    ; player arrived with the knockout's screen haze stuck on
int Property RescueTimer = 0 AutoReadOnly
int Property SettleTimer = 1 AutoReadOnly

bool arena          ; the player is in the arena
bool madeEssential  ; the player is essential because of this script
bool listening      ; registered for the player going down
bool rescuing       ; the safety net caught the player: waiting for them to get up
int rescuePolls

Function SetArena(bool abInside)
	arena = abInside
	Update()
EndFunction

Function SetSafetyNet(bool abOn)
	If abOn
		SBR_SafetyNet.SetValue(1)
		Debug.Notification("Safety net on: you cannot die. Going down brings you to the Sandbox Room, healed.")
	Else
		SBR_SafetyNet.SetValue(0)
		Debug.Notification("Safety net off")
	EndIf
	Update()
EndFunction

bool Function SafetyNetOn()
	Return SBR_SafetyNet.GetValue() == 1
EndFunction

Function Update()
	Actor player = Game.GetPlayer()
	bool want = arena || SafetyNetOn() || rescuing
	If want && !madeEssential && !player.IsEssential()
		madeEssential = true
		player.SetEssential(true)
	ElseIf !want && madeEssential
		madeEssential = false
		player.SetEssential(false)
	EndIf
	If want && !listening
		listening = true
		RegisterForRemoteEvent(player, "OnEnterBleedout")
	ElseIf !want && listening
		listening = false
		UnregisterForRemoteEvent(player, "OnEnterBleedout")
	EndIf
	Debug.Trace(self + " SandboxRoom safety: arena " + arena + ", net " + SafetyNetOn() + ", essential " + player.IsEssential())
EndFunction

Event Actor.OnEnterBleedout(Actor akSender)
	Debug.Trace(self + " SandboxRoom safety: player went down, arena " + arena + ", net " + SafetyNetOn())
	If arena
		Zone.Knockout()
	ElseIf SafetyNetOn() && !rescuing
		rescuing = true
		akSender.ResetHealthAndLimbs()
		akSender.RestoreValue(Health, RestoreAll)
		rescuePolls = 0
		StartTimer(RescuePoll, RescueTimer)
	EndIf
EndEvent

Event OnTimer(int aiTimerID)
	Actor player = Game.GetPlayer()
	If aiTimerID == RescueTimer
		If player.IsBleedingOut() && rescuePolls < RescueMaxPolls
			rescuePolls += 1
			StartTimer(RescuePoll, RescueTimer)
		Else
			StartTimer(SettleDelay, SettleTimer)
		EndIf
		Return
	EndIf
	If player.IsBleedingOut() && rescuePolls < RescueMaxPolls  ; down again while settling
		StartTimer(RescuePoll, RescueTimer)
		Return
	EndIf
	If player.GetParentCell() != SandboxRoom
		SBR_ReturnMarker.MoveTo(player)  ; Teleport Out goes back to where they fell
		SBR_ReturnSaved.SetValue(1)
	EndIf
	player.MoveTo(SBR_EntryMarker)
	SandboxRoom:HolotapeScript.BringFollowers()
	player.ResetHealthAndLimbs()
	player.RestoreValue(Health, RestoreAll)
	player.RestoreValue(Rads, RestoreAll)
	rescuing = false
	Update()
	Debug.Notification("Safety net: knocked out, healed and brought to the Sandbox Room")
	Debug.Trace(self + " SandboxRoom safety: rescued after " + rescuePolls + " checks, in the room " + (player.GetParentCell() == SandboxRoom))
EndEvent
