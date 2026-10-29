"""Sensor calibration only (no conditions): Rusty's lattice, per corner and strength.
P(tuple Size>=1), P(tuple Position == corner | tuple), P(signal tuple at corner)."""
import importlib.util, sys
import numpy as np
spec = importlib.util.spec_from_file_location("ok", sys.argv[1]); O = importlib.util.module_from_spec(spec); spec.loader.exec_module(O)
CORNERS = [(0, 0), (0, 3), (3, 0), (3, 3)]
np.random.seed(424242)
N = 200000
for st in (0.3, 0.6):
    row = []
    for q, c in enumerate(CORNERS):
        lat = O.OrigamiLattice(); sig = sig_here = tup = pos_ok = 0
        for _ in range(N):
            f, v = lat.fold(c, st); t = O.compute_sdkp(f, v, (4, 4))
            if t is None: continue
            tup += 1; pos_ok += t.position == q
            if t.size >= 1:
                sig += 1; sig_here += t.position == q
        row.append(f"corner{q}: sig={sig/N:.4f} sig@corner={sig_here/N:.4f} tuple={tup/N:.3f} pos_match={pos_ok/max(tup,1):.3f}")
    print(f"strength {st}:\n  " + "\n  ".join(row))
