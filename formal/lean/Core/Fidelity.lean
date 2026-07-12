/-
  Formal Symbolic Systems Theory — Fidelity relations.

  Status: candidate formalization target / stage 1 / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Sections 3, 5, 6.8.

  Purpose:
    Define fidelity preservation and loss under transformation.
    The central claim: transformation alone cannot increase fidelity
    without new grounding or correction.

  Non-claims:
    1. No quantitative fidelity measure yet. Fidelity is a relation (Prop),
       not a metric (Real). Quantification is a later stage.
    2. No claim that all transformations lose fidelity.
    3. No claim about specific transformation rules.
-/

import Core.SymbolicSystem

namespace FSST

open FSST

def TransformPreservesFidelity (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.fidelity r s → sys.fidelity r (sys.transform s)

def TransformLosesFidelity (sys : SymbolicSystem) : Prop :=
  ∃ r : sys.Referent, ∃ s : sys.Symbol,
    sys.fidelity r s ∧ ¬ sys.fidelity r (sys.transform s)

def TransmitPreservesFidelity (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.fidelity r s → sys.fidelity r (sys.transmit s)

def CorrectionRestoresFidelity (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.scope r → sys.violationDetected r s →
    sys.fidelity r (sys.correct s)

end FSST
