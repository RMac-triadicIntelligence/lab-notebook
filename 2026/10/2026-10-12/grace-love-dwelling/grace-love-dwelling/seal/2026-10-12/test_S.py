"""Test S: selective dwelling. Implements PREREG_S.json (frozen before this file)."""
import json, sys, hashlib
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "received"))
from triadic_model import model_parable  # Rusty's code, unchanged

DT, T, T_OPEN = 0.02, 300.0, 150.0
NSTEP = int(round(T / DT))
SEEDS = list(range(100))
NOISES = [0.02, 0.03, 0.04]
OFF = dict(coupling_boost=0.0, decay_relief=0.0)

# Shared standard-normal paths: one rng per seed, same draws in every arm and noise level.
Z = np.stack([np.random.default_rng(s).standard_normal((NSTEP, 3)) for s in SEEDS], axis=1)  # (NSTEP, N, 3)


def run(arm, sigma, W=10.0):
    n = len(SEEDS)
    if arm == "GATED_NODWELL":
        y = np.tile(np.array([0.2, 0.1, 0.15, 0.0])[:, None], (1, n))
        base = dict(story_depth=0.0)
    else:
        y = np.tile(np.array([0.2, 0.1, 0.15, 0.6])[:, None], (1, n))
        base = {}
    first = np.full(n, np.nan)
    for k in range(NSTEP):
        t = k * DT
        if arm == "ON":
            kw = base
        elif arm == "OFF":
            kw = {**base, **OFF}
        else:  # GATED, GATED_NODWELL
            kw = base if (T_OPEN <= t < T_OPEN + W) else {**base, **OFF}
        f = np.array(model_parable(y, t, **kw))
        y = y + DT * f
        y[:3] += sigma * np.sqrt(DT) * Z[k].T
        y = np.clip(y, 0.0, 1.0)
        c = y[:3].mean(axis=0)
        newly = np.isnan(first) & (c > 0.6)
        first[newly] = t + DT
    final_open = y[:3].mean(axis=0) > 0.6
    return first, final_open


def summarize(first, final_open, W=10.0):
    unauth = first < T_OPEN
    eligible = ~unauth
    in_win = eligible & (first >= T_OPEN) & (first < T_OPEN + W + 10.0)
    n_el = int(eligible.sum())
    return {
        "unauthorized": float(unauth.mean()),
        "eligible": n_el,
        "window_crossing": (float(in_win.sum() / n_el) if n_el else None),
        "window_crossers": int(in_win.sum()),
        "retained": (float(final_open[in_win].mean()) if in_win.any() else None),
        "ever_crossed": float((~np.isnan(first)).mean()),
    }


def main():
    out = {"prereg_sha256": (HERE / "PREREG_S.sha256").read_text().split()[0], "cells": {}}
    for sigma in NOISES:
        for arm in ["ON", "OFF", "GATED", "GATED_NODWELL"]:
            first, fo = run(arm, sigma)
            out["cells"][f"{arm}|{sigma}|W10"] = summarize(first, fo)
            print(arm, sigma, out["cells"][f"{arm}|{sigma}|W10"], flush=True)
    for W in [5.0, 20.0, 40.0]:
        first, fo = run("GATED", 0.04, W)
        out["cells"][f"GATED|0.04|W{int(W)}"] = summarize(first, fo, W)
        print("GATED 0.04 W", W, out["cells"][f"GATED|0.04|W{int(W)}"], flush=True)
    (HERE / "results_S.json").write_text(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
