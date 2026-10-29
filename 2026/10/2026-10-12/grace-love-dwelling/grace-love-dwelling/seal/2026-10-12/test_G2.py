"""Test G2: grace as the nudge, love as the field window. Implements PREREG_G2.json (frozen before this file)."""
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "received"))
from triadic_model import model_parable  # unchanged

DT, T, W0, W1, TN = 0.02, 300.0, 150.0, 160.0, 155.0
NSTEP = int(round(T / DT)); KN = int(round(TN / DT))
SEEDS = list(range(100))
OFF = dict(coupling_boost=0.0, decay_relief=0.0)
Z = np.stack([np.random.default_rng(s).standard_normal((NSTEP, 3)) for s in SEEDS], axis=1)
CONDS = ["NONE", "GRACE", "LOVE", "GRACE_LOVE", "GRACE_LOVE_NODWELL"]


def run(cond, sigma, g, n=None):
    n = n or len(SEEDS)
    nodwell = cond.endswith("NODWELL")
    y = np.tile(np.array([0.2, 0.1, 0.15, 0.0 if nodwell else 0.6])[:, None], (1, n))
    base = dict(story_depth=0.0) if nodwell else {}
    love = "LOVE" in cond
    grace = "GRACE" in cond
    first = np.full(n, np.nan)
    for k in range(NSTEP):
        t = k * DT
        kw = base if (love and W0 <= t < W1) else {**base, **OFF}
        f = np.array(model_parable(y, t, **kw))
        y = y + DT * f
        if sigma:
            y[:3] += sigma * np.sqrt(DT) * Z[k, :n].T
        if grace and k == KN:
            y[0] += g
        y = np.clip(y, 0.0, 1.0)
        c = y[:3].mean(axis=0)
        newly = np.isnan(first) & (c > 0.6)
        first[newly] = t + DT
    open_end = y[:3].mean(axis=0) > 0.6
    return first, open_end


def crossed(first, open_end):
    return (first >= W0) & open_end


def g_star(cond):
    lo, hi = 0.0, 1.0
    for _ in range(14):
        m = (lo + hi) / 2
        f, o = run(cond, 0.0, m, n=1)
        if crossed(f, o)[0]: hi = m
        else: lo = m
    return round(hi, 5)


def main():
    out = {"prereg_sha256": (HERE / "PREREG_G2.sha256").read_text().split()[0], "g_star": {}, "cells": {}}
    for c in ["GRACE", "GRACE_LOVE", "GRACE_LOVE_NODWELL"]:
        out["g_star"][c] = g_star(c); print("g*", c, out["g_star"][c], flush=True)
    for sigma in [0.02, 0.04]:
        for c in CONDS:
            gs = [0.0] if c in ("NONE", "LOVE") else [0.10, 0.20, 0.25, 0.30, 0.40]
            for g in gs:
                f, o = run(c, sigma, g)
                after = f >= W0
                cell = {"p_cross": float(crossed(f, o).mean()), "unauthorized": float((f < W0).mean()),
                        "retained": (float(o[after].mean()) if after.any() else None), "n_after": int(after.sum())}
                out["cells"][f"{c}|{sigma}|{g}"] = cell
                print(c, sigma, g, cell, flush=True)
    (HERE / "results_G2.json").write_text(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
