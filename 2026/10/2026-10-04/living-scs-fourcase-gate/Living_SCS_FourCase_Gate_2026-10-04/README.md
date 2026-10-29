# Living SCS: Four-Case Judge Gate (4 October 2026)

- **Start with:** `RESULTS.md`. The acceptance list, written and hashed before any judge was built, is `ACCEPTANCE.md` (hash in `ACCEPTANCE.sha256`).
- **Run it:** `python3 gate_battery.py` (needs `cryptography`). It writes `gate_results.json` and `gate_receipt.txt`; the expected receipt is `a06cc12b…43be8`.

**Files**
- `witness_judge.py`: the witness judge (own clock, persisted head, fail-closed). It also contains `NaiveJudge`, a control only; never deploy it.
- `gate_battery.py`: drives the real v1.1.5 notary and runs the legacy, naive and witness judges through every case.
- `candidate/`: the v1.1.5 layer-2 tree, byte-identical to the reviewed package and unmodified.
- `first_run/`: the battery, results and receipt from before the two harness edits described in `RESULTS.md`.
- `gate_stdout_run_a.txt`, `gate_stdout_run_b.txt`: two consecutive runs, each with fresh keys, producing the same receipt.
