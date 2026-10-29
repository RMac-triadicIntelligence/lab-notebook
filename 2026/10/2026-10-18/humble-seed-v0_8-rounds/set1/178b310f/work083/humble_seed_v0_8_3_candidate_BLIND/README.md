# Humble Seed v0.8.3 CANDIDATE — blind review pack

A small "organism" that may change its own character only when its owner signs a reading,
and only in ways the owner tool can verify afterwards. This pack holds the candidate, a
falsification harness, and a declaration of predicted outcomes frozen before the harness
was written. It contains **no results**.

v0.8.3 adds an owner-side ledger. It runs reading lifetimes on the owner's clock, treats
an owner's answer as their current position, and checks every field of every change
record. The candidate's docstring explains each change and lists the known limits.

## Run it

```
python3 -I falsify_v0_8_3.py
```

Requires Python 3.10+ and `cryptography`; runs in about 15 seconds with no network.
Please report:

- the final **receipt** line, your Python version and your cryptography version;
- the exit code, every MISMATCH line, and **your diagnosis of each mismatch**.

`RECEIPT_COMMITMENT_v0_8_3.txt` commits to the expected receipt. The salt is released
after you report.

## Then look for what the harness misses

- Can a crossing be attested that the owner didn't sign, answered "no" to, or let lapse?
- Can ordinary use stop a valid reading from ever applying, or leave a state that can never
  be attested?
- Do the organism-side and owner-side checks ever disagree in a way that matters?
- Is any test true by construction, or any mutant killed for the wrong reason?

Runnable code with actual output is the most useful form for a finding. Please include it
for every "no evidence of X" claim too.

## Files

| File | What |
|---|---|
| `humble_seed_v0_8_3_candidate.py` | The candidate |
| `falsify_v0_8_3.py` | The harness; reads the mutants from the declaration |
| `DECLARED_v0_8_3.json` (+ `.sha256`, `.frozen_at`) | Frozen predictions |
| `CANDIDATE_v0_8_3_AT_FREEZE.sha256` | Candidate hash at the freeze |
| `parent_humble_seed_v0_7_C5.py` | v0.7 parent, used by T20 |
| `v0_8_2_record/humble_seed_v0_8_2_candidate.py` | The previous version, for diffing |
| `MANIFEST.sha256` | Hashes of everything above |
