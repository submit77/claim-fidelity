/-
  Formal Symbolic Systems Theory - Consequence licensing core.

  Status: candidate formalization target / stage 1 / do not promote.

  Source prose:
    docs/formation/10_formalization_targets_v0.1.md
    docs/formation/14_structural_normal_form_v0.1.md

  Purpose:
    Encode the smallest abstract predicate surface for consequence licensing.
    This file intentionally avoids domain-specific validity rules. It proves
    structural facts about drawn consequences, licenses, transmission metadata,
    and chain links.

  Non-claims:
    1. No claim that any real consequence is licensed.
    2. No domain-specific validity criterion.
    3. No quantitative confidence model.
    4. No complete FSST object model.
-/

namespace FSST

universe u

structure LicenseWorld where
  CarrierState : Type u
  Inference : Type u
  ValidityCriterion : Type u
  Scope : Type u
  Confidence : Type u
  Consequence : Type u
  ValidFor :
    CarrierState ->
    Inference ->
    ValidityCriterion ->
    Scope ->
    Confidence ->
    Prop
  Licensed :
    Consequence ->
    ValidityCriterion ->
    Scope ->
    Confidence ->
    Prop
  Drawn :
    CarrierState ->
    Inference ->
    Consequence ->
    Prop

namespace LicenseWorld

variable (W : LicenseWorld)

structure SymbolicUse where
  state : W.CarrierState
  inference : W.Inference
  criterion : W.ValidityCriterion
  scope : W.Scope
  confidence : W.Confidence

structure Transmission where
  source : SymbolicUse W
  received : SymbolicUse W

structure Link where
  use : SymbolicUse W
  consequence : W.Consequence

def ValidForUse
    (use : SymbolicUse W) : Prop :=
  W.ValidFor use.state use.inference use.criterion use.scope use.confidence

def LicensedConsequence
    (use : SymbolicUse W)
    (consequence : W.Consequence) : Prop :=
  W.Licensed consequence use.criterion use.scope use.confidence

def LicensedAt
    (state : W.CarrierState)
    (inference : W.Inference)
    (criterion : W.ValidityCriterion)
    (scope : W.Scope)
    (confidence : W.Confidence) : Prop :=
  W.ValidFor state inference criterion scope confidence

def ConsequenceLicensedAt
    (consequence : W.Consequence)
    (criterion : W.ValidityCriterion)
    (scope : W.Scope)
    (confidence : W.Confidence) : Prop :=
  W.Licensed consequence criterion scope confidence

variable {W}

def ConsequenceDrawn
    (use : SymbolicUse W)
    (consequence : W.Consequence) : Prop :=
  W.Drawn use.state use.inference consequence

def Operative (use : SymbolicUse W) : Prop :=
  Exists (ConsequenceDrawn use)

def UnauthorizedConsequence
    (use : SymbolicUse W)
    (consequence : W.Consequence) : Prop :=
  Operative use
    /\ ConsequenceDrawn use consequence
    /\ Not (LicensedConsequence W use consequence)

def FalseSymbolicRealityByConsequence (use : SymbolicUse W) : Prop :=
  Exists (UnauthorizedConsequence use)

def MetadataStripped
    (transmission : Transmission W)
    (consequence : W.Consequence) : Prop :=
  ConsequenceDrawn transmission.received consequence
    /\ LicensedConsequence W transmission.source consequence
    /\ Not (LicensedConsequence W transmission.received consequence)

def LinkLicensed (link : Link W) : Prop :=
  LicensedConsequence W link.use link.consequence

def ChainLicensed (links : List (Link W)) : Prop :=
  forall link, link ∈ links -> LinkLicensed link

theorem unauthorized_consequence_has_drawn_unlicensed
    {use : SymbolicUse W}
    {consequence : W.Consequence}
    (h : UnauthorizedConsequence use consequence) :
    ConsequenceDrawn use consequence
      /\ Not (LicensedConsequence W use consequence) := by
  exact And.intro h.right.left h.right.right

theorem false_symbolic_reality_iff_exists_unauthorized
    (use : SymbolicUse W) :
    FalseSymbolicRealityByConsequence use
      <-> Exists (UnauthorizedConsequence use) := by
  rfl

theorem metadata_stripped_yields_received_unlicensed
    {transmission : Transmission W}
    {consequence : W.Consequence}
    (h : MetadataStripped transmission consequence) :
    ConsequenceDrawn transmission.received consequence
      /\ Not (LicensedConsequence W transmission.received consequence) := by
  exact And.intro h.left h.right.right

theorem metadata_stripped_source_was_licensed
    {transmission : Transmission W}
    {consequence : W.Consequence}
    (h : MetadataStripped transmission consequence) :
    LicensedConsequence W transmission.source consequence := by
  exact h.right.left

theorem unlicensed_link_breaks_chain
    {link : Link W}
    {links : List (Link W)}
    (hin : link ∈ links)
    (hunlicensed : Not (LinkLicensed link)) :
    Not (ChainLicensed links) := by
  intro hchain
  have hlicensed : LinkLicensed link := hchain link hin
  exact hunlicensed hlicensed

theorem chain_license_requires_each_link
    {link : Link W}
    {links : List (Link W)}
    (hchain : ChainLicensed links)
    (hin : link ∈ links) :
    LinkLicensed link := by
  exact hchain link hin

end LicenseWorld

end FSST
