Scriptname SandboxRoom:InfiniteChestScript extends ObjectReference
{A chest that never runs out: whatever is taken is put straight back. Items the player puts in stay there.}

Event OnInit()
	AddInventoryEventFilter(None)
EndEvent

Event OnLoad()
	; Inventory event filters are not kept in the save, so set it again whenever the room loads.
	AddInventoryEventFilter(None)
EndEvent

Event OnItemRemoved(Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akDestContainer)
	AddItem(akBaseItem, aiItemCount, true)
EndEvent
