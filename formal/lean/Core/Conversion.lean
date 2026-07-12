/-
  Formal Symbolic Systems Theory — Conversion structure.

  Status: candidate formalization target / stage 1 extension / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Section 6.

  Purpose:
    Formalize conversion as the dominant content of reality coupling.
    Symbolic systems primarily encode conversion-relevant structure: how
    states, resources, signals, actions, relations, or configurations can
    be transformed into other states under constraint.

    Conversion is a constrained transformation from one state, resource,
    relation, or configuration into another. This includes direct
    conversions (food → energy), preservation (current state → future
    state), avoidance (threat → non-loss), coordination (many agents →
    shared action), and all derivative operations that preserve or
    constrain future conversion possibilities.

  Non-claims:
    1. No claim that all symbolic content is conversion.
    2. No claim about specific conversion rates or costs.
    3. The scoped claim: most symbolic systems encode conversion-relevant
       structure, not that all are only about conversion.
    4. No reduction of meaning to conversion.
-/

import Core.SymbolicSystem
import Core.ValidityLayers
import Core.Viability

namespace FSST

open FSST

universe u v

structure Conversion where
  Source : Type u
  Target : Type v
  constraint : Prop
  cost : Int
  risk : Int
  feasible : Prop
  prohibited : Prop

inductive ConversionContent where
  | pathway
  | rate
  | cost
  | risk
  | constraint
  | eligibility
  | timing
  | agent
  | tool
  | prohibition
  | failure
  | gain
  | loss
  deriving DecidableEq, Repr

inductive DerivativeOperation where
  | preservation
  | avoidance
  | coordination
  | classification
  | measurement
  | prediction
  | memory
  | norm
  | pricing
  | identity
  deriving DecidableEq, Repr

structure ConversionMap (sys : SymbolicSystem) where
  Conv : Type u
  source : Conv → Type
  target : Conv → Type
  cost : Conv → Int
  risk : Conv → Int
  feasible : Conv → Prop
  prohibited : Conv → Prop
  encodedBy : Conv → sys.Symbol
  grounded : Conv → Prop

def ConversionRelevant
    (sys : SymbolicSystem) (cm : ConversionMap sys)
    (s : sys.Symbol) : Prop :=
  ∃ c : cm.Conv, cm.encodedBy c = s ∧ cm.grounded c

def ProhibitedConversion
    (sys : SymbolicSystem) (cm : ConversionMap sys)
    (c : cm.Conv) : Prop :=
  cm.prohibited c ∧ cm.grounded c

def FeasibleConversion
    (sys : SymbolicSystem) (cm : ConversionMap sys)
    (c : cm.Conv) : Prop :=
  cm.feasible c ∧ ¬ cm.prohibited c ∧ cm.grounded c

theorem prohibited_not_feasible
    (sys : SymbolicSystem) (cm : ConversionMap sys) (c : cm.Conv)
    (hproh : ProhibitedConversion sys cm c) :
    ¬ FeasibleConversion sys cm c := by
  intro ⟨_, hnp, _⟩
  exact hnp hproh.1

structure ConversionChain (sys : SymbolicSystem) where
  steps : List sys.Symbol
  grounded : ∀ s : sys.Symbol, List.Mem s steps → SyntacticallyValid sys s
  linked : Prop

structure ViabilityConversion (vf : ViabilityFrame) where
  system : vf.System
  condition : vf.Condition
  before : Int
  after : Int
  increases : after > before

theorem viability_conversion_increases_margin
    (vf : ViabilityFrame)
    (vc : ViabilityConversion vf) :
    vc.after > vc.before :=
  vc.increases

inductive ConversionPrimitive where
  | stateToState
  | resourceToWork
  | signalToAction
  | constraintToResponse
  | riskToMitigation
  | differenceToComparison
  | quantityToAllocation
  | conflictToCoordination
  | uncertaintyToPrediction
  | possibilityToSelection
  | energyToMaintenance
  | informationToOptionality
  deriving DecidableEq, Repr

structure ConversionSkeleton where
  primitive : ConversionPrimitive
  domain : Type u
  localSyntax : Type v
  embedding : localSyntax → ConversionPrimitive

structure ComposedConversion where
  steps : List ConversionPrimitive
  nonempty : steps ≠ []

structure Decompression (sys : SymbolicSystem) where
  extractPrimitive : sys.Symbol → Option ConversionPrimitive
  extractScope : sys.Symbol → Option (sys.Referent → Prop)
  extractCost : sys.Symbol → Option Int
  grounded : sys.Symbol → Prop

def SameSkeleton
    (d₁ : Decompression sys₁)
    (d₂ : Decompression sys₂)
    (s₁ : sys₁.Symbol)
    (s₂ : sys₂.Symbol) : Prop :=
  ∃ p : ConversionPrimitive,
    d₁.extractPrimitive s₁ = some p ∧
    d₂.extractPrimitive s₂ = some p

end FSST
