"""Local source lock. Not a signature or an independently retained trust anchor."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
def source_paths():
    files=list(ROOT.glob("*.py"))+list(ROOT.glob("*.md"))+list(ROOT.glob("requirements.txt"))
    for name in ("inputs","spec","tools"):
        files.extend(p for p in (ROOT/name).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return sorted({p.relative_to(ROOT).as_posix() for p in files})
def state():return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths()}
def check_lock():
    saved=json.loads((ROOT/"SOURCE_LOCK.json").read_text())
    if saved!=state():raise RuntimeError("Source lock mismatch or file set changed")
    pre=json.loads((ROOT/"spec/PRE_IMPLEMENTATION.json").read_text())
    for name,wanted in pre.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=wanted:raise RuntimeError("Pre-implementation freeze changed: "+name)
    return True
if __name__=="__main__":
    p=ROOT/"SOURCE_LOCK.json"
    p.write_text(json.dumps(state(),sort_keys=True,indent=2)+"\n")
    check_lock()
    print("SOURCE_LOCK_SHA256",hashlib.sha256(p.read_bytes()).hexdigest())

