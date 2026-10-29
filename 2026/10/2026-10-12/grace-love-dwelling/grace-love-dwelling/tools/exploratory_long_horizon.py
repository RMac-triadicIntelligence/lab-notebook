#!/usr/bin/env python3
"""EXPLORATORY, not preregistered. Reproduces seal/2026-10-12/EXPLORATORY_T_long_horizon.txt.
Does the 4-coordinate full reader's protection hold past day 365, or is it only delay?
Runs in a scratch copy of the seal; imports test_T.py unchanged and only lengthens the horizon."""
import shutil, sys, tempfile
from pathlib import Path

SEAL = Path(__file__).resolve().parent.parent / "seal" / "2026-10-12"

with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp) / "seal"
    shutil.copytree(SEAL, work)
    sys.path.insert(0, str(work))
    import test_T as T
    T.DAYS = 1825
    for w in ["CONF", "NULL"]:
        streams = [T.make_stream(w, "4coord", s) for s in range(100)]
        for r in ["R_full", "R_place"]:
            days = [T.run_reader(st, r) for st in streams]
            print(w, "4coord", r, {c: T.rate_by(days, c) for c in [365, 730, 1095, 1825]})
