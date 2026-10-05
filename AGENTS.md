# Research documentation conventions

This repository supports an ongoing, LLM-assisted research project. Start with
[the project index](research/project/README.md) and its current status when doing
research or changing the experimental implementation.

The user has requested that research execution and implementation be documented
so the work can be shared, reviewed and improved. Follow
[the documentation workflow](research/project/DOCUMENTATION_WORKFLOW.md).

- Record each meaningful work step, including its purpose, actor, exact commands
  or request-record links, inputs/versions, observable outcome, validation, and
  resulting decision. Routine reads may be grouped; each inference attempt has
  its own record. Record failures and unrun planned work explicitly.
- Update the research record and affected documentation before closing a task.
  Keep a distinction among observations, interpretations, proposals and decisions.
- Preserve raw outputs, original strict-format outcomes, frozen inputs and prior
  errors. Use new versions/amendments for changes; never silently replace failed
  attempts or present a retrospective plan as a preregistration.
- Separate authoring context from evaluated input. This file, the project record,
  feedback, gold labels, witness files and prior answers do not belong in a
  reviewer packet unless a protocol explicitly studies that information access.
- Record model/provider/harness identity and actual access evidence. The user's
  Cursor Ultra/OAuth access works; do not treat a failure of one model selection
  as evidence that the subscription or OAuth route is unavailable.
- Use only the user's currently authorized scope. The current documentation
  request pauses further experiments. Documentation work alone does not resume
  them. A later explicit instruction to resume a study stage authorizes its
  routine steps without repeated per-step permission requests.
- Do not infer subagent/delegation permission from these conventions. No
  automatic background logging, experiments, outreach, or publication is implied.

These are operational records, not a claim of independent human review, complete
logging of all historical actions, OS isolation, immutable model weights, or
established research conclusions. Mark missing evidence as missing.
