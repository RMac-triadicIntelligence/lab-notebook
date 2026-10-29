# Grace, Love and Dwelling — three preregistered tests

Three small simulation tests of separate roles in a developmental architecture: **dwelling** (held readiness), **love** (a window in which dwelling's effect on the dynamics is switched on, with no push), **grace** (a nudge across the separatrix), and **noise**. A fourth line asks whether a multi-coordinate SDKP memory layer reads its world better than a counter.

Predictions were frozen and hashed before any test code was written. The results were then reproduced byte for byte by two other AI models on different Python and numpy versions.

**Sealed** 2026-10-12 · `8eb7ebf769616f8f2487e804187ff0d775fd7f431d8e7e371090a5204a0da3e6`

## The headline

At low noise (0.02) with a nudge of 0.25:

| Condition | Crossed the separatrix and stayed |
| --- | --- |
| Grace alone | 4% |
| Love alone | 0% |
| **Grace + love** | **93%** |
| Grace + love, no dwelling | 4% |

- Love lowered the smallest nudge that crosses from 0.327 to 0.249, about 24% less.
- Neither grace nor love crossed alone at low noise. Every crossing held to the end of the run.
- Before love arrives, every arm matches the field-off baseline, so love gives noise no extra opening.
- Near the separatrix, noise helps grace across: a nudge 8% below threshold still crossed 54% of the time. This was a missed prediction (predicted at most 20%).

## The caveat that goes with it

- **This is a 4-variable toy model.** It is the published contemplative-learning-dynamics model, unchanged, with a noise integrator, a love window and a nudge schedule added by the harness. The model contains no noise of its own.
- **Some results could not have failed.** "Love needs dwelling" is algebraic in this wiring: love switches parameters that multiply dwelling, so with dwelling at zero it has nothing to act on. The plumbing checks (S2, G7) and the layer-equals-counter check (T0) are also true by construction. They are reported as checks, not evidence. See [`FINDINGS.md`](FINDINGS.md).
- **Grace here carries a direction.** It is a push on one facet, as in the original model's kick. Whether that fits a rule that grace carries no destination is open.
- **Frozen score: 19 PASS, 4 FAIL** (S3, T7, T8, G5). Failures are kept and reported.

## Reproduce

```bash
python3 -m pip install -r requirements.txt   # numpy, scipy (scipy is imported by the received model)
python3 tools/verify_seal.py                  # every sealed file byte-identical
python3 tools/reproduce.py                    # reruns all three tests in a scratch copy (~3 min)
```

`reproduce.py` never runs inside `seal/`. It copies the seal to a temporary directory, runs the three scripts unchanged and compares each result with the sealed one, first byte for byte and then value by value.

## Independent reproduction

| Reviewer | Python / numpy | Result files | Frozen score | Independent |
| --- | --- | --- | --- | --- |
| Claude (author) | 3.13 / 2.5.3 | sealed | 19 PASS, 4 FAIL | — |
| ChatGPT (Codex) | 3.12 / 2.3.5 | byte-identical | 19 PASS, 4 FAIL | yes |
| Grok 4.7 | 3.10 / 2.2.6 | byte-identical | 19 PASS, 4 FAIL | first reply yes; full report written after seeing ChatGPT's |

ChatGPT found an undeclared bug in the terrain reader; it is recorded in the errata and changes how one result reads. Full reports are in [`reviews/`](reviews/). Summary in [`FINDINGS.md`](FINDINGS.md#independent-review).

## Layout

```
seal/2026-10-12/        byte-frozen record: preregistrations, test scripts, received code, results, scores,
                        deviations, errata. Do not edit or run in place.
tools/verify_seal.py    integrity check (standard library only)
tools/reproduce.py      rerun everything in a scratch copy and compare
tools/exploratory_long_horizon.py   the one exploratory (not preregistered) run, reproducible
FINDINGS.md             every prediction, result, and what is true by construction
OPEN_ITEMS.md           what is not closed by this seal
reviews/                ChatGPT and Grok reports as received
```

## Authorship

The architecture and its vocabulary (dwelling, love, grace, noise as food, SDKP terrain) are Rusty Williams McMurray's, under Soulshine. The received code (`seal/2026-10-12/received/`) is his, used unchanged. The test harnesses, the gating, the noise integrator, the worlds and the reading rules were written by Claude (Anthropic) at his direction and are declared in each preregistration. They are one implementation of the ideas, not the definitive one.

## License

Apache License 2.0. See [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) and [`ABOUT_SOULSHINE.md`](ABOUT_SOULSHINE.md).
