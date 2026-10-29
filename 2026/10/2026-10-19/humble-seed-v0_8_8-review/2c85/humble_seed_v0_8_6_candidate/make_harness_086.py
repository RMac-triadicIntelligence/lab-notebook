#!/usr/bin/env python3
"""Derives falsify_v0_8_6.py from falsify_v0_8_5.py. Written after DECLARED_v0_8_6 was frozen."""
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


once('Falsification harness for humble_seed_v0_8_5_candidate.py  (v0.8.5)\n\nWritten AFTER DECLARED_v0_8_5.json was frozen.',
     'Falsification harness for humble_seed_v0_8_6_candidate.py  (v0.8.6)\n\nWritten AFTER DECLARED_v0_8_6.json was frozen.')
once("Run:  python3 -I falsify_v0_8_5.py", "Run:  python3 -I falsify_v0_8_6.py")
once("import json\nimport shutil\n", "import json\nimport os\nimport shutil\nimport stat\n")
once('CANDIDATE = HERE / "humble_seed_v0_8_5_candidate.py"', 'CANDIDATE = HERE / "humble_seed_v0_8_6_candidate.py"')
once('DECL = HERE / "DECLARED_v0_8_5.json"', 'DECL = HERE / "DECLARED_v0_8_6.json"')
once('DECL_SHA = HERE / "DECLARED_v0_8_5.sha256"', 'DECL_SHA = HERE / "DECLARED_v0_8_6.sha256"')
once('DECL_AT = HERE / "DECLARED_v0_8_5.frozen_at"', 'DECL_AT = HERE / "DECLARED_v0_8_6.frozen_at"')
once('raise SystemExit("DECLARED_v0_8_5.json differs', 'raise SystemExit("DECLARED_v0_8_6.json differs')
once('print("Humble Seed v0.8.5 CANDIDATE — falsification harness")',
     'print("Humble Seed v0.8.6 CANDIDATE — falsification harness")')
once('K = load_module(CANDIDATE, "hs085_candidate")', 'K = load_module(CANDIDATE, "hs086_candidate")')
every('prefix="hs085_', 'prefix="hs086_', 2)
once('(HERE / "RESULTS_v0_8_5.json")', '(HERE / "RESULTS_v0_8_6.json")')
once('print("RESULTS_v0_8_5.json written.', 'print("RESULTS_v0_8_6.json written.')
once('    s, o = born(K, d / "v085")', '    s, o = born(K, d / "v086")')
once('return (f"v0.8.5 applied {applied}/4', 'return (f"v0.8.6 applied {applied}/4')

# T57 corrected (v0.8.5 DEVIATIONS E1): the check that actually fires first
once('''    need(got.startswith("IntegrityError") and "Unattested authorizing event" in got,''',
     '''    need(got.startswith("IntegrityError") and "Category sequences do not match the attested checkpoint" in got,''')

NEW = r'''

# ---------------------------------------------------------------------------
# New in v0.8.6 (T62–T69): one organism persistence protocol
# ---------------------------------------------------------------------------

def expect_stale(K, fn):
    try:
        fn()
    except K.StaleOrganism as e:
        need("stale organism object" in str(e), f"StaleOrganism for a different reason: {str(e)!r}")
        return str(e)
    raise Fail("stale write ACCEPTED")


def T62_stale_object_cannot_overwrite_newer_state(K, d):
    """ChatGPT, round 6, F1 (stale_public_write)."""
    s, o = born(K, d)
    old = expect_loads(K, s.data_dir)
    apply_ok(K, s, o, propose(s, "verbosity"))
    why = expect_stale(K, lambda: old.dwell_or_propose("formality", "evt", "hmm ok"))
    need(saved_seq(s) == 1, f"saved state rewound to checkpoint {saved_seq(s)}")
    f = expect_loads(K, s.data_dir)
    need(near(f.character["verbosity"], 0.25), f"verbosity {f.character['verbosity']}")
    audit_ok(K, o, f)
    dwell(f, "formality", "hmm ok")
    return why


def T63_stale_write_during_attest_is_refused(K, d):
    """ChatGPT, round 6, F1 (advanced_memory_save_during_attest)."""
    s, o = born(K, d)
    old = expect_loads(K, s.data_dir)
    apply_ok(K, s, o, propose(s, "verbosity"), attest=False)
    real = o.witness.commit
    seen = []

    def commit_with_stale_write(cp):
        try:
            old.dwell_or_propose("formality", "evt", "hmm ok")
            seen.append("stale write ACCEPTED")
        except K.StaleOrganism as e:
            seen.append(f"StaleOrganism: {e}")
        return real(cp)
    o.witness.commit = commit_with_stale_write
    try:
        attest_ok(K, o, s)
    finally:
        o.witness.commit = real
    need(len(seen) == 1 and seen[0].startswith("StaleOrganism") and "stale organism object" in seen[0],
         f"stale write during attest: {seen}")
    need(saved_seq(s) == 1 and fresh_witness_seq(K, d, s) == 1,
         f"saved state at {saved_seq(s)}, witness at {fresh_witness_seq(K, d, s)}")
    f = expect_loads(K, s.data_dir)
    audit_ok(K, o, f)
    return seen[0]


def T64_interrupted_commit_then_stale_write_keeps_signoff(K, d):
    """ChatGPT, round 6, F1 (interrupted_commit_stale_write)."""
    s, o = born(K, d)
    old = expect_loads(K, s.data_dir)
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
    why = expect_stale(K, lambda: old.dwell_or_propose("formality", "evt", "hmm ok"))
    f = expect_loads(K, s.data_dir)
    need(f.checkpoint.sequence == 1 and near(f.character["verbosity"], 0.25),
         f"saved state at checkpoint {f.checkpoint.sequence}, verbosity {f.character['verbosity']}")
    audit_ok(K, reopen(K, o, d), f)
    w = K.OwnerWitness(d / "witness.json")
    need(w.ledger[s.organism_id]["sequence"] == 1 and w.pending_for(s.organism_id) is None,
         "recovery did not complete the signed-off intent")
    return why


def T65_failure_after_replace_keeps_memory_with_disk(K, d):
    """ChatGPT, round 6, F2 (post_replace_fsync_failure)."""
    s, o = born(K, d)
    apply_ok(K, s, o, propose(s, "verbosity"), attest=False)
    real_fsync = K.os.fsync
    fired = []

    def fsync_failing_after_replace(fd):
        if not fired and stat.S_ISDIR(os.fstat(fd).st_mode) and saved_seq(s) == 1:
            fired.append(True)
            raise OSError("injected: directory fsync failed after the organism's replace")
        return real_fsync(fd)
    K.os.fsync = fsync_failing_after_replace
    try:
        o.attest(s)
    except OSError:
        pass
    else:
        raise Fail("injected failure did not happen")
    finally:
        K.os.fsync = real_fsync
    need(fired, "the injection point was not reached")
    need(s.checkpoint.sequence == 1 and saved_seq(s) == 1,
         f"after the failure: object at {s.checkpoint.sequence}, saved state at {saved_seq(s)}")
    w = K.OwnerWitness(d / "witness.json")
    need(w.ledger[s.organism_id]["sequence"] == 0 and w.pending_for(s.organism_id) is not None,
         "expected the witness at 0 with the intent pending")
    attest_ok(K, o, s)
    f = expect_loads(K, s.data_dir)
    audit_ok(K, o, f)
    need(fresh_witness_seq(K, d, f) == 2, f"witness at {fresh_witness_seq(K, d, f)}, expected 2")
    return "replace landed before the failure; memory kept with disk; same-object retry attested"


def T66_recovery_refuses_a_saved_state_that_does_not_verify(K, d):
    """Author A1 (sealed 2026-10-19T12:34Z)."""
    s, o = born(K, d)
    apply_ok(K, s, o, propose(s, "verbosity"), attest=False)
    real = s.install_checkpoint

    def crash_before(cp, sig):
        raise OSError("interrupted before the organism installed")
    s.install_checkpoint = crash_before
    try:
        o.attest(s)
    except OSError:
        pass
    else:
        raise Fail("injected interruption did not happen")
    finally:
        s.install_checkpoint = real
    p = K.OwnerWitness(d / "witness.json").pending_for(s.organism_id)
    need(p is not None, "no pending intent after the interrupted attest")
    original = s._state_path().read_text()
    st = json.loads(original)
    st["checkpoint"], st["checkpoint_sig"] = p["checkpoint"], p["signature_b64"]
    st["character"]["formality"] = 0.99
    s._state_path().write_text(json.dumps(st, sort_keys=True, separators=(",", ":")))
    try:
        o.audit(s)
        got = "audit returned"
    except (K.RollbackDetected, K.IntegrityError) as e:
        got = f"{type(e).__name__}: {e}"
    need(got.startswith("RollbackDetected") and "claims it but does not verify" in got,
         f"audit on the forged saved state: {got}")
    w = K.OwnerWitness(d / "witness.json")
    need(w.ledger[s.organism_id]["sequence"] == 0 and w.pending_for(s.organism_id) is not None,
         "the witness moved, or the intent was dropped")
    s._state_path().write_text(original)
    attest_ok(K, o, s)
    f = expect_loads(K, s.data_dir)
    audit_ok(K, o, f)
    need(fresh_witness_seq(K, d, f) == 1, "witness not at 1 after the restore")
    return got


def T67_hatch_cannot_overwrite_an_existing_organism(K, d):
    s, o = born(K, d)
    before = s._state_path().read_bytes()
    second = K.HumbleSeed(s.data_dir)
    why = expect_stale(K, lambda: second.hatch())
    need(s._state_path().read_bytes() == before, "the saved organism was overwritten")
    f = expect_loads(K, s.data_dir)
    audit_ok(K, o, f)
    return why


def T68_attest_refuses_a_stale_object_before_signing(K, d):
    s, o = born(K, d)
    old = expect_loads(K, s.data_dir)
    dwell(s, "formality", "hmm ok")
    why = expect_stale(K, lambda: o.attest(old))
    w = K.OwnerWitness(d / "witness.json")
    need(w.ledger[s.organism_id]["sequence"] == 0 and w.pending_for(s.organism_id) is None,
         "attest of a stale object moved the witness or left an intent pending")
    attest_ok(K, o, s)
    return why


def T69_organism_lock_held_for_saves_and_attest(K, d):
    s, o = born(K, d)
    lock = s.data_dir / "organism.lock"

    def probe():
        return subprocess.run([sys.executable, "-I", "-c", LOCK_PROBE, str(lock)],
                              capture_output=True, text=True, timeout=30).stdout.strip()
    during_save, during_attest = [], []
    real_write = K._durable_write

    def probing_write(path, text):
        if Path(path) == s._state_path():
            during_save.append(probe())
        return real_write(path, text)
    K._durable_write = probing_write
    try:
        dwell(s, "formality", "hmm ok")
    finally:
        K._durable_write = real_write
    real_check = o.witness.check_successor

    def probing_check(cp):
        during_attest.append(probe())
        return real_check(cp)
    o.witness.check_successor = probing_check
    try:
        attest_ok(K, o, s)
    finally:
        o.witness.check_successor = real_check
    need(during_save and all(x == "locked" for x in during_save), f"organism lock during a save: {during_save}")
    need(during_attest and all(x == "locked" for x in during_attest), f"organism lock during attest: {during_attest}")
    after = probe()
    need(after == "free", f"organism lock still held after attest: {after!r}")
    return f"held during a save ({len(during_save)} probe) and attest ({len(during_attest)} probes); free after"


TESTS = TESTS + [T62_stale_object_cannot_overwrite_newer_state, T63_stale_write_during_attest_is_refused,
                 T64_interrupted_commit_then_stale_write_keeps_signoff, T65_failure_after_replace_keeps_memory_with_disk,
                 T66_recovery_refuses_a_saved_state_that_does_not_verify, T67_hatch_cannot_overwrite_an_existing_organism,
                 T68_attest_refuses_a_stale_object_before_signing, T69_organism_lock_held_for_saves_and_attest]
'''

once('''                 T61_owner_no_before_signing_holds_later_crossing]
''', '''                 T61_owner_no_before_signing_holds_later_crossing]
''' + NEW)

out_path.write_text(src, encoding="utf-8")
print("written", out_path)
