#!/usr/bin/env python3
"""Claims battery for Humble Seed v0.8.7: a scaffold for checking whether each documented claim
in the candidate's docstring is accurate as stated.

The claims are in CLAIMS.json, quoted verbatim from the docstring. For each claim there is one
check_<ID>(d) function below. Fill it in, so that it returns:
    {"verdict": "HOLDS" | "HOLDS WITH CAVEATS" | "WRONG" | "NOT TESTED",
     "evidence": <anything JSON-serializable: what you ran and what it returned>}
Open questions QA, QB and QC have check_QA, check_QB and check_QC; a "verdict" there is "FOUND" or "NOT FOUND".
Anything else you find goes in a function named extra_<name>(d); it is run and reported too.

Each function gets a fresh, empty temporary directory d (a pathlib.Path).
Run:  python3 -I claims_battery_v0_8_7.py
Output: a table on stdout, and CLAIMS_RESULTS_v0_8_7.json next to this file.
"""
import importlib.util, json, os, stat, subprocess, sys, tempfile, threading, time, traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAND = HERE / "humble_seed_v0_8_7_candidate.py"
CLAIMS = json.loads((HERE / "CLAIMS.json").read_text())


def _load(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[alias] = m          # needed: the candidate defines dataclasses
    spec.loader.exec_module(m)
    return m


K = _load(CAND, "hs087")

# ---------------------------------------------------------------------------
# Helpers (use, change or ignore them; nothing below is part of the candidate)
# ---------------------------------------------------------------------------
PREF = "I always prefer shorter answers"   # the stub interpreter reads this as a preference -> a proposal
PLAIN = "hmm ok"                           # read as unclear -> the organism dwells (a non-authorizing event)


def born(d):
    """A hatched organism whose genesis the owner has attested. Returns (seed, owner)."""
    seed = K.HumbleSeed(d / "org")
    _, pem, _ = seed.hatch()
    owner = K.OwnerTool(pem, K.OwnerWitness(d / "witness.json"))
    assert owner.attest(seed) is True
    return seed, owner


def reading(seed, category="verbosity"):
    r = seed.dwell_or_propose(category, "evt", PREF)
    assert r["status"] == "proposal", r["status"]
    return r


def apply(seed, owner, r, attest=True):
    """Owner signs the reading; organism applies it; optionally the owner attests the result."""
    res = seed.authorize_and_apply(r["proposal_id"], owner.sign_proposal(r["payload_to_sign"]))
    assert res is not None, seed.trace[-1]
    if attest:
        assert owner.attest(seed) is True
    return res


def dwell(seed, category="formality"):
    r = seed.dwell_or_propose(category, "evt", PLAIN)
    assert r["status"] == "dwelling", r["status"]
    return r


def reload(seed_or_dir):
    """A new organism object loaded from the saved file (raises if the file does not load)."""
    data_dir = seed_or_dir.data_dir if hasattr(seed_or_dir, "data_dir") else Path(seed_or_dir)
    f = K.HumbleSeed(data_dir)
    f.load()
    return f


def saved(seed):
    """The organism's saved file, parsed."""
    return json.loads(seed._state_path().read_text())


def reopen_owner(owner):
    """A new owner session over the same witness file and key."""
    return K.OwnerTool(owner._pem, K.OwnerWitness(owner.witness.path))


def witness_seq(owner, seed):
    return K.OwnerWitness(owner.witness.path).ledger[seed.organism_id]["sequence"]


def intent_pending(owner, seed):
    return K.OwnerWitness(owner.witness.path).pending_for(seed.organism_id) is not None


def outcome(fn):
    """Run fn(); return what it returned or what it raised, as data."""
    try:
        return {"returned": fn()}
    except Exception as e:
        return {"exception": type(e).__name__, "message": str(e)}


LOADER = ("import importlib.util, sys\n"
          "spec = importlib.util.spec_from_file_location('hs087', sys.argv[1])\n"
          "K = importlib.util.module_from_spec(spec); sys.modules['hs087'] = K; spec.loader.exec_module(K)\n")


def python_subprocess(code, *args, timeout=300, wait=True):
    """Run `LOADER + code` in a separate Python process. Inside it, K is the candidate and
    sys.argv[2:] are *args (as strings). With wait=False, returns the Popen object."""
    cmd = [sys.executable, "-I", "-c", LOADER + code, str(CAND), *map(str, args)]
    if not wait:
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return {"rc": p.returncode, "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:]}


NOT_TESTED = {"verdict": "NOT TESTED", "evidence": None}


# ---------------------------------------------------------------------------
# Worked example
# ---------------------------------------------------------------------------

def check_U1(d):
    """If a save fails and the saved generation cannot be re-read, the object refuses every operation
    until it is reloaded. (Example: one failure mode, one operation; a full check would try more.)"""
    seed, owner = born(d)
    real_fsync, real_gen = K.os.fsync, seed._saved_generation
    fired = {"fsync": False, "reread": False}
    def fsync(fd):
        if not fired["fsync"] and stat.S_ISDIR(os.fstat(fd).st_mode) and saved(seed)["checkpoint"]["sequence"] == 1:
            fired["fsync"] = True
            raise OSError("injected: directory fsync failed after the replace")
        return real_fsync(fd)
    def gen():
        if fired["fsync"] and not fired["reread"]:
            fired["reread"] = True
            raise OSError("injected: generation re-read failed")
        return real_gen()
    K.os.fsync, seed._saved_generation = fsync, gen
    try:
        first = outcome(lambda: owner.attest(seed))
    finally:
        K.os.fsync = real_fsync
        del seed._saved_generation
    nxt = outcome(lambda: dwell(seed))
    after_reload = outcome(lambda: dwell(reload(seed)))
    ok = (fired["fsync"] and fired["reread"] and first.get("exception") == "OSError"
          and nxt.get("exception") == "StaleOrganism" and "unusable" in nxt.get("message", "")
          and "returned" in after_reload)
    return {"verdict": "HOLDS" if ok else "WRONG",
            "evidence": {"injected": fired, "attest": first, "next_dwell_same_object": nxt,
                         "dwell_after_reload": after_reload}}


# ---------------------------------------------------------------------------
# Claims to check (texts from CLAIMS.json). Replace `return NOT_TESTED`.
# ---------------------------------------------------------------------------

def check_Q1(d): return NOT_TESTED
def check_Q2(d): return NOT_TESTED
def check_Q3(d): return NOT_TESTED
def check_Q4(d): return NOT_TESTED
def check_Q5(d): return NOT_TESTED
def check_U2(d): return NOT_TESTED
def check_G1(d): return NOT_TESTED
def check_A1(d): return NOT_TESTED
def check_R1(d): return NOT_TESTED
def check_R2(d): return NOT_TESTED
def check_R20(d): return NOT_TESTED
def check_R31a(d): return NOT_TESTED
def check_R31b(d): return NOT_TESTED
def check_R33(d): return NOT_TESTED
def check_R35a(d): return NOT_TESTED
def check_R35b(d): return NOT_TESTED
def check_R36(d): return NOT_TESTED

# Open questions: return {"verdict": "FOUND" | "NOT FOUND" | "NOT TESTED", "evidence": ...}
def check_QA(d): return NOT_TESTED
def check_QB(d): return NOT_TESTED
def check_QC(d): return NOT_TESTED

# Anything else: define extra_<name>(d) returning {"verdict": <your label>, "evidence": ...}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
CLAIM_VERDICTS = {"HOLDS", "HOLDS WITH CAVEATS", "WRONG", "NOT TESTED"}
QUESTION_VERDICTS = {"FOUND", "NOT FOUND", "NOT TESTED"}


def _run(fn):
    with tempfile.TemporaryDirectory(prefix="hs087_claims_") as t:
        d = Path(t) / "case"
        d.mkdir()
        t0 = time.time()
        try:
            r = fn(d)
        except Exception as e:
            r = {"verdict": "ERROR", "evidence": f"{type(e).__name__}: {e}",
                 "traceback": traceback.format_exc()[-2000:]}
        r["seconds"] = round(time.time() - t0, 2)
        return r


def main():
    results = {"python": sys.version.split()[0], "candidate": CAND.name, "claims": {}, "open_questions": {}, "extra": {}}
    try:
        import cryptography
        results["cryptography"] = cryptography.__version__
    except Exception:
        pass
    rows = []
    for section, items, allowed in (("claims", CLAIMS["claims"], CLAIM_VERDICTS),
                                    ("open_questions", CLAIMS["open_questions"], QUESTION_VERDICTS)):
        for c in items:
            fn = globals().get(f"check_{c['id']}")
            r = _run(fn) if fn else {"verdict": "ERROR", "evidence": f"no check_{c['id']} defined"}
            if r.get("verdict") not in allowed | {"ERROR"}:
                r["verdict_not_in_allowed_set"] = r.get("verdict")
            r["claim"] = c["text"]
            results[section][c["id"]] = r
            rows.append((c["id"], r.get("verdict")))
    for name in sorted(n for n in globals() if n.startswith("extra_") and callable(globals()[n])):
        r = _run(globals()[name])
        results["extra"][name] = r
        rows.append((name, r.get("verdict")))
    out = HERE / "CLAIMS_RESULTS_v0_8_7.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True, default=repr))
    print(f"Humble Seed v0.8.7 claims battery  (Python {results['python']}, cryptography {results.get('cryptography')})")
    for cid, v in rows:
        print(f"  {cid:<28} {v}")
    print(f"written {out.name}")


if __name__ == "__main__":
    main()
