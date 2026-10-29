# 2026-10-24 — Gospel package: falsification brief, P1–P5 probe reconstruction, earned-landscape protocol draft

**Worked on:** a hostile-reader brief against the Raised, Not Rented / Developmental Meaning Fork package, an executed reconstruction of the narrated probes P1–P5, and a protocol draft for "earned landscape v0.1."

## What was tested
- **Learner robustness:** whether the history-negative result depends on k=15 kNN.
- **Position leak:** whether "position" is the hidden state. (`gospel-falsification-brief/BRIEF.md`, `learner_robustness.csv`, `position_leak.txt`)
- **Probes P1–P5:** a reconstruction under a declared model. (`gospel-probes-p1-p5/FINDINGS.md`, `results/`)

## Findings
- **Failed (claim challenged):** the history-negative result is not robust to the learner. On the forward-only reverse test, logistic regression with history gets 0.9437, against kNN15's 0.6958. (BRIEF.md §1, `learner_robustness.csv`)
- **Failed (claim challenged):** position recovers the capacity measure almost exactly (R² 0.9995), so its success is the frozen identity reached by another route. (BRIEF.md §2, `position_leak.txt`)
- **Open:** eight more attacks are listed. Among them, the tilt schedule against the developmental claim is untested, confession and realization are stubs, P1–P5 are uncited, and cross-model review is not independent replication. (BRIEF.md §3–§10)
- **Probe reconstruction:** (FINDINGS.md)
  - **Held:** P1 and P4 reproduced.
  - **Partly held:** P3.
  - **Failed:** P2 as gated; dense K24 fell below the 1% coupling-detectability gate.
  - **Failed:** P5 as preregistered. It reproduces only in a post-hoc, noise-free variant.
- **Earned landscape v0.1:** "draft. Nothing has been run. No code exists yet." No results recorded. (`gospel-earned-landscape-v0_1/PROTOCOL_DRAFT.md`)

## Labels
- **verified:** the brief's kNN15 reproduces the packaged metrics exactly. The probe tests pass, 6 of 6. (`results/tests.log`)
- **failed:** P2 and P5 as preregistered, and the two challenged claims.
- **draft:** the protocol and the brief.

## Caveats
- The P1–P5 work is a reconstruction, not the original. It checks the narrated qualitative claims only and verifies none of the original numbers. (FINDINGS.md)
- The P5 match is post hoc.
