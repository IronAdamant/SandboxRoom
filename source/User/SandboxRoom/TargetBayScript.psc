Scriptname SandboxRoom:TargetBayScript extends ObjectReference
{A target bay, on its controller marker. Keeps TargetCount targets standing around the marker: held in place,
shown as holograms, health set from the bay's terminal, and each one replaced RespawnDelay seconds after it dies.}

Form[] Property TargetTypes Auto Const Mandatory
{Actors or leveled actor lists the terminal chooses between (menu "Target" items, in order).}
int Property TargetCount = 1 Auto Const
float Property Spacing = 150.0 Auto Const
{Distance between targets when there is more than one.}
float Property RespawnDelay = 3.0 Auto Const
float Property RespawnShift = 90.0 Auto Const
{A target that died comes back up to this far from its spot, so the new one is not standing in the old place.}
ActorValue Property Health Auto Const Mandatory
ActorValue Property Aggression Auto Const Mandatory
ActorValue Property Confidence Auto Const Mandatory
ActorValue Property DamageResist Auto Const Mandatory
ActorValue Property EnergyResist Auto Const Mandatory
EffectShader Property Hologram Auto Const
{Played on every target for as long as it stands.}

int Property RefillTimer = 1000 AutoReadOnly  ; timer IDs below it are target slots
int typeIndex = 0
float healthValue = 0.0  ; 0 = whatever the game gives that enemy
bool noArmor = false     ; true: no damage or energy resistance, so health is exactly the damage it takes
bool active = false
Actor[] targets

Event OnCellAttach()
	; Fill the bay with its default targets the first time the room loads (and after "Clear the bay").
	If !active
		Refill()
	EndIf
EndEvent

; The terminal's choices: the old targets go at once, the new ones come once the terminal is closed (spawning
; from inside the terminal menu left the bay empty).
Function SetType(int aiIndex)
	If aiIndex >= 0 && aiIndex < TargetTypes.Length
		typeIndex = aiIndex
		Clear()
		StartTimer(0.1, RefillTimer)
	EndIf
EndFunction

Function SetHealth(float afHealth)
	healthValue = afHealth
	If afHealth > 0
		Debug.Notification("Target health: " + afHealth as int)
	Else
		Debug.Notification("Target health: game default")
	EndIf
	Debug.Trace(self + " SandboxRoom bay: health " + afHealth)
	Clear()
	StartTimer(0.1, RefillTimer)
EndFunction

Function SetArmor(bool abNone)
	noArmor = abNone
	If abNone
		Debug.Notification("Target armor: none")
	Else
		Debug.Notification("Target armor: game default")
	EndIf
	Clear()
	StartTimer(0.1, RefillTimer)
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

Actor Function SpawnTarget(int aiSlot, bool abRespawn = false)
	Actor target = PlaceAtMe(TargetTypes[typeIndex], 1, abForcePersist = true, abInitiallyDisabled = true) as Actor
	Debug.Trace(self + " SandboxRoom bay: slot " + aiSlot + " type " + typeIndex + " placed " + target)
	If !target
		Return None
	EndIf
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
	If abRespawn
		dx += Utility.RandomFloat(-RespawnShift, RespawnShift)
		dy += Utility.RandomFloat(-RespawnShift, RespawnShift)
	EndIf
	target.MoveTo(self, dx, dy, 0.0)
	; Held in place with their AI on, not frozen: an actor with its AI off never finishes fading in (see-through
	; targets) and never processes its own death (no OnDeath, so no respawn). They do not fight back.
	target.SetValue(Aggression, 0.0)
	target.SetValue(Confidence, 0.0)
	target.Enable()
	target.SetRestrained(true)
	target.StopCombat()
	target.BlockActivation(true, true)  ; no "Talk" prompt
	RegisterForRemoteEvent(target, "OnDeath")
	; The game levels an actor and sets its health when its 3D loads, and an effect shader only takes on loaded
	; 3D (the head loads last): wait for it, up to two seconds, then set health and show the hologram.
	int tries = 0
	While !target.Is3DLoaded() && tries < 40
		Utility.Wait(0.05)
		tries += 1
	EndWhile
	Utility.Wait(0.3)
	If noArmor
		target.SetValue(DamageResist, 0.0)
		target.SetValue(EnergyResist, 0.0)
	EndIf
	If healthValue > 0
		target.SetValue(Health, healthValue)
		target.RestoreValue(Health, 1000000.0)
	EndIf
	If Hologram
		Hologram.Play(target, -1.0)
	EndIf
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
	If aiTimerID == RefillTimer
		Refill()
	ElseIf active && aiTimerID < targets.Length
		RemoveTarget(aiTimerID)
		targets[aiTimerID] = SpawnTarget(aiTimerID, true)
	EndIf
EndEvent
