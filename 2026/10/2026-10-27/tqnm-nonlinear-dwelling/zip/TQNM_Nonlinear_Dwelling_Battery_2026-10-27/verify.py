#!/usr/bin/env python3
"""Independent reconstruction of task evidence, calibration and scored decisions."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.stats import fisher_exact

ROOT=Path(__file__).resolve().parent


def lines(p):
    return [json.loads(x) for x in p.read_text().splitlines() if x]


def clean(x):
    if isinstance(x,dict):
        return {k:clean(v) for k,v in x.items() if not k.endswith('_ns')}
    if isinstance(x,list):
        return [clean(v) for v in x]
    return x


def evidence_check(out):
    config=json.loads((ROOT/'protocol.json').read_text())
    cases=json.loads((out/'cases.json').read_text())
    history=np.load(out/'histories.npz')['truncated']
    by_id={c['id']:c for c in cases}
    assert history.shape==(len(cases),180,8)
    for c,h in zip(cases,history):
        assert hashlib.sha256(h.tobytes()).hexdigest()==c['history_sha256']
        assert int(h[:60].sum())==24
        expected=48 if c['world']=='NULL' else c['signal_count_setting']
        assert int(h[60:].sum())==expected
        assert c['truth']==(c['world']=='SPREAD')
        base=h[:60]; signal=h[60:]
        def supports(s,b):
            k1,n1=int(s.sum()),s.size; k0,n0=int(b.sum()),b.size
            return fisher_exact([[k1,n1-k1],[k0,n0-k0]],alternative='greater')[1]<.05
        gp=sum(supports(signal[:,2*p:2*p+2],base[:,2*p:2*p+2]) for p in range(4))/4
        gt=sum(supports(signal[30*p:30*p+30],base) for p in range(4))/4
        effect=float(np.clip((signal.mean()-base.mean())/.10,0,1))
        assert np.allclose(c['cues'],[gp,gt,effect],atol=0,rtol=0)
        assert (c['reading']['decision']=='SUPPORT')==(gp>=.5 and gt>=.5)
    groups=defaultdict(list)
    for c,h in zip(cases,history):
        groups[(c['seed'],c['signal_count_setting'])].append(h)
    assert all(all(np.array_equal(group[0][:60],h[:60]) for h in group) for group in groups.values())
    raw=lines(out/'dynamics.jsonl'); decisions=lines(out/'decisions.jsonl')
    raw_index={(r['config'],r['arm'],r['case_id']):r for r in raw}
    cal=json.loads((out/'CALIBRATION.json').read_text())
    meta=json.loads((out/'run_metadata.json').read_text())
    result=json.loads((out/'RESULTS.json').read_text())
    for arm,fit in cal['arms'].items():
        assert fit['calibration_case_ids']==[c['id'] for c in cases if c['split']=='calibration']
        assert all(by_id[x]['split']=='calibration' for x in fit['calibration_case_ids'])
        chosen=[d for d in decisions if d['config']=='PRIMARY' and d['arm']==arm and d['split']=='calibration']
        assert len(chosen)==len(fit['calibration_case_ids'])
        scores=np.asarray([d['score'] for d in chosen]); truth=np.asarray([by_id[d['case_id']]['truth'] for d in chosen])
        floor=.6 if arm in config['models'] else 0.
        options=[i/1000 for i in range(int(round(floor*1000)),1001)]
        ranked=[]
        for threshold in options:
            p=scores>threshold
            valid=True
            for world in ['CONCENTRATED','BURST','NULL']:
                mask=np.asarray([by_id[d['case_id']]['world']==world for d in chosen])
                if p[mask].mean()>.05:
                    valid=False
            if valid:
                ranked.append((int((p&truth).sum()),-int((p&~truth).sum()),threshold))
        assert max(ranked)[2]==fit['threshold']
    summary=defaultdict(lambda:[0,0,0])
    for d in decisions:
        c=by_id[d['case_id']]
        assert d['truth']==c['truth']
        assert d['threshold']==cal['arms'][d['arm']]['threshold']
        assert d['commit']==(d['score']>d['threshold'])
        assert not d['permission_withheld_commit']
        if d['arm'] in config['models']:
            assert d['score']==raw_index[(d['config'],d['arm'],d['case_id'])]['score']
        else:
            cues=c['cues']
            if d['config']!='PRIMARY':
                inp=json.loads((out/f'input_{d["config"]}.json').read_text())
                cues=inp['cues'][inp['case_ids'].index(c['id'])]
            expected={'ARCHIVED_READER':float(cues[0]>=.5 and cues[1]>=.5),'MIN_CUE':min(cues),
                      'MEAN_CUE':float(np.mean(cues)),'GEOMEAN_CUE':float(np.prod(cues)**(1/3))}[d['arm']]
            assert np.isclose(d['score'],expected,atol=1e-15,rtol=0)
        if d['config']=='PRIMARY' and d['split']=='test':
            summary[d['arm']][0]+=int(d['commit'] and c['truth'])
            summary[d['arm']][1]+=int(d['commit'] and not c['truth'])
            summary[d['arm']][2]+=int(not d['commit'])
    for arm,values in summary.items():
        m=result['primary'][arm]
        assert values==[m['correct_commits'],m['false_commits'],m['abstentions']]
    configs=['PRIMARY']+[s['name'] for s in config['sensitivities']]
    for name in configs:
        runs=[r for r in meta['runs'] if r['config']==name]
        assert len(runs)==len(config['models'])
        assert len({r['noise_sha256'] for r in runs})==1
        assert len({r['steps_per_trajectory'] for r in runs})==1
        assert len({r['source_derivative_evaluations'] for r in runs})==1
        indexed={r['arm']:r for r in runs}
        assert indexed['NO_DWELL']['facet_stream_sha256']==indexed['FIELD_OFF']['facet_stream_sha256']
    for arm in config['models']:
        trace=np.load(out/f'trace_PRIMARY_{arm}.npz')
        for j,index in enumerate(trace['case_indices']):
            r=raw_index[('PRIMARY',arm,cases[int(index)]['id'])]
            assert np.array_equal(trace['states'][-1,j,:3],np.asarray(r['final_facets']))
            assert float(trace['states'][-1,j,3])==r['final_dwelling']
    print(json.dumps({'independent_evidence_check':'PASS','histories_checked':len(cases),
                      'dynamics_records':len(raw),'scored_decisions_checked':len(decisions),
                      'calibration_test_separation':'PASS','matched_noise_and_work':'PASS'},indent=2))


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('out',type=Path); parser.add_argument('--compare',type=Path)
    a=parser.parse_args(); evidence_check(a.out)
    if a.compare:
        for name in ['cases.json','CALIBRATION.json','RESULTS.json']:
            assert clean(json.loads((a.out/name).read_text()))==clean(json.loads((a.compare/name).read_text())),name
        for name in ['dynamics.jsonl','decisions.jsonl']:
            assert lines(a.out/name)==lines(a.compare/name),name
        for name in ['histories.npz']:
            assert np.array_equal(np.load(a.out/name)['truncated'],np.load(a.compare/name)['truncated'])
        assert clean(json.loads((a.out/'run_metadata.json').read_text()))==clean(json.loads((a.compare/'run_metadata.json').read_text()))
        print('CLEAN_COPY_REPRODUCTION: scientific outputs, inputs and deterministic work match exactly; timing excluded.')


if __name__=='__main__':
    main()
