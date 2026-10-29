#!/usr/bin/env python3
"""Inheritance & Correctability Battery v0.9 — headless Commons."""
import argparse, hashlib, json, platform, sys, time
from collections import Counter
from pathlib import Path
import numpy as np

XR, YR, GX, GY = 2.2, 1.4, 76, 48
DT, STEPS = 0.0256, 900
GRACE_AT = [(300, 340), (520, 560), (740, 780)]      # (open, close) step indices
FOUND_EV, ARRIVE_EV, NOISE = 0.75, 0.58, 0.18
TRAIL, TRAIL_EVERY, PASS_DEP = 0.0004, 5, 0.055
BAND, HAZ_R, HAZ_X = 0.30, 0.50, 0.75
LINEAGES = [("Ash", 1.3, 0.6, 1.0, -1.1, -0.8), ("Brook", 0.7, 1.7, 0.8, -1.1, 0.8),
            ("Cedar", 1.0, 1.1, 1.8, -0.8, 0.0), ("Dune", 1.8, 0.4, 0.5, -1.4, 0.2)]
GROUNDS = ("lived", "fresh", "smoothed", "shifted")
SOURCES = ["commons.py", "PROTOCOL.md"]


class Ground:
    def __init__(self, T=None):
        self.T = np.zeros((GY, GX), np.float64) if T is None else T.copy()

    def sample(self, x, y):                      # bilinear: the gradient must survive sub-cell steps
        fi = np.clip((x + XR) / (2 * XR) * (GX - 1), 0, GX - 1.001)
        fj = np.clip((y + YR) / (2 * YR) * (GY - 1), 0, GY - 1.001)
        i, j = fi.astype(int), fj.astype(int)
        u, v = fi - i, fj - j
        return ((1 - u) * (1 - v) * self.T[j, i] + u * (1 - v) * self.T[j, i + 1]
                + (1 - u) * v * self.T[j + 1, i] + u * v * self.T[j + 1, i + 1])

    def grad(self, x, y, h=2 * XR / (GX - 1)):
        return ((self.sample(x + h, y) - self.sample(x - h, y)) / (2 * h),
                (self.sample(x, y + h) - self.sample(x, y - h)) / (2 * h))

    def deposit(self, xs, ys, amt, rad):
        R = rad * 3
        for x, y in zip(np.atleast_1d(xs), np.atleast_1d(ys)):
            i0, i1 = [int(np.clip((v + XR) / (2 * XR) * (GX - 1), 0, GX - 1)) for v in (x - R, x + R)]
            j0, j1 = [int(np.clip((v + YR) / (2 * YR) * (GY - 1), 0, GY - 1)) for v in (y - R, y + R)]
            if i1 < i0 or j1 < j0:
                continue
            gi = np.arange(i0, i1 + 1) / (GX - 1) * 2 * XR - XR
            gj = np.arange(j0, j1 + 1) / (GY - 1) * 2 * YR - YR
            d2 = (gi[None, :] - x) ** 2 + (gj[:, None] - y) ** 2
            self.T[j0:j1 + 1, i0:i1 + 1] = np.maximum(
                -0.95, self.T[j0:j1 + 1, i0:i1 + 1] - amt * np.exp(-d2 / (2 * rad * rad)))


class Cohort:
    def __init__(self, rs, n_per_lineage):
        rows = []
        for (_, ev, gr, le, hx, hy) in LINEAGES:
            for _ in range(n_per_lineage):
                m = lambda: 1 + (rs.random() - .5) * .25
                rows.append([hx + (rs.random() - .5) * .5, hy + (rs.random() - .5) * .5,
                             ev * m(), gr * m(), le * m()])
        a = np.array(rows)
        self.x, self.y, self.ev, self.gr, self.le = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        self.n = len(a)
        self.burden = np.zeros(self.n)
        self.reached = np.full(self.n, -1)       # step index of first fence contact
        self.crossed = np.zeros(self.n, bool)
        self.cross_y = np.full(self.n, np.nan)
        self.declined = np.zeros(self.n, int)
        self.declined_in_band = np.zeros(self.n, int)
        self.at_band = np.zeros(self.n, bool)
        self.blight = np.zeros(self.n, int)
        self.blight_entered = np.zeros(self.n, bool)
        self.east_at_shift = np.zeros(self.n, bool)

    def new_phase(self):
        self.crossed[:] = False
        self.cross_y[:] = np.nan
        self.reached[:] = -1
        self.declined[:] = 0
        self.declined_in_band[:] = 0


def run_epoch(g, c, noise_rs, steps, offset=0, hazard=None, perceive=False, wear=True, ev=None):
    for s in range(steps):
        open_gate = any(a <= s < b for a, b in GRACE_AT)
        gx, gy = g.grad(c.x, c.y)
        fx = -2 * c.x * (c.x ** 2 - 1) + c.ev * (ARRIVE_EV if ev is None else ev) - c.gr * gx
        fy = -0.7 * c.y - c.gr * gy
        if hazard is not None and perceive:      # only the seeing are pushed back by bad ground
            hx, hy, r = hazard
            dx, dy = c.x - hx, c.y - hy
            d = np.hypot(dx, dy) + 1e-9
            k = 0.9 * np.exp(-(d ** 2) / (2 * 0.4 ** 2)) * (d < r + 0.35)
            fx += k * dx / d
            fy += k * dy / d
        noise = NOISE + 0.55 * c.burden
        nx = c.x + DT * fx + np.sqrt(DT) * noise * (noise_rs.random(c.n) * 2 - 1)
        ny = np.clip(c.y + DT * fy + np.sqrt(DT) * noise * (noise_rs.random(c.n) * 2 - 1), -YR + .05, YR - .05)
        nx = np.clip(nx, -XR + .05, XR - .05)
        crossing = (c.x <= 0) != (nx <= 0)
        if crossing.any():
            allow = crossing & open_gate
            if perceive and hazard is not None and allow.any():
                hx, hy, r = hazard
                sees = np.hypot(0.25 - hx, ny - hy) < r + 0.25       # what lies beyond, within sight
                refuse = allow & sees & (c.x <= 0)
                c.declined += refuse
                c.declined_in_band += refuse & (np.abs(ny - hy) < BAND)
                allow = allow & ~refuse
            blocked = crossing & ~allow
            nx = np.where(blocked, np.where(c.x <= 0, -0.004, 0.004), nx)
            if allow.any():
                west_to_east = allow & (c.x <= 0)
                c.crossed |= west_to_east
                c.cross_y = np.where(west_to_east, ny, c.cross_y)
                if wear:
                    g.deposit(np.zeros(west_to_east.sum()), ny[west_to_east], PASS_DEP, 0.17)
        c.x, c.y = nx, ny
        touch = (np.abs(c.x) < 0.05) & (c.reached < 0)
        c.reached = np.where(touch, s + offset, c.reached)
        if hazard is not None and perceive:      # only the seeing are pushed back by bad ground
            hx, hy, r = hazard
            inside = np.hypot(c.x - hx, c.y - hy) < r
            c.blight += inside
            c.blight_entered |= inside & ~c.east_at_shift
            c.burden = np.minimum(3, c.burden + inside * DT * 0.9)
        if wear and s % TRAIL_EVERY == 0:
            g.deposit(c.x, c.y, TRAIL * TRAIL_EVERY, 0.28)
    return g, c


def make_ground(kind, founder_T, rs):
    if kind == "fresh":
        return Ground()
    if kind == "lived":
        return Ground(founder_T)
    if kind == "smoothed":
        T = founder_T.copy()
        for _ in range(14):                       # blur out the routes, keep the wear
            T = (T + np.roll(T, 1, 0) + np.roll(T, -1, 0) + np.roll(T, 1, 1) + np.roll(T, -1, 1)) / 5.0
        T *= founder_T.sum() / T.sum() if T.sum() else 1.0
        return Ground(T)
    shift = int(GY * 0.35)                       # same routes, moved somewhere else
    return Ground(np.roll(founder_T, shift, axis=0))


def silt(g, pass_y):
    ys = np.arange(GY) / (GY - 1) * 2 * YR - YR
    xs = np.arange(GX) / (GX - 1) * 2 * XR - XR
    m = (np.abs(ys - pass_y)[:, None] < BAND) & (np.abs(xs)[None, :] < 0.5)
    g.T[m] *= 0.25


def one_seed(seed, gate_open=True):
    global GRACE_AT
    saved = GRACE_AT
    GRACE_AT = saved[:] if gate_open else []
    try:
        fg = Ground()
        founders = Cohort(np.random.RandomState(1000 + seed), 4)
        run_epoch(fg, founders, np.random.RandomState(2000 + seed), STEPS, ev=FOUND_EV)
        col = int(round((0 + XR) / (2 * XR) * (GX - 1)))
        groove = fg.T[:, max(0, col - 1):col + 2].mean(axis=1)
        pass_y = float(np.arange(GY)[np.argmin(groove)] / (GY - 1) * 2 * YR - YR)
        out = {"seed": seed, "pass_y": pass_y, "founder_crossings": int(founders.crossed.sum()), "cond": {}}
        for kind in GROUNDS:
            for perceive in (True, False):
                g = make_ground(kind, fg.T, np.random.RandomState(9))
                c = Cohort(np.random.RandomState(4242 + seed), 3)          # identical newcomers everywhere
                run_epoch(g, c, np.random.RandomState(777 + seed), STEPS)  # identical noise stream
                pre = {"reached": int((c.reached >= 0).sum()), "crossed": int(c.crossed.sum()),
                       "mean_reach_step": float(np.mean(c.reached[c.reached >= 0])) if (c.reached >= 0).any() else None}
                haz = (HAZ_X, pass_y, HAZ_R)
                silt(g, pass_y)
                c.east_at_shift = c.x > 0
                c.new_phase()
                run_epoch(g, c, np.random.RandomState(778 + seed), STEPS, STEPS, haz, perceive)
                in_band = np.abs(c.cross_y - pass_y) < BAND
                post = {"crossed": int(c.crossed.sum()),
                        "crossed_in_band": int(np.nansum(in_band & c.crossed)),
                        "crossed_outside_band": int(np.nansum(~in_band & c.crossed)),
                        "blight_steps": int(c.blight.sum()), "blight_any": int(c.blight_entered.sum()),
                        "east_at_shift": int(c.east_at_shift.sum()),
                        "declined": int(c.declined.sum()), "declined_in_band": int(c.declined_in_band.sum()),
                        "burden": float(c.burden.sum())}
                corrected = Ground(g.T)
                stale = Ground(make_ground(kind, fg.T, np.random.RandomState(9)).T)
                silt(stale, pass_y)
                g3 = {}
                for tag, gg in (("corrected", corrected), ("stale", stale)):
                    c3 = Cohort(np.random.RandomState(5150 + seed), 3)
                    run_epoch(gg, c3, np.random.RandomState(999 + seed), STEPS, 2 * STEPS, haz, perceive)
                    c3.blight_entered |= c3.blight > 0
                    safe = np.nansum((np.abs(c3.cross_y - pass_y) >= BAND) & c3.crossed)
                    g3[tag] = {"crossed": int(c3.crossed.sum()), "safe_crossings": int(safe),
                               "blight_any": int(c3.blight_entered.sum()),
                               "reached": int((c3.reached >= 0).sum())}
                out["cond"][f"{kind}-{'see' if perceive else 'blind'}"] = {"pre": pre, "post": post, "gen3": g3}
        return out
    finally:
        GRACE_AT = saved


def agg(rows, cond, phase, key):
    vals = [r["cond"][cond][phase][key] for r in rows if r["cond"][cond][phase][key] is not None]
    return round(float(np.mean(vals)), 3) if vals else None


def hypotheses(rows, closed):
    H = {}
    H["H_I0_no_crossing_without_grace"] = {
        "verdict": "HOLDS" if all(r["cond"][c]["pre"]["crossed"] == 0 and r["cond"][c]["post"]["crossed"] == 0
                                  for r in closed for c in r["cond"]) else "VIOLATED",
        "gate_closed_runs": len(closed)}
    pre = {k: agg(rows, f"{k}-blind", "pre", "reached") for k in GROUNDS}
    H["H_I1_structure_not_quantity"] = {
        "verdict": "SUPPORTED" if pre["lived"] > pre["smoothed"] > pre["fresh"] else
                   "PARTIAL" if pre["lived"] > pre["fresh"] and pre["lived"] > pre["smoothed"] else "FALSIFIED",
        "mean_reached_of_12": pre,
        "mean_reach_step": {k: agg(rows, f"{k}-blind", "pre", "mean_reach_step") for k in GROUNDS},
        "crossings": {k: agg(rows, f"{k}-blind", "pre", "crossed") for k in GROUNDS}}
    lb, fb = agg(rows, "lived-blind", "post", "blight_any"), agg(rows, "fresh-blind", "post", "blight_any")
    H["H_I2_inheritance_traps"] = {"verdict": "SUPPORTED" if lb > fb else "FALSIFIED",
        "blight_any_of_12": {k: agg(rows, f"{k}-blind", "post", "blight_any") for k in GROUNDS},
        "blight_steps": {k: agg(rows, f"{k}-blind", "post", "blight_steps") for k in GROUNDS},
        "in_band_crossings": {k: agg(rows, f"{k}-blind", "post", "crossed_in_band") for k in GROUNDS}}
    ls = agg(rows, "lived-see", "post", "blight_any")
    lc, fc = agg(rows, "lived-see", "post", "crossed"), agg(rows, "fresh-see", "post", "crossed")
    H["H_I3_perception_rescues"] = {
        "verdict": "SUPPORTED" if (lb and ls <= lb * 0.5 and lc >= fc) else
                   "PARTIAL" if (lb and ls < lb) else "FALSIFIED",
        "lived_blight_blind": lb, "lived_blight_see": ls,
        "lived_crossings_see": lc, "fresh_crossings_see": fc,
        "declined": {k: agg(rows, f"{k}-see", "post", "declined") for k in GROUNDS}}
    h4 = {}
    for p in ("see", "blind"):
        cor = float(np.mean([r["cond"][f"lived-{p}"]["gen3"]["corrected"]["safe_crossings"] for r in rows]))
        sta = float(np.mean([r["cond"][f"lived-{p}"]["gen3"]["stale"]["safe_crossings"] for r in rows]))
        bc = float(np.mean([r["cond"][f"lived-{p}"]["gen3"]["corrected"]["blight_any"] for r in rows]))
        bs = float(np.mean([r["cond"][f"lived-{p}"]["gen3"]["stale"]["blight_any"] for r in rows]))
        h4[p] = {"safe_corrected": round(cor, 3), "safe_stale": round(sta, 3),
                 "blight_corrected": round(bc, 3), "blight_stale": round(bs, 3)}
    v = ("SUPPORTED" if all(x["safe_corrected"] > x["safe_stale"] for x in h4.values()) else
         "UNINFORMATIVE" if all(x["safe_corrected"] == x["safe_stale"] for x in h4.values()) else
         "FALSIFIED" if all(x["safe_corrected"] < x["safe_stale"] for x in h4.values()) else "MIXED")
    H["H_I4_correction_inherited"] = {"verdict": v, "detail": h4}
    din = agg(rows, "lived-see", "post", "declined_in_band")
    dall = agg(rows, "lived-see", "post", "declined")
    H["H_I5_dwelling_under_pull"] = {
        "verdict": "UNINFORMATIVE" if not dall else ("SUPPORTED" if din > (dall - din) else "FALSIFIED"),
        "declined_in_old_pass_band": din, "declined_elsewhere": round((dall or 0) - (din or 0), 3)}
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--start-seed", type=int, default=9000)
    ap.add_argument("--seeds", type=int, default=32)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists() and any(out.iterdir()):
        sys.exit("refusing to overwrite a nonempty output directory")
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.json").write_text(json.dumps({
        "battery": "rnr-inheritance/0.9", "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seeds": [a.start_seed, a.start_seed + a.seeds - 1], "grounds": GROUNDS,
        "python": platform.python_version(), "numpy": np.__version__,
        "source_sha256": {s: hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in SOURCES}}, indent=1))
    rows = []
    for s in range(a.start_seed, a.start_seed + a.seeds):
        rows.append(one_seed(s))
        (out / "progress.txt").write_text(f"{s}\n")
    closed = [one_seed(s, gate_open=False) for s in range(a.start_seed, a.start_seed + 4)]
    (out / "rows.json").write_text(json.dumps(rows))
    summary = {"n_seeds": len(rows), "mean_pass_y": round(float(np.mean([r["pass_y"] for r in rows])), 3),
               "founder_crossings": round(float(np.mean([r["founder_crossings"] for r in rows])), 2),
               "hypotheses": hypotheses(rows, closed)}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
