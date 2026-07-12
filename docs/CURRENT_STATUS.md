# Current status

**Verified:** 2026-07-11  
**Status:** experimental research infrastructure  
**Production claim:** false

The public artifact is named **Claim Fidelity**. Its Lean namespace and historical compiler
records retain the internal `FSST` identifier to preserve traceability to the private research
lineage from which this extraction was made.

The Lake package is named `Theorems` to match the existing umbrella module imported by bundled
environment checkers; `Theorems.lean` transitively imports the full `Core` and theorem surface.

## Current verification surface

The repository now has a buildable Lean 4 project under `formal/lean/` with default `Core` and `Theorems` targets. The current local gate is:

```text
python scripts/run_formal_verification_checks.py --skip-axle
```

The current gate passes all eight top-level local checks:

- Lean build: 32 jobs completed;
- compiler-record harness: 9 expected outcomes, 0 harness failures;
- claim-gap demo: schema-valid artifact refused at the claim layer;
- repository-integrity audit: 6 checks, 0 failures;
- two generated-bundle drift checks;
- two direct Lean checks of generated bundles.

The canonical tracked Lean surface contains 32 files and 148 theorem declaration lines. The audited surface contains no `sorry` tokens or explicit `axiom` declarations. Several files emit unused-variable linter warnings.

## Superseded statements

Some chronological formation documents accurately describe earlier states in which the repository lacked a Lake scaffold, theorem modules were outside the default build target, or verification covered a narrower surface. Those statements are historical and must not be treated as current status.

In particular, a buildability concern preserved in the private chronological provenance was subsequently addressed by the work recorded in:

- `docs/formation/31_route_licensed_axle_result_v0.1.md`;
- `docs/formation/32_lean_project_import_architecture_v0.1.md`;
- `docs/formation/33_formal_verification_pipeline_hardening_v0.1.md`;
- `docs/formation/36_repo_integrity_sweep_v0.1.md`.

## Strongest implemented result

The strongest engineering surface is not a general theory claim. It is the combination of:

1. formal predicates for scope, standing, consequence licensing, and cross-record metadata preservation;
2. a validator for records carrying those fields;
3. fixtures that deliberately attempt prohibited promotions and routes;
4. a regression harness that expects those attempts to be refused or warned.

This makes the repository useful as a seed for empirical work on whether formal or schema-valid artifacts remain faithful to the claims and consequences assigned to them.

## Claim ceiling

The current project may be described as a checked formal and executable schema prototype. It may not be described as:

- empirical confirmation of FSST;
- proof that the formal primitives are necessary or sufficient in real systems;
- a complete formalization;
- a production runtime;
- evidence that formal validity guarantees semantic or task fidelity.

## Known residual risks

- Many Lean results are direct consequences of fields stipulated in structures.
- The project does not yet have external human review or adoption evidence.
- Historical machine-local path prefixes have been normalized to `<workspace>` in this public extraction. Some records still name artifacts in sibling projects as provenance; those references are descriptive and are not required by the local verification gate.
- The optional AXLE integration is not self-contained in this repository.
- The public extraction is licensed under Apache-2.0; this does not make private provenance or sibling repositories part of the release.
- Historical documents vary in status and should be read chronologically, not as a single current specification.
