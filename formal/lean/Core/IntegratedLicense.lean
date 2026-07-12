/-
  Formal Symbolic Systems Theory - Integrated license core.

  Status: candidate integration slice / stage 1 / do not promote.

  Source prose:
    docs/formation/compiler_records/1c_project_artifact_records_v0.1.json

  Purpose:
    Encode the dependency chain pressured by the 1C project-artifact pilot:

      persistent system -> use episode -> recognition/standing -> policy license

    This file is intentionally abstract. It composes the previously discovered
    predicate surfaces without importing or collapsing their richer local
    structures.

  Non-claims:
    1. No domain-specific account of valid systems, standing, or policy.
    2. No claim that formal integration proves empirical warrant.
    3. No collapse of object, event, standing, and norm into one ontology.
    4. No production compiler/runtime claim.
-/

namespace FSST

universe u

structure IntegratedWorld where
  SymbolicSystem : Type u
  SymbolicUse : Type u
  Recognizer : Type u
  Consequence : Type u
  SystemUse :
    SymbolicSystem ->
    SymbolicUse ->
    Prop
  AuthorityLicensed :
    SymbolicUse ->
    Recognizer ->
    Prop
  PolicyLicensed :
    SymbolicUse ->
    Consequence ->
    Prop
  ConsequenceDrawn :
    SymbolicUse ->
    Consequence ->
    Prop

namespace IntegratedWorld

variable (W : IntegratedWorld)

def FullyLicensed
    (system : W.SymbolicSystem)
    (use : W.SymbolicUse)
    (recognizer : W.Recognizer)
    (consequence : W.Consequence) : Prop :=
  W.SystemUse system use /\
    W.AuthorityLicensed use recognizer /\
    W.PolicyLicensed use consequence

variable {W}

def FullyUnauthorized
    (system : W.SymbolicSystem)
    (use : W.SymbolicUse)
    (recognizer : W.Recognizer)
    (consequence : W.Consequence) : Prop :=
  W.ConsequenceDrawn use consequence /\
    Not (FullyLicensed W system use recognizer consequence)

theorem full_license_requires_system_use
    {system : W.SymbolicSystem}
    {use : W.SymbolicUse}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (h : FullyLicensed W system use recognizer consequence) :
    W.SystemUse system use := by
  exact h.left

theorem full_license_requires_authority_license
    {system : W.SymbolicSystem}
    {use : W.SymbolicUse}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (h : FullyLicensed W system use recognizer consequence) :
    W.AuthorityLicensed use recognizer := by
  exact h.right.left

theorem full_license_requires_policy_license
    {system : W.SymbolicSystem}
    {use : W.SymbolicUse}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (h : FullyLicensed W system use recognizer consequence) :
    W.PolicyLicensed use consequence := by
  exact h.right.right

theorem no_system_use_blocks_full_license
    {system : W.SymbolicSystem}
    {use : W.SymbolicUse}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (hnot : Not (W.SystemUse system use)) :
    Not (FullyLicensed W system use recognizer consequence) := by
  intro hlicensed
  exact hnot hlicensed.left

theorem no_authority_blocks_full_license
    {system : W.SymbolicSystem}
    {use : W.SymbolicUse}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (hnot : Not (W.AuthorityLicensed use recognizer)) :
    Not (FullyLicensed W system use recognizer consequence) := by
  intro hlicensed
  exact hnot hlicensed.right.left

theorem no_policy_blocks_full_license
    {system : W.SymbolicSystem}
    {use : W.SymbolicUse}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (hnot : Not (W.PolicyLicensed use consequence)) :
    Not (FullyLicensed W system use recognizer consequence) := by
  intro hlicensed
  exact hnot hlicensed.right.right

theorem drawn_without_system_use_is_fully_unauthorized
    {system : W.SymbolicSystem}
    {use : W.SymbolicUse}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (hdrawn : W.ConsequenceDrawn use consequence)
    (hnot : Not (W.SystemUse system use)) :
    FullyUnauthorized system use recognizer consequence := by
  exact And.intro hdrawn (no_system_use_blocks_full_license hnot)

theorem drawn_without_authority_is_fully_unauthorized
    {system : W.SymbolicSystem}
    {use : W.SymbolicUse}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (hdrawn : W.ConsequenceDrawn use consequence)
    (hnot : Not (W.AuthorityLicensed use recognizer)) :
    FullyUnauthorized system use recognizer consequence := by
  exact And.intro hdrawn (no_authority_blocks_full_license hnot)

theorem drawn_without_policy_is_fully_unauthorized
    {system : W.SymbolicSystem}
    {use : W.SymbolicUse}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (hdrawn : W.ConsequenceDrawn use consequence)
    (hnot : Not (W.PolicyLicensed use consequence)) :
    FullyUnauthorized system use recognizer consequence := by
  exact And.intro hdrawn (no_policy_blocks_full_license hnot)

theorem full_unauthorized_has_drawn_unlicensed
    {system : W.SymbolicSystem}
    {use : W.SymbolicUse}
    {recognizer : W.Recognizer}
    {consequence : W.Consequence}
    (h : FullyUnauthorized system use recognizer consequence) :
    W.ConsequenceDrawn use consequence /\
      Not (FullyLicensed W system use recognizer consequence) := by
  exact h

end IntegratedWorld

end FSST
