#!/usr/bin/env python3
"""Rerun the unchanged shipped harness, recording stdout, stderr and environment."""
import subprocess,sys,json,time,hashlib,platform
from pathlib import Path
import cryptography
root=Path(__file__).resolve().parents[1];pkg=root/'review_input/humble_seed_v0_8_4_candidate_BLIND';ev=root/'evidence';ev.mkdir(exist_ok=True)
checks=subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=pkg,capture_output=True,text=True)
(ev/'manifest_check.txt').write_text(checks.stdout+checks.stderr)
meta={'python':sys.version,'cryptography':cryptography.__version__,'platform':platform.platform(),'command':['python3','-I','falsify_v0_8_4.py'],'cwd':str(pkg),'manifest_exit_code':checks.returncode}
archive=root/'input/Claudehumble_seed_v0_8_4_candidate_BLIND.zip'
if archive.exists():meta['input_zip_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
t=time.monotonic()
with (ev/'harness_stdout.txt').open('w') as out,(ev/'harness_stderr.txt').open('w') as err:
 p=subprocess.run([sys.executable,'-I','falsify_v0_8_4.py'],cwd=pkg,stdout=out,stderr=err)
meta.update(exit_code=p.returncode,elapsed_seconds=time.monotonic()-t)
(ev/'environment.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2));print((ev/'harness_stdout.txt').read_text());sys.exit(p.returncode)
