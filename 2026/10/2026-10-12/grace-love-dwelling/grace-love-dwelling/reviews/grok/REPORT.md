# Reply — Triadic Test Pack 2026-10-12

Reviewer (model and version): Grok 4.7.
Executed the code myself (yes / no): **yes** — all three supplied scripts, unchanged, exited 0.
Python version: **3.10.21**. numpy version: **2.2.6**. scipy version: **1.15.3**.

**Frozen score: 19 PASS, 4 FAIL.** The failures are **S3, T7, T8, and G5**.

## 1. Integrity

- RECEIVED.sha256: **OK** (both received files).
- PREREG hashes: **S OK · T OK · G2 OK**.
- Result file hashes match Claude's committed hashes byte for byte (and match the independent Codex audit).

## 2. Result file hashes (sha256)

- results_S.json: `9e1a46b16cbf01ffa84687c124558ec337b85a55be1e6eae5c70aef7e134d8f3`
- results_T.json: `154e1f466ac7472b47e90201d11ccf8edf8a0809e17bfc0877aa4c13d2160d54`
- results_G2.json: `a96562bd3b345cb7f84549da89f3c28a6e5c67021f090fe7ee58817e7e41d1a4`

All three independently produced result files match Claude's committed hashes and the Codex independent audit byte for byte, despite different Python/numpy versions.

## 3. Scores, exactly as frozen

Rates below are fractions. Medians are days. Joint conditions require every stated clause; no threshold was relaxed. No ratio denominator was zero.

| Prediction | PASS / FAIL | Observed value |
| --- | --- | --- |
| S1_replication | PASS | Noise .04 unauthorized: ON .99 ≥ .90; OFF .06 ≤ .10. |
| S2_plumbing | PASS | GATED = OFF unauthorized exactly: .00, .00, .06 at noise .02, .03, .04. |
| S3_grace_without_push | **FAIL** | Noise .04, W10: 10/94 ≈ .106 < .50. |
| S4_dwelling_needed | PASS | Noise .04, W10, NODWELL: 0/94 = .00 ≤ .10. |
| S5_dose | PASS | W5/10/20/40: .032, .106, .340, .606, nondecreasing. |
| S6_retention | PASS | 10/10 W10 window crossers retained = 1.00 ≥ .90. |
| S7_noise_needed | PASS | Noise .02, W10: 0/100 = .00 ≤ .30. |
| T0_layer_is_counter | PASS | Identical decisions in all 200 streams of each of six world/variant cells: 1.00 throughout. |
| T1_learning | PASS | PREF day365: all four readers in both variants = 1.00 ≥ .90. |
| T2_fragmentation_cost | PASS | PREF 4coord: full median 25, place 4; 25 ≥ 2×4. |
| T3_joint_information | PASS | CONF 2coord day60: full .190 ≤ .5×place .995 = .4975. |
| T4_erosion | PASS | CONF 2coord full day365 = 1.00 ≥ .80. |
| T5_scalar_no_better | PASS | CONF 2coord day60: scalar .935 ≥ .8×place .995 = .796. |
| T6_rollup | PASS | PREF 4coord: roll median 4 ≤ 1.25×place 4 = 5; CONF 2coord day60: roll .190 ≤ .6×place .995 = .597. |
| T7_null_world | **FAIL** | NULL day365, 4coord full 0.0 and roll 0.10 both < .50 (2coord all ≥ .50; 4coord place/scalar = 1.00). |
| T8_shuffle | **FAIL** | CONF 2coord day60 shuffled full .585 < .8×place .995 = .796. |
| G1_love_lowers_grace | PASS | g*: grace .32727, grace+love .24902; .24902 ≤ .85 × .32727 ≈ .27818. |
| G2_love_needs_dwelling | PASS | g* NODWELL .32727; difference from grace = .00000 ≤ .01. |
| G3_together | PASS | Noise .02, g .25: together .93, grace .04; difference .89 ≥ .30. |
| G4_love_alone | PASS | Noise .02 love alone = .00 ≤ .05. |
| G5_grace_alone_subthreshold | **FAIL** | Largest grid g below .32727 is .30; grace p_cross .54 > .20. |
| G6_retained | PASS | Every nonempty crossing cohort retained 1.00 ≥ .95. |
| G7_plumbing | PASS | All dwelling-on arms: unauthorized .00 at noise .02, .06 at noise .04. |

## 4. Attack findings

- **test_S.py:47; DEVIATIONS.md:5** — Window crossing counted in [150, 150+W+10). For W=10 this includes 10 time units after field-off. Disclosed; S3 still fails. **Verdict consequence: none.**
- **test_T.py:45–54; received/origami_kenta_sdkp.py:170–204** — CounterLayer mirrors only crystallization threshold and permanent grounding used by occupied_view. T0 confirms identity. Coherence, logs, and return values are unused by the harness. **Verdict consequence: none.**
- **test_T.py:59–64** — Weight uses co-occurrence counts that stop at crystallization (5 per context). Explicit in the reader; not a silent bug. **Verdict consequence: none as frozen.**
- **test_G2.py:24–35; received/triadic_model.py:38–48** — Love window is algebraically inert under NODWELL (dwelling remains 0; coupling/decay multiply by dwelling; rise multiplies by story_depth). G2 is true by construction. **Verdict consequence: G2 PASS is algebraic.**
- **README.md:22; received/triadic_model.py:2** — “Python 3 and numpy; no other packages” is false: the received module imports scipy.integrate at import time. Tests ran after installing scipy. **Verdict consequence: none; would fail to import in a pure numpy environment.**
- **test_S.py / test_G2.py** — Custom Euler-Maruyama with clip [0,1]; never calls received simulate() / odeint. Declared by the preregistrations. **Verdict consequence: none.**

## 5. True by construction

- **S2_plumbing and G7_plumbing:** identical pre-t=150 parameters, order, and noise paths force equal unauthorized counts.
- **G2_love_needs_dwelling:** NODWELL keeps dwelling ≡ 0, so field-parameter switch has no effect; g* matches GRACE exactly.
- **T0_layer_is_counter:** the control reproduces the saturating counters and crystallization membership the reader actually consults. Other class state is ignored.

Other threshold predictions can and did fail (S3, T7, T8, G5).

## 6. Anything else

Result hashes are identical to Claude's commitment and to the Codex independent audit, confirming reproducibility of the numerical outcomes across Python 3.10/3.12 and numpy 2.2/2.3.

The selective-dwelling claim in S3 does not hold under the frozen measure. The grace-alone subthreshold claim in G5 fails. In T, the 4-coordinate null world does not force the predicted false-commit rate for the full and roll-up readers (T7), and the shuffle does not restore the place-reader rate (T8).

Reproduction commands (from the included pack directory, after ensuring scipy is available for the import):

```bash
sha256sum -c RECEIVED.sha256 PREREG_S.sha256 PREREG_T.sha256 PREREG_G2.sha256
python3 test_S.py
python3 test_T.py
python3 test_G2.py
sha256sum results_*.json
```

The archive includes the unchanged original pack, the scored results_*.json files, this report, and environment details. No later repair has been used to reinterpret a frozen verdict.
