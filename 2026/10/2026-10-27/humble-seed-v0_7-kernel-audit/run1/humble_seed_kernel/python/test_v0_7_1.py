#!/usr/bin/env python3
"""
Extra checks for the v0.7.1 candidate that the attack script does not isolate.

  T1  K1 on its own: the owner is handed the attacker's organism id as the
      "expected" id (so K2 passes). check_current must still refuse, because
      the witness never enrolled that id.
  T2  Liveness: a legitimate organism through several attested mutations
      audits cleanly, with and without an explicit expected id.
  T3  Rollback detection is unchanged (v0.7 test [10]) under the new audit.
  T4  A fresh OwnerTool that attested nothing refuses to audit without an id.

Usage: python3 -I test_v0_7_1.py <humble_seed_v0_7_1.py>
"""
import json
import runpy
import shutil
import sys
import tempfile
from pathlib import Path

here = Path(__file__).resolve().parent
attack = runpy.run_path(str(here / "attack_identity_substitution.py"), run_name="attack_lib")
hs = attack["load_module"](sys.argv[1])
results = {}
root = Path(tempfile.mkdtemp(prefix="hs_t071_"))
try:
    # T1
    w = hs.OwnerWitness(root / "t1_w.json")
    seed, oid, _, owner = attack["owner_organism"](hs, root / "t1_owner", w)
    att, oid_x, _ = attack["attacker_organism"](hs, root / "t1_att")
    shutil.copy(att._state_path(), seed._state_path())
    fresh = hs.HumbleSeed(data_dir=root / "t1_owner"); fresh.load()
    try:
        owner.audit(fresh, expected_organism_id=oid_x)
        results["T1_K1_alone_rejects_unenrolled"] = False
        print("[T1] audit with attacker id as expected: ACCEPTED — FAIL")
    except hs.RollbackDetected as ex:
        results["T1_K1_alone_rejects_unenrolled"] = str(ex).startswith("Unenrolled organism")
        print(f"[T1] audit with attacker id as expected: rejected ({ex})")

    # T2
    w2 = hs.OwnerWitness(root / "t2_w.json")
    s2, oid2, _, o2 = attack["owner_organism"](hs, root / "t2", w2)
    for cat in ("formality", "curiosity", "verbosity"):
        r = s2.dwell_or_propose(cat, "x", "I always prefer shorter answers")
        cp = s2.authorize_and_apply(r["proposal_id"], o2.sign_proposal(r["payload_to_sign"]))
        assert cp is not None and o2.attest(s2, cp)
    f2 = hs.HumbleSeed(data_dir=root / "t2"); f2.load()
    ok_implicit = o2.audit(f2)
    ok_explicit = o2.audit(f2, expected_organism_id=oid2)
    fresh_tool = hs.OwnerTool("unused", w2)
    ok_fresh_tool = fresh_tool.audit(f2, expected_organism_id=oid2)
    results["T2_liveness"] = ok_implicit and ok_explicit and ok_fresh_tool
    print(f"[T2] legit organism, seq {f2.checkpoint.sequence}: implicit={ok_implicit} "
          f"explicit={ok_explicit} fresh-tool-with-id={ok_fresh_tool}")

    # T3
    snap = s2._state_path().read_text()
    r = s2.dwell_or_propose("formality", "x", "I always prefer shorter answers")
    cp = s2.authorize_and_apply(r["proposal_id"], o2.sign_proposal(r["payload_to_sign"]))
    assert o2.attest(s2, cp)
    s2._state_path().write_text(snap)
    rolled = hs.HumbleSeed(data_dir=root / "t2"); rolled.load()
    try:
        o2.audit(rolled)
        results["T3_rollback_detected"] = False
        print("[T3] rollback: ACCEPTED — FAIL")
    except hs.RollbackDetected as ex:
        results["T3_rollback_detected"] = str(ex).startswith("Rollback")
        print(f"[T3] rollback: rejected ({ex})")

    # T4
    try:
        hs.OwnerTool("unused", w2).audit(f2)
        results["T4_needs_expected_id"] = False
        print("[T4] tool with no attestation, no id: ACCEPTED — FAIL")
    except hs.IntegrityError as ex:
        results["T4_needs_expected_id"] = True
        print(f"[T4] tool with no attestation, no id: rejected ({ex})")
finally:
    shutil.rmtree(root, ignore_errors=True)

print("\nRESULTS " + json.dumps(results, sort_keys=True))
sys.exit(0 if all(results.values()) else 1)
