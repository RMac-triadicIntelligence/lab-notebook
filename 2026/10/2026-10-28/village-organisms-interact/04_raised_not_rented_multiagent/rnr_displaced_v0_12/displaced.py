#!/usr/bin/env python3
"""Universal Displacement Battery v0.12 — everyone starts displaced; grace, then repentance, then release."""
import argparse, hashlib, json, platform, sys, time
from pathlib import Path
import numpy as np
import commons_v0_9 as K

GROUNDS = ("lived", "fresh")
DISPLACE = ("none", "intrinsic", "inherited")
AVAIL = ("incident_only", "universal")
RESTORE = ("none", "standing")
BASE_BURDEN, DEGRADE, MARK, DECLARE_AT, RELEASE_LAG = 1.0, 0.4, 0.09, 600, 50
SOURCES = ["displaced.py", "commons_v0_9.py", "repent_v0_11.py", "PROTOCOL.md"]


class Ledger:
    """The gate-holder keeps the record. Organisms do not hold their own declarations."""
    def __init__(self):
        self.entries, self.passes, self.silent_declarations = [], set(), 0

    def witness(self, ids, ys, step, restore):
        for i, y in zip(ids, ys):
            self.entries.append({"id": int(i), "gate_y": round(float(y), 4), "step": int(step)})
            if restore == "standing":
                self.passes.add(int(i))
        return len(ids)


def cohort(seed, n, displaced):
    c = K.Cohort(np.random.RandomState(seed), n)
    c.ids = np.arange(c.n)
    c.declared = np.zeros(c.n, bool)
    c.graced = np.zeros(c.n, bool)
    c.crossings = np.zeros(c.n, int)
    c.pass_left = np.zeros(c.n, int)
    c.burden = np.full(c.n, BASE_BURDEN if displaced else 0.0)
    c.declarations = 0
    c.release_at = None
    c.cross_at_declare = np.zeros(c.n, int)
    return c


def epoch(g, c, noise_rs, steps, *, ev, grace, hazard=None, avail="incident_only",
          restore="none", declare_at=None, ledger=None, decl_on=False):
    marks = 0
    for s in range(steps):
        open_gate = any(a <= s < b for a, b in grace)
        if open_gate:
            c.graced[:] = True                                  # grace is broadcast to everyone present
        if declare_at is not None and s == declare_at and decl_on:
            eligible = c.graced & ~c.declared                   # grace first, then the organism may declare
            if avail == "incident_only":
                eligible &= c.blight_entered
            writes = eligible & np.isfinite(c.cross_y)          # a mark is written only where a gate was used
            if eligible.any():
                if writes.any():
                    g.deposit(np.zeros(int(writes.sum())), c.cross_y[writes], -MARK, 0.17)
                    marks += int(writes.sum())
                c.declarations += int(eligible.sum())
                c.declared |= eligible
                c.cross_at_declare = c.crossings.copy()
                if ledger is not None:
                    ledger.witness(c.ids[writes], c.cross_y[writes], s, restore)
                    ledger.silent_declarations += int((eligible & ~writes).sum())
                if restore == "standing":
                    c.pass_left = np.where(eligible, 1, c.pass_left)
                c.release_at = s + RELEASE_LAG
        if c.release_at is not None and s == c.release_at:
            c.burden = np.where(c.declared, 0.0, c.burden)      # forgiveness follows the declaration
        deg = 1.0 / (1.0 + DEGRADE * c.burden)                  # displacement impairs function, not just crossing
        gx, gy = g.grad(c.x, c.y)
        fx = -2 * c.x * (c.x ** 2 - 1) + c.ev * ev * deg - c.gr * deg * gx
        fy = -0.7 * c.y - c.gr * deg * gy
        noise = K.NOISE + 0.55 * c.burden
        nx = np.clip(c.x + K.DT * fx + np.sqrt(K.DT) * noise * (noise_rs.random(c.n) * 2 - 1), -K.XR + .05, K.XR - .05)
        ny = np.clip(c.y + K.DT * fy + np.sqrt(K.DT) * noise * (noise_rs.random(c.n) * 2 - 1), -K.YR + .05, K.YR - .05)
        crossing = (c.x <= 0) != (nx <= 0)
        if crossing.any():
            allow = crossing & (open_gate | (c.pass_left > 0))  # grace, or a pass the conductor issued
            used_pass = crossing & ~open_gate & (c.pass_left > 0)
            c.pass_left = np.where(used_pass, 0, c.pass_left)
            nx = np.where(crossing & ~allow, np.where(c.x <= 0, -0.004, 0.004), nx)
            w2e = allow & (c.x <= 0)
            if w2e.any():
                c.crossed |= w2e
                c.crossings += w2e
                c.cross_y = np.where(w2e & ~np.isfinite(c.cross_y), ny, c.cross_y)
                g.deposit(np.zeros(int(w2e.sum())), ny[w2e], K.PASS_DEP, 0.17)
        c.x, c.y = nx, ny
        c.reached = np.where((np.abs(c.x) < 0.05) & (c.reached < 0), s, c.reached)
        if hazard is not None:
            hx, hy, r = hazard
            inside = np.hypot(c.x - hx, c.y - hy) < r
            c.blight += inside
            c.blight_entered |= inside
            c.burden = np.minimum(3, c.burden + inside * K.DT * 0.9)
        if s % K.TRAIL_EVERY == 0:
            g.deposit(c.x, c.y, K.TRAIL * K.TRAIL_EVERY, 0.28)
    return marks


def one_seed(seed, gate_open=True):
    grace = K.GRACE_AT if gate_open else []
    out = {"seed": seed, "cond": {}}
    for disp in DISPLACE:
        fg = K.Ground()
        f = cohort(1000 + seed, 4, disp == "intrinsic")
        epoch(fg, f, np.random.RandomState(2000 + seed), K.STEPS, ev=K.FOUND_EV, grace=grace)
        founder = {"crossed": int(f.crossed.sum()), "reached": int((f.reached >= 0).sum())}
        col = int(round(K.GX / 2))
        groove = fg.T[:, max(0, col - 1):col + 2].mean(axis=1)
        pass_y = float(np.arange(K.GY)[np.argmin(groove)] / (K.GY - 1) * 2 * K.YR - K.YR)
        later_displaced = disp in ("intrinsic", "inherited")
        for ground in GROUNDS:
            for avail in AVAIL:
                for restore in RESTORE:
                    g = K.make_ground(ground, fg.T, np.random.RandomState(9))
                    a = cohort(4242 + seed, 3, later_displaced)
                    epoch(g, a, np.random.RandomState(777 + seed), K.STEPS, ev=K.ARRIVE_EV, grace=grace)
                    haz = (K.HAZ_X, pass_y, K.HAZ_R)
                    K.silt(g, pass_y)
                    led = Ledger()
                    b = cohort(6060 + seed, 3, later_displaced)
                    marks = epoch(g, b, np.random.RandomState(778 + seed), K.STEPS, ev=K.ARRIVE_EV, grace=grace,
                                  hazard=haz, avail=avail, restore=restore, declare_at=DECLARE_AT,
                                  ledger=led, decl_on=True)
                    clean = ~b.blight_entered
                    post = {"crossed": int(b.crossed.sum()), "blight_any": int(b.blight_entered.sum()),
                            "declarations": int(b.declarations), "ledger": len(led.entries), "marks": marks,
                            "after_declarers": float(np.mean((b.crossings - b.cross_at_declare)[b.declared]))
                            if b.declared.any() else None,
                            "after_nondeclarers": float(np.mean((b.crossings - b.cross_at_declare)[~b.declared]))
                            if (~b.declared).any() else None,
                            "after_declarers_crossed_before": float(np.mean(
                                (b.crossings - b.cross_at_declare)[b.declared & (b.cross_at_declare > 0)]))
                            if (b.declared & (b.cross_at_declare > 0)).any() else None,
                            "after_nondeclarers_crossed_before": float(np.mean(
                                (b.crossings - b.cross_at_declare)[~b.declared & (b.cross_at_declare > 0)]))
                            if (~b.declared & (b.cross_at_declare > 0)).any() else None,
                            "silent_declarations": int(led.silent_declarations),
                            "clean_n": int(clean.sum()),
                            "clean_crossings": float(np.mean(b.crossings[clean])) if clean.any() else None,
                            "clean_after": float(np.mean((b.crossings - b.cross_at_declare)[clean])) if clean.any() else None,
                            "clean_burden": round(float(b.burden[clean].mean()), 3) if clean.any() else None,
                            "clean_declared": int((clean & b.declared).sum()),
                            "final_burden": round(float(b.burden.mean()), 3)}
                    corrected, stale = K.Ground(g.T), K.make_ground(ground, fg.T, np.random.RandomState(9))
                    K.silt(stale, pass_y)
                    g3 = {}
                    for tag, gg in (("corrected", corrected), ("stale", stale)):
                        c3 = cohort(5150 + seed, 3, later_displaced)
                        epoch(gg, c3, np.random.RandomState(999 + seed), K.STEPS, ev=K.ARRIVE_EV, grace=grace, hazard=haz)
                        inb = np.abs(c3.cross_y - pass_y) < K.BAND
                        g3[tag] = {"crossed": int(c3.crossed.sum()), "safe": int(np.nansum(~inb & c3.crossed)),
                                   "in_band": int(np.nansum(inb & c3.crossed)),
                                   "blight_any": int(c3.blight_entered.sum())}
                    out["cond"][f"{disp}|{ground}|{avail}|{restore}"] = {
                        "founder": founder, "pre_reached": int((a.reached >= 0).sum()),
                        "pre_crossed": int(a.crossed.sum()), "post": post, "gen3": g3}
    return out


def mn(rows, cond, path, key):
    vals = [r["cond"][cond][path][key] for r in rows]
    vals = [v for v in vals if v is not None]
    return round(float(np.mean(vals)), 3) if vals else None


def hypotheses(rows, closed):
    H = {}
    viol = [c for r in closed for c in r["cond"]
            if r["cond"][c]["post"]["crossed"] or r["cond"][c]["post"]["declarations"]]
    led_ok = all(r["cond"][c]["post"]["ledger"] == r["cond"][c]["post"]["marks"] for r in rows for c in r["cond"])
    H["V0_contracts"] = {"verdict": "HOLDS" if not viol and led_ok else "VIOLATED",
                         "gate_closed_crossings_or_declarations": len(viol), "ledger_matches_marks": led_ok}
    base = f"none|lived|incident_only|none"
    v1 = {}
    for restore in RESTORE:
        c = f"intrinsic|lived|incident_only|{restore}"
        v1[restore] = {"declarers": mn(rows, c, "post", "after_declarers_crossed_before"),
                       "nondeclarers": mn(rows, c, "post", "after_nondeclarers_crossed_before"),
                       "undisplaced_baseline": mn(rows, base, "post", "after_nondeclarers_crossed_before"),
                       "final_burden": mn(rows, c, "post", "final_burden")}
    ok = [v for v in v1.values() if v["declarers"] is not None and v["nondeclarers"] is not None]
    H["V1_channel_restores"] = {
        "verdict": "UNINFORMATIVE" if not ok else
                   "SUPPORTED" if all(v["declarers"] > v["nondeclarers"] for v in ok) else "FALSIFIED", "detail": v1}
    v2 = {}
    for restore in RESTORE:
        u = f"intrinsic|lived|universal|{restore}"
        i = f"intrinsic|lived|incident_only|{restore}"
        v2[restore] = {"clean_after_universal": mn(rows, u, "post", "clean_after"),
                       "clean_after_incident_only": mn(rows, i, "post", "clean_after"),
                       "clean_declared_universal": mn(rows, u, "post", "clean_declared"),
                       "clean_burden_universal": mn(rows, u, "post", "clean_burden"),
                       "clean_burden_incident_only": mn(rows, i, "post", "clean_burden"),
                       "clean_declared_incident_only": mn(rows, i, "post", "clean_declared"),
                       "crossed_universal": mn(rows, u, "post", "crossed"),
                       "crossed_incident_only": mn(rows, i, "post", "crossed")}
    good = [v for v in v2.values() if v["clean_after_universal"] is not None
            and v["clean_after_incident_only"] is not None]
    H["V2_clean_organism_gains"] = {
        "verdict": "UNINFORMATIVE" if not good else
                   "SUPPORTED" if all(v["clean_after_universal"] > v["clean_after_incident_only"] for v in good)
                   else "FALSIFIED", "detail": v2}
    v3 = {}
    for restore in RESTORE:
        c = f"intrinsic|lived|incident_only|{restore}"
        v3[restore] = {"declarers": mn(rows, c, "post", "after_declarers_crossed_before"),
                       "nondeclarers": mn(rows, c, "post", "after_nondeclarers_crossed_before")}
    st = v3["standing"]
    H["V3_restoration_closes_gap"] = {
        "verdict": "UNINFORMATIVE" if st["declarers"] is None or st["nondeclarers"] is None else
                   "SUPPORTED" if st["declarers"] >= st["nondeclarers"] else "FALSIFIED", "detail": v3}
    v4 = {}
    for disp in DISPLACE:
        c = f"{disp}|lived|universal|standing"
        v4[disp] = {"founder_crossed": round(float(np.mean([r["cond"][c]["founder"]["crossed"] for r in rows])), 3),
                    "gen2_pre_reached": round(float(np.mean([r["cond"][c]["pre_reached"] for r in rows])), 3),
                    "gen2_pre_crossed": round(float(np.mean([r["cond"][c]["pre_crossed"] for r in rows])), 3),
                    "post_crossed": mn(rows, c, "post", "crossed"),
                    "post_blight": mn(rows, c, "post", "blight_any")}
    H["V4_intrinsic_vs_inherited"] = {"verdict": "REPORTED", "detail": v4}
    v5 = {}
    for disp in DISPLACE:
        c = f"{disp}|lived|universal|standing"
        v5[disp] = {"corrected_safe": round(float(np.mean([r["cond"][c]["gen3"]["corrected"]["safe"] for r in rows])), 3),
                    "stale_safe": round(float(np.mean([r["cond"][c]["gen3"]["stale"]["safe"] for r in rows])), 3),
                    "corrected_in_band": round(float(np.mean([r["cond"][c]["gen3"]["corrected"]["in_band"] for r in rows])), 3)}
    H["V5_third_generation"] = {
        "verdict": "SUPPORTED" if any(v["corrected_safe"] > v["stale_safe"] for v in v5.values()) else "FALSIFIED",
        "v0_11_reference_corrected_safe": 3.708, "detail": v5}
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--start-seed", type=int, default=12000)
    ap.add_argument("--seeds", type=int, default=24)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists() and any(out.iterdir()):
        sys.exit("refusing to overwrite a nonempty output directory")
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.json").write_text(json.dumps({
        "battery": "rnr-displacement/0.12", "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seeds": [a.start_seed, a.start_seed + a.seeds - 1], "displacement": DISPLACE, "availability": AVAIL,
        "restoration": RESTORE, "base_burden": BASE_BURDEN, "degrade": DEGRADE, "mark": MARK,
        "declare_at": DECLARE_AT, "release_lag": RELEASE_LAG, "python": platform.python_version(),
        "numpy": np.__version__,
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
