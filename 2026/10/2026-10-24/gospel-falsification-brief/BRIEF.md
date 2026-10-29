# Falsification brief — Raised, Not Rented / Developmental Meaning Fork

Hostile reader's brief against the package at `/workspace/gospel-package/` (PI: Rusty Williams McMurray). Written 24 Oct 2026.
Status labels: **E** = established by packaged, runnable artefacts; **N** = narrated in the master record only (no code or raw data in the package); **H** = held open by the record itself.
Checks marked *RUN* were executed here; scripts and outputs are in this folder. Every number below comes from those outputs or from the packaged results. Nothing has been estimated.

## Checks run in this folder

| Script | Input | Output |
|---|---|---|
| `learner_robustness.py` | packaged v0.2 `observable_dataset.json`, `heldout_truth.json` | `learner_robustness.csv`, `.txt` |
| `position_leak.py` | packaged v0.2 `diagnostic_hidden.json`, `substrate_v01.py` | `position_leak.txt` |

Environment: Python venv at `/workspace/fbenv` (numpy, scikit-learn). Run with `/workspace/fbenv/bin/python <script>` from this folder.

---

## Attacks in priority order

### 1. The history-negative result is a property of k=15 kNN, not of the substrate (claim: E, "convergent negative result")
**Claim.** Added history features do not improve prediction. Position is the strongest predictor. The record cites two independent implementations.
**Attack.** Both implementations use local, distance-based learners on standardised features. A difference feature (`x(now) − x(−0.5)`) is small in scale, and kNN treats it as an equal Euclidean axis. That inflates noise. A learner that can weight features may behave differently.
**RUN result** (same packaged train/held-out split, no tuning; `learner_robustness.csv`):

| Regime / test group | Features | kNN15 acc (Brier) | Logistic reg. acc (Brier) | Grad. boost acc | Random forest acc |
|---|---|---|---|---|---|
| mixed / all | position | 0.9958 (0.0075) | 0.9865 (0.0235) | 0.9979 | 0.9979 |
| mixed / all | history (pack) | 0.9865 (0.0305) | **0.9979 (0.0100)** | 0.9979 | 0.9958 |
| forward-only / reverse | position | 0.8187 (0.264) | 0.8917 (0.1745) | 0.8187 | 0.8187 |
| forward-only / reverse | history (pack) | 0.6958 (0.373) | **0.9437 (0.0876)** | 0.7438 | 0.7438 |
| forward-only / reverse | position + one lag-difference | 0.7271 | **0.9458 (0.0795)** | 0.8187 | 0.7188 |

(My kNN15 reproduces the packaged metrics exactly: 0.9958 / 0.8187 / 0.6958.)
**Verdict.** **Refuted as a general statement. It survives only per learner.** With logistic regression, history *improves* both the mixed-regime result (0.9865 → 0.9979) and the hardest case, direction transfer (0.8917 → 0.9437; Brier halved). Tree learners agree with kNN that history hurts under transfer. The correct statement is: "for kNN and tree ensembles, history did not help; for a linear-logistic learner it helped, most under reverse transfer". The "convergent" status should be withdrawn. The two original implementations share the learner family that fails.
**Next falsifier.** Repeat across 10 resampled seed splits. Refutation of the original claim = logistic history beats logistic position on reverse-transfer Brier in ≥8/10 splits. Code change: wrap the `regime` loop in a seed-resampling loop (≈10 lines).

### 2. "Position" is the hidden state under another name (claim: E, "current position is strongest")
**Attack.** At each checkpoint the organism has been dwelling and sits close to its left attractor. That attractor is a monotone function of the hidden tilt `a`. Observed `x` therefore encodes `a`, and the frozen capacity follows almost exactly. "Observable-only" is true of the schema, not of the information.
**RUN result** (`position_leak.txt`, 96 held-out snapshots): R²(a ~ cubic(x)) = **0.9986**. R²(critical impulse ~ cubic(x)) = **0.9995**. Median |dx/dt| at snapshot = 5.85e-3, max 2.22e-2: the organism is near equilibrium.
**Verdict.** The "position" predictor recovers the capacity measure almost exactly. Its success is the v0.1 frozen identity again, reached by a different route. It is not evidence that observables carry reception information beyond the declared geometry.
**Falsifier.** Break quasi-equilibrium: take snapshots during transients (fast tilt rate, e.g. `rate` ∈ [1,3], or add process noise σ to dx/dt), or add observation noise to `x`. Refutation of "position is a reception predictor" = position accuracy falls to that of `time` once R²(a~x) < 0.5. Code change: in `draw_history`, widen `rate`; in `public_row`, add `x + rng.gauss(0,σ)`. 2–3 lines.

### 3. The supplied tilt schedule versus the developmental claim (claim: H / central fork claim, untested)
**Attack.** `History.evidence(t) = target + amplitude·sin(0.35t + phase)`, and `da/dt = rate·(evidence − a)`. Its sign is fixed by family. Nothing the organism does changes `a`. "Development" is an exogenous clock. Every reception result is conditional on a landscape that was chosen in advance. The alternative v0.2 text says so: "The schedule was chosen."
**Falsifier.** Make `da/dt` depend on the organism's own trajectory, e.g. `da/dt = rate·(g(x̄_window) − a)`, or on the outcomes of prior offerings. Then test whether capacity *grows through dwelling* without a positive target being supplied (set `target=0`). Refutation of "dwelling develops capacity" = with `target=0`, mean critical impulse at t=24 is not lower than at t=2 across ≥30 seeds. Code change: replace `h.evidence(t)` in `step()` with a function of `s.x` history. That requires a state buffer (~15 lines).

### 4. Junction completion criterion is instantaneous basin membership at a chosen instant (claim: E operationally, disagreement flagged)
**Attack.** The completion criterion is "instantaneous basin at end of bound assay". Under a moving landscape, the instantaneous basin and the terminal attractor can disagree. v0.3 tests disagreement only by *injecting* an `unresolved` label. It does not search for natural disagreements. The verdict therefore depends on the assay length. "Complete" at T may be "not complete" at T′.
**Falsifier.** Sweep assay duration T ∈ {6,12,24,48,96} and impulse over a grid near threshold at dwell 2 and 24. Count natural cases where the instantaneous-basin verdict differs from the terminal-attractor label, or flips with T. Refutation of the criterion as a well-defined completion rule = any flip in a case with valid authorization. Code change: loop over T in the junction run script, recording both labels (≈10 lines; T is already a bound parameter).

### 5. Repeated-impulse wound: authorization-per-transition does not bound physical dose (claim: E for the fixture, H for policy)
**Attack.** v0.1 shows that two +0.6 impulses 0.05 apart cross where one does not. Article II's "one approval per transition" binds one *offering*, not cumulative dose. Two valid events on recurrence ("each occurrence is a new event") could compose into a crossing that neither authorizes.
**Falsifier.** In junction v0.3, issue two independently valid approvals for two separate events on the same organism, Δt apart. Refutation of "authorization does not manufacture outcome" = completion occurs for an event whose own offering, applied alone, yields `OFFER_NO_CROSSING`. Code change: a new test case that calls `propose`/apply twice with event IDs E1, E2 and Δt=0.05 (~20 lines).

### 6. Confession and realization are structural stubs (claim: E as R5 only; substance H)
**Attack.** `Confession` passes on any non-whitespace string. `Realization` passes on any non-empty `behavioural_evidence` list. The code comments admit this. A one-character confession completes forgiveness.
**Falsifier.** Add a case with `Confession(event_id, "x")` and `Realization(event_id, ["."])`. Refutation of any claim that the junction enforces Article II's realization or confession components = COMPLETE is returned. Code change: one test case. Expected to "pass" today, which is the point. Any substance constraint must then be paired with a mutant that accepts prose without content.

### 7. P1–P5 are uncited (claim: N, yet listed under "Established" in §10)
**Attack.** §10 lists P1–P5 conclusions as established. The package contains no probe code, seeds, parameters or raw outputs. Key quantities are not reproducible: "5–17× baseline", "d≤4 and climbing", "ten steps per hop", the transient overshoot.
**Falsifier.** Rebuild each probe from the prose with declared parameters. Refutation of P4's headline = an inferential chain that contains error (spread d≤2) under some coupling or anchoring weight still within the record's description. Refutation of P5 = a nonzero residual after origin release at any tested commitment weight. Until then, demote P1–P5 from "Established" to "Narrated".

### 8. Cross-model review is not independent replication (claim: methodological, N)
**Attack.** Claude and ChatGPT shared prompts, documents and the investigator's framing, and each saw the other's output. Errors that are correlated through shared context (e.g. both v0.2 implementations choosing local learners — see attack 1) pass both. The record counts findings "in both directions". It does not measure blind agreement.
**Falsifier.** Give an outside implementer (human or model) only PROTOCOL.md, with no learner specified and no prior results. Refutation of "convergent" = their history-vs-position sign differs from the packaged sign. Attack 1 already supplies one such disagreement.

### 9. Gospel source versus fixture (claim: design boundary; mapping not claimed but invited)
**Attack.** Nothing in the code is derived from the four Gospels. Parameters such as tilt target, impulse grid and thresholds are numerical choices. Labels such as "dwelling", "offering" and "for those with ears to hear" invite readers to take fixture results as textual findings. §6's close reading even *falsified* the strong reception reading. The fixture still implements a static, receiver-side capacity.
**Falsifier.** Rename every theological identifier to a neutral one (offering→impulse, dwelling→evolve) and rerun. If every result is byte-identical (it must be), then no result bears on the Gospel source. Code change: sed over identifiers. Any claim that survives in the theology after this rename has to rest on argument, not on the runs.

### 10. Minor: the alternative v0.2 run is not a replication of the packaged v0.2
Different seeds (0–11 / 12–23 vs 0–29 / 1000–1011), arms (it adds `fixed_landscape`), impulse grids, and only 144 fitting examples. History is worse there mainly on `fixed_landscape` (0.9583 vs 1.0000), an arm with no history signal by construction. Do not pool the two tables.

---

## What survives the brief
- Authorization ≠ transition on the declared fixture: same impulse 0.60 with valid approval, no completion at dwell 2 and completion at dwell 24. This is untouched, but it is conditional on attacks 4 and 5.
- The v0.3 mutant gate and the degenerate-gate rule are sound methodology.
- Retirement of II.8 by provenance remains a valid process result.
- Direction-transfer fragility (forward-only → reverse) is confirmed by every learner and feature set here: reverse-test accuracy is 0.70–0.95, against ≥0.98 in the mixed regime. That makes it the most robust finding in the reception work.
