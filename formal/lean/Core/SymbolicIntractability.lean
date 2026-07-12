/-
  Formal Symbolic Systems Theory — Symbolically induced intractability.

  Status: candidate formalization target / stage 1 extension / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md.

  Purpose:
    Formalize the distinction between referent conditions, symbolic
    artifacts, and coupled failures. A domain may appear unsolvable
    because the symbolic system used to define it generates the
    instability being interpreted as a feature of the referent.

    Key theorem target: intensifying operations within a failing
    symbolic system preserves or amplifies the anomaly unless the
    symbolic structure itself is repaired.

  Non-claims:
    1. No claim that all hard problems are symbolic artifacts.
    2. No claim that symbolic repair is always sufficient.
    3. No claim about any specific domain.
    4. No claim that referent conditions are easy.
-/

import Core.SymbolicSystem
import Core.ValidityLayers

namespace FSST

open FSST

inductive AnomalySource where
  | referentCondition
  | symbolicArtifact
  | coupledFailure
  deriving DecidableEq, Repr

structure DomainAnomaly (sys : SymbolicSystem) where
  symbol : sys.Symbol
  source : AnomalySource
  persistent : Prop

def IsSymbolicArtifact (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ReferentiallyNull sys s ∧ SyntacticallyValid sys s

def IsReferentCondition (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ReferentiallyValid sys s ∧
  ∃ r : sys.Referent, sys.fidelity r s ∧ sys.violationDetected r s

def IsCoupledFailure (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ∃ r : sys.Referent,
    sys.scope r ∧
    sys.fidelity r s ∧
    ¬ sys.fidelity r (sys.transform s)

def SymbolicallyInducedIntractability (sys : SymbolicSystem) : Prop :=
  ∃ s : sys.Symbol,
    IsSymbolicArtifact sys s ∧
    SyntacticallyValid sys (sys.transform s) ∧
    IsSymbolicArtifact sys (sys.transform s)

theorem symbolic_artifact_survives_transform
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hart : IsSymbolicArtifact sys s)
    (htrans_null : ReferentiallyNull sys (sys.transform s)) :
    IsSymbolicArtifact sys (sys.transform s) :=
  ⟨htrans_null, trivial⟩

theorem intensifying_operations_preserves_artifact
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hart : IsSymbolicArtifact sys s)
    (htrans_null : ReferentiallyNull sys (sys.transform s))
    (htrans2_null : ReferentiallyNull sys (sys.transform (sys.transform s))) :
    IsSymbolicArtifact sys (sys.transform s) ∧
    IsSymbolicArtifact sys (sys.transform (sys.transform s)) :=
  ⟨⟨htrans_null, trivial⟩, ⟨htrans2_null, trivial⟩⟩

theorem artifact_not_referent_condition
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hart : IsSymbolicArtifact sys s) :
    ¬ IsReferentCondition sys s := by
  intro ⟨href, r, hfid, _⟩
  obtain ⟨hnull, _⟩ := hart
  exact hnull r hfid

def DiagnosticPriority : AnomalySource → Nat
  | .symbolicArtifact => 0
  | .coupledFailure => 1
  | .referentCondition => 2

theorem check_symbolic_before_referent :
    DiagnosticPriority AnomalySource.symbolicArtifact <
    DiagnosticPriority AnomalySource.referentCondition := by
  decide

end FSST
