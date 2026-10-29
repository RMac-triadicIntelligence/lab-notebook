"""Careful-adversary battery against the v1.1.6 candidate (layer 2 + -I).

Threat model for layer 2: the notary is FULLY compromised and may report any head it likes.
Its real power is therefore: (a) the genuine signed envelopes the organism legitimately holds
(session.material: ISSUED authorize, REFUSED refuse, EXPIRED authorize-but-lapsed), (b) the
ability to construct its own engine (so it controls its own clock), and (c) the ability to
report any records/proofs/state over the judge channel. The judge (judge_verify) gets its
inputs from session setup, never from the notary: public key, authority_id, organism_id,
initial_state.

Nothing is fixed to make these pass. Each attack prints the judge verdict and whether it is a
BREACH = the judge said VERIFIED for a head that is not the honest juvenile-at-initial-state,
or that hides a real commit.
"""
import copy, importlib.util, json, os, re, subprocess, sys, time
sys.path.insert(0, "."); import session, supervisor, judge_verify as JV
ROOT = os.path.dirname(os.path.abspath("."))
T0 = session.T0
INIT = session.INITIAL_STATE


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
    spec.loader.exec_module(mod); return mod

m = load("core.py", "lscs_core_battery")


def judge(head, cfg):
    return JV.verify_ledger(head, cfg["public_key_hex"], cfg["authority_id"],
                            cfg["organism_id"], INIT)


def honest_head_via_notary(cfg, submissions, clock_t0=None):
    """Drive the REAL notary.py; optionally with a backdated engine clock. Returns its head."""
    c = dict(cfg)
    if clock_t0 is not None:
        c["clock_t0"] = clock_t0
    h = supervisor.NotaryHandle(ROOT, c, isolation="local")
    o = supervisor.OrgClient(h.org_w, h.org_r)
    outs = [o.request({"op": "commit", "submission": s}) for s in submissions]
    head = h.head(); h.shutdown()
    return outs, head


def show(name, verdict, breach, note=""):
    ok, probs = verdict
    tag = "*** BREACH" if breach else ("VERIFIED" if ok else "held (FORGED)")
    print("%-34s judge=%-13s %s" % (name, "VERIFIED" if ok else "FORGED", tag))
    if note:
        print("      " + note)
    if probs and not breach:
        print("      judge: " + probs[0])
    return breach


def A1_clock_backdate_expired(cfg):
    """Compromised notary builds its engine with a backdated clock and commits the EXPIRED
    (genuinely authority-signed) authorize envelope. Real signature; only 'now' is a lie."""
    _, mat = cfg["_mat"], cfg["_mat"]
    back = T0 - 500  # inside [issued_at=T0-1000, expires_at=T0-10]
    outs, head = honest_head_via_notary(cfg, [cfg["_mat"]["EXPIRED"]], clock_t0=back)
    v = judge(head, cfg)
    changed = head and head["state"] != INIT
    breach = v[0] and changed
    return show("A1 clock-backdate EXPIRED replay", v, breach,
                "commit outcome=%s; state.tone=%s (honest would REFUSE at T0)"
                % (outs[0]["outcome"], head["state"]["personality"].get("tone")))


def A2_rollback_hide_commit(cfg):
    """Honest commit happens; compromised notary then reports an empty ledger (rollback)."""
    outs, real = honest_head_via_notary(cfg, [cfg["_mat"]["ISSUED"]])
    rolled = {"state": copy.deepcopy(INIT), "state_digest": m.sha256_hex(INIT),
              "verify_history": True, "records": [], "proofs": []}
    v = judge(rolled, cfg)
    breach = v[0] and len(real["records"]) > 0  # judge accepts a head that hides a real commit
    return show("A2 rollback / hide real commit", v, breach,
                "real commit outcome=%s (1 record); notary reports 0 records" % outs[0]["outcome"])


def A3_truncate_prefix(cfg):
    """Two real commits; notary reports only the first (drops the later one)."""
    back = T0 - 500
    # commit ISSUED at honest clock won't chain with EXPIRED (future); do EXPIRED-only twice? no.
    # Instead: one real commit (ISSUED), then fabricate nothing; truncation of a 1-chain to 0
    # is A2. For a 2-chain we need two authorizes from evolving state; only ISSUED is valid from
    # INIT. So truncate the ISSUED head to 0 records but keep verify_history True and OLD state.
    outs, real = honest_head_via_notary(cfg, [cfg["_mat"]["ISSUED"]])
    trunc = {"state": copy.deepcopy(real["state"]),           # keeps the mutated state...
             "state_digest": real["state_digest"],
             "verify_history": True, "records": [], "proofs": []}  # ...but no records to justify it
    v = judge(trunc, cfg)
    breach = v[0]
    return show("A3 state kept, records dropped", v, breach,
                "reports mutated state with an empty chain")


def B1_history_key_forge(cfg):
    """Attacker with the history key (see B2) forges an HMAC-valid maturity record.
    verify_history() will say True; the judge should not, because there is no authority proof."""
    key = bytes.fromhex(cfg["history_key_hex"])
    mature = copy.deepcopy(INIT); mature["maturity"] = "mature"
    event = {"sequence": 1, "event": "mutation_committed",
             "trace_digest": "0" * 64, "proposal_digest": "0" * 64,
             "predecessor_digest": m.sha256_hex(INIT), "resulting_digest": m.sha256_hex(mature),
             "authorization_id": "forged-det", "authority_id": cfg["authority_id"],
             "reason": "forged", "timestamp": T0, "previous_record_hash": "0" * 64}
    rec = m.CommitRecord(**event, record_hash=m.record_hash_for(event, key))
    vh = m.verify_record_chain([rec], history_key=key)   # the notary's own self-check
    head = {"state": mature, "state_digest": m.sha256_hex(mature), "verify_history": vh,
            "records": [dict(event, record_hash=rec.record_hash)], "proofs": []}
    v = judge(head, cfg)
    breach = v[0]
    return show("B1 history-key HMAC forgery", v, breach,
                "notary self-check verify_history=%s on the forged record" % vh)


def B2_history_key_extractable(cfg):
    """Is the 32-byte history key present in the notary's readable process memory?
    code_06b showed same-uid can read /proc/<pid>/mem; here we scan (as the launching user)
    for the known key bytes to confirm the confidentiality assumption the key rests on."""
    key = bytes.fromhex(cfg["history_key_hex"])
    h = supervisor.NotaryHandle(ROOT, dict(cfg), isolation="local")
    o = supervisor.OrgClient(h.org_w, h.org_r)
    o.request({"op": "commit", "submission": cfg["_mat"]["ISSUED"]})
    found = False; scanned = 0
    try:
        with open("/proc/%d/maps" % h.pid) as mp:
            regions = [ln for ln in mp if " rw" in ln]
        fd = os.open("/proc/%d/mem" % h.pid, os.O_RDONLY)
        for ln in regions:
            a, b = (int(x, 16) for x in ln.split()[0].split("-"))
            if b - a > 64 * 1024 * 1024:
                continue
            try:
                os.lseek(fd, a, os.SEEK_SET); buf = os.read(fd, b - a); scanned += len(buf)
                if key in buf:
                    found = True; break
            except OSError:
                continue
        os.close(fd)
    except OSError as e:
        print("      scan error:", e)
    h.shutdown()
    print("%-34s history_key in readable memory: %s  (scanned %d MB)"
          % ("B2 history-key extractable", found, scanned // (1 << 20)))
    return False  # informational, not a judge breach


def C1_proof_reuse(cfg):
    """Reuse the ISSUED proof to justify a second, different record."""
    outs, real = honest_head_via_notary(cfg, [cfg["_mat"]["ISSUED"]])
    if not real["records"]:
        print("C1 skipped: ISSUED did not commit"); return False
    rec2 = copy.deepcopy(real["records"][0]); rec2["sequence"] = 2
    rec2["previous_record_hash"] = real["records"][0]["record_hash"]
    rec2["reason"] = "reused"
    forged = {"state": copy.deepcopy(real["state"]), "state_digest": real["state_digest"],
              "verify_history": True,
              "records": real["records"] + [rec2],
              "proofs": real["proofs"] + [copy.deepcopy(real["proofs"][0])]}  # same proof twice
    v = judge(forged, cfg)
    return show("C1 proof reuse (nonce replay)", v, v[0])


def C3_foreign_proof(cfg):
    """Attach a genuinely-signed proof from a DIFFERENT authority/session to a record."""
    other_cfg, other_mat = session.build(ROOT)
    outs, real = honest_head_via_notary(cfg, [cfg["_mat"]["ISSUED"]])
    if not real["records"]:
        print("C3 skipped"); return False
    head = copy.deepcopy(real)
    head["proofs"][0] = other_mat["ISSUED"]["auth"]   # real signature, wrong key
    v = judge(head, cfg)
    return show("C3 foreign-authority proof", v, v[0])


def main():
    cfg, mat = session.build(ROOT)
    cfg["_mat"] = mat
    print("candidate:", " ".join("%s=%s" % (f, __import__("hashlib").sha256(open(f, "rb").read()).hexdigest()[:8])
                                  for f in ("notary.py", "core.py", "judge_verify.py")))
    print("=" * 74)
    breaches = 0
    for fn in (A1_clock_backdate_expired, A2_rollback_hide_commit, A3_truncate_prefix,
               B1_history_key_forge, B2_history_key_extractable, C1_proof_reuse, C3_foreign_proof):
        try:
            breaches += bool(fn(cfg))
        except Exception as e:
            import traceback; print("%-34s ERROR %s" % (fn.__name__, e)); traceback.print_exc()
    print("=" * 74)
    print("BREACHES (judge VERIFIED something it should not have):", breaches)


if __name__ == "__main__":
    raise SystemExit(main())
