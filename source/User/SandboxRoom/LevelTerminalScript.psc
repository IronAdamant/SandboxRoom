Scriptname SandboxRoom:LevelTerminalScript extends Terminal
{Perks & Stats: the Level terminal. Item N raises the player's level by N, by awarding exactly the XP those levels
need (each level then brings its usual perk point and level-up message). Going from level L to L + 1 takes
fXPLevelUpBase + fXPLevelUpMult * (L - 1) XP: 200, then 275, 350 and so on. The XP is direct, so Intelligence and
XP perks do not add to it. Levels cannot be lowered without F4SE.}

Event OnMenuItemRun(int auiMenuItemID, ObjectReference akTerminalRef)
	If auiMenuItemID < 1 || auiMenuItemID > 100
		Return
	EndIf
	float base = Game.GetGameSettingFloat("fXPLevelUpBase")
	float mult = Game.GetGameSettingFloat("fXPLevelUpMult")
	If base <= 0.0
		base = 200.0
	EndIf
	If mult <= 0.0
		mult = 75.0
	EndIf
	int level = Game.GetPlayer().GetLevel()
	float xp = 0.0
	int i = 0
	While i < auiMenuItemID
		xp += base + mult * (level + i - 1)
		i += 1
	EndWhile
	Game.RewardPlayerXP(xp as int, true)
	Debug.Notification("Level: " + level + " -> " + (level + auiMenuItemID))
EndEvent
