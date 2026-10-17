Scriptname SandboxRoom:FactionStatusScript extends ObjectReference
{Perks & Stats: the Factions and Hostile Groups terminals. Reads each group's relation to the player from the game
into its state global (1 friendly, 2 neutral, 3 hostile), which the terminal's menus show, whenever the terminal
loads or is used: story quests and other mods can change relations while the player is away.}

Faction[] Property Factions Auto Const Mandatory
{One faction per group, in the order of States.}
GlobalVariable[] Property States Auto Const Mandatory

Event OnLoad()
	Refresh()
EndEvent

Event OnActivate(ObjectReference akActionRef)
	Refresh()
EndEvent

Function Refresh()
	Actor player = Game.GetPlayer()
	int i = 0
	While i < Factions.Length
		States[i].SetValue(StateOf(Factions[i], player))
		i += 1
	EndWhile
EndFunction

int Function StateOf(Faction akFaction, Actor akPlayer) global
	If akFaction.IsPlayerEnemy()
		Return 3
	EndIf
	int reaction = akFaction.GetFactionReaction(akPlayer)  ; 0 neutral, 1 enemy, 2 ally, 3 friend
	If reaction == 1
		Return 3
	ElseIf reaction == 0
		Return 2
	EndIf
	Return 1
EndFunction
