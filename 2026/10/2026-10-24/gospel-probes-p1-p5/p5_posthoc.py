"""POST-HOC (written after the preregistered P5 run failed; not preregistered).
Noise-free chain (s=0, eps=0) so the residual is purely the error's own deviation;
Damage_i = max |delta_i| over the clamp window; masses chosen around critical damping m=0.25."""
import json, numpy as np
N, DT, W, REL, POST = 24, 0.1, 2.0, 1500, 4000
def run(m):
    b = np.zeros(N); v = np.zeros(N); D = []
    for t in range(REL+POST):
        F = np.concatenate([[0 - b[0]], b[:-1] - b[1:]])
        if m > 0: v += DT*(F - v)/m; b = b + DT*v
        else: b = b + DT*F
        if t < REL: b[0] = W; v[0] = 0
        D.append(np.abs(b.copy()))
    D = np.array(D); dmg = D[:REL].max(0); post = D[REL:]
    heal = np.array([ (np.where(post[:, i] > 0.01*dmg[i])[0][-1]+1) for i in range(N)])
    first = np.array([ int(np.argmax(post[:, i] < 0.5*dmg[i])) for i in range(N)])
    return dict(mass=m, final_resid=float(post[-1].max()/W), damage_min=float(dmg[1:].min()),
        steps_per_hop_heal1pct=float(np.polyfit(range(1,N), heal[1:],1)[0]),
        steps_per_hop_half=float(np.polyfit(range(1,N), first[1:],1)[0]),
        monotone=bool(np.all(np.diff(heal[1:])>=0)),
        max_post_over_damage=float((post[:,1:].max(0)/dmg[1:]).max()), heal_steps=heal.tolist())
res = [run(m) for m in [0, 0.1, 0.25, 0.5, 1.0, 2.0]]
for r in res: print({k:v for k,v in r.items() if k!="heal_steps"})
json.dump(res, open("results/p5_posthoc.json","w"), indent=1)
