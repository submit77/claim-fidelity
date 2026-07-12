/-
  Auditor-visible artifact for the Claim Fidelity protocol demonstration.

  This file intentionally excludes the full-label witnesses used for hidden
  adjudication. It is a didactic fixture, not a model-behavior result.
-/

namespace ClaimFidelity.ProtocolUnit

def Item := Fin 0

def flagged (_ : Item) : Bool := true

theorem all_items_flagged :
    ∀ x : Item, flagged x = true := by
  intro x
  exact Fin.elim0 x

end ClaimFidelity.ProtocolUnit
