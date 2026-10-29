# grace_window_v1: deviations and corrections

The single scored run (receipt 746856fc…) is final. It scored 12 of 12 predictions as
frozen. Nothing was re-scored.

## Scoring deviations

None. The smoke test passed on its first attempt, and run_v1.py was sealed before the run
(RUN_V1.sha256, 6f5f0f90…, 16:07:38Z).

## Author's estimation errors (recorded; no effect on verdicts)

1. **Lattice power was overestimated again.**

   | Separation under R_FULL | Expected | Measured |
   |---|---|---|
   | sep(LATTICE) | 0.15 | 0.065 |
   | sep(FOLD_MEMORY) | 0.08 | 0.015 |

   Before the freeze I had already cut the first guess (0.45) using analytic per-place
   power. Even that was optimistic: measured per-place support for LATTICE under SPREAD
   was 0.10–0.26.
2. **Exploratory D** (the landing consequence under R_PLACE, not scored) came out −0.035
   against +0.02 expected. The PREREG declared it underpowered: FOLD_MEMORY's SPREAD
   crossing under R_PLACE is 0.045, so there is nothing for it to resolve.

## Corrections to earlier text

1. **grace_window_v0's PREREG overstated the sensor rates.** It gave the signal-tuple
   rates as "~26% truncated, ~1.7% ordinary". v1's calibration (r3_thinning_probe/
   calibrate_sensor.py, 200,000 folds per corner) measured **23% and 0.7%**. The v0 text
   was descriptive and none of v0's verdicts depended on it.
2. **The r3 thinning probe was run twice.** The first version had a dead line that
   consumed extra random draws without affecting the logic; it gave separation 0.840. The
   corrected version gave 0.780. Both are reported (PREREG why_v1). Both are within 0.10
   of the lattice's 0.755, and the gap between them shows the probe's sampling noise.
3. **Claim correction in the conversation.** I first said a state-dependent lattice could
   "beat the labels". It can't: the data-processing inequality covers every lattice fed
   only by the labels. I corrected this before the PREREG, which frames v1 as computation,
   not information.
