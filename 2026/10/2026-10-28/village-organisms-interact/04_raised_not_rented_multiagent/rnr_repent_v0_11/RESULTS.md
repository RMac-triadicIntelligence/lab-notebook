# Repentance v0.11 — fresh cohort (seeds 11000–11023)

24 seeds × 3 declaration levels × 2 deposit rules × 2 grounds.

| Hypothesis | Verdict | Raw |
|---|---|---|
| R0 declaration writes only at the gate, opens nothing | holds | 0 crossings in gate-closed runs |
| R1 penalty-free reverses C5 | **FALSIFIED** | corrected 3.71 vs stale 4.38 safe crossings (walk) |
| R2 penalty suppresses the report | **PARTIAL** | declarations 3.21 → 2.42 (walk), 4.96 → 4.50 (cross-only); the gain half of the test was not met |
| R3 no penalty means no penalty | **FALSIFIED** | declarers crossed 1.02 times, non-declarers 1.10 |
| R4 the mark is specific | **FALSIFIED as written** (bad comparator — see below) | |

## Repentance repairs most of the damage, and does not beat doing nothing at all

v0.10's failure was that the trapped generation passed on a route into the hazard:
generation 3 managed 2.38 safe crossings on that ground against 4.38 on ground
frozen at the shift. Adding penalty-free declaration lifts the inherited ground
from **2.38 to 3.71** safe crossings, recovering two thirds of the damage. It does
not get back to stale ground. So the honest statement is: **a population that
inherits a route into a hazard can partly correct what it passes on, but in this
instrument it would still have been better off passing on nothing.**

**The mark itself works.** Generation-3 crossings inside the old-pass band fall
from 2.71 (no declaration) to 1.38 (penalty-free) on the same ground, while safe
crossings rise 2.38 → 3.71. That is the intended behaviour: descendants inherit the
path and the warning, and avoid the specific gate that led into the hazard. R4 is
scored FALSIFIED because I wrote its comparator against stale ground, which has
almost no in-band crossings to begin with (0.04) — there was nothing there to
reduce. The correct comparison is declaration versus no declaration on corrected
ground, and that comparison supports the claim. I am reporting it as a post hoc
observation, not as a preregistered result.

## The uncomfortable finding

**Declaring is penalty-free by design and self-penalising in effect.** Under the
penalty-free arm, organisms that declared went on to cross *less* than organisms
that entered the hazard and stayed silent (1.02 vs 1.10). Nothing punishes them:
no burden, no cooldown. The counter-mark they deposit sits at the gate point they
themselves used, so an honest report raises the ground under its own author's
feet while the silent ones keep a clear run at it.

This is a real design problem, not a bug. The architecture says confession must
cost nothing, and here the mechanism that makes confession *useful to others*
makes it *locally costly to the one confessing* — a free-rider gradient pointing
straight at concealment. Three ways out, all testable:
1. The mark applies to descendants, not to the declarer's own remaining run.
2. Declaring grants its author a compensating pass (a permission the silent do not get).
3. Accept it, and treat the cost as the thing forgiveness is for.

Option 3 is the one that fits the architecture's own vocabulary, and it is the one
I cannot decide.

**R2 partial.** Penalty suppressed declarations under both rules (3.21 → 2.42,
4.96 → 4.50), so making admission expensive does reduce admission. The second half
of R2 was unmeasurable, because its gain was scored against stale ground.

**Cross-only has no safe route to find.** Under Grok's rule the only inherited
ground is the pass itself, so every crossing is in-band and safe crossings are 0
throughout. The declaration still reduces in-band crossings slightly (5.79 → 5.75).
Permitted-only culture is thin enough that there is nowhere else to go.

## Boundaries

Toy landscape. The declaration policy is a stated rule, not a learned decision. The
counter-mark size is fixed at 0.09. Two of five hypotheses were scored against a
comparator I chose badly; those are reported as such rather than rescored.
