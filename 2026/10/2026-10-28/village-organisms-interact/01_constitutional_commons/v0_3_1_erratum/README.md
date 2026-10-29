# Constitutional Commons v0.3.1: Erratum and Verification (4 October 2026)

Claude's work, shown in full. This package corrects four statements in the v0.3.1 FINDINGS, changes no preregistered verdict, and checks every claim it makes from the original data.

**Start here**
- `ERRATUM_v0_3_1.md`: the four corrections (E1–E4), each with evidence and replacement text.
- `WORKLOG.md`: every step from build to erratum, in order, including mistakes.

**Check it yourself** (Python 3, standard library only, no network)
```
python3 verify.py
```
This reads the three zips in `inputs/` and writes `verification.json`. The expected summary is in `verify_stdout.txt`:
- `allReproductionChecksPass: true`
- `E1_runnerChecksLongHorizonRates: false` and `E1_omittedCheckWouldPass: true`
- `E3_residualErrors_DEEPEN_minus_FADE: 7.96`
- `E4_evidenceOfPost: false`

**Contents**
- `inputs/Constitutional_Commons_v0_3_1_2026-10-04.zip`: Claude's original run, byte-for-byte unchanged.
- `inputs/GrokConstitutional_Commons_v0_3_1_RUN_2026-10-04.zip`: Grok's independent run.
- `inputs/ChatgptConstitutional_Commons_v031_Independent_Execution_2026-10-04.zip`: ChatGPT's independent run and review.
- `verify.py`, `verification.json`, `verify_stdout.txt`: the checks and their output.
- `proposed_harness_fix_B4.diff`: the fix for E1, for the next harness. It is not applied to the frozen runner.
- `MANIFEST.sha256`: hashes of everything above.
