#!/usr/bin/env python3
"""Generate an FSST compiler-record scaffold without doing the analysis.

The generator fills repeatable template structure and forces the productive-
friction fields to exist: scope, distributed standing, blocked consequences,
claim ceiling, review metadata, and validation metadata. It intentionally
leaves analysis fields marked with TODO text.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO_ROOT / "docs" / "schemas" / "fsst_compiler_record_v0.2.schema.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "formation" / "compiler_records" / "drafts"
VALIDATOR = REPO_ROOT / "scripts" / "validate_compiler_records.py"


ARTIFACT_TYPES = [
    "governance_doc",
    "runtime_packet",
    "formalization_target",
    "normal_form",
    "reflexive_audit",
    "admission_gate",
    "grounding_doc",
    "roadmap_or_state",
]

SOURCE_STATUSES = [
    "canonical",
    "active_candidate",
    "runtime_design_candidate",
    "checked_slice",
    "draft",
    "unknown",
]


def todo(label: str) -> str:
    return f"TODO: {label}"


def default_record(args: argparse.Namespace) -> dict[str, Any]:
    source_path = args.source_path.as_posix()
    today = date.today().isoformat()
    record_id = args.record_id

    return {
        "record_id": record_id,
        "record_version": "fsst_compiler_record_v0.1",
        "source": {
            "repo": args.source_repo,
            "artifact": args.source_artifact,
            "path": source_path,
            "artifact_type": args.artifact_type,
            "source_status": args.source_status,
        },
        "symbolic_system": {
            "system_name": args.system_name or todo("name the symbolic system"),
            "system_type": todo("classify the symbolic system"),
            "boundary": todo("state what is inside vs outside the system"),
        },
        "carrier": {
            "carrier_kind": todo("name the carrier kind"),
            "carrier_state": todo("describe the current carrier state"),
            "carrier_state_space": todo("describe the distinctions the carrier can bear"),
            "maintainer": todo("name what maintains the carrier"),
        },
        "use_episode": {
            "use": todo("describe the use episode"),
            "actor_context": todo("state who/what is using it and under what context"),
            "inference_drawn": todo("state the inference actually drawn"),
            "inference_type": todo("classify the inference type"),
            "non_inferences": [
                "TODO: name at least one inference this record does not license"
            ],
        },
        "binding": {
            "binding_target": todo("state what the carrier binds to"),
            "binding_basis": ["TODO: referential / operational / codebook / frame-relative / normative / indexical"],
            "binding_mechanism": ["TODO: institutional / causal / conventional / computational / ecological"],
            "claimed_mode": todo("state the source/domain claimed mode"),
            "operative_mode": todo("state the observed operative mode"),
        },
        "validity": {
            "validity_criterion": todo("state the mode-specific validity criterion"),
            "validity_status": "unassessed",
            "validity_evidence": todo("cite evidence for validity status"),
            "confidence": todo("bound confidence"),
            "uncertainty": todo("state remaining uncertainty"),
        },
        "scope": {
            "scope_conditions": todo("state valid scope conditions"),
            "scope_status": "unknown",
            "scope_preserved": [todo("name preserved scope metadata")],
            "scope_lost": [todo("name lost scope metadata, or say none")],
            "prohibited_scope_extensions": [
                "TODO: name at least one prohibited extension"
            ],
        },
        "recognition_authority": {
            "recognizers": [todo("name recognizer")],
            "recognizer_standing": todo("state recognizer standing"),
            "authority_source": todo("state authority source"),
            "uptake_path": todo("state uptake path"),
            "distributed_standing": [
                {
                    "recognizer": todo("name standing-bearing recognizer"),
                    "standing_scope": todo("state what this recognizer has standing to do"),
                    "standing_basis": todo("state basis for that standing"),
                }
            ],
            "recognition_relation": [todo("decode / execute / comply / apply / enforce")],
            "response_eligibility": [todo("name eligible responses")],
        },
        "policy_license": {
            "attempted_consequence": todo("state attempted consequence"),
            "action_policy": todo("state policy controlling the consequence"),
            "licensed_consequence": todo("state what is actually licensed"),
            "license_basis": todo("state basis for license"),
            "consequence_status": "unknown",
            "all_or_refuse_policy": False,
            "blocked_consequences": [
                "TODO: name at least one blocked consequence"
            ],
        },
        "transmission": {
            "transmission_path": todo("state transmission path"),
            "metadata_preserved": [todo("name preserved metadata")],
            "metadata_lost": [todo("name lost metadata, or say none")],
        },
        "chain": {
            "upstream_links": [todo("name upstream link")],
            "downstream_links": [todo("name downstream link")],
            "chain_license_status": "unknown",
            "unlicensed_links": [todo("name unlicensed link, or say none")],
        },
        "verdict": {
            "verdict": "draft_scaffold",
            "claim_ceiling": args.claim_ceiling or todo("state claim ceiling"),
            "next_check": todo("state the next check required before use"),
        },
        "validation": {
            "record_validation_status": "not_validated",
            "validated_by": "not yet validated",
            "validated_at": today,
            "schema_version": "fsst_compiler_record_v0.2",
        },
        "review": {
            "cold_review_status": "pending",
            "promotion_authority": todo("state who can promote this record, if anyone"),
            "operator_instruction_reference": args.operator_instruction_reference
            or todo("state operator instruction reference, or none"),
        },
        "reflexive_pressure": {
            "self_application": False,
            "composition_pressure": "weak",
            "new_field_pressure": [],
            "notes": "Draft scaffold. TODO markers must be resolved before relying on this record.",
        },
    }


def safe_name(record_id: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in record_id).strip("_")


def run_validator(path: Path, schema: Path, strict: bool) -> int:
    cmd = [
        sys.executable,
        str(VALIDATOR),
        str(path),
        "--schema",
        str(schema),
    ]
    if strict:
        cmd.append("--fail-on-warnings")
    completed = subprocess.run(cmd, check=False)
    return completed.returncode


def has_todo(value: Any) -> bool:
    if isinstance(value, str):
        return "todo:" in value.lower()
    if isinstance(value, list):
        return any(has_todo(item) for item in value)
    if isinstance(value, dict):
        return any(has_todo(item) for item in value.values())
    return False


def friction_findings(record: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if has_todo(record):
        findings.append("record contains unresolved TODO markers")

    claim_ceiling = record["verdict"]["claim_ceiling"].strip().lower()
    if not claim_ceiling or claim_ceiling.startswith("todo:"):
        findings.append("verdict.claim_ceiling must be authored")

    blocked = record["policy_license"]["blocked_consequences"]
    if not blocked or any(str(item).strip().lower().startswith("todo:") for item in blocked):
        findings.append("policy_license.blocked_consequences must name at least one real blocked consequence")

    prohibited = record["scope"]["prohibited_scope_extensions"]
    if not prohibited or any(str(item).strip().lower().startswith("todo:") for item in prohibited):
        findings.append("scope.prohibited_scope_extensions must name at least one real prohibited extension")

    scope_conditions = record["scope"]["scope_conditions"].strip().lower()
    if not scope_conditions or scope_conditions.startswith("todo:"):
        findings.append("scope.scope_conditions must be authored")

    for idx, standing in enumerate(record["recognition_authority"]["distributed_standing"]):
        for field in ("recognizer", "standing_scope", "standing_basis"):
            value = str(standing.get(field, "")).strip().lower()
            if not value or value.startswith("todo:"):
                findings.append(f"distributed_standing[{idx}].{field} must be authored")

    non_inferences = record["use_episode"]["non_inferences"]
    if not non_inferences or any(str(item).strip().lower().startswith("todo:") for item in non_inferences):
        findings.append("use_episode.non_inferences must name at least one real non-inference")

    consequence = record["policy_license"]["licensed_consequence"].strip().lower()
    if not consequence or consequence.startswith("todo:"):
        findings.append("policy_license.licensed_consequence must be authored")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record-id", required=True, help="Stable compiler record id")
    parser.add_argument("--source-path", required=True, type=Path, help="Source artifact path")
    parser.add_argument("--source-repo", required=True, help="Source repo name")
    parser.add_argument("--source-artifact", required=True, help="Human-readable artifact name")
    parser.add_argument("--artifact-type", required=True, choices=ARTIFACT_TYPES)
    parser.add_argument("--source-status", default="draft", choices=SOURCE_STATUSES)
    parser.add_argument("--system-name", default="", help="Optional symbolic system name")
    parser.add_argument("--claim-ceiling", default="", help="Optional claim ceiling")
    parser.add_argument(
        "--operator-instruction-reference",
        default="",
        help="Optional operator instruction reference",
    )
    parser.add_argument("--output", type=Path, help="Output JSON path")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--validate", action="store_true", help="Run validator after writing")
    parser.add_argument(
        "--finalize",
        action="store_true",
        help="Refuse unresolved TODO/friction fields before writing.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="When validating, fail on guardrail warnings too.",
    )
    args = parser.parse_args()

    output = args.output
    if output is None:
        output = DEFAULT_OUTPUT_DIR / f"{safe_name(args.record_id)}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    record = default_record(args)
    if args.finalize:
        findings = friction_findings(record)
        if findings:
            print("Refusing to finalize scaffold:")
            for finding in findings:
                print(f"  - {finding}")
            return 2

    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote scaffold: {output}")
    print("Claim ceiling:", record["verdict"]["claim_ceiling"])
    print("Blocked consequences:", "; ".join(record["policy_license"]["blocked_consequences"]))
    print("Distributed standing entries:", len(record["recognition_authority"]["distributed_standing"]))

    if args.validate:
        sys.stdout.flush()
        return run_validator(output, args.schema, args.strict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
