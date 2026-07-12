#!/usr/bin/env python3
"""Run the FSST compiler-record positive and negative local checks."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_V02 = REPO_ROOT / "docs" / "schemas" / "fsst_compiler_record_v0.2.schema.json"
SCHEMA_V03 = REPO_ROOT / "docs" / "schemas" / "fsst_compiler_record_v0.3.schema.json"
SCHEMA_V04 = REPO_ROOT / "docs" / "schemas" / "fsst_compiler_record_v0.4.schema.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_compiler_records.py"


@dataclass(frozen=True)
class Check:
    name: str
    path: Path
    expected_exit: int
    fail_on_warnings: bool = False
    schema: Path = SCHEMA_V02


CHECKS = [
    Check(
        name="positive_1d_runtime_records",
        path=REPO_ROOT / "docs" / "formation" / "compiler_records" / "1d_runtime_artifact_records_v0.1.json",
        expected_exit=0,
    ),
    Check(
        name="positive_1g_filled_scaffold",
        path=REPO_ROOT / "docs" / "formation" / "compiler_records" / "drafts" / "1g_filled_scaffold_record_v0.1.json",
        expected_exit=0,
    ),
    Check(
        name="warning_1f_unresolved_scaffold",
        path=REPO_ROOT / "docs" / "formation" / "compiler_records" / "drafts" / "1f_smoke_test_scaffold_v0.1.json",
        expected_exit=2,
        fail_on_warnings=True,
    ),
    Check(
        name="warning_1e_guardrail_refusals",
        path=REPO_ROOT / "docs" / "formation" / "compiler_records" / "refusal_fixtures" / "1e_schema_valid_guardrail_refusal_fixtures_v0.1.json",
        expected_exit=2,
        fail_on_warnings=True,
    ),
    Check(
        name="failure_1e_schema_refusals",
        path=REPO_ROOT / "docs" / "formation" / "compiler_records" / "refusal_fixtures" / "1e_schema_invalid_refusal_fixtures_v0.1.json",
        expected_exit=1,
    ),
    Check(
        name="positive_1k_partial_standing_routes",
        path=REPO_ROOT / "docs" / "formation" / "compiler_records" / "batch_trials" / "1k_partial_standing_restricted_license_records_v0.1.json",
        expected_exit=0,
        schema=SCHEMA_V03,
    ),
    Check(
        name="warning_1k_route_overreach_refusals",
        path=REPO_ROOT / "docs" / "formation" / "compiler_records" / "refusal_fixtures" / "1k_route_overreach_guardrail_fixtures_v0.1.json",
        expected_exit=2,
        fail_on_warnings=True,
        schema=SCHEMA_V03,
    ),
    Check(
        name="positive_1o_cross_record_routes",
        path=REPO_ROOT / "docs" / "formation" / "compiler_records" / "batch_trials" / "1o_cross_record_route_composition_records_v0.1.json",
        expected_exit=0,
        schema=SCHEMA_V04,
    ),
    Check(
        name="warning_1o_cross_record_overreach_refusals",
        path=REPO_ROOT / "docs" / "formation" / "compiler_records" / "refusal_fixtures" / "1o_cross_record_route_overreach_fixtures_v0.1.json",
        expected_exit=2,
        fail_on_warnings=True,
        schema=SCHEMA_V04,
    ),
]


def run_check(check: Check) -> bool:
    cmd = [
        sys.executable,
        str(VALIDATOR),
        str(check.path),
        "--schema",
        str(check.schema),
    ]
    if check.fail_on_warnings:
        cmd.append("--fail-on-warnings")

    print(f"\n=== {check.name}")
    completed = subprocess.run(cmd, check=False)
    if completed.returncode == check.expected_exit:
        print(f"PASS {check.name}: exit={completed.returncode}")
        return True

    print(
        f"FAIL {check.name}: expected exit {check.expected_exit}, "
        f"got {completed.returncode}"
    )
    return False


def main() -> int:
    failures = 0
    for check in CHECKS:
        if not run_check(check):
            failures += 1

    print(f"\nSummary: checks={len(CHECKS)} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
