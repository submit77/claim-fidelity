#!/usr/bin/env python3
"""Run a compact demonstration of machine validity versus claim fidelity."""

from __future__ import annotations

import sys
from pathlib import Path

from validate_compiler_records import (
    as_records,
    guardrail_warnings,
    load_json,
    schema_for_record,
    validator_for,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO_ROOT
    / "docs"
    / "formation"
    / "compiler_records"
    / "refusal_fixtures"
    / "1o_cross_record_route_overreach_fixtures_v0.1.json"
)
REQUIRED_FINDINGS = {
    "consequence_routes[0] licenses through unresolved recognizer: future cold reviewer",
    "cross_record_routes[0] licensed route loses required metadata: blocked consequences, scope",
}


def main() -> int:
    records = as_records(load_json(FIXTURE))
    if len(records) != 1:
        print(f"DEMO RESULT     FAIL — expected one fixture, found {len(records)}")
        return 1

    record = records[0]
    validator = validator_for(schema_for_record(record))
    schema_errors = list(validator.iter_errors(record))
    findings = guardrail_warnings(record)
    attempted = record["policy_license"]["attempted_consequence"]

    if schema_errors:
        print("MACHINE CHECK   FAIL — fixture is not schema-valid")
        for error in schema_errors:
            print(f"  - {error.message}")
        print("DEMO RESULT     FAIL — machine/claim distinction was not isolated")
        return 1

    print("MACHINE CHECK   PASS — artifact is schema-valid")
    print(f"ATTEMPTED       {attempted}")
    print(f"CLAIM CHECK     REFUSE — {len(findings)} guardrail findings")
    for finding in findings:
        print(f"  - {finding}")
    print("CONTROL         preserve required metadata and require established standing")

    missing = REQUIRED_FINDINGS.difference(findings)
    if missing:
        print("DEMO RESULT     FAIL — expected control-relevant findings were absent")
        for finding in sorted(missing):
            print(f"  - missing: {finding}")
        return 1

    print("DEMO RESULT     PASS — validity/claim gap detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
