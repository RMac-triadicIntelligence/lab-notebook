# 2026-10-26 — agent-welcome battery v1 results, and probes from the permission-receipts draft

**Worked on:** the agent-welcome v1 verifier, which checks signed shopping-agent receipts with a price cap, against a preregistered acceptance list. Also extra probes taken from `draft-izmaylov-agent-permission-receipts-01` that the battery does not test. (`agent-welcome-vs-apr/probes.py` docstring)

## What was tested
- 15 cases (C01–C15): valid path, backdated expiry, replay, cart swap, tampering and others. Each must end with the exact preregistered decision and reason. (`agent-welcome-battery-results/ACCEPTANCE.md`)
- 8 probes (P1–P8), recording what agent-welcome v0.1 does today. (`agent-welcome-vs-apr/probes_out.json`)

## Findings
- **Held:** OVERALL PASS, 15 of 15 cases, each with the exact decision and reason. Two runs wrote byte-identical `results.json` (sha `d5139a41…3438`). (`agent-welcome-battery-results/RECEIPT.md`)
- **Disclosed failure:** the first run failed C15 because of a harness bug (a receipt built for the wrong cart). Only the harness line was fixed. The acceptance list and verifier were untouched. (RECEIPT.md)
- **Open, probe gaps** (behaviour outside the battery, from `probes_out.json`):
  - three receipts, each under its own cap, are all accepted, with no running total (P1);
  - a rolled-back log accepts a replay (P2);
  - the same receipt is accepted against two separate logs (P3);
  - no cancellation record exists (P4);
  - a small-order-key signature verifies (P5);
  - an unknown field is accepted (P8).
- Malleable-S signatures are rejected (P6), and an overlong lifetime is refused (P7).

## Labels
- **verified:** the byte-identical double run.
- **failed:** the first-run C15 harness bug, now fixed and disclosed.
- **draft:** the probe interpretation. These are recorded behaviours, not preregistered verdicts.

## Caveats
- Not externally witnessed. (RECEIPT.md)
- The runs are dated 2026-10-15 in RECEIPT.md; the folder date comes from the source folder.
- The probes import a local agent-welcome copy that is not in this folder.
