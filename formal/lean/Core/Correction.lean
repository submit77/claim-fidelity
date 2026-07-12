/-
  Formal Symbolic Systems Theory — Correction regimes.

  Status: candidate formalization target / stage 1 / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Sections 3, 6.5.

  Purpose:
    Define correction as a function that restores fidelity.
    Key conjecture target: correction regime sufficiency (6.5) —
    a system maintains fidelity iff correction dominates drift.

  Non-claims:
    1. No specific correction mechanism modeled.
    2. No quantitative correction strength.
    3. No claim that correction is always possible.
-/

import Core.SymbolicSystem

namespace FSST

open FSST

def CorrectionDominatesDrift (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol, ∀ n : Nat,
    sys.scope r →
    sys.fidelity r s →
    sys.fidelity r (sys.correct (sys.drift s n))

def CorrectionRestoresFromViolation (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.scope r →
    sys.violationDetected r s →
    sys.fidelity r (sys.correct s)

def MaintainedSystem (sys : SymbolicSystem) : Prop :=
  CorrectionDominatesDrift sys ∧
  CorrectionRestoresFromViolation sys

end FSST
