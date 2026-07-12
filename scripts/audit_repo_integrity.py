#!/usr/bin/env python3
"""Audit FSST repo integrity beyond the normal formal gate.

This script is intentionally broader than the regression harness. The harness
checks curated positive/negative behavior; this audit inventories coverage so
new files do not silently sit outside the verification surface.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = REPO_ROOT / "formal" / "lean"
VALIDATOR = REPO_ROOT / "scripts" / "validate_compiler_records.py"
GENERATOR = REPO_ROOT / "scripts" / "generate_axle_bundle.py"
SCHEMA_BASE = REPO_ROOT / "docs" / "schemas" / "fsst_compiler_record.schema.json"
SCHEMA_V02 = REPO_ROOT / "docs" / "schemas" / "fsst_compiler_record_v0.2.schema.json"
SCHEMA_V03 = REPO_ROOT / "docs" / "schemas" / "fsst_compiler_record_v0.3.schema.json"
SCHEMA_V04 = REPO_ROOT / "docs" / "schemas" / "fsst_compiler_record_v0.4.schema.json"


@dataclass(frozen=True)
class RecordExpectation:
    path: Path
    schema: Path
    expected_exit: int
    fail_on_warnings: bool = False


RECORD_EXPECTATIONS = [
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/1c_project_artifact_records_v0.1.json",
        SCHEMA_BASE,
        0,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/1d_runtime_artifact_records_v0.1.json",
        SCHEMA_V02,
        0,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/batch_trials/1h_small_batch_records_v0.1.json",
        SCHEMA_V02,
        0,
        True,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/batch_trials/1i_ambiguous_standing_records_v0.1.json",
        SCHEMA_V02,
        2,
        True,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/batch_trials/1j_standing_resolution_v0.3_records_v0.1.json",
        SCHEMA_V03,
        2,
        True,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/batch_trials/1k_partial_standing_restricted_license_records_v0.1.json",
        SCHEMA_V03,
        0,
        True,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/batch_trials/1o_cross_record_route_composition_records_v0.1.json",
        SCHEMA_V04,
        0,
        True,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/drafts/1f_smoke_test_scaffold_v0.1.json",
        SCHEMA_V02,
        2,
        True,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/drafts/1g_filled_scaffold_record_v0.1.json",
        SCHEMA_V02,
        0,
        True,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/refusal_fixtures/1e_schema_invalid_refusal_fixtures_v0.1.json",
        SCHEMA_V02,
        1,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/refusal_fixtures/1e_schema_valid_guardrail_refusal_fixtures_v0.1.json",
        SCHEMA_V02,
        2,
        True,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/refusal_fixtures/1k_route_overreach_guardrail_fixtures_v0.1.json",
        SCHEMA_V03,
        2,
        True,
    ),
    RecordExpectation(
        REPO_ROOT / "docs/formation/compiler_records/refusal_fixtures/1o_cross_record_route_overreach_fixtures_v0.1.json",
        SCHEMA_V04,
        2,
        True,
    ),
]


AXLE_BUNDLES = [
    (
        "Core.RouteLicensed",
        REPO_ROOT / "formal/lean/Bundles/RouteLicensedStandalone.lean",
    ),
    (
        "Core.CrossRecordRoute",
        REPO_ROOT / "formal/lean/Bundles/CrossRecordRouteStandalone.lean",
    ),
]

ELAN_BIN = Path.home() / ".elan" / "bin"


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def run(cmd: list[str], cwd: Path = REPO_ROOT) -> int:
    env = os.environ.copy()
    env["PATH"] = f"{ELAN_BIN}{os.pathsep}{env.get('PATH', '')}"
    completed = subprocess.run(cmd, cwd=str(cwd), env=env, check=False)
    return completed.returncode


def find_executable(name: str) -> str | None:
    env = os.environ.copy()
    env["PATH"] = f"{ELAN_BIN}{os.pathsep}{env.get('PATH', '')}"
    return shutil.which(name, path=env.get("PATH", ""))


def local_module_path(module: str) -> Path:
    return LEAN_ROOT.joinpath(*module.split(".")).with_suffix(".lean")


def audit_lean_roots() -> list[str]:
    failures: list[str] = []
    for root_name in ("Core", "Theorems"):
        root_file = LEAN_ROOT / f"{root_name}.lean"
        imports = {
            line.split()[1]
            for line in root_file.read_text(encoding="utf-8").splitlines()
            if line.startswith("import ")
        }
        modules = {
            f"{root_name}.{path.with_suffix('').name}"
            for path in (LEAN_ROOT / root_name).glob("*.lean")
        }
        missing = sorted(modules - imports)
        stale = sorted(imports - modules)
        for module in missing:
            failures.append(f"{root_name}.lean missing import: {module}")
        for module in stale:
            failures.append(f"{root_name}.lean stale import: {module}")

    for path in sorted(LEAN_ROOT.rglob("*.lean")):
        if ".lake" in path.parts:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not (line.startswith("import Core.") or line.startswith("import Theorems.")):
                continue
            module = line.split()[1]
            if not local_module_path(module).exists():
                failures.append(f"{rel(path)}:{lineno} imports missing module {module}")
    return failures


def audit_record_inventory() -> list[str]:
    failures: list[str] = []
    all_records = set((REPO_ROOT / "docs/formation/compiler_records").rglob("*.json"))
    expected = {item.path for item in RECORD_EXPECTATIONS}
    for path in sorted(all_records - expected):
        failures.append(f"compiler record lacks audit expectation: {rel(path)}")
    for path in sorted(expected - all_records):
        failures.append(f"compiler record expectation points to missing file: {rel(path)}")
    return failures


def audit_record_expectations() -> list[str]:
    failures: list[str] = []
    for item in RECORD_EXPECTATIONS:
        cmd = [
            sys.executable,
            str(VALIDATOR),
            str(item.path),
            "--schema",
            str(item.schema),
        ]
        if item.fail_on_warnings:
            cmd.append("--fail-on-warnings")
        code = run(cmd)
        if code != item.expected_exit:
            failures.append(
                f"{rel(item.path)} expected exit {item.expected_exit}, got {code}"
            )
    return failures


def audit_bundle_drift() -> list[str]:
    failures: list[str] = []
    lean = find_executable("lean")
    if lean is None:
        return ["required executable not found on PATH: lean"]

    for module, bundle in AXLE_BUNDLES:
        code = run(
            [
                sys.executable,
                str(GENERATOR),
                module,
                str(bundle),
                "--check",
            ]
        )
        if code != 0:
            failures.append(f"bundle drift or missing bundle: {module} -> {rel(bundle)}")
        # Resolve the repository-pinned toolchain rather than relying on a
        # machine-global Elan default.
        code = run([lean, str(bundle)], cwd=LEAN_ROOT)
        if code != 0:
            failures.append(f"generated bundle fails local lean check: {module} -> {rel(bundle)}")
    return failures


def audit_lean_reachability() -> list[str]:
    failures: list[str] = []
    allowlisted = {bundle.resolve() for _module, bundle in AXLE_BUNDLES}
    covered_roots = {LEAN_ROOT / "Core.lean", LEAN_ROOT / "Theorems.lean"}
    meta_files = {LEAN_ROOT / "lakefile.lean"}
    covered_dirs = {LEAN_ROOT / "Core", LEAN_ROOT / "Theorems"}

    for path in sorted(LEAN_ROOT.rglob("*.lean")):
        if ".lake" in path.parts:
            continue
        resolved = path.resolve()
        if resolved in {item.resolve() for item in meta_files}:
            continue
        if resolved in {item.resolve() for item in covered_roots}:
            continue
        if any(parent.resolve() in resolved.parents for parent in covered_dirs):
            continue
        if resolved in allowlisted:
            continue
        failures.append(f"Lean file outside default roots and bundle allowlist: {rel(path)}")
    return failures


def audit_json_parse() -> list[str]:
    failures: list[str] = []
    for path in sorted((REPO_ROOT / "docs").rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"invalid JSON: {rel(path)}: {exc}")
    return failures


def main() -> int:
    checks = [
        ("lean root/import coverage", audit_lean_roots),
        ("lean reachability allowlist", audit_lean_reachability),
        ("compiler record inventory", audit_record_inventory),
        ("compiler record expectations", audit_record_expectations),
        ("generated bundle drift", audit_bundle_drift),
        ("JSON parse", audit_json_parse),
    ]

    failures: list[str] = []
    for label, fn in checks:
        print(f"\n=== {label}")
        result = fn()
        if result:
            print(f"FAIL {label}: {len(result)} issue(s)")
            for issue in result:
                print(f"  - {issue}")
            failures.extend(result)
        else:
            print(f"PASS {label}")

    print(f"\nSummary: checks={len(checks)} failures={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
