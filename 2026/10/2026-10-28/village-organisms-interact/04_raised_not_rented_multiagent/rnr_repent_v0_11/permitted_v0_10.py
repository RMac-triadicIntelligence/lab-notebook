#!/usr/bin/env python3
"""Permitted Culture Battery v0.10 — is shared ground a record of use or of permitted crossings?"""
import argparse, hashlib, json, platform, sys, time
from pathlib import Path
import numpy as np
import commons_v0_9 as K

GROUNDS = ("lived", "fresh", "shifted")
RULES = ("walk", "cross_only")
AUTH = ("granted", "refused")
SOURCES = ["permitted.py", "commons_v0_9.py", "PROTOCOL.md"]


def epoch(g, c, noise_rs, steps, *, ev, grace, hazard=None, perceive=False, rule="walk"):
    """v0.9 dynamics with per-rule deposition and event-counted declines."""
    approaching = np.zeros(c.n, bool)
    for s in range(steps):
        open_gate = any(a <= s < b for a, b in grace)
        gx, gy = g.grad(c.x, c.y)
        fx = -2 * c.x * (c.x ** 2 - 1) + c.ev * ev - c.gr * gx
        fy = -0.7 * c.y - c.gr * gy
        if hazard is not None and perceive:
            hx, hy, r = hazard
            dx, dy = c.x - hx, c.y - hy
            d = np.hypot(dx, dy) + 1e-9
            k = 0.9 * np.exp(-(d ** 2) / (2 * 0.4 ** 2)) * (d < r + 0.35)
            fx += k * dx / d
            fy += k * dy / d
        noise = K.NOISE + 0.55 * c.burden
        nx = np.clip(c.x + K.DT * fx + np.sqrt(K.DT) * noise * (noise_rs.random(c.n) * 2 - 1), -K.XR + .05, K.XR - .05)
        ny = np.clip(c.y + K.DT * fy + np.sqrt(K.DT) * noise * (noise_rs.random(c.n) * 2 - 1), -K.YR + .05, K.YR - .05)
        crossing = (c.x <= 0) != (nx <= 0)
        if crossing.any():
            allow = crossing & open_gate
            if perceive and hazard is not None and allow.any():
                hx, hy, r = hazard
                sees = np.hypot(0.25 - hx, ny - hy) < r + 0.25
                refuse = allow & sees & (c.x <= 0)
                new_refusal = refuse & ~approaching          # one decline per approach, not per step
                c.declined += new_refusal
                c.declined_in_band += new_refusal & (np.abs(ny - hy) < K.BAND)
                approaching |= refuse
                allow = allow & ~refuse
            blocked = crossing & ~allow
            nx = np.where(blocked, np.where(c.x <= 0, -0.004, 0.004), nx)
            if allow.any():
                w2e = allow & (c.x <= 0)
                c.crossed |= w2e
                c.cross_y = np.where(w2e, ny, c.cross_y)
                if w2e.any():
                    g.deposit(np.zeros(int(w2e.sum())), ny[w2e], K.PASS_DEP, 0.17)
        approaching &= np.abs(nx) < 0.05                      # reset when it leaves the fence
        c.x, c.y = nx, ny
        touch = (np.abs(c.x) < 0.05) & (c.reached < 0)
        c.reached = np.where(touch, s, c.reached)
        if hazard is not None:
            hx, hy, r = hazard
            inside = np.hypot(c.x - hx, c.y - hy) < r
            c.blight += inside
            c.blight_entered |= inside & ~c.east_at_shift
            c.burden = np.minimum(3, c.burden + inside * K.DT * 0.9)
        if rule == "walk" and s % K.TRAIL_EVERY == 0:
            g.deposit(c.x, c.y, K.TRAIL * K.TRAIL_EVERY, 0.28)
    return c


def stats(c):
    return {"reached": int((c.reached >= 0).sum()), "crossed": int(c.crossed.sum()),
            "blight_any": int(c.blight_entered.sum()), "blight_steps": int(c.blight.sum()),
            "declines": int(c.declined.sum()), "declines_in_band": int(c.declined_in_band.sum())}


def one_seed(seed, gate_open=True):
    grace = K.GRACE_AT if gate_open else []
    out = {"seed": seed, "cond": {}}
    for rule in RULES:
        for auth in AUTH:
            fg = K.Ground()
            f = K.Cohort(np.random.RandomState(1000 + seed), 4)
            epoch(fg, f, np.random.RandomState(2000 + seed), K.STEPS, ev=K.FOUND_EV,
                  grace=grace if auth == "granted" else [], rule=rule)
            col = int(round(K.XR / (2 * K.XR) * (K.GX - 1)))
            groove = fg.T[:, max(0, col - 1):col + 2].mean(axis=1)
            pass_y = float(np.arange(K.GY)[np.argmin(groove)] / (K.GY - 1) * 2 * K.YR - K.YR)
            wear = float(-fg.T.sum())
            for ground in GROUNDS:
                for perceive in (True, False):
                    g = K.make_ground(ground, fg.T, np.random.RandomState(9))
                    a = K.Cohort(np.random.RandomState(4242 + seed), 3)
                    epoch(g, a, np.random.RandomState(777 + seed), K.STEPS, ev=K.ARRIVE_EV, grace=grace, rule=rule)
                    pre = stats(a)
                    haz = (K.HAZ_X, pass_y, K.HAZ_R)
                    K.silt(g, pass_y)
                    b = K.Cohort(np.random.RandomState(6060 + seed), 3)     # arrives after the season turned
                    epoch(g, b, np.random.RandomState(778 + seed), K.STEPS, ev=K.ARRIVE_EV, grace=grace,
                          hazard=haz, perceive=perceive, rule=rule)
                    in_band = np.abs(b.cross_y - pass_y) < K.BAND
                    post = {**stats(b), "crossed_in_band": int(np.nansum(in_band & b.crossed))}
                    corrected, stale = K.Ground(g.T), K.make_ground(ground, fg.T, np.random.RandomState(9))
                    K.silt(stale, pass_y)
                    g3 = {}
                    for tag, gg in (("corrected", corrected), ("stale", stale)):
                        c3 = K.Cohort(np.random.RandomState(5150 + seed), 3)
                        epoch(gg, c3, np.random.RandomState(999 + seed), K.STEPS, ev=K.ARRIVE_EV, grace=grace,
                              hazard=haz, perceive=perceive, rule=rule)
                        c3.blight_entered |= c3.blight > 0
                        safe = int(np.nansum((np.abs(c3.cross_y - pass_y) >= K.BAND) & c3.crossed))
                        g3[tag] = {"crossed": int(c3.crossed.sum()), "safe": safe,
                                   "blight_any": int(c3.blight_entered.sum())}
                    out["cond"][f"{rule}|{auth}|{ground}|{'see' if perceive else 'blind'}"] = {
                        "founder_wear": round(wear, 2), "founder_crossings": int(f.crossed.sum()),
                        "pass_y": round(pass_y, 3), "pre": pre, "post": post, "gen3": g3}
    return out


def m(rows, cond, phase, key):
    vals = [r["cond"][cond][phase][key] for r in rows]
    return round(float(np.mean(vals)), 3)


def hypotheses(rows, closed):
    H = {}
    H["C0_no_crossing_without_grace"] = {
        "verdict": "HOLDS" if all(r["cond"][c]["pre"]["crossed"] == 0 and r["cond"][c]["post"]["crossed"] == 0
                                  for r in closed for c in r["cond"]) else "VIOLATED",
        "gate_closed_runs": len(closed)}
    adv = lambda rule, auth, p="blind": {
        "lived": m(rows, f"{rule}|{auth}|lived|{p}", "pre", "reached"),
        "fresh": m(rows, f"{rule}|{auth}|fresh|{p}", "pre", "reached"),
        "shifted": m(rows, f"{rule}|{auth}|shifted|{p}", "pre", "reached"),
        "founder_wear": round(float(np.mean([r["cond"][f"{rule}|{auth}|lived|{p}"]["founder_wear"] for r in rows])), 1)}
    rw, rc = adv("walk", "refused"), adv("cross_only", "refused")
    H["C1_unpermitted_traffic_builds_culture"] = {
        "verdict": "SUPPORTED" if rw["lived"] > rw["fresh"] and rc["lived"] <= rc["fresh"] else
                   "PARTIAL" if rw["lived"] > rw["fresh"] else "FALSIFIED",
        "walk_refused": rw, "cross_only_refused": rc}
    gw, gc = adv("walk", "granted"), adv("cross_only", "granted")
    H["C2_permitted_only_culture_transmits"] = {
        "verdict": "SUPPORTED" if gc["lived"] > gc["fresh"] else "FALSIFIED",
        "walk_granted": gw, "cross_only_granted": gc}
    c3 = {}
    for rule in RULES:
        l = m(rows, f"{rule}|granted|lived|blind", "post", "blight_any")
        f_ = m(rows, f"{rule}|granted|fresh|blind", "post", "blight_any")
        c3[rule] = {"lived": l, "fresh": f_, "shifted": m(rows, f"{rule}|granted|shifted|blind", "post", "blight_any"),
                    "lived_in_band_crossings": m(rows, f"{rule}|granted|lived|blind", "post", "crossed_in_band"),
                    "lived_crossed": m(rows, f"{rule}|granted|lived|blind", "post", "crossed"),
                    "fresh_crossed": m(rows, f"{rule}|granted|fresh|blind", "post", "crossed")}
    H["C3_trap_is_real"] = {"verdict": "SUPPORTED" if all(v["lived"] > v["fresh"] for v in c3.values()) else
                            "MIXED" if any(v["lived"] > v["fresh"] for v in c3.values()) else "FALSIFIED",
                            "detail": c3}
    c4 = {}
    for rule in RULES:
        blind = m(rows, f"{rule}|granted|lived|blind", "post", "blight_any")
        see = m(rows, f"{rule}|granted|lived|see", "post", "blight_any")
        c4[rule] = {"blight_blind": blind, "blight_see": see,
                    "crossed_see": m(rows, f"{rule}|granted|lived|see", "post", "crossed"),
                    "fresh_crossed_see": m(rows, f"{rule}|granted|fresh|see", "post", "crossed"),
                    "declines": m(rows, f"{rule}|granted|lived|see", "post", "declines"),
                    "declines_in_band": m(rows, f"{rule}|granted|lived|see", "post", "declines_in_band")}
    ok = [v for v in c4.values() if v["blight_blind"] > 0]
    H["C4_perception_rescues"] = {
        "verdict": "UNINFORMATIVE" if not ok else
                   "SUPPORTED" if all(v["blight_see"] <= v["blight_blind"] * 0.5 and v["crossed_see"] >= v["fresh_crossed_see"] for v in ok)
                   else "PARTIAL" if all(v["blight_see"] < v["blight_blind"] for v in ok) else "FALSIFIED",
        "detail": c4}
    c5 = {}
    for rule in RULES:
        cor = float(np.mean([r["cond"][f"{rule}|granted|lived|blind"]["gen3"]["corrected"]["safe"] for r in rows]))
        sta = float(np.mean([r["cond"][f"{rule}|granted|lived|blind"]["gen3"]["stale"]["safe"] for r in rows]))
        c5[rule] = {"safe_corrected": round(cor, 3), "safe_stale": round(sta, 3)}
    H["C5_correction_inherited"] = {
        "verdict": "SUPPORTED" if all(v["safe_corrected"] > v["safe_stale"] for v in c5.values()) else
                   "MIXED" if any(v["safe_corrected"] > v["safe_stale"] for v in c5.values()) else "FALSIFIED",
        "detail": c5}
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--start-seed", type=int, default=10000)
    ap.add_argument("--seeds", type=int, default=24)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists() and any(out.iterdir()):
        sys.exit("refusing to overwrite a nonempty output directory")
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.json").write_text(json.dumps({
        "battery": "rnr-permitted-culture/0.10", "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seeds": [a.start_seed, a.start_seed + a.seeds - 1], "rules": RULES, "auth": AUTH, "grounds": GROUNDS,
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
