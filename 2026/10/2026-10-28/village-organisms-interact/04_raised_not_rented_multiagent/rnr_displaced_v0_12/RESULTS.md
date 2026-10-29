# Universal Displacement v0.12 — fresh cohort (seeds 12000–12023)

24 seeds × 3 displacement sources × 2 availability × 2 restoration × 2 grounds.

| Hypothesis | Verdict | Raw |
|---|---|---|
| V0 contracts | **HOLDS** | 0 crossings and 0 declarations with the gate closed; ledger entries = marks deposited, every run |
| V1 the channel restores | **FALSIFIED** | post-declaration crossings: declarers 0.04, non-declarers 0.29 |
| V2 the clean organism gains | **FALSIFIED as scored**, supported on the population measure | clean-organism crossings after declaring 0.07 vs 0.06; but cohort crossings 4.75 (universal) vs 3.63 (incident-only) |
| V3 restoration closes the gap | **FALSIFIED** | declarers 0.04 vs non-declarers 0.29 even with a pass issued |
| V4 intrinsic vs inherited | reported | founders crossed 8.5 (intrinsic) vs 10.2 (inherited/none); gen-2 reached the fence 8.8 in both displaced arms vs 5.0 undisplaced |
| V5 third generation | **FALSIFIED** | corrected 2.4–3.0 vs stale 2.7–3.8 across all three sources |

## What held

**All four architectural changes are mechanically sound.** Grace precedes
declaration (no declaration ever fired before a broadcast, in any run). The
gate-holder's ledger matched the marks exactly. Declaration wrote only at gate
points actually used, and burden release followed it at the stated lag. The
ordering grace → repentance → forgiveness is enforceable, and it held under
24 seeds and 576 condition-runs.

**Universal availability beats incident-only at the population level.** With
restoration standing, cohorts under universal declaration crossed 4.75 times on
average against 3.63 under incident-only — the arm where only organisms with a
logged incident may declare. Clean organisms declared 7.9 times per cohort and
their burden went to 0.0, against 1.0 for the clean organisms who were not
allowed to declare. So opening the channel to everyone did change the population,
which is the closest thing here to your premise being load-bearing.

## What failed, and it is the same failure three ways

**V1, V2 and V3 all fail on the individual measure: declaring does not pay the
declarer.** After the declaration step, declarers crossed 0.04 times on average
and non-declarers 0.29 — about seven times worse. Issuing a compensating pass
barely moved it (0.014 → 0.043). This is v0.11's finding, larger rather than
smaller, and the restoration fix I proposed does not repair it.

The mechanism is now clear. Declaring raises ground at the gate the declarer
used, and that is the gate it is standing nearest to. The pass it receives is
one crossing; the mark it deposits obstructs every crossing it would have made
afterwards. Individually costly, collectively useful — the population gains
(4.75 vs 3.63) while the individual declarer loses. That is a textbook public-good
structure, and this kernel says repentance sits squarely in it.

**Displacement made generation 2 better at reaching the fence, not worse** (8.8
vs 5.0 undisplaced). That contradicts change 2's intent. The extra noise from
baseline burden shakes organisms out of the west basin more often than the
degraded evidence-reading holds them back. Displacement as implemented is partly
a kick, not only an impairment. Anything read from the displaced arms inherits
that confound.

**V5 failed again.** No displacement source produced a third generation that did
better on corrected ground than on stale. v0.11's 3.71 was not beaten by any arm
here (best 3.04).

## What this hands back

Your intuition that everyone starts wrong is implementable and coherent, and the
ordering you specified holds. What the kernel keeps saying is that **a declaration
that writes at the gate is a gift to others and a cost to the one who makes it.**
Three readings, and the choice is yours:
1. That cost is precisely what forgiveness releases, and the model should let
   release remove the declarer's own obstruction while leaving it for others. That
   makes forgiveness load-bearing rather than decorative.
2. Restoration should be larger than one pass: standing, not a token.
3. The public-good structure is the truth of the thing, and repentance is
   genuinely costly to the penitent. Then "no penalty for repentance" is a claim
   about what the *conductor* imposes, not about what the act costs.

Reading 1 is the one I would test next, and it is a one-line change: release
lifts the declarer's own mark, not the record of it.

## Boundaries

Toy landscape. Baseline burden, degradation coefficient, mark size and release lag
are fixed constants. The displacement implementation has the noise confound named
above. One theological reading among several; the kernel tests mechanics, not
doctrine.
