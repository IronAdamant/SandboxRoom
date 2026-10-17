Scriptname SandboxRoom:InfiniteChestScript extends ObjectReference
{A chest that never runs out: whatever is taken is put straight back. Items the player puts in stay there, except
Purge items in a cabinet that has them.}

FormList Property Purge Auto Const
{Weapon cabinets: all ammo. The game puts a few rounds in with every weapon in a container; they are cleared out
whenever the cabinet loads and after every refill, and never put back (the Ammo cabinet has it all).}

int Property PurgeCount = 100000 AutoReadOnly  ; more than any stack: removes them all

Event OnInit()
	AddInventoryEventFilter(None)
EndEvent

Event OnLoad()
	; Inventory event filters are not kept in the save, so set it again whenever the room loads.
	AddInventoryEventFilter(None)
	ClearPurge()
EndEvent

Event OnItemRemoved(Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akDestContainer)
	If Purge && Purge.HasForm(akBaseItem)
		Return  ; cleared out, or taken: not put back
	EndIf
	AddItem(akBaseItem, aiItemCount, true)
	ClearPurge()  ; the game may hand out rounds with the weapon put back
EndEvent

Function ClearPurge()
	If !Purge || GetItemCount(Purge) == 0
		Return
	EndIf
	RemoveItem(Purge, PurgeCount, true)
	If GetItemCount(Purge) > 0  ; the list as a whole did not work: one form at a time
		Debug.Trace(self + " InfiniteChestScript: clearing the purge list one form at a time")
		int i = Purge.GetSize() - 1
		While i >= 0
			Form f = Purge.GetAt(i)
			If GetItemCount(f) > 0
				RemoveItem(f, PurgeCount, true)
			EndIf
			i -= 1
		EndWhile
	EndIf
	Debug.Trace(self + " InfiniteChestScript: purged, " + GetItemCount(Purge) + " left")
EndFunction
