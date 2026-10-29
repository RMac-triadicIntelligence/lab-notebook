# 2026-10-19 — Humble Seed v0.8.5–v0.8.8 candidates and the v0.8.8 release review

**Worked on:** the last revisions of the Humble Seed v0.8 line (v0.8.5, v0.8.6, v0.8.7 candidates), the v0.8.8 release pack, and an independent rerun of v0.8.8 (`humble-seed-v0_8_8-review/_review/`).

## What was tested
- `falsify_v0_8_8.py` against its frozen `DECLARED_v0_8_8.json`.
- Every earlier v0.8 harness rerun from the release copy. (`f86a/Humble_Seed_v0.8.8/RELEASE_VERIFICATION.txt`)
- The ChatGPT round 4–6 regression probes and post-freeze author probes. (`f86a/…/AUTHOR_FINDINGS_v0_8_8.md`)

## Findings
- **Reproduced:**
  - The release manifest is OK (467 files). The v0.8.8 receipt `3d3b3d1a…4224` reproduces. (RELEASE_VERIFICATION.txt)
  - The v0.8 to v0.8.4 harnesses each reproduce their recorded receipts. (RELEASE_VERIFICATION.txt)
  - The independent rerun gave the same receipt. (`_review/falsify_v0_8_8.stdout.txt`)
- **Failed (as frozen): 3 mismatches.** (`_review/falsify_v0_8_8.stdout.txt`)
  - T88 ("a symlinked path shares the organism lock") failed.
  - Mutant XE7 (lock keyed by absolute path) survived.
  - XO1's declared kill set missed T88.
- **Post-freeze author findings:** B1, a cosmetic wrong refusal reason, and B2, a lock-order refusal that is wider than needed. The author says neither changes a scored outcome. (AUTHOR_FINDINGS_v0_8_8.md)
- **Open:** the README calls v0.8.8 "candidate, not canonical… work in progress," and its license was not yet set. (`f86a/…/README.md`)

## Labels
- **verified:** the receipt reproductions.
- **failed:** T88, XE7 and XO1.
- **draft:** the candidate itself.

## Caveats
- The receipt covers statuses only. The full results JSON differs between runs, as expected for run-dependent fields.
- **Withheld:** 23 files (receipt and author-findings salts, and archives containing them). Only their hashes are in `MANIFEST.md`.
