Scriptname SandboxRoom:SpecialTerminalScript extends Terminal
{Perks & Stats: the S.P.E.C.I.A.L. terminal. Its top menu sets all seven attributes at once (items 11-13: all to 1,
5 or 10); each attribute's submenu (Stat set) raises or lowers it by one (items 1, 2) or sets it (3-5: to 1, 5 or
10). This changes the base value, the one the game raises when an attribute is picked in the perk chart, so
bobblehead and apparel bonuses still come on top.}

ActorValue[] Property Specials Auto Const Mandatory
{Strength to Luck, in S.P.E.C.I.A.L. order.}
int Property Stat = -1 Auto Const
{An attribute's submenu: its index in Specials. -1: the top menu.}
string Property StatName Auto Const
{The attribute's name, for the notification.}

int Property MinValue = 1 AutoReadOnly
int Property MaxValue = 15 AutoReadOnly

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	Actor player = Game.GetPlayer()
	If Stat < 0
		int target = 0
		If auiMenuItemID == 11
			target = 1
		ElseIf auiMenuItemID == 12
			target = 5
		ElseIf auiMenuItemID == 13
			target = 10
		EndIf
		If target > 0
			int i = 0
			While i < Specials.Length
				player.SetValue(Specials[i], target)
				i += 1
			EndWhile
			Debug.Notification("S.P.E.C.I.A.L.: all set to " + target)
		EndIf
		Return
	EndIf
	ActorValue av = Specials[Stat]
	int value = player.GetBaseValue(av) as int
	If auiMenuItemID == 1
		value += 1
	ElseIf auiMenuItemID == 2
		value -= 1
	ElseIf auiMenuItemID == 3
		value = 1
	ElseIf auiMenuItemID == 4
		value = 5
	ElseIf auiMenuItemID == 5
		value = 10
	Else
		Return
	EndIf
	If value < MinValue
		value = MinValue
	ElseIf value > MaxValue
		value = MaxValue
	EndIf
	player.SetValue(av, value)
	Debug.Notification(StatName + ": " + value)
EndEvent
