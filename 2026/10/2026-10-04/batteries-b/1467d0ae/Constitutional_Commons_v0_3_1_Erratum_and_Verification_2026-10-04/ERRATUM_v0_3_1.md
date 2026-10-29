# Erratum — Constitutional Commons v0.3.1 FINDINGS
Soulshine · 4 October 2026 · applies to `FINDINGS.md` inside `Constitutional_Commons_v0_3_1_2026-10-04.zip` (receipt `1025cb60…5ffb`)

The original FINDINGS.md and all its evidence are **unchanged** and included byte-for-byte in `inputs/`. This file corrects four statements. **No preregistered verdict changes:** B1 and B2 failed; B3, B4, A1, A2 and A3 held. Every number below is produced by `verify.py` from the packages in `inputs/` (see `verification.json`).

Credit: E1–E3 were raised by ChatGPT's independent execution and review. E4 was found by Claude after ChatGPT noted that no public post was verified.

---

## Three independent executions agree
| | Claude | Grok | ChatGPT |
|---|---|---|---|
| Sources match the frozen hashes (preregistration `5786c457…1d26`) | yes | yes | yes |
| Receipt | `1025cb60…5ffb` | `1025cb60…5ffb` | `1025cb60…5ffb` |
| paired-runs.csv / long-horizon.csv | — | byte-identical | byte-identical |

ChatGPT also re-ran the v0.3 battery against the v0.3.1 kernel and reproduced v0.3's receipt, `3450e400…bfa`.

---

## E1 — The runner did not check everything B4 promised (harness gap)
**What the preregistration promised (B4):** *"In every parable condition, planted and unplanted, **and in the long horizon**: story-decided conclusions = 0, wrong lock-in and false-correction rates ≤ e^-3."*

**What the runner checked:** in the long horizon, only `storyDecided === 0`. It did not compare the long-horizon rates to the bound.

**Impact:** none on the verdict. The omitted check, computed here, passes:

| Long-horizon mode | Wrong lock-in rate | False-correction rate | Bound |
|---|---|---|---|
| FADE | 1.601% | 1.539% | 4.979% |
| DEEPEN | 1.374% | 1.278% | 4.979% |
| RESONATE | 1.320% | 1.210% | 4.979% |

**Why it matters anyway:** the runner reported B4 as true without checking everything B4 claims. That is the same class of error as "a field is not a check." The frozen runner is not edited. The fix for the next harness is in `proposed_harness_fix_B4.diff` (not applied).

## E2 — The mechanism was overclaimed
**Original:** *"…Fade puts full meaning at the threshold and withdraws later; deepening and resonance hold it back at the threshold. **That is the whole failure: 184–223 fewer encounters.**"*

**Problem:** each shape replaces the whole curve at once: its value at the threshold (k = 0), its slope, and its behavior after k = D. No condition varies the threshold value alone. The encounter loss is observed (−184 and −223). That it is *the* cause is an explanation, not a finding.

**Corrected:** *"Both new shapes produced fewer encounters (−184, −223) and fewer restorations. One plausible explanation is that they give less meaning at the threshold, where approach cost binds. This design does not isolate that explanation, because each shape changes the entire curve."*

## E3 — "Deepening is more careful" is retracted
**Original:** *"Deepening is more careful… It is slower, but it errs less per gate. That is a real tradeoff, not just a loss."*

**What the data show, per seed over 12 generations, paired against FADE:**
| | True restorations | False corrections | Wrong lock-ins | Residual errors at the end (per-seed mean) |
|---|---|---|---|---|
| DEEPEN − FADE | −8.24 (CI −9.54, −6.93) | −0.28 (CI −0.45, −0.11) | −0.04 (CI −0.23, +0.16) | **+7.96** |
| RESONATE − FADE | −15.24 (CI −16.45, −14.03) | −0.37 (CI −0.53, −0.20) | −0.23 (CI −0.43, −0.03) | **+14.87** |

Deepening prevents about 0.3 false corrections and leaves about 8 more real errors unresolved. Over 12 generations its lock-in difference is indistinguishable from zero. The lower long-horizon *rates* are rates per sampled gate, and fewer gates are sampled. On balance this is worse, not a tradeoff.

**Corrected:** *"Both new shapes resolved fewer errors and left more uncorrected: +8.0 (DEEPEN) and +14.9 (RESONATE) residual errors per seed, against −0.28 and −0.37 false corrections. Their lower long-horizon error rates are per sampled gate and do not offset the loss."*

## E4 — The witness claim was unverified
**Original:** *"Preregistration SHA-256 `5786c457…1d26`, **posted publicly by Rusty before the run** as the external witness of when it was frozen."*

**Problem:** the author never verified a public post. "Go" was taken as confirmation. No package contains a link to a post, and ChatGPT's review states that no public post was performed or verified. The FINDINGS asserted, as witnessed, something nobody outside had witnessed. That is the record vouching for itself, which is the very failure the witness practice exists to prevent.

**Corrected:** *"The preregistration SHA-256 `5786c457…1d26` was given to Rusty before the run for public posting. As of this erratum, no public post has been verified. The freeze time therefore rests on: the sandbox file timestamps, the hash shown in the conversation before 'Go', and the identical source hashes in three independent executions. These establish which files were run. They do not establish, through an external witness, when the files were frozen."*

**If a post exists:** a dated addendum will record its link. It will not overwrite this text.

---

## What stands unchanged
- The B1 and B2 failures: deepen −8.2 and resonate −15.2 restorations against fade.
- B3: the lens persists under deepening.
- B4: truth is intact, including the long-horizon rates checked here.
- A1: the answer pocket is causal under matched prehistory (+11.5 points).
- A2: parables stay within ±2 points in every shape.
- A3: 45/45 probes refused for the right reason.
- The next test (separating threshold help from experience-dependent meaning, e.g. at reception) was reached independently by Claude and ChatGPT.
