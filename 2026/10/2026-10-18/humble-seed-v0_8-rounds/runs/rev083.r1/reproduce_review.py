#!/usr/bin/env python3
"""Reproduce execution and probes from this archive; requires Python + cryptography.
Example: python3 -I reproduce_review.py --output /tmp/hs083_rerun
The shipped harness is expected to exit 1. This wrapper records that fact.
"""
import argparse,hashlib,json,pathlib,shutil,subprocess,sys,tempfile,zipfile
HERE=pathlib.Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=pathlib.Path);a=ap.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if list(out.iterdir()):raise SystemExit('Choose an empty output directory to preserve earlier evidence.')
records=[]
def run(name,argv,cwd=None,expect=0):
    p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True)
    (out/(name+'_stdout.txt')).write_text(p.stdout);(out/(name+'_stderr.txt')).write_text(p.stderr)
    records.append({'name':name,'command':[str(x) for x in argv],'exit_code':p.returncode,'expected_exit_code':expect})
    print(name+': exit '+str(p.returncode)+' (expected '+str(expect)+')')
    return p.returncode==expect
with tempfile.TemporaryDirectory(prefix='hs083_review_rerun_') as td:
    tmp=pathlib.Path(td)
    with zipfile.ZipFile(HERE/'source'/'Claudehumble_seed_v0_8_3_candidate.zip') as z:
        for info in z.infolist():
            target=(tmp/info.filename).resolve()
            if not target.is_relative_to(tmp.resolve()):raise SystemExit('Unsafe zip member')
        z.extractall(tmp)
    root=tmp/'humble_seed_v0_8_3_candidate';candidate=root/'humble_seed_v0_8_3_candidate.py'
    ok=run('harness',[sys.executable,'-I','falsify_v0_8_3.py'],root,1)
    shutil.copy2(root/'RESULTS_v0_8_3.json',out/'RESULTS_v0_8_3_reproduced.json')
    ok=run('independent_probes',[sys.executable,'-I',str(HERE/'code'/'independent_probes.py'),str(candidate),str(out)]) and ok
    ok=run('extra_mutants',[sys.executable,'-I',str(HERE/'code'/'extra_mutants.py'),str(root),str(out)]) and ok
    ok=run('T26_diagnostic',[sys.executable,'-I',str(root/'diagnostic_T26_v0_8_3.py'),str(root)]) and ok
    ok=run('corrected_answer',[sys.executable,'-I',str(root/'regression_corrected_answer_attest.py'),str(candidate)]) and ok
(out/'rerun_commands.json').write_text(json.dumps(records,indent=2)+'\n')
sys.exit(0 if ok else 1)
