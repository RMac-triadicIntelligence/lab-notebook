# Engineering log — v0.11

1. v0.9 kernel and v0.10 runner copied unchanged for provenance (hashes in run.json).
   New code is repent.py only: declaration operation, penalty/cooldown, counter-mark deposit.
2. Declaration is implemented as a mid-epoch action at step 600 so both its penalty and its
   mark act inside the same run.
3. Development (seed 0): declarations fire (4 of 4 eligible under penalty-free, 3 under
   penalized), and the counter-mark measurably moves generation 3 out of the old-pass band
   under the walk rule (in-band 2 → 1). Instrument validated; no constant retuned afterwards.
