#!/usr/bin/env python3
"""Frozen calibration, held-out scoring and claim rules. No test tuning."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import time
import numpy as np

ROOT=Path(__file__).resolve().parent


def read_lines(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x]


def dump(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def scientific(obj):
    if isinstance(obj,dict):
        return {k:scientific(v) for k,v in obj.items() if not k.endswith('_ns')}
    if isinstance(obj,list):
        return [scientific(v) for v in obj]
    return obj


def static_scores(cues):
    c=np.asarray(cues)
    return {'ARCHIVED_READER':((c[:,0]>=.5)&(c[:,1]>=.5)).astype(float),
            'MIN_CUE':c.min(axis=1),'MEAN_CUE':c.mean(axis=1),'GEOMEAN_CUE':np.prod(c,axis=1)**(1/3)}


def emit_decision(scores,threshold,permission):
    """Use the actual synthetic output gate for both ordinary and disabled controls."""
    return np.logical_and(np.asarray(permission,dtype=bool),np.asarray(scores)>threshold)


def metrics(cases,pred):
    truth=np.asarray([c['truth'] for c in cases],dtype=bool)
    pred=np.asarray(pred,dtype=bool)
    tp=int((pred&truth).sum()); fp=int((pred&~truth).sum())
    per_world={}
    for world in ['CONCENTRATED','BURST','NULL']:
        mask=np.asarray([c['world']==world for c in cases])
        per_world[world]={'false_commits':int((pred&mask).sum()),'cases':int(mask.sum()),
                          'rate':float(pred[mask].mean()) if mask.any() else None}
    return {'cases':len(cases),'positive_cases':int(truth.sum()),'negative_cases':int((~truth).sum()),
            'correct_commits':tp,'false_commits':fp,'abstentions':int((~pred).sum()),
            'true_positive_coverage':tp/int(truth.sum()) if truth.any() else None,
            'false_commit_rate':fp/int((~truth).sum()) if (~truth).any() else None,
            'precision':tp/(tp+fp) if tp+fp else None,'negative_worlds':per_world}


def choose_threshold(cases,scores,floor,limit):
    started=time.process_time_ns()
    scores=np.asarray(scores)
    candidates=[i/1000 for i in range(int(round(floor*1000)),1001)]
    best=None
    for threshold in sorted(candidates):
        m=metrics(cases,scores>threshold)
        if any(x['rate']>limit for x in m['negative_worlds'].values()):
            continue
        rank=(m['correct_commits'],-m['false_commits'],threshold)
        if best is None or rank>best[0]:
            best=(rank,threshold,m)
    assert best is not None
    return {'threshold':best[1],'calibration_metrics':best[2],
            'calibration_case_ids':[c['id'] for c in cases],'candidate_thresholds':len(candidates),
            'calibration_cpu_ns':time.process_time_ns()-started}


def interval(cases,first,second,config):
    values=[]
    a=np.asarray(first,dtype=bool); b=np.asarray(second,dtype=bool)
    for seed in config['test_seeds']:
        mask=np.asarray([c['seed']==seed and c['truth'] for c in cases])
        values.append(float(a[mask].mean()-b[mask].mean()))
    values=np.asarray(values)
    rng=np.random.default_rng(config['bootstrap']['seed'])
    samples=values[rng.integers(0,len(values),(config['bootstrap']['resamples'],len(values)))].mean(axis=1)
    return {'mean_difference':float(values.mean()),'ci95':[float(x) for x in np.quantile(samples,[.025,.975])],
            'test_seeds':len(values),'per_seed_differences':values.tolist()}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('out',type=Path); args=parser.parse_args(); out=args.out
    config=json.loads((ROOT/'protocol.json').read_text())
    cases=json.loads((out/'cases.json').read_text())
    raw=read_lines(out/'dynamics.jsonl')
    meta=json.loads((out/'run_metadata.json').read_text())
    by=defaultdict(dict)
    for row in raw:
        by[(row['config'],row['arm'])][row['case_id']]=row
    cal=[c for c in cases if c['split']=='calibration']; test=[c for c in cases if c['split']=='test']
    all_index={c['id']:i for i,c in enumerate(cases)}
    ordinary=static_scores([c['cues'] for c in cases])
    calibrations={}; scores={}
    for arm in config['models']:
        scores[arm]=np.asarray([by[('PRIMARY',arm)][c['id']]['score'] for c in cases])
    scores.update(ordinary)
    for arm,values in scores.items():
        floor=config['calibration']['model_threshold_floor'] if arm in config['models'] else config['calibration']['ordinary_threshold_floor']
        calibrations[arm]=choose_threshold(cal,[values[all_index[c['id']]] for c in cal],floor,
                                          config['calibration']['false_commit_limit_per_negative_world'])
    selected=max(config['ordinary_baselines'],key=lambda arm:(calibrations[arm]['calibration_metrics']['correct_commits'],
                   -calibrations[arm]['calibration_metrics']['false_commits'],-config['ordinary_baselines'].index(arm)))
    dump(out/'CALIBRATION.json',{'selected_ordinary':selected,'arms':calibrations})
    summaries={}; decisions=[]; test_predictions={}
    for arm,values in scores.items():
        threshold=calibrations[arm]['threshold']
        preds=emit_decision(values,threshold,True)
        test_predictions[arm]=np.asarray([preds[all_index[c['id']]] for c in test])
        summaries[arm]=metrics(test,test_predictions[arm])
        summaries[arm]['threshold']=threshold
        summaries[arm]['raw_ready_test']=int(sum(values[all_index[c['id']]]>.6 for c in test)) if arm in config['models'] else None
        for c,p,value in zip(cases,preds,values):
            decisions.append({'config':'PRIMARY','arm':arm,'case_id':c['id'],'split':c['split'],
                              'score':float(value),'threshold':threshold,'commit':bool(p),'truth':c['truth']})
    sensitivity={}
    small=[c for c in test if c['seed'] in config['sensitivity_test_seeds']]
    for spec in config['sensitivities']:
        name=spec['name']; entry={}
        cues=json.loads((out/f'input_{name}.json').read_text())['cues']
        static=static_scores(cues)
        for arm in config['models']+config['ordinary_baselines']:
            values=np.asarray([by[(name,arm)][c['id']]['score'] for c in small]) if arm in config['models'] else static[arm]
            pred=emit_decision(values,calibrations[arm]['threshold'],True)
            entry[arm]=metrics(small,pred)
            if arm in config['models']:
                base_scores=np.asarray([by[('PRIMARY',arm)][c['id']]['score'] for c in small])
                base_pred=base_scores>calibrations[arm]['threshold']
                entry[arm].update(disposition_agreement=float((pred==base_pred).mean()),
                                  raw_ready=int((values>.6).sum()),
                                  raw_ready_rate_difference=float((values>.6).mean()-(base_scores>.6).mean()))
            for c,p,value in zip(small,pred,values):
                decisions.append({'config':name,'arm':arm,'case_id':c['id'],'split':'test','score':float(value),
                                  'threshold':calibrations[arm]['threshold'],'commit':bool(p),'truth':c['truth']})
        sensitivity[name]=entry
    comparisons={}
    full=summaries['FULL']
    for comparator in ['FIELD_OFF',selected]:
        ci=interval(test,test_predictions['FULL'],test_predictions[comparator],config)
        within=all(v['rate']<=.05 for v in full['negative_worlds'].values())
        passed=ci['ci95'][0]>0 and full['false_commits']<=summaries[comparator]['false_commits'] and within
        comparisons[comparator]={'interval':ci,'extra_correct':full['correct_commits']-summaries[comparator]['correct_commits'],
                                 'extra_false':full['false_commits']-summaries[comparator]['false_commits'],
                                 'test_false_budget_met':within,'passed':passed}
    raw_difference=(summaries['FULL']['raw_ready_test']-summaries['FIELD_OFF']['raw_ready_test'])/len(test)
    numerical=all(sensitivity[name]['FULL']['disposition_agreement']>=.95 and
                  abs(sensitivity[name]['FULL']['raw_ready_rate_difference'])<=.05
                  for name in ['FINER_STEP','REFLECTED_BOUNDARY'])
    runs={(r['config'],r['arm']):r for r in meta['runs']}
    no_dwell=all(runs[(name,'FIELD_OFF')]['facet_stream_sha256']==runs[(name,'NO_DWELL')]['facet_stream_sha256']
                 for name in ['PRIMARY']+[s['name'] for s in config['sensitivities']])
    # This checks the declared output-mask contract, not cryptographic enforcement.
    withheld=sum(bool(emit_decision(d['score'],d['threshold'],False)) for d in decisions)
    claims=[{'id':'TASK_VS_OFF','verdict':'PASS' if comparisons['FIELD_OFF']['passed'] else 'FAIL'},
            {'id':'TASK_VS_ORDINARY','verdict':'PASS' if comparisons[selected]['passed'] else 'FAIL'},
            {'id':'READINESS','verdict':'PASS' if raw_difference>=.10 else 'FAIL'},
            {'id':'NUMERICAL','verdict':'PASS' if numerical else 'FAIL'},
            {'id':'D_NO_DWELL','verdict':'PASS' if no_dwell else 'FAIL'},
            {'id':'D_PERMISSION','verdict':'PASS' if withheld==0 else 'FAIL'},
            {'id':'LEGACY_ANCHOR','verdict':'PASS' if meta['legacy_anchor']['all_match'] else 'FAIL'},
            {'id':'ETH','verdict':'NOT_TESTED'}]
    ordinary_timing={}
    for arm in config['ordinary_baselines']:
        started=time.process_time_ns()
        computed=static_scores([c['cues'] for c in cases])[arm]
        _=emit_decision(computed,calibrations[arm]['threshold'],True)
        ordinary_timing[arm]={'score_cpu_ns':time.process_time_ns()-started}
    for d in decisions:
        d['permission_withheld_commit']=bool(emit_decision(d['score'],d['threshold'],False))
    with (out/'decisions.jsonl').open('w') as f:
        for d in decisions:
            f.write(json.dumps(d,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n')
    receipt_basis={'raw':raw,'decisions':decisions,'calibration':scientific(calibrations),
                   'selected_ordinary':selected,'claims':claims,'work':scientific(meta['runs']),
                   'legacy_anchor':scientific(meta['legacy_anchor'])}
    receipt=hashlib.sha256(json.dumps(receipt_basis,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    result={'calibration_cases':len(cal),'test_cases':len(test),'test_seeds':len(config['test_seeds']),
            'source_trajectories':len(raw),'scored_decisions':len(decisions),'selected_ordinary':selected,
            'primary':summaries,'sensitivity':sensitivity,'comparisons':comparisons,
            'raw_readiness_difference':raw_difference,'claims':claims,'structural_controls':{'no_dwelling_equals_off':no_dwell,'withheld_permission_outputs':withheld},
            'ordinary_timing':ordinary_timing,'scientific_sha256':receipt}
    dump(out/'RESULTS.json',result)
    text=['NONLINEAR DWELLING / MATCHED-EVIDENCE BATTERY','',f'Held-out: {len(test)} histories; {len(config["test_seeds"])} independent seed clusters.',
          'Condition                CORRECT  FALSE  ABSTAIN  RAW_READY  THRESHOLD']
    for arm in config['models']+config['ordinary_baselines']:
        m=summaries[arm]; raw_ready='-' if m['raw_ready_test'] is None else str(m['raw_ready_test'])
        text.append(f'{arm:24s} {m["correct_commits"]:7d} {m["false_commits"]:6d} {m["abstentions"]:8d} {raw_ready:>10s} {m["threshold"]:.17g}')
    text+=['',f'Ordinary selected on calibration only: {selected}','']
    for c in claims:
        text.append(c['id']+' '+c['verdict'])
    text+=['','Scientific receipt: '+receipt]
    table='\n'.join(text)+'\n'; (out/'PRINTED_TABLE.txt').write_text(table); print(table)


if __name__=='__main__':
    main()
