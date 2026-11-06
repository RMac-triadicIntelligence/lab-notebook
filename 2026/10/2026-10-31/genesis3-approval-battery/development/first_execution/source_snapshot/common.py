"""Shared serialization and PUBLIC TEST signing fixtures. Never use these keys outside tests."""
from pathlib import Path
import base64, hashlib, json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
ROOT = Path(__file__).resolve().parent
def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def digest(obj): return hashlib.sha256(canonical(obj)).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def write(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def private(owner):
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(("PUBLIC GENESIS3 TEST KEY:"+owner).encode()).digest())
def public(owner):
    return base64.b64encode(private(owner).public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
def approval_body(request):
    return {"domain":"genesis3-approval-v1","proposal_hash":digest(request),"decision":"APPROVE"}
def approve(request,owner):
    return {"owner":owner,"signature":base64.b64encode(private(owner).sign(canonical(approval_body(request)))).decode()}
def public_registry(): return {k:public(k) for k in ("owner_a","owner_b")}

