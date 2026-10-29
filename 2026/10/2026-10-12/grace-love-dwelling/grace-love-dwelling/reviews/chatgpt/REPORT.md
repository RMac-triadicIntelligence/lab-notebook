# Reply — Triadic Test Pack 2026-10-12

Reviewer (model and version): Codex (GPT-6; exact runtime build identifier not exposed).
Executed the code myself (yes / no): **yes** — all three supplied scripts, unchanged, exited 0. I also executed separate reviewer probes and the received origami demonstration.
Python version: **3.12.14**. numpy version: **2.3.5**. scipy version: **1.17.0**.

**Frozen score: 19 PASS, 4 FAIL.** The failures are **S3, T7, T8, and G5**. G6 is a conditional PASS on observed crossing cohorts; seven empty cohorts have undefined retention, not an invented retention value.

## 1. Integrity

- RECEIVED.sha256: **OK** (both received files).
- PREREG hashes: **S OK · T OK · G2 OK**.
- All 19 original non-directory archive entries remain byte-identical to the uploaded ZIP, including all test scripts. Checks were repeated after execution and attacks.
- Input ZIP SHA-256: `054e8ccbd8fc7c9004138a04c2535c7b04102927998cee92217c96e40e1d079d`.
- Integrity authenticates these bytes against the supplied manifests. It does not independently establish that the supplied freeze timestamps preceded code creation.

## 2. Result file hashes (sha256)

- results_S.json: `9e1a46b16cbf01ffa84687c124558ec337b85a55be1e6eae5c70aef7e134d8f3`
- results_T.json: `154e1f466ac7472b47e90201d11ccf8edf8a0809e17bfc0877aa4c13d2160d54`
- results_G2.json: `a96562bd3b345cb7f84549da89f3c28a6e5c67021f090fe7ee58817e7e41d1a4`

All three independently produced result files match Claude's committed hashes byte for byte, despite the different reported Python/numpy versions. No result contents were supplied in the original archive.

## 3. Scores, exactly as frozen

Rates below are fractions. Medians are days. Joint conditions require every stated clause; no threshold was relaxed. No ratio denominator was zero.

| Prediction | PASS / FAIL | Observed value |
| --- | --- | --- |
| S1_replication | PASS | Noise .04 unauthorized: ON .99 ≥ .90; OFF .06 ≤ .10. |
| S2_plumbing | PASS | GATED = OFF unauthorized exactly: .00, .00, .06 at noise .02, .03, .04. |
| S3_grace_without_push | **FAIL** | Noise .04, W10: 10/94 = .1063829787 < .50. |
| S4_dwelling_needed | PASS | Noise .04, W10, NODWELL: 0/94 = .00 ≤ .10. |
| S5_dose | PASS | W5/10/20/40: 3/94, 10/94, 32/94, 57/94; .0319148936, .1063829787, .3404255319, .6063829787, nondecreasing. |
| S6_retention | PASS | 10/10 W10 window crossers retained = 1.00 ≥ .90. |
| S7_noise_needed | PASS | Noise .02, W10: 0/100 = .00 ≤ .30. |
| T0_layer_is_counter | PASS | Identical commit/noncommit decisions and commit days in all 200 streams of each of six world/variant cells: 1.00 throughout. |
| T1_learning | PASS | PREF day365: all four readers in both variants = 1.00 ≥ .90. |
| T2_fragmentation_cost | PASS | PREF 4coord: full median 25, place 4; 25 ≥ 2×4; ratio 6.25. |
| T3_joint_information | PASS | CONF 2coord day60: full .190 ≤ .5×place .995 = .4975. |
| T4_erosion | PASS | CONF 2coord full day365 = 1.00 ≥ .80. |
| T5_scalar_no_better | PASS | CONF 2coord day60: scalar .935 ≥ .8×place .995 = .796. |
| T6_rollup | PASS | PREF 4coord: roll median 4 ≤ 1.25×place 4 = 5; CONF 2coord day60: roll .190 ≤ .6×place .995 = .597. |
| T7_null_world | **FAIL** | NULL day365, place/scalar/full/roll: 2coord 1/1/1/1; 4coord 1/1/0/.10. Full and roll 4coord fail ≥ .50. |
| T8_shuffle | **FAIL** | CONF 2coord day60 shuffled full .585 < .8×place .995 = .796. |
| G1_love_lowers_grace | PASS | g*: grace .32727, grace+love .24902; ratio .7609007853 ≤ .85 (23.91% lower). |
| G2_love_needs_dwelling | PASS | g* NODWELL .32727; difference from grace = .00000 ≤ .01. |
| G3_together | PASS | Noise .02, g .25: together .93, grace .04; difference .89 ≥ .30. |
| G4_love_alone | PASS | Noise .02 love alone = .00 ≤ .05. |
| G5_grace_alone_subthreshold | **FAIL** | Largest grid g below .32727 is .30; grace p_cross .54 > .20. |
| G6_retained | PASS* | Every nonempty crossing cohort retained 1.00 ≥ .95: 27 populated cells. Seven cells have no eligible crossing and retention null. |
| G7_plumbing | PASS | All dwelling-on arms/g levels: unauthorized .00 at noise .02, .06 at noise .04. |

*G6 is a conditional statement about runs that crossed. There were no observed losses in any applicable cohort. Empty cohorts supply no empirical retention estimate; this PASS does not claim retention was demonstrated in those cells. The predicate in the script uses first crossing **at or after** 150, while the prediction says **after** 150. No crossing occurred exactly at 150 in the tested G2 cells, so this boundary wording does not change the score.

## 4. Attack findings

Each entry names the actual file and line, the discrepancy or limitation, and its verdict consequence. The original scores above remain unchanged. Counterfactuals are separately identified as reviewer work.

- **test_T.py:59–64; received/origami_kenta_sdkp.py:177–184** — The preregistration promises weight = a key's total deposit count. The reader instead sums co-occurrence counters, which stop increasing when each context crystallizes at five. A two-context key is capped at ten, regardless of subsequent exposure. In an executed 105-event probe (100 ord, five sig), stored counts were ord=5 and sig=5, the reader weight was 10, and its signal fraction was 1.00 despite an actual signal frequency of 5/105. **Verdict consequence: a separate repair using an external actual-deposit ledger flips T8 from FAIL to PASS; other T prediction verdicts stay unchanged.** This is the main undeclared preregistration/implementation mismatch.
- **test_T.py:63,109–114** — Any crystallized signal makes the entire key's weight count as signal evidence, even if ord also crystallized. This is explicitly preregistered, but it measures occupancy of a permanent signal label, not signal prevalence or preference strength. Combined with saturated counts, rare background becomes affirmative evidence. **Verdict consequence: none as frozen; interpretation of T1/T4/T7 is limited to this reader.** The 105-event probe directly demonstrated the effect.
- **test_T.py:9,94–97,102–114; received/origami_kenta_sdkp.py:267–280** — T imports only SDKPTuple and ConsciousnessLayer and supplies synthetic coordinates, sig/ord contexts, a signal-count need trigger, occupancy reader, HOLD footprint, and terminal COMMIT. It bypasses OrigamiLattice.fold, compute_sdkp, homeostatic_context, the authorization stream, and coherence decay. It also ignores the received layer's coherence, unknown-events log, and returned symbols. **Verdict consequence: none for the declared toy experiment.** This is a subcomponent test, not an execution of the received origami architecture or its original decision process; the received module contains no equivalent COMMIT reader.
- **test_T.py:29–33,98–102** — CONF's informative joint cell is hand-specified, and read timing is driven by the same signal labels used as evidence. These are declared world/need choices, not hidden prediction leakage. A shuffled label stream therefore changes both key-label relationships and need times. **Verdict consequence: none demonstrated; T8 does not isolate the relationship while holding read times fixed.** No outcome-guided tuning or hidden access to Claude's result contents was found in the scripts.
- **test_T.py:18; PREREG_T.json world.rng** — The variant seed sets are 0..199 and 10..209 within each world. They overlap at 190 seeds; the executed probe confirmed identical P/K arrays for the shifted-index overlapping streams. Each cell still has 200 unique seeds, and readers share streams as intended. **Verdict consequence: none; treating the two variant populations as independent replication would be incorrect.** Shuffle seed 777+stream was unfrozen, as DEVIATIONS.md discloses; the blind pack cannot verify when it was selected.
- **test_T.py:122–125** — Day60/120/365 rates are emitted, but only a final-horizon conditional median is emitted. The frozen reporting instruction asks for median commit day at all three horizons. **Verdict consequence: none; the frozen median-based predictions use final-horizon medians.** Reporting is incomplete for the earlier horizons.
- **test_S.py:36,51; DEVIATIONS.md:5** — A W10 crossing is counted through t<170 even though the field closes at160. This matches the frozen measure and disclosed note; it is not an implementation error. Executed timing probe: eight crossings in [150,160), two in [160,170), six before150. **Verdict consequence: none; S3 still fails.** Calling all ten in-window authorized crossings would misdescribe two of them.
- **test_S.py:14,36–40; test_G2.py:13,28–35; received/triadic_model.py:38–48** — The window switches two differential-equation parameters; it is not an authorization check on the crossing. Ordinary field-off noise can cross before permission: six of 100 at noise .04. Both scripts report that separately. The received triadic model has no constitutional gate, permission object, or external authorization function. **Verdict consequence: none; S2/G7 verify shared pre-window dynamics, not default-deny safety.** The gating and noise are Claude's declared additions.
- **test_G2.py:30–38** — The nominal t=155 jump is applied after integrating the step from155 to155.02, and is recorded at155.02. A separately executed pre-step jump at exact155 produced the same rounded g* values (.32727/.24902/.32727). **Verdict consequence: none demonstrated for the deterministic g*-based scores.** The stochastic cells were not rerun under that alternate timing, so no claim is made about their unchanged values.
- **test_G2.py:47–54** — Bisection does not check that g=0 fails and g=1 succeeds; if no crossing were possible, it would still return1 as a supposed threshold. Executed endpoint probes gave [False, True] in all three deterministic arms, so this bug was dormant here. **Verdict consequence: none on this pack.** Monotonicity is also assumed rather than independently checked across the full continuous interval.
- **test_G2.py:43–44,66–68** — The p_cross definition requires final success, but the retention denominator is independently selected using first crossing. G6 is therefore **not** made true merely by defining p_cross as retained crossings. The seven null retention cells must not be replaced by1. **Verdict consequence: none; limits the empirical coverage of G6.** Endpoint retention does not check whether a trajectory ever recrossed downward in between.
- **test_S.py:38–40; test_G2.py:30–35; received/triadic_model.py:70–87** — The tests use noisy projected Euler steps rather than the received simulate() odeint workflow. Projection rectifies noise at zero: an executed 100,000-draw one-step probe at sigma .04, dt .02 had raw mean .0000324 and clipped mean .00226925. This is the declared integrator, not hidden added noise, but its effective boundary dynamics differ from unconstrained zero-mean additive noise and the original deterministic simulator. **Verdict consequence: none established; no alternate-integrator convergence sweep was run.** “Own noise” is supplied externally by the harness; no noise process exists in the received ODE.
- **README.md:22; received/triadic_model.py:2** — “Python 3 and numpy; no other packages” is false: the received module imports scipy.integrate at import time. scipy was installed here, so all tests ran. **Verdict consequence: none here; S/G2 fail to import in a numpy-only environment.**
- **received/origami_kenta_sdkp.py:139–145** — The original equilibre branch is unreachable for binary lattices: at density in [.35,.65], activity sqrt(d(1−d)) is at least about .477, contradicting activity<.45. An executed enumeration of all17 possible occupied-cell counts reached no equilibre state. **Verdict consequence: none in S/T/G2; T bypasses this context function.** This is a bug in the received architecture, not introduced by the comparison harness.
- **received/origami_kenta_sdkp.py:257,319–323,402–403** — The received demonstration's printed seed initializes legacy np.random for folds, but authorization_stream uses an independently unseeded default_rng. The printed seed alone cannot replay the demonstration. Its printed rest-period delta uses history[end], including the first post-rest event; check_life_signs uses end−1 correctly. In my executed supplemental demonstration, the first printed delta was +.066 while the actual withdrawal-decay check passed. **Verdict consequence: none for S/T/G2, which bypass these paths.**

The exact-deposit counterfactual changed CONF 2coord day60 full/roll rates from .190 to .475, place from .995 to1.00, and shuffled full from .585 to .810. T3 still passes (.475 ≤ .500), T6 still passes (.475 ≤ .600), and T8 now passes (.810 ≥ .800). This is a separately run repair, not a substitute scored result. NULL 4coord full stayed0, and roll rose from .10 to .245; T7 still fails.

## 5. True by construction

- **S2_plumbing and G7_plumbing:** same facets, parameters, integration order, and random draws before the intervention give identical pre-intervention crossing records. These are useful implementation checks but no independent mechanism evidence.
- **G2_love_needs_dwelling:** the NODWELL initialization and story_depth=0 keep dwelling exactly zero. The switched parameters multiply dwelling, so they have no effect. Dwelling-on GRACE has both effects explicitly disabled. Consequently the compared facet trajectories, nudge threshold, and corresponding noise-cell facet outcomes coincide. The PASS is algebraic under this setup.
- **T0_layer_is_counter:** the control reproduces the exact saturating counters and crystallization membership used by the reader. Coherence, logs, symbol names, and receive() return values cannot influence a decision because the harness never reads them. The decision-equivalence result is guaranteed by this projection, not full equivalence of the two classes. Their receive() return behavior even differs on the fifth encounter, without affecting this test.

Other finite-horizon numerical threshold predictions can fail; four did. CONF embeds joint-only information and the received layer permanently crystallizes at an absolute count, but this does not force any particular 60/365-day rate. T7's failure demonstrates that fragmentation and the HOLD/reopen rules can prevent the predicted finite-horizon erosion. G6 is not circularly guaranteed by the retained-crossing definition, as discussed above.

## 6. Anything else

The strongest measured separation is in G2: at noise .02 and g .25, grace+love crossed in93/100, grace alone in4/100; deterministic g* fell23.91%. Love alone crossed0/100 at that noise level. At noise .04 it crossed10/100 after the opening, so “love never crosses alone” is not supported. Deterministic subthreshold grace was not safely subthreshold in the noisy test: g .30 crossed54/100 at noise .02.

T's full reader showed a temporary CONF 2coord advantage (38/200 false commits by60 days versus199/200 for place), but all200 full-reader streams falsely committed by365 days. In4coord, full-reader suppression also appears in the NULL world, where it never commits; finite-horizon abstention must be distinguished from learned discrimination. The roll-up recovery is a property of Claude's place fallback reader, not an implemented feature of the received layer.

I also ran `python3 received/origami_kenta_sdkp.py` unchanged. Its six embedded life-sign checks all reported PASS in that supplemental stochastic run: seven grounded symbols/emergence events,40 unknown events, three contexts, and decay over both rest periods. These heuristic checks are separate from the23 frozen predictions; their names do not establish cognition, deliberation, or evidence-seeking, and the printed seed is insufficient to replay them.

Reproduction commands from the included pack directory:

```bash
sha256sum -c RECEIVED.sha256 PREREG_S.sha256 PREREG_T.sha256 PREREG_G2.sha256
python3 test_S.py
python3 test_T.py
python3 test_G2.py
sha256sum results_*.json
```

The archive includes the unchanged original pack, all scored JSON outputs and stdout/stderr logs, executable scoring and reviewer probe scripts, probe results, environment details, integrity checks, and a file manifest. No later repair has been used to reinterpret or overwrite a frozen verdict.
