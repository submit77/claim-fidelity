/-
  Formal Symbolic Systems Theory — Constraint mesh assembly.

  Status: candidate formalization target / stage 2 extension / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Section 15.

  Purpose:
    Formalize the constraint mesh: the distributed, fragmented map of
    constraints that define human boundedness, scattered across the
    symbolic outputs of every domain. A mature symbolic systems theory
    enables extraction, typing, grounding, reconciliation, and assembly
    of those constraints into a coherent, reality-coupled graph.

    The problem is not absence of knowledge. It is symbolic fragmentation.
    The constraint mesh is documented but not composed.

  Non-claims:
    1. No claim that the mesh is completable.
    2. No claim about any specific domain's constraint coverage.
    3. No claim that assembly eliminates all conflict.
    4. No claim that the mesh replaces domain expertise.
-/

namespace FSST

open FSST

universe u v

inductive ConstraintCategory where
  | energetic
  | metabolic
  | cognitive
  | perceptual
  | temporal
  | mortality
  | coordination
  | ecological
  | material
  | informational
  | institutional
  | symbolic
  deriving DecidableEq, Repr

inductive ConstraintDomain where
  | physics
  | chemistry
  | biology
  | medicine
  | ecology
  | economics
  | engineering
  | mathematics
  | law
  | anthropology
  | psychology
  | linguistics
  | history
  | logistics
  | systemsTheory
  | computerScience
  | institutionalRecords
  | culturalNarrative
  deriving DecidableEq, Repr

structure TypedConstraint where
  Referent : Type u
  category : ConstraintCategory
  sourceDomain : ConstraintDomain
  grounded : Prop
  scope : Type v
  scopeValid : scope → Prop
  confidence : Int

structure ConstraintMesh where
  Constraint : Type u
  category : Constraint → ConstraintCategory
  sourceDomain : Constraint → ConstraintDomain
  grounded : Constraint → Prop
  compatible : Constraint → Constraint → Prop
  composes : Constraint → Constraint → Prop
  confidence : Constraint → Int

def MeshConsistent (mesh : ConstraintMesh) : Prop :=
  ∀ c₁ c₂ : mesh.Constraint,
    mesh.composes c₁ c₂ →
    mesh.compatible c₁ c₂

def MeshGrounded (mesh : ConstraintMesh) : Prop :=
  ∀ c : mesh.Constraint, mesh.grounded c

def CrossDomainEquivalence (mesh : ConstraintMesh)
    (c₁ c₂ : mesh.Constraint) : Prop :=
  mesh.sourceDomain c₁ ≠ mesh.sourceDomain c₂ ∧
  mesh.compatible c₁ c₂ ∧
  mesh.category c₁ = mesh.category c₂

def CrossDomainConflict (mesh : ConstraintMesh)
    (c₁ c₂ : mesh.Constraint) : Prop :=
  mesh.sourceDomain c₁ ≠ mesh.sourceDomain c₂ ∧
  ¬ mesh.compatible c₁ c₂ ∧
  mesh.category c₁ = mesh.category c₂

def MeshGap (mesh : ConstraintMesh)
    (cat : ConstraintCategory) : Prop :=
  ¬ ∃ c : mesh.Constraint,
    mesh.category c = cat ∧ mesh.grounded c

structure FragmentedCorpus where
  Domain : Type u
  Output : Type v
  source : Output → Domain
  containsConstraint : Output → Prop

structure ConstraintExtraction (corpus : FragmentedCorpus) (mesh : ConstraintMesh) where
  extract : corpus.Output → Option mesh.Constraint
  extractionPreservesGrounding :
    ∀ o : corpus.Output,
      ∀ c : mesh.Constraint,
        extract o = some c →
        corpus.containsConstraint o →
        mesh.grounded c

theorem conflict_is_not_equivalence
    (mesh : ConstraintMesh)
    (c₁ c₂ : mesh.Constraint)
    (hconf : CrossDomainConflict mesh c₁ c₂) :
    ¬ CrossDomainEquivalence mesh c₁ c₂ := by
  intro ⟨_, hcompat, _⟩
  exact hconf.2.1 hcompat

theorem consistent_mesh_composes_only_compatible
    (mesh : ConstraintMesh)
    (hcons : MeshConsistent mesh)
    (c₁ c₂ : mesh.Constraint)
    (hcomp : mesh.composes c₁ c₂) :
    mesh.compatible c₁ c₂ :=
  hcons c₁ c₂ hcomp

end FSST
