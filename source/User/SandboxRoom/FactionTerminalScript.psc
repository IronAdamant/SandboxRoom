Scriptname SandboxRoom:FactionTerminalScript extends Terminal
{Perks & Stats: one faction's (or group's) submenu on the Factions and Hostile Groups terminals. Item 1 makes it
friendly to the player, 2 neutral, 3 hostile, the way the game's own quests do it (SetAlly / SetEnemy with the
player faction, and the player-enemy flag). Story quests can change these again, and some places give their people
an extra faction of their own, which keeps its own attitude.}

Faction[] Property Factions Auto Const Mandatory
{The faction, or every faction of a group (e.g. the three trapper factions).}
Faction Property PlayerFaction Auto Const Mandatory
string Property GroupName Auto Const
{The name shown in the notification.}

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	If auiMenuItemID < 1 || auiMenuItemID > 3
		Return
	EndIf
	int i = 0
	While i < Factions.Length
		Faction f = Factions[i]
		If auiMenuItemID == 1
			f.SetPlayerEnemy(false)
			f.SetAlly(PlayerFaction, true, true)  ; friends both ways (allies would also join your fights)
		ElseIf auiMenuItemID == 2
			f.SetPlayerEnemy(false)
			f.SetEnemy(PlayerFaction, true, true)  ; neutral both ways
		Else
			f.SetEnemy(PlayerFaction)
			f.SetPlayerEnemy(true)
		EndIf
		i += 1
	EndWhile
	string[] states = new string[3]
	states[0] = "friendly"
	states[1] = "neutral"
	states[2] = "hostile"
	Debug.Notification(GroupName + ": " + states[auiMenuItemID - 1])
EndEvent
