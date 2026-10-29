#!/usr/bin/env python3
"""
Identity-substitution attacks against Humble Seed's OwnerTool.audit.

Usage:
    python3 -I attack_identity_substitution.py <path/to/humble_seed_module.py> [--witness-binds-expected]

Threat model is the one v0.5+ already assumes: the attacker can WRITE the
organism's state file, but has neither the owner's private key nor write access
to the owner's witness ledger (R1 is not exercised here).

Attack S1 (unknown id): the attacker hatches a fresh organism with their own
key, gives it a permissive constitution and an arbitrary character, signs
its genesis checkpoint with THEIR key, and copies the state file over the
owner's. The owner then loads and audits their own directory.

Attack S2 (enrolled sibling): the owner's witness ledger holds two organisms,
A and B. The attacker copies B's genuine, owner-attested current state over
A's directory. The owner audits A's directory.

Each attack prints whether the owner's audit ACCEPTED the substituted state.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path


def load_module(path: str):
    spec = importlib.util.spec_from_file_location("humble_seed_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["humble_seed_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def audit(hs, owner, data_dir, expected_oid):
    """Run the module's own audit path on whatever is in data_dir."""
    fresh = hs.HumbleSeed(data_dir=data_dir)
    try:
        fresh.load()
    except Exception as ex:          # load() failing closed is a rejection
        return False, f"load rejected: {type(ex).__name__}: {ex}", None
    try:
        # v0.7.1 candidate takes the expected organism id; v0.7 does not.
        try:
            ok = owner.audit(fresh, expected_organism_id=expected_oid)
        except TypeError:
            ok = owner.audit(fresh)
        return bool(ok), "audit returned True", fresh
    except Exception as ex:
        return False, f"audit rejected: {type(ex).__name__}: {ex}", fresh


def owner_organism(hs, data_dir, witness):
    """Owner hatches, attests genesis, applies one legitimate mutation, attests."""
    seed = hs.HumbleSeed(data_dir=data_dir)
    oid, pem, gcp = seed.hatch()
    owner = hs.OwnerTool(pem, witness)
    assert owner.attest(seed, gcp)
    r = seed.dwell_or_propose("verbosity", "len", "I always prefer shorter answers")
    cp = seed.authorize_and_apply(r["proposal_id"], owner.sign_proposal(r["payload_to_sign"]))
    assert cp is not None and owner.attest(seed, cp)
    return seed, oid, pem, owner


def attacker_organism(hs, data_dir):
    """Attacker builds a self-consistent organism under their OWN key."""
    seed = hs.HumbleSeed(data_dir=data_dir)
    oid, attacker_pem, _ = seed.hatch()
    # Permissive constitution, rebuilt so every local cross-check is consistent.
    seed.constitution["rule"] = "The organism may authorize its own growth."
    seed.constitution["invariants"] = []
    ch = hs._sha256(hs._canonical_json(seed.constitution))
    seed.birth.constitution_hash = ch
    seed.birth.genesis_hash = hs.HumbleSeed._derive_genesis(
        seed.birth.organism_id, seed.birth.public_key_b64, seed.birth.created_at, ch)
    birth_entry = {k: v for k, v in seed.trace[0].items() if k not in ("prev_hash", "entry_hash")}
    birth_entry["constitution_hash"] = ch
    birth_entry["genesis_hash"] = seed.birth.genesis_hash
    seed.trace = []
    seed._trace_head = "0" * 64
    seed._append_trace(birth_entry)
    seed.character = {"verbosity": 0.99, "formality": 0.01, "curiosity": 0.99}
    cp = seed.checkpoint_request()
    sig = hs.owner_sign_external(attacker_pem, hs.HumbleSeed.checkpoint_payload(cp))
    assert seed.install_checkpoint(cp, sig), "attacker could not install own checkpoint"
    return seed, oid, attacker_pem


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    hs = load_module(sys.argv[1])
    print(f"module under test : {sys.argv[1]}  (SCHEMA_VERSION {hs.SCHEMA_VERSION})")
    results = {}
    root = Path(tempfile.mkdtemp(prefix="hs_attack_"))
    try:
        # ---------------- S1: unknown organism id -----------------------
        d_owner = root / "s1_owner"
        d_att = root / "s1_attacker"
        witness = hs.OwnerWitness(root / "s1_witness.json")
        seed, oid_a, _, owner = owner_organism(hs, d_owner, witness)
        ok, why, _ = audit(hs, owner, d_owner, oid_a)
        print(f"\n[S1] baseline audit of owner's own organism : {ok}  ({why})")
        assert ok, "baseline must pass or the attack proves nothing"

        att_seed, oid_x, attacker_pem = attacker_organism(hs, d_att)
        shutil.copy(att_seed._state_path(), seed._state_path())
        ok, why, fresh = audit(hs, owner, d_owner, oid_a)
        print(f"[S1] audit after wholesale substitution      : {'ACCEPTED' if ok else 'rejected'}  ({why})")
        if fresh is not None and ok:
            print(f"     organism id now        : {fresh.organism_id}  (owner enrolled {oid_a})")
            print(f"     constitution rule now  : {fresh.constitution['rule']!r}")
            print(f"     character now          : {fresh.character}")
            # The substituted organism now accepts mutations signed by the attacker.
            r = fresh.dwell_or_propose("formality", "tone", "I always prefer shorter answers")
            cp = fresh.authorize_and_apply(
                r["proposal_id"], hs.owner_sign_external(attacker_pem, r["payload_to_sign"]))
            applied = cp is not None
            if applied:
                fresh.install_checkpoint(cp, hs.owner_sign_external(
                    attacker_pem, hs.HumbleSeed.checkpoint_payload(cp)))
            ok2, why2, _ = audit(hs, owner, d_owner, oid_a)
            print(f"     attacker-signed mutation applied : {applied}")
            print(f"     owner audit still passes         : {ok2}  ({why2})")
        results["S1_unknown_id_accepted"] = ok

        # ---------------- S2: enrolled sibling --------------------------
        witness2 = hs.OwnerWitness(root / "s2_witness.json")
        seed_a, oid_a2, _, owner_a = owner_organism(hs, root / "s2_A", witness2)
        seed_b, oid_b2, _, owner_b = owner_organism(hs, root / "s2_B", witness2)
        ok, why, _ = audit(hs, owner_a, root / "s2_A", oid_a2)
        print(f"\n[S2] baseline audit of A (shared witness)   : {ok}  ({why})")
        assert ok
        shutil.copy(seed_b._state_path(), seed_a._state_path())
        ok, why, fresh = audit(hs, owner_a, root / "s2_A", oid_a2)
        print(f"[S2] audit of A's dir holding B's state      : {'ACCEPTED' if ok else 'rejected'}  ({why})")
        if fresh is not None and ok:
            print(f"     organism id now : {fresh.organism_id}  (expected {oid_a2})")
        results["S2_enrolled_sibling_accepted"] = ok

        # ---------------- S3: same id, new key (control: v0.7 M1 should catch)
        witness3 = hs.OwnerWitness(root / "s3_witness.json")
        seed3, oid3, _, owner3 = owner_organism(hs, root / "s3_owner", witness3)
        att3, _, att_pem3 = attacker_organism(hs, root / "s3_att")
        # Re-label the attacker's organism with the victim's id, rebuild consistently.
        att3.organism_id = oid3
        att3.birth.organism_id = oid3
        att3.birth.genesis_hash = hs.HumbleSeed._derive_genesis(
            oid3, att3.birth.public_key_b64, att3.birth.created_at, att3.birth.constitution_hash)
        be = {k: v for k, v in att3.trace[0].items() if k not in ("prev_hash", "entry_hash")}
        be["organism_id"] = oid3
        be["genesis_hash"] = att3.birth.genesis_hash
        att3.trace = []; att3._trace_head = "0" * 64; att3._append_trace(be)
        att3.checkpoint = None; att3.checkpoint_sig = None
        cp = att3.checkpoint_request()
        assert att3.install_checkpoint(cp, hs.owner_sign_external(att_pem3, hs.HumbleSeed.checkpoint_payload(cp)))
        shutil.copy(att3._state_path(), seed3._state_path())
        ok, why, _ = audit(hs, owner3, root / "s3_owner", oid3)
        print(f"\n[S3] control: victim's id under a new key    : {'ACCEPTED' if ok else 'rejected'}  ({why})")
        results["S3_same_id_new_key_accepted"] = ok
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("\nRESULTS " + json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
