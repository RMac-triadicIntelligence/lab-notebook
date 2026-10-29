#!/usr/bin/env python3
"""Derives falsify_v0_8_7.py from falsify_v0_8_6.py. Written after DECLARED_v0_8_7 was frozen."""
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


once('Falsification harness for humble_seed_v0_8_6_candidate.py  (v0.8.6)\n\nWritten AFTER DECLARED_v0_8_6.json was frozen.',
     'Falsification harness for humble_seed_v0_8_7_candidate.py  (v0.8.7)\n\nWritten AFTER DECLARED_v0_8_7.json was frozen.')
once("Run:  python3 -I falsify_v0_8_6.py", "Run:  python3 -I falsify_v0_8_7.py")
once("import tempfile\nimport time\n", "import tempfile\nimport threading\nimport time\n")
once('CANDIDATE = HERE / "humble_seed_v0_8_6_candidate.py"', 'CANDIDATE = HERE / "humble_seed_v0_8_7_candidate.py"')
once('DECL = HERE / "DECLARED_v0_8_6.json"', 'DECL = HERE / "DECLARED_v0_8_7.json"')
once('DECL_SHA = HERE / "DECLARED_v0_8_6.sha256"', 'DECL_SHA = HERE / "DECLARED_v0_8_7.sha256"')
once('DECL_AT = HERE / "DECLARED_v0_8_6.frozen_at"', 'DECL_AT = HERE / "DECLARED_v0_8_7.frozen_at"')
once('raise SystemExit("DECLARED_v0_8_6.json differs', 'raise SystemExit("DECLARED_v0_8_7.json differs')
once('print("Humble Seed v0.8.6 CANDIDATE — falsification harness")',
     'print("Humble Seed v0.8.7 CANDIDATE — falsification harness")')
once('K = load_module(CANDIDATE, "hs086_candidate")', 'K = load_module(CANDIDATE, "hs087_candidate")')
every('prefix="hs086_', 'prefix="hs087_', 2)
once('(HERE / "RESULTS_v0_8_6.json")', '(HERE / "RESULTS_v0_8_7.json")')
once('print("RESULTS_v0_8_6.json written.', 'print("RESULTS_v0_8_7.json written.')
once('    s, o = born(K, d / "v086")', '    s, o = born(K, d / "v087")')
once('return (f"v0.8.6 applied {applied}/4', 'return (f"v0.8.7 applied {applied}/4')

NEW = r'''

# ---------------------------------------------------------------------------
# New in v0.8.7 (T70–T81): one operation at a time; unusable objects; restore
# ---------------------------------------------------------------------------

def saved_state(s):
    return json.loads(s._state_path().read_text())


def saved_dwellings(s):
    return [e.get("category") for e in saved_state(s)["trace"] if e.get("event") == "dwelling"]


def expect_stale_reason(K, fn, sub):
    try:
        fn()
    except K.StaleOrganism as e:
        need(sub in str(e), f"StaleOrganism for a different reason: {str(e)!r}")
        return str(e)
    raise Fail("ACCEPTED (no StaleOrganism)")


def restore_ok(K, o, s):
    try:
        return o.restore(s)
    except (K.RollbackDetected, K.IntegrityError, K.AttestationRefused) as e:
        raise Fail(f"restore refused: {type(e).__name__}: {e}")


def _start(fn, name):
    box = {"done": threading.Event()}

    def run():
        try:
            box["result"] = fn()
        except BaseException as e:          # re-raised unchanged by the caller
            box["error"] = e
        finally:
            box["done"].set()
    threading.Thread(target=run, name=name, daemon=True).start()
    return box


def paused_race(first, second, install_pause, b_window=0.25):
    """Run first() in thread 'A' until its pause point, then second() in thread 'B'.
    Returns (B finished while A was paused, A's result, B's result). Thread errors re-raise unchanged."""
    ready, release = threading.Event(), threading.Event()
    undo = install_pause(ready, release)
    b = None
    try:
        a = _start(first, "A")
        while not ready.wait(0.05):
            if a["done"].is_set():
                break
        if "error" in a:
            raise a["error"]
        need(ready.is_set(), "thread A finished without reaching its pause point")
        b = _start(second, "B")
        b_early = b["done"].wait(b_window)
        release.set()
        finished = a["done"].wait(30) and b["done"].wait(30)
    finally:
        release.set()
        undo()
    for box in (a, b):
        if "error" in box:
            raise box["error"]
    need(finished, "a thread did not finish within 30 s of the release")
    return b_early, a.get("result"), b.get("result")


def pause_in_state_serialization(K):
    def install(ready, release):
        real = K._canonical_json

        def pausing(obj):
            text = real(obj)
            if (threading.current_thread().name == "A" and isinstance(obj, dict)
                    and "state_seal" in obj and not ready.is_set()):
                ready.set()
                release.wait(30)
            return text
        K._canonical_json = pausing

        def undo():
            K._canonical_json = real
        return undo
    return install


def pause_at_second_clock_call(s):
    def install(ready, release):
        real = s.clock
        calls = []

        def pausing():
            t = real()
            if threading.current_thread().name == "A":
                calls.append(t)
                if len(calls) == 2 and not ready.is_set():
                    ready.set()
                    release.wait(30)
            return t
        s.clock = pausing

        def undo():
            s.clock = real
        return undo
    return install


def T70_two_threads_one_object_lose_no_dwelling(K, d):
    """ChatGPT, round 7, F1 (schedule 1)."""
    s, o = born(K, d)
    g0 = saved_state(s)["generation"]
    b_early, ra, rb = paused_race(lambda: s.dwell_or_propose("curiosity", "evt", "hmm ok")["status"],
                                  lambda: s.dwell_or_propose("formality", "evt", "hmm ok")["status"],
                                  pause_in_state_serialization(K))
    need(not b_early, "thread B finished its dwell while A was paused mid-save")
    need(ra == rb == "dwelling", f"statuses {ra!r}, {rb!r}")
    ds = saved_dwellings(s)
    need("curiosity" in ds and "formality" in ds, f"a dwelling was lost: saved dwellings {ds}")
    g = saved_state(s)["generation"]
    need(g == g0 + 2, f"saved generation {g}, expected {g0 + 2}")
    audit_ok(K, o, expect_loads(K, s.data_dir))
    return f"B waited for A; both dwellings saved; generation {g0} -> {g}"


def T71_two_threads_attest_cannot_be_rewound(K, d):
    """ChatGPT, round 7, F1 (schedule 2)."""
    s, o = born(K, d)
    b_early, ra, rb = paused_race(lambda: s.dwell_or_propose("curiosity", "evt", "hmm ok")["status"],
                                  lambda: o.attest(s), pause_in_state_serialization(K))
    need(not b_early, "attest finished while A was paused mid-save")
    need(ra == "dwelling" and rb is True, f"dwell returned {ra!r}, attest returned {rb!r}")
    st = saved_state(s)
    need(st["checkpoint"]["sequence"] == 1 and fresh_witness_seq(K, d, s) == 1,
         f"saved checkpoint {st['checkpoint']['sequence']}, witness {fresh_witness_seq(K, d, s)}")
    need("curiosity" in saved_dwellings(s), "A's dwelling was lost")
    audit_ok(K, o, expect_loads(K, s.data_dir))
    return "attest waited for A; saved checkpoint 1 = witness 1"


def T72_operation_is_atomic_across_threads(K, d):
    """Author's third schedule: a pause between an operation's changes to memory."""
    s, o = born(K, d)
    g0 = saved_state(s)["generation"]
    b_early, ra, rb = paused_race(lambda: s.dwell_or_propose("curiosity", "evt", "hmm ok")["status"],
                                  lambda: s.dwell_or_propose("formality", "evt", "hmm ok")["status"],
                                  pause_at_second_clock_call(s))
    need(not b_early, "thread B finished while A was paused between its changes to memory")
    need(ra == rb == "dwelling", f"statuses {ra!r}, {rb!r}")
    ds = saved_dwellings(s)
    need("curiosity" in ds and "formality" in ds, f"a dwelling was lost: saved dwellings {ds}")
    g = saved_state(s)["generation"]
    need(g == g0 + 2, f"saved generation {g}, expected {g0 + 2}")
    audit_ok(K, o, expect_loads(K, s.data_dir))
    return f"B waited for A's whole operation; generation {g0} -> {g}"


def T73_unconfirmed_save_leaves_object_unusable(K, d):
    """ChatGPT, round 7, F2 (double fault)."""
    s, o = born(K, d)
    real_fsync, real_gen = K.os.fsync, s._saved_generation
    phase = {"fsync": False, "reread": False}

    def fsync(fd):
        if not phase["fsync"] and stat.S_ISDIR(os.fstat(fd).st_mode) and saved_seq(s) == 1:
            phase["fsync"] = True
            raise OSError("injected: directory fsync failed after the organism's replace")
        return real_fsync(fd)

    def gen():
        if phase["fsync"] and not phase["reread"]:
            phase["reread"] = True
            raise OSError("injected: re-reading the saved generation failed")
        return real_gen()
    K.os.fsync, s._saved_generation = fsync, gen
    try:
        o.attest(s)
    except OSError:
        pass
    else:
        raise Fail("injected failure did not happen")
    finally:
        K.os.fsync = real_fsync
        del s._saved_generation
    need(phase["fsync"] and phase["reread"], f"injection points not both reached: {phase}")
    need(s.checkpoint.sequence == 1 and saved_seq(s) == 1,
         f"memory at checkpoint {s.checkpoint.sequence}, saved state at {saved_seq(s)}")
    why = expect_stale_reason(K, lambda: s.dwell_or_propose("formality", "evt", "hmm ok"), "unusable")
    f = expect_loads(K, s.data_dir)
    audit_ok(K, o, f)
    need(fresh_witness_seq(K, d, f) == 1, f"witness at {fresh_witness_seq(K, d, f)}, expected 1")
    return why


def T74_stale_object_refused_before_memory_changes(K, d):
    """ChatGPT, round 7, F3."""
    s, o = born(K, d)
    old = expect_loads(K, s.data_dir)
    dwell(s, "formality", "hmm ok")

    def snap(x):
        return (len(x.trace), len(x.basin), sorted(x.pending), dict(x.character))
    before = snap(old)
    why = expect_stale(K, lambda: old.dwell_or_propose("formality", "evt", "hmm ok"))
    expect_stale(K, lambda: old.dwell_or_propose("verbosity", "evt", PREF))
    need(snap(old) == before, f"the stale object's memory changed: {before} -> {snap(old)}")
    return why


def T75_answer_through_stale_object_records_nothing(K, d):
    """Author A3; ChatGPT, round 7, F3."""
    s, o = born(K, d)
    r = propose(s, "verbosity")
    pid = r["proposal_id"]
    old = expect_loads(K, s.data_dir)
    dwell(s, "formality", "hmm ok")
    n = len(old.trace)
    why = expect_stale(K, lambda: o.answer(old, pid, "no"))
    need("was not recorded" in why, f"the refusal does not say the answer was not recorded: {why!r}")
    need(o.ledger.answers_to(s.organism_id, pid) == [], f"the ledger recorded {o.ledger.answers_to(s.organism_id, pid)}")
    need(not [e for e in saved_state(s)["trace"] if e.get("event") == "owner_answer"], "the organism recorded the answer")
    need(len(old.trace) == n, "the stale object's trace changed")
    f = expect_loads(K, s.data_dir)
    o.answer(f, pid, "no")
    need(o.ledger.answers_to(s.organism_id, pid) == ["no"],
         f"after reload, the ledger holds {o.ledger.answers_to(s.organism_id, pid)}")
    last = saved_state(s)["trace"][-1]
    need(last.get("event") == "owner_answer" and last.get("answer") == "no", f"saved trace ends with {last.get('event')}")
    return why


def T76_write_landing_during_an_operation_is_not_overwritten(K, d):
    """The save's own generation check: a write through a callback, same thread."""
    s, o = born(K, d)
    r = propose(s, "verbosity")
    sig = o.sign_proposal(r["payload_to_sign"])
    b = expect_loads(K, s.data_dir)
    calls = []

    def reader(reading, terrain, events_since):
        if not calls:
            calls.append(b.dwell_or_propose("formality", "evt", "hmm ok")["status"])
        return None
    s.reader = reader
    why = expect_stale(K, lambda: s.authorize_and_apply(r["proposal_id"], sig))
    need(calls == ["dwelling"], f"the reader's write did not happen as set up: {calls}")
    st = saved_state(s)
    ds = [e.get("category") for e in st["trace"] if e.get("event") == "dwelling"]
    need("formality" in ds, f"b's dwelling was overwritten: saved dwellings {ds}")
    need(st["mutation_sequence"] == 0 and near(st["character"]["verbosity"], 0.5),
         f"the crossing reached disk: mutation_sequence {st['mutation_sequence']}, verbosity {st['character']['verbosity']}")
    audit_ok(K, o, expect_loads(K, s.data_dir))
    return why


def T77_hatch_refuses_a_file_without_generation(K, d):
    """Author A1 (sealed 2026-10-19T14:33:59Z)."""
    s, o = born(K, d)
    st = saved_state(s)
    del st["generation"]
    s._state_path().write_text(json.dumps(st, sort_keys=True, separators=(",", ":")))
    before = s._state_path().read_bytes()
    second = K.HumbleSeed(s.data_dir)
    why = expect_stale_reason(K, lambda: second.hatch(), "no valid generation")
    need(s._state_path().read_bytes() == before, "the hatch changed the file")
    expect_stale_reason(K, lambda: s.dwell_or_propose("formality", "evt", "hmm ok"), "no valid generation")
    need(s._state_path().read_bytes() == before, "the dwell changed the file")
    return why


def T78_restore_after_lifetime_lapse(K, d):
    """R20 (Rusty's ruling, 2026-10-19 11:09 CT)."""
    s, o = born(K, d)
    r = propose(s, "verbosity")
    sig = o.sign_proposal(r["payload_to_sign"])
    res = s.authorize_and_apply(r["proposal_id"], sig)
    need(res is not None, f"apply failed: {s.trace[-1].get('reason')!r}")
    propose(s, "formality", CASUAL)                  # left pending
    entry = o.ledger.signed(s.organism_id, K._sha256(r["payload_to_sign"]))
    ttl = K.policy_ttl(s.constitution)
    o.clock = lambda: entry["signed_at"] + 2 * ttl
    why = expect_refused(K, lambda: o.attest(s), "past its lifetime")
    out = restore_ok(K, o, s)
    need(out.get("status") == "restored", f"restore returned {out}")
    need(s.checkpoint.sequence == 0 and near(s.character["verbosity"], 0.5) and s.mutation_sequence == 0
         and not s.pending,
         f"restored state: checkpoint {s.checkpoint.sequence}, verbosity {s.character['verbosity']}, "
         f"mutation_sequence {s.mutation_sequence}, pending {sorted(s.pending)}")
    last = s.trace[-1]
    need(last.get("event") == "restored", f"last trace event is {last.get('event')!r}")
    kept = s.data_dir / str(last.get("kept_as"))
    need(kept.exists() and hashlib.sha256(kept.read_bytes()).hexdigest() == last.get("discarded_file_sha256"),
         "the discarded file was not kept, or its digest does not match the event")
    need(fresh_witness_seq(K, d, s) == 0, "the witness moved")
    audit_ok(K, o, expect_loads(K, s.data_dir))
    apply_ok(K, s, o, propose(s, "verbosity"))
    need(fresh_witness_seq(K, d, s) == 1, "the new crossing was not attested")
    audit_ok(K, o, expect_loads(K, s.data_dir))
    return f"refused ({why}); restored to checkpoint 0 ({last.get('discarded_entries')} entries discarded); new crossing attested"


def T79_restore_refuses_when_saved_checkpoint_is_not_witness_head(K, d):
    s, o = born(K, d)
    kept = s._state_path().read_bytes()
    attest_ok(K, o, s)
    need(fresh_witness_seq(K, d, s) == 1, "setup: the second attestation did not land")
    s._state_path().write_bytes(kept)
    before = s._state_path().read_bytes()
    why = expect_rollback(K, lambda: o.restore(s), "not the witness head")
    need(s._state_path().read_bytes() == before, "restore changed the file")
    need(fresh_witness_seq(K, d, s) == 1, "the witness moved")
    return why


def T80_restore_refuses_a_rewritten_attested_prefix(K, d):
    s, o = born(K, d)
    dwell(s, "formality", "hmm ok")
    attest_ok(K, o, s)
    idx = next(i for i, e in enumerate(s.trace) if e.get("event") == "dwelling")
    need(idx < s.checkpoint.attested_trace_len, "setup: the dwelling is not inside the attested prefix")

    def rewrite(st):
        st["trace"][idx]["reason"] = "rewritten after attestation"
    K._reseal_attack(s, rewrite, rechain=True)
    before = s._state_path().read_bytes()
    try:
        o.restore(s)
    except K.IntegrityError as e:
        need("attested prefix does not match the checkpoint" in str(e), f"refused for a different reason: {e}")
        why = str(e)
    else:
        raise Fail("restore accepted a rewritten attested prefix")
    need(s._state_path().read_bytes() == before, "restore changed the file")
    return why


def T81_restore_completes_a_pending_commit_first(K, d):
    s, o = born(K, d)
    real = o.witness.commit

    def interrupted(cp):
        raise OSError("injected: interrupted after the organism installed, before the witness advanced")
    o.witness.commit = interrupted
    try:
        o.attest(s)
    except OSError:
        pass
    else:
        raise Fail("injected interruption did not happen")
    finally:
        o.witness.commit = real
    w = K.OwnerWitness(d / "witness.json")
    need(w.ledger[s.organism_id]["sequence"] == 0 and w.pending_for(s.organism_id) is not None and saved_seq(s) == 1,
         "setup: expected witness 0 with an intent pending and the organism at checkpoint 1")
    out = restore_ok(K, o, s)
    need(out.get("status") == "restored" and out.get("checkpoint_sequence") == 1, f"restore returned {out}")
    w = K.OwnerWitness(d / "witness.json")
    need(w.ledger[s.organism_id]["sequence"] == 1 and w.pending_for(s.organism_id) is None,
         "the pending commit was not completed")
    audit_ok(K, o, expect_loads(K, s.data_dir))
    return "pending commit completed, then restored at checkpoint 1"


TESTS = TESTS + [T70_two_threads_one_object_lose_no_dwelling, T71_two_threads_attest_cannot_be_rewound,
                 T72_operation_is_atomic_across_threads, T73_unconfirmed_save_leaves_object_unusable,
                 T74_stale_object_refused_before_memory_changes, T75_answer_through_stale_object_records_nothing,
                 T76_write_landing_during_an_operation_is_not_overwritten, T77_hatch_refuses_a_file_without_generation,
                 T78_restore_after_lifetime_lapse, T79_restore_refuses_when_saved_checkpoint_is_not_witness_head,
                 T80_restore_refuses_a_rewritten_attested_prefix, T81_restore_completes_a_pending_commit_first]


def S1_two_threads_stress(K, d, seconds=3.0):
    """Candidate only: two threads on one object, a timed run."""
    s, o = born(K, d)
    stop = time.time() + seconds
    a_ok, b_ok = [0], [0]

    def A():
        while time.time() < stop:
            if s.dwell_or_propose("formality", "evt", "hmm ok")["status"] == "dwelling":
                a_ok[0] += 1

    def B():
        while time.time() < stop:
            r = s.dwell_or_propose("verbosity", "evt", PREF)
            if r["status"] == "proposal":
                s.authorize_and_apply(r["proposal_id"], o.sign_proposal(r["payload_to_sign"]))
            if o.attest(s) is True:
                b_ok[0] += 1
    boxes = [_start(A, "S1-A"), _start(B, "S1-B")]
    for box in boxes:
        need(box["done"].wait(120), "a stress thread did not finish")
    for box in boxes:
        if "error" in box:
            raise box["error"]
    st = saved_state(s)
    saved = sum(1 for e in st["trace"] if e.get("event") == "dwelling" and e.get("category") == "formality")
    need(saved == a_ok[0], f"{a_ok[0]} dwellings returned, {saved} saved")
    need(st["checkpoint"]["sequence"] == fresh_witness_seq(K, d, s),
         f"saved checkpoint {st['checkpoint']['sequence']}, witness {fresh_witness_seq(K, d, s)}")
    audit_ok(K, o, expect_loads(K, s.data_dir))
    return f"{a_ok[0]} dwellings and {b_ok[0]} attestations; all saved; checkpoint = witness"


CANDIDATE_ONLY = [S1_two_threads_stress]
'''

once('''                 T68_attest_refuses_a_stale_object_before_signing, T69_organism_lock_held_for_saves_and_attest]
''', '''                 T68_attest_refuses_a_stale_object_before_signing, T69_organism_lock_held_for_saves_and_attest]
''' + NEW)

# main: candidate-only checks
once('''    if names != list(declared["tests"]):
        raise SystemExit("harness tests differ from the declared tests; refusing to run")
''', '''    if names != list(declared["tests"]):
        raise SystemExit("harness tests differ from the declared tests; refusing to run")
    if [c.__name__ for c in CANDIDATE_ONLY] != list(declared.get("candidate_only_checks", {})):
        raise SystemExit("harness candidate-only checks differ from the declared ones; refusing to run")
''')
once('''    passing = {n for n, r in base.items() if r["status"] == "PASS"}
''', '''    cand_only = {}
    for check in CANDIDATE_ONLY:
        d = Path(tempfile.mkdtemp(prefix="hs087_check_"))
        try:
            cand_only[check.__name__] = {"status": "PASS", "detail": str(check(K, d))}
        except Fail as f:
            cand_only[check.__name__] = {"status": "FAIL", "detail": str(f)}
        except Exception as e:
            cand_only[check.__name__] = {"status": "ERROR", "detail": f"{type(e).__name__}: {e}"}
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print(f"\\n{'CANDIDATE-ONLY CHECK':48s} {'DECLARED':9s} {'MEASURED':9s} VERDICT")
    for name, spec in declared.get("candidate_only_checks", {}).items():
        got = cand_only[name]["status"]
        ok = (got == spec["expect"])
        mismatches += (not ok)
        print(f"{name:48s} {spec['expect']:9s} {got:9s} {'MATCH' if ok else 'MISMATCH'}")
        print(f"    -> {cand_only[name]['detail']}")

    passing = {n for n, r in base.items() if r["status"] == "PASS"}
''')
once('''    normalized = {"tests": {n: r["status"] for n, r in base.items()},
''', '''    normalized = {"tests": {n: r["status"] for n, r in base.items()},
                  "candidate_only": {n: r["status"] for n, r in cand_only.items()},
''')
once('''               "parent_v07_sha256": _sha(PARENT_V07), "tests": base, "mutants": mut_results,
''', '''               "parent_v07_sha256": _sha(PARENT_V07), "tests": base, "candidate_only": cand_only,
               "mutants": mut_results,
''')

out_path.write_text(src, encoding="utf-8")
print("written", out_path)
