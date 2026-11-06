# Publish bounds (honest limits)

This note is **not** part of `SOURCE_LOCK.json`. It restates limits already in `README.md` / `reports/REPORT.md`, and records an independent re-check done when this repository was published.

## Already in README.md
- The evidence digest is **unsigned**. Keep a copy of the published digest outside the archive if authenticity matters.
- The admission wrapper is **same-process software wiring**, not an inaccessible key boundary. Local source locks do **not** provide **OS confinement** or an independent notary.
- Reviewer mistakes are **authored / scripted fallibility** for harness calibration. They are **not** empirical persuasion findings about AI models or people.

## Work date and shipped receipt
- **Work date:** 2026-10-31 (from zip-internal file times in the intake archive; folder/work date is not a self-voucher — the Git commit time below is the publish time).
- **Shipped evidence receipt SHA-256:** `cf5a23d6951a0ce9a030a1f8ecdd402843288035098e1d75feb022c765a3b255` (also in `reports/REPORT.md` and `evidence/RECEIPT.json`).

## Independent re-run at publish prep (2026-11-06, America/Chicago)
On a separate machine (Python 3.13.5, cryptography 43.0.0 vs shipped 3.12.14 / 50.0.2):
- `SOURCE_LOCK.json` and pack `ARCHIVE_MANIFEST.sha256` verified.
- `python3 -I verify.py evidence` exited 0 on the shipped evidence.
- A fresh `run.py` + `verify.py` exited 0; substantive evidence files (`structural.json`, `mutations.json`, `single_reviews.json`, `dual_reviews.json`, `canonical_probes.json`) were **byte-identical** to the shipped set. Only `context.json` differed (runtime environment metadata), which cascades to RECEIPT / RESULTS / TABLE hashes.
- `tools/tamper_check.py` detected 5/5 deliberate corruptions.

