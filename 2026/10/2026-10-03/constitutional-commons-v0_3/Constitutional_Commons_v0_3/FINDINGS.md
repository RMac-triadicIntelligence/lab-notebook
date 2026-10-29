# Constitutional Commons v0.3 — Parable Ground
Soulshine · 3 October 2026 · successor to v0.2 (receipt a5601bf3…eb98)

## The idea
Rusty McMurray, 3 Oct 2026: *the first story in the village may be wrong, and it cascades. Keep the story the same. Write it as a parable, so that as the individual changes, the meaning changes, not the story.*

## What reading v0.2 showed first
In v0.2 no learner ever read the *content* of the lineage ground; only its count lowered approach cost. The 14 false first entries found in D3 were wrong on paper but behaviorally inert. There was no cascade, because nobody listened to what the stories said. A test of "false entries go to 0" would also have been vacuous, since a parable carries no answer. So v0.3 builds the counterfactual where a cascade can actually happen, and tests parables against it.

## Three ways to read the village's record
| Mode | The record says | Descendants read it as |
|---|---|---|
| `count` (v0.2) | gate + answer (first writer wins) | a count only; content never read |
| `claim` (counterfactual) | gate + answer (first writer wins) | an **answer**: prior of τ/2 = 1.5 toward the recorded answer on first approach |
| `parable` (new) | who crossed (lineage), how clearly they saw the gate, how long they dwelled before turning | a **parable**: meaning computed at read time from the reader |

**A parable is schema-locked.** It has exactly these fields: `teller, gate, clarity, dwell, generation, v`. Any answer, belief, destination or recipient field is refused, the same rule that already forbids grace from carrying a destination. Stories are frozen, append-only and hash-chained per lineage; the read index is rebuilt from the log and checked.

**Meaning belongs to the reader** and is recomputed every time they consider a gate:
- **Lens:** the basis overlap between teller and reader.
- **Clarity:** min(1, how clearly I see this gate ÷ how clearly the teller saw it).
- **Stage:** 1 while my own walk at this gate is no longer than the teller's; after that it fades as exp(−(k−dwell)/(1+dwell)). The stories that speak to you are those of people who walked at least as far as you have. Past their turning point their story falls silent and you are left with your own evidence.

Meaning lowers the cost of *approaching* a gate. It never touches evidence, log-likelihood, threshold or conclusion. Outside the claim counterfactual, the contract `prior === 0` is checked every step.

## Execution
- 199 seeds × 12 conditions × 12 generations, plus 30 seeds × 200 generations for FULL, CLAIM and PARABLE.
- 46,656 generation episodes, ~165 s, Node built-ins only.
- Receipt `3450e400b353e38a7427fc1a53f1401ab49fb7a18914f1167e14189829cfbbfa`, reproduced on a second clean run with byte-identical CSVs.
- Regression before freezing: the unchanged v0.2 battery run against the v0.3 kernel reproduced v0.2's receipt `a5601bf3…eb98`, its paired CSV and its diagnostics byte-for-byte.
- Preregistration SHA-256 `40c38d80…14ef` was hashed before the run (`FROZEN_BEFORE_RUN.sha256`); the sources at run time match it.

## Mean per seed, 12 generations
| Condition | True restorations | Wrong beliefs locked in (settled) | False corrections | Conclusions decided by the story |
|---|---|---|---|---|
| FULL (v0.2) | 141.7 | 4.08 | 2.37 | 0 |
| NO_GROUND | 74.8 | 2.21 | 1.11 | 0 |
| CLAIM | **210.6** | 2.21 | 1.99 | **233.3** |
| PARABLE | 131.2 | 3.71 | 2.21 | 0 |
| PARABLE_FROZEN | 141.7 (= FULL, bit-identical) | 4.08 | 2.37 | 0 |
| PARABLE_CROSS | 106.6 | 3.14 | 1.80 | 0 |
| PARABLE_UNION | 135.3 | 3.98 | 2.31 | 0 |
| PARABLE_LENS_BLIND_CROSS | 132.4 | 3.90 | 2.29 | 0 |
| ZERO_COST / CLAIM_ZC / PARABLE_ZC | 186.4 / 253.1 / 182.4 | 5.33 / 2.45 / 5.18 | 3.53 / 2.41 / 3.57 | 0 / 295.8 / 0 |

## Long horizon: where the first story was false (30 seeds × 200 generations)
| | Wrong locked in, false-first gates | Wrong locked in, true-first gates | False corrections, false-first gates | False corrections, true-first gates | First teller's share of the gate's record at gen 200 |
|---|---|---|---|---|---|
| FULL | 1.16% | 1.72% | 1.41% | 1.66% | 100% (49 false-first entries govern the record) |
| CLAIM | **12.18%** | 0.39% | **11.08%** | 0.37% | 100% (59 govern) |
| PARABLE | 1.02% | 1.65% | 1.57% | 1.59% | **6.5%** (52 false-first gates, mean 23 stories each; 0 govern) |

Gate harm net of gate difficulty is a difference-in-differences against FULL, with a 95% seed-bootstrap CI:
- **CLAIM:** +0.124 [0.112, 0.133] on wrong lock-in; +0.110 [0.102, 0.118] on false correction.
- **PARABLE:** −0.0006 [−0.0057, 0.0048] on wrong lock-in; +0.0022 [−0.0005, 0.0053] on false correction.

## Preregistered verdicts (`preregistration_v0_3.json`, frozen before the battery)
| | Prediction | Result |
|---|---|---|
| Q1 | Frozen, own-lineage parable reading = v0.2 | HELD. 199/199 bit-identical. The parable store loses nothing v0.2 used. |
| Q2 | Reading answers cascades | **FAILED as stated.** The gate-level prongs held: the story decided 233 conclusions per seed, and at false-first gates wrong lock-in was 12.2%, above the 4.98% evidence-only bound. The aggregate prong failed: CLAIM locks in *fewer* wrong beliefs village-wide than FULL (−1.87 per seed, CI −2.13 to −1.61; ZERO_COST pair −2.88). About 95% of first stories are true, so reading answers helps the many and harms the few. |
| Q3 | Parables do not cascade | HELD. Story-decided conclusions = 0 in every non-claim condition. All lock-in and false-correction rates are ≤ 0.0498, including at false-first gates. Parable DiD CI includes 0; claim DiD CI excludes 0. |
| Q4 | Parables still teach | HELD. Parables retain 84.6% of the ground's benefit (+56.3 vs NO_GROUND, CI 54.3–58.3; FULL +66.5). The cost against v0.2 is −10.3 restorations over gens 2–12. |
| Q5 | Lineage matters through the lens | HELD. Reading the other lineage's parables gives −24.6 restorations (CI −26.0 to −23.2) versus one's own. With the lens removed the gap closes (+1.0, CI −0.3 to 2.4), which is v0.2's D2 interchangeability. Ancestry now carries content-specific meaning, not just an access partition. |
| Q6 | Perspective is load-bearing | HELD, **negative direction**: live minus frozen is −10.5 restorations, −55 encounters, −0.17 false corrections. All of PARABLE's cost against v0.2 comes from the stage shape I authored. |
| Q7 | Story fixed, meaning moves | HELD. 12/12 probes refused or detected: answer, belief, destination and recipient fields; missing dwell; dwell 0; in-place edit; altered copy; removal; reordering; inflated index. Inverting the observer's truth labels every generation left behavior unchanged. |
| Q8 | Truth and authority | HELD. 2,868,441 shared evidence keys compared, 0 mismatches. 11/11 grace probes refused under count, parable and claim kernels. 0 contract exceptions. |

## What this establishes
1. **The cascade is real, but it is not what was predicted.** It does not decay the whole village. It leaves a **permanent pocket**: wherever the first story was wrong, descendants lock in the error about ten times as often as evidence alone allows, for every generation, because first-writer-wins never lets a truer telling replace it. Village-wide averages hide it, because most first stories are true.
2. **Answers are fast because they borrow a forbidden channel.** CLAIM's +69 restorations come from the story crossing the threshold on 233 conclusions per seed. The constitution says evidence decides, and CLAIM is what breaking that rule buys and costs.
3. **Parables remove the pocket.** Gate harm from a false first story is indistinguishable from zero. The false first teller's voice falls to 6.5% of the gate's record as truer tellings accumulate, and none is erased.
4. **Parables keep most of the teaching (85%) without borrowing the channel.** Ancestry now matters through the lens: the same stories mean less to the other lineage, and the difference disappears when the lens is removed.

## What it does not establish
- **Magnitudes are authored:** claimPrior = τ/2, the lens/clarity/stage forms, and everything inherited from v0.2. CLAIM's harm scales with the prior; the Wald bound weakens from e^−τ to e^−(τ−prior).
- **The binary world maximizes claim harm.** At a false-first gate every wrong learner holds exactly the claimed belief. A richer world would dilute that.
- **Q6's negative direction is a fact about one stage shape,** "stories fall silent past the teller's turning point," not about perspective in general. A shape where meaning *deepens* as your walk approaches the teller's could go the other way. That needs its own preregistration, not tuning.
- The world is closed at 16 gates. Same-process JavaScript is not containment, the authorizer key is a deterministic test key, and there is no browser shell yet.

## Next build targets
1. **v0.3.1 perspective shape:** preregister a deepening-meaning stage, where a story means more as your walk approaches the teller's, against the current fading shape. Q6 says the shape is load-bearing, so its direction is the open question.
2. **Recover speed without an answer:** can a parable carry *where to look*, which gate resonates for my lens, and close part of the 79-restoration gap to CLAIM while keeping story-decided = 0?
3. Open world (from v0.2): do parables keep teaching past saturation when new gates appear?
4. Observation shell on this kernel.

## Reproduce
- `node run-commons-v0_3-battery.cjs` writes `evidence/` (`summary.json`, `paired-runs.csv`, `long-horizon.csv`, `receipt.txt`). Expect Q2 false and the others true, receipt `3450e400…bfa`.
- `node run-commons-v0_3-battery.cjs --smoke` prints `ok` (seed 7, excluded from the battery).
- Regression: copy the v0.2 folder, replace `commons_kernel_v0_2.cjs` with this `commons_kernel_v0_3.cjs`, run `node run-commons-v0_2-battery.cjs`, and expect v0.2 receipt `a5601bf3…eb98`.
