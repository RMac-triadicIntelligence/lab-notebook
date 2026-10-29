# Findings

All numbers come from `seal/2026-10-12/results_*.json` and `SCORE_*.json`. Scores are exactly as frozen; nothing was rescored after review.

## Background

The tests grew out of a look back at earlier work on 2026-10-12. Rerunning the published contemplative-learning-dynamics model showed that its dwelling field lowers the barrier for a nudge and for noise alike. At noise 0.04 (exploratory, 30 seeds) the system opened by itself in 30 of 30 runs with the field on and 0 of 30 with it off. That raised the question these tests ask: can dwelling be made selective, and what does each piece do?

---

## Test S — selective dwelling

`PREREG_S.json` (6c47f7f2…). Love, in the sense used later, is the permission window here: inside it the dwelling field's parameters are switched on; outside it the dynamics are field-off. There is no push. Any crossing must come from noise.

| Prediction | Verdict | Observed |
| --- | --- | --- |
| S1 replication of the exploratory result | PASS | Field on: 0.99 crossed before t=150; field off: 0.06 |
| S2 gated arm equals field-off before the window (plumbing) | PASS | Identical at all noise levels |
| S3 a 10-unit window carries ≥ 50% across at noise 0.04 | **FAIL** | 0.106 |
| S4 no dwelling, no crossing in the window | PASS | 0.000 |
| S5 crossing grows with window length | PASS | W5/10/20/40: 0.032, 0.106, 0.340, 0.606 |
| S6 crossers stay open | PASS | 1.0 |
| S7 low noise is not enough | PASS | 0.0 at noise 0.02 |

Reading: selectivity held; the window gives noise no opening before permission. Crossing inside the window is dose-dependent and slower than predicted. Of the 10 crossings counted at W=10, 8 happened inside the window and 2 in the following 10 units, after it closed (errata E2).

## Test G2 — grace as the nudge, love as the window

`PREREG_G2.json` (9228a974…). Grace is a nudge on facet 1 at t=155, the middle of the love window.

| Prediction | Verdict | Observed |
| --- | --- | --- |
| G1 love lowers the nudge grace needs (≤ 0.85×) | PASS | 0.249 vs 0.327 (0.761×) |
| G2 love needs dwelling | PASS, by construction | No dwelling: 0.327, identical to grace alone |
| G3 together beat grace alone by ≥ 0.30 | PASS | 0.93 vs 0.04 at noise 0.02, nudge 0.25 |
| G4 love alone does not cross at low noise | PASS | 0.00 at noise 0.02 (0.10 at noise 0.04) |
| G5 a sub-threshold nudge rarely crosses | **FAIL** | Nudge 0.30 crossed 0.54 at noise 0.02 |
| G6 crossings hold | PASS | 1.0 in every populated cell |
| G7 identical before t=150 (plumbing) | PASS | — |

Reading: dwelling holds readiness, love opens the field, grace makes the crossing, and noise closes the remaining gap near the separatrix. The noise in these runs comes from the harness, not the received model.

## Test T — terrain vs counter

`PREREG_T.json` (949fab60…). The received ConsciousnessLayer (exact-key co-occurrence counting, threshold 5, permanent crystallization) is read through four keys: place only, the four coordinates multiplied into one number, the full tuple, and a roll-up from place to full. Worlds vary on 2 or 4 coordinates. PREF has a real preference, CONF a confound hidden in a joint cell, NULL background only.

| Prediction | Verdict | Observed |
| --- | --- | --- |
| T0 the layer is a counter | PASS, by construction | Identical decisions in 100% of streams |
| T1 every reader learns a real preference | PASS | 1.0 by day 365 |
| T2 full tuple learns ≥ 2× slower in a 4-coordinate world | PASS | Median 25 days vs 4 |
| T3 full tuple halves day-60 false commits on the joint confound | PASS | 0.19 vs 0.995 |
| T4 full tuple still erodes by day 365 | PASS | 1.0 |
| T5 the product reader is no better than place | PASS | 0.935 vs 0.995 |
| T6 roll-up keeps place speed and full-tuple protection | PASS | 4 vs 4 days; 0.19 vs 0.995 |
| T7 every reader false-commits in a background-only world by day 365 | **FAIL** | 4-coordinate full 0.0, roll-up 0.10 |
| T8 shuffled labels erase the full-tuple advantage | **FAIL** | 0.585 vs 0.995 |

Reading, after review: the layer counts absolute occurrences with no rate and no forgetting, so steady background eventually becomes a symbol. Extra coordinates delay that but do not stop it: an exploratory run to day 1,825 (`tools/exploratory_long_horizon.py`) took the 4-coordinate full reader from 0% false commits at day 365 to 100% by day 1,095. The full tuple's joint-information advantage is real but smaller than the frozen numbers show; see errata E1.

---

## Errata (from `seal/2026-10-12/ERRATA_2026-10-12.md`)

- **E1, reader weight (found by ChatGPT, confirmed).** The preregistration says a key's weight is its total deposit count. The reader used counters that stop at crystallization, so weight caps at 10: 100 ordinary and 5 signal events read as all signal. ChatGPT's separately run repair gives CONF 2-coordinate day-60 false commits of 0.475 (full) vs 1.00 (place), with the shuffle at 0.810. T3 and T6 still pass and T8 would pass. The earlier reading that half the advantage was dilution is withdrawn.
- **E2.** Two of Test S's ten W=10 crossings came after the window closed.
- **E3, received code.** In `origami_kenta_sdkp.py`, the `equilibre` context cannot be reached on a binary 16-cell lattice.
- **E4.** The original pack README said numpy only; the received model also imports scipy.
- **E5.** The pack showed Claude's result hashes, so a matching hash alone does not prove a reviewer executed the code. Both reviewers returned the result files, which match.

## Independent review

Both reviewers reproduced all three result files byte for byte and scored 19 PASS, 4 FAIL with no disagreement.

- **ChatGPT (Codex):** independent. Found E1 and E2, the unreachable `equilibre` context, overlapping seed sets between variants, an unchecked bisection endpoint (dormant), and that clipping at zero gives the noise a small positive mean. None changes a frozen verdict; E1 changes the reading of T.
- **Grok 4.7:** its first reply was independent and found the scipy import. Its full report cites and reuses wording from ChatGPT's audit, so it is not independent. It judged the E1 weight behaviour intended.

## Exploratory, not preregistered

`tools/exploratory_long_horizon.py` reproduces `EXPLORATORY_T_long_horizon.txt`: CONF and NULL, 4 coordinates, 100 streams, to day 1,825. The event arrays are longer than in the sealed run, so per-stream draws differ. Use it only to tell delay from protection.
