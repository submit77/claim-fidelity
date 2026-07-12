#!/usr/bin/env python3
"""Run the local FSST formal verification gate."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = REPO_ROOT / "formal" / "lean"
GENERATOR = REPO_ROOT / "scripts" / "generate_axle_bundle.py"
COMPILER_RECORD_CHECKS = REPO_ROOT / "scripts" / "run_compiler_record_checks.py"
REPO_INTEGRITY_AUDIT = REPO_ROOT / "scripts" / "audit_repo_integrity.py"
CLAIM_GAP_DEMO = REPO_ROOT / "scripts" / "run_claim_gap_demo.py"
PROTOCOL_DEMO = REPO_ROOT / "examples" / "protocol_unit" / "run_demo.py"
AXLE = REPO_ROOT.parent / "coherent-ontology" / "tools" / "axle_lean.py"
AXLE_BUNDLES = [
    (
        "RouteLicensed",
        "Core.RouteLicensed",
        REPO_ROOT / "formal" / "lean" / "Bundles" / "RouteLicensedStandalone.lean",
    ),
    (
        "CrossRecordRoute",
        "Core.CrossRecordRoute",
        REPO_ROOT / "formal" / "lean" / "Bundles" / "CrossRecordRouteStandalone.lean",
    ),
]
ELAN_BIN = Path.home() / ".elan" / "bin"


def env_with_elan() -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{ELAN_BIN}{os.pathsep}{env.get('PATH', '')}"
    return env


def require_executable(name: str, env: dict[str, str]) -> str:
    found = shutil.which(name, path=env.get("PATH", ""))
    if found is None:
        raise SystemExit(f"required executable not found on PATH: {name}")
    return found


def run(name: str, cmd: list[str], cwd: Path, env: dict[str, str]) -> bool:
    print(f"\n=== {name}")
    print(" ".join(cmd))
    completed = subprocess.run(cmd, cwd=str(cwd), env=env, check=False)
    if completed.returncode == 0:
        print(f"PASS {name}")
        return True
    print(f"FAIL {name}: exit={completed.returncode}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-axle",
        action="store_true",
        help="Skip remote AXLE check/verify and run only local gates.",
    )
    args = parser.parse_args()

    env = env_with_elan()
    lake = require_executable("lake", env)
    lean = require_executable("lean", env)
    checks: list[tuple[str, list[str], Path]] = [
        ("lake build", [lake, "build"], LEAN_ROOT),
        (
            "compiler record checks",
            [sys.executable, str(COMPILER_RECORD_CHECKS)],
            REPO_ROOT,
        ),
        (
            "claim-gap demo",
            [sys.executable, str(CLAIM_GAP_DEMO)],
            REPO_ROOT,
        ),
        (
            "verifier-optimization protocol demo",
            [sys.executable, str(PROTOCOL_DEMO)],
            REPO_ROOT,
        ),
        (
            "repo integrity audit",
            [sys.executable, str(REPO_INTEGRITY_AUDIT)],
            REPO_ROOT,
        ),
    ]

    for label, module, bundle in AXLE_BUNDLES:
        checks.append(
            (
                f"bundle drift check {label}",
                [
                    sys.executable,
                    str(GENERATOR),
                    module,
                    str(bundle),
                    "--check",
                ],
                REPO_ROOT,
            )
        )
        checks.append(
            (
                f"local lean check generated bundle {label}",
                [lean, str(bundle)],
                # Elan resolves the pinned toolchain from formal/lean/lean-toolchain.
                # Running from the repo root works only when a global default exists.
                LEAN_ROOT,
            )
        )

    if not args.skip_axle:
        for label, _module, bundle in AXLE_BUNDLES:
            checks.extend(
                [
                    (
                        f"AXLE check {label} bundle",
                        [
                            sys.executable,
                            str(AXLE),
                            "check",
                            str(bundle),
                            "--ignore-imports",
                            "--environment",
                            "lean-4.29.0",
                            "--timeout-seconds",
                            "240",
                        ],
                        REPO_ROOT,
                    ),
                    (
                        f"AXLE verify {label} bundle",
                        [
                            sys.executable,
                            str(AXLE),
                            "verify",
                            str(bundle),
                            "--ignore-imports",
                            "--environment",
                            "lean-4.29.0",
                            "--timeout-seconds",
                            "240",
                        ],
                        REPO_ROOT,
                    ),
                ]
            )

    failures = 0
    for name, cmd, cwd in checks:
        if not run(name, cmd, cwd, env):
            failures += 1

    print(f"\nSummary: checks={len(checks)} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
