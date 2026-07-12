/-
  Formal Symbolic Systems Theory — Reality coupling.

  Status: candidate formalization target / stage 1 extension / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Section 5.

  Purpose:
    Formalize the central functional account: symbolic systems exist to
    maximize reality coupling under constraint. Reality coupling is the
    degree to which symbolic states preserve action-relevant contact with
    referent structure.

    Every major symbolic-system property is an operation on coupling:
    grounding establishes it, fidelity preserves it, transmission propagates
    it, transformation risks it, scope bounds it, drift degrades it,
    correction restores it, selection reshapes it, engineering designs it.

    A symbolic system fails when it preserves symbolic form while losing
    reality coupling. All failure modes — null referents, semantic drift,
    metric-referent collapse, certainty laundering, scope erasure — are
    forms of reduced or false coupling.

  Non-claims:
    1. No claim that coupling is quantitatively measurable in all domains.
    2. No claim that coupling is the only thing symbolic systems do.
    3. No claim about any specific coupling threshold.
    4. No reduction of truth to coupling (truth is one mode of coupling).
-/

import Core.SymbolicSystem
import Core.ValidityLayers

namespace FSST

open FSST

universe u v

structure CouplingMeasure (sys : SymbolicSystem) where
  coupling : sys.Symbol → Int
  actionRelevant : sys.Referent → Prop
  costBound : Int

def RealityCoupled
    (sys : SymbolicSystem) (cm : CouplingMeasure sys) (s : sys.Symbol) : Prop :=
  ∃ r : sys.Referent,
    sys.scope r ∧ sys.fidelity r s ∧ cm.actionRelevant r ∧ cm.coupling s > 0

def CouplingLost
    (sys : SymbolicSystem) (cm : CouplingMeasure sys) (s : sys.Symbol) : Prop :=
  SyntacticallyValid sys s ∧ ¬ RealityCoupled sys cm s

inductive CouplingOperation where
  | grounding
  | fidelity
  | transmission
  | transformation
  | scope
  | drift
  | correction
  | selection
  | engineering
  deriving DecidableEq, Repr

inductive CouplingGap where
  | distance
  | time
  | absence
  | uncertainty
  | complexity
  | coordination
  | memoryLimit
  | energyConstraint
  | socialScale
  | futureConsequence
  | counterfactual
  deriving DecidableEq, Repr

structure CouplingObjective (sys : SymbolicSystem) where
  coupling : sys.Symbol → Int
  actionRelevance : sys.Symbol → Int
  transmissibility : sys.Symbol → Int
  maintainability : sys.Symbol → Int
  cost : sys.Symbol → Int
  driftRate : sys.Symbol → Int
  distortion : sys.Symbol → Int
  scopeError : sys.Symbol → Int
  correctionFailure : sys.Symbol → Int

def CouplingPositive
    (obj : CouplingObjective sys) (s : sys.Symbol) : Prop :=
  obj.coupling s > 0 ∧
  obj.actionRelevance s > 0 ∧
  obj.transmissibility s > 0 ∧
  obj.maintainability s > 0

def CouplingDegraded
    (obj : CouplingObjective sys) (s : sys.Symbol) : Prop :=
  obj.driftRate s > 0 ∨
  obj.distortion s > 0 ∨
  obj.scopeError s > 0 ∨
  obj.correctionFailure s > 0

theorem coupling_lost_implies_not_coupled
    (sys : SymbolicSystem) (cm : CouplingMeasure sys) (s : sys.Symbol)
    (hlost : CouplingLost sys cm s) :
    ¬ RealityCoupled sys cm s :=
  hlost.2

theorem null_referent_implies_coupling_lost
    (sys : SymbolicSystem)
    (cm : CouplingMeasure sys)
    (s : sys.Symbol)
    (hnull : ReferentiallyNull sys s) :
    CouplingLost sys cm s := by
  constructor
  · trivial
  · intro ⟨r, _, hfid, _, _⟩
    exact hnull r hfid

theorem transform_can_lose_coupling
    (sys : SymbolicSystem)
    (cm : CouplingMeasure sys)
    (s : sys.Symbol)
    (hcoupled : RealityCoupled sys cm s)
    (htrans_null : ReferentiallyNull sys (sys.transform s)) :
    CouplingLost sys cm (sys.transform s) := by
  constructor
  · trivial
  · intro ⟨r, _, hfid, _, _⟩
    exact htrans_null r hfid

theorem correction_can_restore_coupling
    (sys : SymbolicSystem)
    (cm : CouplingMeasure sys)
    (hcorr : ReferentCheckingCorrection sys)
    (r : sys.Referent)
    (s : sys.Symbol)
    (hscope : sys.scope r)
    (hviol : sys.violationDetected r s)
    (hrelevant : ∀ r' : sys.Referent,
      sys.scope r' →
      sys.fidelity r' (sys.correct s) →
      cm.actionRelevant r')
    (hpositive : cm.coupling (sys.correct s) > 0) :
    RealityCoupled sys cm (sys.correct s) := by
  obtain ⟨r', hscope', hfid'⟩ := hcorr r s hscope hviol
  exact ⟨r', hscope', hfid', hrelevant r' hscope' hfid', hpositive⟩

def CouplingPreservedUnderTransform
    (sys : SymbolicSystem) (cm : CouplingMeasure sys) : Prop :=
  ∀ s : sys.Symbol,
    RealityCoupled sys cm s →
    RealityCoupled sys cm (sys.transform s)

def CouplingPreservedUnderTransmit
    (sys : SymbolicSystem) (cm : CouplingMeasure sys) : Prop :=
  ∀ s : sys.Symbol,
    RealityCoupled sys cm s →
    RealityCoupled sys cm (sys.transmit s)

def CouplingSpansGap
    (sys : SymbolicSystem)
    (cm : CouplingMeasure sys)
    (gap : CouplingGap) : Prop :=
  ∃ s : sys.Symbol,
    RealityCoupled sys cm s ∧
    cm.coupling s > cm.costBound

end FSST
