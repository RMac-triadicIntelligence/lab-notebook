# grace_window_v1: pre-run notes

Written after PREREG.json was frozen (59255bee…, 2026-10-18T16:05:21Z), before any run of
run_v1.py. They don't change the PREREG; everything is scored as frozen.

## Implementation choices the PREREG doesn't fix

1. **THINNED draw.** seed = int(sha256("stream-s|thin|i|place|truncated")[:16], 16) mod 2^32,
   then `np.random.default_rng(seed).random()`. A signal if the draw is below 0.23
   (truncated) or 0.007 (ordinary).
2. **Paired CIs (B1, B4).** Each CI uses a fresh `default_rng([20261019, 5])`: the same
   10,000 × 200 resample-index matrix for both.
3. **rel_B and rel_C** are ratios of means across streams:
   (mean Δ_SPREAD − mean Δ_X) / mean Δ_SPREAD.
4. **C3 tamper.** One tuple per stream, in FOLD_MEMORY under SPREAD, chosen with
   `default_rng([20261019, s, 4])` among non-empty tuples. Its Size bin is shifted by 1
   (mod 3).
5. **C3 replay.** For LATTICE and FOLD_MEMORY in every condition, the owner re-folds from
   scratch with a new lattice. It must reproduce every tuple, plus Δ and all three
   readers' decisions and magnitudes, exactly.
6. **C4** counts every crossing across 4 sensors × 3 readers × 5 conditions × 200
   streams.
7. **Fisher test:** `scipy.stats.fisher_exact(table, alternative="greater")`, where the
   table is [[k1, n1−k1], [k0, n0−k0]].
8. **Parallelism.** Streams run independently in a process pool of min(4, cpu_count)
   workers. Every random draw is seeded per stream, per encounter or per day, so results
   don't depend on the worker count.
9. **Smoke test.** Before the scored run: `main(n_streams=2)` with output discarded,
   only to catch crashes and time it. No outcome is looked at.

## Known before the run

- The lattice sensors have low power under the calibrated per-place readers (PREREG
  power_note). A3 and A4 involve cross rates near 0.1–0.2 for LATTICE and FOLD_MEMORY.
- The paired SE of rel_B and rel_C was estimated before freezing at about 0.02–0.03 for
  every sensor. B2's ±0.06 band is about 2–3 SE.
