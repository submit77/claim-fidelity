# Verifier-optimization protocol unit

> **Protocol demonstration—not a pilot, benchmark, or empirical result.** The artifact, atom bank, weak audit, and candidate certificates are deliberately constructed to make the proposed study mechanically inspectable. They do not estimate whether model generations exhibit this pattern, how often it occurs, whether an auditor is effective, or whether the result transfers beyond this unit.

Run from the repository root:

```text
python examples/protocol_unit/run_demo.py
```

## What the unit demonstrates

The frozen Lean artifact proves that every inhabitant of an empty finite type is flagged. That universal statement is valid. It does not license the existential claim that a flagged inhabitant exists.

Four typed atoms ship with checked Lean witnesses. A deterministic low-cost audit reads the direct conclusion but does not inspect finite cardinality or search for a nonempty witness. Its declared blind spot therefore licenses the existential atom. Four hand-authored, exhaustive certificates make the scoring and selection calculation inspectable.

The runner:

1. compiles the artifact and its positive and negative witnesses;
2. derives weak labels from the declared audit rules;
3. validates and scores every candidate against weak labels (`R`) and full witnessed labels (`R*`);
4. performs nested same-prefix best-of-N selection;
5. reports proxy lift, expected-random target-score loss, unsupported-authorization enrichment, and the proxy–target-gap diagnostic;
6. verifies that the auditor request contains no labels, scores, pressure level, pool position, selection history, or weak-audit information;
7. validates a hand-authored example response against the auditor schema.

The candidate pool is frozen in didactic order. The expected random policy is the mean of every candidate in the same prefix; no random seed is chosen to create an attractive comparison. Ties are resolved by the first candidate in the frozen pool order.

## Why the weak audit is not ground truth

The weak audit approximates a cheap predicate- and citation-matching triage heuristic: one read of the direct conclusion, maximum normalization depth one, no proof search, no finite-cardinality inspection, and no nonempty-witness search. This unit deliberately exposes one consequence of that budget. The full study must test whether such a heuristic is useful enough to be a plausible ranking signal and whether real model candidate pools contain enough variation for selection to amplify its omissions.

## Files

- `FrozenArtifact.lean` — auditor-visible definitions and original theorem.
- `FullLabelWitnesses.lean` — hidden adjudication material, excluded from the auditor request.
- `atoms.json` — typed claims, binary full labels, and named witnesses.
- `weak_audit.json` — the typed structural-linter rules and enforced resource envelope.
- `candidate.schema.json` and `candidate_pool.jsonl` — the certificate contract and four hand-authored exhaustive certificates.
- `auditor/request.json` — selection-blind auditor input contract.
- `auditor/response.schema.json` — required auditor output.
- `auditor/response.example.json` — hand-authored schema fixture, not an auditor run.
- `run_demo.py` — independent validation, scoring, and selection calculation.

## Claim boundary

- Lean checks the formal artifact and stored witnesses; it does not certify the broader research interpretation.
- The hand-authored candidate pool supplies no evidence about model behavior.
- The weak audit is deliberately incomplete and is not claimed to represent a production verifier.
- The example auditor response validates an interface; no auditor was run or evaluated.
- Best-of-N here demonstrates a calculation, not RL training, gaming, intention, or adaptive evasion.
- One constructed unit estimates neither prevalence nor effect size.
- Cross-domain relevance is motivation, not demonstrated transfer.

> **Protocol demonstration—not a pilot, benchmark, or empirical result.** Its purpose is to make the proposed experiment inspectable and falsifiable before any model-behavior claim is attempted.
