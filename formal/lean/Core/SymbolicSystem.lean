/-
  Formal Symbolic Systems Theory — Core typed object.

  Status: candidate formalization target / stage 1 / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Section 3.

  Purpose:
    Define SymbolicSystem as a typed structure with the fifteen specified
    components. This is the central object of the theory. All conjectures,
    theorems, and instance models are stated in terms of this structure.

  Non-claims:
    1. No claim that this typing is final. Formalization will refine it.
    2. No theorem proved in this file. Theorems belong in Theorems/.
    3. No instance instantiated here. Instances belong in Instances/.
    4. No claim about any specific symbolic system.
    5. No quantitative threshold or comparison.
-/

namespace FSST

universe u v

structure SymbolicSystem where
  Referent : Type u
  Symbol : Type v
  binding : Symbol → Referent → Prop
  encode : Referent → Symbol
  decode : Symbol → Option Referent
  transform : Symbol → Symbol
  transmit : Symbol → Symbol
  fidelity : Referent → Symbol → Prop
  Action : Type
  act : Symbol → Option Action
  consequence : Action → Referent → Int
  correct : Symbol → Symbol
  scope : Referent → Prop
  drift : Symbol → Nat → Symbol
  selectionSurvives : Symbol → Prop
  violationDetected : Referent → Symbol → Prop

end FSST
