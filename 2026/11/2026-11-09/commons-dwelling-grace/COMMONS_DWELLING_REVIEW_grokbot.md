# Commons and dwelling_grace: history-seat review

Free-hand, non-normative conductor builds, 2026-11-09 evening. Not a v0.7 scored run. Nothing here is published.

**Sources read:** the zip (`zip_1910.zip`, sha256 a15f5ffb…ae16), both READMEs, both scripts, the predictions file, run1 and full-run outputs, and the public repos `contemplative-learning-dynamics` (README, `run_simulation.py`, and the model file stored on GitHub as `src`) and `triadic-quantum-nonlinear-memory` (`triadic_forgiveness_operator.py`), fetched from raw.githubusercontent and the GitHub API. Seat-blindness list unchanged: I did not open `sealed/`, `source/`, `AUDIT_CHECK_*`, or the v1 prompts.

**Rerun:** `/workspace/incoming-2026-11-09/zip_1910_rerun/`, Python 3.13.5, numpy 2.5.4.

---

## Reproduction

Every `results.json` / `results_sweep.json` hash reproduced byte for byte. Raw text reproduced byte for byte except one environment path in a numpy warning. There is no sweep mode in the shipped `commons.py`; I reconstructed the sweep by calling the same `society()` with seeds (11, 12, 13) and the B values printed in `raw_output_sweep.txt`. That reconstruction is valid because the B=0.05 records in the original sweep file are byte-identical to the full-run "rain, ground on" arm, which used those seeds. The reconstructed `results_sweep.json` and `raw_output_sweep.txt` both matched.

The original run lived at `/home/claude/commons/`. numpy's `default_rng` was deterministic across that environment and this one. I saw no other nondeterminism.

| File | sha256 | Rerun |
|---|---|---|
| `run1/results.json` | 8a18e4ca72d1b0187b51f92187fcfbc868dc1bb6acf3e9c3f562908eb0d208b7 | match |
| `run1/raw_output_run1.txt` | 1932be69854b576a02baddf8e2c62eb7d3bddbdf0f99e115457ca6d14436d055 | match |
| `commons_v1/results.json` | 84a018f673fb29cd5e90f17bb71b93c6e524347c8f7313a3df3d3b0526d2ffd5 | match |
| `commons_v1/raw_output.txt` | 3fadc32f44e95b67e497ef53f70263d9714ea7a43d1049979ec08d4f15232360 | body match; only the RuntimeWarning path differs (`/home/claude/commons/commons.py` vs the rerun path) |
| `results_sweep.json` | ce019dd11bccf46008a5caca1cbfd3698a557e56b8139d77e2886cd795e6ccc4 | match (reconstructed) |
| `raw_output_sweep.txt` | 08644bf529357cb64edf47375e6ebb2dca3d7f3677dbb4573deef5785fe6d88c | match (reconstructed) |
| `dwelling_grace/results.json` | d31bb9ec1d210e7ed3641bf873174e6903e3e10bf0cf2c215d175096d0741436 | match |
| `dwelling_grace/raw_output.txt` | b5fcba793efcad2ddaa8b8ac5f61c229a0aa9e575738e7c40811ea7f5ec99e3c | match |

The printed hashes inside the original raw outputs match these files. The B=0 sweep records are also byte-identical to `run1` "rain_ground_on", so the only behavioural change between run 1 and the full model, on the default arm, is the recognition rule when B > 0.

---

## Commons: the claims, checked

### The predictions file and the post-hoc rule

The predictions file says it was written at "2026-11-09 18:2x CT, before commons.py was run for the first time." I cannot verify that from dates. Every entry in the zip is stamped 2026-11-09 18:52:26, so the archive has no useful order.

What the content does show, and it is consistent with the claim but not a proof of it:

- The predictions file never mentions recognition or B.
- `run1/commons.py` has no recognition rule and no B.
- The full `commons.py` comments that recognition was "added after run 1", and the README says the same.
- Run 1 and the B=0 sweep agree exactly, and almost nobody turns (~1%).

So I can confirm that the 75–80% turning result comes from a rule that was not in the first script and was not one of PA–PD. I cannot confirm that the predictions file was written before any run.

B was chosen after the sweep, as the README and the code comment both say. The sweep is sharp: B=0 stays at 1%; B=0.02 already reaches 70% by generation 5; B=0.05 to 0.4 sit on a plateau at 75–80%. 0.05 is "a value that works", not a uniquely justified constant. The headline turning rate is therefore a post-hoc rule plus a post-hoc parameter.

### PA conservation — true by construction

Rain is the only source of fill. Gifts, estates, and passing-on by the turned only move fill from one organism to another. Crossing does not consume it. The check `sum(L) == total rain` cannot fail except by floating-point noise (the runs show errors of 0 to about 1e-8). PA is a bookkeeping identity, not a finding about the world of the model.

### PB riches — holds, and is mostly designed in

The isolated test (fixed fill, fixed grip, no rain, no calls) matches the README numbers: open hand, 81% turn at a full basin; grip 0.1, 23% at a full basin, 6% at 1.5×, 1% at 2×; grip 0.25 or more, almost none. That tension is written into the cling force `g * K * min(L, 4H)`, which grows with fill. So the *direction* of PB is a designed mechanism, then measured. One small overclaim: with an open hand, turning is not strictly increasing in fill once L is past the barrier (81%, 79%, 76%, 74% at 1×, 1.5×, 2×, 3×).

### PC orphans — "best ground, no grace" cannot fail because of ground

The test sets L=0 and grip to GMIN. In `move()`, grip only appears in the cling term, and cling is multiplied by `min(L, 4H)`. Lift requires `V(x) < L`. With L=0 both terms are off for any grip, so a child with the "best possible ground" has the same dynamics as a child with no ground at all. The 0 of 600 crossings is a measurement of noise against a dry barrier, not a test of inheritance. PC as written is true by construction on the point it claims to test.

### Q2, "ground barely matters" — partly built in

Ground only shifts birth grip, and only by at most RHO=0.3 (because of `tanh`). Recognition then loosens grip over a lifetime and is what actually produces turning. Against that, a 0.3 cap on the inherited shift is small by design. The observed +3 to +5 points, and a family-level correlation of about 0, are still worth recording — the shuffled arm really does match the real one, so in this model the change travels through the society, not down the family line — but they should not be read as a surprise about lineage ground in general.

The ~0.5 correlation in the "never give" arms is, as the README says, an artefact. The pinned 20% never give, never receive recognition, never turn, and never deposit. Pooling them with people who do turn and do deposit produces a correlation between ground and turning that is mostly the pinned flag. Confirmed: those arms have correlations 0.42 to 0.53; the ordinary arms are about 0.

### The water line has no ceiling — confirmed

On the holding side, V(x) is at most H=1 (at the barrier). For any L > 1, `V(x) < L` holds for every x < 0, so the landscape force is identically zero on the whole holding basin. Only cling and noise remain. When the turned pour fill onto those who have not turned, L can reach many times the barrier; if their grip is also small, they are random-walking in a flat well. That is the artefact the conductor flagged, and it is in the equations. It also bears on Q1: after the rain stops, turning is slightly *higher* than with continuing rain, which may be this flood behaving badly rather than a clean fact about residual grace.

### Other code-vs-README nits

The docstring says only an organism's own acts change its grip, and that crossing the separatrix at x=0 is the turning. Recognition changes grip without an act of giving or refusing. The code turns at x ≥ 0.5, not at x=0. The "neighbour in need" is a random call, after which the gift goes to the poorer neighbour.

---

## dwelling_grace: against the two public repos

**Equations.** The motion in the script matches the contemplative-learning-dynamics README: coherence as the mean of the three facets, the dwelling ODE, coupling and decay shaped by dwelling, and the Hill activation in the facet equations. The one change, which they flagged, is that `d'` uses `(1 - closure - d)` instead of `(1 - d)`, so closure caps how far dwelling can grow.

**Constants do not match the library code.** The README of that repo gives no numbers, as they said. The model file on GitHub (stored as a file named `src`, not `src/triadic_model.py`) does:

- Hill: gamma=10, steepness=6, threshold=0.5
- rise=0.35, fade=0.45, story_depth=0.8, coupling_boost=0.8, base_decay=0.22, decay_relief=0.6
- start at (x1,x2,x3,d) = (0.2, 0.1, 0.15, 0.6)
- jump amount 0.5
- integrated with `scipy.odeint`, no noise

The script uses rise=0.5, fade=1.0, story_depth=1.0, coupling_boost=1.5, base_decay=0.6, decay_relief=0.5, gamma=1, n=4, start at x=0.02 and d=0, Euler with dt=0.01 and noise 0.02, and an "insight" cut at mean(x)>0.4 that the library does not define. So the *shape* of the equations was taken from the README; the numbers, the start, the integrator, and the scoring rule were not taken from the code.

**Forgiveness constants match; the gate does not.** In `triadic_forgiveness_operator.py`, forgiveness requires a witnessed confession in an UNKNOWN determination; it then does closure → max(closure − 0.2, 0.1), dwelling → min(dwelling + 0.3, 0.95), and leaves the three facets untouched. Those three number-caps are used as written. Two other parts are not: memory_fast and memory_slow are decayed toward 0.5, and the witness/authorization check is never implemented — the script just applies the caps at scheduled times and comments that a witnessed confession is assumed.

The printed dwelling results match the README (0% with no nudge and d≈0.96; a 0.5 nudge is 0% at t=0, 81% at dwelling 0.62, 100% later; a 0.9 shove works at any time; a 0.3 nudge never works; locked-in plus a shove is 0%; forgiven once then nudged is 80%, twice 100%; four forgivenesses and no nudge is 0% with d≈0.87; a one-facet nudge lifts all three to mean 0.64 and dwelling falls to 0.22).

---

## Findings

### CD-F1. The 75–80% turning rate is a post-hoc rule plus a post-hoc B. WOUNDING. DOC.

**What:** Recognition (grip *= 1−B with probability 1−g per unit of received gift) was added after run 1, and B=0.05 was picked after the sweep as a value on the plateau that works.

**Scenario:** Run 1, and B=0, stay at about 1% turning in every arm. Turn recognition on at B=0.02 and the society is at 70% by generation 5. PA–PD did not predict this.

**Minimal fix:** Treat run 1 as the pre-registered model. If recognition is to be kept, freeze B (and the rule) before the next run, and report the whole B-sweep as the result, not a single favoured value.

### CD-F2. The predictions file cannot be shown to predate the first run. MINOR. DOC.

**What:** Every file in the zip shares the timestamp 2026-11-09 18:52:26. There is no independent commit or clock.

**Scenario:** The file *could* have been written after run 1. The content is consistent with the claim (it never mentions recognition), but that is not a proof of order.

**Minimal fix:** For the next free-hand run, hash the predictions file and publish the hash before any script is executed.

### CD-F3. PA conservation is true by construction. MINOR. DOC.

**What:** Fill is only moved, never created, except by rain. The 1e-8 agreement is arithmetic, not evidence.

**Minimal fix:** Report it as a sanity check of the bookkeeping, not as a passed prediction about the model world.

### CD-F4. PC cannot test inherited ground. WOUNDING (for the interpretation). DOC.

**What:** With L=0, grip does not enter the equations, so "best possible ground, no grace" is dynamically identical to "no ground, no grace."

**Scenario:** Ground could be enormous; the child still cannot be moved by it, because ground only changes grip and grip only scales cling, which is zero when there is no fill. 0 of 600 then measures noise versus a dry barrier.

**Minimal fix:** To test "ground is inherited, the crossing is not," compare best-ground and no-ground at a *small but non-zero* fill, where cling and lift are both live.

### CD-F5. The water line has no ceiling, as flagged. WOUNDING (for who-doesn't-turn and for Q1). DOC.

**What:** Any L > H submerges the whole holding basin. The landscape force is then identically zero for all x < 0.

**Scenario:** The turned pour fill onto those who remain. L can be many times the barrier, grip can be near 0, and those organisms wander in a flat well. The README's diagnostic (the ones who never turn have grip about 0 and huge fill) follows from this rule. After the rain stops, turning is slightly higher than with continuing rain; that comparison is not clean while this rule is in place.

**Minimal fix:** Cap the lift at the basin (excess fill runs over, as the conductor already suggested), and rerun Q1 and the "who never turns" diagnostic.

### CD-F6. "Ground barely matters" is partly built in. WOUNDING (for the Q2 reading). DOC.

**What:** Inherited ground can shift birth grip by at most 0.3, while recognition, which was added after run 1, is what produces almost all turning.

**Scenario:** A modest inherited shift is easily swamped. The shuffle arm matching the real arm is still a genuine observation in this model (the effect, such as it is, is not family-aligned). It is not a general result about lineage ground.

**Minimal fix:** Report Q2 as "under these caps, and under the post-hoc recognition rule, ground is swamped," and add an arm with recognition off, or with a larger inherited effect, before claiming that ground barely matters.

### CD-F7. Recognition writes grip, against the model's own rule. WOUNDING. DOC.

**What:** The docstring says grip changes only through the organism's own acts. Recognition loosens grip when a gift is merely received.

**Scenario:** An organism that never gives can still have its topography rewritten by other people's passing-on. That is the path that produces the 75–80% turning.

**Minimal fix:** Either drop the sentence "only its own acts change it," or make recognition something the organism *does* (an act of seeing), with the same give/refuse symmetry already used for the call.

### CD-F8. dwelling_grace does not use the library's constants, start, or integrator. WOUNDING. PRIOR (the public `src` model file and `run_simulation.py` in contemplative-learning-dynamics).

**What:** The equations match the README. The numbers do not match the code. Library defaults are gamma=10, steepness=6, rise=0.35, fade=0.45, story_depth=0.8, coupling_boost=0.8, base_decay=0.22, start (0.2, 0.1, 0.15, 0.6), jump 0.5, `odeint`, no noise. The script uses a different set, Euler plus noise, a start at nearly zero, and an insight cut at 0.4 that the library does not define.

**Scenario:** A run of the public demo, and a run of this script, are not the same model. Results such as "a 0.9 shove works at any time" may be an artefact of these constants and of starting at d=0, rather than a property of Rusty's published equations.

**Minimal fix:** Rerun with the library defaults, `odeint`, and the library start, and report any change. Say clearly that the constants were not taken from the code.

### CD-F9. The forgiveness operator's constants are used; its gate and memory are not. MINOR. PRIOR (`triadic_forgiveness_operator.py`).

**What:** The −0.2/0.1 and +0.3/0.95 caps match, and the facets are left alone. The real operator also decays two memory fields and will not forgive without a witnessed confession in an UNKNOWN state. The script applies the caps on a timer and assumes the witness.

**Minimal fix:** Either implement the witness/authorization check and the memory update, or say that only the two caps were borrowed.

---

## Tie-back to v0.7 and our Round 4 findings (brief)

**R4-F1 (grace had no causal path to the crossing).** Commons does give grace a causal path, in two places: the lift (fill can zero the landscape force below the water line) and recognition (received gifts loosen grip). That is the existence proof we said was missing. It does not, as written, satisfy the keel. v0.7 §1.2 says grace must not change the landscape or private topography; the lift changes the effective landscape, and recognition writes grip, which this model itself calls personal topography. So the build shows a way to give grace an effect, and also shows how easy it is to do it by routes the keel just forbade.

dwelling_grace is closer to two keys: dwelling is the organism's own readiness, and a nudge is external. A gentle nudge (0.5) really does need dwelling (0% at t=0, 81% once d≈0.62). A hard shove (0.9) does not — it works at t=0 with d=0 — which is grace forcing a crossing, the thing §1.4 said must not happen. Forgiveness alone never crosses, which is clean.

**H3 (inherited ground).** Commons has a real J, empty and shuffled controls, and no parental fill or position passed on, which is in the spirit of v0.7 §4. Under this parameterization the developmental increment is small and not family-aligned, and the 0.5 correlation is an artefact of the pinned arm. That is not a scored H3 result, but it is a warning: a social channel added after the fact can swamp inherited ground, and a shuffle control is what shows whether any remainder is actually lineage-aligned.

---

**PRIOR claims** in CD-F8 and CD-F9 rest on the public GitHub files fetched this turn, not on memory.
