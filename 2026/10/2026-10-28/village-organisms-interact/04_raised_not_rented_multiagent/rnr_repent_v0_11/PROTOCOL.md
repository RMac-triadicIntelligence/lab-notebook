# Raised, Not Rented — Repentance Battery v0.11

Frozen before the fresh cohort. v0.10 ended with inheritance faithfully passing on
an error: generation 3 did worse on the ground generation 2 left (2.29 safe
crossings) than on ground frozen at the shift (4.13). The population that walked
into the hazard wore a route into it and had no way to say so.

v0.11 adds the missing operation.

## Repentance, as specified

**Declaration is an action the organism takes itself.** It requires no permission,
because it is not a transition — it is a report. It is available only to an
organism that actually entered the hazard.

**It writes at the gate, and only at the gate.** A declaration deposits a
counter-mark (raised ground) at the fence point the organism crossed through to
reach the hazard: coordinates (0, cross_y). The worn route it walked afterwards is
left exactly as it is. Forgiven, not forgotten: descendants inherit the path and
the warning, and the history is not rewritten.

**It comes first.** Burden release is unavailable to an organism that has not
declared. v0.10 and earlier released burden with no declaration at all, which was
forgiveness without repentance.

**Declaration policy (stated, not tuned).** An organism declares when the burden it
would take on by declaring is lower than the burden it already carries. Under
penalty-free that condition is always true (cost 0). Under penalized, declaring
costs +1 burden and forfeits crossing for 150 steps, so only organisms carrying
more than that declare. This is the concealment mechanism: make admitting an error
expensive and the ones with least to report are the ones who report.

## Factors

| Factor | Levels |
|---|---|
| Declaration | none (v0.10 baseline) / penalty_free / penalized |
| Deposit rule | walk / cross_only (Grok's rule) |
| Ground | lived-in / fresh |

3 × 2 × 2 = 12 conditions × 24 seeds. Declaration happens at step 600 of the
post-shift epoch, so its penalty and its mark both act inside the same run.
Perception is off throughout: this battery is about correcting an error that was
actually made, not about avoiding it.

## Hypotheses

- **R0 (contract).** A declaration never opens a gate (gate-closed runs stay at 0
  crossings), never shrinks the hazard, and writes only at the fence column.
- **R1 — penalty-free repentance reverses v0.10's C5.** Generation 3 on corrected
  ground achieves more safe crossings than on stale ground, and more than the
  no-declaration arm's corrected ground. *Falsified* if corrected ≤ stale under
  penalty-free.
- **R2 — penalty suppresses the report.** Declarations are fewer under penalized
  than penalty-free, and its generation-3 benefit is smaller. *Falsified* if
  penalized declares as often or transmits as well.
- **R3 — no penalty means no penalty.** Under penalty-free, organisms that declare
  cross at least as often afterwards as those that do not. *Falsified* if declaring
  costs crossings.
- **R4 — the mark is specific.** On corrected ground, generation-3 crossings inside
  the old-pass band fall and crossings outside it rise, relative to stale ground.
  *Falsified* if the mark simply reduces all crossings.

## Boundaries

Toy landscape. The declaration policy is a stated rule, not a learned decision. The
counter-mark size is a fixed constant. "Safe" means outside the old-pass band by
construction. Nothing here concerns language models or the v0.4 kernel.
