# grace_window_v1: blind review brief

You're reviewing a pre-registered simulation. The author has already run it once and
scored it. Those results are **not in this pack**. The author's receipt is sealed in
`RECEIPT_COMMITMENT.txt` as sha256(salt + receipt). The salt is released after you report.

## What it tests

The owner signs openness to change, with no magnitude. The organism's terrain then
decides whether to hold and how far to move. Four sensors build that terrain from the same
replies:
- **COUNTER:** the labels themselves.
- **THINNED:** a stateless coin at the lattice's rates.
- **LATTICE:** Rusty's origami lattice, unchanged (`received/`).
- **FOLD_MEMORY:** Rusty's fold plus one rule, that a crease holds until it relaxes
  (`fold_memory.py`).

Three readers then decide:
- **R_NAIVE:** count only.
- **R_PLACE:** calibrated place breadth.
- **R_FULL:** places × time.

There are five count-matched conditions: SPREAD, CONCENTRATED, BURST, NULL and
SHUFFLED_BURST. The full specification is in `PREREG.json`. The sensor calibration, run
before the freeze, is in `calibration/`.

## Please do, in this order

1. **Predict first.** Before running anything, write your own PASS or FAIL, with a number,
   for A2, A3, A4, B1, B2, B3 and B4.
2. **Verify hashes:**
   - `PREREG.json` against `PREREG.sha256`.
   - `fold_memory.py` and the lattice against `PREREG.json` → `frozen_inputs`.
   - `run_v1.py` against `RUN_V1.sha256`.
   - `PRE_RUN_NOTES.md` against `PRE_RUN_NOTES.sha256`.
3. **Audit fidelity.** Read `run_v1.py` against `PREREG.json` and `PRE_RUN_NOTES.md`.
   List every place where the code does something the PREREG doesn't say, or says
   differently. Pay particular attention to:
   - k_s and count matching;
   - the shuffle;
   - relaxation timing and seeds;
   - the Fisher tables;
   - the bootstrap;
   - the scoring of each prediction.
4. **Audit the calibration.** Was λ chosen by the declared criterion? Could the criterion
   or the BURST design have been chosen to make B1 pass?
5. **Run once:** `python3 -I run_v1.py`. It needs numpy, scipy and cryptography and takes
   about 3 minutes on 2 cores. Report every verdict, the tables and the `receipt` line.
6. **Attack.** Look for:
   - predictions that are true by construction but presented as evidence;
   - thresholds set too loose;
   - controls that don't control what they claim;
   - anything that would let a per-place saturating counter, with no lattice, do
     everything FOLD_MEMORY does.

   Give runnable probe code for every claim.

Report your receipt exactly. If it differs from the author's, say which numbers differ.
Don't edit frozen files. Put probes in separate scripts.
