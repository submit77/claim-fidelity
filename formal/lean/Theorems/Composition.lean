/-
  Formal Symbolic Systems Theory — Composition theorems.

  Status: candidate formalization target / stage 3 / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Sections 6.2, 6.3.

  Purpose:
    Prove structural properties of symbolic system composition:
      - fidelity composition bound: composed fidelity cannot exceed
        component fidelity
      - scope intersection: composed scope is at most the intersection
        of component scopes

  Non-claims:
    1. No specific composition of real systems.
    2. No quantitative fidelity measure.
    3. Composition is modeled as sequential application of encode/decode
       chains. This is a starting model, not a final theory of composition.
-/

import Core.SymbolicSystem

namespace FSST

open FSST

structure ComposedPair where
  first : SymbolicSystem
  second : SymbolicSystem
  bridge : first.Symbol → second.Referent

def ComposedFidelity
    (pair : ComposedPair)
    (r : pair.first.Referent)
    (s₂ : pair.second.Symbol) : Prop :=
  ∃ s₁ : pair.first.Symbol,
    pair.first.fidelity r s₁ ∧
    pair.second.fidelity (pair.bridge s₁) s₂

def ComposedScope
    (pair : ComposedPair)
    (r : pair.first.Referent) : Prop :=
  pair.first.scope r ∧
  ∃ s₁ : pair.first.Symbol,
    pair.first.fidelity r s₁ ∧
    pair.second.scope (pair.bridge s₁)

theorem composed_scope_subset_first
    (pair : ComposedPair)
    (r : pair.first.Referent)
    (h : ComposedScope pair r) :
    pair.first.scope r :=
  h.left

theorem composed_fidelity_requires_first_fidelity
    (pair : ComposedPair)
    (r : pair.first.Referent)
    (s₂ : pair.second.Symbol)
    (h : ComposedFidelity pair r s₂) :
    ∃ s₁ : pair.first.Symbol, pair.first.fidelity r s₁ :=
  ⟨h.choose, h.choose_spec.left⟩

theorem no_composed_fidelity_without_first
    (pair : ComposedPair)
    (r : pair.first.Referent)
    (s₂ : pair.second.Symbol)
    (hno : ∀ s₁ : pair.first.Symbol, ¬ pair.first.fidelity r s₁) :
    ¬ ComposedFidelity pair r s₂ := by
  intro ⟨s₁, hf₁, _⟩
  exact hno s₁ hf₁

theorem no_composed_fidelity_without_second
    (pair : ComposedPair)
    (r : pair.first.Referent)
    (s₂ : pair.second.Symbol)
    (hno : ∀ s₁ : pair.first.Symbol,
      pair.first.fidelity r s₁ →
      ¬ pair.second.fidelity (pair.bridge s₁) s₂) :
    ¬ ComposedFidelity pair r s₂ := by
  intro ⟨s₁, hf₁, hf₂⟩
  exact hno s₁ hf₁ hf₂

end FSST
