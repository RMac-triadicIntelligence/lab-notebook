#!/usr/bin/env python3
"""New matched-evidence harness around byte-preserved archived source."""
from __future__ import annotations
import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor/received'))
sys.path.insert(0,str(ROOT/'vendor/historical'))
import triadic_model
import dwelling
from topography import Encounter


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+'\n')


def freeze_check():
    lock=json.loads((ROOT/'FREEZE.json').read_text())
    for name,expected in lock['sha256'].items():
        if sha(ROOT/name)!=expected:
            raise RuntimeError('Frozen file changed: '+name)
    return sha(ROOT/'FREEZE.json')


def build_cases(config):
    started=time.process_time_ns()
    cases,histories=[],[]
    for seed in config['calibration_seeds']+config['test_seeds']:
        split='calibration' if seed in config['calibration_seeds'] else 'test'
        for count in config['signal_counts']:
            base_rng=np.random.default_rng(np.random.SeedSequence([20261027,1,seed,count]))
            baseline=base_rng.choice(480,config['history']['baseline_truncated'],replace=False)
            for world_index,world in enumerate(config['worlds']):
                rng=np.random.default_rng(np.random.SeedSequence([20261027,2,seed,count,world_index]))
                history=np.zeros((180,8),dtype=np.bool_)
                history.reshape(-1)[baseline]=True
                if world=='SPREAD':
                    indices=rng.choice(np.arange(480,1440),count,replace=False)
                elif world=='CONCENTRATED':
                    place=seed%4
                    pool=[(d-1)*8+i for d in range(61,181) for i in range(8) if i//2==place]
                    indices=rng.choice(pool,count,replace=False)
                elif world=='BURST':
                    start=config['history']['burst_starts'][seed%6]
                    pool=[(d-1)*8+i for d in range(start,start+20) for i in range(8)]
                    indices=rng.choice(pool,count,replace=False)
                else:
                    indices=rng.choice(np.arange(480,1440),config['history']['null_signal_truncated'],replace=False)
                history.reshape(-1)[indices]=True
                records=tuple(Encounter(day=d,index=i,place=i//2,truncated=bool(history[d-1,i]))
                              for d in range(1,181) for i in range(8))
                reading=dwelling.read(records,180)
                excess=float(history[60:].mean()-history[:60].mean())
                cues=[float(reading.place_support),float(reading.time_support),float(np.clip(excess/.10,0,1))]
                case={'id':f's{seed}_k{count}_{world}','seed':seed,'split':split,'world':world,
                      'world_index':world_index,'signal_count_setting':count,'truth':world=='SPREAD',
                      'history_sha256':hashlib.sha256(history.tobytes()).hexdigest(),
                      'baseline_count':int(history[:60].sum()),'recent_count':int(history[60:].sum()),
                      'reading':asdict(reading),'cues':cues}
                cases.append(case)
                histories.append(history)
    return cases,np.stack(histories),time.process_time_ns()-started


def make_noise(cases,dt,config):
    """One fine Brownian stream per case; coarse increments sum adjacent fine ones."""
    start=time.process_time_ns()
    fine_dt=.01
    fine_steps=int(round(config['dynamics']['end']/fine_dt))
    steps=int(round(config['dynamics']['end']/dt))
    output=np.empty((steps,len(cases),3),dtype=np.float64)
    for i,case in enumerate(cases):
        entropy=[20261027,17,case['seed'],case['signal_count_setting'],case['world_index']]
        z=np.random.default_rng(np.random.SeedSequence(entropy)).standard_normal((fine_steps,3))
        if dt==fine_dt:
            output[:,i]=z
        elif dt==2*fine_dt:
            output[:,i]=z.reshape(steps,2,3).sum(axis=1)/np.sqrt(2.)
        else:
            raise ValueError('Only declared .01/.02 grids are supported')
    return output,{'noise_cpu_ns':time.process_time_ns()-start,
                   'normal_draws':fine_steps*len(cases)*3,
                   'noise_sha256':hashlib.sha256(output.tobytes()).hexdigest(),
                   'dt':dt,'cases':len(cases)}


def finite(value):
    return None if not np.isfinite(value) else float(value)


def simulate(arm,cues,noise,settings,trace_indices):
    start_cpu,start_wall=time.process_time_ns(),time.perf_counter_ns()
    dt=settings['dt']; n=len(cues); steps=int(round(settings['end']/dt))
    y=np.tile(np.asarray(settings['initial'],dtype=float)[:,None],(1,n))
    nodwell=arm=='NO_DWELL'
    if nodwell:
        y[3]=0
    ke=int(round(settings['evidence_time']/dt))
    kn=int(round(settings['nudge_time']/dt))
    k0=int(round(settings['permission_start']/dt)); k1=int(round(settings['permission_end']/dt))
    score=np.zeros(n); first=np.full(n,np.nan); authorized_first=np.full(n,np.nan)
    trace=[y[:,trace_indices].T.copy()]; times=[0.]
    stream=hashlib.sha256()
    for k in range(steps):
        active=arm=='ALWAYS_ON' or k0<=k<k1
        coupling=settings['coupling_boost'] if active and arm not in ('FIELD_OFF','DECAY_ONLY') else 0.
        relief=settings['decay_relief'] if active and arm not in ('FIELD_OFF','COUPLING_ONLY') else 0.
        kw={'coupling_boost':coupling,'decay_relief':relief}
        if nodwell:
            kw['story_depth']=0.
        y += dt*np.asarray(triadic_model.model_parable(y,k*dt,**kw))
        y[:3] += settings['noise']*np.sqrt(dt)*noise[k].T
        if k==ke:
            y[:3] += settings['evidence_gain']*cues.T
        if k==kn:
            y[0] += settings['nudge']
        if settings.get('boundary','clip')=='reflect':
            folded=np.mod(y[:3],2.)
            y[:3]=np.where(folded<=1.,folded,2.-folded)
        else:
            y[:3]=np.clip(y[:3],0.,1.)
        y[3]=np.clip(y[3],0.,1.)
        coherence=y[:3].mean(axis=0)
        fresh=np.isnan(first)&(coherence>settings['opening_threshold'])
        first[fresh]=(k+1)*dt
        eligible=k>=ke and k>=k0 and k+1<k1
        if eligible:
            score=np.maximum(score,coherence)
            newly=np.isnan(authorized_first)&(coherence>settings['opening_threshold'])
            authorized_first[newly]=(k+1)*dt
        stream.update(y[:3].tobytes())
        if (k+1)%int(round(1./dt))==0:
            trace.append(y[:,trace_indices].T.copy()); times.append((k+1)*dt)
    rows=[]
    for i in range(n):
        rows.append({'score':float(score[i]),'raw_first':finite(first[i]),
                     'authorized_first':finite(authorized_first[i]),
                     'pre_evidence_open':bool(np.isfinite(first[i]) and first[i]<settings['evidence_time']),
                     'retained':bool(y[:3,i].mean()>settings['opening_threshold']),
                     'final_facets':[float(v) for v in y[:3,i]],'final_dwelling':float(y[3,i])})
    work={'trajectories':n,'steps_per_trajectory':steps,'source_derivative_evaluations':steps*n,
          'decision_horizon_evaluations':k1*n,'retention_evaluations':(steps-k1)*n,
          'arm_cpu_ns':time.process_time_ns()-start_cpu,'arm_wall_ns':time.perf_counter_ns()-start_wall,
          'facet_stream_sha256':stream.hexdigest()}
    return rows,work,np.stack(trace),np.asarray(times)


def ordinary_scores(cases,cues=None):
    cues=np.asarray([c['cues'] for c in cases]) if cues is None else cues
    return {'ARCHIVED_READER':((cues[:,0]>=.5)&(cues[:,1]>=.5)).astype(float),
            'MIN_CUE':cues.min(axis=1),'MEAN_CUE':cues.mean(axis=1),
            'GEOMEAN_CUE':np.prod(cues,axis=1)**(1./3.)}


def source_audits():
    states=np.asarray([[.12,.23,.31,.45],[.3,.1,.27,.6],[.11,.15,.2,.7]]).T
    batch=np.asarray(triadic_model.model_parable(states,1.))
    scalar=np.stack([triadic_model.model_parable(states[:,i],1.) for i in range(states.shape[1])],axis=1)
    assert np.array_equal(batch,scalar)
    return {'vectorized_scalar_derivative_parity':True}


def legacy_anchor():
    start=time.process_time_ns()
    spec=importlib.util.spec_from_file_location('legacy_g2',ROOT/'vendor/legacy_g2/test_G2.py')
    legacy=importlib.util.module_from_spec(spec); spec.loader.exec_module(legacy)
    expected=json.loads((ROOT/'vendor/legacy_g2/results_G2.json').read_text())
    rows=[]
    for condition,nudge in [('GRACE',.25),('LOVE',0.),('GRACE_LOVE',.25),('GRACE_LOVE_NODWELL',.25)]:
        first,last=legacy.run(condition,.02,nudge)
        measured=float(legacy.crossed(first,last).mean())
        key=f'{condition}|0.02|{nudge}'
        ref=expected['cells'][key]['p_cross']
        rows.append({'condition':condition,'measured':measured,'archived':ref,'exact_match':measured==ref})
        print('legacy anchor',condition,measured,flush=True)
    return {'rows':rows,'cpu_ns':time.process_time_ns()-start,'all_match':all(r['exact_match'] for r in rows)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=ROOT/'evidence/run')
    args=parser.parse_args()
    if args.out.exists() and any(args.out.iterdir()):
        raise SystemExit('Output is not empty. Choose a new directory.')
    args.out.mkdir(parents=True,exist_ok=True)
    lock=freeze_check(); config=json.loads((ROOT/'protocol.json').read_text())
    audits=source_audits()
    started_cpu,started_wall=time.process_time_ns(),time.perf_counter_ns()
    cases,histories,setup_cpu=build_cases(config)
    save(args.out/'cases.json',cases)
    np.savez_compressed(args.out/'histories.npz',truncated=histories)
    cues=np.asarray([case['cues'] for case in cases])
    settings=dict(config['dynamics'])
    noise,noise_meta=make_noise(cases,settings['dt'],config)
    subset=[i for i,c in enumerate(cases) if c['seed'] in config['sensitivity_test_seeds']]
    small_cases=[cases[i] for i in subset]; small_cues=cues[subset]; small_noise=noise[:,subset]
    selected_traces=[i for i,c in enumerate(cases) if c['seed'] in (0,1000) and c['signal_count_setting']==115]
    metadata={'freeze_sha256':lock,'python':platform.python_version(),'numpy':np.__version__,
              'scipy':scipy.__version__,'platform':platform.platform(),'source_audits':audits,
              'setup_cpu_ns':setup_cpu,'primary_noise':noise_meta,'cases':len(cases),
              'calibration_cases':sum(c['split']=='calibration' for c in cases),
              'test_cases':sum(c['split']=='test' for c in cases),'runs':[]}
    with (args.out/'dynamics.jsonl').open('w') as out:
        for arm in config['models']:
            results,work,trace,times=simulate(arm,cues,noise,settings,selected_traces)
            np.savez_compressed(args.out/f'trace_PRIMARY_{arm}.npz',states=trace,times=times,case_indices=selected_traces)
            for case,result in zip(cases,results):
                out.write(canonical({'config':'PRIMARY','arm':arm,'case_id':case['id'],**result}).decode()+'\n')
            metadata['runs'].append({'config':'PRIMARY','arm':arm,'noise_sha256':noise_meta['noise_sha256'],**work})
            print('PRIMARY',arm,'complete',flush=True)
        # The sensitivities keep the primary calibration policy; no test threshold is trained.
        for sensitivity in config['sensitivities']:
            varied={**settings,**{k:v for k,v in sensitivity.items() if k not in ('name','shuffle')}}
            name=sensitivity['name']; these_cues=small_cues.copy()
            if sensitivity.get('shuffle'):
                groups={}
                for j,case in enumerate(small_cases):
                    groups.setdefault((case['seed'],case['signal_count_setting']),[]).append(j)
                for (seed,count),indices in groups.items():
                    shift=1+(seed+count)%3
                    these_cues[indices]=small_cues[np.roll(indices,shift)]
            if varied['dt']!=settings['dt']:
                these_noise,sm=make_noise(small_cases,varied['dt'],config)
            else:
                these_noise=small_noise
                sm={'noise_sha256':hashlib.sha256(these_noise.tobytes()).hexdigest(),
                    'normal_draws':int(2*these_noise.size),'noise_cpu_ns':0}
            save(args.out/f'input_{name}.json',{'case_ids':[c['id'] for c in small_cases],
                                              'cues':these_cues.tolist(),'settings':varied,'noise':sm})
            for arm in config['models']:
                results,work,_,_=simulate(arm,these_cues,these_noise,varied,[])
                for case,result in zip(small_cases,results):
                    out.write(canonical({'config':name,'arm':arm,'case_id':case['id'],**result}).decode()+'\n')
                metadata['runs'].append({'config':name,'arm':arm,'noise_sha256':sm['noise_sha256'],**work})
                print(name,arm,'complete',flush=True)
            if varied['dt']!=settings['dt']:
                del these_noise
    metadata['legacy_anchor']=legacy_anchor()
    metadata['run_cpu_ns']=time.process_time_ns()-started_cpu
    metadata['run_wall_ns']=time.perf_counter_ns()-started_wall
    save(args.out/'run_metadata.json',metadata)
    print(json.dumps({k:metadata[k] for k in ['cases','calibration_cases','test_cases','run_cpu_ns','run_wall_ns']},indent=2))


if __name__=='__main__':
    main()
