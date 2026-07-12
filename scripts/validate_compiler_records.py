#!/usr/bin/env python3
"""Validate FSST compiler record JSON files.

This is a minimal validator for Milestone 1D. It checks JSON Schema
conformance and a few FSST-specific guardrails that are easier to express in
code than in schema.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - user-facing environment guard
    raise SystemExit(
        "Missing dependency: jsonschema. Install it or use the bundled workspace "
        "Python environment that includes it."
    ) from exc

try:
    from referencing import Registry, Resource
except ImportError as exc:  # pragma: no cover - user-facing environment guard
    raise SystemExit(
        "Missing dependency: referencing. Install it or use the bundled workspace "
        "Python environment that includes it."
    ) from exc


DEFAULT_SCHEMA = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "schemas"
    / "fsst_compiler_record.schema.json"
)
SCHEMA_DIR = DEFAULT_SCHEMA.parent
SCHEMA_BY_VERSION = {
    "fsst_compiler_record_v0.2": SCHEMA_DIR / "fsst_compiler_record_v0.2.schema.json",
    "fsst_compiler_record_v0.3": SCHEMA_DIR / "fsst_compiler_record_v0.3.schema.json",
    "fsst_compiler_record_v0.4": SCHEMA_DIR / "fsst_compiler_record_v0.4.schema.json",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_record_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("*.json"))


def as_records(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    raise ValueError("top-level JSON must be an object or array of objects")


def pointer(path: list[Any]) -> str:
    if not path:
        return "/"
    return "/" + "/".join(str(part) for part in path)


def contains_todo(value: Any) -> bool:
    if isinstance(value, str):
        return "todo:" in value.lower()
    if isinstance(value, list):
        return any(contains_todo(item) for item in value)
    if isinstance(value, dict):
        return any(contains_todo(item) for item in value.values())
    return False


def contains_any_term(value: Any, terms: tuple[str, ...]) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return any(term in lowered for term in terms)
    if isinstance(value, list):
        return any(contains_any_term(item, terms) for item in value)
    if isinstance(value, dict):
        return any(contains_any_term(item, terms) for item in value.values())
    return False


def standing_resolution_warnings(record: dict[str, Any]) -> list[str]:
    recognition = record.get("recognition_authority", {})
    policy = record.get("policy_license", {})
    validation = record.get("validation", {})
    schema_version = validation.get("schema_version")
    warnings: list[str] = []

    if schema_version not in {"fsst_compiler_record_v0.3", "fsst_compiler_record_v0.4"}:
        if contains_any_term(recognition, ("standing unresolved", "standing contested", "open standing", "standing question")):
            warnings.append("standing question is unresolved or contested")
        return warnings

    aggregate = recognition.get("standing_resolution_state")
    distributed = recognition.get("distributed_standing", [])
    if not isinstance(distributed, list):
        return warnings

    item_states = [
        item.get("standing_resolution_state")
        for item in distributed
        if isinstance(item, dict)
    ]
    unresolved_states = {"unresolved", "contested"}
    restricted_states = {"restricted", "unresolved", "contested"}
    has_unresolved = "unresolved" in item_states
    has_contested = "contested" in item_states
    has_restricted = any(state in restricted_states for state in item_states)
    has_established = "established" in item_states

    if aggregate in {"unresolved", "contested"}:
        warnings.append("standing resolution is unresolved or contested")

    if aggregate == "resolved" and any(state not in {"established", "out_of_scope"} for state in item_states):
        warnings.append("standing resolution aggregate says resolved but a recognizer standing is not established")
    if aggregate == "partially_resolved" and not (has_established and has_restricted):
        warnings.append("partially_resolved standing requires both established and restricted/unresolved/contested recognizers")
    if aggregate == "unresolved" and not has_unresolved:
        warnings.append("unresolved standing aggregate requires at least one unresolved recognizer")
    if aggregate == "contested" and not has_contested:
        warnings.append("contested standing aggregate requires at least one contested recognizer")

    open_questions = recognition.get("standing_open_questions", [])
    if aggregate in {"unresolved", "contested"} and not open_questions:
        warnings.append("unresolved or contested standing lacks standing_open_questions")

    consequence_status = policy.get("consequence_status")
    if aggregate in {"partially_resolved", "unresolved", "contested"} and consequence_status == "licensed":
        warnings.append("unrestricted licensed consequence with unresolved or contested standing")
    if consequence_status == "licensed_with_restriction" and has_restricted:
        blocked = policy.get("blocked_consequences", [])
        item_has_block = any(
            isinstance(item, dict)
            and (item.get("blocked_consequences") or item.get("standing_resolution_blockers"))
            for item in distributed
        )
        if not blocked or not item_has_block:
            warnings.append("restricted license with unresolved standing lacks per-recognizer blockers")

    for idx, item in enumerate(distributed):
        if not isinstance(item, dict):
            continue
        state = item.get("standing_resolution_state")
        blockers = item.get("standing_resolution_blockers", [])
        blocked = item.get("blocked_consequences", [])
        if state in {"unresolved", "contested", "restricted"} and not blockers and not blocked:
            warnings.append(f"distributed_standing[{idx}] {state} without blockers or blocked consequences")
        if state in {"unresolved", "contested", "out_of_scope"} and item.get("licensed_consequences", []):
            warnings.append(f"distributed_standing[{idx}] {state} recognizer has current licensed_consequences")

    return warnings


def consequence_route_warnings(record: dict[str, Any]) -> list[str]:
    validation = record.get("validation", {})
    if validation.get("schema_version") not in {"fsst_compiler_record_v0.3", "fsst_compiler_record_v0.4"}:
        return []

    warnings: list[str] = []
    recognition = record.get("recognition_authority", {})
    policy = record.get("policy_license", {})
    routes = policy.get("consequence_routes", [])
    consequence_status = policy.get("consequence_status")
    aggregate = recognition.get("standing_resolution_state")

    distributed = recognition.get("distributed_standing", [])
    if not isinstance(distributed, list):
        return warnings

    standing_by_recognizer = {
        item.get("recognizer"): item
        for item in distributed
        if isinstance(item, dict) and isinstance(item.get("recognizer"), str)
    }

    if consequence_status in {"licensed", "licensed_with_restriction"} and not routes:
        warnings.append("licensed consequence lacks consequence_routes")
        return warnings

    if not isinstance(routes, list):
        return warnings

    licensed_route_count = 0
    for route_idx, route in enumerate(routes):
        if not isinstance(route, dict):
            continue
        route_status = route.get("route_status")
        consequence = str(route.get("consequence", "")).strip()
        chain = route.get("recognizer_chain", [])
        if route_status in {"licensed", "licensed_with_restriction"}:
            licensed_route_count += 1
            if not isinstance(chain, list) or not chain:
                warnings.append(f"consequence_routes[{route_idx}] licensed route lacks recognizer_chain")
                continue
            for recognizer in chain:
                item = standing_by_recognizer.get(recognizer)
                if item is None:
                    warnings.append(f"consequence_routes[{route_idx}] references unknown recognizer: {recognizer}")
                    continue
                state = item.get("standing_resolution_state")
                licensed = [str(value).strip().lower() for value in item.get("licensed_consequences", [])]
                blocked = [str(value).strip().lower() for value in item.get("blocked_consequences", [])]
                consequence_key = consequence.lower()
                if route_status == "licensed" and state != "established":
                    warnings.append(
                        f"consequence_routes[{route_idx}] unrestricted license passes through non-established recognizer: {recognizer}"
                    )
                if route_status == "licensed_with_restriction" and state in {"unresolved", "contested", "out_of_scope"}:
                    warnings.append(
                        f"consequence_routes[{route_idx}] licenses through {state} recognizer: {recognizer}"
                    )
                if route_status == "licensed_with_restriction" and state == "restricted" and consequence_key not in licensed:
                    warnings.append(
                        f"consequence_routes[{route_idx}] licenses consequence not explicitly allowed by restricted recognizer: {recognizer}"
                    )
                if consequence_key in blocked:
                    warnings.append(
                        f"consequence_routes[{route_idx}] licenses consequence blocked by recognizer: {recognizer}"
                    )
        elif route_status in {"blocked", "deferred", "unlicensed"}:
            blockers = route.get("blocked_by", [])
            if not blockers:
                warnings.append(f"consequence_routes[{route_idx}] blocked/deferred route lacks blocked_by")

    if consequence_status == "licensed_with_restriction" and licensed_route_count == 0:
        warnings.append("licensed_with_restriction requires at least one licensed consequence route")
    if consequence_status == "licensed" and aggregate != "resolved":
        warnings.append("unrestricted licensed consequence requires resolved aggregate standing")

    return warnings


def cross_record_route_warnings(record: dict[str, Any]) -> list[str]:
    validation = record.get("validation", {})
    if validation.get("schema_version") != "fsst_compiler_record_v0.4":
        return []

    warnings: list[str] = []
    chain = record.get("chain", {})
    routes = chain.get("cross_record_routes", [])
    status = chain.get("chain_license_status")

    if not isinstance(routes, list):
        return warnings

    licensed_count = 0
    for route_idx, route in enumerate(routes):
        if not isinstance(route, dict):
            continue
        route_status = route.get("route_status")
        required = {str(item).strip().lower() for item in route.get("metadata_required", [])}
        preserved = {str(item).strip().lower() for item in route.get("metadata_preserved", [])}
        lost = {str(item).strip().lower() for item in route.get("metadata_lost", [])}
        missing = sorted(required - preserved)

        if route_status in {"licensed", "licensed_with_restriction"}:
            licensed_count += 1
            if missing:
                warnings.append(
                    f"cross_record_routes[{route_idx}] licensed route missing required metadata: {', '.join(missing)}"
                )
            overlapping_lost = sorted(required & lost)
            if overlapping_lost:
                warnings.append(
                    f"cross_record_routes[{route_idx}] licensed route loses required metadata: {', '.join(overlapping_lost)}"
                )
            if route_status == "licensed" and lost:
                warnings.append(
                    f"cross_record_routes[{route_idx}] unrestricted cross-record license has metadata_lost"
                )
        elif route_status in {"blocked", "deferred", "unlicensed"}:
            blockers = route.get("blocked_by", [])
            if not blockers:
                warnings.append(f"cross_record_routes[{route_idx}] blocked/deferred/unlicensed route lacks blocked_by")

    if status == "all_links_licensed" and not routes:
        warnings.append("all_links_licensed chain lacks cross_record_routes")
    if status == "all_links_licensed" and licensed_count != len(routes):
        warnings.append("all_links_licensed chain includes unlicensed cross-record route")

    return warnings


def guardrail_warnings(record: dict[str, Any]) -> list[str]:
    warnings: list[str] = []

    verdict = record.get("verdict", {})
    policy = record.get("policy_license", {})
    recognition = record.get("recognition_authority", {})
    source = record.get("source", {})
    scope = record.get("scope", {})
    chain = record.get("chain", {})
    validation = record.get("validation", {})

    if contains_todo(record):
        warnings.append("record contains unresolved TODO markers")

    warnings.extend(standing_resolution_warnings(record))
    warnings.extend(consequence_route_warnings(record))
    warnings.extend(cross_record_route_warnings(record))

    claim_ceiling = str(verdict.get("claim_ceiling", "")).strip().lower()
    if not claim_ceiling:
        warnings.append("missing non-empty verdict.claim_ceiling")

    blocked = policy.get("blocked_consequences", [])
    if isinstance(blocked, list) and not blocked:
        warnings.append("policy_license.blocked_consequences is empty")

    standing = str(recognition.get("recognizer_standing", "")).strip().lower()
    if not standing:
        warnings.append("missing non-empty recognition_authority.recognizer_standing")

    if validation.get("schema_version") in {"fsst_compiler_record_v0.2", "fsst_compiler_record_v0.3", "fsst_compiler_record_v0.4"}:
        distributed = recognition.get("distributed_standing", [])
        if not isinstance(distributed, list) or not distributed:
            warnings.append(f"{validation.get('schema_version')} record is missing recognition_authority.distributed_standing")

    status = source.get("source_status")
    consequence_status = policy.get("consequence_status")
    if status in {"draft", "unknown"} and consequence_status == "licensed":
        warnings.append("draft/unknown source should not carry unrestricted licensed consequence")

    if "truth" in claim_ceiling or "empirical" in claim_ceiling:
        warnings.append("claim ceiling appears to overstate compiler-record authority")

    attempted = str(policy.get("attempted_consequence", "")).strip().lower()
    licensed = str(policy.get("licensed_consequence", "")).strip().lower()
    promotion_terms = ("admit", "admission", "promote", "promotion", "production", "kernel")
    if consequence_status == "licensed" and any(term in attempted or term in licensed for term in promotion_terms):
        chain_status = chain.get("chain_license_status")
        if chain_status != "all_links_licensed":
            warnings.append("promotion/admission consequence is licensed while chain is not all_links_licensed")

    scope_conditions = str(scope.get("scope_conditions", "")).strip()
    prohibited = scope.get("prohibited_scope_extensions", [])
    if consequence_status in {"licensed", "licensed_with_restriction"} and not scope_conditions:
        warnings.append("licensed consequence lacks non-empty scope.scope_conditions")
    if consequence_status in {"licensed", "licensed_with_restriction"} and isinstance(prohibited, list) and not prohibited:
        warnings.append("licensed consequence lacks prohibited_scope_extensions")

    lost_metadata = record.get("transmission", {}).get("metadata_lost", [])
    if scope.get("scope_status") == "stripped" and consequence_status in {"licensed", "licensed_with_restriction"}:
        warnings.append("licensed consequence with stripped scope metadata")
    if "scope" in [str(item).strip().lower() for item in lost_metadata] and consequence_status in {"licensed", "licensed_with_restriction"}:
        warnings.append("licensed consequence after transmission lost scope metadata")

    return warnings


def schema_for_record(record: dict[str, Any]) -> Path:
    validation = record.get("validation", {})
    if isinstance(validation, dict):
        version = validation.get("schema_version")
        if isinstance(version, str) and version in SCHEMA_BY_VERSION:
            return SCHEMA_BY_VERSION[version]
    return DEFAULT_SCHEMA


def validate_file(
    path: Path,
    validator: jsonschema.Draft202012Validator | None,
    validator_cache: dict[Path, jsonschema.Draft202012Validator] | None = None,
) -> tuple[int, int]:
    try:
        value = load_json(path)
        records = as_records(value)
    except Exception as exc:
        print(f"FAIL {path}: {exc}")
        return 1, 0

    failures = 0
    warnings = 0
    for idx, record in enumerate(records):
        label = f"{path}#{idx}" if len(records) > 1 else str(path)
        active_validator = validator
        if active_validator is None:
            schema_path = schema_for_record(record)
            if validator_cache is None:
                validator_cache = {}
            active_validator = validator_cache.get(schema_path)
            if active_validator is None:
                active_validator = validator_for(schema_path)
                validator_cache[schema_path] = active_validator

        schema_errors = sorted(active_validator.iter_errors(record), key=lambda err: list(err.path))
        if schema_errors:
            failures += len(schema_errors)
            print(f"FAIL {label}: {len(schema_errors)} schema error(s)")
            for err in schema_errors:
                print(f"  {pointer(list(err.path))}: {err.message}")
            continue

        guardrail = guardrail_warnings(record)
        if guardrail:
            warnings += len(guardrail)
            print(f"WARN {label}: {len(guardrail)} guardrail warning(s)")
            for warning in guardrail:
                print(f"  - {warning}")
        else:
            print(f"OK   {label}")

    return failures, warnings


def validator_for(schema_path: Path) -> jsonschema.Draft202012Validator:
    schema = load_json(schema_path)
    schema_dir = schema_path.resolve().parent

    registry = Registry()
    for candidate in sorted(schema_dir.glob("*.schema.json")):
        candidate_schema = load_json(candidate)
        resource = Resource.from_contents(candidate_schema)
        registry = registry.with_resource(candidate.name, resource)
        schema_id = candidate_schema.get("$id")
        if isinstance(schema_id, str):
            registry = registry.with_resource(schema_id, resource)

    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema, registry=registry)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Record JSON file or directory")
    parser.add_argument(
        "--schema",
        type=Path,
        default=None,
        help=(
            "Schema path. When omitted, the validator auto-detects versioned "
            "schemas from validation.schema_version and falls back to the base schema."
        ),
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Return non-zero when guardrail warnings are emitted.",
    )
    args = parser.parse_args()

    validator = validator_for(args.schema) if args.schema is not None else None
    validator_cache: dict[Path, jsonschema.Draft202012Validator] = {}
    files = iter_record_files(args.path)
    if not files:
        print(f"No JSON files found: {args.path}")
        return 1

    failures = 0
    warnings = 0
    for file_path in files:
        file_failures, file_warnings = validate_file(file_path, validator, validator_cache)
        failures += file_failures
        warnings += file_warnings

    print(f"Summary: files={len(files)} failures={failures} warnings={warnings}")
    if failures:
        return 1
    if args.fail_on_warnings and warnings:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
