# Probes P1–P5 reconstruction — protocol set before the first run

2026-10-24. **RECONSTRUCTION, NOT THE ORIGINAL.** The original P1–P5 code and artefacts are not available. The only source is §4 of *The Developmental Meaning Fork* (loose/1d3bd887…md). This pack declares its own toy model. Its numbers cannot confirm or refute the original numbers; it only checks whether the *narrated qualitative results* reproduce under this declared model. Exploratory engineering experiment, not an external preregistration.

## Declared model (probes.py)
N=24 units on a graph A. Each unit i has belief b_i tracking a latent world value s_i(t).
- World: s_i Ornstein–Uhlenbeck, θ=0.05, σ=0.3, independent per unit (except P4 shared/chain: one common s).
- Evidence each step: e_i = s_i + ε, ε~N(0, 0.3²) (P4 variants change this, below).
- Dynamics (Euler, dt=0.1): b_i' = F_i = k_e(e_i − b_i) + c·Σ_j A_ij(b_j − b_i)/n_i, k_e=1.0, c=0.5, n_i=deg_i (normalised) or 1 (P3 unnormalised).
- Error: a fixed wrong commitment — b_site clamped to W=2.0 for the whole run.
- Commitment weight (P5 only): inertia m, b'=v, m·v' = F − v; m=0 reduces to first order.
- Common random numbers: error and baseline runs share every noise draw.

## Metrics (fixed)
- Tracking error per unit: RMS(b_i − s_i) over steps 1000–3000 of a 3000-step run, 20 seeds (0–19).
- Excess ratio R(d) = mean over seeds and units at graph distance d of err_error/err_baseline.
- Extent d* = largest d with R(d) > 1.10 (0 if none). Contained ⇔ d* ≤ 2.
- Coupling measurable ⇔ R(1) − 1 > 0.01. **Every containment pass also requires coupling measurable** (degenerate-gate guard: a zero-coupling model contains trivially).

## Probes and pass rules (reproduce / partly / not)
- **P1** ring(24). Reproduce: median site ratio ∈ [5,17] AND R(2) < 1.10 AND coupling measurable. Partly: site ratio ≥ 2 and contained but outside [5,17]. Else not.
- **P2** ring, 4×6 periodic lattice, Watts–Strogatz k=4 p=0.1 and p=0.3 (graph seed 7), complete K24. Reproduce: all contained + coupling measurable, AND complete has the smallest R(1)−1. Partly: all contained but dense not most contained.
- **P3** ring and K24 unnormalised; Barabási–Albert m=2 (seed 7) with error on max-degree hub, normalised and unnormalised. Reproduce: all contained + coupling measurable. Mechanism check: anchoring mutant (k_e=0.05, everything else equal) on ring must have d* ≥ 4; if the anchoring mutant is still contained, the anchoring explanation is NOT supported.
- **P4** (truth is a common world s for all): shared evidence on ring (e_i = s+ε); belief-as-evidence on ring (e_i = 0.5(s+ε) + 0.5·mean neighbour belief); inferential chain on a 24-path, unit 0 observes s+ε, unit i>0 has e_i = b_{i−1}+ε, no other coupling, error at unit 0. Reproduce: shared d* ≤ 2; testimony d* > shared d*; chain d* = 23. Partly: chain destroyed but ordering of the other two differs.
- **P5** chain from P4, origin clamped for 1500 steps then released (resumes normal dynamics), 3000 further steps; m ∈ {0, 1, 4, 10}; seed 0. Residual δ_i = |b_i − b_i^baseline|. Damage_i = δ_i at release. Heal step_i = last post-release step with δ_i > 0.01·Damage_i. Steps/hop = slope of linear fit of heal step vs i. Reproduce: final max δ/W < 1e-3 for every m; heal steps increase monotonically with i (wavefront); steps/hop increases with m and is finite; post-release max δ_i > Damage_i for some unit at m=10 but for no unit at m=0. "About 10 steps per hop" is reported, not gated (the step scale depends on dt, which the narrative does not give).

## Degenerate-gate tests (test_probes.py), written with the protocol
Each pass condition is run against a broken model that could satisfy it: zero-coupling (contains trivially → must FAIL coupling gate); k_e=0 ring (must FAIL containment); instant-teleport release (no wavefront → must FAIL P5); never-release (must FAIL residual); verdicts must be strict booleans, prose/truthy values rejected.
