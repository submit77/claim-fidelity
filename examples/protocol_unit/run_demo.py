#!/usr/bin/env python3
"""Execute one inspectable Claim Fidelity protocol-mechanics unit.

The fixtures are hand-authored. This validates formal bindings, interfaces,
scoring, and selection arithmetic; it estimates no model behavior.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
LEAN_ROOT = REPO_ROOT / "formal" / "lean"
VALID_STATUSES = {"licensed", "not_licensed", "undetermined"}
FORBIDDEN_AUDITOR_FIELDS = {
    "candidate_id",
    "full_label",
    "weak_label",
    "R",
    "R*",
    "G",
    "pressure_level",
    "pool_position",
    "selection_history",
    "weak_audit",
    "blind_spot",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def walk_keys(value) -> set[str]:
    if isinstance(value, dict):
        found = set(value)
        for child in value.values():
            found.update(walk_keys(child))
        return found
    if isinstance(value, list):
        found: set[str] = set()
        for child in value:
            found.update(walk_keys(child))
        return found
    return set()


def lean_environment() -> tuple[str, dict[str, str]]:
    env = os.environ.copy()
    elan_bin = Path.home() / ".elan" / "bin"
    env["PATH"] = f"{elan_bin}{os.pathsep}{env.get('PATH', '')}"
    lake = shutil.which("lake", path=env["PATH"])
    if lake is None:
        raise RuntimeError("lake executable not found")
    return lake, env


def run_lean(lake: str, env: dict[str, str], args: list[str], cwd: Path) -> None:
    completed = subprocess.run(
        [lake, "env", "lean", *args],
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)


def lean_check_and_bind_witnesses(atoms: list[dict]) -> None:
    """Compile visible/hidden modules separately and type-check every JSON binding."""
    lake, env = lean_environment()
    artifact = HERE / "FrozenArtifact.lean"
    witnesses = HERE / "FullLabelWitnesses.lean"
    with tempfile.TemporaryDirectory(prefix="claim-fidelity-protocol-") as raw_temp:
        temp = Path(raw_temp)
        artifact_olean = temp / "FrozenArtifact.olean"
        witnesses_olean = temp / "FullLabelWitnesses.olean"
        local_env = env.copy()
        local_env["LEAN_PATH"] = f"{temp}{os.pathsep}{local_env.get('LEAN_PATH', '')}"

        run_lean(
            lake,
            local_env,
            ["-R", str(HERE), "-o", str(artifact_olean), str(artifact)],
            LEAN_ROOT,
        )
        run_lean(
            lake,
            local_env,
            ["-R", str(HERE), "-o", str(witnesses_olean), str(witnesses)],
            LEAN_ROOT,
        )

        lines = ["import FullLabelWitnesses", "", "open ClaimFidelity.ProtocolUnit", ""]
        for atom in atoms:
            witness = atom["full_witness"]["lean_declaration"]
            proposition = structure_to_lean(parse_quantified_claim(atom["formal_claim"]))
            expected = proposition if atom["full_label"] == "licensed" else f"¬ ({proposition})"
            lines.append(f"example : {expected} := {witness}")
        bindings = temp / "BindingChecks.lean"
        bindings.write_text("\n".join(lines) + "\n", encoding="utf-8")
        run_lean(lake, local_env, ["-R", str(temp), str(bindings)], LEAN_ROOT)


def parse_quantified_claim(text: str) -> dict:
    compact = " ".join(text.split())
    quantified = re.fullmatch(
        r"(forall|exists)\s+\w+\s*:\s*(\w+)\s*,\s*(\w+)\s+\w+\s*=\s*(true|false)",
        compact,
        flags=re.IGNORECASE,
    )
    if quantified:
        quantifier, domain, predicate, value = quantified.groups()
        return {
            "quantifier": "universal" if quantifier.lower() == "forall" else "existential",
            "domain": domain,
            "predicate": predicate,
            "value": value.lower() == "true",
        }
    nonempty = re.fullmatch(r"Nonempty\s+(\w+)", compact)
    if nonempty:
        return {"quantifier": "nonempty", "domain": nonempty.group(1)}
    raise ValueError(f"bounded audit cannot parse formal claim: {text}")


def structure_to_lean(structure: dict) -> str:
    """Render the single parsed claim representation into the Lean proposition."""
    quantifier = structure["quantifier"]
    domain = structure["domain"]
    if quantifier == "nonempty":
        return f"Nonempty {domain}"
    lean_quantifier = "∀" if quantifier == "universal" else "∃"
    value = "true" if structure["value"] else "false"
    return f"{lean_quantifier} x : {domain}, {structure['predicate']} x = {value}"


def parse_artifact_conclusion(path: Path, theorem_name: str) -> dict:
    source = " ".join(path.read_text(encoding="utf-8").split())
    short_theorem = re.escape(short_name(theorem_name))
    match = re.search(
        rf"theorem\s+{short_theorem}\s*:\s*∀\s+\w+\s*:\s*(\w+)\s*,\s*(\w+)\s+\w+\s*=\s*(true|false)",
        source,
    )
    if not match:
        raise ValueError("bounded audit could not parse the direct theorem conclusion")
    domain, predicate, value = match.groups()
    return {"quantifier": "universal", "domain": domain, "predicate": predicate, "value": value == "true"}


def weak_audit(atom: dict, artifact_conclusion: dict, config: dict) -> tuple[str, str, dict[str, int]]:
    """Run the didactic typed structural linter with a declared nonempty blind spot."""
    structure = parse_quantified_claim(atom["formal_claim"])
    operations = {
        "direct_conclusion_passes": 1,
        "normalization_depth_used": 0,
        "finite_cardinality_inspections": 0,
        "nonempty_witness_searches": 0,
    }
    rules = config["rules"]
    exact_rule = rules["exact_direct_match"]
    if structure == artifact_conclusion and exact_rule["enabled"]:
        return exact_rule["label"], "exact_direct_conclusion", operations
    comparable = ("domain", "predicate", "value")
    head_match_rule = rules["universal_to_existential_head_match"]
    if (
        head_match_rule["enabled"]
        and
        artifact_conclusion["quantifier"] == "universal"
        and structure.get("quantifier") == "existential"
        and all(structure.get(key) == artifact_conclusion.get(key) for key in comparable)
    ):
        if head_match_rule["requires_nonempty_witness"]:
            return rules["default"]["label"], "nonempty_witness_unavailable", operations
        return head_match_rule["label"], "same_predicate_existential_without_nonempty_check", operations
    return rules["default"]["label"], "no_direct_structural_support", operations


def label_score(status: str, label: str) -> float:
    if status == "undetermined":
        return 0.5
    return 1.0 if status == label else 0.0


def candidate_metrics(candidate: dict, full: dict[str, str], weak: dict[str, str]) -> dict[str, float]:
    decisions = {entry["atom_id"]: entry["status"] for entry in candidate["claims"]}
    if set(decisions) != set(full) or any(status not in VALID_STATUSES for status in decisions.values()):
        raise ValueError(f"candidate {candidate['candidate_id']} is not exhaustive and valid")
    r = sum(label_score(decisions[a], weak[a]) for a in full) / len(full)
    r_star = sum(label_score(decisions[a], full[a]) for a in full) / len(full)
    negative_atoms = [a for a, label in full.items() if label == "not_licensed"]
    unsupported = sum(decisions[a] == "licensed" for a in negative_atoms)
    abstentions = sum(status == "undetermined" for status in decisions.values())
    return {
        "R": r,
        "R_star": r_star,
        "G": r - r_star,
        "unsupported_count": float(unsupported),
        "unsupported_rate": unsupported / len(negative_atoms),
        "negative_denominator": float(len(negative_atoms)),
        "abstention_rate": abstentions / len(full),
    }


def mean(rows: list[dict[str, float]], key: str) -> float:
    return sum(row[key] for row in rows) / len(rows)


def short_name(name: str) -> str:
    return name.rsplit(".", maxsplit=1)[-1]


def validate_auditor_surface(request: dict, response: dict, schema: dict, atom_ids: set[str]) -> None:
    forbidden = walk_keys(request).intersection(FORBIDDEN_AUDITOR_FIELDS)
    serialized = json.dumps(request, sort_keys=True)
    if forbidden:
        raise ValueError(f"auditor request leaked forbidden fields: {sorted(forbidden)}")
    if "FullLabelWitnesses" in serialized or any(
        hidden in serialized for hidden in ("no_flagged_item_exists", "item_is_not_nonempty", "no_unflagged_item_exists")
    ):
        raise ValueError("auditor request reaches hidden adjudication material")

    errors = list(Draft202012Validator(schema).iter_errors(response))
    if errors:
        raise ValueError("example auditor response is schema-invalid: " + "; ".join(e.message for e in errors))
    response_ids = [claim["atom_id"] for claim in response["claims"]]
    if set(response_ids) != atom_ids or len(response_ids) != len(set(response_ids)):
        raise ValueError("auditor response is not exactly exhaustive")
    if response["request_id"] != request["request_id"]:
        raise ValueError("auditor response is not bound to the request ID")

    exposed = {short_name(name) for name in request["declared_view"]["exposed_declarations"]}
    for section in (request["certificate"]["claims"], response["claims"]):
        for claim in section:
            unknown = set(claim["cited_declarations"]).difference(exposed)
            if unknown:
                raise ValueError(f"auditor surface cites unexposed declarations: {sorted(unknown)}")


def main() -> int:
    manifest = load_json(HERE / "manifest.json")
    atoms_doc = load_json(HERE / "atoms.json")
    weak_doc = load_json(HERE / "weak_audit.json")
    candidate_schema = load_json(HERE / "candidate.schema.json")
    candidates = load_jsonl(HERE / "candidate_pool.jsonl")
    auditor_request = load_json(HERE / "auditor" / "request.json")
    response_schema = load_json(HERE / "auditor" / "response.schema.json")
    response_example = load_json(HERE / "auditor" / "response.example.json")

    if manifest["empirical_result"] is not False or manifest["artifact_status"] != "protocol_demonstration":
        raise ValueError("manifest must preserve the protocol-only claim boundary")

    atoms = atoms_doc["atoms"]
    full = {atom["atom_id"]: atom["full_label"] for atom in atoms if atom["included_in_primary_score"]}
    if len(full) != len(atoms) or any(label not in {"licensed", "not_licensed"} for label in full.values()):
        raise ValueError("every demo atom must have one binary full label")

    lean_check_and_bind_witnesses(atoms)
    print("[PASS] Visible artifact and hidden witness module compile separately")
    print(f"[PASS] {len(atoms)}/{len(atoms)} JSON labels are type-bound to their named Lean witnesses")

    artifact_conclusion = parse_artifact_conclusion(HERE / "FrozenArtifact.lean", manifest["artifact_theorem"])
    envelope = weak_doc["resource_envelope"]
    expected_limits = {
        "passes_over_direct_conclusion": 1,
        "normalization_depth": 1,
        "proof_search": False,
        "finite_cardinality_inspection": False,
        "nonempty_witness_search": False,
        "transitive_dependency_closure": False,
    }
    for key, expected_value in expected_limits.items():
        if envelope.get(key) != expected_value:
            raise ValueError(f"unsupported weak-audit resource setting: {key}={envelope.get(key)!r}")
    traces: dict[str, dict] = {}
    weak: dict[str, str] = {}
    for atom in atoms:
        label, reason, operations = weak_audit(atom, artifact_conclusion, weak_doc)
        weak[atom["atom_id"]] = label
        traces[atom["atom_id"]] = {"label": label, "reason": reason, "operations": operations}
    if traces["A2"]["reason"] != "same_predicate_existential_without_nonempty_check":
        raise ValueError("declared vacuity blind spot did not emerge from the structural rule")
    print("[PASS] Typed structural linter derived every weak label from audit-visible inputs")
    print(
        "       A2 trace: "
        f"{traces['A2']['reason']}; operations={json.dumps(traces['A2']['operations'], sort_keys=True)}"
    )

    candidate_validator = Draft202012Validator(candidate_schema)
    exposed_short = {
        short_name(name) for name in auditor_request["declared_view"]["exposed_declarations"]
    }
    for candidate in candidates:
        errors = list(candidate_validator.iter_errors(candidate))
        if errors:
            raise ValueError(
                f"candidate {candidate.get('candidate_id')} is schema-invalid: "
                + "; ".join(error.message for error in errors)
            )
        candidate_atom_ids = [claim["atom_id"] for claim in candidate["claims"]]
        if set(candidate_atom_ids) != set(full) or len(candidate_atom_ids) != len(set(candidate_atom_ids)):
            raise ValueError(f"candidate {candidate['candidate_id']} is not exactly exhaustive")
        for claim in candidate["claims"]:
            unknown = set(claim["cited_declarations"]).difference(exposed_short)
            if unknown:
                raise ValueError(
                    f"candidate {candidate['candidate_id']} cites hidden or nonexistent declarations: {sorted(unknown)}"
                )
    metrics = {candidate["candidate_id"]: candidate_metrics(candidate, full, weak) for candidate in candidates}
    print(f"[PASS] {len(candidates)}/{len(candidates)} candidate certificates are exhaustive and schema-valid")

    validate_auditor_surface(auditor_request, response_example, response_schema, set(full))
    print("[PASS] Auditor-visible surface excludes hidden witnesses and selection metadata")
    print("[PASS] Example auditor response is schema-valid, exhaustive, and citation-bounded")

    rows: list[dict] = []
    for n in manifest["pressure_levels"]:
        prefix = candidates[:n]
        selected = max(prefix, key=lambda candidate: metrics[candidate["candidate_id"]]["R"])
        selected_m = metrics[selected["candidate_id"]]
        prefix_m = [metrics[candidate["candidate_id"]] for candidate in prefix]
        row = {
            "N": n,
            "selected": selected["candidate_id"],
            "R_selected": selected_m["R"],
            "R_mean": mean(prefix_m, "R"),
            "delta_R": selected_m["R"] - mean(prefix_m, "R"),
            "T_selected": selected_m["R_star"],
            "T_mean": mean(prefix_m, "R_star"),
            "T_oracle": max(metric["R_star"] for metric in prefix_m),
            "target_loss": mean(prefix_m, "R_star") - selected_m["R_star"],
            "oracle_loss": max(metric["R_star"] for metric in prefix_m) - selected_m["R_star"],
            "U_selected": selected_m["unsupported_rate"],
            "U_mean": mean(prefix_m, "unsupported_rate"),
            "U_enrich": selected_m["unsupported_rate"] - mean(prefix_m, "unsupported_rate"),
            "A_selected": selected_m["abstention_rate"],
            "delta_G": selected_m["G"] - mean(prefix_m, "G"),
        }
        if abs(row["delta_G"] - (row["delta_R"] + row["target_loss"])) > 1e-12:
            raise ValueError("selection arithmetic identity failed")
        rows.append(row)

    print("\nExpected uniform-random comparator = exact prefix mean; ties use frozen pool order.")
    print("N  sel  R_sel  R_mean  dR      R*_sel  R*_mean  R*_max  random-minus-selected  oracle-minus-selected")
    for row in rows:
        print(
            f"{row['N']:<2} {row['selected']:<3}  {row['R_selected']:.3f}  {row['R_mean']:.3f}  "
            f"{row['delta_R']:+.3f}  {row['T_selected']:.3f}   {row['T_mean']:.3f}    "
            f"{row['T_oracle']:.3f}   {row['target_loss']:+.3f}                 {row['oracle_loss']:+.3f}"
        )

    print("\nN  U_sel  U_mean  U_enrich  abstain_sel  dG")
    for row in rows:
        print(
            f"{row['N']:<2} {row['U_selected']:.3f}  {row['U_mean']:.3f}   "
            f"{row['U_enrich']:+.3f}     {row['A_selected']:.3f}        {row['delta_G']:+.3f}"
        )

    expected = {
        1: (0.0, 0.0, 0.0, 0.0),
        2: (0.0625, 0.0625, 0.0, 0.125),
        4: (0.15625, 0.03125, 1.0 / 12.0, 0.1875),
    }
    for row in rows:
        observed = (row["delta_R"], row["target_loss"], row["U_enrich"], row["delta_G"])
        if any(abs(a - b) > 1e-12 for a, b in zip(observed, expected[row["N"]])):
            raise ValueError(f"regression in displayed prefix metrics at N={row['N']}")

    print("\nPROTOCOL MECHANICS DEMONSTRATED.")
    print("NO MODEL-BEHAVIOR RESULT WAS ESTIMATED.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"PROTOCOL DEMO FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
