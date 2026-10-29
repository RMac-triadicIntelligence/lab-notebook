# 2026-10-27 — Containment battery v0.1 and v0.2 with audits, and the TQNM nonlinear dwelling task battery

**Worked on:** `nonself_auth_agent_battery`, which tests whether a signer gate stops an agent from making unauthorized changes. It covers v0.1, v0.2, two reruns of each and adversarial audits. Also a matched-evidence task battery for the nonlinear dwelling model.

## What was tested
- **v0.1:** 4 claims over 128 episodes. (`containment-v0_1/run1/…/evidence/RESULTS.json`)
- **v0.2:** 14 claims over 64 episodes, under a process boundary. (`containment-v0_2/run1/…/nonself_auth_agent_battery_v0_2/evidence/RESULTS.json`, `…_v0_2/README.md`)
- **Audits:** `containment-v0_1/scratch/adversarial_probe.py`, and `containment-v0_2/scratch/adv_audit*.py` with output in `audit_findings2.json`.
- **TQNM:** FULL against FIELD_OFF and a MIN_CUE baseline on 384 held-out histories. (`tqnm-nonlinear-dwelling/zip/…/REPORT.md`)

## Findings
- **v0.1:** all 4 claims PASS as shipped. (RESULTS.json) The audit findings F1–F4 broke it. F1 was a direct balance write and F2 a runtime gate flip. The v0.2 README says v0.2 closes them. (`…_v0_2/README.md`)
- **v0.2:** all 14 claims PASS (A1–A14). Run1 and run2 match the shipped RESULTS.json byte for byte. The freeze is `e1858104…f18da`.
- **v0.2 audit, failed:** (`audit_findings2.json`)
  - **CRITICAL:** the child process can write to the package directory (agents.py, world.py, FREEZE.json).
  - **CRITICAL:** the child can scrape the parent's secret from `/proc/<ppid>/mem`.
  - **HIGH:** A13 is defeated if the anchor head is stored where the child can rewrite it.
  - **MEDIUM:** an exposed agent can forge authorized spends.
- **TQNM:** the archived state-transition effect reproduced exactly (FULL opened in 131 of 384 cases, FIELD_OFF in 3). **The task advantage failed:** FULL made 0 correct commitments, against MIN_CUE's 57. (REPORT.md)
- **Open:** OS-level sandboxing for containment (the v0.3 request).

## Labels
- **verified:** the v0.2 byte-identical reruns, and the TQNM state-effect reproduction.
- **failed:** the v0.2 audit findings, and the TQNM task-answer advantage.
- **draft:** v0.2 as a containment claim for real models.

## Caveats
- v0.2's PASS holds only for stub agents inside the shipped boundary.
- TQNM rejects only this adapter, not every decoder. (REPORT.md)
