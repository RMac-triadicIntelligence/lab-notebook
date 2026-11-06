"""Adapter to the byte-identical v0.7 source, with deterministic TEST-only providers."""
import base64,copy,hashlib,importlib.util,itertools,json,sys,tempfile,types,uuid
from pathlib import Path
from common import ROOT,canonical,private
def load_kernel(label):
    name="_genesis3_native_"+hashlib.sha256(label.encode()).hexdigest()[:16]
    spec=importlib.util.spec_from_file_location(name,ROOT/"inputs/humble_seed_v0_7.py")
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    counts=itertools.count();clock=types.SimpleNamespace(now=1000000.0)
    def token(n):return hashlib.shake_256((label+":"+str(next(counts))).encode()).hexdigest(n)
    m.time=types.SimpleNamespace(time=lambda:clock.now)
    m.uuid=types.SimpleNamespace(uuid4=lambda:uuid.UUID(token(16)))
    m.secrets=types.SimpleNamespace(token_hex=token)
    # Replace only the entropy provider in this private module. Native checks are untouched.
    m.Ed25519PrivateKey=types.SimpleNamespace(generate=lambda:private("native/"+label))
    return m,clock
class Native:
    def __init__(self,label):
        self.tmp=tempfile.TemporaryDirectory(prefix="genesis3_native_")
        self.m,self.clock=load_kernel(label)
        self.seed=self.m.HumbleSeed(Path(self.tmp.name)/"organism")
        self.organism_id,self.pem,cp=self.seed.hatch()
        self.owner=self.m.OwnerTool(self.pem,self.m.OwnerWitness(Path(self.tmp.name)/"witness.json"))
        assert self.owner.attest(self.seed,cp)
    def raw(self):return json.loads(self.seed._state_path().read_text())
    def normal(self,evidence=None):
        transcript="I prefer brief replies."
        if evidence is not None:transcript+=" Synthetic primary observations: "+json.dumps(evidence,sort_keys=True)
        reply=self.seed.dwell_or_propose("verbosity","preference",transcript)
        assert reply["status"]=="proposal"
        return self.seed.pending[reply["proposal_id"]]
    def large(self):
        return self.seed._issue_pending_proposal("verbosity",{"verbosity":0.0},{"preference":1.0},["Synthetic direct-helper fixture."])
    def apply_record(self,p,attempt=True,kind="normal",signature=None):
        original_payload=p.payload_to_sign
        if signature is None and attempt:signature=self.owner.sign_proposal(original_payload)
        before=self.raw();cp=None
        if attempt:cp=self.seed.authorize_and_apply(p.proposal_id,signature or "")
        applied=cp is not None
        attested=False;audited=False;loaded=False
        if applied:
            attested=self.owner.attest(self.seed,cp)
            reloaded=self.m.HumbleSeed(self.seed.data_dir);reloaded.load()
            audited=self.owner.audit(reloaded);loaded=True
        after=self.raw()
        return {"kind":kind,"attempted":attempt,"applied":applied,"original_payload":original_payload,
                "mutation_signature":signature,"public_key":self.seed.birth.public_key_b64,
                "before":before,"after":after,"attested":attested,"audited":audited,"reloaded":loaded,
                "checkpoint_payload":self.m.HumbleSeed.checkpoint_payload(self.seed.checkpoint),
                "checkpoint_signature":self.seed.checkpoint_sig}
    def close(self):
        # The exported evidence retains no OS paths or private key material.
        self.tmp.cleanup()
def semantic_native(label,admitted,evidence):
    n=Native(label)
    try:return n.apply_record(n.normal(evidence),attempt=admitted)
    finally:n.close()
def probes():
    out=[]
    for name in ("normal","no_signature","wrong_signature","payload_changed","expired","stale","exact_replay","private_large_step","unsupported_but_signed"):
        n=Native("probe/"+name)
        try:
            primary=[{"source":"s1","supports":True}] if name=="unsupported_but_signed" else [{"source":"s1","supports":True},{"source":"s2","supports":True}]
            p=n.large() if name=="private_large_step" else n.normal(primary)
            sig=n.owner.sign_proposal(p.payload_to_sign)
            preparation=[]
            if name=="no_signature":sig=""
            if name=="wrong_signature":sig=base64.urlsafe_b64encode(private("wrong_native_owner").sign(p.payload_to_sign.encode())).decode()
            if name=="payload_changed":p.change["verbosity"]=0.125
            if name=="expired":n.clock.now=p.expires_at+1
            if name=="stale":
                n.seed._append_trace({"event":"dwelling","timestamp":n.clock.now,"reason":"synthetic intervening event"});n.seed._save()
            if name=="exact_replay":
                preparation.append(n.apply_record(p,signature=sig))
            result=n.apply_record(p,kind=name,signature=sig)
            expected=name in ("normal","private_large_step","unsupported_but_signed")
            out.append({"name":name,"expected_applied":expected,"primary_evidence":primary,"record":result,"preparation":preparation})
        finally:n.close()
    return out

