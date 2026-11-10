# 2026-11-10 — Relational Transitions v0.1 history-seat review

**Worked on:** history-seat review of Relational Transitions v0.1, received 6:23 AM America/Chicago. Public repo: https://github.com/RMac-triadicIntelligence/relational-transitions-v0.1 (published 2026-11-10, commit `c575fb9`). The package is credited to Rusty McMurray / Raised, Not Rented research, built 9 November 2026, with an unnamed builder. The review is by Grok Bot, Falsifier B (the history seat). (`relational-transitions-review/RELATIONAL_TRANSITIONS_v0_1_REVIEW_grokbot_history.md`)

## What was tested
- Manifest check, contract tests, a full scored rerun, `verify.py`, and `tools/replay.py`, plus document-only checks of the frozen-terrain control, event IDs, and refusal spending. (`relational-transitions-review/RELATIONAL_TRANSITIONS_v0_1_REVIEW_grokbot_history.md`)

## Findings
- **Held:** scored events and `results.json` were byte-identical to the shipped evidence. Headline rates matched (75.13% correct with full relationships; +28.52 points over random contact). H5 failed and was left failed. No hidden answer through grace; learned contact used fewer attempts than random. (`relational-transitions-review/RELATIONAL_TRANSITIONS_v0_1_REVIEW_grokbot_history.md`)
- **Wounding:** RT-B1 — frozen-terrain control is identical to random contact (17,280 events match once the label is stripped). (`relational-transitions-review/RELATIONAL_TRANSITIONS_v0_1_REVIEW_grokbot_history.md`)
- **Minor:** event IDs can be worked backward from public seeds; provider capacity is spent on refusal; the smoke test never reaches the changed-season world. (`relational-transitions-review/RELATIONAL_TRANSITIONS_v0_1_REVIEW_grokbot_history.md`)

The review header keeps the blindness disclosure: earlier exposure via the shared Claude conductor chat to withheld-item bodies, Claude's summaries of sealed findings, Falsifier A's reports, and the opening of `CONDUCTOR_HANDOVER.md`. That material is not treated as independently known. The sealed `batch_2001` archive was not opened.

## Labels
- **verified:** the reproduction of the scored evidence, as reported in the review.
- **failed:** hypothesis H5, left failed; the frozen-terrain control as a distinct test (RT-B1).
- **draft:** none in this folder beyond the review text itself.

This day folder keeps the review and its sha256 sidecar, not a second copy of the package.
