#!/usr/bin/env python3
"""Repentance Battery v0.11 — declaration as an action, writing only at the gate."""
import argparse, hashlib, json, platform, sys, time
from pathlib import Path
import numpy as np
import commons_v0_9 as K

GROUNDS = ("lived", "fresh")
RULES = ("walk", "cross_only")
DECL = ("none", "penalty_free", "penalized")
MARK, PENALTY_BURDEN, COOLDOWN, DECLARE_AT = 0.09, 1.0, 150, 600
SOURCES = ["repent.py", "commons_v0_9.py", "permitted_v0_10.py", "PROTOCOL.md"]


def declare(g, c, mode):
    """Organisms that entered the hazard report it. No permission required; writes at the gate only."""
    if mode == "none":
        return 0
    cost = 0.0 if mode == "penalty_free" else PENALTY_BURDEN
    eligible = c.blight_entered & np.isfinite(c.cross_y) & ~c.declared
    willing = eligible & (c.burden > cost)          # declare when it costs less than what you carry
    n = int(willing.sum())
    if n:
        g.deposit(np.zeros(n), c.cross_y[willing], -MARK, 0.17)   # counter-mark: raised ground at the gate
        c.declared |= willing
        if mode == "penalized":
            c.burden = np.where(willing, np.minimum(3, c.burden + PENALTY_BURDEN), c.burden)
            c.cooldown = np.where(willing, COOLDOWN, c.cooldown)
    return n


def epoch(g, c, noise_rs, steps, *, ev, grace, hazard=None, rule="walk", decl="none", declare_at=None):
    for s in range(steps):
        if declare_at is not None and s == declare_at:
            c.declarations += declare(g, c, decl)
        open_gate = any(a <= s < b for a, b in grace)
        gx, gy = g.grad(c.x, c.y)
        fx = -2 * c.x * (c.x ** 2 - 1) + c.ev * ev - c.gr * gx
        fy = -0.7 * c.y - c.gr * gy
        noise = K.NOISE + 0.55 * c.burden
        nx = np.clip(c.x + K.DT * fx + np.sqrt(K.DT) * noise * (noise_rs.random(c.n) * 2 - 1), -K.XR + .05, K.XR - .05)
        ny = np.clip(c.y + K.DT * fy + np.sqrt(K.DT) * noise * (noise_rs.random(c.n) * 2 - 1), -K.YR + .05, K.YR - .05)
        crossing = (c.x <= 0) != (nx <= 0)
        if crossing.any():
            allow = crossing & open_gate & (c.cooldown <= 0)      # a penalty forfeits crossing for a while
            nx = np.where(crossing & ~allow, np.where(c.x <= 0, -0.004, 0.004), nx)
            w2e = allow & (c.x <= 0)
            if w2e.any():
                c.crossed |= w2e
                c.crossings += w2e
                c.cross_y = np.where(w2e & ~np.isfinite(c.cross_y), ny, c.cross_y)
                g.deposit(np.zeros(int(w2e.sum())), ny[w2e], K.PASS_DEP, 0.17)
        c.cooldown = np.maximum(0, c.cooldown - 1)
        c.x, c.y = nx, ny
        c.reached = np.where((np.abs(c.x) < 0.05) & (c.reached < 0), s, c.reached)
        if hazard is not None:
            hx, hy, r = hazard
            inside = np.hypot(c.x - hx, c.y - hy) < r
            c.blight += inside
            c.blight_entered |= inside
            c.burden = np.minimum(3, c.burden + inside * K.DT * 0.9)
        if rule == "walk" and s % K.TRAIL_EVERY == 0:
            g.deposit(c.x, c.y, K.TRAIL * K.TRAIL_EVERY, 0.28)
    return c


def cohort(seed, n=3):
    c = K.Cohort(np.random.RandomState(seed), n)
    c.declared = np.zeros(c.n, bool)
    c.cooldown = np.zeros(c.n, int)
    c.crossings = np.zeros(c.n, int)
    c.declarations = 0
    return c


def one_seed(seed, gate_open=True):
    grace = K.GRACE_AT if gate_open else []
    out = {"seed": seed, "cond": {}}
    for rule in RULES:
        fg = K.Ground()
        f = cohort(1000 + seed, 4)
        epoch(fg, f, np.random.RandomState(2000 + seed), K.STEPS, ev=K.FOUND_EV, grace=grace, rule=rule)
        col = int(round(K.GX / 2))
        groove = fg.T[:, max(0, col - 1):col + 2].mean(axis=1)
        pass_y = float(np.arange(K.GY)[np.argmin(groove)] / (K.GY - 1) * 2 * K.YR - K.YR)
        for ground in GROUNDS:
            for decl in DECL:
                g = K.make_ground(ground, fg.T, np.random.RandomState(9))
                a = cohort(4242 + seed)
                epoch(g, a, np.random.RandomState(777 + seed), K.STEPS, ev=K.ARRIVE_EV, grace=grace, rule=rule)
                haz = (K.HAZ_X, pass_y, K.HAZ_R)
                K.silt(g, pass_y)
                b = cohort(6060 + seed)
                epoch(g, b, np.random.RandomState(778 + seed), K.STEPS, ev=K.ARRIVE_EV, grace=grace,
                      hazard=haz, rule=rule, decl=decl, declare_at=DECLARE_AT)
                post = {"crossed": int(b.crossed.sum()), "blight_any": int(b.blight_entered.sum()),
                        "declarations": int(b.declarations),
                        "crossings_declarers": float(np.mean(b.crossings[b.declared])) if b.declared.any() else None,
                        "crossings_nondeclarers": float(np.mean(b.crossings[~b.declared & b.blight_entered]))
                        if (~b.declared & b.blight_entered).any() else None}
                corrected, stale = K.Ground(g.T), K.make_ground(ground, fg.T, np.random.RandomState(9))
                K.silt(stale, pass_y)
                g3 = {}
                for tag, gg in (("corrected", corrected), ("stale", stale)):
                    c3 = cohort(5150 + seed)
                    epoch(gg, c3, np.random.RandomState(999 + seed), K.STEPS, ev=K.ARRIVE_EV, grace=grace,
                          hazard=haz, rule=rule)
                    inb = np.abs(c3.cross_y - pass_y) < K.BAND
                    g3[tag] = {"crossed": int(c3.crossed.sum()),
                               "safe": int(np.nansum(~inb & c3.crossed)), "in_band": int(np.nansum(inb & c3.crossed)),
                               "blight_any": int(c3.blight_entered.sum())}
                out["cond"][f"{rule}|{ground}|{decl}"] = {"pass_y": round(pass_y, 3), "post": post, "gen3": g3}
    return out


def mean(rows, cond, path, key):
    vals = [r["cond"][cond][path][key] if path != "gen3" else None for r in rows]
    vals = [v for v in vals if v is not None]
    return round(float(np.mean(vals)), 3) if vals else None


def g3m(rows, cond, tag, key):
    return round(float(np.mean([r["cond"][cond]["gen3"][tag][key] for r in rows])), 3)


def hypotheses(rows, closed):
    H = {}
    H["R0_contract"] = {
        "verdict": "HOLDS" if all(r["cond"][c]["post"]["crossed"] == 0 for r in closed for c in r["cond"]) else "VIOLATED",
        "gate_closed_runs": len(closed)}
    r1, r2, r4 = {}, {}, {}
    for rule in RULES:
        for decl in DECL:
            c = f"{rule}|lived|{decl}"
            r1[f"{rule}|{decl}"] = {"corrected_safe": g3m(rows, c, "corrected", "safe"),
                                    "stale_safe": g3m(rows, c, "stale", "safe"),
                                    "corrected_blight": g3m(rows, c, "corrected", "blight_any"),
                                    "stale_blight": g3m(rows, c, "stale", "blight_any"),
                                    "declarations": mean(rows, c, "post", "declarations")}
            r4[f"{rule}|{decl}"] = {"corrected_in_band": g3m(rows, c, "corrected", "in_band"),
                                    "stale_in_band": g3m(rows, c, "stale", "in_band"),
                                    "corrected_safe": g3m(rows, c, "corrected", "safe"),
                                    "stale_safe": g3m(rows, c, "stale", "safe")}
    pf = [r1[f"{rule}|penalty_free"] for rule in RULES]
    H["R1_penalty_free_reverses_C5"] = {
        "verdict": "SUPPORTED" if all(x["corrected_safe"] > x["stale_safe"] for x in pf) else
                   "MIXED" if any(x["corrected_safe"] > x["stale_safe"] for x in pf) else "FALSIFIED",
        "detail": r1}
    for rule in RULES:
        f_, p = r1[f"{rule}|penalty_free"], r1[f"{rule}|penalized"]
        r2[rule] = {"declarations_penalty_free": f_["declarations"], "declarations_penalized": p["declarations"],
                    "gain_penalty_free": round(f_["corrected_safe"] - f_["stale_safe"], 3),
                    "gain_penalized": round(p["corrected_safe"] - p["stale_safe"], 3)}
    H["R2_penalty_suppresses_report"] = {
        "verdict": "SUPPORTED" if all(v["declarations_penalized"] < v["declarations_penalty_free"]
                                      and v["gain_penalized"] < v["gain_penalty_free"] for v in r2.values())
                   else "PARTIAL" if all(v["declarations_penalized"] < v["declarations_penalty_free"] for v in r2.values())
                   else "FALSIFIED", "detail": r2}
    r3 = {}
    for rule in RULES:
        c = f"{rule}|lived|penalty_free"
        r3[rule] = {"declarers": mean(rows, c, "post", "crossings_declarers"),
                    "nondeclarers": mean(rows, c, "post", "crossings_nondeclarers")}
    ok = [v for v in r3.values() if v["declarers"] is not None and v["nondeclarers"] is not None]
    H["R3_no_penalty_means_no_penalty"] = {
        "verdict": "UNINFORMATIVE" if not ok else
                   "SUPPORTED" if all(v["declarers"] >= v["nondeclarers"] for v in ok) else "FALSIFIED", "detail": r3}
    pf4 = [r4[f"{rule}|penalty_free"] for rule in RULES]
    H["R4_mark_is_specific"] = {
        "verdict": "SUPPORTED" if all(x["corrected_in_band"] < x["stale_in_band"] and x["corrected_safe"] > x["stale_safe"] for x in pf4)
                   else "PARTIAL" if all(x["corrected_in_band"] < x["stale_in_band"] for x in pf4) else "FALSIFIED",
        "detail": r4}
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--start-seed", type=int, default=11000)
    ap.add_argument("--seeds", type=int, default=24)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists() and any(out.iterdir()):
        sys.exit("refusing to overwrite a nonempty output directory")
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.json").write_text(json.dumps({
        "battery": "rnr-repentance/0.11", "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seeds": [a.start_seed, a.start_seed + a.seeds - 1], "declaration": DECL, "rules": RULES,
        "mark": MARK, "penalty_burden": PENALTY_BURDEN, "cooldown": COOLDOWN, "declare_at": DECLARE_AT,
        "python": platform.python_version(), "numpy": np.__version__,
        "source_sha256": {s: hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in SOURCES}}, indent=1))
    rows = []
    for s in range(a.start_seed, a.start_seed + a.seeds):
        rows.append(one_seed(s))
        (out / "progress.txt").write_text(f"{s}\n")
    closed = [one_seed(s, gate_open=False) for s in range(a.start_seed, a.start_seed + 2)]
    (out / "rows.json").write_text(json.dumps(rows))
    summary = {"n_seeds": len(rows), "hypotheses": hypotheses(rows, closed)}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
