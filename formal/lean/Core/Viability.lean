/-
  Formal Symbolic Systems Theory — Viability and margin relations.

  Status: candidate formalization target / stage 1 extension / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md.

  Purpose:
    Ground symbolic systems in thermodynamic viability. Symbolic systems
    exist because organisms and organized systems must maintain viability
    under constraint. They encode referent distinctions that allow systems
    to preserve or increase margin above viability floors.

    Normativity is formalized as indexed margin relations: how a referent
    state moves a system toward or away from viability under specified
    conditions. "Good," "bad," "valuable," "dangerous" are compressed
    margin-relative predicates, not free-floating properties of reality.

  Non-claims:
    1. No claim that all symbolic systems are conscious of viability.
    2. No quantitative viability threshold.
    3. No claim that margin is the only thing that matters.
    4. No reduction of meaning to survival.
-/

namespace FSST

universe u

structure ViabilityFrame where
  System : Type u
  Condition : Type u
  margin : System → Condition → Int
  floor : System → Int
  viable : System → Condition → Prop := fun s c => margin s c ≥ floor s

def AboveFloor (vf : ViabilityFrame) (s : vf.System) (c : vf.Condition) : Prop :=
  vf.margin s c ≥ vf.floor s

def AtFloor (vf : ViabilityFrame) (s : vf.System) (c : vf.Condition) : Prop :=
  vf.margin s c = vf.floor s

def BelowFloor (vf : ViabilityFrame) (s : vf.System) (c : vf.Condition) : Prop :=
  vf.margin s c < vf.floor s

structure MarginRelation (vf : ViabilityFrame) where
  system : vf.System
  condition : vf.Condition
  referent : Type
  effect : referent → Int
  horizon : Nat

def IncreasesMargin (vf : ViabilityFrame) (mr : MarginRelation vf) (r : mr.referent) : Prop :=
  mr.effect r > 0

def DecreasesMargin (vf : ViabilityFrame) (mr : MarginRelation vf) (r : mr.referent) : Prop :=
  mr.effect r < 0

def MarginNeutral (vf : ViabilityFrame) (mr : MarginRelation vf) (r : mr.referent) : Prop :=
  mr.effect r = 0

structure IndexedEvaluation (vf : ViabilityFrame) where
  system : vf.System
  condition : vf.Condition
  referent : Type
  value : referent → Int
  goal : Type
  horizon : Nat
  mechanism : Type
  cost : referent → Int

theorem evaluation_requires_index
    (vf : ViabilityFrame)
    (s₁ s₂ : vf.System)
    (c₁ c₂ : vf.Condition)
    (hne_sys : s₁ ≠ s₂)
    (hm₁ : vf.margin s₁ c₁ ≥ vf.floor s₁)
    (hm₂ : vf.margin s₂ c₂ < vf.floor s₂) :
    AboveFloor vf s₁ c₁ ∧ BelowFloor vf s₂ c₂ :=
  ⟨hm₁, hm₂⟩

def Affordance (vf : ViabilityFrame) : Type :=
  (s : vf.System) × (c : vf.Condition) × (AboveFloor vf s c → Prop)

end FSST
