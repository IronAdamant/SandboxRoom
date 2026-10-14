Scriptname SandboxRoom:PerkResetScript extends Terminal
{Perks & Stats: the Perks terminal's top menu. Item 901 removes every perk chart rank the player has; 902 does the
same and gives back one perk point per rank removed (a respec). Only the 70 chart perks are touched, not perks from
bobbleheads, magazines, companions or quests. The ranks are listed per S.P.E.C.I.A.L., male and female versions
included (Papyrus arrays hold at most 128 entries; each list here is well under that).}

Perk[] Property StrengthPerks Auto Const Mandatory
Perk[] Property PerceptionPerks Auto Const Mandatory
Perk[] Property EndurancePerks Auto Const Mandatory
Perk[] Property CharismaPerks Auto Const Mandatory
Perk[] Property IntelligencePerks Auto Const Mandatory
Perk[] Property AgilityPerks Auto Const Mandatory
Perk[] Property LuckPerks Auto Const Mandatory

int Property MenuRemoveAll = 901 AutoReadOnly
int Property MenuReset = 902 AutoReadOnly

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	If auiMenuItemID != MenuRemoveAll && auiMenuItemID != MenuReset
		Return
	EndIf
	Actor player = Game.GetPlayer()
	int removed = RemoveAll(player, StrengthPerks) + RemoveAll(player, PerceptionPerks)
	removed += RemoveAll(player, EndurancePerks) + RemoveAll(player, CharismaPerks)
	removed += RemoveAll(player, IntelligencePerks) + RemoveAll(player, AgilityPerks) + RemoveAll(player, LuckPerks)
	If auiMenuItemID == MenuReset && removed > 0
		Game.AddPerkPoints(removed)
		Debug.Notification("Perks reset: " + removed + " ranks removed, " + removed + " perk points back")
	Else
		Debug.Notification("Perks removed: " + removed + " ranks")
	EndIf
EndEvent

int Function RemoveAll(Actor akPlayer, Perk[] akList)
	int n = 0
	int i = 0
	While i < akList.Length
		If akPlayer.HasPerk(akList[i])
			akPlayer.RemovePerk(akList[i])
			n += 1
		EndIf
		i += 1
	EndWhile
	Return n
EndFunction
