"""Attack: does observed x simply encode the hidden tilt a (and hence the capacity)?
Uses packaged v0.2 diagnostic_hidden.json (held-out hidden states)."""
import json, sys, numpy as np
sys.path.insert(0,'../positional_reception_v0_2'); import substrate_v01 as S
H=json.load(open('../positional_reception_v0_2/results/diagnostic_hidden.json'))
H=H if isinstance(H,list) else H.get('trials',H)
seen={};
for r in H:
    st=r['state']; seen[(r['seed'],r['family'],st['t'])]=st
x=np.array([s['x'] for s in seen.values()]); a=np.array([s['a'] for s in seen.values()])
A=np.c_[np.ones_like(x),x,x**2,x**3]; coef,*_=np.linalg.lstsq(A,a,rcond=None)
r2=1-((A@coef-a)**2).sum()/((a-a.mean())**2).sum()
cap=np.array([S.capacity(S.State(**s))['critical_positive_impulse'] for s in seen.values()])
B=np.c_[np.ones_like(x),x,x**2,x**3]; c2,*_=np.linalg.lstsq(B,cap,rcond=None)
r2c=1-((B@c2-cap)**2).sum()/((cap-cap.mean())**2).sum()
eq=np.array([abs(S.drift(s['x'],s['a'])) for s in seen.values()])
print(f'snapshots={len(x)}  R2(a ~ cubic(x))={r2:.4f}  R2(capacity ~ cubic(x))={r2c:.4f}')
print(f'|dx/dt| at snapshot: median={np.median(eq):.2e} max={eq.max():.2e}')
