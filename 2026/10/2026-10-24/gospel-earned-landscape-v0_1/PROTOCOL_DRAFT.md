# Earned landscape v0.1 — protocol DRAFT for PI review

Raised, Not Rented. PI: Rusty Williams McMurray. Drafted 24 Oct 2026.
**Status: draft. Nothing has been run. No code exists yet.** This file is meant to be frozen, with the PI's decisions in §9, before the first confirmatory run. It is an exploratory engineering experiment with a confirmatory core. It is not an external preregistration.

Inherited unchanged: the potential V(x,a) = x⁴/4 − x²/2 − a·x and dx/dt = x − x³ + a (`reception.py`, v0.1). Also inherited unchanged: the frozen-geometry capacity measure (critical positive impulse = saddle − x, measured before any offering), and the junction v0.3 Authority and JunctionOrganism authorization path, checked by AST hash. **The only thing that changes is the tilt law da/dt.** In v0.1–v0.3 it was `rate·(evidence(t) − a)`, with `evidence(t) = 0.31 + 0.015·sin(0.35t + φ)`. That is an exogenous clock with a positive target. The record (§6) says plainly that the improvement with dwelling "was prescribed". This experiment removes that prescription.

---

## 1. Questions, and what counts as YES / NO / UNRESOLVED

**Q1 (junction contrast).** With the tilt earned rather than scheduled, does there exist, in a pre-declared fraction of histories, one fixed impulse I with valid authorization at both checkpoints such that the offering yields `OFFER_NO_CROSSING` at an earlier dwell checkpoint and `COMPLETE` at a later one, or the reverse? The outcome must be predicted by the pre-offering capacity measured at each checkpoint.

**Q2 (boundary approach).** Does the pre-offering critical impulse c(t) fall with dwelling? In other words, does the boundary come toward the organism, as opposed to the organism walking to the boundary?

**Q3 (is it earned).** Is any Q1/Q2 effect attributable to path dependence? That is, is it present in the earned arm and absent or materially smaller in the shuffled-history arm, which has the same tilt statistics and the link to the organism's own path cut?

Fixed verdicts (thresholds marked ⟨PI⟩ are set in §9 and then frozen):

| Verdict | Condition (primary arm, confirmatory seeds) |
|---|---|
| **YES** | Q1 contrast rate ≥ ⟨PI: 10 %⟩ of eligible histories, with the 95 % bootstrap CI lower bound > 0. **And** Q3: earned minus shuffled contrast rate has a CI lower bound > 0. **And** every gate in §3 passes. Q2 is reported separately as YES-approach, NO-entrenchment or flat. |
| **NO** | Gates pass, and either the contrast rate CI upper bound < ⟨PI: 2 %⟩, or the earned and shuffled rates are indistinguishable (difference CI contains 0 and its upper bound < ⟨PI: 3 pp⟩). A NO is reported as a result, not a failure. |
| **UNRESOLVED** | Any gate fails. Or > 20 % of histories leave the two-basin regime (|a| ≥ 2/(3√3) ≈ 0.385). Or a verdict flips between the T=24 instantaneous-basin rule and the T=96 terminal-attractor label in more than 5 % of contrast cases (§5). Or the CIs straddle the YES and NO bands. |

Q2 is descriptive, with its sign fixed in advance. Median Δc = c(24) − c(2) < 0 with CI excluding 0 counts as "approach". > 0 counts as "entrenchment". Otherwise "flat". **Entrenchment is a live possibility under the primary mechanism and is not a failure of the experiment.** It would say that dwelling on one's own path alone deepens the current basin, and that any approach requires something the organism does not generate itself.

## 2. Earned-tilt mechanisms

Shared notation. x̄ is the organism's own commitment: an exponential moving average of its own position, dx̄/dt = (x − x̄)/τ. a(0) = 0, so the landscape starts symmetric. x(0) = x̄(0) = −1, so the organism starts in the left basin. That initial position is the only asymmetry, and it belongs to the organism. **No law may take t as an argument.** No law may read impulse, approval, offering or outcome.

### M-A: Commitment only (pure self-reference; P4's inferential regime)
da/dt = r · (κ · x̄ − a)

The landscape follows where the organism has been. With κ > 0, dwelling deepens the current basin (entrenchment). The sign of κ is a modelling choice that settles the direction of Q2 by itself, so **M-A cannot answer Q2 alone**. It is the w = 0 limit of M-B and serves as its self-reference comparator. It is the dynamical analogue of P4, where a unit inherits only what its earlier state concluded.

### M-B (PRIMARY): Commitment corrected by independent first-hand evidence
da/dt = r · [ (1 − w) · κ · x̄ + w · ô(t) − a ]
dô/dt = (o(t) − ô)/τ_o,   o(t) = θ + η(t)

θ is a world fact that the organism neither chooses nor affects, drawn per history. η is observation noise, white with standard deviation σ_o and pre-seeded. ô is the organism's running first-hand estimate. Path dependence comes from x̄. Correction comes from o, which is first-hand and not inherited from the organism's own conclusions, as P4 prescribes. The landscape moves toward the boundary only if the world's evidence opposes the organism's commitment strongly enough to beat entrenchment. Neither the sign nor the size of that outcome is set by the experimenter.

M-B is primary because (i) it is the minimal law in which approach can arise without being chosen, (ii) it directly tests the P4 design constraint (first-hand observation alongside the chain), and (iii) its w = 0 limit gives M-A for free.

### M-C (EXPLORATORY): Unresolved error as emergent burden-like noise
dx = (x − x³ + a) dt + σ(t) dW,   σ(t)² = σ₀² + β · Σ_{e ∈ unresolved} max(0, −x̄ · ô)

Each unresolved error event e contributes excess noise for as long as it is unresolved, scaled by the current mismatch between commitment and evidence. The tilt follows M-B. **There is no burden variable.** Burden is *measured* as excess variance of dx over σ₀², from the trajectory alone. On release, event e leaves the unresolved set, so its term is gone in full, not decayed. Whether removing a cause this way respects "observed, not decremented" is a PI decision (§9, D4). That question is why M-C is exploratory only.

### Guaranteeing zero hidden drift
1. **Reflection equivariance.** V(x,a) = V(−x,−a). Each law is odd under (x, x̄, a, θ, η) → −(·). Test: mirror the initial state and the noise. The trajectory must mirror to ≤ 1e-12 at every step. A mutant with an added constant +0.01 in da/dt must fail this test.
2. **Antithetic θ.** Each seed s uses θ = +|θ_s| and its partner uses −|θ_s|, with the same |θ_s| and η → −η. Mean a over each pair must be 0 to ≤ 1e-12 at every t.
3. **No clock.** AST check that no tilt function takes `t`, or calls `sin`, `cos` or anything time-indexed.
4. **No outcome leakage.** AST and import check that the tilt module cannot read authorization, impulse or outcome objects. The mutant "tilt += 0.05 after approval" must be detected by the outcome-independence test (§3, G7).
5. **Null arm Δc = 0 exactly** (a frozen at 0). This catches integrator bias.

## 3. Arms, controls and degenerate-gate guards

| Arm | Tilt law | Role |
|---|---|---|
| E-B (primary) | M-B | Confirmatory |
| E-A | M-A (w = 0) | Confirmatory comparator: does self-reference alone suffice? |
| S (supplied) | Old q(t) schedule, v0.3 parameters | Positive control. Must reproduce thr ≈ 0.8853 at dwell 2 and 0.4341 at dwell 24, and the (NO_CROSSING, COMPLETE) contrast at I = 0.60, to 1e-4. |
| N (null) | a ≡ 0 | Negative control. c(t) constant, so the contrast rate must be exactly 0. |
| H (shuffled history) | Replays recorded a(t) trajectories from E-B, permuted across histories within the same θ-sign stratum, as a supplied schedule | Path dependence broken. The multiset of tilt trajectories is identical, so the tilt statistics match exactly. |
| E-C | M-C | Exploratory only |

**Degenerate-gate guards.** For each pass condition: a broken model that would also satisfy it, and how this protocol rules that out.

| # | Pass condition | Broken model that also passes | Guard |
|---|---|---|---|
| G1 | Contrast appears in E-B | A clock or positive target smuggled into the "earned" law (the old schedule renamed) | Equivariance test, no-clock AST check, antithetic mean-zero check. The H arm must not equal E-B. |
| G2 | Δc < 0 (approach) | Integrator bias, or the organism drifting rather than the boundary moving | N arm gives Δc = 0 exactly. Half-step rerun on a fixed 24-history sample, with verdict unchanged. Gap decomposition (closure = (x−x₀) − (s−s₀)) reports the boundary and organism shares separately. |
| G3 | E-B differs from H | A shuffle that changes the statistics (lengths, strata, initial a) and so differs trivially | Assert the multisets of a(t) are identical, the θ-sign strata are matched, and the per-history checkpoint distribution of a is identical. |
| G4 | Completion occurs | Authorization manufactures completion (complete whenever approved) | The v0.3 "complete-on-approval" check: E-B must contain valid-authorization `OFFER_NO_CROSSING` cases. A mutant that always completes must fail. |
| G5 | Non-crossing occurs | Reject-everything, so nothing ever completes | Reuse the v0.3 reject-everything mutant. Arm S must show COMPLETE. |
| G6 | Capacity predicts outcome | Frozen-geometry identity (predictor = definition) | Frozen agreement is reported as an instrument check only. The scientific metric is agreement under *continued earned dwelling*, where the boundary can move during the assay. Misses are preserved and counted. |
| G7 | Outcome independent of authorization path | Tilt reads approval or outcome (the "+0.05 after approval" mutant) | Run every offering twice, with valid and with withheld authorization. The physical endpoint x must be bitwise identical; only the record differs. The mutant must fail. |
| G8 | Regime-loss cases excluded honestly | Loss of bistability counted as a crossing | `geometry()` ValueError is recorded as `REGIME_ABSENT` and never as COMPLETE. The count is reported, and > 20 % → UNRESOLVED. |
| G9 | (M-C) Release returns noise to baseline | Release sets σ to σ₀ by fiat, or writes a burden variable | AST check: the release path writes nothing in the dynamics state except the unresolved-event set. The "decrement burden" mutant must fail. Burden is estimated only from the trajectory. |

Gate rule (inherited): the run exits zero only if the normal suite passes **and** every mutant fails exactly its required cases.

## 4. Investigator settlements as invariants, and how each is checked in code

| Settlement (§2 of the record) | Code check |
|---|---|
| Burden emergent and observed, never declared or decremented | No field matching `burden`, `turmoil` or `noise_level` in any state dataclass (reflection over fields). Burden is estimated by a pure function of the recorded trajectory. G9 mutant. In E-A and E-B there is no noise term, so the invariant holds vacuously, and this is stated rather than claimed as a test. |
| Release total: no residual, no floor | E-C only. After release, excess-variance estimate over a fixed window vs. a never-burdened matched control (same seed and θ). Equivalence margin ⟨D4⟩. A floor or slow decay is a reported violation, not something to tune away. |
| One approval per transition | The v0.3 Authority is reused unchanged (AST hash). Re-applying a consumed approval must be refused. In §5's repeated-impulse study, each event has its own approval and binding. A second approval for the *same* event must be refused. |
| Restored state is position, no status field | State fields are exactly {x, x̄, a, ô, t}. Reflection test: no `status`, `restored`, `forgiven` or boolean flag. The completion verdict is a function of x and geometry only. Mutant with a `restored=True` field must fail the schema test. |
| Non-self-authorization (all participants) | The organism and tilt modules cannot import signing keys (import check). The organism cannot create an approval for itself (inherited v0.3 case). New: the tilt law cannot read approvals (G7). The landscape must not become a back door through which approval moves the organism. |

## 5. Wounds: measured, not hidden

**Repeated-impulse composition (brief attack 5).** For each eligible history at dwell 2 and 24, take impulse pairs (I₁, I₂) from the grid where each alone yields `OFFER_NO_CROSSING`. Apply them as two separately authorized events at Δt ∈ {0.05, 0.5, 2, 8}. Report the composition rate: the fraction where the pair completes. Report it per arm. No policy is introduced to suppress it. A non-zero rate is recorded as "authorization per transition does not bound physical dose" in this fixture. Whether policy must respond is held open, as in §10 of the record.

**Assay-length dependence (brief attack 4).** Every offering is assayed at T ∈ {6, 12, 24, 48, 96}. Both labels are recorded: instantaneous basin at the end of T (the v0.3 operational rule) and terminal attractor at T = 96 with the landscape continuing to evolve. Report the flip rate across T and the disagreement rate between the two labels. **The confirmatory verdict uses T = 24 (the inherited rule), and a contrast case counts only if its terminal-attractor label agrees.** If > 5 % of contrast cases flip, the verdict is UNRESOLVED. The rule is not quietly replaced.

## 6. Fixed design: seeds, parameters, metrics, analysis

**Calibration (exploratory, seeds 0–19).** Used only to fix κ, w, r, τ, τ_o, σ_o and |θ| ranges such that ≥ 90 % of histories stay bistable through t = 96. Outcome metrics (contrast, Δc) **must not be computed** during calibration. Code enforces this: the calibration script has no access to the offering function. Parameters are then written to `params_frozen.json` and hashed before confirmatory seeds are generated.

**Proposed starting values (to be confirmed by calibration, not by outcome):** r = 0.15 (inherited), τ = 4, τ_o = 2, κ = 0.25, w ∈ {0, 0.25, 0.5, 0.75}, with w = 0.5 primary. |θ| ~ U[0.10, 0.35], σ_o = 0.05, dt = 0.02, RK4 (inherited). For M-C: σ₀ = 0.02, β = 0.05.

**Confirmatory (seeds 1000–1199).** 100 antithetic pairs give 200 histories per arm. Checkpoints at dwell 2, 6, 12, 24, 48. Impulse grid 0.30–1.50 in steps of 0.05. The H permutation is drawn from a fixed RNG seed, 777.

**Metrics.** c(t) per checkpoint. Δc = c(24) − c(2). Contrast rate (either direction, reported by direction). Gap-closure decomposition (boundary vs organism share). Continued-dwelling prediction misses. Composition rate. Assay flip rate. REGIME_ABSENT count. M-C only: excess-variance burden estimate before and after release.

**Analysis.** History is the unit; the pair is the resampling unit (antithetic pairs are not independent). 10 000 bootstrap resamples, percentile 95 % CIs. No p-values, no significance claim. **The one confirmatory contrast is E-B vs H at w = 0.5.** Secondary: E-B vs E-A, the other w levels and Q2 sign. Everything else, including E-C, any post-hoc variant and any parameter outside the frozen file, is labelled EXPLORATORY in outputs and text.

**Process.** Predictions from pre-offering capacity are written by a separate process before outcomes are computed (v0.2 practice). Manifest with file hashes. Every negative result is preserved.

## 7. What a result would and would not mean

- YES says only this: on this declared fixture, a junction contrast arises from a tilt that depends on the organism's own path plus independent evidence, does not arise when that dependence is cut, and needed no scheduled target. It does not show that development produces meaning, that the law is the right one, or anything about an LM substrate. Clean x is still privileged (brief attack 2).
- NO, if gates pass, is the first result in the programme that bears negatively on the central fork claim *in this form*. It should be written up as such.
- θ is still supplied by the experimenter as a fact about the world. "Earned" here means the landscape's *response* is earned. The evidence itself is not earned. A hostile reader will say this, and the write-up should say it first.

## 8. Out of scope
Retry policy after non-crossing. Confession substance. Bilateral authority dynamics. Any LM or memory substrate. Changes to Article II. No new reception law is introduced if the result is NO.

## 9. DECISIONS FOR THE PI

Each has a recommended default. Answer "yes" or pick an option.

**D1. What may development depend on?**
Recommended: **the organism's own past positions (commitment x̄) plus independent first-hand evidence about the world (θ), and nothing else.** No clock, no outcome labels, no approvals.
Alternatives: (a) own path only (M-A primary); (b) also the outcomes of its own past offerings.

**D2. Do corrections from independent evidence count as development?**
Recommended: **yes, provided the evidence is first-hand and the organism's response is through its own dynamics (M-B primary).** M-A runs as the self-reference comparator.
Alternative: no. Then M-A is primary, and κ's sign must be fixed by you in advance, knowing it settles Q2.

**D3. Sign of commitment (κ).**
Recommended: **κ > 0: dwelling deepens the current basin ("memory persists and reshapes the field").** This biases *against* the hoped-for approach, so any approach found must be earned against it.
Alternative: κ = 0 (no self-reinforcement).

**D4. Burden-like noise (M-C).**
Recommended: **keep it exploratory in v0.1.** Treat removal of an event from the unresolved set as release removing the cause, and burden as only ever measured. Equivalence margin for "total": excess variance within 5 % of matched control.
Alternative: drop M-C entirely from v0.1.

**D5. Refutation threshold.**
Recommended: **YES needs contrast rate ≥ 10 % with CI lower bound > 0, and earned − shuffled CI lower bound > 0. NO is contrast CI upper bound < 2 %, or earned − shuffled indistinguishable with upper bound < 3 percentage points.**
Pick other numbers if you prefer, but before the run.

**D6. Completion rule.**
Recommended: **keep the inherited rule (instantaneous basin at T = 24) for the verdict, require terminal-attractor agreement, and mark the result UNRESOLVED if > 5 % of contrast cases flip.**
Alternative: switch to the terminal-attractor label as the rule. That is a change to junction semantics and should be recorded as such.

**D7. Repeated-impulse wound.**
Recommended: **measure and report the composition rate only. No policy change in v0.1.**
Alternative: also run an exploratory "cumulative-dose binding" variant.

**D8. Independent read.**
Recommended: **freeze this protocol and send it with the falsification brief to a reader outside the two original models before the confirmatory run.**
Alternative: run first and review after.
