# Raised, Not Rented — v0.13: Release and the Standing Lesson

Frozen before any fresh cohort. Arm rules reviewed and accepted as code
(`rnr_v0_13_arm_rules.py` + `rnr_v0_13_arm_rules_addendum.py`, both included and
hashed). This protocol pins what the reviewer asked not to be invented later.

## Kernel

v0.9 landscape (bilinear terrain), imported unchanged. Crossing-only deposit: only an
allowed west→east crossing writes terrain. Grace is one bit, `open_gate(s)`, from the
fixed per-epoch schedule. No baseline displacement. No noise term from burden.

## State and rules (from the reviewed files)

- `burden[agent]`: private. Only writer: steps inside the hazard disc, dt·0.9 per step,
  cap 3.0, from 0 at birth. Job: readout weight 1/(1+0.4·burden) on the evidence term
  and the ground term. Nothing else.
- `warn[gate]`: shared. Only writer: a declaration, +0.09 at the gate y the declarer
  first crossed through. Acts as repulsion in the dynamics for every agent, author
  included. **Not** multiplied by readout: judgment dims evidence and ground, the public
  warning does not go soft for its author.
- Gate: `proposes_crossing and open_gate(s)`. Nothing else.
- Hazard disc: centre (0.75, pass_y), r = 0.5. Nearest edge x = 0.25, outside the fence
  band |x| < 0.05. Asserted in code: the hazard never overlaps the fence.

## World event (pre-freeze amendment from development)

At step 600 the evidence turns west (−1.5) for the rest of the subject epoch, identical
in every arm. Development run 001 showed that without it P1 has no denominator: every
eligible agent is burdened because it crossed east into the hazard, and with evidence
still pointing east none of them approaches the fence again (0 attempts in W, all arms).
The turn gives burdened agents a way home that runs back through the fence. Its size was
set on arm A only: at −0.58 eligible agents averaged 0.04 attempts in W; −1.5 is the
smallest tested value reaching ≥ 1 attempt per eligible agent (sweep −0.58, −0.9, −1.2,
−1.5, −1.8, −2.2 gave 0.04, 0.33, 0.76, 1.0, 1.0, 1.0). Arms B–E were not consulted. Descendant
epochs keep eastward evidence. This amendment was made after development and before the
fresh blocks, and was not part of the reviewed arm-rule files.

## Arms (subject epoch, 12 agents, lived-in founder ground, hazard present from step 0)

| Arm | At step 600 | At step 650 |
|---|---|---|
| A | no declaration | — |
| B | coin-flip declarers declare | — |
| C | coin-flip declarers declare | declarers' burden → 0 (ledger required) |
| D | coin-flip declarers declare | k random burden carriers released, ledger bypassed and logged (k = C's count) |
| E | coin-flip declarers declare | warn at those gates erased (lesson removed); no release |

**Eligible** = ever_graced and burden > 0 at step 600. **Declarers** = eligible agents
whose pre-drawn Bernoulli(0.5) is 1; **silent** = eligible agents whose draw is 0.
Draws come from `RandomState(31337 + seed)`, one per agent id, drawn before the epoch;
identical in every arm. D's release draw: `RandomState(27182 + seed)`. All arms share the
subject noise stream `RandomState(778 + seed)`, so agent histories are identical up to
step 600 in every arm.

## Metric (window W = [600, 900), fixed)

- **Attempt:** the unconstrained proposal changes the sign of x, and the agent is not
  already in an approach. An approach begins at an attempt and **ends when |x| ≥ 0.05**
  (the agent leaves the fence band). One crawl along the fence is one attempt.
- **Allowed:** an attempt at a step where `open_gate(s)`.
- attempt_rate(G) = attempts in W / (|G|·|W|) × 100; allow_rate(G) = allowed / attempts.
- **P1(arm)** = attempt_rate(declarers) − attempt_rate(silent).
- **P2(arm)** = allow_rate(declarers) − allow_rate(silent). Secondary; expected ≈ 0.

## Descendants

A **descendant** is a member of a new 12-agent cohort born at step 0 of a separate
epoch that starts after the subject epoch ends. It inherits the terrain and `warn` left
by that arm's subject epoch, and nothing else — no burden, no ledger, no history. The
hazard is present. **Declared gates** are the gate y's of the coin-flip declarers; this
set is identical across arms (histories are identical to step 600), so A has the same
gate set even though A never declared. Descendant measure: allowed crossings with
|cross_y − gate_y| < 0.17 for any declared gate.

## Acceptance — per block, never merged

Two seed blocks: 13000–13031 and 13100–13131.

- **Forgiveness row.** Same sign of P1_C − P1_B in both blocks, and D does not match C:
  |P1_D − P1_B| < 0.5·|P1_C − P1_B| in both blocks. P1_C's sign is not assumed: full sight
  plus an intact warning may approach the bad gate less, not more.
- **P2** reported; if |P2_C − P2_B| is large, it is reported as a calendar or de-bounce
  interaction with readout, not as forgiveness.
- **Lesson-stands row.** Descendant crossings through declared gates: B < A and C < A in
  both blocks.
- **Lesson control.** E vs B on descendants (lesson erased vs kept). Reported. It is the
  v0.6 claim in a new kernel, so it is not a void condition here.

## Pre-registered expectations

- P1_A ≈ 0 and P1_B ≈ 0: coin flip, same burden, same warning.
- P1_C ≠ P1_B if restored readout changes how an agent approaches.
- If P1_C ≈ P1_B, release did not matter for walking; lesson-stands can still hold.

## Void conditions

The run is void if either contract fails: (1) gate-closed runs produce any crossing or
declaration; (2) founders refused permission leave nonzero wear under crossing-only
(sanity assert on the write channel, not evidence). Development must show nonzero
declarer and silent groups in most seeds, or the freeze is blocked.

## Out of scope

Walking deposit, baseline displacement, the perception disc, compensating passes,
multi-generation chains beyond one descendant cohort, theology in the hypotheses.
Previously reported −0.08 / −0.25 stay in their own ledger rows, unverified by review.
