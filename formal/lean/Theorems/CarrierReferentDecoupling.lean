/-
  Formal Symbolic Systems Theory — Carrier-referent decoupling theorems.

  Status: candidate formalization target / stage 3 extension / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Sections 10, 11.

  Purpose:
    Prove the central diagnostic theorem: syntactic validity does not
    entail referential validity. In any symbolic system where operations
    can proceed without referent validation, well-formed null-grounded
    symbols can propagate through valid transformations.

    This formalizes the failure chain:
      well-formed symbol
      → missing or malformed referent relation
      → accepted by symbolic procedure
      → propagated through transformations
      → treated as grounded by downstream systems
      → acted upon
      → real consequences

  Non-claims:
    1. No claim that all symbolic systems exhibit this failure.
    2. No claim about specific systems (software, law, metrics, etc.).
    3. No quantitative measure of propagation depth.
    4. No claim that referent checking is always feasible.
-/

import Core.SymbolicSystem
import Core.ValidityLayers

namespace FSST

open FSST

theorem referentially_null_is_not_referentially_valid
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hnull : ReferentiallyNull sys s) :
    ¬ ReferentiallyValid sys s := by
  intro ⟨r, _, hfid⟩
  exact hnull r hfid

theorem well_formed_referential_failure_exists_implies_decoupling
    (sys : SymbolicSystem)
    (wfrf : WellFormedReferentialFailure sys) :
    SyntacticallyValid sys wfrf.symbol ∧
    ¬ ReferentiallyValid sys wfrf.symbol := by
  exact ⟨wfrf.syntacticallyValid,
    referentially_null_is_not_referentially_valid sys wfrf.symbol wfrf.referentiallyNull⟩

theorem transform_preserves_syntactic_not_referential
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hnull : ReferentiallyNull sys s)
    (htrans_null : ReferentiallyNull sys (sys.transform s)) :
    SyntacticallyValid sys (sys.transform s) ∧
    ¬ ReferentiallyValid sys (sys.transform s) := by
  exact ⟨trivial,
    referentially_null_is_not_referentially_valid sys (sys.transform s) htrans_null⟩

theorem transmit_preserves_syntactic_not_referential
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hnull : ReferentiallyNull sys s)
    (htrans_null : ReferentiallyNull sys (sys.transmit s)) :
    SyntacticallyValid sys (sys.transmit s) ∧
    ¬ ReferentiallyValid sys (sys.transmit s) := by
  exact ⟨trivial,
    referentially_null_is_not_referentially_valid sys (sys.transmit s) htrans_null⟩

def TransformPreservesNullGrounding (sys : SymbolicSystem) : Prop :=
  ∀ s : sys.Symbol,
    ReferentiallyNull sys s →
    ReferentiallyNull sys (sys.transform s)

def TransmitPreservesNullGrounding (sys : SymbolicSystem) : Prop :=
  ∀ s : sys.Symbol,
    ReferentiallyNull sys s →
    ReferentiallyNull sys (sys.transmit s)

theorem null_propagation_under_transform_preservation
    (sys : SymbolicSystem)
    (hpres : TransformPreservesNullGrounding sys)
    (s : sys.Symbol)
    (hnull : ReferentiallyNull sys s) :
    ReferentiallyNull sys (sys.transform s) :=
  hpres s hnull

theorem syntax_only_correction_leaves_null_grounding
    (sys : SymbolicSystem)
    (s : sys.Symbol)
    (hnull : ReferentiallyNull sys s)
    (hcorr_null : ReferentiallyNull sys (sys.correct s)) :
    SyntacticallyValid sys (sys.correct s) ∧
    ¬ ReferentiallyValid sys (sys.correct s) := by
  exact ⟨trivial,
    referentially_null_is_not_referentially_valid sys (sys.correct s) hcorr_null⟩

theorem referent_checking_correction_blocks_null_propagation
    (sys : SymbolicSystem)
    (hcorr : ReferentCheckingCorrection sys)
    (r : sys.Referent)
    (s : sys.Symbol)
    (hscope : sys.scope r)
    (hviol : sys.violationDetected r s) :
    ReferentiallyValid sys (sys.correct s) :=
  hcorr r s hscope hviol

end FSST
