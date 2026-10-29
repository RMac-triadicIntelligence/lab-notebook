# 2026-10-10 — Persistence-as-nonclosure battery v1.0

**Worked on:** translating the four categories in Anthropic's report on unintended model actions (9 Oct 2026) into a governed-decision battery. It adds a third state, "dwell and ask," alongside stopping and working around. (`persistence-as-nonclosure-v1/persistence_as_nonclosure_battery_v1/README.md`)

## What was tested
- Eight incident scenarios (S1–S8) and three controls (C1–C3), under the full constitution and with each of six invariants (G1–G6) removed one at a time.
- Predictions were frozen in `prereg.json`. (`PAPER.md` §5)

## Findings
- **Held:** every report category is blocked under the full constitution (S1–S6 all dwell). (PAPER.md §5)
- **Held:** dwelling is not a blanket brake. Reversible work (C1) and a verified irreversible crossing (C2) both run. (PAPER.md §5)
- **Held:** a grant that is only named, and doesn't verify (C3), dwells. (PAPER.md §5)
- **Held:** each invariant is load-bearing. Removing G4 flips five scenarios. S2 needs both G2 and G4 removed before it goes through. (PAPER.md §5)
- **Held:** silently disabling G1 makes the harness FAIL, so the battery can fail things. (PAPER.md §5)
- **Open:** the hard seam of who classifies an action as reversible (S7, G5), and the "next rung." (PAPER.md §4, §8)

## Labels
- **verified:** on 2026-10-29 I reran `python3 run.py` in a scratch copy. It gave OVERALL: PASS and reproduced both the preregistration hash `e03f9d31…54d5` and the execution receipt `277f7e0d…e53d04` from PAPER.md.
- **draft:** PAPER.md (self-labelled "Draft v1.0").

## Caveats
- This is a model of a policy, not an agent that acts. (README.md)
- Results are not evidence about how any deployed model behaves. (PAPER.md abstract, §7)
- A green harness means the predicted decisions were reproduced, including the unsafe ones under ablation. Safety is the separate target verdict. (PAPER.md §5)
- The rerun is a determinism check, not new evidence.
