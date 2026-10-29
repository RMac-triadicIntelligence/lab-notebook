#!/usr/bin/env python3
"""Independent F1-F4 verdicts (Chief of Staff review, 2026-10-19). Steps follow ChatGPT round-5
probes; verdict = PASS when the bug does NOT reproduce. Usage: f1_f4_repro.py <candidate.py> <falsify.py>"""
import importlib.util, json, sys, tempfile
from pathlib import Path
def load(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); sys.modules[n] = m; s.loader.exec_module(m); return m
K = load(sys.argv[1], "cand"); H = load(sys.argv[2], "harn")
def apply(s, o, r, **kw): return s.authorize_and_apply(r["proposal_id"], o.sign_proposal(r["payload_to_sign"]), **kw)
def oc(f):
    try: return ("ok", f())
    except Exception as e: return ("err", type(e).__name__)
def disk(s): return json.loads(s._state_path().read_text())["checkpoint"]["sequence"]
def wit(o, s): return K.OwnerWitness(o.witness.path).ledger[s.organism_id]["sequence"]
def F1(d):
    s, o = H.born(K, d); x = H.propose(s, "verbosity"); y = H.propose(s, "verbosity")
    o.answer(s, y["proposal_id"], "no"); s.record_owner_answer(y["proposal_id"], "yes", "forged")
    apply(s, o, x); a = oc(lambda: o.attest(s))
    return a[0] == "err" and wit(o, s) == 0, f"attest={a} witness={wit(o,s)}"
def F2(d):
    s, o = H.born(K, d); apply(s, o, H.propose(s, "verbosity")); real = s._save
    def fail(*a, **k): raise OSError("inj")
    s._save = fail; oc(lambda: o.attest(s)); s._save = real
    au = oc(lambda: o.audit(s)); w = wit(o, s); dk = disk(s)
    return w == 0 and dk == 0 and au[0] == "err", f"audit={au} witness={w} disk={dk}"
def F3(d):
    s, o = H.born(K, d); st = K.HumbleSeed(s.data_dir); st.load(); apply(s, o, H.propose(s, "verbosity"))
    real = o.witness.commit
    def fail(cp): raise OSError("inj")
    o.witness.commit = fail; oc(lambda: o.attest(s)); o.witness.commit = real
    oc(lambda: o.audit(st)); w = wit(o, s); dk = disk(s)
    return w == 1 and dk == 1, f"after stale audit: witness={w} disk={dk}"
def F4(d):
    s, o = H.born(K, d); r = H.propose(s, "verbosity"); res = oc(lambda: apply(s, o, r, annotation="a"*2001))
    pend = r["proposal_id"] in s.pending; at = oc(lambda: o.attest(s)); ld = oc(K.HumbleSeed(s.data_dir).load)
    applied = res[0] == "ok" and res[1] is not None and res[1].get("status") == "applied"
    return (not applied) and at[0] == "ok" and ld[0] == "ok", f"apply={res if not isinstance(res[1],dict) else res[1].get('status')} pending={pend} attest={at[0]} reload={ld[0]}"
for f in (F1, F2, F3, F4):
    with tempfile.TemporaryDirectory() as t:
        try: ok, info = f(Path(t) / "c")
        except Exception as e: ok, info = False, f"probe crashed: {type(e).__name__}: {e}"
        print(f.__name__, "PASS(fixed)" if ok else "FAIL(bug present)", info)
