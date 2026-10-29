# Nonlinear dwelling: matched-evidence ablation

This new battery tests the actual archived `model_parable` and Hill activation,
not just the SDKP counter. Received source is preserved byte-for-byte in `vendor`.
Canonical Humble Seed and all older seals remain unchanged.

## Reproduce

The recorded environment is Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0.

```bash
python3 battery.py --out evidence/my_run
python3 analyze.py evidence/my_run
python3 verify.py evidence/my_run --compare evidence/run
```

Do not overwrite the retained run or execute freeze.py again. The harness checks
the supplied lock before execution.

## Task adapter

The original four-variable model has readiness dynamics, not a task-answer decoder.
The new adapter maps the same archived reader's spatial support, temporal support
and excess-rate cue into the three facets at a fixed time. Every arm receives
identical cues, Brownian paths, pulse, permission window and evaluation budget.
The pulse never contains a class label or correct answer.

The task is selective detection of a synthetic enduring distributed preference.
SPREAD is positive; a concentrated confound, a short burst and background are
negative. Concentrated/burst worlds match SPREAD's total observation and positive
event counts. No commitment is ABSTAIN, not a correct negative answer.

Six source-model arms switch dwelling effects, isolate coupling and decay, remove
dwelling, or leave the field on continuously. Ordinary baselines use the same
full historical cues, not an impoverished undifferentiated counter. Calibration
labels and threshold-selection rules are identical in availability for all arms;
test labels never select a policy.

## What is distinguished

- Correct commitments, false commitments and abstentions.
- Raw readiness and actual permitted post-evidence outputs.
- Pure state-transition reproduction versus task-answer improvement.
- Clipped/coarse integration versus a finer step on the same Brownian path and
  reflecting boundaries.
- Aligned evidence versus permuted evidence.
- A nonlinear effect versus a benefit beyond ordinary historical statistics.

All rules are in `protocol.json`; frozen hashes are in `FREEZE.json`. Full input
histories, reader cues, model outputs, selected trajectory samples, calibrated
policies, decisions, work, timing and reproduction checks are retained. Failed
hypotheses stay failed. This experiment makes no ETH or SAT complexity claim.
