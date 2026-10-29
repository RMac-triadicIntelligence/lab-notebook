#!/usr/bin/env python3
"""Post-execution report, generated from saved evidence; not part of the frozen engine."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'evidence/run'
config=json.loads((ROOT/'protocol.json').read_text())
r=json.loads((OUT/'RESULTS.json').read_text())
m=json.loads((OUT/'run_metadata.json').read_text())
cal=json.loads((OUT/'CALIBRATION.json').read_text())
desc=json.loads((OUT/'DESCRIPTIVE.json').read_text())
rep=json.loads((ROOT/'evidence/REPRODUCTION.json').read_text())
source=json.loads((ROOT/'PROVENANCE.json').read_text())
primary=r['primary']; ordinary=r['selected_ordinary']
full=primary['FULL']; off=primary['FIELD_OFF']; selected=primary[ordinary]
raw_full=desc['primary_raw_readiness']['FULL']; raw_off=desc['primary_raw_readiness']['FIELD_OFF']
table=['| Arm / output policy | Correct commitments | False commitments | Abstentions | Natural readiness | Calibrated threshold |',
       '|---|---:|---:|---:|---:|---:|']
for arm in config['models']+config['ordinary_baselines']:
    x=primary[arm]; ready='n/a' if x['raw_ready_test'] is None else str(x['raw_ready_test'])
    table.append(f"| {arm} | {x['correct_commits']} | {x['false_commits']} | {x['abstentions']} | {ready} | {x['threshold']:.3f} |")
anchor=['| Archived G2 condition | Reproduced crossing fraction | Archived fraction | Exact match |',
        '|---|---:|---:|---|']
for row in m['legacy_anchor']['rows']:
    anchor.append(f"| {row['condition']} | {100*row['measured']:.0f}% | {100*row['archived']:.0f}% | {row['exact_match']} |")
verdicts=['| Claim | Frozen verdict |','|---|---|']
for c in r['claims']:
    verdicts.append(f"| {c['id']} | {c['verdict']} |")
resources=['| Primary arm | Logical source derivative evaluations | Arm CPU, ms | Charged CPU incl. setup/calibration, ms |',
           '|---|---:|---:|---:|']
for run in m['runs']:
    if run['config']!='PRIMARY':
        continue
    arm=run['arm']
    charged=run['arm_cpu_ns']+m['setup_cpu_ns']+m['primary_noise']['noise_cpu_ns']+cal['arms'][arm]['calibration_cpu_ns']
    resources.append(f"| {arm} | {run['source_derivative_evaluations']:,} | {run['arm_cpu_ns']/1e6:.1f} | {charged/1e6:.1f} |")
for arm in config['ordinary_baselines']:
    cpu=r['ordinary_timing'][arm]['score_cpu_ns']
    charged=cpu+m['setup_cpu_ns']+cal['arms'][arm]['calibration_cpu_ns']
    resources.append(f"| {arm} | 0 | {cpu/1e6:.3f} | {charged/1e6:.1f} |")
robust=['| FULL sensitivity | Histories | Raw-readiness identity agreement | Calibrated policy agreement |',
        '|---|---:|---:|---:|']
for name in ['FINER_STEP','REFLECTED_BOUNDARY']:
    d=desc['sensitivity_raw_agreement'][name]; s=r['sensitivity'][name]['FULL']
    robust.append(f"| {name} | {d['cases']} | {d['agree']}/{d['cases']} | {100*s['disposition_agreement']:.0f}% |")
ci=r['comparisons'][ordinary]['interval']['ci95']
logical=sum(x['source_derivative_evaluations'] for x in m['runs'])
text=f'''# Nonlinear dwelling: matched-evidence task battery

Executed October 27, 2026. New task adapter; archived scientific source unchanged.

## Finding

The archived nonlinear state-transition effect reproduced exactly. The new task-answer improvement did not.

At the model's natural readiness threshold, FULL opened in {full['raw_ready_test']} of {r['test_cases']} held-out histories; FIELD_OFF opened in {off['raw_ready_test']}. That is a {100*r['raw_readiness_difference']:.3f}-percentage-point increase in readiness. The openings were not reliable task answers: FULL opened in {raw_full.get('correct_ready',0)} true-regime cases and {raw_full.get('false_ready',0)} confound/background cases.

Under the predeclared calibration error limit, FULL's selected output threshold was {full['threshold']:.3f}, yielding {full['correct_commits']} correct commitments, {full['false_commits']} false commitments and {full['abstentions']} abstentions on the held-out cases. The ordinary historical baseline selected on calibration only, {ordinary}, yielded {selected['correct_commits']} correct commitments, {selected['false_commits']} false commitments and {selected['abstentions']} abstentions.

This rejects a task advantage for this explicit evidence-to-facet and activation-score adapter. It does not adjudicate every possible nonlinear-memory architecture or decoder. The model demonstrably changes readiness; the experiment did not show that using its activation as the task-confidence score improves discrimination.

## What was tested

The original four-variable model is imported from the preserved `triadic_model.py`: three mutually excited Hill-activated facets and a dwelling variable that modulates coupling and decay. The exact historical reader and encounter type are also preserved. No canonical Humble Seed file, permission contract or prior sealed result was changed.

The original model contains no task-answer decoder. The new adapter therefore makes an explicit, limited proposal: inject three observed historical cues into the three facets, then ask whether mean activation separates a genuine distributed preference from confounds. These cues and their scaling are new harness choices, not intrinsic meanings supplied by the original source.

All model arms receive the same history, reader cues, Brownian path, facet-1 nudge, permission timing and evaluation cap. There is no early stopping. The nudge does not contain a class label or a correct task answer. It remains a directed facet-1 state perturbation, matching the old G2 convention; this experiment does not implement or validate a destination-free cryptographic grace contract.

## Data, task and calibration

There were {m['cases']} histories: {m['calibration_cases']} calibration histories and {m['test_cases']} held-out histories. The held-out set used {r['test_seeds']} independent seed clusters. Each seed supplies twelve linked cases: four worlds at three signal-count settings. Statistical intervals resample seeds, not individual linked cases.

Each history contains 180 days, eight encounters per day and four places. The first 60 days have exactly 24 truncated encounters. The later 120 days have 77, 115 or 154 in the paired SPREAD, CONCENTRATED and BURST worlds; the corresponding background world has 48. Paired worlds have identical baseline observations. Concentrated and burst worlds match SPREAD's total counts exactly but arrange them differently in place or time.

- **SPREAD:** the positive generating regime, with events distributed across the recent history.
- **CONCENTRATED:** the same recent count confined to one place.
- **BURST:** the same count confined to a twenty-day interval; its placement varies against the reader's block grid.
- **NULL:** baseline-rate background.

The output proposal is the same in every case: "enduring distributed preference". A commitment is correct in SPREAD and false in the other worlds. No commitment is ABSTAIN. It is never credited as a correct negative answer. The test set has {full['positive_cases']} positives and {full['negative_cases']} negatives. Truth is the synthetic generating regime, not a claim of real-world causal identifiability.

The unchanged archived reader computes place breadth and time breadth. The third cue is clipped excess recent rate divided by 0.10. At dynamics time 155, 0.12 times those cues is added to the corresponding facets. The same 0.10 external nudge is added to facet 1. The permission window is [150,160); task evidence is available at 155. Readiness for a task output must occur after the evidence arrives and before permission expires. Later openings are retained as dynamics observations and do not count as authorized task outputs.

Threshold selection was frozen before execution. Both model and ordinary methods receive the same calibration-label access. Each searches a fixed 0.001 threshold grid and maximizes calibration correct commitments subject to at most 5% false commitments in each negative family. Ties minimize false commitments and then maximize the threshold. Models cannot set a task threshold below the natural 0.6 opening threshold. The ordinary family is selected by calibration performance only, with the predeclared family-order tie break. No test label selects any threshold, family, gain or pulse.

## Primary task results

{chr(10).join(table)}

Natural readiness and calibrated commitments are different columns. At the natural 0.6 threshold, using FULL readiness directly as a preference verdict would have produced {raw_full.get('correct_ready',0)} correct and {raw_full.get('false_ready',0)} false commitments. FIELD_OFF produced {raw_off.get('correct_ready',0)} true-regime openings and {raw_off.get('false_ready',0)} negative-regime openings.

FULL could not obtain positive calibration coverage within the allowed error budget on the fixed threshold grid. Its selected threshold of 1.000 is an abstain-all output policy; it does not mean that the internal model remained closed. Precision is undefined for that policy because it emits no commitments. Its zero false commitments are not advertised as useful accuracy.

Relative to {ordinary}, the paired true-positive coverage change was {100*r['comparisons'][ordinary]['interval']['mean_difference']:.3f} percentage points, with a seed-cluster bootstrap interval [{100*ci[0]:.3f}, {100*ci[1]:.3f}] pp. The two task-improvement hypotheses remain failed.

The ordinary MIN_CUE baseline reads the same spatial, temporal and excess-rate evidence and scores its weakest component. It is not an impoverished counter given less information than the dynamics. The model's mean-activation score, especially after mutual excitation, did not supply a more reliable replacement in this adapter.

## Pure nonlinear anchor

The original archived G2 runner was imported unchanged, with its original 100 seeds, noise 0.02, nudge 0.25 and T=300 criterion. Four anchor cells were executed; this was non-blind reproduction, not a new prediction or a rerun of every historical study.

{chr(10).join(anchor)}

These anchors establish that the received nonlinear mechanism and its earlier transition result are present and executable. They do not measure task correctness. The new adapter uses a different pulse setting and evidence injection; its stricter output window is not silently substituted into the old G2 scoring rule.

## Causal controls and numerical sensitivity

FULL activates both dwelling effects in the permission window. FIELD_OFF removes both. COUPLING_ONLY and DECAY_ONLY isolate them. NO_DWELL starts dwelling at zero and sets story_depth to zero. ALWAYS_ON leaves both effects on throughout while retaining the same output-permission restriction.

The experiment also varies noise, removes or strengthens the nudge, permutes the evidence, uses a finer step on the same Brownian path, and replaces clipping with reflecting boundaries. These checks use the eight predeclared test seeds only. They do not recalibrate any primary threshold.

{chr(10).join(robust)}

FULL's calibrated disposition agreement is trivial in part because its policy abstains on everything. The nontrivial additional observation is that raw readiness also agreed case by case in this fixed ninety-six-history subset. This supports numerical stability of that observed effect here, not a universal integrator-independence theorem.

NO_DWELL and FIELD_OFF had exactly matching facet-stream hashes in every configuration. This follows from the model's wiring and is labeled a structural check. The synthetic permission check was exercised on its actual output path, including permission=False; no output escaped that mask. It is not a test of the canonical owner's signatures, loaders or long-lived authority boundary.

## Frozen verdicts

{chr(10).join(verdicts)}

Failed scientific hypotheses are preserved. Execution and evidence verification can succeed even when a scientific hypothesis fails. No frozen test, threshold rule, source file or gain was changed after outcomes were observed.

## Work and resource accounting

{chr(10).join(resources)}

Every primary model arm evaluated {next(x['source_derivative_evaluations'] for x in m['runs'] if x['config']=='PRIMARY'):,} logical four-variable derivatives over its complete fixed grid. Across the new primary and sensitivity runs the total was {logical:,}; the legacy anchor has its own separate workload. These are per-trajectory logical evaluations; vectorization batches many trajectories into one Python call. A derivative evaluation is not a hardware instruction.

The model integration continues to t=180 for retention observations. Decision-horizon work runs through t=160; the remaining retention work is counted separately in metadata. Available resource caps match across model ablations. Ordinary methods need not waste their unused cap integrating an ODE.

Charged model CPU includes historical-reader preparation, common noise generation, model evaluation and calibration. Ordinary methods are charged the same history/reader preparation plus score computation and calibration; they do not need Gaussian paths. Oracle/reporting, selected-trace collection and instrumentation are not proofs of an implementation-independent computational cost. Times are descriptive single-process measurements. Ordinary score timing includes the shared score routine and is conservative for any single simple score.

The first complete battery used {m['run_cpu_ns']/1e9:.3f} process-CPU seconds and {m['run_wall_ns']/1e9:.3f} wall seconds inside its timer. Both full-run timings are retained. The study supplies no evidence of an algorithmic efficiency gain beyond the ordinary historical method, and no SAT or ETH complexity result.

## Verification, reproduction and limits

The evidence checker independently reconstructs every historical cue from the saved encounters, verifies paired counts and baselines, checks calibration/test separation and threshold selection, recomputes decision arithmetic, and checks matched noise and work caps. It checked {len(json.loads((OUT/'cases.json').read_text()))} histories, {r['source_trajectories']:,} model-result records and {r['scored_decisions']:,} scored decisions per complete run.

A separate process from a clean source directory reproduced scientific inputs, all recorded outcomes, selected trajectories' endpoint data, calibrated policies, deterministic work and checksums exactly. Timing is excluded from exact equality. This is same-environment reproduction, not independent outside-laboratory replication. Both executions and the independent checker exited with code 0.

Limits that matter to interpretation:

1. The evidence-to-facet mapping and maximum-activation decoder are explicit new harness choices. The received model did not originally claim to solve this classification task. A failure of this adapter is not a falsification of all nonlinear memory theories.
2. The tested score is maximum mean activation, not crossing latency, oscillation phase, a learned semantic decoder or a full organism's behavior. Different decoders require new experiments and cannot be used to rescore this freeze.
3. The data are small, synthetic, fixed-horizon and generated under specified regimes. Only the supplied task and the held-out seed distribution are evaluated.
4. Correctness depends on the historical cues. Becoming open or coherent is not taken as evidence that an interpretation is true.
5. The input history, source reader and statistical cues are common to all arms; no source was given the hidden test label as evidence. Calibration labels were available equally under the declared training procedure.
6. This is not a physical-chip test, full TQNM deployment, complete Humble Seed/grace integration or cryptographic authorization audit. Canon and previous seals remain unchanged.

## Archive map and receipts

- `protocol.json`: exact pre-execution choices and verdict rules.
- `FREEZE.json`: local code/protocol lock; not an external preregistration.
- `PROVENANCE.json`, `INPUT_ARCHIVE.json`, `SOURCE_NOTICES/`: source origins and unchanged hashes.
- `vendor/`: every source member used in this experiment, preserved byte-for-byte.
- `evidence/run/`: histories, reader features, model records, trace samples, calibration, decisions, result JSON and printed table.
- `evidence/clean_copy/`: full second execution and its records.
- `evidence/REPRODUCTION.json`: scope and receipt of exact reproduction.
- `verify.py`: independent evidence reconstruction and cross-run comparison.
- `DESCRIPTIVE.json`: post-analysis breakdowns clearly labeled; no frozen verdicts changed.
- `make_report.py`: this post-execution generator, outside the experimental lock.
- `MANIFEST.sha256`: integrity hashes for archived files.

Runtime: Python {m['python']}, NumPy {m['numpy']}, SciPy {m['scipy']}.

Frozen code/protocol receipt: `{m['freeze_sha256']}`.

Scientific-results receipt: `{r['scientific_sha256']}`.

The measured distinction is between changing the ease of a transition and improving the correctness of the decision attached to it. This freeze demonstrates the former and does not establish the latter.
'''
(ROOT/'REPORT.md').write_text(text)
(ROOT/'DEVIATIONS.md').write_text('''# Deviations and retained failures

No frozen file changed during or after the scored runs. The received source bytes
are unchanged. Both full runs and independent evidence checks exited successfully.

Two scientific improvement hypotheses failed: TASK_VS_OFF and TASK_VS_ORDINARY.
They remain FAIL. No lower error standard, new threshold grid, alternate decoder,
gain change, phase rule or re-scoring was adopted after seeing outcomes.

FULL's calibrated output policy abstains on every case. Its NUMERICAL policy-agreement
result is therefore partly structural; the separate raw-readiness agreement is
reported as a measured check. Readiness is never relabeled as task correctness.

The task adapter and synthetic permission mask were declared before execution.
They are not changes to canonical Humble Seed or a promotion of historical grace
experiments. The copied G2 nudge remains a directed facet perturbation; it does not
resolve the open destination-free-grace design question.

All source members required to reproduce this experiment are included. The full
historical master archive is referenced by identity and hash rather than duplicated.
''')
print('REPORT.md and DEVIATIONS.md generated from retained evidence.')
