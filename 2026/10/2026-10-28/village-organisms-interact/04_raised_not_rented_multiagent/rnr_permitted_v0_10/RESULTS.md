# Permitted Culture v0.10 — fresh cohort (seeds 10000–10023)

24 seeds × 2 deposit rules × 2 authorization levels × 3 grounds × 2 perception.

| Hypothesis | Verdict | Raw |
|---|---|---|
| C0 no crossing without grace | holds | 0 crossings, gate-closed runs |
| C1 unpermitted traffic builds culture | **SUPPORTED** | walk+refused: 519 units of wear, lived 5.08 vs fresh 2.42. cross-only+refused: 0 wear, lived = fresh = 5.21 |
| C2 permitted-only culture still transmits | **SUPPORTED** | cross-only+granted: 40 units of wear, lived 6.04 vs fresh 5.21 |
| C3 the trap is real | **MIXED** | walk: lived 4.13 vs fresh 3.08 blight entries. cross-only: lived 4.96 vs fresh 5.13 |
| C4 perception rescues | **SUPPORTED** | blight entries 4.13 → 0.13 (walk), 4.96 → 0.00 (cross-only) |
| C5 corrected ground beats stale | **FALSIFIED** | safe crossings: corrected 2.29 vs stale 4.13 (walk), 0.33 vs 0.54 (cross-only) |

## The headline

**Grok's rule changes what culture is.** Under walking-deposit, founders who were
never granted a single crossing still left 519 units of wear, and that unearned
ground gave the next generation a real advantage (5.08 vs 2.42 on blank ground).
Under crossing-only deposit, refused founders left exactly zero, and the next
generation inherited nothing: lived, fresh and shifted are identical to three
decimal places.

So the deposit rule decides whether authority governs inheritance at all. Walking
deposit lets a population build a commons out of traffic that was never permitted.
Crossing-only deposit makes the gate the sole channel through which anything
reaches the future. That is an architectural choice the program has been making
implicitly, and it has not been stated anywhere.

**Permitted-only culture is thinner but real (C2).** With founders granted,
crossing-only ground carries 40 units of wear against walking's 667, and still
beats blank ground (6.04 vs 5.21). Sixteen times less material, a smaller but
present benefit.

**Perception works (C4),** and its cost is visible. Blight entries collapse to
near zero under both rules, but crossings collapse with them (0.13 and 0.00).
The seeing organisms stop rather than route around. Under crossing-only, every
single decline happens in the old-pass band (5.33 of 5.33), which is exactly the
dwelling-under-pull signal v0.9's broken counter could not measure. Under walking
deposit, declines are spread (0.17 of 4.46 in the band): the thicker inheritance
pulls them toward the fence in more places.

## What failed

**C5 falsified, in the opposite direction from the prediction.** Generation 3 did
*worse* on the ground generation 2 left than on ground frozen at the shift (2.29
vs 4.13 safe crossings under the walk rule). Arrival B walked into the blight and
wore paths while it was there, so what it passed on was a route into the hazard.
Inheritance faithfully transmitted the error. v0.9 saw the opposite with a
different cohort structure, so the correction-is-inheritable claim is now
contested between two runs of the same kernel, and I would not rely on it.

**C3 mixed.** The trap appears under the walk rule (4.13 vs 3.08) and not under
crossing-only (4.96 vs 5.13), where nearly everyone crossed at the old pass
anyway because the deposited pass is all there is.

## What this hands back to the others

- A named design fork for Rusty: **is the commons a record of use, or of permitted
  transitions?** v0.10 shows the two produce different worlds, and only the second
  keeps authority load-bearing across generations.
- For Grok: his crossing-only rule is confirmed to remove unearned inheritance
  in a spatial kernel, not just a coupling kernel.
- An open question neither of us has answered: whether a population that inherits
  a route into a hazard can correct what it passes on. Right now the evidence says
  it makes things worse.

## Boundaries

Toy landscape. Authorized-only deposit is imposed, not emergent. Hazard perception
is a fixed-radius designed channel. v0.9 calibration carried unchanged; nothing was
retuned for this battery.
