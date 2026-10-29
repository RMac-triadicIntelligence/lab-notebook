# 2026-10-16 — Humble Seed / terrain falsification bundle, and Genesis Seed v0.1 intake

**Worked on:** a series of preregistered terrain-falsifier versions (v1.2–v1.9, built 2026-10-15 per their READMEs), poisoning and terrain-vs-SQL batteries, a root-adversary battery against Humble Seed v0.7.1, and the Genesis Seed v0.1 beta intake.

## What was tested
- Each terrain version against its own frozen `PREREG.json`.
- Each run was executed twice (`runs/*.r1`, `*.r2`). (`humble-seed-falsification-bundle/`)

## Findings
Frozen scores, from each `README.md`:
- **v1.2:** 7 PASS / 2 FAIL.
- **v1.3:** 4 PASS / 5 FAIL. The README calls it "a real negative result."
- **v1.4:** 8 PASS / 2 FAIL.
- **v1.5:** 8 PASS / 2 FAIL.
- **v1.6:** 8 PASS / 2 FAIL.
- **v1.7:** 6 PASS / 4 FAIL.
- **v1.8:** 6 PASS / 3 FAIL.
- **v1.9:** 6 PASS / 0 FAIL.

Other batteries:
- **Poisoning v0.1:** 5 PASS / 1 FAIL. A burst of 8 forged truncations a day induced 28 false proposals in v1.2 (Q2 FAIL). (`runs/terrain_poisoning_v0_1.r1/README.md`)
- **Terrain vs SQL v0.1:** 4 PASS / 1 FAIL. SQL over the same counts matches the terrain reader (.852). The advantage is the reading, not the store. (`runs/terrain_vs_sql_v0_1.r1/README.md`)
- **Root adversary:** v0.7.1 holds every row that S2 holds, and also G1b without the witness. (`runs/ra_d155b5ef.r1/RESULTS.md`)
- **Open:** rollback needs an external witness, and the unattested tail is forgeable as a record (R8). (`runs/ra_d155b5ef.r1/RESULTS.md`)
- **Genesis Seed v0.1:** an app intake only (`genesis-seed-v0_1-intake/zip/genesis-seed-v0.1/README.txt`). No results recorded.

## Labels
- **verified:** every r1/r2 pair gives the same `RECEIPT.txt`. The v1.2–v1.6 and poisoning/SQL receipts were checked here, and all match.
- **failed:** the FAIL rows above, which were kept as frozen.
- **draft:** the rest.

## Caveats
- The r1/r2 reruns are same-seed determinism checks.
- Each rule's operationalization is flagged in the READMEs as Claude's.
- The root-adversary result's G1b win comes from owner-signed checkpoints, which an SQL stack can match. (RESULTS.md)
