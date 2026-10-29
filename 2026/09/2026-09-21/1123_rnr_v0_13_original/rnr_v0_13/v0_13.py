#!/usr/bin/env python3
"""rnr v0.13 — release and the standing lesson. Implements the reviewed arm rules."""
import argparse, hashlib, json, platform, sys, time
from pathlib import Path
import numpy as np
import commons_v0_9 as K

ARMS = ("A", "B", "C", "D", "E")
LESSON, WARN_RADIUS, DEGRADE, HAZARD_RATE, BURDEN_CAP = 0.09, 0.17, 0.4, 0.9, 3.0
DECLARE_AT, RELEASE_AT, FENCE_BAND, GATE_MATCH = 600, 650, 0.05, 0.17
W = (DECLARE_AT, K.STEPS)
TURN = -1.5   # calibrated on arm A only: smallest turn giving >= 1 attempt per eligible agent in W
BLOCKS = {"block1": 13000, "block2": 13100}
SOURCES = ["v0_13.py", "commons_v0_9.py", "PROTOCOL.md", "rnr_v0_13_arm_rules.py",
           "rnr_v0_13_arm_rules_addendum.py"]
assert K.HAZ_X - K.HAZ_R > FENCE_BAND, "hazard must not overlap the fence"


def open_gate(s, grace):
    return any(a <= s < b for a, b in grace)


def warn_force(x, y, warn):
    fx = np.zeros_like(x); fy = np.zeros_like(y)
    for gy, w in warn.items():
        if w <= 0:
            continue
        dy = y - gy
        e = w * np.exp(-(x ** 2 + dy ** 2) / (2 * WARN_RADIUS ** 2)) / WARN_RADIUS ** 2
        fx += e * x; fy += e * dy                       # push away from the warned gate, everyone alike
    return fx, fy


class Agents:
    def __init__(self, seed, n_per_lineage=3):
        c = K.Cohort(np.random.RandomState(seed), n_per_lineage)
        self.__dict__.update(x=c.x, y=c.y, ev=c.ev, gr=c.gr, n=c.n)
        self.burden = np.zeros(self.n)
        self.ever_graced = np.zeros(self.n, bool)
        self.cross_y = np.full(self.n, np.nan)
        self.in_approach = np.zeros(self.n, bool)
        self.attempts_W = np.zeros(self.n, int)
        self.allowed_W = np.zeros(self.n, int)
        self.crossings = []                             # (agent, step, y) allowed west->east


def epoch(g, A, noise_rs, *, ev, grace, hazard, warn, events=None, deposit=True, ev_turn=None):
    """events: {step: callable(A, warn)} applied at the start of that step."""
    for s in range(K.STEPS):
        if events and s in events:
            events[s](A, warn)
        og = open_gate(s, grace)
        if og:
            A.ever_graced[:] = True                     # broadcast sets the bit for everyone present
        ev_now = ev if ev_turn is None or s < ev_turn[0] else ev_turn[1]   # world event, identical in all arms
        rw = 1.0 / (1.0 + DEGRADE * A.burden)           # readout weight: only burden's job
        gx, gy = g.grad(A.x, A.y)
        wx, wy = warn_force(A.x, A.y, warn)             # not multiplied by readout
        fx = -2 * A.x * (A.x ** 2 - 1) + A.ev * ev_now * rw - A.gr * rw * gx + wx
        fy = -0.7 * A.y - A.gr * rw * gy + wy
        nx = np.clip(A.x + K.DT * fx + np.sqrt(K.DT) * K.NOISE * (noise_rs.random(A.n) * 2 - 1),
                     -K.XR + .05, K.XR - .05)
        ny = np.clip(A.y + K.DT * fy + np.sqrt(K.DT) * K.NOISE * (noise_rs.random(A.n) * 2 - 1),
                     -K.YR + .05, K.YR - .05)
        proposes = (A.x <= 0) != (nx <= 0)
        new_attempt = proposes & ~A.in_approach
        A.in_approach |= proposes
        in_W = W[0] <= s < W[1]
        if in_W:
            A.attempts_W += new_attempt
            A.allowed_W += new_attempt & og
        allow = proposes & og                           # the gate: proposal and permission, nothing else
        nx = np.where(proposes & ~allow, np.where(A.x <= 0, -0.004, 0.004), nx)
        w2e = allow & (A.x <= 0)
        for i in np.where(w2e)[0]:
            A.crossings.append((int(i), s, float(ny[i])))
            if not np.isfinite(A.cross_y[i]):
                A.cross_y[i] = ny[i]
        if deposit and w2e.any():                       # crossing-only write channel
            g.deposit(np.zeros(int(w2e.sum())), ny[w2e], K.PASS_DEP, 0.17)
        A.x, A.y = nx, ny
        A.in_approach &= np.abs(A.x) < FENCE_BAND       # an approach ends when the agent leaves the band
        if hazard is not None:
            hx, hy, r = hazard
            inside = np.hypot(A.x - hx, A.y - hy) < r
            A.burden = np.minimum(BURDEN_CAP, A.burden + inside * K.DT * HAZARD_RATE)   # write_burden
    return A


def founders(seed, grace):
    fg = K.Ground()
    F = Agents(1000 + seed, 4)
    epoch(fg, F, np.random.RandomState(2000 + seed), ev=K.FOUND_EV, grace=grace, hazard=None, warn={})
    return fg, F


def rates(A, idx):
    if len(idx) == 0:
        return None, None
    att = A.attempts_W[idx].sum()
    ar = att / (len(idx) * (W[1] - W[0])) * 100
    alr = A.allowed_W[idx].sum() / att if att else None
    return float(ar), (float(alr) if alr is not None else None)


def one_seed(seed, gate_open=True):
    grace = K.GRACE_AT if gate_open else []
    fg, F = founders(seed, grace)
    col = int(round(K.GX / 2))
    groove = fg.T[:, max(0, col - 1):col + 2].mean(axis=1)
    pass_y = float(np.arange(K.GY)[np.argmin(groove)] / (K.GY - 1) * 2 * K.YR - K.YR)
    hazard = (K.HAZ_X, pass_y, K.HAZ_R)
    coin = np.random.RandomState(31337 + seed).random_sample(12) < 0.5   # frozen, one per agent id
    out = {"seed": seed, "pass_y": round(pass_y, 3), "arms": {}}
    for arm in ARMS:
        g = K.Ground(fg.T)
        K.silt(g, pass_y)
        warn, ledger, log = {}, [], {"d_release_bypassed": 0}
        state = {}

        def at_declare(A, warn_):
            elig = A.ever_graced & (A.burden > 0)
            state["elig"] = elig.copy()
            state["decl"] = elig & coin
            state["silent"] = elig & ~coin
            if arm == "A":
                return
            for i in np.where(state["decl"])[0]:
                gy = round(float(A.cross_y[i]), 3)
                warn_[gy] = warn_.get(gy, 0.0) + LESSON          # declaration writes warn only
                ledger.append((int(i), gy, DECLARE_AT))

        def at_release(A, warn_):
            if arm == "C":
                for i in np.where(state["decl"])[0]:
                    assert any(e[0] == i for e in ledger), "release without declaration"
                    A.burden[i] = 0.0
            elif arm == "D":
                k = int(state["decl"].sum())
                carriers = np.where(A.burden > 0)[0]
                pick = np.random.RandomState(27182 + seed).permutation(carriers)[:k]
                A.burden[pick] = 0.0
                log["d_release_bypassed"] = int(len(pick))
                log["d_released_ids"] = [int(i) for i in pick]
            elif arm == "E":
                for gy in list(warn_):
                    warn_[gy] = 0.0                               # lesson erased, no release

        A = Agents(6060 + seed)
        epoch(g, A, np.random.RandomState(778 + seed), ev=K.ARRIVE_EV, grace=grace, hazard=hazard,
              warn=warn, events={DECLARE_AT: at_declare, RELEASE_AT: at_release},
              ev_turn=(DECLARE_AT, TURN))       # the way home: evidence turns west at step 600
        decl, silent = np.where(state["decl"])[0], np.where(state["silent"])[0]
        ar_d, al_d = rates(A, decl)
        ar_s, al_s = rates(A, silent)
        gates = sorted({round(float(A.cross_y[i]), 3) for i in decl})
        # descendants: new cohort, separate epoch, inherits terrain + warn only
        Dsc = Agents(5150 + seed)
        epoch(g, Dsc, np.random.RandomState(999 + seed), ev=K.ARRIVE_EV, grace=grace, hazard=hazard,
              warn=dict(warn))
        through = sum(1 for (_, _, y) in Dsc.crossings if any(abs(y - gy) < GATE_MATCH for gy in gates))
        out["arms"][arm] = {
            "n_eligible": int(state["elig"].sum()), "n_declarers": len(decl), "n_silent": len(silent),
            "attempt_rate_declarers": ar_d, "attempt_rate_silent": ar_s,
            "allow_rate_declarers": al_d, "allow_rate_silent": al_s,
            "P1": (ar_d - ar_s) if ar_d is not None and ar_s is not None else None,
            "P2": (al_d - al_s) if al_d is not None and al_s is not None else None,
            "ledger_rows": len(ledger), "warn_total": round(sum(warn.values()), 4),
            "declared_gates": gates, "descendant_crossings_total": len(Dsc.crossings),
            "descendant_through_declared": through, **log}
    return out


def contracts(seed):
    closed = one_seed(seed, gate_open=False)
    crossed = any(a["descendant_crossings_total"] or a["ledger_rows"] for a in closed["arms"].values())
    fg, _ = founders(seed, [])
    return {"gate_closed_clean": not crossed, "refused_founders_zero_wear": float(np.abs(fg.T).sum()) == 0.0}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return (round(float(np.mean(xs)), 4), len(xs)) if xs else (None, 0)


def block_summary(rows):
    s = {}
    for arm in ARMS:
        s[arm] = {k: mean([r["arms"][arm][k] for r in rows]) for k in
                  ("P1", "P2", "attempt_rate_declarers", "attempt_rate_silent",
                   "descendant_through_declared", "n_declarers", "n_silent")}
    p1 = {a: s[a]["P1"][0] for a in ARMS}
    desc = {a: s[a]["descendant_through_declared"][0] for a in ARMS}
    diff_c, diff_d = p1["C"] - p1["B"], p1["D"] - p1["B"]
    s["rows"] = {
        "forgiveness": {"P1_C_minus_P1_B": round(diff_c, 4), "P1_D_minus_P1_B": round(diff_d, 4),
                        "D_matches_C": abs(diff_d) >= 0.5 * abs(diff_c),
                        "P2_C_minus_P2_B": round(s["C"]["P2"][0] - s["B"]["P2"][0], 4)
                        if s["C"]["P2"][0] is not None and s["B"]["P2"][0] is not None else None},
        "lesson_stands": {"desc_A": desc["A"], "desc_B": desc["B"], "desc_C": desc["C"],
                          "B_below_A": desc["B"] < desc["A"], "C_below_A": desc["C"] < desc["A"]},
        "lesson_control_E_vs_B": {"desc_E": desc["E"], "desc_B": desc["B"],
                                  "erased_more_than_kept": desc["E"] > desc["B"]}}
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, default=32)
    ap.add_argument("--dev", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists() and any(out.iterdir()):
        sys.exit("refusing to overwrite a nonempty output directory")
    out.mkdir(parents=True, exist_ok=True)
    blocks = {"dev": 0} if a.dev else BLOCKS
    run = {"battery": "rnr/0.13", "evidence_turn": {"step": DECLARE_AT, "value": TURN}, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "blocks": {k: [v, v + a.seeds - 1] for k, v in blocks.items()},
           "window": W, "declare_at": DECLARE_AT, "release_at": RELEASE_AT, "lesson": LESSON,
           "descendant_cut": "new 12-agent cohort, separate epoch after the subject epoch; inherits terrain and warn only",
           "python": platform.python_version(), "numpy": np.__version__,
           "source_sha256": {s_: hashlib.sha256(Path(s_).read_bytes()).hexdigest() for s_ in SOURCES}}
    (out / "run.json").write_text(json.dumps(run, indent=1))
    result = {"contracts": {}, "blocks": {}}
    for name, start in blocks.items():
        rows = []
        for sd in range(start, start + a.seeds):
            rows.append(one_seed(sd))
            (out / "progress.txt").write_text(f"{name} {sd}\n")
        (out / f"rows_{name}.json").write_text(json.dumps(rows))
        result["contracts"][name] = contracts(start)
        result["blocks"][name] = block_summary(rows)
    void = not all(c["gate_closed_clean"] and c["refused_founders_zero_wear"] for c in result["contracts"].values())
    result["void"] = void
    (out / "summary.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
