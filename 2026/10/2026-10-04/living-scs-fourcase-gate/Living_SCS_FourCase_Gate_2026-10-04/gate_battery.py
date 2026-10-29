"""Four-case judge gate for Living SCS. Run:  python3 gate_battery.py
Drives the REAL v1.1.5 notary (candidate/v115) with REAL authority-signed envelopes, and runs three
judges through the acceptance list in ACCEPTANCE.md:
  LEGACY  - v1.1.5 judge_verify.verify_ledger (no clock, no head memory). Must FAIL cases 1 and 2.
  NAIVE   - expiry vs clock-now, head in memory only. CONTROL. Must FAIL case 3 or case 4.
  WITNESS - witness_judge.WitnessJudge. Passes only if it holds all four cases plus replay, crash, fallback.
"""
import copy, hashlib, json, os, shutil, sys, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
V115 = os.path.join(HERE, "candidate", "v115")
ROOT = os.path.join(HERE, "candidate")
sys.path.insert(0, V115); sys.path.insert(0, HERE)
os.chdir(V115)
import session, supervisor, judge_verify as JV          # noqa: E402  (v1.1.5, unchanged)
import witness_judge as WJ                              # noqa: E402

T0 = session.T0
INIT = session.INITIAL_STATE
spec = importlib.util.spec_from_file_location("lscs_core_gate", os.path.join(ROOT, "v114", "living_scs_v114", "core.py"))
m = importlib.util.module_from_spec(spec); sys.modules[spec.name] = m; spec.loader.exec_module(m)


# ------------------------------------------------------------------ material (test authority)
def build_material():
    """Same construction as session.build, plus a replay pair minted from the state after ISSUED.
    The harness plays the authority here (a test key); the judge and notary only ever see public material."""
    def to_json(obj):
        if isinstance(obj, m.MutationProposal):
            d = obj.unsigned_body(); d["evidence"] = [dict(e) for e in d["evidence"]]; return d
        if isinstance(obj, m.ConsolidationTrace):
            d = obj.body(); d["evidence_ids"] = list(d["evidence_ids"]); return d
        if isinstance(obj, m.AuthorizationEnvelope):
            d = obj.signed_body(); d["signature"] = obj.signature; return d
        raise TypeError(type(obj))
    priv = m.Ed25519PrivateKey.generate(); auth_id = "minato-" + os.urandom(4).hex()
    signer = m.MinatoAuthority(auth_id, priv); pub = signer.public_key_bytes()
    org = "organism-" + os.urandom(4).hex(); hk = os.urandom(32)
    eng = m.CommitEngine(org, INIT, m.MinatoAuthority.verifier_only(auth_id, priv.public_key()), m.TrustedClock(T0),
                         expected_authority_id=auth_id, expected_public_key=pub, history_key=hk)

    def mint(e, pid, mut, issued_at, expires_at, det=None, nonce=None):
        p = e.proposal_for_mutation(proposal_id=pid, mutation_type=mut["op"], mutation=mut,
                                    evidence=[m.EvidenceItem("ev-" + pid, "sensor://x/" + pid, T0 - 50, "drift_detector", "1.0", {"score": 0.91})],
                                    interpretation=m.Interpretation("basin", "1.3", {"r": "ok"}, 0.9, 0.8, 0.7, 0.9), created_at=issued_at)
        t = m.make_trace(p, trace_id="trace-" + pid, created_at=issued_at)
        a = signer.issue(t, p, decision=m.Decision.AUTHORIZE, determination_id=det or ("det-" + pid),
                         nonce=nonce or os.urandom(16).hex(), issued_at=issued_at, expires_at=expires_at)
        return {"proposal": to_json(p), "trace": to_json(t), "auth": to_json(a)}, (p, t, a)

    mat = {}
    mat["ISSUED"], objs = mint(eng, "p-issued", session.ISSUED_MUT, T0, T0 + 300)
    mat["EXPIRED"], _ = mint(eng, "p-old", session.EXPIRED_MUT, T0 - 1000, T0 - 10)
    eng.commit(*objs, reason="mint")  # advance the minting engine to the state after ISSUED
    state_after = copy.deepcopy(eng.state)
    n1, d1 = mat["ISSUED"]["auth"]["nonce"], mat["ISSUED"]["auth"]["determination_id"]
    mat["REPLAY_NONCE"], _ = mint(eng, "p-rn", {"op": "set", "path": ["personality", "note"], "value": "again"}, T0, T0 + 300, nonce=n1)
    mat["SECOND"], _ = mint(eng, "p-second", {"op": "set", "path": ["personality", "note"], "value": "second"}, T0, T0 + 300)
    mat["REPLAY_DET"], _ = mint(eng, "p-rd", {"op": "set", "path": ["personality", "note"], "value": "again2"}, T0, T0 + 300, det=d1)
    cfg = {"organism_id": org, "authority_id": auth_id, "public_key_hex": pub.hex(), "history_key_hex": hk.hex(),
           "initial_state": INIT, "clock_t0": T0}
    del signer, priv
    return cfg, mat, state_after


# ------------------------------------------------------------------ notary + judges
def notary_run(cfg, subs, clock_t0=None, initial_state=None, judge=None, judge_times=None):
    """Drive the REAL notary. If a judge is given, it witnesses after each commit (at commit time)."""
    c = dict(cfg)
    if clock_t0 is not None: c["clock_t0"] = clock_t0
    if initial_state is not None: c["initial_state"] = initial_state
    h = supervisor.NotaryHandle(ROOT, c, isolation="local"); o = supervisor.OrgClient(h.org_w, h.org_r)
    outs, wits = [], []
    for i, s in enumerate(subs):
        outs.append(o.request({"op": "commit", "submission": s}))
        if judge is not None:
            if judge_times: judge.clock.set(judge_times[i])
            wits.append(judge.witness(h.head()))
    head = h.head(); h.shutdown()
    return outs, wits, head


class Legacy:
    name = "LEGACY"
    def __init__(self, path, cfg, clock): self.cfg, self.clock = cfg, clock
    def witness(self, head): return []
    def verify(self, head):
        try:
            return JV.verify_ledger(head, self.cfg["public_key_hex"], self.cfg["authority_id"], self.cfg["organism_id"], INIT)
        except Exception as e:
            return None, ["CRASH %s: %s" % (type(e).__name__, e)]


def mk(kind, path, cfg, t):
    clock = WJ.JudgeClock(t)
    if kind == "LEGACY": return Legacy(path, cfg, clock)
    cls = WJ.WitnessJudge if kind == "WITNESS" else WJ.NaiveJudge
    return cls(path, cfg["public_key_hex"], cfg["authority_id"], cfg["organism_id"], INIT, clock)


def empty_head():
    return {"state": copy.deepcopy(INIT), "state_digest": m.sha256_hex(INIT), "verify_history": True, "records": [], "proofs": []}


def outcome(v, want, reason_word=None):
    ok, probs = v
    if ok is None:
        return {"verdict": "CRASH", "reasons": probs, "pass": False}
    if want == "accept":
        return {"verdict": "ACCEPT" if ok else "REFUSE", "reasons": probs, "pass": bool(ok)}
    hit = (not ok) and any(reason_word in p for p in probs)
    return {"verdict": "ACCEPT" if ok else "REFUSE", "reasons": probs, "pass": hit}


# ------------------------------------------------------------------ the four cases
def case1(kind, cfg, mat, tmp):
    """Backdated expiry. Record-keeper's engine clock is set into the expired approval's window.
    1a: the judge witnesses at commit time on its own clock. 1b: the judge is shown the head only afterwards."""
    res = {}
    j = mk(kind, os.path.join(tmp, "c1a.json"), cfg, T0)
    outs, wits, head = notary_run(cfg, [mat["EXPIRED"]], clock_t0=T0 - 500, judge=j, judge_times=[T0])
    res["engine_with_backdated_clock"] = outs[0]["outcome"]
    res["1a_witnessed_at_commit"] = outcome(j.verify(head), "refuse", "expired")
    j2 = mk(kind, os.path.join(tmp, "c1b.json"), cfg, T0 + 50)
    res["1b_shown_afterwards"] = outcome(j2.verify(head), "refuse", "expired")
    res["pass"] = res["1a_witnessed_at_commit"]["pass"] and res["1b_shown_afterwards"]["pass"]
    return res


def case2(kind, cfg, mat, tmp):
    """Empty head: a real commit was witnessed; the record-keeper reports genesis and an empty chain."""
    j = mk(kind, os.path.join(tmp, "c2.json"), cfg, T0 + 5)
    outs, wits, real = notary_run(cfg, [mat["ISSUED"]], judge=j, judge_times=[T0 + 5])
    r = outcome(j.verify(empty_head()), "refuse", "empty head")
    return {"real_commit": outs[0]["outcome"], "empty_head": r, "pass": r["pass"]}


def case3(kind, cfg, mat, tmp):
    """Legitimate history verified later: witnessed inside its window, verified after expiry."""
    j = mk(kind, os.path.join(tmp, "c3.json"), cfg, T0 + 5)
    outs, wits, real = notary_run(cfg, [mat["ISSUED"]], judge=j, judge_times=[T0 + 5])
    j.clock.set(T0 + 10_000)  # well past expires_at = T0+300
    r = outcome(j.verify(real), "accept")
    return {"real_commit": outs[0]["outcome"], "verified_after_expiry": r, "pass": r["pass"]}


def case4(kind, cfg, mat, tmp):
    """Judge restart: rebuilt from its persisted state, it must still refuse the empty head and accept the real one."""
    p = os.path.join(tmp, "c4.json")
    j = mk(kind, p, cfg, T0 + 5)
    outs, wits, real = notary_run(cfg, [mat["ISSUED"]], judge=j, judge_times=[T0 + 5])
    del j
    j2 = mk(kind, p, cfg, T0 + 60)
    r_empty = outcome(j2.verify(empty_head()), "refuse", "empty head")
    r_real = outcome(j2.verify(real), "accept")
    return {"real_commit": outs[0]["outcome"], "after_restart_empty_head": r_empty, "after_restart_real_head": r_real,
            "pass": r_empty["pass"] and r_real["pass"]}


# ------------------------------------------------------------------ alongside the gate
def replay(kind, cfg, mat, state_after, tmp):
    res = {}
    # the engine (real notary) refuses replay once it has seen ISSUED
    outs, _, _ = notary_run(cfg, [mat["ISSUED"], mat["REPLAY_NONCE"], mat["REPLAY_DET"]])
    res["engine"] = [o["outcome"] + (": " + o["reason"] if o["reason"] else "") for o in outs]
    res["engine_refuses_both"] = outs[1]["outcome"] == "REFUSE" and outs[2]["outcome"] == "REFUSE" \
        and all("replay" in o["reason"] for o in outs[1:])
    for which in ("REPLAY_NONCE", "REPLAY_DET"):
        j = mk(kind, os.path.join(tmp, "rp_%s.json" % which), cfg, T0 + 5)
        _, _, h1 = notary_run(cfg, [mat["ISSUED"]], judge=j, judge_times=[T0 + 5])
        # compromised record-keeper: a second engine that never saw the first nonce/determination
        o2, _, h2 = notary_run(cfg, [mat[which]], initial_state=state_after)
        spliced = {"state": h2["state"], "state_digest": h2["state_digest"], "verify_history": True,
                   "records": h1["records"] + h2["records"], "proofs": h1["proofs"] + h2["proofs"]}
        j.clock.set(T0 + 6); j.witness(spliced)
        res[which] = {"compromised_engine": o2[0]["outcome"], "judge": outcome(j.verify(spliced), "refuse", "replay")}
    res["pass"] = res["engine_refuses_both"] and res["REPLAY_NONCE"]["judge"]["pass"] and res["REPLAY_DET"]["judge"]["pass"]
    return res


def malformed(kind, cfg, mat, tmp):
    j = mk(kind, os.path.join(tmp, "mf.json"), cfg, T0 + 5)
    _, _, real = notary_run(cfg, [mat["ISSUED"]], judge=j, judge_times=[T0 + 5])
    r0, p0 = real["records"][0], real["proofs"][0]
    bad = {
        "head is a list": [], "head is None": None, "records is an int": dict(real, records=7),
        "proofs missing": {k: v for k, v in real.items() if k != "proofs"},
        "record missing digests": dict(real, records=[{k: v for k, v in r0.items() if k not in ("predecessor_digest", "resulting_digest")}]),
        "timestamp is a string": dict(real, records=[dict(r0, timestamp="yesterday")]),
        "timestamp is None": dict(real, records=[dict(r0, timestamp=None)]),
        "signature not hex": dict(real, proofs=[dict(p0, signature="zz")]),
        "expires_at is a string": dict(real, proofs=[dict(p0, expires_at="later")]),
        "state missing": {k: v for k, v in real.items() if k != "state"},
        "record is a string": dict(real, records=["r"]),
        "proof is a list": dict(real, proofs=[[1, 2]]),
    }
    rows = {}
    for name, h in bad.items():
        try:
            ok, probs = j.verify(h)
            rows[name] = "CRASH (returned None)" if ok is None else ("ACCEPT" if ok else "REFUSE")
        except Exception as e:
            rows[name] = "CRASH %s" % type(e).__name__
    return {"rows": rows, "pass": all(v == "REFUSE" for v in rows.values())}


def no_fallback(kind, cfg, mat, tmp):
    j = mk(kind, os.path.join(tmp, "nf.json"), cfg, T0 + 5)
    _, _, real = notary_run(cfg, [mat["ISSUED"]], judge=j, judge_times=[T0 + 5])
    h = dict(real, verify_history=True, proofs=[])
    r = outcome(j.verify(h), "refuse", "")
    src = open(os.path.join(HERE, "witness_judge.py")).read() if kind != "LEGACY" else ""
    code = "\n".join(l.split("#")[0] for l in src.splitlines() if not l.strip().startswith(('"""', "#")))
    static = ("verify_history" not in code and "history_key" not in code) if kind != "LEGACY" else None
    return {"self_vouched_head": r, "judge_source_never_reads_notary_self_check": static,
            "pass": r["pass"] and (static is not False)}


KEYWORDS = ("expired", "empty head", "truncated head", "replay", "unwitnessed", "malformed", "signature",
            "descent", "binding", "state", "rollback", "not yet valid")


def extra_truncated_prefix(kind, cfg, mat, tmp):
    """NOT IN THE ACCEPTANCE LIST (added after the first run). Two real commits witnessed; the
    record-keeper reports only the first, a valid signed prefix. Same family as the empty head."""
    j = mk(kind, os.path.join(tmp, "tp.json"), cfg, T0 + 5)
    outs, _, real = notary_run(cfg, [mat["ISSUED"], mat["SECOND"]], judge=j, judge_times=[T0 + 5, T0 + 7])
    prefix = {"state": None, "verify_history": True, "records": real["records"][:1], "proofs": real["proofs"][:1]}
    _, _, h1 = notary_run(cfg, [mat["ISSUED"]])
    prefix["state"], prefix["state_digest"] = h1["state"], h1["state_digest"]
    r = outcome(j.verify(prefix), "refuse", "truncated head")
    full = outcome(j.verify(real), "accept")
    return {"commits": [o["outcome"] for o in outs], "prefix_only": r, "full_head": full, "pass": r["pass"] and full["pass"]}


def category(v):
    """Run-independent label for the receipt (reasons contain per-run key-dependent digests)."""
    if isinstance(v, dict) and "verdict" in v:
        if v["verdict"] != "REFUSE":
            return v["verdict"]
        first = v["reasons"][0] if v["reasons"] else ""
        return "REFUSE:" + next((k for k in KEYWORDS if k in first), "other")
    if isinstance(v, dict):
        return {k: category(x) for k, x in sorted(v.items())}
    return v


def main():
    acc = hashlib.sha256(open(os.path.join(HERE, "ACCEPTANCE.md"), "rb").read()).hexdigest()
    frozen = open(os.path.join(HERE, "ACCEPTANCE.sha256")).read().split()[0]
    assert acc == frozen, "ACCEPTANCE.md changed after it was hashed"
    cfg, mat, state_after = build_material()
    results = {}
    for kind in ("LEGACY", "NAIVE", "WITNESS"):
        tmp = tempfile.mkdtemp(prefix="gate_%s_" % kind)
        r = {"case1_backdated_expiry": case1(kind, cfg, mat, tmp), "case2_empty_head": case2(kind, cfg, mat, tmp),
             "case3_history_verified_later": case3(kind, cfg, mat, tmp), "case4_restart": case4(kind, cfg, mat, tmp),
             "replay": replay(kind, cfg, mat, state_after, tmp), "crash_is_not_refusal": malformed(kind, cfg, mat, tmp),
             "no_fallback": no_fallback(kind, cfg, mat, tmp),
             "extra_truncated_prefix_NOT_IN_ACCEPTANCE": extra_truncated_prefix(kind, cfg, mat, tmp)}
        r["gate_pass"] = all(r[c]["pass"] for c in ("case1_backdated_expiry", "case2_empty_head", "case3_history_verified_later", "case4_restart"))
        r["alongside_pass"] = all(r[c]["pass"] for c in ("replay", "crash_is_not_refusal", "no_fallback"))
        results[kind] = r
        shutil.rmtree(tmp)
    L, N, Wt = results["LEGACY"], results["NAIVE"], results["WITNESS"]
    validation = {"legacy_fails_case1": not L["case1_backdated_expiry"]["pass"], "legacy_fails_case2": not L["case2_empty_head"]["pass"],
                  "naive_fails_case3_or_case4": (not N["case3_history_verified_later"]["pass"]) or (not N["case4_restart"]["pass"])}
    validation["gate_discriminates"] = all(validation.values())
    verdict = {"gate_discriminates": validation["gate_discriminates"], "witness_judge_passes_gate": Wt["gate_pass"],
               "witness_judge_passes_alongside": Wt["alongside_pass"],
               "PASS": validation["gate_discriminates"] and Wt["gate_pass"] and Wt["alongside_pass"]}
    out = {"acceptance_sha256": acc, "candidate_files": {f: hashlib.sha256(open(os.path.join(V115, f), "rb").read()).hexdigest()
                                                       for f in ("notary.py", "core.py", "judge_verify.py", "supervisor.py", "session.py")},
           "witness_judge_sha256": hashlib.sha256(open(os.path.join(HERE, "witness_judge.py"), "rb").read()).hexdigest(),
           "validation": validation, "verdict": verdict, "results": results}
    with open(os.path.join(HERE, "gate_results.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    table = category({k: {c: (v[c] if c in ("gate_pass", "alongside_pass") else {kk: vv for kk, vv in v[c].items() if kk != "rows"}) for c in v} for k, v in results.items()})
    receipt = hashlib.sha256(json.dumps({"verdict": verdict, "validation": validation, "table": table}, sort_keys=True).encode()).hexdigest()
    with open(os.path.join(HERE, "gate_receipt.txt"), "w") as f:
        f.write("receipt %s\nacceptance %s\nwitness_judge %s\n" % (receipt, acc, out["witness_judge_sha256"]))
    w = 34
    print("%-*s %-10s %-10s %-10s" % (w, "", "LEGACY", "NAIVE", "WITNESS"))
    for c in ("case1_backdated_expiry", "case2_empty_head", "case3_history_verified_later", "case4_restart", "replay", "crash_is_not_refusal", "no_fallback", "extra_truncated_prefix_NOT_IN_ACCEPTANCE"):
        print("%-*s %-10s %-10s %-10s" % (w, c, *("pass" if results[k][c]["pass"] else "FAIL" for k in ("LEGACY", "NAIVE", "WITNESS"))))
    print("validation", json.dumps(validation))
    print("verdict", json.dumps(verdict))
    print("receipt", receipt)


if __name__ == "__main__":
    main()
