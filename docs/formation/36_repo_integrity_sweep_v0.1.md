# Repo Integrity Sweep v0.1

```yaml
status: integrity_sweep_completed
date: 2026-05-07
claim_ceiling: verification_surface_hardening
production_formalization_claim: false
```

## 1. Trigger

The drift-coupling cleanup exposed a serious process gap:

```text
plain lake build was not checking theorem modules
```

That meant a formal theorem error could sit outside the default verification
surface while the repo still reported a passing local build.

## 2. Findings

The sweep found additional integrity gaps:

```text
v0.4 compiler-record schema temporarily inherited from the base schema,
dropping v0.2/v0.3 hardening

validate_compiler_records.py defaulted to the permissive base schema unless
callers manually selected the versioned schema

generated standalone Lean bundles were checked for drift and by AXLE, but the
local skip-AXLE path did not directly check the generated Lean files

historical docs described then-current verification results without clearly
preserving the exact target surface checked at the time
```

## 3. Repairs

Repairs applied:

```text
docs/schemas/fsst_compiler_record_v0.4.schema.json
  now inherits from v0.3 instead of the base schema

docs/schemas/fsst_compiler_record_v0.3.schema.json
  now permits v0.4 records as an inheritance base while v0.4 preserves its own const

scripts/validate_compiler_records.py
  auto-detects versioned schemas from validation.schema_version when --schema is omitted

scripts/audit_repo_integrity.py
  inventories Lean root coverage, local imports, compiler-record expectations,
  generated bundle drift, local generated-bundle Lean validity, and JSON parse

scripts/run_formal_verification_checks.py
  includes repo integrity audit and local Lean checks for generated bundles
```

## 4. Verification

Full gate:

```text
python scripts/run_formal_verification_checks.py
```

Result:

```text
PASS lake build
PASS compiler record checks
PASS repo integrity audit
PASS bundle drift check RouteLicensed
PASS local lean check generated bundle RouteLicensed
PASS bundle drift check CrossRecordRoute
PASS local lean check generated bundle CrossRecordRoute
PASS AXLE check RouteLicensed bundle
PASS AXLE verify RouteLicensed bundle
PASS AXLE check CrossRecordRoute bundle
PASS AXLE verify CrossRecordRoute bundle

Summary: checks=11 failures=0
```

Skip-AXLE local gate:

```text
python scripts/run_formal_verification_checks.py --skip-axle
```

Result:

```text
Summary: checks=7 failures=0
```

## 5. Residual Risk

The sweep improves verification coverage; it does not prove completeness of the
formalization or the compiler schema.

Known residual risks:

```text
schema-valid guardrail refusal fixtures are still checked at file-level
aggregate exit status rather than per-record expected warning counts

older Lean files still emit unused-variable warnings

future Lean files outside Core/Theorems/Bundles will fail the integrity audit
until they are intentionally rooted or allowlisted
```
