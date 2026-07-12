/-
  Formal Symbolic Systems Theory — Binding relation.

  Status: candidate formalization target / stage 1 extension / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Section 5.5.

  Purpose:
    Formalize binding as the relation by which symbolic states attach to
    reality. Without binding, a symbolic system may have syntax but no
    reality coupling. Binding is the point at which symbolic structure
    becomes reality-coupled.

    Binding can be measured across dimensions (referential specificity,
    causal contact, predictive power, operational effect, fidelity, scope
    validity, correction sensitivity, thermodynamic value) and classified
    by state (unbound, weakly bound, misbound, stale-bound, strongly
    bound, self-correcting bound).

  Non-claims:
    1. No claim about specific binding thresholds.
    2. No claim that all binding is equally measurable.
    3. No claim that binding is binary.
    4. No reduction of meaning to binding.
-/

import Core.SymbolicSystem

namespace FSST

open FSST

universe u v

inductive BindingState where
  | unbound
  | weaklyBound
  | ambiguouslyBound
  | misbound
  | staleBound
  | scopeBound
  | stronglyBound
  | selfCorrecting
  deriving DecidableEq, Repr

inductive BindingDimension where
  | referentialSpecificity
  | causalContact
  | predictivePower
  | operationalEffect
  | fidelityPreservation
  | scopeValidity
  | correctionSensitivity
  | thermodynamicValue
  deriving DecidableEq, Repr

def Bound (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ∃ r : sys.Referent, sys.binding s r

def Unbound (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ¬ ∃ r : sys.Referent, sys.binding s r

def StronglyBound (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ∃ r : sys.Referent,
    sys.binding s r ∧
    sys.scope r ∧
    sys.fidelity r s

def Misbound (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ∃ r : sys.Referent,
    sys.binding s r ∧
    ¬ sys.fidelity r s

def SelfCorrectingBound (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ∃ r : sys.Referent,
    sys.binding s r ∧
    sys.fidelity r s ∧
    (sys.violationDetected r s → sys.fidelity r (sys.correct s))

structure BindingEvaluation (sys : SymbolicSystem) where
  symbol : sys.Symbol
  state : BindingState
  dimensions : List BindingDimension
  strength : Int

theorem unbound_implies_not_strongly_bound
    (sys : SymbolicSystem) (s : sys.Symbol)
    (hunb : Unbound sys s) :
    ¬ StronglyBound sys s := by
  intro ⟨r, hbind, _, _⟩
  exact hunb ⟨r, hbind⟩

theorem strongly_bound_implies_bound
    (sys : SymbolicSystem) (s : sys.Symbol)
    (hstrong : StronglyBound sys s) :
    Bound sys s := by
  obtain ⟨r, hbind, _, _⟩ := hstrong
  exact ⟨r, hbind⟩

theorem misbound_implies_bound
    (sys : SymbolicSystem) (s : sys.Symbol)
    (hmis : Misbound sys s) :
    Bound sys s := by
  obtain ⟨r, hbind, _⟩ := hmis
  exact ⟨r, hbind⟩

theorem misbound_implies_not_strongly_bound
    (sys : SymbolicSystem) (s : sys.Symbol)
    (hmis : Misbound sys s)
    (huniq : ∀ r : sys.Referent, sys.binding s r → ¬ sys.fidelity r s) :
    ¬ StronglyBound sys s := by
  intro ⟨r, hbind, _, hfid⟩
  exact huniq r hbind hfid

inductive SelectionRoute where
  | adaptive
  | neutral
  | parasitic
  deriving DecidableEq, Repr

inductive SymbolicSystemClass where
  | adaptive
  | maladaptive
  | parasitic
  | vestigial
  | misbound
  | overfit
  deriving DecidableEq, Repr

end FSST
