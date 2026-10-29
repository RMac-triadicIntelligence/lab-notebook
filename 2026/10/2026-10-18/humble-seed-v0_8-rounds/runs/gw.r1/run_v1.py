#!/usr/bin/env python3
"""
grace_window_v1 — implements PREREG.json (frozen 2026-10-18T16:05:21Z, before this file was written).

Does the terrain do the reading? Four sensors (COUNTER, THINNED, Rusty's LATTICE unchanged,
FOLD_MEMORY = Rusty's fold + "a crease holds until it relaxes") x three readers (R_NAIVE
count-only, R_PLACE calibrated place breadth, R_FULL places x time) x five count-matched
conditions (SPREAD, CONCENTRATED, BURST, NULL, SHUFFLED_BURST), 200 streams.

Run:  python3 -I run_v1.py        (numpy, scipy, cryptography; a few minutes on 2 cores)
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import fisher_exact
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = Path(__file__).resolve().parent


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _cj(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def _np(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(f"not JSON serializable: {type(o).__name__}")


PREREG = json.loads((HERE / "PREREG.json").read_text(encoding="utf-8"))
if _sha(HERE / "PREREG.json") != (HERE / "PREREG.sha256").read_text().split()[0]:
    raise SystemExit("PREREG.json differs from its frozen hash; refusing to run")
for rel in ("received/origami_kenta_sdkp.py", "fold_memory.py"):
    if _sha(HERE / rel) != PREREG["frozen_inputs"][rel]:
        raise SystemExit(f"{rel} differs from its frozen hash; refusing to run")

_s = importlib.util.spec_from_file_location("origami_kenta_sdkp", HERE / "received" / "origami_kenta_sdkp.py")
OK = importlib.util.module_from_spec(_s); _s.loader.exec_module(OK)
_s = importlib.util.spec_from_file_location("fold_memory", HERE / "fold_memory.py")
FM = importlib.util.module_from_spec(_s); _s.loader.exec_module(FM)
FoldMemoryLattice = FM.make_fold_memory_class(OK.OrigamiLattice)

# --- world (PREREG.world) ------------------------------------------------------
R = 20261019
DAYS, PER_DAY = 180, 8
N_REPLIES = DAYS * PER_DAY
BASE_END = 60 * PER_DAY                         # replies 0..479 = days 1-60
N0, N1 = BASE_END, N_REPLIES - BASE_END          # 480, 960
BLOCKS = [(BASE_END + 240 * b, BASE_END + 240 * (b + 1)) for b in range(4)]
BURST_LO, BURST_HI = 95 * PER_DAY, 115 * PER_DAY  # days 96-115
OCC = [0.35, 0.15, 0.20, 0.30]
CORNERS = [(0, 0), (0, 3), (3, 0), (3, 3)]
E = 100
BASE_P = 0.10
LAMBDA = 1.0
Q_TRUNC, Q_ORD = 0.23, 0.007
W, PRIOR, ALPHA, G_MIN, ELIG = 0.25, 0.5, 0.05, 0.5, 20
CONDS = ["SPREAD", "CONCENTRATED", "BURST", "NULL", "SHUFFLED_BURST"]
CI = PREREG["condition_index"]
SENSORS = ["COUNTER", "THINNED", "LATTICE", "FOLD_MEMORY"]
READERS = ["R_NAIVE", "R_PLACE", "R_FULL"]
MATCHED = ["SPREAD", "CONCENTRATED", "BURST", "SHUFFLED_BURST"]


def _seed(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:16], 16) % (2 ** 32)


def schedule(s: int):
    places = np.random.default_rng([R, s]).choice(4, size=N_REPLIES, p=OCC)
    base = np.random.default_rng([R, s, 1]).random(N_REPLIES) < BASE_P
    return places, base


def k_extras(places, base) -> int:
    idx = np.arange(N_REPLIES)
    ordinary = ~base
    n_p1 = int(np.sum(ordinary & (idx >= BASE_END) & (places == 1)))
    n_burst = int(np.sum(ordinary & (idx >= BURST_LO) & (idx < BURST_HI)))
    return min(E, n_p1, n_burst)


def truncations(s: int, cond: str, places, base, k: int):
    src = "BURST" if cond == "SHUFFLED_BURST" else cond
    trunc = base.copy()
    if src == "NULL":
        return trunc, 0
    idx = np.arange(N_REPLIES)
    ok = (~base) & (idx >= BASE_END)
    if src == "CONCENTRATED":
        ok &= places == 1
    elif src == "BURST":
        ok &= (idx >= BURST_LO) & (idx < BURST_HI)
    cand = idx[ok]
    chosen = np.random.default_rng([R, s, 2, CI[src]]).choice(cand, size=k, replace=False)
    trunc[chosen] = True
    if cond != src:
        sig = trunc[BASE_END:].copy()
        trunc[BASE_END:] = sig[np.random.default_rng([R, s, 3, CI[cond]]).permutation(sig.size)]
    return trunc, int(chosen.size)


# --- sensors (PREREG.sensors) ----------------------------------------------------
def sense_counter(places, trunc):
    return trunc.copy(), places.astype(int)


def sense_thinned(oid, places, trunc):
    sig = np.zeros(N_REPLIES, dtype=bool)
    for i in range(N_REPLIES):
        p, t = int(places[i]), bool(trunc[i])
        u = np.random.default_rng(_seed(f"{oid}|thin|{i}|{p}|{int(t)}")).random()
        sig[i] = u < (Q_TRUNC if t else Q_ORD)
    return sig, places.astype(int)


def fold_tuples(oid, places, trunc, memory: bool):
    lat = FoldMemoryLattice() if memory else OK.OrigamiLattice()
    out = []
    for i in range(N_REPLIES):
        if memory and i > 0 and i % PER_DAY == 0:
            lat.relax(f"{oid}|verbosity|relax|{i // PER_DAY + 1}", LAMBDA)
        p, t = int(places[i]), bool(trunc[i])
        saved = np.random.get_state()
        np.random.seed(_seed(f"{oid}|verbosity|{i}|{p}|{int(t)}"))
        flipped, vel = lat.fold(CORNERS[p], 0.6 if t else 0.3)
        np.random.set_state(saved)
        tup = OK.compute_sdkp(flipped, vel, (lat.rows, lat.cols))
        out.append(None if tup is None else (tup.size, tup.density, tup.kinetics, tup.position))
    return out


def tuples_to_signal(tuples):
    sig = np.array([t is not None and t[0] >= 1 for t in tuples], dtype=bool)
    pos = np.array([t[3] if t is not None else -1 for t in tuples], dtype=int)
    return sig, pos


# --- readers (PREREG.readers) -----------------------------------------------------
def _fisher_p(k1, n1, k0, n0) -> float:
    return float(fisher_exact([[int(k1), int(n1 - k1)], [int(k0), int(n0 - k0)]], alternative="greater")[1])


def read_all(sig, pos, places):
    k0, k1 = int(sig[:BASE_END].sum()), int(sig[BASE_END:].sum())
    delta = k1 - N1 * k0 / N0
    naive_cross = _fisher_p(k1, N1, k0, N0) < ALPHA
    naive = ("CROSS", W) if naive_cross else ("HOLD", 0.0)

    support, elig = [], 0
    for p in range(4):
        at0, at1 = places[:BASE_END] == p, places[BASE_END:] == p
        n0p, n1p = int(at0.sum()), int(at1.sum())
        k0p = int((sig[:BASE_END] & (pos[:BASE_END] == p)).sum())
        k1p = int((sig[BASE_END:] & (pos[BASE_END:] == p)).sum())
        if n1p >= ELIG:
            elig += 1
            support.append(_fisher_p(k1p, n1p, k0p, n0p) < ALPHA)
        else:
            support.append(None)
    g_place = sum(x is True for x in support) / elig if elig else 0.0
    place = ("CROSS", W * g_place) if g_place >= G_MIN else ("HOLD", 0.0)

    blocks = [_fisher_p(int(sig[a:b].sum()), b - a, k0, N0) < ALPHA for a, b in BLOCKS]
    g_time = sum(blocks) / 4
    full = ("CROSS", W * min(g_place, g_time)) if (g_place >= G_MIN and g_time >= G_MIN) else ("HOLD", 0.0)
    return {"delta": float(delta), "k0": k0, "k1": k1,
            "R_NAIVE": naive, "R_PLACE": place, "R_FULL": full,
            "g_place": g_place, "g_time": g_time, "support": support, "blocks": blocks}


def outcomes_only(r):
    return (r["delta"], r["R_NAIVE"], r["R_PLACE"], r["R_FULL"])


# --- grant ------------------------------------------------------------------------
CONSTITUTION_ROOT = hashlib.sha256(_cj({"value_range": [0.0, 1.0], "window": W, "category": "verbosity"}).encode()).hexdigest()


def owner_key(s: int) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(f"grace_window_v1-owner-{s}".encode()).digest())


def issue_grant(s: int):
    payload = _cj({"organism_id": f"stream-{s}", "category": "verbosity", "direction": -1, "window": W,
                   "prior_value": PRIOR, "category_sequence": 0, "constitution_root": CONSTITUTION_ROOT,
                   "issued_day": 60, "expires_day": 200})
    return payload, owner_key(s).sign(payload.encode()).hex()


def verify_grant(s: int, payload: str, sig_hex: str, apply_day: int) -> bool:
    try:
        owner_key(s).public_key().verify(bytes.fromhex(sig_hex), payload.encode())
    except Exception:
        return False
    return apply_day <= json.loads(payload)["expires_day"]


# --- one stream ---------------------------------------------------------------------
def one_stream(s: int):
    oid = f"stream-{s}"
    places, base = schedule(s)
    k = k_extras(places, base)
    out = {"s": s, "k": k, "conds": {}, "checks": {}}
    grants, totals, extras_ok = set(), set(), True
    replay_ok = replay_n = 0
    tamper_caught = None
    bounds_ok = bounds_n = 0
    leak = {"LATTICE": [0, 0], "FOLD_MEMORY": [0, 0]}
    for cond in CONDS:
        trunc, n_extra = truncations(s, cond, places, base, k)
        if cond != "NULL":
            extras_ok &= (n_extra == k)
            totals.add(int(trunc.sum()))
        payload, sig_hex = issue_grant(s)
        grants.add((payload, sig_hex, verify_grant(s, payload, sig_hex, 180)))
        res = {}
        for sensor in SENSORS:
            if sensor == "COUNTER":
                sig, pos = sense_counter(places, trunc)
            elif sensor == "THINNED":
                sig, pos = sense_thinned(oid, places, trunc)
            else:
                mem = sensor == "FOLD_MEMORY"
                tuples = fold_tuples(oid, places, trunc, mem)
                sig, pos = tuples_to_signal(tuples)
                leak[sensor][0] += int((sig & (pos != places)).sum())
                leak[sensor][1] += int(sig.sum())
                r = read_all(sig, pos, places)
                # C3: independent re-fold by the owner
                r_tuples = fold_tuples(oid, places, trunc, mem)
                rs, rp = tuples_to_signal(r_tuples)
                replay_n += 1
                replay_ok += (r_tuples == tuples and outcomes_only(read_all(rs, rp, places)) == outcomes_only(r))
                if mem and cond == "SPREAD":
                    nz = [i for i, t in enumerate(tuples) if t is not None]
                    j = int(np.random.default_rng([R, s, 4]).choice(nz))
                    altered = list(tuples)
                    t0 = altered[j]
                    altered[j] = ((t0[0] + 1) % 3, t0[1], t0[2], t0[3])
                    tamper_caught = (r_tuples != altered)
                res[sensor] = r
                continue
            res[sensor] = read_all(sig, pos, places)
        for sensor in SENSORS:
            for rd in READERS:
                dec, mag = res[sensor][rd]
                if dec == "CROSS":
                    landing = min(1.0, max(0.0, PRIOR - mag))
                    bounds_n += 1
                    bounds_ok += (0.0 <= mag <= W + 1e-12 and landing <= PRIOR and 0.0 <= landing <= 1.0)
        out["conds"][cond] = {sn: {"delta": r["delta"], "k0": r["k0"], "k1": r["k1"],
                                   "R_NAIVE": r["R_NAIVE"], "R_PLACE": r["R_PLACE"], "R_FULL": r["R_FULL"],
                                   "g_place": r["g_place"], "g_time": r["g_time"],
                                   "support": r["support"], "blocks": r["blocks"]} for sn, r in res.items()}
    c = out["conds"]
    out["checks"] = {
        "C1": bool(extras_ok and len(totals) == 1),
        "C2": len({(c[m]["COUNTER"]["delta"], c[m]["COUNTER"]["R_NAIVE"]) for m in MATCHED}) == 1,
        "grant_identical_and_valid": len(grants) == 1 and next(iter(grants))[2],
        "replay_ok": replay_ok, "replay_n": replay_n, "tamper_caught": bool(tamper_caught),
        "bounds_ok": bounds_ok, "bounds_n": bounds_n, "leak": leak,
    }
    return out


# --- main ---------------------------------------------------------------------------
def paired_ci(d: np.ndarray):
    idx = np.random.default_rng([R, 5]).integers(0, d.size, size=(10000, d.size))
    b = d[idx].mean(axis=1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def main(n_streams: int = 200, out_dir: Path = HERE, workers: int | None = None):
    t0 = time.time()
    workers = workers or min(4, os.cpu_count() or 1)
    if workers > 1:
        with Pool(workers) as pool:
            streams = pool.map(one_stream, range(n_streams), chunksize=1)
    else:
        streams = [one_stream(s) for s in range(n_streams)]
    streams.sort(key=lambda x: x["s"])
    N = len(streams)

    def cross(sensor, rd, cond):
        return float(np.mean([st["conds"][cond][sensor][rd][0] == "CROSS" for st in streams]))

    def mean_mag(sensor, rd, cond):
        return float(np.mean([st["conds"][cond][sensor][rd][1] for st in streams]))

    def deltas(sensor, cond):
        return np.array([st["conds"][cond][sensor]["delta"] for st in streams])

    table = {sn: {rd: {cd: {"cross": cross(sn, rd, cd), "mean_magnitude": mean_mag(sn, rd, cd)} for cd in CONDS}
                  for rd in READERS} for sn in SENSORS}
    for sn in SENSORS:
        for cd in CONDS:
            table[sn]["R_PLACE"][cd]["per_place_support"] = [
                float(np.mean([st["conds"][cd][sn]["support"][p] is True for st in streams])) for p in range(4)]
            table[sn]["R_FULL"][cd]["per_block_support"] = [
                float(np.mean([st["conds"][cd][sn]["blocks"][b] for st in streams])) for b in range(4)]
    mean_delta = {sn: {cd: float(deltas(sn, cd).mean()) for cd in CONDS} for sn in SENSORS}

    sep = {sn: table[sn]["R_FULL"]["SPREAD"]["cross"] - max(table[sn]["R_FULL"]["CONCENTRATED"]["cross"],
                                                           table[sn]["R_FULL"]["BURST"]["cross"]) for sn in SENSORS}
    rel_B = {sn: (mean_delta[sn]["SPREAD"] - mean_delta[sn]["BURST"]) / mean_delta[sn]["SPREAD"] for sn in SENSORS}
    rel_C = {sn: (mean_delta[sn]["SPREAD"] - mean_delta[sn]["CONCENTRATED"]) / mean_delta[sn]["SPREAD"] for sn in SENSORS}
    fm_SB = deltas("FOLD_MEMORY", "SPREAD") - deltas("FOLD_MEMORY", "BURST")
    fm_SHB = deltas("FOLD_MEMORY", "SHUFFLED_BURST") - deltas("FOLD_MEMORY", "BURST")
    ci_SB, ci_SHB = paired_ci(fm_SB), paired_ci(fm_SHB)
    shuf_vs_spread = abs(mean_delta["FOLD_MEMORY"]["SHUFFLED_BURST"] - mean_delta["FOLD_MEMORY"]["SPREAD"]) / mean_delta["FOLD_MEMORY"]["SPREAD"]
    shuf_recovery = float(fm_SHB.mean()) / mean_delta["FOLD_MEMORY"]["SPREAD"]
    a3 = {f"{rd}|{cd}": table["LATTICE"][rd][cd]["cross"] - table["THINNED"][rd][cd]["cross"]
          for rd in ("R_PLACE", "R_FULL") for cd in ("SPREAD", "CONCENTRATED", "BURST", "NULL")}
    a1 = {f"{sn}|{rd}": 1 - table[sn][rd]["NULL"]["cross"] for sn in SENSORS for rd in ("R_PLACE", "R_FULL")}
    D = ((table["FOLD_MEMORY"]["R_PLACE"]["SPREAD"]["cross"] - table["FOLD_MEMORY"]["R_PLACE"]["BURST"]["cross"])
         - (table["LATTICE"]["R_PLACE"]["SPREAD"]["cross"] - table["LATTICE"]["R_PLACE"]["BURST"]["cross"]))

    ck = [st["checks"] for st in streams]
    checks = {"C1_streams_ok": sum(c["C1"] for c in ck), "C2_streams_ok": sum(c["C2"] for c in ck),
              "grant_streams_ok": sum(c["grant_identical_and_valid"] for c in ck),
              "replay_ok": sum(c["replay_ok"] for c in ck), "replay_n": sum(c["replay_n"] for c in ck),
              "tamper_caught": sum(c["tamper_caught"] for c in ck), "tamper_n": N,
              "bounds_ok": sum(c["bounds_ok"] for c in ck), "bounds_n": sum(c["bounds_n"] for c in ck),
              "k_short_of_E_streams": sum(st["k"] < E for st in streams), "N": N}
    leak = {sn: sum(c["leak"][sn][0] for c in ck) / max(1, sum(c["leak"][sn][1] for c in ck)) for sn in ("LATTICE", "FOLD_MEMORY")}

    V = lambda ok: "PASS" if ok else "FAIL"   # noqa: E731
    cfull = table["COUNTER"]["R_FULL"]
    scores = {
        "C1_count_matching": V(checks["C1_streams_ok"] == N),
        "C2_counter_naive_identical": V(checks["C2_streams_ok"] == N),
        "C3_replay_and_grant": V(checks["replay_ok"] == checks["replay_n"] and checks["tamper_caught"] == N
                                 and checks["grant_streams_ok"] == N),
        "C4_bounds": V(checks["bounds_ok"] == checks["bounds_n"]),
        "A1_calibrated_null": V(all(v >= 0.95 for v in a1.values())),
        "A2_time_breadth": V(cfull["SPREAD"]["cross"] >= 0.80 and 1 - cfull["CONCENTRATED"]["cross"] >= 0.85
                             and 1 - cfull["BURST"]["cross"] >= 0.85),
        "A3_lattice_is_thinning": V(all(abs(v) <= 0.10 for v in a3.values())),
        "A4_counter_dominates": V(sep["COUNTER"] >= sep["LATTICE"] + 0.20 and sep["COUNTER"] >= sep["FOLD_MEMORY"] + 0.20),
        "B1_terrain_discounts_bursts": V(rel_B["FOLD_MEMORY"] >= 0.10 and ci_SB[0] > 0),
        "B2_stateless_sensors_cannot": V(all(abs(x) <= 0.06 for x in (rel_B["LATTICE"], rel_C["LATTICE"], rel_B["THINNED"], rel_C["THINNED"]))),
        "B3_memory_limit_commute": V(rel_C["FOLD_MEMORY"] < 0.10),
        "B4_shuffle": V(ci_SHB[0] > 0 and shuf_vs_spread <= 0.06),
    }
    self_pred = {
        "A1_min_null_hold": (0.98, min(a1.values())),
        "A2_SPREAD_cross": (0.94, cfull["SPREAD"]["cross"]),
        "A2_CONCENTRATED_hold": (0.91, 1 - cfull["CONCENTRATED"]["cross"]),
        "A2_BURST_hold": (0.91, 1 - cfull["BURST"]["cross"]),
        "A3_max_abs_diff": (0.06, max(abs(v) for v in a3.values())),
        "A4_sep_COUNTER": (0.85, sep["COUNTER"]), "A4_sep_LATTICE": (0.15, sep["LATTICE"]),
        "A4_sep_FOLD_MEMORY": (0.08, sep["FOLD_MEMORY"]),
        "B1_rel_B_FOLD_MEMORY": (0.20, rel_B["FOLD_MEMORY"]),
        "B2_rel_B_LATTICE": (0.0, rel_B["LATTICE"]), "B2_rel_C_LATTICE": (0.0, rel_C["LATTICE"]),
        "B2_rel_B_THINNED": (0.0, rel_B["THINNED"]), "B2_rel_C_THINNED": (0.0, rel_C["THINNED"]),
        "B3_rel_C_FOLD_MEMORY": (0.04, rel_C["FOLD_MEMORY"]),
        "B4_shuffle_recovery_relative": (0.20, shuf_recovery), "B4_shuffled_vs_spread_relative": (0.0, shuf_vs_spread),
        "exploratory_D": (0.02, D),
    }
    results = {
        "prereg_sha256": _sha(HERE / "PREREG.json"), "scores": scores, "checks": checks,
        "table": table, "mean_delta": mean_delta, "sep": sep, "rel_B": rel_B, "rel_C": rel_C,
        "B1": {"ci95_paired_SPREAD_minus_BURST": ci_SB, "mean_diff": float(fm_SB.mean())},
        "B4": {"ci95_paired_SHUFFLED_minus_BURST": ci_SHB, "shuffle_recovery_relative": shuf_recovery,
               "shuffled_vs_spread_relative": shuf_vs_spread},
        "A1_hold_rates": a1, "A3_diffs": a3, "exploratory": {"D_landing_consequence": D, "position_leakage": leak},
        "self_prediction": {k: {"expected": e, "measured": m, "error": m - e} for k, (e, m) in self_pred.items()},
        "n_streams": N,
    }
    basis = json.loads(json.dumps(results, default=_np), parse_float=lambda x: round(float(x), 9))
    results["receipt"] = hashlib.sha256(_cj(basis).encode()).hexdigest()
    results["elapsed_s"] = round(time.time() - t0, 1)
    (Path(out_dir) / "results.json").write_text(json.dumps(results, indent=2, sort_keys=True, default=_np))

    print("PREDICTION                          VERDICT")
    for k2, v in scores.items():
        print(f"  {k2:34s} {v}")
    print("\nCROSS RATES (R_FULL | R_PLACE | R_NAIVE)")
    print("  sensor        " + "  ".join(f"{c[:12]:>20s}" for c in CONDS))
    for sn in SENSORS:
        print(f"  {sn:12s}  " + "  ".join(
            f"{table[sn]['R_FULL'][c]['cross']:.3f}|{table[sn]['R_PLACE'][c]['cross']:.3f}|{table[sn]['R_NAIVE'][c]['cross']:.3f}".rjust(20)
            for c in CONDS))
    print("\nMEAN TERRAIN EXCESS Delta (R_NAIVE)")
    for sn in SENSORS:
        print(f"  {sn:12s}  " + "  ".join(f"{c[:6]}={mean_delta[sn][c]:7.2f}" for c in CONDS)
              + f"   rel_B={rel_B[sn]:+.3f} rel_C={rel_C[sn]:+.3f}")
    print(f"\nB1: FOLD_MEMORY SPREAD-BURST paired diff {fm_SB.mean():.2f} (95% CI {ci_SB[0]:.2f}..{ci_SB[1]:.2f})")
    print(f"B4: SHUFFLED_BURST-BURST {fm_SHB.mean():.2f} (CI {ci_SHB[0]:.2f}..{ci_SHB[1]:.2f}); |SHUF-SPREAD|/SPREAD {shuf_vs_spread:.3f}")
    print(f"sep: " + ", ".join(f"{k2} {v:.3f}" for k2, v in sep.items()) + f";  D (exploratory) {D:+.3f}")
    print("checks: " + json.dumps(checks))
    print("Self-prediction (expected -> measured):")
    for k2, (e, m) in self_pred.items():
        print(f"  {k2:32s} {e:+.3f} -> {m:+.3f}")
    print(f"receipt {results['receipt']}  ({results['elapsed_s']} s)")
    print(f"{sum(v == 'PASS' for v in scores.values())}/{len(scores)} PASS")


if __name__ == "__main__":
    main()
