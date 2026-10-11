Scriptname SandboxRoom:GiveHolotapeScript extends Quest
{Gives the player the Sandbox Room holotape as soon as they have a Pip-Boy: in Vault 111 right after picking it
up, at once with an alternative-start mod that hands one out, or straight away on a save that already has one.
Checks every CheckInterval seconds until then, and never gives a second holotape.}

Holotape Property SBR_Holotape Auto Const Mandatory
Form[] Property PipBoys Auto Const Mandatory
{The Pip-Boy items (the vanilla one and its variants): having any of them counts.}
float Property CheckInterval = 3.0 Auto Const
float Property GiveDelay = 2.0 Auto Const
{A short wait after the Pip-Boy turns up, so the holotape is not added during a load or a scene start.}

int CheckTimer = 1
int GiveTimer = 2

Event OnInit()
	StartTimer(CheckInterval, CheckTimer)
EndEvent

Event OnTimer(int aiTimerID)
	Actor player = Game.GetPlayer()
	If player.GetItemCount(SBR_Holotape) > 0
		Return  ; already given (or the player kept it): nothing more to do
	EndIf
	If aiTimerID == CheckTimer
		If HasPipBoy(player)
			StartTimer(GiveDelay, GiveTimer)
		Else
			StartTimer(CheckInterval, CheckTimer)
		EndIf
	ElseIf aiTimerID == GiveTimer
		player.AddItem(SBR_Holotape)
	EndIf
EndEvent

bool Function HasPipBoy(Actor akPlayer)
	int i = 0
	While i < PipBoys.Length
		If akPlayer.GetItemCount(PipBoys[i]) > 0
			Return True
		EndIf
		i += 1
	EndWhile
	Return False
EndFunction
