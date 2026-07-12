/-
  Formal Symbolic Systems Theory - Route-licensed consequence core.

  Status: candidate module-composition slice / stage 1 / do not promote.

  Source pressure:
    docs/formation/30_partial_standing_restricted_license_batch_v0.1.md

  Purpose:
    Encode the route-level invariant discovered by the 1K partial-standing
    batch: a consequence route is licensed only when every recognizer in the
    route has ordinary full license for the system/use/consequence and also
    has standing that covers that specific consequence.

    This file intentionally composes the earlier integrated license surface:

      IntegratedWorld.FullyLicensed

    The one new predicate is consequence-specific standing:

      ConsequenceStanding use recognizer consequence

  Non-claims:
    1. No domain-specific account of what grants standing.
    2. No claim that route licensing proves moral or political legitimacy.
    3. No production compiler/runtime claim.
    4. No claim that local Lean project import architecture is finalized.
-/

import Core.IntegratedLicense

namespace FSST

universe u

structure RouteLicenseWorld where
  integrated : IntegratedWorld
  ConsequenceStanding :
    integrated.SymbolicUse ->
    integrated.Recognizer ->
    integrated.Consequence ->
    Prop

namespace RouteLicenseWorld

variable (W : RouteLicenseWorld)

structure ConsequenceRoute where
  system : W.integrated.SymbolicSystem
  use : W.integrated.SymbolicUse
  consequence : W.integrated.Consequence
  recognizer_chain : List W.integrated.Recognizer

def RouteLicensed
    (route : ConsequenceRoute W) : Prop :=
  W.integrated.SystemUse route.system route.use /\
    W.integrated.PolicyLicensed route.use route.consequence /\
    forall recognizer,
      recognizer ∈ route.recognizer_chain ->
        W.integrated.AuthorityLicensed route.use recognizer /\
          W.ConsequenceStanding route.use recognizer route.consequence

variable {W}

def RouteConsequenceDrawn
    (route : ConsequenceRoute W) : Prop :=
  W.integrated.ConsequenceDrawn route.use route.consequence

def RouteUnauthorized
    (route : ConsequenceRoute W) : Prop :=
  RouteConsequenceDrawn route /\
    Not (RouteLicensed W route)

theorem route_license_requires_system_use
    {route : ConsequenceRoute W}
    (h : RouteLicensed W route) :
    W.integrated.SystemUse route.system route.use := by
  exact h.left

theorem route_license_requires_policy_license
    {route : ConsequenceRoute W}
    (h : RouteLicensed W route) :
    W.integrated.PolicyLicensed route.use route.consequence := by
  exact h.right.left

theorem route_license_requires_each_authority_license
    {route : ConsequenceRoute W}
    {recognizer : W.integrated.Recognizer}
    (h : RouteLicensed W route)
    (hmem : recognizer ∈ route.recognizer_chain) :
    W.integrated.AuthorityLicensed route.use recognizer := by
  exact (h.right.right recognizer hmem).left

theorem route_license_requires_each_consequence_standing
    {route : ConsequenceRoute W}
    {recognizer : W.integrated.Recognizer}
    (h : RouteLicensed W route)
    (hmem : recognizer ∈ route.recognizer_chain) :
    W.ConsequenceStanding route.use recognizer route.consequence := by
  exact (h.right.right recognizer hmem).right

theorem unlicensed_recognizer_breaks_route_license
    {route : ConsequenceRoute W}
    {recognizer : W.integrated.Recognizer}
    (hmem : recognizer ∈ route.recognizer_chain)
    (hnot : Not (W.integrated.AuthorityLicensed route.use recognizer)) :
    Not (RouteLicensed W route) := by
  intro hroute
  exact hnot (route_license_requires_each_authority_license hroute hmem)

theorem no_consequence_standing_breaks_route_license
    {route : ConsequenceRoute W}
    {recognizer : W.integrated.Recognizer}
    (hmem : recognizer ∈ route.recognizer_chain)
    (hnot : Not (W.ConsequenceStanding route.use recognizer route.consequence)) :
    Not (RouteLicensed W route) := by
  intro hroute
  exact hnot (route_license_requires_each_consequence_standing hroute hmem)

theorem authority_and_policy_do_not_suffice_without_consequence_standing
    {route : ConsequenceRoute W}
    {recognizer : W.integrated.Recognizer}
    (hmem : recognizer ∈ route.recognizer_chain)
    (_hauthority : W.integrated.AuthorityLicensed route.use recognizer)
    (_hpolicy : W.integrated.PolicyLicensed route.use route.consequence)
    (hnot : Not (W.ConsequenceStanding route.use recognizer route.consequence)) :
    Not (RouteLicensed W route) := by
  exact no_consequence_standing_breaks_route_license hmem hnot

theorem route_license_yields_full_license_for_member
    {route : ConsequenceRoute W}
    {recognizer : W.integrated.Recognizer}
    (h : RouteLicensed W route)
    (hmem : recognizer ∈ route.recognizer_chain) :
    IntegratedWorld.FullyLicensed
      W.integrated
      route.system
      route.use
      recognizer
      route.consequence := by
  exact And.intro
    h.left
    (And.intro
      (route_license_requires_each_authority_license h hmem)
      h.right.left)

theorem drawn_without_consequence_standing_is_route_unauthorized
    {route : ConsequenceRoute W}
    {recognizer : W.integrated.Recognizer}
    (hdrawn : RouteConsequenceDrawn route)
    (hmem : recognizer ∈ route.recognizer_chain)
    (hnot : Not (W.ConsequenceStanding route.use recognizer route.consequence)) :
    RouteUnauthorized route := by
  exact And.intro hdrawn
    (no_consequence_standing_breaks_route_license hmem hnot)

theorem route_unauthorized_has_drawn_unlicensed
    {route : ConsequenceRoute W}
    (h : RouteUnauthorized route) :
    RouteConsequenceDrawn route /\
      Not (RouteLicensed W route) := by
  exact h

end RouteLicenseWorld

end FSST
