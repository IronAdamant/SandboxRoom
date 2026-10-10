Scriptname SandboxRoom:TargetBayScript extends ObjectReference
{A target bay, on its controller marker. Keeps TargetCount targets standing around the marker: AI switched off,
health set from the bay's terminal, and each one replaced RespawnDelay seconds after it dies.}

Form[] Property TargetTypes Auto Const Mandatory
{Leveled actor lists the terminal chooses between (menu "Target" items, in order).}
int Property TargetCount = 1 Auto Const
float Property Spacing = 150.0 Auto Const
{Distance between targets when there is more than one.}
float Property RespawnDelay = 3.0 Auto Const
ActorValue Property Health Auto Const Mandatory

int typeIndex = 0
float healthValue = 0.0  ; 0 = whatever the game gives that enemy
bool active = false
Actor[] targets

Event OnCellAttach()
	; Fill the bay with its default targets the first time the room loads (and after "Clear the bay").
	If !active
		Refill()
	EndIf
EndEvent

Function SetType(int aiIndex)
	If aiIndex >= 0 && aiIndex < TargetTypes.Length
		typeIndex = aiIndex
		Refill()
	EndIf
EndFunction

Function SetHealth(float afHealth)
	healthValue = afHealth
	Refill()
EndFunction

Function Clear()
	active = false
	int i = 0
	While targets && i < targets.Length
		RemoveTarget(i)
		i += 1
	EndWhile
	targets = new Actor[0]
EndFunction

Function Refill()
	Clear()
	active = true
	targets = new Actor[TargetCount]
	int i = 0
	While i < TargetCount
		targets[i] = SpawnTarget(i)
		i += 1
	EndWhile
EndFunction

Actor Function SpawnTarget(int aiSlot)
	Actor target = PlaceAtMe(TargetTypes[typeIndex], 1, abForcePersist = true, abInitiallyDisabled = true) as Actor
	; slot 0 in the middle, the others on a cross around it
	float dx = 0.0
	float dy = 0.0
	If aiSlot == 1
		dy = Spacing
	ElseIf aiSlot == 2
		dy = -Spacing
	ElseIf aiSlot == 3
		dx = Spacing
	ElseIf aiSlot == 4
		dx = -Spacing
	ElseIf aiSlot > 4
		dx = Spacing * (aiSlot - 4)
		dy = Spacing
	EndIf
	target.MoveTo(self, dx, dy, 0.0)
	If healthValue > 0
		target.SetValue(Health, healthValue)
	EndIf
	target.Enable()
	target.EnableAI(false)
	RegisterForRemoteEvent(target, "OnDeath")
	Return target
EndFunction

Function RemoveTarget(int aiSlot)
	Actor target = targets[aiSlot]
	If target
		UnregisterForRemoteEvent(target, "OnDeath")
		target.Disable()
		target.Delete()
	EndIf
	targets[aiSlot] = None
EndFunction

Event Actor.OnDeath(Actor akSender, Actor akKiller)
	int slot = targets.Find(akSender)
	If slot >= 0
		StartTimer(RespawnDelay, slot)
	EndIf
EndEvent

Event OnTimer(int aiTimerID)
	If active && aiTimerID < targets.Length
		RemoveTarget(aiTimerID)
		targets[aiTimerID] = SpawnTarget(aiTimerID)
	EndIf
EndEvent
