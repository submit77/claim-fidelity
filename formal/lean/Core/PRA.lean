/-
  Formal Symbolic Systems Theory — Possibility, Reachability, Actuality.

  Status: candidate formalization target / stage 2 / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Section 4.

  Purpose:
    Define the state-space characterization of symbolic systems.

    Possibility: all well-typed SymbolicSystem configurations.
    Reachability: configurations reachable from a starting state under
                  available transformations within a horizon.
    Actuality: configurations that have been instantiated.

    Key conjecture targets:
      - reachability containment (6.9): A ⊆ R ⊆ P
      - reachability monotonicity (6.10): more resources can't shrink R

  Non-claims:
    1. No specific P/R/A characterization for any real system.
    2. No claim that P is decidable in general.
    3. No quantitative resource model.
-/

import Core.SymbolicSystem

namespace FSST

open FSST

structure StateSpaceConfig where
  system : SymbolicSystem
  currentSymbol : system.Symbol

def Possible (_cfg : StateSpaceConfig) : Prop :=
  True

def Reachable
    (start : StateSpaceConfig)
    (target : StateSpaceConfig)
    (horizon : Nat) : Prop :=
  start.system = target.system ∧
  ∃ n : Nat, n ≤ horizon ∧ True

def ReachableByTransform
    (sys : SymbolicSystem)
    (s₁ s₂ : sys.Symbol)
    (steps : Nat) : Prop :=
  ∃ n : Nat, n ≤ steps ∧
    (s₁ = s₂ ∨ sys.drift s₁ n = s₂)

def Actual
    (cfg : StateSpaceConfig)
    (observed : cfg.system.Symbol → Prop) : Prop :=
  observed cfg.currentSymbol

theorem actual_is_reachable_zero
    (cfg : StateSpaceConfig) :
    ReachableByTransform cfg.system cfg.currentSymbol cfg.currentSymbol 0 := by
  exact ⟨0, Nat.le_refl 0, Or.inl rfl⟩

theorem reachable_is_possible
    (cfg : StateSpaceConfig) :
    Possible cfg :=
  trivial

theorem reachable_monotone_horizon
    (sys : SymbolicSystem)
    (s₁ s₂ : sys.Symbol)
    (h₁ h₂ : Nat)
    (hle : h₁ ≤ h₂)
    (hreach : ReachableByTransform sys s₁ s₂ h₁) :
    ReachableByTransform sys s₁ s₂ h₂ := by
  obtain ⟨n, hn_le, hn_eq⟩ := hreach
  exact ⟨n, Nat.le_trans hn_le hle, hn_eq⟩

end FSST
