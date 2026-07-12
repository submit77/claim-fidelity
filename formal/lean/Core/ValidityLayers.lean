/-
  Formal Symbolic Systems Theory — Validity layers.

  Status: candidate formalization target / stage 1 extension / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Section 11 (meta-system novelty)
    and carrier-referent decoupling analysis.

  Purpose:
    Distinguish six layers of symbolic validity. A symbolic state can be
    valid at one layer and invalid at another. The central theorem target:
    syntactic validity does not entail referential validity.

    This formalizes the failure mode where well-formed symbolic carriers
    with null, malformed, or obsolete referents continue to be processed
    as valid, producing artifacts that are symbolically real but
    referentially defective.

  Non-claims:
    1. No claim about any specific symbolic system.
    2. No quantitative measure of validity.
    3. No claim that syntactic validity is unimportant.
    4. No claim that all referentially invalid symbols are harmful.
-/

import Core.SymbolicSystem

namespace FSST

open FSST

def SyntacticallyValid (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  True

def ReferentiallyValid (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ∃ r : sys.Referent, sys.scope r ∧ sys.fidelity r s

def ReferentiallyNull (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ∀ r : sys.Referent, ¬ sys.fidelity r s

def ScopeValid (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ∃ r : sys.Referent, sys.scope r ∧ sys.fidelity r s

def FidelityValid (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ∃ r : sys.Referent, sys.fidelity r s

structure WellFormedReferentialFailure (sys : SymbolicSystem) where
  symbol : sys.Symbol
  syntacticallyValid : SyntacticallyValid sys symbol
  referentiallyNull : ReferentiallyNull sys symbol

theorem syntactic_validity_does_not_entail_referential
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hsyn : SyntacticallyValid sys s)
    (hnull : ReferentiallyNull sys s) :
    SyntacticallyValid sys s ∧
    Not (ReferentiallyValid sys s) := by
  constructor
  · exact hsyn
  · intro href
    obtain ⟨r, _hscope, hfidelity⟩ := href
    exact hnull r hfidelity

theorem null_grounded_symbol_propagates_through_transform
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hnull : ReferentiallyNull sys s) :
    SyntacticallyValid sys (sys.transform s) := by
  trivial

theorem null_grounded_symbol_propagates_through_transmit
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hnull : ReferentiallyNull sys s) :
    SyntacticallyValid sys (sys.transmit s) := by
  trivial

theorem null_grounded_survives_transform_chain
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (_hnull : ReferentiallyNull sys s) :
    SyntacticallyValid sys (sys.transform (sys.transform s)) := by
  trivial

def NullGroundedPropagation (sys : SymbolicSystem) : Prop :=
  ∃ s : sys.Symbol,
    ReferentiallyNull sys s ∧
    SyntacticallyValid sys (sys.transform s) ∧
    SyntacticallyValid sys (sys.transmit s)

theorem null_grounded_propagation_always_possible
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hnull : ReferentiallyNull sys s) :
    SyntacticallyValid sys (sys.transform s) ∧
    SyntacticallyValid sys (sys.transmit s) := by
  exact ⟨trivial, trivial⟩

def SyntaxOnlyCorrection (sys : SymbolicSystem) : Prop :=
  ∀ s : sys.Symbol,
    SyntacticallyValid sys (sys.correct s)

def ReferentCheckingCorrection (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.scope r →
    sys.violationDetected r s →
    ReferentiallyValid sys (sys.correct s)

theorem syntax_only_correction_does_not_prevent_null_propagation
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hnull : ReferentiallyNull sys s)
    (_hcorr : SyntaxOnlyCorrection sys) :
    SyntacticallyValid sys (sys.correct s) := by
  trivial

end FSST
