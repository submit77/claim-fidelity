/-
  Formal Symbolic Systems Theory — Symbolic stacking and pathology.

  Status: candidate formalization target / stage 2 extension / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Section 7.

  Purpose:
    Formalize the relationship between symbolic stack depth, margin,
    leverage, and pathology capacity. Symbolic systems build in layers.
    Each layer increases affordance and distance from direct referent
    contact. The margin produced by symbolic leverage permits further
    stacking, but stack depth increases the space in which misalignment
    can persist because feedback is delayed, distributed, or symbolically
    mediated.

    Key law-like claims:
    - Symbolic stack depth increases both leverage and pathology capacity.
    - Surplus can subsidize false symbols.
    - The margin-pathology cycle: margin → drift tolerance →
      accumulated misalignment → margin depletion.

  Non-claims:
    1. No claim about specific stack depth thresholds.
    2. No claim that all stacking is pathological.
    3. No claim about specific civilizations or institutions.
    4. No claim that pathology is inevitable.
-/

import Core.Viability

namespace FSST

open FSST

universe u

inductive StackLayer where
  | directCoupling
  | signsAndMemory
  | languageAndNorm
  | institutionAndLaw
  | modelAndMetric
  | automatedProduction
  deriving DecidableEq, Repr

def stackDepth : StackLayer → Nat
  | .directCoupling => 0
  | .signsAndMemory => 1
  | .languageAndNorm => 2
  | .institutionAndLaw => 3
  | .modelAndMetric => 4
  | .automatedProduction => 5

structure StackProperties where
  layer : StackLayer
  affordance : Int
  correctionDirectness : Int
  pathologyCapacity : Int
  correctionRegimeRequired : Prop

def deeperThan (l₁ l₂ : StackLayer) : Prop :=
  stackDepth l₁ > stackDepth l₂

theorem automated_deeper_than_direct :
    deeperThan StackLayer.automatedProduction StackLayer.directCoupling := by
  unfold deeperThan stackDepth
  decide

structure MarginState (vf : ViabilityFrame) where
  system : vf.System
  condition : vf.Condition
  currentMargin : Int
  driftTolerance : Int
  correctionStrength : Int
  stackDepthVal : Nat

def DriftExceedsCorrection (ms : MarginState vf) : Prop :=
  ms.driftTolerance > ms.correctionStrength

def SurplusSubsidizesDrift (ms : MarginState vf) : Prop :=
  ms.currentMargin > 0 ∧ DriftExceedsCorrection ms

def MarginPathologyCycle (vf : ViabilityFrame)
    (before after : MarginState vf) : Prop :=
  before.currentMargin > after.currentMargin ∧
  after.stackDepthVal ≥ before.stackDepthVal ∧
  DriftExceedsCorrection after

theorem surplus_enables_drift_persistence
    (vf : ViabilityFrame)
    (ms : MarginState vf)
    (hsurplus : ms.currentMargin > 0)
    (hdrift : DriftExceedsCorrection ms) :
    SurplusSubsidizesDrift ms :=
  ⟨hsurplus, hdrift⟩

end FSST
