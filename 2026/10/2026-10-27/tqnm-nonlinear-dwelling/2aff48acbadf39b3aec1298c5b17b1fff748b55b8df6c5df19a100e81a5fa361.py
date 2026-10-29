"""Post-hoc descriptive diagnosis of the FULL all-abstain policy (Claude audit, 2026-10-27).

Reads retained evidence only; changes no frozen verdict, threshold or file.
Usage:  python3 diagnose_full_abstain.py evidence/run

Checks:
  1. Cue profile per world.
  2. Whether the FULL score is bimodal (saturated).
  3. Natural crossings by world and signal count, calibration and test.
  4. Whether any threshold in (0.6, 1] separates SPREAD from confounds among opened cases.
  5. Calibration feasibility under the frozen 5%-per-family limit.
  6. Which cues drive crossing (AUC + linear probe).
  7. Pattern completion: do opened confounds end with all three facets high?
  8. Sensitivity configs (8 seeds): crossings by world under each nudge/noise setting,
     and FULL-without-nudge vs MIN_CUE on the same subset.
"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

run = Path(sys.argv[1])
cases = json.loads((run / 'cases.json').read_text())
idx = {c['id']: c for c in cases}
dyn = defaultdict(dict)
for line in (run / 'dynamics.jsonl').read_text().splitlines():
    r = json.loads(line)
    if r['config'] == 'PRIMARY':
        dyn[r['arm']][r['case_id']] = r

worlds = ['SPREAD', 'CONCENTRATED', 'BURST', 'NULL']

print('== cue profile by world (all 576), mean [place, time, excess] ==')
for w in worlds:
    cs = np.array([c['cues'] for c in cases if c['world'] == w])
    print(f'{w:13s}', np.round(cs.mean(0), 3), ' min-cue mean', round(float(cs.min(1).mean()), 3))

def score(arm, cid):
    return dyn[arm][cid]['score']

print('\n== FULL score distribution: is it bimodal? ==')
s = np.array([score('FULL', c['id']) for c in cases])
bins = [0, .2, .4, .6, .8, .9, .95, .98, .99, .995, 1.0001]
h, _ = np.histogram(s, bins=bins)
for a, b, n in zip(bins[:-1], bins[1:], h):
    print(f'  [{a:.3f},{b:.3f}) {n}')
op = s[s > .6]
print('  opened scores: n=%d min=%.4f median=%.4f max=%.4f' % (len(op), op.min(), np.median(op), op.max()))

for split in ['calibration', 'test']:
    print(f'\n== FULL natural crossing (>0.6) by world and count, {split} ==')
    for w in worlds:
        row = []
        for k in [77, 115, 154]:
            sel = [c for c in cases if c['split'] == split and c['world'] == w and c['signal_count_setting'] == k]
            n_open = sum(score('FULL', c['id']) > .6 for c in sel)
            row.append(f'k{k}: {n_open}/{len(sel)}')
        tot = [c for c in cases if c['split'] == split and c['world'] == w]
        print(f'  {w:13s}', '  '.join(row), f'  total {sum(score("FULL", c["id"]) > .6 for c in tot)}/{len(tot)}')

print('\n== Among OPENED cases (all splits): can any threshold in (0.6,1] separate SPREAD from negatives? ==')
opened = [(score('FULL', c['id']), c['truth'], c['world']) for c in cases if score('FULL', c['id']) > .6]
for w in worlds:
    v = np.array([x[0] for x in opened if x[2] == w])
    if len(v):
        print(f'  {w:13s} n={len(v):3d} score min={v.min():.4f} median={np.median(v):.4f} max={v.max():.4f}')
pos = np.array([x[0] for x in opened if x[1]]); neg = np.array([x[0] for x in opened if not x[1]])
# AUC of score among opened
auc = (np.mean([[p > q for q in neg] for p in pos]) + 0.5 * np.mean([[p == q for q in neg] for p in pos]))
print('  AUC(score | opened) SPREAD vs negatives = %.3f' % auc)

print('\n== Calibration feasibility for FULL: best threshold per 5% per-family limit ==')
cal = [c for c in cases if c['split'] == 'calibration']
for t in [0.6, 0.9, 0.98, 0.99, 0.992, 0.994, 0.996, 0.998, 0.999]:
    pred = {c['id']: score('FULL', c['id']) > t for c in cal}
    tp = sum(pred[c['id']] for c in cal if c['truth'])
    fam = {w: sum(pred[c['id']] for c in cal if c['world'] == w) for w in worlds[1:]}
    print(f'  t={t:.3f}  TP={tp:2d}/48  false by family {fam}  (limit is 2 per 48)')

print('\n== What drives crossing? AUC of cue statistics for predicting FULL crossing (all 576) ==')
cues = np.array([c['cues'] for c in cases])
y = s > .6
def auc_of(x):
    p, n = x[y], x[~y]
    order = np.argsort(np.concatenate([p, n]))
    ranks = np.empty(len(order)); ranks[order] = np.arange(1, len(order) + 1)
    return (ranks[:len(p)].sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n))
for name, x in [('MIN cue', cues.min(1)), ('MEAN cue', cues.mean(1)), ('place', cues[:, 0]),
                ('time', cues[:, 1]), ('excess', cues[:, 2])]:
    print(f'  {name:9s} AUC={auc_of(x):.3f}')
# linear probe: least squares on cues for crossing indicator
X = np.c_[cues, np.ones(len(cues))]
w_, *_ = np.linalg.lstsq(X, y.astype(float), rcond=None)
print('  linear probe weights [place, time, excess, bias] =', np.round(w_, 3))

print('\n== Pattern completion check: negatives with one weak cue that still opened ==')
for w in ['CONCENTRATED', 'BURST']:
    sel = [c for c in cases if c['world'] == w and score('FULL', c['id']) > .6]
    if sel:
        cs = np.array([c['cues'] for c in sel])
        print(f'  {w:13s} opened n={len(sel)} mean cues of opened [place,time,excess]={np.round(cs.mean(0), 3)}')
        fin = np.array([dyn['FULL'][c['id']]['final_facets'] for c in sel])
        print(f'  {"":13s} final facets of opened (all three driven up?) mean={np.round(fin.mean(0), 3)}')

print('\n== SPREAD cases that did NOT open, by signal count (all 576) ==')
for k in [77, 115, 154]:
    sel = [c for c in cases if c['world'] == 'SPREAD' and c['signal_count_setting'] == k]
    print(f'  k{k}: opened {sum(score("FULL", c["id"]) > .6 for c in sel)}/{len(sel)}  mean cues {np.round(np.array([c["cues"] for c in sel]).mean(0), 3)}')

print('\n== Sensitivity configs, FULL crossings (>0.6) by world, 8 sensitivity seeds (descriptive only) ==')
sens_seeds = set(range(1000, 1008))
counts = defaultdict(lambda: defaultdict(lambda: [0, 0]))
min_cue = defaultdict(lambda: [0, 0, 0])
for line in (run / 'dynamics.jsonl').read_text().splitlines():
    r = json.loads(line)
    if r['arm'] != 'FULL':
        continue
    c = idx[r['case_id']]
    if r['config'] == 'PRIMARY' and c['seed'] not in sens_seeds:
        continue
    cell = counts[r['config']][c['world']]
    cell[0] += r['score'] > .6
    cell[1] += 1
for name, by_world in counts.items():
    print(f'  {name:20s}', '  '.join(f'{w}:{by_world[w][0]}/{by_world[w][1]}' for w in worlds))
for line in (run / 'decisions.jsonl').read_text().splitlines():
    d = json.loads(line)
    if d['config'] == 'NO_NUDGE' and d['arm'] in ('MIN_CUE', 'FULL'):
        m = min_cue[d['arm']]
        m[0] += d['commit'] and d['truth']; m[1] += d['commit'] and not d['truth']; m[2] += d['truth']
nn = counts['NO_NUDGE']
print('\n== Best case for the model vs ordinary baseline, same 96-case subset ==')
print(f"  FULL, no nudge, raw crossing as verdict: correct {nn['SPREAD'][0]}/{nn['SPREAD'][1]}, "
      f"false {sum(nn[w][0] for w in worlds[1:])}")
mc = min_cue['MIN_CUE']
print(f'  MIN_CUE at its frozen calibrated threshold: correct {mc[0]}/{mc[2]}, false {mc[1]}')
