"""Test T: terrain vs counter in a multi-coordinate world. Implements PREREG_T.json (frozen before this file)."""
import json, sys
from collections import Counter
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "received"))
from origami_kenta_sdkp import ConsciousnessLayer, SDKPTuple  # unchanged

N_STREAMS, EPD, DAYS = 200, 6, 365
WORLDS = ["PREF", "CONF", "NULL"]
VARIANTS = {"2coord": 0, "4coord": 1}
PW, KW = [0.4, 0.3, 0.2, 0.1], [0.5, 0.35, 0.15]


def make_stream(world, variant, s):
    rng = np.random.default_rng(1000 * WORLDS.index(world) + 10 * VARIANTS[variant] + s)
    n = EPD * DAYS
    P = rng.choice(4, size=n, p=PW)
    K = rng.choice(3, size=n, p=KW)
    if variant == "4coord":
        S = rng.integers(0, 3, size=n); D = rng.integers(0, 3, size=n)
    else:
        S = np.zeros(n, int); D = np.zeros(n, int)
    u = rng.random(n)
    if world == "PREF":
        p = np.full(n, 0.6)
    elif world == "CONF":
        p = np.where((P == 0) & (K == 2), 0.9, 0.1)
    else:
        p = np.full(n, 0.1)
    sig = u < p
    return S, D, K, P, sig


def key_place(s, d, k, p): return SDKPTuple(0, 0, 0, int(p))
def key_scalar(s, d, k, p): return SDKPTuple(int((s + 1) * (d + 1) * (k + 1) * (p + 1)), 0, 0, 0)
def key_full(s, d, k, p): return SDKPTuple(int(s), int(d), int(k), int(p))


class CounterLayer:
    """T0 control: plain Counter, threshold 5, permanent."""
    SEUIL_MOT = 5
    def __init__(self):
        self.cooccurrence_counts = Counter(); self.grounded_symbols = {}
    def receive(self, sdkp, context, idx):
        key = (sdkp, context)
        if key in self.grounded_symbols: return self.grounded_symbols[key]
        self.cooccurrence_counts[key] += 1
        if self.cooccurrence_counts[key] >= self.SEUIL_MOT:
            self.grounded_symbols[key] = "g"
        return None


def occupied_view(layer, keys_filter=None):
    """Return {key: (weight, sig_crystallized)} for occupied keys."""
    tot = Counter(); occ = {}
    for (k, ctx), c in layer.cooccurrence_counts.items():
        tot[k] += c
    for (k, ctx) in layer.grounded_symbols:
        occ.setdefault(k, False)
        if ctx == "sig": occ[k] = True
    return {k: (tot[k], sg) for k, sg in occ.items()}


def rollup_view(full, place):
    vf, vp = occupied_view(full), occupied_view(place)
    out = {}
    for p in range(4):
        under = {k: v for k, v in vf.items() if k.position == p}
        if under:
            out.update({("F", k): v for k, v in under.items()})
        elif SDKPTuple(0, 0, 0, p) in vp:
            out[("P", p)] = vp[SDKPTuple(0, 0, 0, p)]
    return out


def run_reader(stream, reader, shuffle_seed=None, layer_cls=ConsciousnessLayer):
    S, D, K, P, sig = stream
    if shuffle_seed is not None:
        sig = np.random.default_rng(shuffle_seed).permutation(sig)
    if reader == "R_roll":
        full, place = layer_cls(), layer_cls()
    else:
        layer = layer_cls()
        keyf = {"R_place": key_place, "R_scalar": key_scalar, "R_full": key_full}[reader]
    state, footprint, cum_sig, next_need = "WAIT", set(), 0, 8
    commit_day = None
    for i in range(len(sig)):
        day = i // EPD + 1
        ctx = "sig" if sig[i] else "ord"
        if reader == "R_roll":
            full.receive(key_full(S[i], D[i], K[i], P[i]), ctx, i)
            place.receive(key_place(S[i], D[i], K[i], P[i]), ctx, i)
        else:
            layer.receive(keyf(S[i], D[i], K[i], P[i]), ctx, i)
        if sig[i]:
            cum_sig += 1
        if cum_sig >= next_need:
            next_need += 8
            view = rollup_view(full, place) if reader == "R_roll" else occupied_view(layer)
            sig_keys = {k for k, (w, sg) in view.items() if sg}
            if state == "HOLD" and not (sig_keys - footprint):
                continue  # pressure alone never reopens
            if not view:
                continue
            wt = sum(w for w, _ in view.values())
            frac = sum(w for k, (w, sg) in view.items() if sg) / wt
            if frac >= 0.5:
                commit_day = day
                break
            if sig_keys:
                state = "HOLD"; footprint |= sig_keys
    return commit_day


def rate_by(days, cut):
    return float(np.mean([d is not None and d <= cut for d in days]))


def summarize(days):
    c = [d for d in days if d is not None]
    return {"d60": rate_by(days, 60), "d120": rate_by(days, 120), "d365": rate_by(days, 365),
            "median_commit_day": (float(np.median(c)) if c else None), "n_commit": len(c)}


def main():
    out = {"prereg_sha256": (HERE / "PREREG_T.sha256").read_text().split()[0], "cells": {}, "T0": {}}
    readers = ["R_place", "R_scalar", "R_full", "R_roll"]
    for w in WORLDS:
        for v in VARIANTS:
            streams = [make_stream(w, v, s) for s in range(N_STREAMS)]
            for r in readers:
                days = [run_reader(st, r) for st in streams]
                out["cells"][f"{w}|{v}|{r}"] = summarize(days)
                print(w, v, r, out["cells"][f"{w}|{v}|{r}"], flush=True)
            plain = [run_reader(st, "R_full", layer_cls=CounterLayer) for st in streams]
            layerd = [run_reader(st, "R_full") for st in streams]
            out["T0"][f"{w}|{v}"] = float(np.mean([a == b for a, b in zip(plain, layerd)]))
            if w == "CONF" and v == "2coord":
                sh = [run_reader(st, "R_full", shuffle_seed=777 + s) for s, st in enumerate(streams)]
                out["cells"]["CONF|2coord|R_full_SHUFFLED"] = summarize(sh)
                print("shuffled", out["cells"]["CONF|2coord|R_full_SHUFFLED"], flush=True)
    print("T0", out["T0"])
    (HERE / "results_T.json").write_text(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
