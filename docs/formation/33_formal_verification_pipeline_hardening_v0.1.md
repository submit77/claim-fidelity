# Formal Verification Pipeline Hardening v0.1

```yaml
status: pipeline_hardening_completed
date: 2026-05-07
claim_ceiling: local_formal_verification_gate_with_generated_axle_bundle
production_formalization_claim: false
```

## 1. Purpose

Milestone 1M made the then-default Lean project surface build locally under
Lake. A later follow-up made `Theorems` a default Lake target too, closing the
gap where plain `lake build` checked Core but not theorem modules.

Milestone 1N closes the next gap:

```text
imported durable Lean modules
  must not drift from
flattened AXLE submission bundles
```

Before this pass, the RouteLicensed AXLE bundle was hand-maintained. That left
provenance debt: the Lake module and AXLE bundle could diverge silently.

## 2. Added Tooling

```text
scripts/generate_axle_bundle.py
scripts/run_formal_verification_checks.py
```

`generate_axle_bundle.py` takes a repo-local Lean module and recursively inlines
repo-local imports:

```text
Core.RouteLicensed
  imports Core.IntegratedLicense
```

Generated output:

```text
formal/lean/Bundles/RouteLicensedStandalone.lean
```

The generator supports:

```text
write mode
  regenerate the bundle from the imported module graph

check mode
  fail if the committed bundle differs from generated output
```

`run_formal_verification_checks.py` runs the current formal gate:

```text
lake build
compiler record regression harness
generated-bundle drift check
AXLE check of RouteLicensed bundle
AXLE verify of RouteLicensed bundle
AXLE check/verify of any additional generated bundles registered in the gate
```

It also prepends:

```text
~/.elan/bin
```

to the subprocess PATH, so the gate can find `lake` in local runs.

## 3. Verification Result

Command:

```text
python scripts/run_formal_verification_checks.py
```

Result recorded at this stage:

```text
PASS lake build
PASS compiler record checks
PASS bundle drift check
PASS AXLE check RouteLicensed bundle
PASS AXLE verify RouteLicensed bundle

Summary: checks=5 failures=0
```

That recorded run predates the later addition of `repo integrity audit`, local
standalone bundle checks, and `Theorems` as a default Lake target.

AXLE request ids:

```text
check:  5dcd12dd-5d54-403a-aec2-24ef6918716f
verify: a1fdbcea-05a7-4549-839e-a330dfbb4b36
```

Known warnings:

```text
Lake emits unused-variable linter warnings in older proof files.
AXLE emits the expected wrapper import warning:
  Imports mismatch: expected '[Mathlib]', got '[]'
```

Neither warning indicates proof failure.

## 4. Current Gate

The current formal gate is:

```text
1. Durable Lean modules build under Lake, including Core and Theorems.
2. Compiler records pass expected positive, warning, and refusal checks.
3. Repo integrity audit confirms Lean reachability, record inventory, bundle drift, and JSON parse.
4. Generated AXLE bundles are current with their imported module surfaces.
5. Generated standalone bundles pass local Lean checks.
6. AXLE check passes for each generated bundle.
7. AXLE verify passes for each generated bundle.
```

Follow-up correction:

```text
Theorems is now a default Lake target.
```

This matters because theorem files are the proof surface where cross-module
claims can fail even when the Core object modules build.

## 5. Claim Ceiling

This pass licenses:

```text
generated RouteLicensed AXLE bundle
bundle drift detection
single-command local formal verification gate
continued use of Lake and AXLE as complementary verification surfaces
```

It does not license:

```text
production CI
complete Lean proof library architecture
automatic generation of all possible bundles
formal proof of domain standing
production compiler/runtime
```

## 6. Next Pressure

The next natural milestone is:

```text
Milestone 1O:
Cross-Record Route Composition Batch
```

Question:

```text
When a consequence licensed in one compiler record becomes an input/use in
another record, what scope, confidence, standing, and policy metadata must
survive for the downstream route to remain licensed?
```

That batch should decide whether the next Lean target is a route-composition
predicate, metadata-preservation predicate, or chain-license predicate.
