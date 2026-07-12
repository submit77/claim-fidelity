/-
  Formal Symbolic Systems Theory - Cross-record route composition core.

  Status: candidate composition slice / stage 1 / do not promote.

  Source pressure:
    docs/formation/compiler_records/batch_trials/1o_cross_record_route_composition_records_v0.1.json

  Purpose:
    Encode the route-composition invariant discovered by the 1O batch:
    an upstream licensed route does not by itself license a downstream use.
    The downstream route must also be licensed, the upstream consequence must
    feed the downstream use, and required metadata must survive the transition.

  Non-claims:
    1. No domain-specific account of metadata adequacy.
    2. No proof that any real cross-record route is licensed.
    3. No production compiler/runtime claim.
-/

import Core.RouteLicensed

namespace FSST

universe u

structure CrossRecordWorld where
  routeWorld : RouteLicenseWorld
  FeedsDownstream :
    RouteLicenseWorld.ConsequenceRoute routeWorld ->
    RouteLicenseWorld.ConsequenceRoute routeWorld ->
    Prop
  MetadataPreserved :
    RouteLicenseWorld.ConsequenceRoute routeWorld ->
    RouteLicenseWorld.ConsequenceRoute routeWorld ->
    Prop

namespace CrossRecordWorld

variable (W : CrossRecordWorld)

structure CrossRecordRoute where
  upstream : RouteLicenseWorld.ConsequenceRoute W.routeWorld
  downstream : RouteLicenseWorld.ConsequenceRoute W.routeWorld

def CrossRecordLicensed
    (route : CrossRecordRoute W) : Prop :=
  RouteLicenseWorld.RouteLicensed W.routeWorld route.upstream /\
    RouteLicenseWorld.RouteLicensed W.routeWorld route.downstream /\
    W.FeedsDownstream route.upstream route.downstream /\
    W.MetadataPreserved route.upstream route.downstream

variable {W}

def CrossRecordConsequenceDrawn
    (route : CrossRecordRoute W) : Prop :=
  RouteLicenseWorld.RouteConsequenceDrawn route.downstream

def CrossRecordUnauthorized
    (route : CrossRecordRoute W) : Prop :=
  CrossRecordConsequenceDrawn route /\
    Not (CrossRecordLicensed W route)

theorem cross_record_license_requires_upstream_route
    {route : CrossRecordRoute W}
    (h : CrossRecordLicensed W route) :
    RouteLicenseWorld.RouteLicensed W.routeWorld route.upstream := by
  exact h.left

theorem cross_record_license_requires_downstream_route
    {route : CrossRecordRoute W}
    (h : CrossRecordLicensed W route) :
    RouteLicenseWorld.RouteLicensed W.routeWorld route.downstream := by
  exact h.right.left

theorem cross_record_license_requires_feed
    {route : CrossRecordRoute W}
    (h : CrossRecordLicensed W route) :
    W.FeedsDownstream route.upstream route.downstream := by
  exact h.right.right.left

theorem cross_record_license_requires_metadata
    {route : CrossRecordRoute W}
    (h : CrossRecordLicensed W route) :
    W.MetadataPreserved route.upstream route.downstream := by
  exact h.right.right.right

theorem upstream_license_does_not_suffice_without_downstream_license
    {route : CrossRecordRoute W}
    (_hup : RouteLicenseWorld.RouteLicensed W.routeWorld route.upstream)
    (hnot : Not (RouteLicenseWorld.RouteLicensed W.routeWorld route.downstream)) :
    Not (CrossRecordLicensed W route) := by
  intro hcross
  exact hnot (cross_record_license_requires_downstream_route hcross)

theorem route_licenses_do_not_suffice_without_feed
    {route : CrossRecordRoute W}
    (_hup : RouteLicenseWorld.RouteLicensed W.routeWorld route.upstream)
    (_hdown : RouteLicenseWorld.RouteLicensed W.routeWorld route.downstream)
    (hnot : Not (W.FeedsDownstream route.upstream route.downstream)) :
    Not (CrossRecordLicensed W route) := by
  intro hcross
  exact hnot (cross_record_license_requires_feed hcross)

theorem route_licenses_do_not_suffice_without_metadata
    {route : CrossRecordRoute W}
    (_hup : RouteLicenseWorld.RouteLicensed W.routeWorld route.upstream)
    (_hdown : RouteLicenseWorld.RouteLicensed W.routeWorld route.downstream)
    (hnot : Not (W.MetadataPreserved route.upstream route.downstream)) :
    Not (CrossRecordLicensed W route) := by
  intro hcross
  exact hnot (cross_record_license_requires_metadata hcross)

theorem downstream_drawn_without_metadata_is_cross_record_unauthorized
    {route : CrossRecordRoute W}
    (hdrawn : CrossRecordConsequenceDrawn route)
    (hnot : Not (W.MetadataPreserved route.upstream route.downstream)) :
    CrossRecordUnauthorized route := by
  exact And.intro hdrawn (by
    intro hcross
    exact hnot (cross_record_license_requires_metadata hcross))

theorem cross_record_unauthorized_has_drawn_unlicensed
    {route : CrossRecordRoute W}
    (h : CrossRecordUnauthorized route) :
    CrossRecordConsequenceDrawn route /\
      Not (CrossRecordLicensed W route) := by
  exact h

end CrossRecordWorld

end FSST
