/-
  Formal Symbolic Systems Theory - Consequence policy core.

  Status: candidate formalization target / stage 1 / do not promote.

  Source prose:
    docs/formation/16_structural_compiler_seed_v0.1.md

  Purpose:
    Encode the next abstract predicate surface discovered by the structural
    compiler seed: a valid inference does not by itself license every
    consequence. A consequence also requires an action policy that allows that
    inference to route that consequence under the preserved scope and
    confidence.

  Non-claims:
    1. No domain-specific policy content.
    2. No claim that any real policy is good or sufficient.
    3. No quantitative confidence model.
    4. No complete FSST object model.
-/

namespace FSST

universe u

structure PolicyWorld where
  CarrierState : Type u
  Inference : Type u
  ValidityCriterion : Type u
  Scope : Type u
  Confidence : Type u
  Consequence : Type u
  ActionPolicy : Type u
  ValidFor :
    CarrierState ->
    Inference ->
    ValidityCriterion ->
    Scope ->
    Confidence ->
    Prop
  PolicyAllows :
    ActionPolicy ->
    Inference ->
    Consequence ->
    Scope ->
    Confidence ->
    Prop
  Drawn :
    CarrierState ->
    Inference ->
    Consequence ->
    Prop

namespace PolicyWorld

variable (W : PolicyWorld)

structure SymbolicUse where
  state : W.CarrierState
  inference : W.Inference
  criterion : W.ValidityCriterion
  scope : W.Scope
  confidence : W.Confidence
  policy : W.ActionPolicy

def ValidForUse
    (use : SymbolicUse W) : Prop :=
  W.ValidFor use.state use.inference use.criterion use.scope use.confidence

def PolicyAllowsUse
    (use : SymbolicUse W)
    (consequence : W.Consequence) : Prop :=
  W.PolicyAllows
    use.policy
    use.inference
    consequence
    use.scope
    use.confidence

def PolicyLicensed
    (use : SymbolicUse W)
    (consequence : W.Consequence) : Prop :=
  ValidForUse W use /\ PolicyAllowsUse W use consequence

variable {W}

def ConsequenceDrawn
    (use : SymbolicUse W)
    (consequence : W.Consequence) : Prop :=
  W.Drawn use.state use.inference consequence

def PolicyUnauthorized
    (use : SymbolicUse W)
    (consequence : W.Consequence) : Prop :=
  ConsequenceDrawn use consequence /\
    Not (PolicyLicensed W use consequence)

theorem policy_license_requires_valid_for
    {use : SymbolicUse W}
    {consequence : W.Consequence}
    (h : PolicyLicensed W use consequence) :
    ValidForUse W use := by
  exact h.left

theorem policy_license_requires_policy_allowance
    {use : SymbolicUse W}
    {consequence : W.Consequence}
    (h : PolicyLicensed W use consequence) :
    PolicyAllowsUse W use consequence := by
  exact h.right

theorem invalid_use_cannot_be_policy_licensed
    {use : SymbolicUse W}
    {consequence : W.Consequence}
    (hinvalid : Not (ValidForUse W use)) :
    Not (PolicyLicensed W use consequence) := by
  intro hlicensed
  exact hinvalid hlicensed.left

theorem disallowed_consequence_cannot_be_policy_licensed
    {use : SymbolicUse W}
    {consequence : W.Consequence}
    (hdisallowed : Not (PolicyAllowsUse W use consequence)) :
    Not (PolicyLicensed W use consequence) := by
  intro hlicensed
  exact hdisallowed hlicensed.right

theorem drawn_but_invalid_is_policy_unauthorized
    {use : SymbolicUse W}
    {consequence : W.Consequence}
    (hdrawn : ConsequenceDrawn use consequence)
    (hinvalid : Not (ValidForUse W use)) :
    PolicyUnauthorized use consequence := by
  exact And.intro hdrawn (invalid_use_cannot_be_policy_licensed hinvalid)

theorem drawn_but_disallowed_is_policy_unauthorized
    {use : SymbolicUse W}
    {consequence : W.Consequence}
    (hdrawn : ConsequenceDrawn use consequence)
    (hdisallowed : Not (PolicyAllowsUse W use consequence)) :
    PolicyUnauthorized use consequence := by
  exact And.intro hdrawn
    (disallowed_consequence_cannot_be_policy_licensed hdisallowed)

theorem policy_unauthorized_has_drawn_unlicensed
    {use : SymbolicUse W}
    {consequence : W.Consequence}
    (h : PolicyUnauthorized use consequence) :
    ConsequenceDrawn use consequence /\
      Not (PolicyLicensed W use consequence) := by
  exact h

end PolicyWorld

end FSST
