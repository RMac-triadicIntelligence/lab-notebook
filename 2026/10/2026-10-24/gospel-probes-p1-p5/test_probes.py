"""Degenerate-gate tests: each pass condition vs a broken model that could also satisfy it."""
import probes as P
P.SEEDS = range(4)
def test_zero_coupling_contains_but_fails_coupling_gate():
    R, _ = P.excess_profile(P.graph("ring"), c=0.0)
    assert P.extent(R) <= 2          # would 'contain' trivially
    assert P.coupled(R) is False and P.contained(R) is False
def test_no_anchoring_ring_fails_containment():
    R, _ = P.excess_profile(P.graph("ring"), ke=0.0)
    assert P.contained(R) is False
def test_real_model_passes():
    R, _ = P.excess_profile(P.graph("ring")); assert P.contained(R) is True
def test_teleport_release_is_not_a_wavefront():
    r = P.p5_run(0, teleport=True); assert not (r["monotone"] and r["steps_per_hop"] > 0)
def test_never_release_fails_residual():
    r = P.p5_run(0, never=True); assert r["final_resid"] >= 1e-3
def test_verdicts_strict_bool():
    for v in P.p5_verdict([P.p5_run(0), P.p5_run(1)]).values(): assert type(v) is bool
    assert type(P.coupled({1: "prose"} if False else {1: 1.5})) is bool
