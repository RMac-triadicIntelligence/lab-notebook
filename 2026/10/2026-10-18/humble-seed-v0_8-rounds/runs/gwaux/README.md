# grace_window_v1: does the terrain do the reading?

**Result: 12 of 12 PASS** (4 construction checks; 8 evidence predictions, including the
primary). Scored once, as frozen.

| Item | Value |
|---|---|
| PREREG | `59255bee…`, frozen 2026-10-18T16:05:21Z, before any experiment code |
| run_v1.py | `6f5f0f90…`, sealed 16:07:38Z |
| Receipt | `746856fc3ea3d9d48814f80ef3f51e10694c590dd0ce8c08201be939aebe89f4` |
| Lattice | Rusty's `origami_kenta_sdkp.py` (`3ef44fe5…`), unchanged |

**Fold memory** is Rusty's fold plus one rule: a crease holds until it relaxes. It lives in
`fold_memory.py` (`8f68aeb5…`), frozen with the PREREG.

## Why v1

- **v0** passed its primary, but its reader was miscalibrated, and a bad stretch fooled
  it.
- **v0 post-hoc:** with a sound test, the stateless lattice kept almost no power.
- **sdkp_r3:** its lattice "advantage" turned out to be thinning. A coin with the
  lattice's rates (23% truncated, 0.7% ordinary), with no lattice at all, reproduces it:
  0.780 vs 0.755 (`r3_thinning_probe/`).
- **Structural reason:** Rusty's fold never reads its own state. Each tuple is a random
  function of (place, truncated), so no lattice fed only those labels can carry more than
  the labels do. That holds with or without memory.
- **So v1 asks about computation, not information.** If a crease holds until it relaxes,
  does the terrain itself discount concentrated evidence, so that a reader blind to place
  and time can still tell a preference from a confound?

## Scores

| | Prediction | Threshold | Measured | Verdict |
|---|---|---|---|---|
| C1 | Exact count matching | 100% | 200/200 | PASS |
| C2 | Counter + count-only reader identical across matched conditions | 100% | 200/200 | PASS |
| C3 | Owner re-fold reproduces every tuple and outcome; tamper caught; grant valid | 100% | 2000/2000; 200/200; 200/200 | PASS |
| C4 | Crossings inside the window | 100% | 3712/3712 | PASS |
| A1 | Calibrated readers hold under NULL, every sensor | ≥ 0.95 | min 0.985 | PASS |
| A2 | Counter, places × time: SPREAD crosses / commute holds / bad stretch holds | ≥ 0.80 / 0.85 / 0.85 | 0.970 / 0.920 / 0.905 | PASS |
| A3 | Rusty's lattice behaves like a thinned counter (8 comparisons) | \|diff\| ≤ 0.10 | max 0.025 | PASS |
| A4 | Counter dominates both lattices in separation | +0.20 | 0.875 vs 0.065 and 0.015 | PASS |
| **B1** | **Fold memory discounts bursts in the terrain (count-only view)** | **≥ 0.10, CI > 0** | **0.191** (paired diff 2.79, CI 2.13–3.43) | **PASS** |
| B2 | Stateless lattice and thinned counter don't | \|rel\| ≤ 0.06 | +0.006, +0.024, −0.031, −0.030 | PASS |
| B3 | Fold memory does NOT discount the commute (predicted limit) | < 0.10 | 0.018 | PASS |
| B4 | Shuffling the burst back across time restores it | CI > 0; ≤ 0.06 | 2.59 (CI 1.73–3.46); 0.013 | PASS |

**Cross rates.** Each cell is R_FULL \| R_PLACE \| R_NAIVE.

| Sensor | SPREAD | CONCENTRATED | BURST | NULL |
|---|---|---|---|---|
| COUNTER | .970 \| .970 \| 1.0 | .080 \| .080 \| 1.0 | .095 \| .990 \| 1.0 | .000 \| .015 \| .045 |
| THINNED | .155 \| .160 \| .650 | .070 \| .080 \| .665 | .045 \| .160 \| .680 | .005 \| .005 \| .050 |
| LATTICE | .155 \| .170 \| .675 | .090 \| .105 \| .635 | .045 \| .150 \| .640 | .010 \| .010 \| .050 |
| FOLD_MEMORY | .045 \| .045 \| .470 | .020 \| .025 \| .420 | .030 \| .060 \| .315 | .000 \| .000 \| .045 |

**Self-prediction.**

| | Expected | Measured |
|---|---|---|
| B1 | 0.20 | 0.191 |
| B3 | 0.04 | 0.018 |
| A2 | 0.94 / 0.91 / 0.91 | 0.97 / 0.92 / 0.905 |
| sep(COUNTER) | 0.85 | 0.875 |
| sep(LATTICE) | 0.15 | 0.065 |
| sep(FOLD_MEMORY) | 0.08 | 0.015 |

The lattice estimates were optimistic again (DEVIATIONS).

## What it shows

1. **The grace pipeline works when the sensor is the labels.**
   - The calibrated places × time reader fixes all three of v0's misses: genuine
     preference crosses 97%, the commute holds 92%, a bad stretch holds 90.5%, and no
     signal holds 100%.
   - Every landing stays in the window, and the owner can replay every one.
2. **Rusty's lattice, as is, is a thinning channel.**
   - It matches a coin-flip counter in every condition (A3, B2).
   - Fed the labels, it only discards signal: separation 0.065 against the counter's
     0.875.
3. **With memory, the terrain does part of the reading.**
   - A reader that sees only totals gets 19% less evidence from a bad stretch than from
     a spread preference of the same size. The stateless sensors show no such discount,
     and scattering the burst back across time restores it (B4).
   - It shows up in landings too, though not scored: under the count-only reader, fold
     memory crosses 47% on SPREAD vs 31.5% on BURST, while the lattice gives 67.5% vs
     64%.
   - This is the first measured case of SDKP terrain computing something the labels
     don't hand a simple reader for free.
4. **And it has a limit, predicted before the run (B3).**
   - The memory lasts about a day. Calibration showed that background traffic saturates
     any slower relaxation.
   - So a once-a-day commute isn't discounted (1.8%). Memory handles time, not places.
   - Memory also costs signal: 37% less terrain excess than the stateless lattice.

## What it doesn't show

- **This confirms a mechanism; it doesn't discover one.** B1 hit the value the
  calibration predicted.
- **A lattice isn't needed.** A per-place saturating counter could compute the same
  discount (data-processing inequality). That wasn't tested.
- **One world, one mechanism.** λ = 1.0 came from a declared criterion, and the
  conditions were authored. Synthetic owners. Not wired into Humble Seed.

## Where this leaves SDKP

Wherever clean labels exist, read them with the calibrated reader. The lattice earns a
place only where the reading has to happen in the substrate: a reader too simple to track
places and time, as on edge or legacy hardware. There, memory gives a discount for
temporal concentration at the cost of signal.

The open problem is **place memory that background traffic doesn't erase**. For example,
ordinary replies might not crease at all, or relaxation might scale with traffic. That is
a separate hypothesis and needs its own pre-registration.

## Files

| Path | What it is |
|---|---|
| `PREREG.json` (+ `.sha256`, `.frozen_at`) | Frozen design, 12 predictions, expected values |
| `fold_memory.py` | The memory rule (frozen input) |
| `calibration/` | Pre-freeze, sensor-only λ calibration, criterion declared in its docstring |
| `r3_thinning_probe/` | Post-hoc check of sdkp_r3 (motivates the THINNED control) |
| `PRE_RUN_NOTES.md` (+ `.sha256`) | Implementation choices, sealed before the run |
| `run_v1.py` (+ `RUN_V1.sha256`) | The experiment; refuses to run if frozen inputs differ |
| `results.json`, `RUN_LOG.txt` | The scored run |
| `DEVIATIONS.md` | No scoring deviations; estimation errors and corrections |
| `make_prereg_v1.py` | Generated and froze the PREREG |
| `RECEIPT_COMMITMENT.txt`, `REVIEW_BRIEF_BLIND.md` | For blind reviewers. The salt is held back until they report |

**Reproduce:** `python3 -I run_v1.py`. Needs numpy, scipy and cryptography. Takes about
3 minutes on 2 cores and about 6 on 1. The receipt doesn't depend on core count.
