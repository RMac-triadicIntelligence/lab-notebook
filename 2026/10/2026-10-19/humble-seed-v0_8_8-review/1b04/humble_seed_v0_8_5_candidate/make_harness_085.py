#!/usr/bin/env python3
"""Derives falsify_v0_8_5.py from falsify_v0_8_4.py. Written after DECLARED_v0_8_5 was frozen."""
import sys
from pathlib import Path

src_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
src = src_path.read_text(encoding="utf-8")


def once(old, new):
    global src
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"anchor occurs {n} times:\n{old[:200]}")
    src = src.replace(old, new)


def every(old, new, expect):
    global src
    n = src.count(old)
    if n != expect:
        raise SystemExit(f"expected {expect} occurrences, found {n}: {old}")
    src = src.replace(old, new)


once('Falsification harness for humble_seed_v0_8_4_candidate.py  (v0.8.4)\n\nWritten AFTER DECLARED_v0_8_4.json was frozen.',
     'Falsification harness for humble_seed_v0_8_5_candidate.py  (v0.8.5)\n\nWritten AFTER DECLARED_v0_8_5.json was frozen.')
once("Run:  python3 -I falsify_v0_8_4.py", "Run:  python3 -I falsify_v0_8_5.py")
once('CANDIDATE = HERE / "humble_seed_v0_8_4_candidate.py"', 'CANDIDATE = HERE / "humble_seed_v0_8_5_candidate.py"')
once('DECL = HERE / "DECLARED_v0_8_4.json"', 'DECL = HERE / "DECLARED_v0_8_5.json"')
once('DECL_SHA = HERE / "DECLARED_v0_8_4.sha256"', 'DECL_SHA = HERE / "DECLARED_v0_8_5.sha256"')
once('DECL_AT = HERE / "DECLARED_v0_8_4.frozen_at"', 'DECL_AT = HERE / "DECLARED_v0_8_5.frozen_at"')
once('raise SystemExit("DECLARED_v0_8_4.json differs', 'raise SystemExit("DECLARED_v0_8_5.json differs')
once('print("Humble Seed v0.8.4 CANDIDATE — falsification harness")',
     'print("Humble Seed v0.8.5 CANDIDATE — falsification harness")')
once('K = load_module(CANDIDATE, "hs084_candidate")', 'K = load_module(CANDIDATE, "hs085_candidate")')
every('prefix="hs084_', 'prefix="hs085_', 2)
once('(HERE / "RESULTS_v0_8_4.json")', '(HERE / "RESULTS_v0_8_5.json")')
once('print("RESULTS_v0_8_4.json written.', 'print("RESULTS_v0_8_5.json written.')
once('    s, o = born(K, d / "v084")', '    s, o = born(K, d / "v085")')
once('return (f"v0.8.4 applied {applied}/4', 'return (f"v0.8.5 applied {applied}/4')

# T53 corrected (v0.8.4 DEVIATIONS E2): sign off from a freshly opened session
once('''def T53_lifetime_runs_from_first_signing(K, d):
    """ChatGPT, round 4, F1 (stale_signer_refreshes_lifetime) and its control."""
    s, o = born(K, d, reading_ttl_seconds=10.0)
    b = reopen(K, o, d)                      # opened before the first signing
    r = propose(s, "verbosity")
    t0 = time.time()
    o.clock = lambda: t0
    sig = o.sign_proposal(r["payload_to_sign"])
    b.clock = lambda: t0 + 11.0
    b.sign_proposal(r["payload_to_sign"])
    o.sign_proposal(r["payload_to_sign"])
    res = s.authorize_and_apply(r["proposal_id"], sig)
    need(res is not None, f"organism did not apply: {s.trace[-1].get('reason')!r}")
    o.clock = lambda: t0 + 11.0
    return expect_refused(K, lambda: o.attest(s), "past its lifetime by the owner's clock")
''', '''def T53_lifetime_runs_from_first_signing(K, d):
    """ChatGPT, round 4, F1 (stale_signer_refreshes_lifetime). Corrected in v0.8.5
    (v0.8.4 DEVIATIONS E2; ChatGPT r5): sign-off from a freshly opened session."""
    s, o = born(K, d, reading_ttl_seconds=10.0)
    b = reopen(K, o, d)                      # opened before the first signing
    r = propose(s, "verbosity")
    t0 = time.time()
    o.clock = lambda: t0
    sig = o.sign_proposal(r["payload_to_sign"])
    b.clock = lambda: t0 + 11.0
    b.sign_proposal(r["payload_to_sign"])
    res = s.authorize_and_apply(r["proposal_id"], sig)
    need(res is not None, f"organism did not apply: {s.trace[-1].get('reason')!r}")
    c = reopen(K, o, d)                      # a fresh session signs off
    c.clock = lambda: t0 + 11.0
    return expect_refused(K, lambda: c.attest(s), "past its lifetime by the owner's clock")
''')

# T56 corrected (v0.8.4 DEVIATIONS E1): probe from the organism's install, outside the replay
once('''    seen = []

    def clock():
        seen.append(probe())
        return time.time()
    o.clock = clock
    attest_ok(K, o, s)
    o.clock = time.time
    need(seen and all(x == "locked" for x in seen), f"another process could take the owner lock during attest: {seen}")
    after = probe()
    need(after == "free", f"lock still held after attest: {after!r}")
    return f"held during attest ({len(seen)} probe(s)); free after"
''', '''    seen = []
    real = s.install_checkpoint

    def probing_install(cp, sig):           # v0.8.5: outside the replay (v0.8.4 E1)
        seen.append(probe())
        return real(cp, sig)
    s.install_checkpoint = probing_install
    try:
        attest_ok(K, o, s)
    finally:
        s.install_checkpoint = real
    need(seen == ["locked"], f"another process could take the owner lock during attest: {seen}")
    after = probe()
    need(after == "free", f"lock still held after attest: {after!r}")
    return "held during attest (probed from install_checkpoint); free after"
''')

NEW = r'''

# ---------------------------------------------------------------------------
# New in v0.8.5 (T57–T61): saved-state recovery, apply = replay, owner window
# ---------------------------------------------------------------------------

def saved_seq(s):
    return json.loads(s._state_path().read_text())["checkpoint"]["sequence"]


def T57_failed_checkpoint_save_changes_nothing(K, d):
    """ChatGPT, round 5, F2 (failed_install_then_ram_recovery)."""
    s, o = born(K, d)
    apply_ok(K, s, o, propose(s, "verbosity"), attest=False)
    real = s._save

    def failing_save():
        raise OSError("injected: the checkpoint save failed before writing")
    s._save = failing_save
    try:
        o.attest(s)
    except OSError:
        pass
    else:
        raise Fail("injected save failure did not happen")
    finally:
        s._save = real
    need(s.checkpoint.sequence == 0 and saved_seq(s) == 0,
         f"after the failed save: object at {s.checkpoint.sequence}, saved state at {saved_seq(s)}")
    try:
        o.audit(s)
        got = "audit returned"
    except (K.IntegrityError, K.RollbackDetected) as e:
        got = f"{type(e).__name__}: {e}"
    need(got.startswith("IntegrityError") and "Unattested authorizing event" in got,
         f"audit after the failed save: {got}")
    w = K.OwnerWitness(d / "witness.json")
    need(w.ledger[s.organism_id]["sequence"] == 0 and w.pending_for(s.organism_id) is None,
         "the witness advanced past the saved state, or kept the intent")
    attest_ok(K, o, s)
    f = expect_loads(K, s.data_dir)
    audit_ok(K, reopen(K, o, d), f)
    need(fresh_witness_seq(K, d, f) == 1, "witness not at 1 after the retry")
    return "failed save left object and disk at 0; audit refused the unattested crossing and dropped the intent; retry attested"


def T58_stale_object_cannot_abandon_an_installed_intent(K, d):
    """ChatGPT, round 5, F3 (stale_object_abandons_installed_intent)."""
    s, o = born(K, d)
    stale = expect_loads(K, s.data_dir)              # an object kept at checkpoint 0
    apply_ok(K, s, o, propose(s, "verbosity"), attest=False)
    real = o.witness.commit

    def interrupted(cp):
        raise OSError("injected: interrupted after the organism saved, before the witness advanced")
    o.witness.commit = interrupted
    try:
        o.attest(s)
    except OSError:
        pass
    else:
        raise Fail("injected interruption did not happen")
    finally:
        o.witness.commit = real
    need(saved_seq(s) == 1 and fresh_witness_seq(K, d, s) == 0,
         f"setup: saved state at {saved_seq(s)}, witness at {fresh_witness_seq(K, d, s)}")
    why = expect_rollback(K, lambda: o.audit(stale), "Rollback: organism presents sequence 0, witness holds 1")
    w = K.OwnerWitness(d / "witness.json")
    need(w.pending_for(s.organism_id) is None and w.ledger[s.organism_id]["sequence"] == 1,
         "recovery did not complete the installed intent from the saved state")
    f = expect_loads(K, s.data_dir)
    audit_ok(K, reopen(K, o, d), f)
    apply_ok(K, f, reopen(K, o, d), propose(f, "formality", CASUAL))
    return why


def T59_apply_refuses_what_replay_would_refuse(K, d):
    """ChatGPT, round 5, F4 (long_annotation_strands_valid_crossing)."""
    s, o = born(K, d)
    r = propose(s, "verbosity")
    pid = r["proposal_id"]
    sig = o.sign_proposal(r["payload_to_sign"])
    before = snapshot(s)
    out = []

    def refused(name, expect, **kw):
        res = s.authorize_and_apply(pid, sig, **kw)
        need(res is None, f"{name}: APPLIED")
        last = s.trace[-1]
        reason = last.get("reason", "")
        need(last.get("event") == "authorization_rejected" and "replay would refuse" in reason and expect in reason,
             f"{name}: {last.get('event')!r} {reason!r}")
        need(snapshot(s) == before and pid in s.pending, f"{name}: state changed or reading consumed")
        out.append(name)
    refused("2001-character annotation", "unverified_annotation is not a short string", annotation="a" * 2001)
    refused("dict annotation", "unverified_annotation is not a short string",
            annotation={"forged": "owner said yes"})
    t0 = s.pending[pid].timestamp
    s.clock = lambda: t0 - 100.0
    try:
        refused("clock behind issuance", "authorized_at outside the reading's own window")
    finally:
        s.clock = time.time
    res = s.authorize_and_apply(pid, sig, annotation="a" * 2000)
    need(res is not None, f"2000-character annotation did not apply: {s.trace[-1].get('reason')!r}")
    attest_ok(K, o, s)
    f = expect_loads(K, s.data_dir)
    audit_ok(K, o, f)
    return "refused before any change: " + ", ".join(out) + "; 2000 characters applies and attests"


def T60_owner_no_before_signing_holds_first_crossing(K, d):
    """ChatGPT, round 5, F1 (pre_sign_category_no_bypass)."""
    s, o = born(K, d)
    x, y = propose(s, "verbosity"), propose(s, "verbosity")
    o.answer(s, y["proposal_id"], "no", "no")
    s.record_owner_answer(y["proposal_id"], "yes", "forged: written to the organism only")
    res = s.authorize_and_apply(x["proposal_id"], o.sign_proposal(x["payload_to_sign"]))
    need(res is not None, f"organism did not apply X: {s.trace[-1].get('reason')!r}")
    why = expect_refused(K, lambda: o.attest(s), "owner's position")
    need(fresh_witness_seq(K, d, s) == 0, "witness advanced")
    o.answer(s, y["proposal_id"], "yes", "yes")
    attest_ok(K, o, s)
    need(near(s.character["verbosity"], 0.25), f"verbosity {s.character['verbosity']}")
    return why


def T61_owner_no_before_signing_holds_later_crossing(K, d):
    """ChatGPT, round 5, F1, extended to a category's later crossings (author)."""
    s, o = born(K, d)
    apply_ok(K, s, o, propose(s, "verbosity"))
    x2, y2 = propose(s, "verbosity"), propose(s, "verbosity")
    o.answer(s, y2["proposal_id"], "no", "no")
    s.record_owner_answer(y2["proposal_id"], "yes", "forged: written to the organism only")
    res = s.authorize_and_apply(x2["proposal_id"], o.sign_proposal(x2["payload_to_sign"]))
    need(res is not None, f"organism did not apply X2: {s.trace[-1].get('reason')!r}")
    why = expect_refused(K, lambda: o.attest(s), "owner's position")
    need(fresh_witness_seq(K, d, s) == 1, "witness advanced")
    return why


TESTS = TESTS + [T57_failed_checkpoint_save_changes_nothing, T58_stale_object_cannot_abandon_an_installed_intent,
                 T59_apply_refuses_what_replay_would_refuse, T60_owner_no_before_signing_holds_first_crossing,
                 T61_owner_no_before_signing_holds_later_crossing]
'''

once('''                 T55_commit_recovers_before_organism_install, T56_owner_lock_excludes_other_processes]
''', '''                 T55_commit_recovers_before_organism_install, T56_owner_lock_excludes_other_processes]
''' + NEW)

out_path.write_text(src, encoding="utf-8")
print("written", out_path)
