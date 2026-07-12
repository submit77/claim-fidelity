# Route Licensed AXLE Result v0.1

```yaml
status: checked_formal_slice
date: 2026-05-07
source_file: formal/lean/Core/RouteLicensed.lean
claim_ceiling: route_level_license_slice
domain_claim: false
production_runtime_claim: false
```

## 1. Purpose

Milestone 1K produced the route-level standing invariant:

```text
a consequence is licensed only if its recognizer chain has standing for that
specific consequence
```

This slice formalizes that pressure.

The new predicate is:

```text
ConsequenceStanding use recognizer consequence
```

The route predicate is:

```text
RouteLicensed(route) :=
  SystemUse(route.system, route.use)
  and PolicyLicensed(route.use, route.consequence)
  and for every recognizer in route.recognizer_chain:
    AuthorityLicensed(route.use, recognizer)
    and ConsequenceStanding(route.use, recognizer, route.consequence)
```

This prevents a laundering path discovered by the compiler records:

```text
authority license holds in general
policy license holds for a consequence
but the recognizer's standing does not cover that consequence
```

## 2. Module Shape

The durable module is:

```text
formal/lean/Core/RouteLicensed.lean
```

It imports:

```lean
import Core.IntegratedLicense
```

This is the first FSST slice where module composition is no longer only an
architectural preference. The import is earned by the 1K route-level records.

At the time of initial AXLE validation, the repo-local module architecture was
not yet checked. AXLE validation was therefore run against a flattened
standalone bundle:

```text
formal/lean/Bundles/RouteLicensedStandalone.lean
```

The flattened bundle contains:

```text
IntegratedLicense.lean
RouteLicensed.lean with the local import removed
```

That initial check validated the proof surface while preserving the then-current
non-claim:

```text
repo-local Lean import architecture is not yet solved
```

The local module architecture has since been installed and checked with Lake.
`formal/lean/Core/RouteLicensed.lean` now builds through the imported module
surface. The first recorded Lake result was:

```text
lake build
```

Result:

```text
Build completed successfully (25 jobs).
```

That recorded run checked the then-default Core target surface. A later sweep
made `Theorems` a default target and expanded the formal gate with repo
inventory and standalone-bundle checks.

## 3. Checked Surface

The Lean file introduces:

```text
RouteLicenseWorld
ConsequenceRoute
RouteLicensed
RouteConsequenceDrawn
RouteUnauthorized
```

Core relation:

```text
ConsequenceStanding :
  use -> recognizer -> consequence -> Prop
```

## 4. Checked Theorems

```text
route_license_requires_system_use
route_license_requires_policy_license
route_license_requires_each_authority_license
route_license_requires_each_consequence_standing
unlicensed_recognizer_breaks_route_license
no_consequence_standing_breaks_route_license
authority_and_policy_do_not_suffice_without_consequence_standing
route_license_yields_full_license_for_member
drawn_without_consequence_standing_is_route_unauthorized
route_unauthorized_has_drawn_unlicensed
```

The theorem with the sharpest consequence is:

```text
authority_and_policy_do_not_suffice_without_consequence_standing
```

It formalizes the 1K discovery:

```text
AuthorityLicensed and PolicyLicensed are not enough.
The recognizer's standing must cover the routed consequence.
```

## 5. AXLE Results

```yaml
check:
  okay: true
  request_id: a1b77f79-9089-47fc-b1fe-999211c77ee5
  environment: lean-4.29.0
  failed_declarations: 0
  lean_errors: 0
  lean_warnings: 0
  tool_errors: 0

verify:
  okay: true
  request_id: 840881e1-cb5b-432d-ae9d-dbfbc3454796
  environment: lean-4.29.0
  failed_declarations: 0
  lean_errors: 0
  lean_warnings: 0
  tool_errors: 0
```

AXLE emitted the expected wrapper warning:

```text
Imports mismatch: expected '[Mathlib]', got '[]'. Using defaults.
```

This warning is from the AXLE wrapper import environment and does not indicate
a Lean proof failure.

## 6. Claim Ceiling

This slice proves only abstract structural dependencies:

```text
1. route licensing requires system use;
2. route licensing requires policy licensing;
3. route licensing requires authority licensing for every recognizer in the route;
4. route licensing requires consequence-specific standing for every recognizer
   in the route;
5. authority and policy licensing do not suffice without consequence-specific
   standing;
6. a drawn route without consequence-specific standing is route-unauthorized.
```

It does not prove:

```text
1. that any real recognizer has standing;
2. that any real policy is valid;
3. that any real route is licensed;
4. that route-level validation is production-ready.
```

## 7. Result

The RouteLicensed slice passes AXLE check and verify as a flattened composition
bundle, and the durable imported module now builds locally under Lake.

This is the first FSST formal slice selected by compiler-record route pressure
and shaped around a recognizer chain rather than a single recognizer.
