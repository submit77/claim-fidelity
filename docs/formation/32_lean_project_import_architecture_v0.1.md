# Lean Project Import Architecture v0.1

```yaml
status: local_core_lake_build_verified_then_expanded
date: 2026-05-07
claim_ceiling: lean_project_structure_with_then_default_core_build
local_build_claim: core_default_target_verified_at_time_of_run
production_formalization_claim: false
```

## 1. Purpose

The RouteLicensed slice created real pressure for module-level composition.

Before this pass, the formal slices were mostly standalone files. AXLE checking
used flattened bundles, and the durable imported module surface could drift
from the checked bundle surface.

This pass adds a minimal Lean/Lake project structure and explicit imports.

## 2. Added Project Files

```text
formal/lean/lean-toolchain
formal/lean/lakefile.lean
formal/lean/Core.lean
formal/lean/Theorems.lean
formal/lean/lake-manifest.json
```

The toolchain pins:

```text
leanprover/lean4:v4.29.0
```

matching the AXLE environment used by the checked FSST slices.

The Lake file defines two libraries:

```text
Core
Theorems
```

with `formal/lean` as the source root.

`Core.lean` and `Theorems.lean` provide the root module surfaces that Lake
expects when building those libraries.

## 3. Import Graph

The true dependency graph is now encoded as explicit imports.

Examples:

```lean
import Core.SymbolicSystem
import Core.ValidityLayers
import Core.IntegratedLicense
```

RouteLicensed remains the important composition pressure:

```lean
import Core.IntegratedLicense
```

The file then defines route-level licensing over `IntegratedWorld`.

## 4. Verification

Local `lean`, `lake`, and `elan` were available through the standard elan bin directory:

```text
~/.elan/bin
```

Elan default toolchain:

```text
leanprover/lean4:v4.29.0
```

Verification performed from the repository-relative Lean project directory:

```text
formal/lean
```

Command:

```text
lake build
```

Result at the time:

```text
Build completed successfully (25 jobs).
```

That run verified the then-default Lake target surface. At the time, the
`Theorems` library was defined but was not yet a default target, so theorem
modules were not included by plain `lake build`. That gap was corrected later
by making `Theorems` a default target and adding the repo-integrity audit.

The recorded build emitted only unused-variable linter warnings in
pre-existing proof files. It emitted no Lean errors for the target surface it
actually built.

AXLE verification remains valid for the RouteLicensed standalone bundle:

```text
AXLE check of formal/lean/Bundles/RouteLicensedStandalone.lean
```

Result:

```text
check: PASS
environment: lean-4.29.0
failed_declarations: 0
lean_errors: 0
lean_warnings: 0
```

Together, the then-local Lake build and AXLE checking validated the imported
Core module surface and the flattened RouteLicensed bundle proof surface. Later
verification expands the default Lake target to include theorem modules.

## 5. Claim Ceiling

This pass licenses:

```text
minimal Lean project structure
explicit import graph
successful local Lake build of the current formal/lean project
continued AXLE bundle checking
```

It does not license:

```text
complete formal project consolidation
retirement of AXLE bundles
production formalization pipeline
```

## 6. Next Check

Continue running from the repository-relative project directory:

```text
formal/lean
```

Expected command:

```text
lake build
```

If future local Lake builds fail, the failure is useful: it will expose the
next module-boundary, import-resolution, or theorem-maintenance defect.
