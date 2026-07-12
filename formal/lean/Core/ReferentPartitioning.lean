/-
  Formal Symbolic Systems Theory — Referent-structure partitioning.

  Status: candidate formalization target / stage 1 extension / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Sections 3, 11.

  Purpose:
    Symbolic systems do not merely label a pre-partitioned referent space.
    They carve referent domains into symbolically available distinctions.
    Different systems can partition the same referent domain differently,
    making some distinctions obligatory, some optional, some costly, and
    some nearly unavailable.

    This file formalizes referent-structure partitioning as a typed
    relation between a referent domain and a set of symbolic distinctions,
    and defines the structural properties that follow: obligatory vs
    optional distinctions, partition-relative fidelity, cross-partition
    translation loss.

  Non-claims:
    1. No claim about which partitioning is correct for any domain.
    2. No claim that partitionings are arbitrary (some preserve more
       referent structure than others).
    3. No specific linguistic, legal, or scientific partitioning modeled.
    4. No claim that finer partitioning is always better.
-/

namespace FSST

universe u v

structure ReferentPartitioning where
  ReferentDomain : Type u
  Distinction : Type v
  partition : ReferentDomain → Distinction
  obligatory : Distinction → Prop
  available : Distinction → Prop

def DistinctionPreserved
    (rp : ReferentPartitioning)
    (r₁ r₂ : rp.ReferentDomain)
    (hne : r₁ ≠ r₂) : Prop :=
  rp.partition r₁ ≠ rp.partition r₂

def DistinctionCollapsed
    (rp : ReferentPartitioning)
    (r₁ r₂ : rp.ReferentDomain)
    (hne : r₁ ≠ r₂) : Prop :=
  rp.partition r₁ = rp.partition r₂

def PartitionFidelity
    (rp : ReferentPartitioning)
    (referents : List rp.ReferentDomain) : Prop :=
  ∀ r₁ r₂ : rp.ReferentDomain,
    List.Mem r₁ referents → List.Mem r₂ referents →
    r₁ ≠ r₂ →
    rp.partition r₁ ≠ rp.partition r₂

structure CrossPartitionTranslation where
  source : ReferentPartitioning
  target : ReferentPartitioning
  sharedDomain : source.ReferentDomain = target.ReferentDomain

def TranslationLoss
    (cpt : CrossPartitionTranslation) : Prop :=
  ∃ r₁ r₂ : cpt.source.ReferentDomain,
    r₁ ≠ r₂ ∧
    cpt.source.partition r₁ ≠ cpt.source.partition r₂ ∧
    cpt.target.partition (cast cpt.sharedDomain r₁) =
      cpt.target.partition (cast cpt.sharedDomain r₂)

def TranslationGain
    (cpt : CrossPartitionTranslation) : Prop :=
  ∃ r₁ r₂ : cpt.source.ReferentDomain,
    r₁ ≠ r₂ ∧
    cpt.source.partition r₁ = cpt.source.partition r₂ ∧
    cpt.target.partition (cast cpt.sharedDomain r₁) ≠
      cpt.target.partition (cast cpt.sharedDomain r₂)

theorem collapsed_distinction_not_preserved
    (rp : ReferentPartitioning)
    (r₁ r₂ : rp.ReferentDomain)
    (hne : r₁ ≠ r₂)
    (hcol : DistinctionCollapsed rp r₁ r₂ hne) :
    ¬ DistinctionPreserved rp r₁ r₂ hne := by
  intro hpres
  exact hpres hcol

end FSST
