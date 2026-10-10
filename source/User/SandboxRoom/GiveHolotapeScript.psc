Scriptname SandboxRoom:GiveHolotapeScript extends Quest
{Gives the player the Sandbox Room holotape once they have left Vault 111 (MQ102 stage 10, the same check the
Creation Club content uses), or straight away on a save that is already past that point.}

Holotape Property SBR_Holotape Auto Const Mandatory
Quest Property MQ102 Auto Const Mandatory
int Property LeftVaultStage = 10 Auto Const

int GiveTimer = 1

Event OnInit()
	If MQ102.GetStageDone(LeftVaultStage)
		; Mid-game install: wait a moment so the item is not added during the save's load.
		StartTimer(5, GiveTimer)
	Else
		RegisterForRemoteEvent(MQ102, "OnStageSet")
	EndIf
EndEvent

Event Quest.OnStageSet(Quest akSender, int auiStageID, int auiItemID)
	If auiStageID == LeftVaultStage
		UnregisterForRemoteEvent(MQ102, "OnStageSet")
		StartTimer(5, GiveTimer)
	EndIf
EndEvent

Event OnTimer(int aiTimerID)
	If aiTimerID == GiveTimer
		Actor player = Game.GetPlayer()
		If player.GetItemCount(SBR_Holotape) == 0
			player.AddItem(SBR_Holotape)
		EndIf
	EndIf
EndEvent
