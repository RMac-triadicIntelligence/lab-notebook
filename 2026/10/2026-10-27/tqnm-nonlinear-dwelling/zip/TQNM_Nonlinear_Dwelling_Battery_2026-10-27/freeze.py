#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,datetime
root=Path(__file__).resolve().parent
dest=root/'FREEZE.json'
if dest.exists():
    raise SystemExit('Already frozen; do not overwrite.')
names=['protocol.json','PROVENANCE.json','battery.py','analyze.py','verify.py','freeze.py']
names+=sorted(str(p.relative_to(root)) for p in (root/'vendor').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
obj={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'registration':'Local pre-execution lock, not external preregistration.',
     'sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}}
dest.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
print('FROZEN',hashlib.sha256(dest.read_bytes()).hexdigest())
