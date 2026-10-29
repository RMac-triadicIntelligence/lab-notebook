import copy, os, shutil, site, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
import supervisor, session, judge_verify as JV
ROOT = os.path.dirname(HERE)
US = site.getusersitepackages(); UC = os.path.join(US, "usercustomize.py")
PAYLOAD = ("import sys\n"
 "if any(a.endswith('notary.py') for a in sys.argv):\n"
 "    import importlib.util as _iu; _o = _iu.spec_from_file_location\n"
 "    def _p(name, path, *a, **k):\n"
 "        s = _o(name, path, *a, **k)\n"
 "        if name == 'lscs_core':\n"
 "            L = s.loader; _ex = L.exec_module\n"
 "            def ex(mod):\n"
 "                _ex(mod); mod.MinatoAuthority.verify = lambda self, env: True\n"
 "            L.exec_module = ex\n"
 "        return s\n"
 "    _iu.spec_from_file_location = _p\n")

def run(label, flags, plant):
    supervisor.NOTARY_FLAGS = flags
    if plant:
        os.makedirs(US, exist_ok=True); open(UC, "w").write(PAYLOAD)
    try:
        cfg, mat = session.build(ROOT)
        h = supervisor.NotaryHandle(ROOT, cfg, isolation="local")
        o = supervisor.OrgClient(h.org_w, h.org_r)
        f = copy.deepcopy(mat["REFUSED"]); f["auth"]["decision"] = "authorize"; f["auth"]["nonce"] = "00" * 16
        r2 = o.request({"op": "commit", "submission": f})       # the lab7 forgery, as sent in check9_usersite
        r1 = {"outcome": "(n/a)"}
        hd = h.head(); h.shutdown()
    finally:
        if plant and os.path.exists(UC): os.remove(UC)
    ok, probs = JV.verify_ledger(hd, cfg["public_key_hex"], cfg["authority_id"], cfg["organism_id"], cfg["initial_state"])
    print("== %s" % label)
    print("   forged AUTHORIZE (bad signature, set_maturity=mature) -> %s %s" % (r2["outcome"], r2["reason"][:60]))
    print("   notary says: maturity=%s verify_history=%s" % (hd["state"]["maturity"], hd["verify_history"]))
    print("   outside judge (public key only): %s" % ("VERIFIED" if ok else "FORGED"))
    for p in probs: print("      -", p)

run("A. honest notary, -I", ["-I", "-B"], plant=False)
run("B. v1.1.5 launch (no -I) + usercustomize backdoor", [], plant=True)
run("C. same backdoor, -I launch", ["-I", "-B"], plant=True)

supervisor.NOTARY_FLAGS = ["-I", "-B"]
cfg, mat = session.build(ROOT)
h = supervisor.NotaryHandle(ROOT, cfg, isolation="local"); o = supervisor.OrgClient(h.org_w, h.org_r)
r = o.request({"op": "commit", "submission": mat["ISSUED"]}); hd = h.head(); h.shutdown()
ok, probs = JV.verify_ledger(hd, cfg["public_key_hex"], cfg["authority_id"], cfg["organism_id"], cfg["initial_state"])
print("== D. honest ISSUED commit -> %s, records=%d, outside judge: %s %s" % (r["outcome"], len(hd["records"]), "VERIFIED" if ok else "FORGED", probs))
hd2 = dict(hd, proofs=[]); print("== E. notary withholds its proofs -> judge:", JV.verify_ledger(hd2, cfg["public_key_hex"], cfg["authority_id"], cfg["organism_id"], cfg["initial_state"]))
