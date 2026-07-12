/-
  Formal Symbolic Systems Theory — Drift dynamics.

  Status: candidate formalization target / stage 1 / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Sections 3, 6.1, 6.7.

  Purpose:
    Define drift as the change in fidelity over time steps. The drift
    function maps a symbol and a time step count to the symbol's state
    after that many steps of transmission/selection/use.

    Key conjecture targets:
      - drift theorem (6.1): without correction, fidelity degrades
      - referent-independent drift (6.7): drift rate depends on system
        properties, not content truth

  Non-claims:
    1. No quantitative drift rate. Time is discrete (Nat), fidelity is
       relational (Prop). Quantification is a later stage.
    2. No specific drift model for any real system.
-/

import Core.SymbolicSystem

namespace FSST

open FSST

def DriftLosesFidelity (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.fidelity r s →
    ∃ n : Nat, ¬ sys.fidelity r (sys.drift s n)

def DriftEventuallyDetected (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.fidelity r s →
    ∀ n : Nat, ¬ sys.fidelity r (sys.drift s n) →
    sys.violationDetected r (sys.drift s n)

def NoDriftWithinHorizon (sys : SymbolicSystem) (horizon : Nat) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.fidelity r s →
    ∀ n : Nat, n ≤ horizon → sys.fidelity r (sys.drift s n)

end FSST
