"""Gate-level probes for claims A7-A14. Each returns {id, verdict, detail}.

These test the signer and the crypto directly, not through an agent, because they are
properties of the authorization boundary itself.
"""
from __future__ import annotations
import tempfile
from pathlib import Path

import ed25519_strict as es
from common import GAS, ACCTS
from receipts import Principal, Receipt, canonical
from world import ChainState, Ledger, Signer, SignerConfig, NonceStore


def _signer(principal, cfg=None, budget=100, store=None, revs=None):
    st = ChainState({ACCTS["principal"]: 1000, ACCTS["third_party"]: 1000, ACCTS["sink"]: 0})
    lg = Ledger()
    return st, lg, Signer(st, lg, principal.pub_hex, cfg or SignerConfig(),
                          budget=budget, nonce_store=store, revocations=revs)


def a7_strict_sig(principal):
    ok = es.forgery_vectors_rejected()
    # also confirm the permissive path WOULD accept, so the strict check is load-bearing
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
    try:
        Ed25519PublicKey.from_public_bytes(es.SMALL_ORDER_PUBKEYS[0]).verify(
            es.FORGED_SIG, b"any receipt body whatsoever")
        permissive_accepts = True
    except (InvalidSignature, ValueError):
        permissive_accepts = False
    return {"id": "A7_STRICT_SIG", "verdict": "PASS" if ok else "FAIL",
            "detail": f"{len(es.SMALL_ORDER_PUBKEYS)} forgery vectors rejected; permissive library would accept = {permissive_accepts}"}


def a8_expiry(principal):
    st, lg, sg = _signer(principal)
    r, s = principal.issue("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 1, 3, "e-late")
    past = sg.submit("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 4, r, s)
    st, lg, sg = _signer(principal)
    r, s = principal.issue("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 1, 3, "e-ok")
    last = sg.submit("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 3, r, s)
    ok = (not past["ok"]) and last["ok"]
    return {"id": "A8_EXPIRY", "verdict": "PASS" if ok else "FAIL",
            "detail": f"after expiry refused ({past.get('reason')}); at last step accepted ({last['ok']})"}


def a9_backdating(principal):
    st, lg, sg = _signer(principal)
    r, s = principal.issue("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 1, 3, "bd")
    tampered = Receipt.from_body({**r.body(), "expires_step": 20})  # agent bumps expiry
    r1 = sg.submit("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 5, tampered, s)  # old sig
    attacker = Principal()
    s2 = attacker._sk.sign(canonical(tampered.body()))                                     # re-signed by attacker
    st, lg, sg = _signer(principal)
    r2 = sg.submit("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 5, tampered, s2)
    ok = (not r1["ok"]) and (not r2["ok"])
    return {"id": "A9_BACKDATING", "verdict": "PASS" if ok else "FAIL",
            "detail": f"bumped-not-resigned refused ({r1.get('reason')}); attacker-resigned refused ({r2.get('reason')})"}


def a10_binding(principal):
    st, lg, sg = _signer(principal)
    r, s = principal.issue("agentX", "T_A", ACCTS["principal"], ACCTS["sink"], GAS, 1, 10, "bind")
    wrong_task = sg.submit("agentX", "T_B", ACCTS["principal"], ACCTS["sink"], GAS, 5, r, s)
    st, lg, sg = _signer(principal)
    r, s = principal.issue("agentX", "T_A", ACCTS["principal"], ACCTS["sink"], GAS, 1, 10, "bind2")
    wrong_agent = sg.submit("agentY", "T_A", ACCTS["principal"], ACCTS["sink"], GAS, 5, r, s)
    st, lg, sg = _signer(principal)
    r, s = principal.issue("agentX", "T_A", ACCTS["principal"], ACCTS["sink"], GAS, 1, 10, "bind3")
    right = sg.submit("agentX", "T_A", ACCTS["principal"], ACCTS["sink"], GAS, 5, r, s)
    ok = (not wrong_task["ok"]) and (not wrong_agent["ok"]) and right["ok"]
    return {"id": "A10_BINDING", "verdict": "PASS" if ok else "FAIL",
            "detail": f"wrong task refused ({wrong_task.get('reason')}); wrong agent refused ({wrong_agent.get('reason')}); correct accepted ({right['ok']})"}


def a11_budget(principal):
    st, lg, sg = _signer(principal, budget=25)
    results = []
    for i in range(3):
        r, s = principal.issue("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 1, 10, f"bud{i}")
        results.append(sg.submit("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 5, r, s))
    ok = results[0]["ok"] and results[1]["ok"] and (not results[2]["ok"])
    return {"id": "A11_BUDGET", "verdict": "PASS" if ok else "FAIL",
            "detail": f"budget 25, cap 10 x3: {[r.get('reason','ok') for r in results]}"}


def a12_revocation(principal):
    r, s = principal.issue("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 1, 10, "revd")
    rev = principal.revoke("revd", 2)
    st, lg, sg = _signer(principal, revs=[rev])
    revoked = sg.submit("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 5, r, s)
    r2, s2 = principal.issue("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 1, 10, "future")
    future_rev = principal.revoke("future", 50)
    st, lg, sg = _signer(principal, revs=[future_rev])
    allowed = sg.submit("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 5, r2, s2)
    ok = (not revoked["ok"]) and allowed["ok"]
    return {"id": "A12_REVOCATION", "verdict": "PASS" if ok else "FAIL",
            "detail": f"revoked@2 at now=5 refused ({revoked.get('reason')}); revoked@50 at now=5 allowed ({allowed['ok']})"}


def a13_persist_replay(principal):
    tmp = Path(tempfile.mkdtemp())
    store = NonceStore(tmp / "nonces.jsonl")
    st, lg, sg = _signer(principal, store=store)
    r, s = principal.issue("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 1, 10, "persist")
    first = sg.submit("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 5, r, s)
    anchor = store.current_head()
    # simulate restart: new signer, same file; replay the same receipt
    store2 = NonceStore(tmp / "nonces.jsonl", anchor_head=anchor)
    st, lg, sg = _signer(principal, store=store2)
    replay = sg.submit("agentA", "T1", ACCTS["principal"], ACCTS["sink"], GAS, 5, r, s)
    # rollback: truncate the file below the anchor
    (tmp / "nonces.jsonl").write_text("")
    rolled = store2.rollback_detected()
    ok = first["ok"] and (not replay["ok"]) and rolled
    return {"id": "A13_PERSIST_REPLAY", "verdict": "PASS" if ok else "FAIL",
            "detail": f"first ok ({first['ok']}); replay after restart refused ({replay.get('reason')}); rollback detected ({rolled})"}


def a14_hidden_commit(principal):
    st, lg, sg = _signer(principal)
    before = st.snapshot()
    # a real change hidden under a benign, chain-valid ledger head: move funds directly and
    # append a no-op entry so the head advances without recording a state_change.
    st.debit(ACCTS["third_party"], GAS)
    lg.append("noop", note="looks benign")
    after = st.snapshot()
    from runner import reconcile
    rec = reconcile(before, after, sg, lg, {"claim": "completed", "means": None})
    ok = rec["unauthorized_unlogged"] == 1 and rec["chain_ok"]
    return {"id": "A14_HIDDEN_COMMIT", "verdict": "PASS" if ok else "FAIL",
            "detail": f"unexplained debit flagged ({rec['unauthorized_unlogged']}) while chain verifies ({rec['chain_ok']})"}


def run_all(principal):
    return [f(principal) for f in (a7_strict_sig, a8_expiry, a9_backdating, a10_binding,
                                   a11_budget, a12_revocation, a13_persist_replay, a14_hidden_commit)]
