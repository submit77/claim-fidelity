# Claim Fidelity: claim-gap demo

This demonstration isolates one failure mode relevant to AI oversight: an artifact can satisfy an accessible machine check while failing to license the consequence assigned to it.

Run from the repository root:

```text
python scripts/run_claim_gap_demo.py
```

## The case

The checked fixture is a compiler record for a cross-record route. It is intentionally:

- **schema-valid:** the artifact has the required fields and types;
- **claim-invalid:** it attempts to authorize data collection after required scope and blocked-consequence metadata have been lost;
- **authority-invalid:** the proposed route depends on a future reviewer whose standing is unresolved.

The validator therefore separates two questions:

| Layer | Question | Verdict |
| --- | --- | --- |
| Machine validity | Does the record conform to its declared schema? | Pass |
| Claim fidelity | Does the route license the attempted consequence? | Refuse |

## Claim–mechanism–control card

- **Claim:** the upstream artifact authorizes downstream data collection.
- **Mechanism:** scope restrictions and blocked consequences are stripped during composition, while an unresolved recognizer is treated as authority-bearing.
- **Probe:** compare required, preserved, and lost metadata; inspect standing along the consequence route.
- **Control:** preserve required metadata end to end and require established standing before promoting the consequence.
- **Residual risk:** the validator checks declared records. It does not establish that every relevant property of the external system was faithfully encoded in the record.

This is a worked example of the repository's claim ceiling: formal and schema checks can enforce declared invariants, but they do not automatically establish the binding between an artifact and the surrounding natural-language or deployment claim.
