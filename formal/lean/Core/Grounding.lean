/-
  Formal Symbolic Systems Theory — Grounding relations.

  Status: candidate formalization target / stage 1 / do not promote.

  Source prose:
    docs/foundation/founding_document_v0.3.md, Section 5.

  Purpose:
    Define the grounding relation between symbolic states and referent
    structure. Grounding is what distinguishes a symbolic state that
    preserves referent contact from one that has drifted.

    Core structural claims formalized here:
      - a symbolic state is grounded when fidelity holds for some referent
      - encoding preserves grounding when the encoded symbol is faithful
      - decoding recovers grounding when the decoded referent matches

  Non-claims:
    1. No claim about what specific referents exist.
    2. No claim about which encodings are correct for any domain.
    3. No quantitative fidelity threshold.
-/

import Core.SymbolicSystem

namespace FSST

open FSST

def IsGrounded (sys : SymbolicSystem) (s : sys.Symbol) : Prop :=
  ∃ r : sys.Referent, sys.scope r ∧ sys.fidelity r s

def EncodingPreservesGrounding (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, sys.scope r → sys.fidelity r (sys.encode r)

def DecodingRecoversReferent (sys : SymbolicSystem) : Prop :=
  ∀ r : sys.Referent, sys.scope r → sys.decode (sys.encode r) = some r

def RoundTripFaithful (sys : SymbolicSystem) : Prop :=
  EncodingPreservesGrounding sys ∧ DecodingRecoversReferent sys

end FSST
