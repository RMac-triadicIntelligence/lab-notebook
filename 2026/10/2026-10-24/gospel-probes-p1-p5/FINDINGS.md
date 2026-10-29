# Probes P1–P5 reconstruction — executed findings

**Reconstruction, not the original.** Agreement or disagreement below is with the *narrated qualitative claims* under *this* declared model. Nothing here verifies the original numbers.

Preregistered verdicts: **P1 reproduced · P2 not reproduced (as gated) · P3 partly · P4 reproduced · P5 not reproduced (as preregistered); P5 reproduces qualitatively only in a post-hoc, noise-free variant.**

## P1 — reproduced
Ring of 24, 20 seeds. Site error ratio median 6.70× (mean 6.50×), inside the narrated 5–17×. R(1)=1.416, R(2)=1.0007, extent d*=1. Coupling measurable (R(1)−1=0.42), so containment is not the zero-coupling triviality.

## P2 — not reproduced as gated; the gate caught something real
Ring, lattice and WS p=0.1/0.3 are all contained (d* ≤ 1; R(1)=1.42/1.11/1.10/1.14). Complete K24 has R(1)=1.0057. That is the "most contained", but it is **below the preregistered 1% coupling-detectability gate**. With degree normalisation, each edge carries 1/23 of c, so in this model the dense graph looks contained because its coupling is diluted out of view. The degenerate-gate rule flagged exactly this case. Under the preregistered rule, P2 fails. Read loosely ("containment everywhere, dense lowest"), it holds.

## P3 — partly
With normalisation removed, and with the error on a Barabási–Albert hub (normalised and unnormalised), containment held: ring_unnorm R(1)=1.59, d*=1; K24_unnorm R(1)=1.27, d*=1 (now measurably coupled); BA hub norm d*=1; unnorm R(2)=1.058, d*=1. **The attack fails and the finding holds, as narrated.** Unnormalised K24 being contained while coupled also argues against dilution as the *only* reason. Mechanism check: weakening evidence anchoring (k_e 1→0.05) breaks containment (d*=3, R(1)=1.98, R(2)=1.37). The direction supports anchoring, but the preregistered threshold was d* ≥ 4, so this counts as partial.

## P4 — reproduced
Shared evidence d*=1 (R(1)=2.04, versus 1.42 independent: it bends a little). Belief-as-testimony d*=2 (R(1)=3.03, R(2)=1.46, R(3)=1.06: bends further). Inferential chain d*=23: every one of the 24 units is damaged (R from 10.3 at the origin to 2.21 at the tail). The ordering peers < testimony < inheritors reproduces. The narrated "d≤4 and climbing" for testimony is only d≤2 here.

## P5 — preregistered run failed; post-hoc variant reproduces
Preregistered (noisy chain, commitment weight = inertia m ∈ {0,1,4,10}): m=0 healed to residual 0 at ~14 steps/hop. m=4 and m=10 **did not heal**. Underdamped stages in a 23-stage chain amplify fluctuations near resonance, and the residual blew up (≈2e4 and ≈2e10 × W). Separately, "Damage = δ at the release step" was a defective metric. In a noisy chain, damage fluctuates, so post-release δ exceeded it even at m=0. This is a degenerate gate of our own, recorded here.
Post-hoc (p5_posthoc.py, noise-free, damage = max over the clamp window, m ∈ {0,…,2}): residual → 0 for all m (≤2e-17). It heals as a monotone wavefront at **10.0 steps per hop** (half-recovery). That number is simply 1/(k_e·dt) = 1/(1·0.1), so it echoes our parameters and corroborates nothing. Weight slows healing (1% heal: 13.3 → 28.2 → 60.4 steps/hop at m=0, 1, 2). The post-release transient exceeds damage at m=2 (1.48×) but not at m=0 (1.00×). **Qualitatively reproduced, post-hoc only.** "Weight slows but does not stop" holds only below the amplification regime. At higher weight, in this model, the chain does not heal at all.

## Surprises
1. The coupling-detectability gate demoted the dense-graph result.
2. Commitment-as-inertia can make an inferential chain unstable. That is a sharper version of "a chain contains nothing".
3. The "10 steps per hop" is a parameter echo here, and may have been one originally.
