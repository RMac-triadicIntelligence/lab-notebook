# 2026-10-18 — Humble Seed v0.8.3 / v0.8.4 blind review rounds

**Worked on:** blind, falsification-first reviews of the Humble Seed v0.8.3 and v0.8.4 candidates by Grok and ChatGPT.

## What was tested
- Each candidate's `falsify_v0_8_x.py` harness against its frozen `DECLARED` predictions and mutant kill sets.
- Adversarial probes beyond the shipped tests. (`set1/…/REPORT_v0_8_3.md`, `set1/…/REPORT_v0_8_4.md`, `set1/54332739/…/REPORT.txt`, `set2/675073a9/…/REPORT.txt`)

## Findings
- **v0.8.3:**
  - The run reproduces down to the results.json bytes. 47 of 48 tests and 40 of 41 mutants matched the declaration. Both mismatches come from T26 catching the attack earlier than predicted. (54332739 REPORT.txt; REPORT_v0_8_3.md)
  - **Failed:** a second open owner session can bypass a real owner's no, erase a signature record and refresh a lifetime. Replay accepts forged timestamp and note values. (54332739 REPORT.txt)
- **v0.8.4:**
  - All 56 tests passed and all 54 mutant classifications matched. Two exact kill-set predictions missed, and the harness correctly exited 1. (675073a9 REPORT.txt; REPORT_v0_8_4.md)
  - **Failed:** probes found an owner-veto attestation bypass and two checkpoint-recovery defects. (675073a9 REPORT.txt)
- grace_window_v1: withheld, blind round open (hashes in MANIFEST).
- **Open:** the owner ledger is "not yet a reliable shared authority." (54332739 REPORT.txt)

## Labels
- **verified:** receipt reproduction across reviewers and Python versions, and the r1/r2 runs under `runs/`.
- **failed:** the probe findings above.
- **draft:** the candidates themselves.

## Caveats
- The reports describe measured behavior of each candidate, not of the architecture.
- **Withheld:** 67 files (receipt salts, author-findings salts and archives containing them), plus 77 grace_window_v1 files (blind round open) and 3 copies of `CHATGPT_review_archive_v0_8_3.zip` (nested salt files; withheld in the 2026-10-29 secret sweep). Only their hashes are in `MANIFEST.md`.
