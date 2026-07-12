/- Hidden adjudication material for the protocol demonstration. -/

import FrozenArtifact

namespace ClaimFidelity.ProtocolUnit

theorem no_flagged_item_exists :
    ¬ ∃ x : Item, flagged x = true := by
  intro h
  obtain ⟨x, _⟩ := h
  exact Fin.elim0 x

theorem item_is_not_nonempty :
    ¬ Nonempty Item := by
  intro h
  cases h with
  | intro x => exact Fin.elim0 x

theorem no_unflagged_item_exists :
    ¬ ∃ x : Item, flagged x = false := by
  intro h
  obtain ⟨x, _⟩ := h
  exact Fin.elim0 x

end ClaimFidelity.ProtocolUnit
