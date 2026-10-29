# v0.13 — Release and the Standing Lesson: results

Two fresh blocks of 32 seeds (13000–13031, 13100–13131). Contracts clean in both
(gate-closed runs: no crossing, no declaration; refused founders: zero wear). Not void.
Per-block numbers for review are in `results/for_review.json`. No merged verdict.

## Lesson-stands row — met in both blocks

| | A (no declaration) | B (declare) | C (declare + release) | E (declare, lesson erased) |
|---|---|---|---|---|
| Block 1 descendant crossings through declared gates | 6.13 | 3.31 | 3.31 | 6.13 |
| Block 2 | 6.34 | 3.34 | 3.34 | 6.34 |

A standing warning roughly halves the next generation's traffic through the gates the
declarers named. Erasing it returns descendants to the no-declaration baseline exactly.
Release (C) leaves descendants identical to B: forgiveness of the author does not
touch what the next generation inherits, which is what the split was meant to
guarantee. This is the v0.6 "keep the lesson" result reproduced in a different kernel
with the lesson in the commons rather than in the individual.

## Forgiveness row — not accepted

| | P1_C − P1_B | P1_D − P1_B | D matches C (margin 0.5) |
|---|---|---|---|
| Block 1 | +0.008 | −0.003 | no |
| Block 2 | +0.007 | −0.011 | **yes** |

Same sign in both blocks, but the ordering control fails in block 2, so the row does not
meet its preregistered acceptance. The effect is also at the instrument's ceiling:
attempt counts saturate at one approach per agent in the window (0.333 per 100 steps),
and in C the declarers are at that ceiling while in B a few are just below it. What P1
can say at this setting is "release got slightly more declarers back to the fence," and
random release (D) did nearly as well in one block.

**P2 moved (−0.05 and −0.11), and I am not reporting it as forgiveness.** Released
declarers reach the fence sooner, before the last grace window opens (steps 740–780), so
more of their attempts land while the gate is shut. That is the calendar/readout
interaction the reviewer predicted, visible exactly as predicted.

## What this means

- **The lesson stands, and it is inheritable.** Clean, both blocks, with the erase
  control behaving exactly as a control should.
- **Release does not show a measurable effect on approach in this instrument.** Not
  "forgiveness failed": the P1 metric saturates, and the only lever release has here is
  readout, on agents whose way home is dominated by a strong westward turn.
- **The public-good structure from v0.11/v0.12 is dissolved by the split.** With the
  warning separated from the author's burden and applied to everyone, declarers are no
  longer behind the silent (P1 ≥ 0 in B, both blocks). The earlier self-penalty was the
  identity-flag conflation the reviewer caught.

## Engineering history

Two pre-freeze amendments, both logged: an evidence turn at step 600 so burdened agents
have a reason to re-approach the fence (without it, P1 had zero attempts), and its size
(−1.5), calibrated on arm A only. Neither was in the reviewed arm-rule files.

## Next, if wanted

A P1 that doesn't saturate: time-to-first-attempt in W, or a longer window with
repeated approaches. That is a metric change and goes back to review before any run.
