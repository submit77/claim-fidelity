/-
  Formal Symbolic Systems Theory — Scope relations.

  Status: candidate formalization target / stage 1 / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Sections 3, 5, 6.3.

  Purpose:
    Define scope as a predicate on referents. Scope conditions determine
    where a symbolic system's encoding, transformations, and claims are
    valid. Scope intersection under composition is a key conjecture target.

  Non-claims:
    1. No claim about which referents are in scope for any real system.
    2. No composition defined here (see Theorems/Composition.lean).
-/

import Core.SymbolicSystem

namespace FSST

open FSST

def InScope (sys : SymbolicSystem) (r : sys.Referent) : Prop :=
  sys.scope r

def OutOfScope (sys : SymbolicSystem) (r : sys.Referent) : Prop :=
  ¬ sys.scope r

def ScopeNonEmpty (sys : SymbolicSystem) : Prop :=
  ∃ r : sys.Referent, sys.scope r

def FidelityOnlyInScope (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, ∀ s : sys.Symbol,
    sys.fidelity r s → sys.scope r

end FSST
