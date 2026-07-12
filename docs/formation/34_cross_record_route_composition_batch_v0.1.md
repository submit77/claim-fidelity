# Cross-Record Route Composition Batch v0.1

```yaml
status: cross_record_composition_completed
date: 2026-05-07
claim_ceiling: cross_record_route_schema_and_formal_slice
production_runtime_claim: false
```

## 1. Purpose

Milestone 1K established route-level standing inside a single compiler record.

Milestone 1O tests the next composition surface:

```text
record A licenses consequence X
X becomes an input, premise, or use in record B
```

The question is not whether A and B each validate separately. The question is:

```text
What must survive across the transition for downstream use to remain licensed?
```

## 2. Schema Pressure

The v0.3 schema could name upstream and downstream links, but it could not type
the route between them.

This pass adds a v0.4 candidate:

```text
docs/schemas/fsst_compiler_record_v0.4.schema.json
```

and optional base-schema support for:

```text
chain.cross_record_routes[*]
```

Each route records:

```text
upstream_record_id
upstream_consequence
downstream_record_id
downstream_use
route_status
metadata_required
metadata_preserved
metadata_lost
composition_basis
blocked_by
```

## 3. Batch Records

Positive batch:

```text
docs/formation/compiler_records/batch_trials/1o_cross_record_route_composition_records_v0.1.json
```

Routes tested:

```text
RAE Pilot 002 protocol-writing consequence
  -> future CDP protocol-drafting use

CDP source-selection fit-routing consequence
  -> future Workstream B pilot-design use
```

Both pass because they preserve:

```text
scope
confidence
standing
blocked consequences
```

Refusal fixture:

```text
docs/formation/compiler_records/refusal_fixtures/1o_cross_record_route_overreach_fixtures_v0.1.json
```

The fixture intentionally routes a drafting consequence into collection while
losing required metadata.

Warnings produced:

```text
unresolved recognizer in licensed route
recognizer-blocked consequence
missing required metadata
lost required metadata
unrestricted license with metadata_lost
stripped scope metadata
scope lost during transmission
```

## 4. Validator Result

The regression harness now includes 1O positive and refusal checks:

```text
positive_1o_cross_record_routes
warning_1o_cross_record_overreach_refusals
```

Result:

```text
Summary: checks=9 failures=0
```

## 5. Formalization Result

The batch forced the next Lean slice:

```text
formal/lean/Core/CrossRecordRoute.lean
```

Generated AXLE bundle:

```text
formal/lean/Bundles/CrossRecordRouteStandalone.lean
```

Core predicate:

```text
CrossRecordLicensed(route) :=
  RouteLicensed(route.upstream)
  and RouteLicensed(route.downstream)
  and FeedsDownstream(route.upstream, route.downstream)
  and MetadataPreserved(route.upstream, route.downstream)
```

Sharp theorems:

```text
upstream_license_does_not_suffice_without_downstream_license
route_licenses_do_not_suffice_without_feed
route_licenses_do_not_suffice_without_metadata
downstream_drawn_without_metadata_is_cross_record_unauthorized
```

## 6. Formal Gate

Command:

```text
python scripts/run_formal_verification_checks.py
```

Result:

```text
PASS lake build
PASS compiler record checks
PASS bundle drift check RouteLicensed
PASS bundle drift check CrossRecordRoute
PASS AXLE check RouteLicensed bundle
PASS AXLE verify RouteLicensed bundle
PASS AXLE check CrossRecordRoute bundle
PASS AXLE verify CrossRecordRoute bundle

Summary: checks=8 failures=0
```

This recorded formal-gate result predates the later theorem-target correction.
At the time, `PASS lake build` checked the then-default Lake surface; the
current gate additionally checks `Theorems`, local generated bundles, and repo
integrity inventory.

## 7. Main Finding

Cross-record licensing is not just route licensing repeated twice.

The new invariant is:

```text
upstream license
+ downstream license
+ actual feed relation
+ preserved metadata
= cross-record license
```

If required metadata is stripped, a downstream consequence can be unauthorized
even when the upstream record had a valid licensed consequence.

## 8. Claim Ceiling

This pass licenses:

```text
v0.4 cross-record route schema candidate
positive cross-record route records
cross-record overreach refusal fixture
validator checks for required metadata preservation
AXLE-checked CrossRecordRoute Lean slice
```

It does not license:

```text
production compiler/runtime
automatic cross-record extraction
domain authority adjudication
final metadata taxonomy
arbitrary-length chain composition
```

## 9. Next Pressure

The next natural target is:

```text
Milestone 1P:
N-Step Chain License And Metadata Taxonomy
```

Question:

```text
What metadata classes are necessary across arbitrary-length symbolic pipelines,
and when does loss of each class block downstream consequence?
```
