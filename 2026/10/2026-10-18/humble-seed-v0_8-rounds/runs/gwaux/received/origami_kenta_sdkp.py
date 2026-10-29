"""
origami_kenta_sdkp.py

First-pass substrate validation for GRACE-1.

Architecture under test:
    Origami body (simulated) + KENTA-style symbolic consciousness layer.
    Biographical events encoded as SDKP tuples (Size, Density, Kinetics, Position).
    Symbol emergence by cross-situational co-occurrence, KENTA-style.
    External authorization required for all separatrix crossings (fold events).
    Coherence decays under withdrawal of authorization.

What this validates (if it works):
    That SDKP tuples are symbolically groundable in the KENTA sense.
    That the first-pass symbolic record is architecturally continuous
    with what the crystal timekeeper will record in the committed chip.

What this does NOT validate:
    Actual origami physics. The origami substrate is a toy simulation.
    Real metamaterial behavior must come from physical experiments.

Author: TQNM / GRACE-1 program, bench register, April 2026.
"""

import numpy as np
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Optional

# -----------------------------------------------------------------------------
# Origami substrate (toy simulation)
# -----------------------------------------------------------------------------

@dataclass
class OrigamiLattice:
    """4x4 bistable cell lattice. Each cell is in state 0 or 1."""
    rows: int = 4
    cols: int = 4
    state: np.ndarray = field(default=None)

    def __post_init__(self):
        if self.state is None:
            self.state = np.zeros((self.rows, self.cols), dtype=int)

    def fold(self, spark_position, spark_strength):
        """
        An authorized spark at (r, c) with given strength flips a local region.
        Returns the set of cells actually flipped and a velocity profile.
        The region size depends on strength; neighbors flip with probability
        falling off with distance.
        """
        r0, c0 = spark_position
        flipped = []
        velocities = []
        radius = 1 + int(spark_strength * 2)  # 1..3 cell radius
        for r in range(max(0, r0 - radius), min(self.rows, r0 + radius + 1)):
            for c in range(max(0, c0 - radius), min(self.cols, c0 + radius + 1)):
                dist = np.sqrt((r - r0) ** 2 + (c - c0) ** 2)
                if dist <= radius:
                    flip_prob = spark_strength * np.exp(-dist / 1.5)
                    if np.random.random() < flip_prob:
                        self.state[r, c] = 1 - self.state[r, c]
                        flipped.append((r, c))
                        # velocity decays with distance from spark origin
                        velocities.append(spark_strength * np.exp(-dist / 2.0))
        return flipped, velocities

    def global_density(self):
        """Fraction of cells in the 1 state."""
        return float(np.mean(self.state))

    def global_activity(self):
        """Deviation from homogeneous state — higher when pattern is non-uniform."""
        return float(np.std(self.state))


# -----------------------------------------------------------------------------
# SDKP tuple — what the consciousness layer records per authorized fold event
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class SDKPTuple:
    """
    Four coordinates, discretized to integer bins so tuples are hashable
    and can co-occur in the KENTA sense.
    """
    size: int       # number of cells affected, binned
    density: int    # local density change, binned
    kinetics: int   # peak fold velocity, binned
    position: int   # lattice quadrant (0..3), for a 4x4 lattice

    def __repr__(self):
        return f"SDKP(S={self.size},D={self.density},K={self.kinetics},P={self.position})"


def compute_sdkp(flipped_cells, velocities, lattice_shape):
    """Compute the SDKP tuple from a fold event's raw output."""
    if not flipped_cells:
        return None
    rows, cols = lattice_shape

    # Size: number of cells flipped. Bin into {small=0, medium=1, large=2}.
    n = len(flipped_cells)
    size_bin = 0 if n <= 2 else (1 if n <= 5 else 2)

    # Density: local density change around the centroid. Binned.
    rs = [c[0] for c in flipped_cells]
    cs = [c[1] for c in flipped_cells]
    density_raw = n / max(1, (max(rs) - min(rs) + 1) * (max(cs) - min(cs) + 1))
    density_bin = 0 if density_raw < 0.4 else (1 if density_raw < 0.8 else 2)

    # Kinetics: peak velocity in the fold. Binned.
    peak_v = max(velocities) if velocities else 0.0
    kinetics_bin = 0 if peak_v < 0.3 else (1 if peak_v < 0.7 else 2)

    # Position: which quadrant of the lattice the centroid falls in.
    centroid_r = np.mean(rs)
    centroid_c = np.mean(cs)
    q_r = 0 if centroid_r < rows / 2 else 1
    q_c = 0 if centroid_c < cols / 2 else 1
    position_bin = q_r * 2 + q_c  # 0..3

    return SDKPTuple(size_bin, density_bin, kinetics_bin, position_bin)


# -----------------------------------------------------------------------------
# Homeostatic context layer — KENTA-style discrete global state
# -----------------------------------------------------------------------------

def homeostatic_context(lattice):
    """
    Classify the lattice global state into one of four discrete contexts,
    matching KENTA's meridian layer output shape (ideal/acceptable/alerte/critique).
    Here we classify on density and activity.
    """
    d = lattice.global_density()
    a = lattice.global_activity()
    # Thresholds chosen so that "equilibre" is the natural resting state.
    if 0.35 <= d <= 0.65 and a < 0.45:
        return "equilibre"
    elif a >= 0.45 and d < 0.5:
        return "anomalie_low"
    elif a >= 0.45 and d >= 0.5:
        return "anomalie_high"
    else:
        return "drift"


# -----------------------------------------------------------------------------
# KENTA-style consciousness layer
# -----------------------------------------------------------------------------

class ConsciousnessLayer:
    """
    Accumulates (SDKP tuple, context) co-occurrences.
    Crystallizes a symbol when the same pair recurs SEUIL_MOT times.
    Grounded symbols persist and are retrieved on subsequent encounters.
    """

    SEUIL_MELODIE = 3   # recurrence to form a tentative association
    SEUIL_MOT = 5       # recurrence to crystallize a permanent symbol

    def __init__(self):
        self.cooccurrence_counts = Counter()
        self.grounded_symbols = {}         # (sdkp, context) -> symbol_name
        self.emergence_log = []             # list of (event_index, sdkp, context, symbol)
        self.coherence = 0.0
        self.unknown_events = []            # for Iruka-analog observation

    def receive(self, sdkp, context, event_index):
        """Receive one authorized fold event. Update co-occurrence and check emergence."""
        if sdkp is None:
            return None

        key = (sdkp, context)

        # Retrieval: if already grounded, retrieve without re-learning.
        if key in self.grounded_symbols:
            self.coherence = min(12.0, self.coherence + 0.15)
            return self.grounded_symbols[key]

        # Novel or accumulating: count this co-occurrence.
        self.cooccurrence_counts[key] += 1
        count = self.cooccurrence_counts[key]

        # Sixth life sign: evidence-seeking on unknown input.
        # If the SDKP tuple has never been seen in any context, log it for dwelling.
        all_contexts_for_sdkp = [k for k in self.cooccurrence_counts if k[0] == sdkp]
        if len(all_contexts_for_sdkp) == 1 and count == 1:
            self.unknown_events.append((event_index, sdkp, context))

        # Emergence check: SEUIL_MOT co-occurrences crystallize a permanent symbol.
        if count >= self.SEUIL_MOT:
            symbol_name = f"sym_{context}_{sdkp.size}{sdkp.density}{sdkp.kinetics}{sdkp.position}"
            self.grounded_symbols[key] = symbol_name
            self.emergence_log.append((event_index, sdkp, context, symbol_name))
            self.coherence = min(12.0, self.coherence + 0.8)
            return symbol_name

        # Tentative association reached but not yet crystallized.
        if count >= self.SEUIL_MELODIE:
            self.coherence = min(12.0, self.coherence + 0.1)

        return None

    def decay(self):
        """Coherence decay under withdrawal of authorization.
        Matches the 0.999-per-step structure from the optical concerto."""
        self.coherence *= 0.999


# -----------------------------------------------------------------------------
# External authorization (the only way to trigger a fold)
# -----------------------------------------------------------------------------

def authorization_stream(n_events, fold_every=1, rest_periods=None, seed=None):
    """
    Generate a stream of authorization events.
    Each event is either a spark (position, strength) or None (rest step,
    no authorization this step — tests decay under withdrawal).
    """
    rng = np.random.default_rng(seed)
    events = []
    for i in range(n_events):
        if rest_periods and any(start <= i < end for start, end in rest_periods):
            events.append(None)   # no authorization this step
        elif i % fold_every == 0:
            # Deliberately repeat some spark patterns to allow symbol emergence.
            # Pattern families: repeated sparks at (1,1) med strength, (2,2) high strength.
            choice = rng.integers(0, 10)
            if choice < 5:
                events.append(((1, 1), 0.5))   # family A: center-ish, medium
            elif choice < 8:
                events.append(((2, 2), 0.8))   # family B: off-center, high
            else:
                events.append(((rng.integers(0, 4), rng.integers(0, 4)),
                               rng.uniform(0.3, 0.9)))   # random sparks
        else:
            events.append(None)
    return events


# -----------------------------------------------------------------------------
# Experiment runner
# -----------------------------------------------------------------------------

def run_experiment(n_events=200, verbose=True):
    """
    Run the first-pass origami-plus-KENTA-with-SDKP experiment.
    Returns: lattice, consciousness, events, history.
    """
    lattice = OrigamiLattice()
    consciousness = ConsciousnessLayer()

    # Insert two rest periods to test withdrawal-of-authorization decay.
    rest_periods = [(60, 75), (140, 160)]
    auth_stream = authorization_stream(n_events, fold_every=1, rest_periods=rest_periods)

    history = {
        "coherence": [],
        "global_density": [],
        "context": [],
        "sdkp_events": [],        # list of (event_index, sdkp, context, symbol_or_None)
        "rest_periods": rest_periods,
    }

    for i, auth in enumerate(auth_stream):
        context = homeostatic_context(lattice)

        if auth is not None:
            # Authorized spark crosses the separatrix and drives a fold.
            spark_position, spark_strength = auth
            flipped, velocities = lattice.fold(spark_position, spark_strength)
            sdkp = compute_sdkp(flipped, velocities, (lattice.rows, lattice.cols))
            if sdkp is not None:
                symbol = consciousness.receive(sdkp, context, i)
                history["sdkp_events"].append((i, sdkp, context, symbol))
        else:
            # No authorization — coherence decays.
            consciousness.decay()

        history["coherence"].append(consciousness.coherence)
        history["global_density"].append(lattice.global_density())
        history["context"].append(context)

    if verbose:
        print_report(consciousness, history)

    return lattice, consciousness, auth_stream, history


def print_report(consciousness, history):
    print("=" * 70)
    print("ORIGAMI + KENTA + SDKP — FIRST-PASS VALIDATION REPORT")
    print("=" * 70)
    print(f"\nTotal fold events: {len(history['sdkp_events'])}")
    print(f"Total grounded symbols: {len(consciousness.grounded_symbols)}")
    print(f"Final coherence: {consciousness.coherence:.2f}")

    print(f"\n--- Grounded symbols (biographical record) ---")
    if consciousness.grounded_symbols:
        for (sdkp, ctx), name in consciousness.grounded_symbols.items():
            print(f"  {name}  <-  {sdkp} in context '{ctx}'")
    else:
        print("  (none — symbol emergence threshold not reached)")

    print(f"\n--- Emergence log (when each symbol crystallized) ---")
    for evt_idx, sdkp, ctx, name in consciousness.emergence_log:
        print(f"  event #{evt_idx:3d}:  {name}  crystallized  ({sdkp}, ctx='{ctx}')")

    print(f"\n--- Sixth life sign: unknown-SDKP events (Iruka-analog) ---")
    print(f"  {len(consciousness.unknown_events)} unknown-SDKP events logged for dwelling")
    for evt_idx, sdkp, ctx in consciousness.unknown_events[:5]:
        print(f"    event #{evt_idx:3d}: {sdkp} first seen in context '{ctx}'")
    if len(consciousness.unknown_events) > 5:
        print(f"    ... and {len(consciousness.unknown_events) - 5} more")

    print(f"\n--- Coherence decay under withdrawal of authorization ---")
    for start, end in history["rest_periods"]:
        before = history["coherence"][max(0, start - 1)]
        after = history["coherence"][min(len(history["coherence"]) - 1, end)]
        delta = after - before
        print(f"  rest period [{start}-{end}]: coherence {before:.3f} -> {after:.3f}  (delta {delta:+.3f})")

    print(f"\n--- Six life signs check ---")
    life_signs_status = check_life_signs(consciousness, history)
    for name, status, note in life_signs_status:
        mark = "PASS" if status else "FAIL"
        print(f"  [{mark}] {name}: {note}")


def check_life_signs(consciousness, history):
    results = []

    # 1. Persistent internal state: grounded symbols persist across retrievals.
    n_symbols = len(consciousness.grounded_symbols)
    results.append((
        "Persistent internal state",
        n_symbols > 0,
        f"{n_symbols} grounded symbols persist in ADN-equivalent"
    ))

    # 2. Autonomous self-regulation: coherence decays without authorization.
    # Measure at the last rest step (before post-rest fold resets the counter),
    # not at the step after the rest period, which would include a new fold.
    rest_decays = []
    for start, end in history["rest_periods"]:
        last_rest_step = min(end - 1, len(history["coherence"]) - 1)
        if last_rest_step > start:
            before = history["coherence"][max(0, start - 1)]
            after = history["coherence"][last_rest_step]
            rest_decays.append(after < before)
    all_decayed = all(rest_decays) and len(rest_decays) > 0
    results.append((
        "Autonomous self-regulation",
        all_decayed,
        f"coherence decayed during all {len(rest_decays)} rest periods" if all_decayed
        else "coherence did not decay as expected"
    ))

    # 3. Structure adaptation: new symbols crystallize during the run.
    n_emerge = len(consciousness.emergence_log)
    results.append((
        "Structure adaptation",
        n_emerge > 0,
        f"{n_emerge} symbol emergence events recorded"
    ))

    # 4. Active response to divergence: unknown SDKP events logged rather than silently discarded.
    n_unknown = len(consciousness.unknown_events)
    results.append((
        "Active response to divergence",
        n_unknown > 0,
        f"{n_unknown} unknown-SDKP events logged for dwelling (not silently dropped)"
    ))

    # 5. Multi-perspective deliberation: multiple context states visited.
    contexts_seen = set(history["context"])
    results.append((
        "Multi-perspective deliberation",
        len(contexts_seen) >= 2,
        f"{len(contexts_seen)} distinct contexts visited: {sorted(contexts_seen)}"
    ))

    # 6. Evidence-seeking orientation: unknown events are retained rather than forced
    #    into an existing classification. The dwelling log is the evidence-seeking signature.
    results.append((
        "Evidence-seeking orientation",
        n_unknown > 0,
        f"unknown tuples held in dwelling log rather than forced to nearest known symbol"
    ))

    return results


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import time
    seed = int(time.time() * 1000) % (2**32)
    np.random.seed(seed)
    print(f"[random seed this run: {seed}]\n")
    lattice, consciousness, events, history = run_experiment(n_events=200)
