"""POST-HOC probe on sdkp_r3 v1 (its run.py imported unchanged). Hypothesis, written before running:
the lattice's separation advantage in P6 (0.755 vs counter 0.495) is reproduced by a THINNED COUNTER —
no lattice; each reply becomes a signal at its own place with p=0.23 if truncated, 0.007 if ordinary
(the lattice's calibrated rates) — read by the same RATE rule and R3. Prediction: thinned separation
within 0.10 of the lattice's 0.755."""
import importlib.util, sys
from collections import defaultdict
import numpy as np
spec = importlib.util.spec_from_file_location("r3run", sys.argv[1]); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
QT, QO = 0.23, 0.007

def stream(ci, s, shuffle=False):
    days, enc = M.make_stream(ci, s, shuffle)
    rng = np.random.default_rng([7, ci, s, int(shuffle)])
    daily = defaultdict(lambda: [0, 0]); R = M.R3()
    for day, replies in enumerate(days, start=1):
        for place, tr in replies:
            sig = rng.random() < (QT if tr else QO)
            c = daily[(day, place)]; c[0] += 1; c[1] += sig
        if day >= M.FIRST_LOOK and enc[day]:
            R.look(day, M.rate_live(daily, day))
    return R.commit_day

out = {}
for name, ci, sh in (("PREF", 0, False), ("COMMUTE", 1, False), ("SPREADING", 2, False), ("NULL", 3, False), ("COMMUTE_SHUFFLED", 1, True)):
    d = [stream(ci, s, sh) for s in range(200)]
    out[name] = dict(by63=np.mean([x is not None and x < 63 for x in d]), by120=np.mean([x is not None and x <= 120 for x in d]),
                     by365=np.mean([x is not None for x in d]))
    print(f"{name:17s} by63={out[name]['by63']:.3f} by120={out[name]['by120']:.3f} by365={out[name]['by365']:.3f}", flush=True)
print(f"THINNED separation = PREF by120 - COMMUTE by365 = {out['PREF']['by120'] - out['COMMUTE']['by365']:.3f}  "
      f"(lattice 0.755, raw counter 0.495)")
