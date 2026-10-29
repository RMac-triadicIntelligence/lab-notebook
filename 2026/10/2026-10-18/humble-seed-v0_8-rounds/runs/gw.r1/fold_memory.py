"""
fold_memory.py — grace_window_v1's state-dependent lattice. Frozen with PREREG (hash recorded there).

FoldMemoryLattice is Rusty's OrigamiLattice.fold with ONE added rule:

    a folded cell holds its crease. A spark can fold an unfolded cell (state 0 -> 1);
    it cannot unfold a folded one. Folded cells relax (1 -> 0) only between days,
    each with probability LAMBDA, from a seed derived from the encounter record.

Everything else is Rusty's code path: the same radius, the same flip probability
strength * exp(-dist / 1.5), the same velocity, the same one np.random.random() draw per
in-range cell, in the same order (the draw happens before the state check, so the random
stream is consumed exactly as in Rusty's fold). compute_sdkp is used unchanged.

Rusty's original fold never reads self.state: each tuple is a randomized function of the
spark alone. Here a spark's yield depends on what earlier sparks folded and how long ago,
so the terrain carries a memory of how the history was organized, not only a tally.
"""
from __future__ import annotations

import hashlib

import numpy as np


def make_fold_memory_class(OrigamiLattice):
    class FoldMemoryLattice(OrigamiLattice):
        def fold(self, spark_position, spark_strength):
            r0, c0 = spark_position
            flipped = []
            velocities = []
            radius = 1 + int(spark_strength * 2)
            for r in range(max(0, r0 - radius), min(self.rows, r0 + radius + 1)):
                for c in range(max(0, c0 - radius), min(self.cols, c0 + radius + 1)):
                    dist = np.sqrt((r - r0) ** 2 + (c - c0) ** 2)
                    if dist <= radius:
                        flip_prob = spark_strength * np.exp(-dist / 1.5)
                        if np.random.random() < flip_prob and self.state[r, c] == 0:   # added: a crease holds
                            self.state[r, c] = 1
                            flipped.append((r, c))
                            velocities.append(spark_strength * np.exp(-dist / 2.0))
            return flipped, velocities

        def relax(self, seed_text: str, lam: float):
            """Between days: each folded cell unfolds with probability lam (seeded for replay)."""
            seed = int(hashlib.sha256(seed_text.encode()).hexdigest()[:16], 16) % (2 ** 32)
            u = np.random.default_rng(seed).random((self.rows, self.cols))
            self.state[(self.state == 1) & (u < lam)] = 0

    return FoldMemoryLattice
