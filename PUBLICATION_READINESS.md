# Claim Fidelity publication readiness

Claim Fidelity is the curated public extraction of a larger private working repository,
prepared 2026-07-11 and renamed around the extraction's actual checked surface. This file
records what was done so the preparation is auditable.

Public repository: <https://github.com/submit77/claim-fidelity>

## Resolved in this extraction

- [x] **Scope:** curated subset selected (Lean project, verification/validation scripts, schemas,
  compiler-record corpus, formation documents 31–36, current-status and claim-boundary docs).
  The fuller chronological theory corpus remains private as provenance.
- [x] **License:** Apache-2.0 (`LICENSE`); citation metadata in `CITATION.cff`.
- [x] **Path normalization:** historical machine-local absolute paths in documents and audit-record
  JSONs normalized to `<workspace>`. The record JSONs are historical audit artifacts; only path
  prefixes were rewritten, no record semantics were changed, and the full verification gate was
  re-run after normalization.
- [x] **History:** fresh repository history (single release commit); no development history is exposed.
- [x] **Secret scan:** bounded pattern scan for API keys, private keys, and password assignments — clean.
- [x] **Cold-clone verification:** the extraction was cloned into a fresh directory and
  `python scripts/run_formal_verification_checks.py --skip-axle` was run from the clone after
  the reviewer-facing demo and CI additions. Result recorded below.

## Cold-clone gate result (2026-07-11)

See README "Quick verification" for the command. Result on the fresh clone:

```text
git clone <this-repo> fresh-dir && cd fresh-dir
python scripts/run_formal_verification_checks.py --skip-axle
→ Summary: checks=8 failures=0
  (lake build; compiler-record checks; claim-gap demo; repo-integrity audit;
   2× bundle drift checks; 2× direct generated-bundle Lean checks)
```

## Remaining owner options (non-blocking)

- [x] Hosted CI workflow executes the full gate and Lean 4.29's bundled `leanchecker` environment
  recheck. The repository-integrity audit separately refuses `sorry` tokens and explicit axioms.
- [ ] Lean unused-variable linter cleanup where it does not alter theorem statements.
- [ ] Contribution policy if external contributions will be accepted.

## Post-release protocol addition (2026-07-12)

The working tree adds `examples/protocol_unit/`, an explicitly non-empirical verifier-optimization protocol demonstration, and includes it in the local gate. The updated gate passes nine top-level checks with zero failures. This section records a post-v0.1.0 change; a new immutable release and cold-clone record should be created only after the addition is independently audited and published.
