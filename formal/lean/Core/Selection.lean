/-
  Formal Symbolic Systems Theory — Selection environments.

  Status: candidate formalization target / stage 1 / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Sections 3, 6.4.

  Purpose:
    Define selection as a predicate on symbolic states. The selection
    environment determines which symbolic variants persist. Key conjecture
    target: selection-fidelity tradeoff (6.4).

  Non-claims:
    1. No specific selection environment modeled.
    2. No claim that selection always reduces fidelity.
    3. No quantitative selection pressure.
-/

import Core.SymbolicSystem

namespace FSST

open FSST

def SelectionPreservesFidelity (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.fidelity r s → sys.selectionSurvives s →
    sys.fidelity r s

def SelectionCanLoseFidelity (sys : SymbolicSystem) : Prop :=
  ∃ r : sys.Referent, ∃ s₁ s₂ : sys.Symbol,
    sys.fidelity r s₁ ∧
    ¬ sys.selectionSurvives s₁ ∧
    sys.selectionSurvives s₂ ∧
    ¬ sys.fidelity r s₂

def SelectionFavorsFidelity (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.fidelity r s → sys.selectionSurvives s

end FSST
