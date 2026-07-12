/-
  Formal Symbolic Systems Theory - Recognition authority core.

  Status: candidate formalization target / stage 1 / do not promote.

  Source prose:
    docs/formation/19_adversarial_structural_compiler_seed_v0.1.md

  Purpose:
    Encode the abstract predicate surface discovered by the adversarial
    compiler seed: in contested symbolic infrastructures, a carrier state
    becomes authority-licensed only when recognized by a recognizer with
    standing inside the relevant scope.

  Non-claims:
    1. No domain-specific account of what grants standing.
    2. No claim that recognized authority is morally legitimate.
    3. No complete theory of institutions, identity, or consent.
    4. No collapse of SymbolicSystem, SymbolicUse, and PolicyWorld.
-/

namespace FSST

universe u

structure AuthorityWorld where
  CarrierState : Type u
  Inference : Type u
  Scope : Type u
  Recognizer : Type u
  Consequence : Type u
  RecognizedBy :
    CarrierState ->
    Inference ->
    Scope ->
    Recognizer ->
    Prop
  HasStanding :
    Recognizer ->
    CarrierState ->
    Inference ->
    Scope ->
    Prop
  Drawn :
    CarrierState ->
    Inference ->
    Consequence ->
    Prop

namespace AuthorityWorld

variable (W : AuthorityWorld)

structure SymbolicUse where
  state : W.CarrierState
  inference : W.Inference
  scope : W.Scope

def RecognizedUseBy
    (use : SymbolicUse W)
    (recognizer : W.Recognizer) : Prop :=
  W.RecognizedBy use.state use.inference use.scope recognizer

def StandingForUse
    (use : SymbolicUse W)
    (recognizer : W.Recognizer) : Prop :=
  W.HasStanding recognizer use.state use.inference use.scope

def AuthorityLicensed
    (use : SymbolicUse W)
    (recognizer : W.Recognizer) : Prop :=
  RecognizedUseBy W use recognizer /\
    StandingForUse W use recognizer

variable {W}

def ConsequenceDrawn
    (use : SymbolicUse W)
    (consequence : W.Consequence) : Prop :=
  W.Drawn use.state use.inference consequence

def AuthorityUnauthorized
    (use : SymbolicUse W)
    (recognizer : W.Recognizer)
    (consequence : W.Consequence) : Prop :=
  ConsequenceDrawn use consequence /\
    Not (AuthorityLicensed W use recognizer)

theorem authority_license_requires_recognition
    {use : SymbolicUse W}
    {recognizer : W.Recognizer}
    (h : AuthorityLicensed W use recognizer) :
    RecognizedUseBy W use recognizer := by
  exact h.left

theorem authority_license_requires_standing
    {use : SymbolicUse W}
    {recognizer : W.Recognizer}
    (h : AuthorityLicensed W use recognizer) :
    StandingForUse W use recognizer := by
  exact h.right

theorem unrecognized_use_cannot_be_authority_licensed
    {use : SymbolicUse W}
    {recognizer : W.Recognizer}
    (hunrecognized : Not (RecognizedUseBy W use recognizer)) :
    Not (AuthorityLicensed W use recognizer) := by
  intro hlicensed
  exact hunrecognized hlicensed.left

theorem no_standing_cannot_be_authority_licensed
    {use : SymbolicUse W}
    {recognizer : W.Recognizer}
    (hno_standing : Not (StandingForUse W use recognizer)) :
    Not (AuthorityLicensed W use recognizer) := by
  intro hlicensed
  exact hno_standing hlicensed.right

theorem drawn_but_unrecognized_is_authority_unauthorized
    {use : SymbolicUse W}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (hdrawn : ConsequenceDrawn use consequence)
    (hunrecognized : Not (RecognizedUseBy W use recognizer)) :
    AuthorityUnauthorized use recognizer consequence := by
  exact And.intro hdrawn
    (unrecognized_use_cannot_be_authority_licensed hunrecognized)

theorem drawn_but_no_standing_is_authority_unauthorized
    {use : SymbolicUse W}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (hdrawn : ConsequenceDrawn use consequence)
    (hno_standing : Not (StandingForUse W use recognizer)) :
    AuthorityUnauthorized use recognizer consequence := by
  exact And.intro hdrawn
    (no_standing_cannot_be_authority_licensed hno_standing)

theorem authority_unauthorized_has_drawn_unlicensed
    {use : SymbolicUse W}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (h : AuthorityUnauthorized use recognizer consequence) :
    ConsequenceDrawn use consequence /\
      Not (AuthorityLicensed W use recognizer) := by
  exact h

end AuthorityWorld

end FSST
