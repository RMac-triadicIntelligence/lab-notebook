"""rnr v0.13 — addendum to arm rules. Supersedes crossing_allowed and the arm D note. NOT RUN."""
import numpy as np

# 1. WRITE_BURDEN — who, when, magnitude --------------------------------------------------
HAZARD_RATE, BURDEN_CAP = 0.9, 3.0

def write_burden(burden, inside_hazard, dt):
    """The only writer. Event: an agent's own step inside the hazard disc (its error).
    Magnitude: dt * 0.9 per step inside, capped at 3.0. Starts at 0 at birth (no baseline
    displacement in v0.13; that was the v0.12 kick confound). Occurs before DECLARE_AT,
    because the hazard exists from the start of the epoch and declaration is at step 600."""
    burden += inside_hazard * dt * HAZARD_RATE
    np.minimum(burden, BURDEN_CAP, out=burden)

# Burden's job in dynamics — readout only, no noise term (noise was the v0.12 kick):
DEGRADE = 0.4
def readout_weight(burden):
    return 1.0 / (1.0 + DEGRADE * burden)       # multiplies the evidence term and the ground term
# fx = well + ev * EVIDENCE * readout_weight(b) - gr * readout_weight(b) * dT/dx - warn_force
# Release (burden -> 0) restores full readout for that agent only. It never touches warn.

# 2. WARN — proposal penalty, not a forbid -------------------------------------------------
WARN_RADIUS = 0.17

def warn_force(y_agent, x_agent, warn, gate_y):
    """warn acts on dynamics as a repulsion around each warned gate bin, for every agent,
    author included, waiver or not. It shapes whether a crossing is proposed. It never
    enters the gate."""
    d2 = x_agent ** 2 + (y_agent - gate_y) ** 2
    return warn * np.exp(-d2 / (2 * WARN_RADIUS ** 2)) / WARN_RADIUS ** 2   # summed over bins

def crossing_allowed(proposes_crossing, open_gate_now):
    return proposes_crossing and open_gate_now   # binary. WARN_BAR is deleted.

# 3. GRACE — one bit, two readers ----------------------------------------------------------
# open_gate(s) := any(a <= s < b for a, b in GRACE_AT)        # the only grace bit
# crossing reads open_gate(s).
# declaration eligibility reads ever_graced[agent] := any(open_gate(t) for t <= s while present).
# broadcast never writes dz.

# 4. METRIC — exact expressions, window fixed before the run ---------------------------------
# W = [DECLARE_AT, STEPS) = [600, 900)
# attempt(agent, s): the unconstrained proposal at step s changes sign of x, AND the agent's
#                    previous step was not an attempt (one attempt per approach, not per step)
# allowed(agent, s): attempt(agent, s) and open_gate(s)
#
# attempt_rate(G) = sum_{a in G} #{s in W : attempt(a, s)} / (|G| * |W|) * 100   # per 100 steps
# allow_rate(G)   = sum_{a in G} #{s in W : allowed(a, s)} / sum_{a in G} #{s in W : attempt(a, s)}
#
# Primary (split, as asked):
#   P1 = attempt_rate(declarers_C) - attempt_rate(silent_C)      # does release change approach?
#   P2 = allow_rate(declarers_C)   - allow_rate(silent_C)        # given approach, is it taken?
# Silent group exists inside each arm: every eligible agent (ever_graced, burden > 0 at 600)
# declares with a pre-drawn Bernoulli(0.5) from its own RNG stream, identical draws in B, C, D.
# Paired check: the same agent ids in arm A have identical histories up to step 600 (same noise
# stream), so C-vs-A twin differences are reported alongside.
#
# ARM D — release onto burden carriers, ignoring the ledger:
#   k = number of releases in C. D releases k agents drawn at random from all agents with
#   burden > 0 at step 600, declared or not. D deliberately bypasses the ledger assert and logs it.
#   If D moves P1 as much as C, the effect is burden reduction, not repentance-then-forgiveness.
#
# Ledger rows, kept apart:
#   "forgiveness"   = C vs B on P1/P2, with D as the ordering control.
#   "lesson stands" = descendant crossings through the declared gate, B and C vs A (must stay below A).
