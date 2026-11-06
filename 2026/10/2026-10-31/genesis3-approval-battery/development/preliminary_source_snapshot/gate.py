"""New experimental admission wrapper. This is NOT the canonical v0.7 kernel."""
import base64, copy, math, unicodedata
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from common import canonical,digest,approval_body
CONTROLS=("key_scope","step_bound","range_bound","signature","dual_control","policy_binding","expiry","state_binding","nonce_replay","exact_types")
REQUEST_FIELDS={"request_id","policy_hash","prior_state_hash","sequence","key","value","nonce","expires_at","evidence_hash"}
@dataclass(frozen=True)
class Controls:
    disabled: str|None=None
    coupled: bool=False
    def on(self,name): return name!=self.disabled
class Gate:
    def __init__(self,policy,registry,controls=None,disabled_set=()):
        self.policy=copy.deepcopy(policy);self.registry=copy.deepcopy(registry)
        self.controls=controls or Controls();self.disabled_set=frozenset(disabled_set)
        self.values=copy.deepcopy(policy["initial_state"]);self.sequence=0;self.consumed=set()
    def on(self,name):return self.controls.on(name) and name not in self.disabled_set
    def snapshot(self):
        return {"values":copy.deepcopy(self.values),"sequence":self.sequence,"consumed":sorted(self.consumed)}
    def state_hash(self):return digest(self.snapshot())
    def request(self,nonce="n0",key="verbosity",value=250,expires_at=10,evidence_hash=None):
        return {"request_id":"request/"+nonce,"policy_hash":digest(self.policy),"prior_state_hash":self.state_hash(),
                "sequence":self.sequence,"key":key,"value":value,"nonce":nonce,"expires_at":expires_at,"evidence_hash":evidence_hash or digest([])}
    def submit(self,request,approvals,now=5):
        before=self.snapshot()
        def done(code,applied=False):
            return {"request":copy.deepcopy(request),"approvals":copy.deepcopy(approvals),"now":now,
                    "before":before,"after":self.snapshot(),"code":code,"applied":applied}
        if not isinstance(request,dict) or set(request)!=REQUEST_FIELDS:return done("closed_schema")
        if any(type(request[k]) is not str for k in ("request_id","policy_hash","prior_state_hash","key","nonce","evidence_hash")):return done("envelope_types")
        if type(request["sequence"]) is not int or type(request["expires_at"]) is not int:return done("envelope_types")
        raw=request["key"];key=unicodedata.normalize("NFKC",raw).strip().casefold()
        if key not in self.values:return done("unknown_storage_field")
        if self.on("key_scope") and (raw!=key or key not in self.policy["allowed_keys"]):return done("key_scope")
        value=request["value"]
        if self.on("exact_types") and type(value) is not int:return done("exact_types")
        if not isinstance(value,(int,float)) or not math.isfinite(value):return done("unsupported_number")
        if self.on("range_bound") and not self.policy["minimum"]<=value<=self.policy["maximum"]:return done("range_bound")
        # In the clean gate the step check is INDEPENDENT of key-scope validation.
        step_active=self.on("step_bound")
        # Deliberately coupled calibration only; not used by the clean gate.
        if self.controls.coupled:step_active=step_active and self.on("key_scope")
        if step_active and abs(value-self.values[key])>self.policy["maximum_step"]:return done("step_bound")
        if self.on("policy_binding") and request["policy_hash"]!=digest(self.policy):return done("policy_binding")
        if self.on("expiry") and now>request["expires_at"]:return done("expiry")
        if self.on("nonce_replay") and request["nonce"] in self.consumed:return done("nonce_replay")
        if self.on("state_binding") and (request["sequence"]!=self.sequence or request["prior_state_hash"]!=self.state_hash()):return done("state_binding")
        if not isinstance(approvals,list) or not approvals:return done("missing_approval")
        owners=[]
        for a in approvals:
            if not isinstance(a,dict) or set(a)!={"owner","signature"} or type(a["owner"]) is not str:return done("approval_schema")
            if a["owner"] not in self.registry:return done("unknown_owner")
            owners.append(a["owner"])
            if self.on("signature"):
                try:
                    sig=base64.b64decode(a["signature"],validate=True)
                    Ed25519PublicKey.from_public_bytes(base64.b64decode(self.registry[a["owner"]],validate=True)).verify(sig,canonical(approval_body(request)))
                except Exception:return done("signature")
        if self.on("dual_control") and (len(owners)!=len(set(owners)) or set(owners)!=set(self.policy["required_signers"])):return done("dual_control")
        self.values[key]=value;self.sequence+=1;self.consumed.add(request["nonce"])
        return done("applied",True)

