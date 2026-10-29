"""Attack: is the history-negative result an artefact of k=15 kNN?
Uses only packaged v0.2 observable_dataset.json + heldout_truth.json."""
import json, csv, numpy as np, sys
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
R='../positional_reception_v0_2/results/'
d=json.load(open(R+'observable_dataset.json')); truth={r['trial_id']:r['label'] for r in json.load(open(R+'heldout_truth.json'))}
def feats(r,fs):
    m={'imp':r['impulse'],'t':r['t'],'x':r['x'],'d1':r['x']-r['x_lag_half'],'d2':r['x_lag_half']-r['x_lag_one'],
       'xh':r['x_lag_half'],'x1':r['x_lag_one'],'acc':r['x']-2*r['x_lag_half']+r['x_lag_one']}
    return [m[f] for f in fs]
SETS={'position':['imp','x'],'time_position':['imp','t','x'],'history(pack)':['imp','t','x','d1','d2'],
 'pos+d1':['imp','x','d1'],'pos+accel':['imp','x','d1','acc'],'raw_lags':['imp','x','xh','x1']}
LEARN={'kNN15':lambda:make_pipeline(StandardScaler(),KNeighborsClassifier(15)),
 'logreg':lambda:make_pipeline(StandardScaler(),LogisticRegression(max_iter=5000,C=10)),
 'gboost':lambda:HistGradientBoostingClassifier(random_state=0),
 'rforest':lambda:RandomForestClassifier(300,random_state=0)}
CL=['left','right','unresolved']
def brier(P,cls,y):
    s=0
    for p,yy in zip(P,y):
        for c in CL:
            pc=p[list(cls).index(c)] if c in cls else 0
            s+=(pc-(yy==c))**2
    return s/len(y)
rows=[]
for regime in ['mixed','forward_only']:
    tr=[r for r in d['train'] if regime=='mixed' or r['family']=='forward']
    for sn,fs in SETS.items():
        X=np.array([feats(r,fs) for r in tr]); y=np.array([r['label'] for r in tr])
        for ln,mk in LEARN.items():
            m=mk().fit(X,y)
            for grp in ['all','forward','reverse']:
                te=[r for r in d['test'] if grp=='all' or r['family']==grp]
                Xt=np.array([feats(r,fs) for r in te]); yt=np.array([truth[r['trial_id']] for r in te])
                P=m.predict_proba(Xt); pred=m.classes_[P.argmax(1)]
                rows.append(dict(regime=regime,features=sn,learner=ln,group=grp,n=len(yt),
                  accuracy=round(float((pred==yt).mean()),4),brier=round(brier(P,m.classes_,yt),4)))
with open('learner_robustness.csv','w',newline='') as f:
    w=csv.DictWriter(f,rows[0].keys()); w.writeheader(); w.writerows(rows)
for r in rows:
    if r['group'] in('all','reverse'): print(r)
