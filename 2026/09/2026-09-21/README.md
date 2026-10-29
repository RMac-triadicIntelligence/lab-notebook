# 2026-09-21 — Raised Not Rented v0.13 and The Commons sandbox archive

**Worked on:** rnr v0.13 ("Release and the Standing Lesson"), its independent repack run, and three versions of The Commons HTML sandbox archive.

## What was tested
- v0.13: five arms (A no declaration, B declare, C declare + release, D shuffled release, E lesson erased), two fresh 32-seed blocks. (`1127_rnr_v0_13_revised/rnr_v0_13/RESULTS.md`)
- Commons sandboxes: v1.0/v2.0 (old sampler) against v1.1/v2.1 (repaired), checked headlessly against a known plane. (`1156_commons_archive_sandbox_review/commons_archive/SANDBOX_REVIEW.md`)

## Findings
- **Held:** contracts clean in both blocks. A standing warning roughly halves descendant crossings through declared gates (6.13 → 3.31; 6.34 → 3.34). Erasing it restores baseline exactly. Release leaves descendants identical to B. (RESULTS.md) The report itself calls this "close to a contract check, not a finding," because the warning is a programmed repulsion.
- **Failed:** the forgiveness row was not accepted. The ordering control D fails in block 2. P2 moved, but the report attributes that to calendar timing, not forgiveness. (RESULTS.md; `1700_…/independent_repack_run/COMPARISON_REPORT.md`)
- **Retracted:** the 11:27 revision withdraws two claims made at 11:23: that this was a reproduction of v0.6, and that v0.13 dissolves the v0.11/v0.12 self-penalty finding. (COMPARISON_REPORT.md, compare `1123_…/RESULTS.md`)
- **Held:** the old sampler defect is confirmed (max error 0.30). The repaired samplers recover the slope to Float32 precision. (SANDBOX_REVIEW.md)
- **Open:** a P1 metric that doesn't saturate. The v0.11/v0.12 code was never audited.

## Labels
- **verified:** the 2026-10-29 rerun (`1127_…/rerun_2026-10-29/`) reproduced summary.json and the row files byte-for-byte.
- **failed:** the forgiveness row.
- **draft:** everything else.

## Caveats
- The rerun used the same seeds only; it is not fresh-seed evidence.
- The 17:00 repack omits 17 files listed in its SHA256SUMS by design.
- No published sandbox URL or browser render was checked.
