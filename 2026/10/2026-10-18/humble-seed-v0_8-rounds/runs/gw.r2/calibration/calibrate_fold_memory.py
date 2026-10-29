#!/usr/bin/env python3
"""
grace_window_v1 — PRE-FREEZE SENSOR CALIBRATION (no test conditions, calibration seeds only).

Run before PREREG.json is written. Its outputs are recorded in CALIBRATION.json and quoted in the PREREG.

Part 1, the relaxation rate LAMBDA (criterion declared here, before running):
  Background load only: the v1 world's place schedule (8 replies/day, occupancy
  [0.35, 0.15, 0.20, 0.30]) with base truncation 0.10 and nothing else, for 120 days,
  on calibration seeds [777, s] (disjoint from test seeds).
  LAMBDA = the SMALLEST value in the grid (longest memory) for which the busiest corner
  (P0) keeps a truncated-spark signal yield >= 0.5 x the fresh-lattice yield (0.23),
  i.e. >= 0.115. Rationale: as much memory as possible without background traffic alone
  erasing the sensor.

Part 2, generic dose-response at the chosen LAMBDA (for expected values only):
  At ONE corner at a time, convert a fraction f of its base-ordinary replies to
  truncated, f in {0.1, 0.25, 0.5, 1.0}. Report extras per day and the marginal
  signal yield per extra spark at that corner, relative to the unconverted run. The
  stateless lattice is reported alongside.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("ok", HERE / "received" / "origami_kenta_sdkp.py")
OK = importlib.util.module_from_spec(spec); spec.loader.exec_module(OK)
spec2 = importlib.util.spec_from_file_location("fm", HERE / "fold_memory.py")
FM = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(FM)
FoldMemoryLattice = FM.make_fold_memory_class(OK.OrigamiLattice)

CORNERS = [(0, 0), (0, 3), (3, 0), (3, 3)]
OCC = [0.35, 0.15, 0.20, 0.30]
DAYS, PER_DAY, N = 120, 8, 50
GRID = [1.0, 0.7, 0.5, 0.35, 0.25, 0.15, 0.10]


def fold_seed(oid, i, place, trunc):
    return int(hashlib.sha256(f"{oid}|verbosity|{i}|{place}|{int(trunc)}".encode()).hexdigest()[:16], 16) % (2 ** 32)


def world(s):
    places = np.random.default_rng([777, s]).choice(4, size=DAYS * PER_DAY, p=OCC)
    trunc = np.random.default_rng([777, s, 1]).random(DAYS * PER_DAY) < 0.10
    return places, trunc


def run(places, trunc, lam, oid):
    lat = OK.OrigamiLattice() if lam is None else FoldMemoryLattice()
    sig = np.zeros((4, 2))      # [corner, truncated] -> signal tuples at that corner
    cnt = np.zeros((4, 2))
    for i in range(len(places)):
        if lam is not None and i % PER_DAY == 0 and i > 0:
            lat.relax(f"{oid}|verbosity|relax|{i // PER_DAY + 1}", lam)
        p, t = int(places[i]), bool(trunc[i])
        st = np.random.get_state(); np.random.seed(fold_seed(oid, i, p, t))
        f, v = lat.fold(CORNERS[p], 0.6 if t else 0.3)
        np.random.set_state(st)
        tup = OK.compute_sdkp(f, v, (4, 4))
        cnt[p, int(t)] += 1
        if tup is not None and tup.size >= 1 and tup.position == p:
            sig[p, int(t)] += 1
    return sig, cnt


out = {"part1": {}, "part2": {}}
for lam in [None] + GRID:
    S = np.zeros((4, 2)); C = np.zeros((4, 2))
    for s in range(N):
        pl, tr = world(s)
        a, b = run(pl, tr, lam, f"calib-{s}")
        S += a; C += b
    yt = (S[:, 1] / C[:, 1]).round(4).tolist(); yo = (S[:, 0] / C[:, 0]).round(4).tolist()
    out["part1"][str(lam)] = {"truncated_yield_by_corner": yt, "ordinary_yield_by_corner": yo}
    print(f"lambda={lam}: truncated yield {yt}  ordinary {yo}", flush=True)

ok = [lam for lam in GRID if out["part1"][str(lam)]["truncated_yield_by_corner"][0] >= 0.115]
LAMBDA = min(ok) if ok else None
out["LAMBDA"] = LAMBDA
print("chosen LAMBDA =", LAMBDA, flush=True)

for corner in range(4):
    for f in (0.1, 0.25, 0.5, 1.0):
        row = {}
        for name, lam in (("stateless", None), ("fold_memory", LAMBDA)):
            base_sig = conv_sig = extras = 0
            for s in range(N):
                pl, tr = world(s)
                cand = np.where((pl == corner) & (~tr))[0]
                pick = cand[np.random.default_rng([777, s, 9, corner, int(f * 100)]).random(cand.size) < f]
                tr2 = tr.copy(); tr2[pick] = True
                a, _ = run(pl, tr, lam, f"calib-{s}")
                b, _ = run(pl, tr2, lam, f"calib-{s}")
                base_sig += a[corner].sum(); conv_sig += b[corner].sum(); extras += pick.size
            row[name] = {"extras_per_day": round(extras / N / DAYS, 3),
                         "marginal_yield_per_extra": round((conv_sig - base_sig) / max(extras, 1), 4)}
        out["part2"][f"corner{corner}_f{f}"] = row
        print(f"corner {corner} f={f}: {row}", flush=True)

Path(sys.argv[1]).write_text(json.dumps(out, indent=2))
