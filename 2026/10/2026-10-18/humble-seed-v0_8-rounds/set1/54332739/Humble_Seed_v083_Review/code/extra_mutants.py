#!/usr/bin/env python3
"""Run the shipped 48 tests against independently designed metadata mutants.
This calls run_suite directly, outside frozen scoring; it does not alter DECLARED.
Usage: python3 -I extra_mutants.py PACKAGE_DIRECTORY OUTPUT_DIRECTORY
"""
import importlib.util,json,pathlib,sys,tempfile
root=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('extra_mutant_harness',root/'falsify_v0_8_3.py')
H=importlib.util.module_from_spec(spec);sys.modules[spec.name]=H;spec.loader.exec_module(H)
K=H.load_module(H.CANDIDATE,'extra_mutant_baseline');base=H.run_suite(K)
passing={n for n,r in base.items() if r['status']=='PASS'}
edits={
 'XM1_invalid_authorized_at':('authorized_at=self.clock(), signature_b64=signature_b64,','authorized_at="not a timestamp", signature_b64=signature_b64,'),
 'XM2_forged_owner_note':('prior_character_snapshot=prior, note=owner_note,','prior_character_snapshot=prior, note={"forged": "owner approved everything"},'),
 'XM3_inconsistent_event_timestamp':('"timestamp": record.authorized_at,','"timestamp": -123456789.0,'),
}
result={}
for name,(old,new) in edits.items():
    src=H.CANDIDATE.read_text();assert src.count(old)==1
    # Keep exact mutant source in the evidence archive.
    mutant_path=out/(name+'.py');mutant_path.write_text(src.replace(old,new))
    M=H.load_module(mutant_path,name);res=H.run_suite(M)
    fail=sorted(n for n in passing if res[n]['status']=='FAIL')
    error=sorted(n for n in passing if res[n]['status']=='ERROR')
    status='KILLED' if fail else ('CRASHED' if error else 'SURVIVES')
    result[name]={'status':status,'new_failures':fail,'new_errors':error,'edit':[old,new],
                  'all_test_results':res}
    print(name+': '+json.dumps({'status':status,'baseline_passes':len(passing),'new_failures':fail,'new_errors':error},sort_keys=True))
(out/'extra_mutant_results.json').write_text(json.dumps({'baseline':base,'mutants':result},indent=2,sort_keys=True)+'\n')
