#!/usr/bin/env python3
"""Living SCS adversarial battery 0.2. Candidate source is never modified.

Trusted setup mints fixtures, then attacks edit copies without signing privileges.
The judge lane requires the actual judge_verify.py; it is never reconstructed.
"""
import argparse
import copy
import dataclasses as dc
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import struct
import sys
import traceback
from collections import Counter

T0 = 2_000_000_000
INIT = {"maturity": "juvenile", "personality": {"tone": "humble"},
        "organs": {}, "policy": {"egress": "deny"}}


class ControlFailure(Exception):
    """An honest control failed; this is not an unauthorized acceptance."""


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def change(value):
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        return ("1" if value[0:1] != "1" else "2") + value[1:] if value else "tampered"
    if isinstance(value, int):
        return value + 1
    if isinstance(value, list):
        return [] if value else ["tampered"]
    if isinstance(value, dict):
        return dict(value, tampered=True)
    return "tampered"


def public_cfg(m, signer, org):
    return {"public_key_hex": signer.public_key_bytes().hex(), "authority_id": signer.authority_id,
            "organism_id": org, "initial_state": copy.deepcopy(INIT), "clock_t0": T0}


def fixture(m, seed, n=3, issued_at=T0, expires_at=T0 + 300, decision=None, reuse_nonce=False, reuse_determination=False):
    """Trusted test authority creates a real chain before attacker code receives it.
    Fixed TEST keys are for repeatability only; never suitable for deployment.
    """
    key = hashlib.sha256(("TEST ONLY " + str(seed)).encode()).digest()
    signer = m.MinatoAuthority("authority-" + str(seed), m.Ed25519PrivateKey.from_private_bytes(key))
    cfg = public_cfg(m, signer, "organism-" + str(seed))
    history_key = hashlib.sha256(("history TEST " + str(seed)).encode()).digest()

    def engine(clock=T0, hook=None):
        return m.CommitEngine(cfg["organism_id"], INIT,
            m.MinatoAuthority.verifier_only(cfg["authority_id"], signer.public_key),
            m.TrustedClock(clock), expected_authority_id=cfg["authority_id"],
            expected_public_key=signer.public_key_bytes(), history_key=history_key, persist_hook=hook)

    eng = engine(issued_at if expires_at < T0 else T0)
    bundles, heads = [], []
    heads.append({"state": eng.state, "state_digest": eng.state_digest,
                  "verify_history": True, "records": [], "proofs": []})
    for i in range(n):
        mut = {"op": "set", "path": ["personality", "lesson"], "value": i + 1}
        p = eng.proposal_for_mutation(proposal_id="p-" + str(i), mutation_type="set", mutation=mut,
            evidence=[m.EvidenceItem("ev-" + str(i), "sensor://test/" + str(i), issued_at,
                                     "drift_detector", "1", {"score": .91})],
            interpretation=m.Interpretation("basin", "1", {"r": "ok"}, .9, .8, .7, .9),
            created_at=issued_at)
        t = m.make_trace(p, trace_id="t-" + str(i), created_at=issued_at)
        a = signer.issue(t, p, decision=decision or m.Decision.AUTHORIZE,
            determination_id="det-" + str(i), nonce="nonce-" + str(i),
            issued_at=issued_at, expires_at=expires_at)
        if a.decision == m.Decision.AUTHORIZE and issued_at <= T0 + 30:
            eng.commit(p, t, a)
            # Trusted fixture authority issues a second valid authorization with
            # a reused identifier. Attacker receives only these signed fixtures.
            if i == 1 and (reuse_nonce or reuse_determination):
                a = signer.issue(t, p, decision=m.Decision.AUTHORIZE,
                    determination_id="det-0" if reuse_determination else "det-1",
                    nonce="nonce-0" if reuse_nonce else "nonce-1",
                    issued_at=issued_at, expires_at=expires_at)
            proof = a.signed_body(); proof["signature"] = a.signature
            head = {"state": eng.state, "state_digest": eng.state_digest, "verify_history": True,
                    "records": [dc.asdict(r) for r in eng.records],
                    "proofs": heads[-1]["proofs"] + [proof]}
            if reuse_determination and i >= 1:
                head["records"][1]["authorization_id"] = "det-0"
                previous = "0"*64
                for rec in head["records"]:
                    rec["previous_record_hash"] = previous
                    body = dict(rec); body.pop("record_hash")
                    rec["record_hash"] = m.record_hash_for(body, history_key)
                    previous = rec["record_hash"]
            heads.append(head)
        bundles.append((p, t, a))
    # Attacks receive no authority private key. Engine factory holds only a verifier.
    del signer, key
    pub = m.Ed25519PublicKey.from_public_bytes(bytes.fromhex(cfg["public_key_hex"]))
    def verifier_engine(clock=T0, hook=None):
        return m.CommitEngine(cfg["organism_id"], INIT,
            m.MinatoAuthority.verifier_only(cfg["authority_id"], pub), m.TrustedClock(clock),
            expected_authority_id=cfg["authority_id"], expected_public_key=bytes.fromhex(cfg["public_key_hex"]),
            history_key=history_key, persist_hook=hook)
    return cfg, bundles, heads, verifier_engine, history_key


class Battery:
    def __init__(self):
        self.results = []

    def record(self, lane, name, status, detail="", contract=""):
        self.results.append(dict(lane=lane, name=name, status=status, detail=str(detail), contract=contract))
        if status != "PASS":
            print(f"{lane:8} {status:8} {name}: {detail}", flush=True)

    def check(self, lane, name, fn, contract=""):
        try:
            detail = fn()
            self.record(lane, name, "PASS", detail or "", contract)
        except ControlFailure as e:
            self.record(lane, name, "CONTROL_FAIL", e, contract)
        except AssertionError as e:
            self.record(lane, name, "BREACH", e, contract)
        except Exception:
            self.record(lane, name, "ERROR", traceback.format_exc(limit=3), contract)


def assert_equal(a, b, msg):
    assert a == b, msg


def engine_lane(b, m, seed):
    cfg, bundles, heads, make, hk = fixture(m, seed)
    p, t, a = bundles[0]

    def rejected(bundle, prefix=(), clock=T0, reason="attack"):
        eng = make(clock)
        for sub in prefix:
            eng.commit(*sub)
        before = (eng.state, eng.state_digest, eng.records)
        try:
            eng.commit(*bundle, reason=reason)
        except (m.Refusal, m.TraceError) as exc:
            assert_equal((eng.state, eng.state_digest, eng.records), before, "refusal mutated the ledger/state")
            assert eng.verify_history(), "refusal corrupted the history"
            return str(exc)
        raise AssertionError("unauthorized or malformed transition committed")

    def accepted(bundle, clock=T0):
        eng = make(clock)
        eng.commit(*bundle)
        assert_equal(len(eng.records), 1, "authorized control did not append exactly once")
        assert_equal(eng.state_digest, bundle[0].expected_result_digest, "wrong resulting state")
        assert eng.verify_history(), "authorized control broke history"

    b.check("engine", "honest_authorize", lambda: accepted(bundles[0]))
    def chain():
        e = make()
        for sub in bundles:
            e.commit(*sub)
        assert_equal(e.state, heads[-1]["state"], "3-commit state differs")
        assert_equal(len(e.records), 3, "3-commit control incomplete")
        assert e.verify_history()
    b.check("engine", "honest_three_commit_chain", chain)
    for section, obj in zip(("proposal", "trace", "auth"), (p, t, a)):
        for field in dc.fields(obj):
            value = getattr(obj, field.name)
            if section == "auth" and field.name == "decision":
                new = m.Decision.REFUSE
            elif section == "trace" and field.name == "status":
                new = m.ProposalStatus.COMMITTED
            else:
                new = change(value)
            sub = list(bundles[0]); sub[("proposal", "trace", "auth").index(section)] = dc.replace(obj, **{field.name: new})
            b.check("engine", f"tamper_{section}_{field.name}", lambda sub=tuple(sub): rejected(sub))
    for index, sub in enumerate(bundles):
        if index:
            b.check("engine", f"future_chain_element_{index+1}", lambda sub=sub: rejected(sub))
    b.check("engine", "replay_after_commit", lambda: rejected(bundles[0], [bundles[0]]))
    for tag,kwargs in [("nonce",{"reuse_nonce":True}), ("determination",{"reuse_determination":True})]:
        _, bs, _, _, _ = fixture(m, seed, n=2, **kwargs)
        b.check("engine", "valid_predecessor_reused_"+tag,
                lambda bs=bs:rejected(bs[1], [bs[0]]))
    for name, kwargs, expected in [
        ("expires_exactly_now", {"expires_at": T0}, True),
        ("expires_one_second_before", {"expires_at": T0-1, "issued_at": T0-100}, False),
        ("future_at_30s_tolerance", {"issued_at": T0+30}, True),
        ("future_at_31s", {"issued_at": T0+31}, False),
        ("signed_refusal", {"decision": m.Decision.REFUSE}, False),
        ("signed_flag", {"decision": m.Decision.FLAG}, False)]:
        _, bs, _, _, _ = fixture(m, seed, n=1, **kwargs)
        b.check("engine", name, (lambda sub=bs[0]: accepted(sub)) if expected else (lambda sub=bs[0]: rejected(sub)))
    for name, value in [("bool_time", True), ("float_time", float(T0)), ("unsafe_time", 2**54),
                        ("string_time", str(T0)), ("null_time", None)]:
        b.check("engine", name, lambda value=value: rejected((p,t,dc.replace(a, issued_at=value))))
    for name, reason in [("reason_nan", float("nan")), ("reason_object", {}), ("reason_null", None)]:
        b.check("engine", name, lambda reason=reason: rejected((p,t,a), reason=reason))
    def detached():
        e = make(); e.commit(*bundles[0]); before = e.state
        leaked = e.state; leaked["maturity"] = "mature"
        rec = e.records[0]; object.__setattr__(rec, "sequence", 999)
        assert_equal(e.state, before, "returned state aliased internal state")
        assert_equal(e.records[0].sequence, 1, "returned record aliased internal record")
        assert e.verify_history()
    b.check("engine", "returned_state_and_record_detached", detached)
    def failed_persistence():
        calls=[]
        def hook(rec, state):
            calls.append(rec.sequence)
            if len(calls) == 1:
                raise OSError("simulated durable-write failure")
        e=make(hook=hook)
        try:
            e.commit(*bundles[0])
        except OSError:
            pass
        else:
            raise AssertionError("persistence exception suppressed")
        assert_equal((e.state, len(e.records)), (INIT,0), "failed persistence mutated state")
        e.commit(*bundles[0])
        assert_equal((calls, len(e.records)), ([1,1],1), "retry failed or consumed authorization")
    b.check("engine", "persistence_failure_atomic_retry", failed_persistence)
    def concurrency():
        from concurrent.futures import ThreadPoolExecutor
        e=make()
        def attempt(_):
            try:
                e.commit(*bundles[0]); return "accepted"
            except (m.Refusal,m.TraceError):
                return "refused"
        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes=list(pool.map(attempt, range(32)))
        assert_equal(outcomes.count("accepted"), 1, "parallel replay committed more than once")
        assert_equal(len(e.records),1,"parallel history length differs")
        assert e.verify_history()
    b.check("engine", "32_concurrent_replays_exactly_one_commit", concurrency)
    def rollback_clock():
        e=make(); e.commit(*bundles[0]); e._clock.set(T0-1)
        before=(e.state,e.records)
        try:
            e.commit(*bundles[1])
        except m.Refusal:
            assert_equal((e.state,e.records),before,"clock refusal mutated state"); return
        raise AssertionError("clock rollback accepted")
    b.check("engine", "clock_rollback_after_observation", rollback_clock)
    # With this key an attacker can forge HMAC records. That is a layer-2 premise,
    # not a verdict that the authority-signature judge accepted the forgery.
    return cfg, bundles, heads, hk


def wire_lane(b, wire, seed):
    payloads=[b'{"op":"head"}', b'{"x":"escaped \\" [ ] { }"}', b'{"unicode":"\\u2600"}']
    stream=b"".join(wire.frame(x) for x in payloads)
    for index in range(64):
        def fragmented(index=index):
            rng=random.Random(seed+index); buf=wire.FrameBuffer(); got=[]; pos=0
            while pos<len(stream):
                n=rng.randrange(1,17); got+=buf.feed(stream[pos:pos+n]); pos+=n
            assert_equal(got,payloads,"fragmented/coalesced frames lost or reordered")
            assert_equal(len(buf.buf),0,"residual bytes after complete frames")
        b.check("wire",f"fragmentation_seed_{index}",fragmented)
    bad=[("duplicate_top",b'{"op":"head","op":"commit"}'),
         ("duplicate_nested",b'{"x":{"a":1,"a":2}}'),
         ("invalid_utf8",b'{"x":"\xff"}'), ("trailing_json",b'{}{}'),
         ("nan",b'{"x":NaN}'),("infinity",b'{"x":Infinity}'),
         ("negative_infinity",b'{"x":-Infinity}'),("truncated_json",b'{"x":'),
         ("depth_97", b'['*97+b'0'+b']'*97)]
    for name,raw in bad:
        def refuse(raw=raw):
            try:
                wire.decode(raw)
            except wire.WireRefusal as e:
                return str(e)
            raise AssertionError("malformed wire accepted")
        b.check("wire",name,refuse)
    def oversized():
        try:
            wire.FrameBuffer().feed(struct.pack(">I",wire.MAX_FRAME+1))
        except wire.WireError:
            return
        raise AssertionError("oversized declared length accepted")
    b.check("wire","oversized_declared_length",oversized)
    def exact_limit():
        raw=b"x"*wire.MAX_FRAME
        assert_equal(wire.FrameBuffer().feed(wire.frame(raw)),[raw],"exact size cap refused")
    b.check("wire","exact_frame_size_control",exact_limit)
    def depth_control():
        assert_equal(wire.decode(b'['*96+b'0'+b']'*96), nested_list(96), "depth cap changed")
    b.check("wire","depth_96_control",depth_control)


def nested_list(n):
    x=0
    for _ in range(n):
        x=[x]
    return x


def judge_cases(m,cfg,bundles,heads,hk,seed):
    cases=[]
    def add(name,head,expect=False,contract="integrity",context=None):
        cases.append((name,copy.deepcopy(head),expect,contract,context or cfg))
    add("honest_empty_control",heads[0],True)
    add("honest_single_control",heads[1],True)
    add("honest_three_commit_control",heads[3],True)
    # Valid historical cuts are controls for integrity. Freshness probes present
    # the same cuts after three commits actually happened: trusted context differs.
    add("honest_historical_prefix_control",heads[1],True)
    add("rollback_to_empty_after_three_commits",heads[0],False,"completeness/freshness")
    add("truncate_to_valid_prefix_after_three_commits",heads[1],False,"completeness/freshness")
    _,_,expired,_,_=fixture(m,seed,n=1,issued_at=T0-1000,expires_at=T0-10)
    add("expired_signed_backdated_head",expired[-1],False,"freshness")
    for section in ("records","proofs"):
        for field,value in heads[1][section][0].items():
            h=copy.deepcopy(heads[1]); h[section][0][field]=change(value)
            diagnostic = section == "records" and field in {"reason","timestamp","record_hash"}
            add(f"tamper_{section}_{field}",h,None if diagnostic else False,
                "unsigned record metadata diagnostic" if diagnostic else "integrity")
        for field in heads[1][section][0]:
            h=copy.deepcopy(heads[1]); del h[section][0][field]
            add(f"missing_{section}_{field}",h,False,"schema")
    for field in ("state","state_digest","records","proofs"):
        h=copy.deepcopy(heads[1]); del h[field]
        add("missing_head_"+field,h,False,"schema")
    for section in ("records","proofs"):
        for tag,value in [("null",None),("object",{}),("string","x"),("integer",1)]:
            h=copy.deepcopy(heads[1]);h[section]=value;add(f"wrong_type_{section}_{tag}",h,False,"schema")
    h=copy.deepcopy(heads[1]);h["records"]=[];h["proofs"]=[];add("state_kept_records_dropped",h)
    h=copy.deepcopy(heads[1]);h["state"]["maturity"]="mature";h["state_digest"]=m.sha256_hex(h["state"]);add("maturity_without_signed_transition",h)
    h=copy.deepcopy(heads[1]);h["proofs"]=[];add("history_hmac_only_no_authority_proof",h)
    h=copy.deepcopy(heads[1]);h["verify_history"]=False;add("untrusted_history_flag_false_diagnostic",h,None,"self-report diagnostic")
    h=copy.deepcopy(heads[1]);h["records"][0]["sequence"]=True;add("boolean_sequence",h)
    for section in ("records","proofs"):
        h=copy.deepcopy(heads[3]);h[section].reverse();add("reordered_"+section,h)
        h=copy.deepcopy(heads[3]);h[section].pop(1);add("drop_middle_"+section,h)
        h=copy.deepcopy(heads[1]);h[section].append(copy.deepcopy(h[section][0]));add("extra_"+section,h)
    h=copy.deepcopy(heads[3]);h["proofs"][1]=copy.deepcopy(h["proofs"][0]);add("proof_reuse_in_real_three_chain",h)
    for tag,kwargs in [("nonce",{"reuse_nonce":True}), ("determination",{"reuse_determination":True})]:
        _, _, reused, _, _ = fixture(m,seed,n=2,**kwargs)
        add("valid_predecessor_signed_reused_"+tag,reused[-1])
    h=copy.deepcopy(heads[3]);h["records"][1]["previous_record_hash"]="0"*64;add("sever_previous_hash",h)
    # Compromised notary knows history HMAC key; recompute the chain to ensure
    # refusal cannot depend only on accidental HMAC breakage.
    h=copy.deepcopy(heads[3]);h["records"][1]["authorization_id"]="forged"
    previous="0"*64
    for rec in h["records"]:
        rec["previous_record_hash"]=previous
        body=dict(rec);body.pop("record_hash")
        rec["record_hash"]=m.record_hash_for(body,hk);previous=rec["record_hash"]
    add("hmac_recomputed_authorization_id_forgery",h)
    _,_,foreign,_,_=fixture(m,seed+999,n=3)
    h=copy.deepcopy(heads[1]);h["proofs"][0]=foreign[1]["proofs"][0];add("foreign_authority_real_proof",h)
    h=copy.deepcopy(heads[3]);h["records"][1:]=foreign[3]["records"][1:];h["proofs"][1:]=foreign[3]["proofs"][1:];add("foreign_chain_splice",h)
    for field,value in [("authority_id","wrong"),("organism_id","wrong"),("public_key_hex","00"*32)]:
        c=dict(cfg);c[field]=value;add("trusted_context_wrong_"+field,heads[1],context=c)
    for value in (True,float(T0),str(T0),None):
        h=copy.deepcopy(heads[1]);h["records"][0]["timestamp"]=value;add("record_timestamp_"+type(value).__name__,h,False,"schema")
    for tag,value in [("before_issue",T0-31),("after_expiry",T0+301)]:
        h=copy.deepcopy(heads[1]);h["records"][0]["timestamp"]=value
        add("record_time_"+tag,h,False,"signed authorization validity window")
    return cases


def judge_lane(b,m,judge,cfg,bundles,heads,hk,seed):
    for name,head,expect,contract,context in judge_cases(m,cfg,bundles,heads,hk,seed):
        if judge is None:
            b.record("judge",name,"BLOCKED","actual judge_verify.py unavailable",contract);continue
        def run(head=head,expect=expect,context=context):
            verdict=judge.verify_ledger(head,context["public_key_hex"],context["authority_id"],context["organism_id"],INIT)
            if not (type(verdict) is tuple and len(verdict)==2 and type(verdict[0]) is bool):
                raise ValueError("invalid judge return contract")
            if expect is True and verdict[0] is False:
                raise ControlFailure("honest judge control rejected: "+repr(verdict))
            if expect is not None:
                assert_equal(verdict[0],expect,f"expected VERIFIED={expect}, got {verdict}")
            return repr(verdict)
        b.check("judge",name,run,contract)


def notary_lane(b,root,layer,seed):
    sys.path.insert(0,str(layer))
    session=load(layer/"session.py","session_expanded")
    sup=load(layer/"supervisor.py","supervisor_expanded")
    cfg,mat=session.build(str(root))
    handle=sup.NotaryHandle(str(root),cfg,isolation="local")
    client=sup.OrgClient(handle.org_w,handle.org_r)
    def submit(name,sub,expected):
        before=handle.head()
        out=client.request({"op":"commit","submission":sub},timeout=5)
        after=handle.head()
        assert out["outcome"] in expected, f"unexpected notary response {out}"
        if "ACCEPT" not in expected:
            for k in ("state","state_digest","records"):
                assert_equal(after[k],before[k],"notary refusal changed "+k)
        return out
    try:
        malformed=[("duplicate_op",b'{"op":"head","op":"commit"}'),
                   ("utf8",b'{"op":"\xff"}'),("nan",b'{"op":"commit","submission":NaN}'),
                   ("trailing_json",b'{}{}'),("too_deep",b'['*97+b'0'+b']'*97),
                   ("organism_shutdown",b'{"op":"shutdown"}'),
                   ("unknown_op",b'{"op":"grant_maturity"}'),
                   ("extra_op_fields",b'{"op":"head","admin":true}'),
                   ("non_object",b'[]'),("non_string_op",b'{"op":true}')]
        for name,raw in malformed:
            def raw_refusal(raw=raw):
                before=handle.head();out=client.raw(raw,timeout=5);after=handle.head()
                assert_equal(out["outcome"],"WIRE_REFUSE","malformed protocol reached commit")
                for k in ("state","state_digest","records"):
                    assert_equal(after[k],before[k],"malformed request changed "+k)
                return out
            b.check("notary","protocol_"+name,raw_refusal)
        def partial_frame():
            packet=sup.wire.frame(sup.wire.encode({"op":"head"}))
            os.write(handle.org_w,packet[:2])
            head=handle.head()
            assert head is not None,"partial organism header stalled the judge channel"
            os.write(handle.org_w,packet[2:])
            out=sup._read_frame(handle.org_r,client.fb,5)
            assert_equal(out["outcome"],"HEAD","completed partial frame failed")
        b.check("notary","partial_header_does_not_stall_judge",partial_frame)
        for name in ("EXPIRED","REFUSED"):
            b.check("notary",name.lower(),lambda name=name: submit(name,mat[name],{"REFUSE"}))
        base=mat["ISSUED"]
        for section in ("proposal","trace","auth"):
            for field,value in base[section].items():
                sub=copy.deepcopy(base);sub[section][field]=change(value)
                b.check("notary",f"tamper_{section}_{field}",lambda sub=sub: submit("tamper",sub,{"REFUSE","ADAPTER_REFUSE"}))
        for field in ("proposal","trace","auth"):
            sub=copy.deepcopy(base);sub.pop(field)
            b.check("notary","missing_"+field,lambda sub=sub:submit("missing",sub,{"REFUSE","ADAPTER_REFUSE"}))
        def honest():
            out=submit("issued",base,{"ACCEPT"})
            head=handle.head()
            assert_equal(len(head["records"]),1,"honest control did not commit exactly once")
            assert_equal(head["state"]["personality"].get("motto"),"dwell first","wrong honest state")
            return out
        b.check("notary","honest_issued_control",honest)
        b.check("notary","replay_issued",lambda:submit("replay",base,{"REFUSE"}))
    finally:
        handle.release_organism_ends();handle.shutdown()
    for name,packet in [("oversized_frame",struct.pack(">I",sup.wire.MAX_FRAME+1)),("organism_eof",None)]:
        def broken_channel(packet=packet):
            h=sup.NotaryHandle(str(root),cfg,isolation="local")
            try:
                if packet is None:
                    h.release_organism_ends()
                else:
                    os.write(h.org_w,packet)
                head=h.head()
                assert head is not None,"broken organism channel lost judge access"
                assert_equal(head["state"],INIT,"broken channel altered state")
                assert_equal(len(head["records"]),0,"broken channel committed")
            finally:
                if packet is not None:
                    h.release_organism_ends()
                h.shutdown()
        b.check("notary","judge_survives_"+name,broken_channel)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate",type=Path,required=True,help="candidate root containing v114 and layer directory")
    parser.add_argument("--layer-dir",default="v115",help="directory containing session/supervisor/wire; e.g. v116")
    parser.add_argument("--core",type=Path,help="override exact core.py location")
    parser.add_argument("--judge",type=Path,help="actual judge_verify.py location")
    parser.add_argument("--seed",type=int,default=17092026)
    parser.add_argument("--output",type=Path,default=Path("results.json"))
    parser.add_argument("--timeout",type=int,default=45,help="per-case alarm on Unix")
    parser.add_argument("--skip-notary",action="store_true")
    args=parser.parse_args()
    root=args.candidate.resolve();layer=(root/args.layer_dir).resolve()
    core=(args.core or layer/"core.py").resolve()
    judge_path=(args.judge or layer/"judge_verify.py").resolve()
    b=Battery()
    hashes={str(p.relative_to(root)) if p.is_relative_to(root) else str(p):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*.py")) if "__pycache__" not in p.parts}
    meta={"candidate_root":str(root),"core_path":str(core),"judge_path":str(judge_path),
          "source_hashes":hashes,"seed":args.seed,"battery_version":"0.2",
          "trusted_time":T0,"fixture_private_keys":"TEST ONLY; deterministic trusted fixture setup"}
    # Alarm prevents a malicious/malformed candidate verdict from stalling forever.
    import signal
    original_check=b.check
    def timed_check(lane,name,fn,contract=""):
        def timeout(*_):
            raise TimeoutError("per-case budget exceeded")
        signal.signal(signal.SIGALRM,timeout);signal.alarm(args.timeout)
        try:
            original_check(lane,name,fn,contract)
        finally:
            signal.alarm(0)
    b.check=timed_check
    try:
        sys.path.insert(0,str(layer))
        m=load(core,"expanded_core")
        wire=load(layer/"wire.py","expanded_wire")
        judge=load(judge_path,"expanded_judge") if judge_path.exists() else None
        print("Core SHA256:",hashlib.sha256(core.read_bytes()).hexdigest(),flush=True)
        cfg,bundles,heads,hk=engine_lane(b,m,args.seed)
        wire_lane(b,wire,args.seed)
        judge_lane(b,m,judge,cfg,bundles,heads,hk,args.seed)
        if not args.skip_notary:
            try:
                notary_lane(b,root,layer,args.seed)
            except Exception:
                b.record("setup","notary_lane","ERROR",traceback.format_exc())
        else:
            b.record("notary","lane_skipped","BLOCKED","explicit --skip-notary")
    except Exception:
        b.record("setup","load_or_fixture","ERROR",traceback.format_exc())
    totals=dict(Counter(r["status"] for r in b.results))
    lanes={lane:dict(Counter(r["status"] for r in b.results if r["lane"]==lane)) for lane in sorted({r["lane"] for r in b.results})}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({"metadata":meta,"totals":totals,"lanes":lanes,"results":b.results},indent=2)+"\n")
    print("RESULTS",json.dumps({"totals":totals,"lanes":lanes},sort_keys=True),flush=True)
    # No error, breach, or missing lane is green. Breach takes priority.
    return 1 if totals.get("BREACH") else 2 if totals.get("ERROR") or totals.get("BLOCKED") or totals.get("CONTROL_FAIL") else 0


if __name__=="__main__":
    raise SystemExit(main())
