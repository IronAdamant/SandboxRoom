Scriptname SandboxRoom:SpawnTrackerScript extends Quest
{Remembers what the spawn terminals created, so they can be removed or killed together.}

ObjectReference[] spawned

Function Track(ObjectReference akRef)
	If spawned == None
		spawned = new ObjectReference[0]
	EndIf
	If spawned.Length >= 128
		; Papyrus arrays stop at 128: forget the oldest entry (it stays in the world).
		spawned.Remove(0)
	EndIf
	spawned.Add(akRef)
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
			a.Kill()
		EndIf
		i += 1
	EndWhile
EndFunction
