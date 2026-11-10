# 2026-11-07 — swarm_r0 v0.2.0

**Worked on:** a local arm-A open-swarm harness from arXiv:2611.03975v1 and a relayed builder brief. Public repo: https://github.com/RMac-triadicIntelligence/swarm-r0 (published 2026-11-10, commit `597da72`). Raw ledgers are on the [v0.2.0 release](https://github.com/RMac-triadicIntelligence/swarm-r0/releases/tag/v0.2.0) as `swarm-r0-v0.2.0-full.zip` (sha256 `cece5ef3…9696dd890d`). This day folder keeps the result files only and does not recopy the ledgers. (`swarm-r0/RESULTS.md`)

## What was tested
- 12 matrix conditions (3 experiments × 2 byzantine modes × 2 alpha values), 10 runs each, plus self-test, tamper, and cross-process replay checks. (`swarm-r0/RESULTS.md`, `swarm-r0/r0_gate.json`)

## Findings
- **Failed (left failed):** R0 — the paper's direction at α = 10 (lower FPR and comparable-or-higher TPR than at α = 1) held in only 2 of 6 exp × byz pairs. (`swarm-r0/RESULTS.md`, `swarm-r0/r0_gate.json`)
- **Held (engineering only):** 120/120 runs replay, 35/35 selftest checks, 5/5 tamper cases detected. That is not evidence of paper fidelity. (`swarm-r0/RESULTS.md`)
- **Open:** OD1–OD5 unset; arms B–D, NULL, and amendments not implemented; isolation is Python class discipline, not process isolation. (`swarm-r0/RESULTS.md`)

## Labels
- **failed:** the R0 gate.
- **verified:** engineering validation receipts summarized in `RESULTS.md` and `r0_gate.json`.
- **draft:** none in this folder.

v0.1.0 was withdrawn and is not part of this day folder.
