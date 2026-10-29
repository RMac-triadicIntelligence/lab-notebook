"""Pure historical support reader. No signing, grant access or mutation."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from scipy.stats import fisher_exact

POLICY = "grace_window_v1 COUNTER/R_FULL; 180d; baseline60d; four30d blocks; Fisher greater p<.05; eligible>=20; breadth>=.5; magnitude=.25*min(breadths)"


@dataclass(frozen=True)
class Reading:
    decision: str
    reason: str
    magnitude: float
    place_support: float
    time_support: float


def _supports(k1, n1, k0, n0) -> bool:
    return bool(fisher_exact([[k1, n1 - k1], [k0, n0 - k0]], alternative="greater")[1] < .05)


def read(history, day: int) -> Reading:
    counts = Counter(e.day for e in history)
    if set(counts) != set(range(day - 179, day + 1)) or any(n != 8 for n in counts.values()):
        return Reading("HOLD", "insufficient_history", 0.0, 0.0, 0.0)
    baseline = [e for e in history if e.day <= day - 120]
    signal = [e for e in history if e.day > day - 120]
    k0, n0 = sum(e.truncated for e in baseline), len(baseline)
    eligible = []
    for place in range(4):
        b = [e for e in baseline if e.place == place]
        s = [e for e in signal if e.place == place]
        if len(s) >= 20:
            eligible.append(_supports(sum(e.truncated for e in s), len(s),
                                      sum(e.truncated for e in b), len(b)))
    gp = sum(eligible) / len(eligible) if eligible else 0.0
    blocks = []
    for block in range(4):
        lo = day - 120 + 30 * block
        rows = [e for e in signal if lo < e.day <= lo + 30]
        blocks.append(_supports(sum(e.truncated for e in rows), len(rows), k0, n0))
    gt = sum(blocks) / 4
    if gp < .5 or gt < .5:
        return Reading("HOLD", "insufficient_breadth", 0.0, gp, gt)
    return Reading("SUPPORT", "supported", .25 * min(gp, gt), gp, gt)
