# Raised, Not Rented — Permitted Culture Battery v0.10

Frozen before the fresh cohort. Takes the rule from Grok's ground-0.3-cut — in his
kernel, couplings deposit **only at an authorized crossing** — and makes it a
factor in the Commons landscape, where wear has so far come from ordinary walking.

The question this opens: is shared ground a record of *use* or a record of
*permitted transitions*? Under walking-deposit, a path can form that nobody was
ever permitted to make, and later generations inherit it. Under crossing-only
deposit, the commons can only accumulate through the gate.

Kernel: v0.9 `commons.py`, imported unchanged (hash pinned in run.json). New code
is `permitted.py` only.

## Factors

| Factor | Levels |
|---|---|
| Deposit rule | walk (v0.9: walking and crossings wear the ground) / cross-only (Grok's rule: only authorized crossings deposit) |
| Founders' authorization | granted (normal grace schedule) / refused (grace never opens for the founders) |
| Ground | lived-in / fresh / shifted (same routes, moved in y) |
| Perception | on / off (post-shift cohorts only) |

24 conditions × 24 seeds. Constants, phases and calibration inherited from v0.9.

## Phases

1. **Founding** (900 steps) under the authorization level.
2. **Arrival A** — generation 2, pre-shift, as in v0.9.
3. **The season turns** — old pass silts, hazard east of it.
4. **Arrival B** — a *new* cohort that arrives after the shift and never saw the
   good season. This is the trap test, with a denominator by construction.
5. **Generation 3** on corrected ground (what Arrival B left) versus stale ground
   (frozen at the shift).

## Fixes carried from v0.9's failures

- Declines are counted as **events** (first refusal per approach to the fence), not
  per step. v0.9's H-I5 numbers were step counts and were not interpretable.
- The trap cohort arrives after the shift, so the empty-denominator failure of
  v0.8/v0.9 cannot recur by construction.

## Hypotheses

- **C0 (contract).** Gate closed → zero crossings, every condition.
- **C1 — unpermitted traffic builds culture under the walk rule.** With founders
  refused, walk-deposit still leaves wear and still gives Arrival A an advantage
  over fresh ground; cross-only leaves wear ≈ 0 and no advantage. *Falsified* if
  refused+walk gives no advantage, or if refused+cross-only gives one.
- **C2 — permitted-only culture still transmits.** With founders granted,
  cross-only ground gives Arrival A an advantage over fresh. Predicted smaller
  than walk-deposit's advantage. *Falsified* if cross-only ≤ fresh.
- **C3 — the trap is real.** Arrival B on lived-in ground, perception off, enters
  the spoiled ground more than on fresh ground. *Falsified* if lived ≤ fresh.
- **C4 — perception rescues without costing the benefit.** For Arrival B on
  lived-in ground, perception on cuts blight entries by at least half while
  keeping crossings above fresh. *Falsified* otherwise.
- **C5 — corrected ground beats stale ground for generation 3**, reported per
  deposit rule. *Falsified* if stale ≥ corrected under both rules.

## Boundaries

Toy landscape; not Grok's kernel and not the v0.4 learner. "Authorized deposit" is
a rule imposed here, not an emergent property. Hazard perception is a fixed-radius
designed channel.
