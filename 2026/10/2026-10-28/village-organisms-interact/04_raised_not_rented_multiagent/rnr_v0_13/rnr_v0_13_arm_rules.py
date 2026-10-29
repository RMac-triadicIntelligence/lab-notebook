"""rnr v0.13 — arm update rules, for comparator review. NOT RUN.

Two state variables that v0.11/v0.12 conflated into one terrain mark:
    warn[gate]      shared. Lives in the commons. Read by every agent and every descendant.
    burden[agent]   private. Judgment carried by one agent. Read only by that agent.

Nothing below lets an agent read another agent's burden, or write warn outside a declaration.
"""
import numpy as np

# --- state ---------------------------------------------------------------------------
# warn:    np.ndarray over gate bins along the fence (y). Initialised 0. Shared.
# burden:  np.ndarray over agents. Private.
# graced:  bool per agent; set True for every agent present when grace is broadcast.
# waiver:  bool per agent; True only after release-exemption (arm C) or shuffle (arm D).

LESSON = 0.09      # warning deposited per declaration (same magnitude as v0.11/v0.12 MARK)
WARN_BAR = 0.05    # warn at a gate above this makes the crossing proposal costlier (see crossing)


# --- grace -----------------------------------------------------------------------------
def broadcast(graced, open_gate):
    """Broadcast offers the bit to everyone. It never writes dz and never lowers a wall."""
    graced |= open_gate
    return graced


# --- declaration (arms B, C, D) -------------------------------------------------------
def declare(agent, gate_bin, warn, burden, ledger, step):
    """Repentance: the agent's own action, available only after grace. Costs the author nothing.
    Writes the lesson to the commons at the gate it used. Does NOT touch burden."""
    warn[gate_bin] += LESSON                  # commons: all agents, all descendants
    ledger.append((agent, gate_bin, step))    # the gate-holder keeps the record
    # burden[agent] unchanged: no penalty for repentance


# --- release ---------------------------------------------------------------------------
def release(agent, burden, waiver, ledger):
    """Forgiveness: release of judgment. Requires a ledger entry for this agent (repentance first).
    burden -> 0. warn is never touched: the lesson stays in the commons, for the author too."""
    assert any(e[0] == agent for e in ledger), "release without declaration"
    burden[agent] = 0.0
    waiver[agent] = True                      # records that release happened; see crossing()


# --- crossing ----------------------------------------------------------------------------
def crossing_allowed(agent, gate_bin, proposes_crossing, open_gate, warn, burden):
    """Permission is the only way across. Warn and burden never grant a crossing; they only
    shape whether the agent proposes one (via dynamics) and whether it is taken.

    Which bar applies to the author:
      - warn[gate] applies to EVERY agent including the author, with or without waiver.
        Release does not erase a lesson the author itself wrote.
      - burden[agent] applies only to that agent, as noise + degraded evidence reading
        (dynamics, not here), and is the only thing release changes.
    So arm C can close the declarer gap ONLY if the author's cost in v0.11/v0.12 came from
    burden. If it came from warn, arm C cannot close it without erasing the warning for all.
    """
    if not (proposes_crossing and open_gate):
        return False
    return warn[gate_bin] <= WARN_BAR          # identical rule for author and everyone else


# --- arms ------------------------------------------------------------------------------
ARMS = {
    "A_no_declaration":  dict(declare=False, release=False, shuffle=False),
    "B_declare_only":    dict(declare=True,  release=False, shuffle=False),   # v0.11 behaviour
    "C_declare_release": dict(declare=True,  release=True,  shuffle=False),   # forgiveness = burden -> 0
    "D_shuffled_release": dict(declare=True, release=True,  shuffle=True),    # same count of releases,
}                                                                             # given to random agents


# --- metric --------------------------------------------------------------------------
def eligible_attempts(log, window):
    """Primary metric counts ELIGIBLE crossings only: an agent at the fence (|x| < 0.05)
    while the gate is open, inside the predeclared window [DECLARE_AT, STEPS). Counted as
    (attempted, allowed) so 'never came back' and 'came back and was blocked' separate."""
    return [(a, s, ok) for (a, s, at_fence, gate_open, ok) in log
            if window[0] <= s < window[1] and at_fence and gate_open]

# Primary:   allowed/attempted for declarers minus silent, window [DECLARE_AT, STEPS),
#            fixed before the run. Silent = eligible agents in the same window who did not declare.
# Secondary: descendant crossings through the declared gate, each arm vs A. Must stay below A,
#            or the warning was erased.
# Shuffle:   if D closes the gap as well as C, the effect is "fewer blocked agents", not
#            forgiveness of the one who declared.
# Acceptance: in BOTH seed blocks — same sign, C >= 0 on primary, C descendants below A.
#
# Prediction, stated before the run: C does NOT close the gap. In v0.11 penalty-free
# declaration added no burden, so the author's cost there came from the warning, which
# this rule leaves standing for the author too. If C closes it anyway, burden was doing
# more than I think.
