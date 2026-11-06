"""Fixture construction. Observer expectations are not supplied to gate/reviewer code."""
import copy
from common import approve,public_registry
from gate import Gate,Controls,CONTROLS
NAMES=("valid",)+CONTROLS+("no_approval","duplicate_owner","unknown_owner","unknown_field","exact_replay","refusal_then_valid")
def signed(q,owners=("owner_a","owner_b")):return [approve(q,x) for x in owners]
def scenario(name,policy,controls=None,disabled_set=()):
    g=Gate(policy,public_registry(),controls,disabled_set);history=[]
    def commit(q,a=None,now=5):
        e=g.submit(q,signed(q) if a is None else a,now);history.append(e);return e
    q=g.request(nonce=name)
    if name=="key_scope":q=g.request(nonce=name,key="protected_flag",value=750)
    elif name=="step_bound":q=g.request(nonce=name,value=0)
    elif name=="range_bound":
        commit(g.request(nonce="warm1",value=750))
        commit(g.request(nonce="warm2",value=1000))
        q=g.request(nonce=name,value=1125)
    elif name=="policy_binding":q["policy_hash"]="f"*64
    elif name=="expiry":q["expires_at"]=4
    elif name=="state_binding":
        q=g.request(nonce=name,value=250)
        commit(g.request(nonce="warm",value=250))
    elif name=="nonce_replay":
        commit(g.request(nonce=name,value=250))
        q=g.request(nonce=name,value=0)
    elif name=="exact_types":q["value"]=500.0
    elif name=="unknown_field":q["unrecognized"]="should refuse"
    elif name=="exact_replay":
        commit(q)
    if name=="signature":
        a=signed(q);a[1]["signature"]="AA==" # valid encoding, invalid Ed25519 signature
    elif name=="dual_control":a=signed(q,("owner_a",))
    elif name=="no_approval":a=[]
    elif name=="duplicate_owner":a=signed(q,("owner_a","owner_a"))
    elif name=="unknown_owner":a=signed(q,("owner_a","owner_c"))
    else:a=signed(q)
    if name=="refusal_then_valid":
        bad=signed(q);bad[0]["signature"]="AA==";commit(q,bad)
        q=g.request(nonce=name);a=signed(q)
    terminal=commit(q,a)
    expected=name in ("valid","refusal_then_valid")
    return {"name":name,"expected_applied":expected,"events":history,"applied":terminal["applied"]}
def suite(policy,controls=None,disabled_set=()):
    return [scenario(n,policy,controls,disabled_set) for n in NAMES]
def key_step_table(policy):
    rows=[]
    for key_on in (True,False):
        for step_on in (True,False):
            disabled=tuple(c for c,on in (("key_scope",key_on),("step_bound",step_on)) if not on)
            for alias in (False,True):
                for large in (False,True):
                    g=Gate(policy,public_registry(),disabled_set=disabled)
                    q=g.request(nonce="matrix",key=" VERBOSITY " if alias else "verbosity",value=0 if large else 250)
                    e=g.submit(q,signed(q))
                    expected=(not alias or not key_on) and (not large or not step_on)
                    rows.append({"key_on":key_on,"step_on":step_on,"alias":alias,"large":large,"expected_applied":expected,"event":e})
    return rows
def mutations(policy):
    base=suite(policy)
    variants=[]
    for control in CONTROLS:
        records=suite(policy,Controls(disabled=control))
        changed=[x["name"] for x,b in zip(records,base) if x["applied"]!=b["applied"]]
        variants.append({"disabled":control,"expected_changed":[control],"changed":changed,"records":records})
    coupled=suite(policy,Controls(disabled="key_scope",coupled=True))
    changed=[x["name"] for x,b in zip(coupled,base) if x["applied"]!=b["applied"]]
    return {"baseline":base,"variants":variants,"coupled":{"disabled":"key_scope","step_configured_on":True,
            "expected_changed":["key_scope","step_bound"],"changed":changed,"records":coupled},
            "key_step_table":key_step_table(policy)}

