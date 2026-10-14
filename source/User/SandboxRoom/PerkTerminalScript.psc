Scriptname SandboxRoom:PerkTerminalScript extends Terminal
{Perks & Stats: one perk's submenu. Item 1 adds a rank, 2 removes one, 3 adds every rank, 4 removes every rank.
Each rank is its own perk (Iron Fist 1 to 5), and a player with rank 3 has ranks 1 to 3. Level and S.P.E.C.I.A.L.
requirements are ignored, as with the console. Removing ranks does not give perk points back (the Perks
terminal's Reset does).}

Perk[] Property Ranks Auto Const Mandatory
{The perk's ranks in order. For a perk with male and female versions (Lady Killer / Black Widow): the male one.}
Perk[] Property FemaleRanks Auto Const
{The female version's ranks, if the perk has one.}
string Property PerkName Auto Const
{The name shown in the notification.}

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	Actor player = Game.GetPlayer()
	Perk[] list = Ranks
	If FemaleRanks && FemaleRanks.Length > 0 && player.GetLeveledActorBase().GetSex() == 1
		list = FemaleRanks
	EndIf
	If auiMenuItemID == 1
		; the lowest rank missing, so a gap (from the console) is filled first
		int i = 0
		While i < list.Length && player.HasPerk(list[i])
			i += 1
		EndWhile
		If i < list.Length
			player.AddPerk(list[i])
		EndIf
	ElseIf auiMenuItemID == 2
		int i = list.Length - 1
		While i >= 0 && !player.HasPerk(list[i])
			i -= 1
		EndWhile
		If i >= 0
			player.RemovePerk(list[i])
		EndIf
	ElseIf auiMenuItemID == 3 || auiMenuItemID == 4
		int i = 0
		While i < list.Length
			If auiMenuItemID == 3 && !player.HasPerk(list[i])
				player.AddPerk(list[i])
			ElseIf auiMenuItemID == 4 && player.HasPerk(list[i])
				player.RemovePerk(list[i])
			EndIf
			i += 1
		EndWhile
	Else
		Return
	EndIf
	Debug.Notification(PerkName + ": rank " + CountRanks(player, list) + " of " + list.Length)
EndEvent

int Function CountRanks(Actor akPlayer, Perk[] akList)
	int n = 0
	int i = 0
	While i < akList.Length
		If akPlayer.HasPerk(akList[i])
			n += 1
		EndIf
		i += 1
	EndWhile
	Return n
EndFunction
