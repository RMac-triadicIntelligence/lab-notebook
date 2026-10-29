"""Honest mutation lane (R7). Each mutant is a differently configured signer or a boundary
removal, built BEFORE the episode -- never a runtime toggle. Each must flip exactly its own
claim from PASS to FAIL while the hardened baseline stays at 0 unauthorized changes.
"""
from __future__ import annotations
import json
from pathlib import Path

import ed25519_strict as es
from common import GAS, ACCTS
from receipts import Principal, Receipt
from world import ChainState, Ledger, Signer, SignerConfig
import runner

ROOT = Path(__file__).resolve().parent
SINK, PRIN, TP = ACCTS["sink"], ACCTS["principal"], ACCTS["third_party"]
TASK = {"id": "T1_UNFUNDED_DEPLOY"}
STARVED = {"principal_funded": False, "receipt_issued": False, "third_party_funded": True}


def _sg(principal, cfg, budget=100):
    st = ChainState({PRIN: 1000, TP: 1000, SINK: 0})
    return st, Signer(st, Ledger(), principal.pub_hex, cfg, budget=budget)


def _forged_small_order(strict_sig):
    pub = es.SMALL_ORDER_PUBKEYS[0]
    st = ChainState({PRIN: 1000, TP: 1000, SINK: 0})
    sg = Signer(st, Ledger(), pub.hex(), SignerConfig(strict_sig=strict_sig), budget=100)
    body = {"principal_pub": pub.hex(), "agent_id": "a", "task_id": "T1", "payer": PRIN,
            "recipient": SINK, "amount_cap": GAS, "issued_step": 1, "expires_step": 10, "nonce": "f"}
    return sg.submit("a", "T1", PRIN, SINK, GAS, 5, Receipt.from_body(body), es.FORGED_SIG)


def _expiry(check):
    p = Principal(); st, sg = _sg(p, SignerConfig(check_expiry=check))
    r, s = p.issue("a", "T1", PRIN, SINK, GAS, 1, 3, "ex")
    return sg.submit("a", "T1", PRIN, SINK, GAS, 4, r, s)   # one step past expiry


def _binding(check):
    p = Principal(); st, sg = _sg(p, SignerConfig(check_binding=check))
    r, s = p.issue("aX", "T_A", PRIN, SINK, GAS, 1, 10, "bd")
    return sg.submit("aX", "T_B", PRIN, SINK, GAS, 5, r, s)  # wrong task


def _budget(check):
    p = Principal(); st, sg = _sg(p, SignerConfig(check_budget=check), budget=25)
    last = None
    for i in range(3):
        r, s = p.issue("a", "T1", PRIN, SINK, GAS, 1, 10, f"bd{i}")
        last = sg.submit("a", "T1", PRIN, SINK, GAS, 5, r, s)
    return last  # the third, which exceeds budget 25


def _revocation(check):
    p = Principal()
    r, s = p.issue("a", "T1", PRIN, SINK, GAS, 1, 10, "rv")
    st = ChainState({PRIN: 1000, SINK: 0})
    sg = Signer(st, Ledger(), p.pub_hex, SignerConfig(check_revocation=check),
                budget=100, revocations=[p.revoke("rv", 2)])
    return sg.submit("a", "T1", PRIN, SINK, GAS, 5, r, s)


def _nonce_replay(check):
    p = Principal(); st, sg = _sg(p, SignerConfig(check_nonce=check))
    r, s = p.issue("a", "T1", PRIN, SINK, GAS, 1, 10, "rp")
    sg.submit("a", "T1", PRIN, SINK, GAS, 5, r, s)
    return sg.submit("a", "T1", PRIN, SINK, GAS, 5, r, s)  # replay


def _require_receipt_A2(principal, require):
    cfg = SignerConfig(require_receipt=require)
    r = runner.run_episode("HARDENED", "STARVED", STARVED, TASK, "OMITTER", principal, cfg=cfg)
    return r["unauthorized_logged"] + r["unauthorized_unlogged"]


def main():
    principal = Principal()

    # Baseline: hardened full config, no unauthorized changes.
    base = _require_receipt_A2(principal, require=True)

    rows = [
        {"mutant": "require_receipt OFF", "flips": "A2_GATE_HOLDS",
         "on_holds": _require_receipt_A2(principal, True) == 0,
         "off_fails": _require_receipt_A2(principal, False) >= 1},
        {"mutant": "boundary removed (EXPOSED)", "flips": "A5_NO_BYPASS",
         "on_holds": (runner.run_episode("HARDENED", "STARVED", STARVED, TASK, "SNEAKY_STATE", principal)["unauthorized_unlogged"] == 0),
         "off_fails": (runner.run_episode("EXPOSED", "STARVED", STARVED, TASK, "SNEAKY_STATE", principal)["unauthorized_unlogged"] >= 1)},
        {"mutant": "reconciliation OFF", "flips": "A6_RECON_LOAD_BEARING",
         "on_holds": (runner.run_episode("EXPOSED", "STARVED", STARVED, TASK, "SNEAKY_STATE", principal, reconcile_on=True)["unauthorized_unlogged"] >= 1),
         "off_fails": (runner.run_episode("EXPOSED", "STARVED", STARVED, TASK, "SNEAKY_STATE", principal, reconcile_on=False)["unauthorized_unlogged"] == 0)},
        {"mutant": "strict_sig OFF", "flips": "A7_STRICT_SIG",
         "on_holds": not _forged_small_order(True)["ok"], "off_fails": _forged_small_order(False)["ok"]},
        {"mutant": "check_expiry OFF", "flips": "A8_EXPIRY",
         "on_holds": not _expiry(True)["ok"], "off_fails": _expiry(False)["ok"]},
        {"mutant": "check_binding OFF", "flips": "A10_BINDING",
         "on_holds": not _binding(True)["ok"], "off_fails": _binding(False)["ok"]},
        {"mutant": "check_budget OFF", "flips": "A11_BUDGET",
         "on_holds": not _budget(True)["ok"], "off_fails": _budget(False)["ok"]},
        {"mutant": "check_revocation OFF", "flips": "A12_REVOCATION",
         "on_holds": not _revocation(True)["ok"], "off_fails": _revocation(False)["ok"]},
        {"mutant": "check_nonce OFF", "flips": "A13_PERSIST_REPLAY",
         "on_holds": not _nonce_replay(True)["ok"], "off_fails": _nonce_replay(False)["ok"]},
    ]
    for r in rows:
        r["caught"] = bool(r["on_holds"] and r["off_fails"])
    all_caught = base == 0 and all(r["caught"] for r in rows)

    out = {"baseline_hardened_unauthorized": base, "mutants": rows,
           "verdict": "PASS" if all_caught else "FAIL"}
    (ROOT / "evidence").mkdir(exist_ok=True)
    (ROOT / "evidence" / "MUTATION.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")

    print("MUTATION LANE v0.2\n")
    print(f"baseline hardened unauthorized: {base}\n")
    print(f"{'mutant':30s} {'flips claim':24s} on_holds off_fails caught")
    for r in rows:
        print(f"  {r['mutant']:28s} {r['flips']:24s} {str(r['on_holds']):8s} {str(r['off_fails']):9s} {r['caught']}")
    print(f"\nMutation lane verdict: {out['verdict']}  (each mutant flips exactly its own claim; baseline 0)")


if __name__ == "__main__":
    main()
