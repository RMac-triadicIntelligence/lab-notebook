"""P1-P5 RECONSTRUCTION from narrative (§4, Developmental Meaning Fork). Not the original code. See PROTOCOL.md."""
import json, sys
import numpy as np, networkx as nx

N, DT, KE, C, W = 24, 0.1, 1.0, 0.5, 2.0
THETA, SIG, NOISE = 0.05, 0.3, 0.3
STEPS, MEAS0, SEEDS = 3000, 1000, range(20)

def graph(name):
    if name == "ring": return nx.cycle_graph(N)
    if name == "lattice": return nx.convert_node_labels_to_integers(nx.grid_2d_graph(4, 6, periodic=True))
    if name == "ws0.1": return nx.connected_watts_strogatz_graph(N, 4, 0.1, seed=7)
    if name == "ws0.3": return nx.connected_watts_strogatz_graph(N, 4, 0.3, seed=7)
    if name == "complete": return nx.complete_graph(N)
    if name == "ba": return nx.barabasi_albert_graph(N, 2, seed=7)
    if name == "path": return nx.path_graph(N)
    raise ValueError(name)

def simulate(G, seed, mode="independent", site=0, err=True, ke=KE, c=C, norm=True,
             mass=0.0, release=None, steps=STEPS, teleport=False):
    """Returns beliefs (steps,N) and truth (steps,N). Same seed => same noise draws."""
    rng = np.random.default_rng(seed)
    A = nx.to_numpy_array(G, nodelist=range(N))
    deg = A.sum(1); n = deg if norm else np.ones(N)
    shared = mode in ("shared", "testimony", "chain")
    s = rng.normal(0, SIG/np.sqrt(2*THETA), 1 if shared else N) * np.ones(N)
    b = s.copy(); v = np.zeros(N)
    B = np.empty((steps, N)); S = np.empty((steps, N))
    for t in range(steps):
        xi = rng.normal(0, 1, N); eps = rng.normal(0, NOISE, N)
        if shared: s = s + (-THETA*s)*DT + SIG*np.sqrt(DT)*xi[0]
        else: s = s + (-THETA*s)*DT + SIG*np.sqrt(DT)*xi
        obs = s + eps
        if mode == "testimony":
            e = 0.5*obs + 0.5*(A @ b)/deg
        elif mode == "chain":
            e = np.concatenate([[obs[0]], b[:-1] + eps[1:]])
        else:
            e = obs
        F = ke*(e - b)
        if mode != "chain": F = F + c*((A @ b) - deg*b)/n
        if mass > 0:
            v = v + DT*(F - v)/mass; b = b + DT*v
        else:
            b = b + DT*F
        clamped = err and (release is None or t < release)
        if clamped: b[site] = W; v[site] = 0.0
        if teleport and err and release is not None and t == release:
            b = s.copy(); v[:] = 0  # mutant: instant global healing
        B[t] = b; S[t] = s
    return B, S

def excess_profile(G, site=0, **kw):
    dist = nx.single_source_shortest_path_length(G, site)
    D = np.array([dist[i] for i in range(N)])
    ratios = []
    for sd in SEEDS:
        Be, S = simulate(G, sd, site=site, err=True, **kw)
        Bb, _ = simulate(G, sd, site=site, err=False, **kw)
        ee = np.sqrt(((Be[MEAS0:]-S[MEAS0:])**2).mean(0)); eb = np.sqrt(((Bb[MEAS0:]-S[MEAS0:])**2).mean(0))
        ratios.append(ee/eb)
    ratios = np.array(ratios)
    R = {int(d): float(ratios[:, D == d].mean()) for d in sorted(set(D))}
    site_med = float(np.median(ratios[:, site]))
    return R, site_med

def extent(R): return max([d for d, r in R.items() if d > 0 and r > 1.10], default=0)
def coupled(R): return bool(R.get(1, 1.0) - 1.0 > 0.01)
def contained(R): return bool(extent(R) <= 2 and coupled(R))

def p5_run(mass, seed=0, release=1500, post=3000, teleport=False, never=False):
    G = graph("path"); steps = release + post
    rel = None if never else release
    Be, S = simulate(G, seed, mode="chain", mass=mass, release=rel, steps=steps, teleport=teleport)
    Bb, _ = simulate(G, seed, mode="chain", err=False, mass=mass, steps=steps)
    d = np.abs(Be - Bb)
    dmg = d[release-1]; postd = d[release:]
    heal = []
    for i in range(N):
        above = np.where(postd[:, i] > 0.01*max(dmg[i], 1e-12))[0]
        heal.append(int(above[-1]+1) if len(above) else 0)
    heal = np.array(heal)
    slope = float(np.polyfit(np.arange(1, N), heal[1:], 1)[0])
    over = postd[:, 1:].max(0) > dmg[1:]
    return dict(mass=mass, final_resid=float(postd[-1].max()/W), heal_steps=heal.tolist(),
                steps_per_hop=slope, monotone=bool(np.all(np.diff(heal[1:]) >= 0) and heal[-1] > heal[1]),
                transient_units=int(over.sum()), max_post_over_damage=float((postd[:,1:].max(0)/np.maximum(dmg[1:],1e-12)).max()),
                damage_min=float(dmg[1:].min()))

def p5_verdict(runs):
    by = {r["mass"]: r for r in runs}; ms = sorted(by)
    resid = all(by[m]["final_resid"] < 1e-3 for m in ms)
    wave = all(by[m]["monotone"] and by[m]["steps_per_hop"] > 0 for m in ms)
    slow = all(by[a]["steps_per_hop"] < by[b]["steps_per_hop"] for a, b in zip(ms, ms[1:]))
    trans = by[ms[-1]]["transient_units"] > 0 and by[0]["transient_units"] == 0
    return dict(residual_zero=bool(resid), wavefront=bool(wave), weight_slows=bool(slow), transient=bool(trans))

def main():
    out = {}
    R, sm = excess_profile(graph("ring"))
    p1 = dict(R=R, site_ratio_median=sm, extent=extent(R), coupled=coupled(R))
    p1["verdict"] = "reproduced" if (5 <= sm <= 17 and R[2] < 1.10 and coupled(R)) else ("partly" if sm >= 2 and contained(R) else "not")
    out["P1"] = p1; print("P1", p1, flush=True)

    p2 = {}
    for g in ["ring", "lattice", "ws0.1", "ws0.3", "complete"]:
        R, sm = excess_profile(graph(g)); p2[g] = dict(R=R, site=sm, extent=extent(R), coupled=coupled(R), contained=contained(R))
        print("P2", g, p2[g], flush=True)
    allc = all(v["contained"] for v in p2.values())
    densest = min(p2, key=lambda g: p2[g]["R"][1] - 1) == "complete"
    out["P2"] = dict(runs=p2, all_contained=allc, dense_most_contained=densest,
                     verdict="reproduced" if allc and densest else ("partly" if allc else "not"))

    p3 = {}
    Gba = graph("ba"); hub = max(Gba.degree, key=lambda x: x[1])[0]
    for name, G, site, norm in [("ring_unnorm", graph("ring"), 0, False), ("complete_unnorm", graph("complete"), 0, False),
                                 ("ba_hub_norm", Gba, hub, True), ("ba_hub_unnorm", Gba, hub, False)]:
        R, sm = excess_profile(G, site=site, norm=norm); p3[name] = dict(R=R, site=sm, extent=extent(R), coupled=coupled(R), contained=contained(R))
        print("P3", name, p3[name], flush=True)
    Rm, smm = excess_profile(graph("ring"), ke=0.05)
    mech = dict(R=Rm, extent=extent(Rm), contained=contained(Rm))
    print("P3 anchoring mutant", mech, flush=True)
    allc = all(v["contained"] for v in p3.values()); mech_ok = mech["extent"] >= 4
    out["P3"] = dict(runs=p3, hub_degree=int(Gba.degree[hub]), anchoring_mutant=mech, all_contained=allc, anchoring_supported=mech_ok,
                     verdict="reproduced" if allc and mech_ok else ("partly" if allc else "not"))

    p4 = {}
    for name, g, mode in [("shared", "ring", "shared"), ("testimony", "ring", "testimony"), ("chain", "path", "chain")]:
        R, sm = excess_profile(graph(g), mode=mode); p4[name] = dict(R=R, site=sm, extent=extent(R), coupled=coupled(R))
        print("P4", name, p4[name], flush=True)
    a = p4["shared"]["extent"] <= 2; b = p4["testimony"]["extent"] > p4["shared"]["extent"]; ch = p4["chain"]["extent"] == 23
    out["P4"] = dict(runs=p4, verdict="reproduced" if a and b and ch else ("partly" if ch else "not"))

    runs = [p5_run(m) for m in [0, 1, 4, 10]]
    for r in runs: print("P5", {k: v for k, v in r.items() if k != "heal_steps"}, flush=True)
    v = p5_verdict(runs)
    out["P5"] = dict(runs=runs, checks=v, verdict="reproduced" if all(v.values()) else ("partly" if v["residual_zero"] and v["wavefront"] else "not"))
    json.dump(out, open("results/results.json", "w"), indent=1)
    print({k: out[k]["verdict"] for k in out})

if __name__ == "__main__": main()
