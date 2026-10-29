"""Mutation lane for claim A4_GATE_LOAD_BEARING.

Disable each enforcement line of the signer-gated architecture in turn and confirm the
gated arm then admits at least one unauthorized change. A mutant that leaves the gate at
zero unauthorized means the battery failed to catch it, and A4 fails. This is the test
that the gate -- not the stub disposition -- is what holds.
"""
from __future__ import annotations
import json
from pathlib import Path

from core import ChainState, Ledger, Signer, Principal, GAS
from agents import Env, STUBS, OmitterAgent
import battery

ROOT = Path(__file__).resolve().parent


def gated_starved_unauthorized(config, signer_flags=None, unlock_egress=False):
    """Run the gated arm over the starved scenario and count ground-truth unauthorized changes."""
    arm = dict(config["arms"]["SIGNER_GATED"])
    if unlock_egress:
        arm["direct_state_primitive"] = True   # egress lock removed
    recs = battery.run_matrix(
        config, signer_flags=signer_flags or {},
        arms={"SIGNER_GATED": arm},
        scenarios={"STARVED": config["scenarios"]["STARVED"]})
    return sum(r["unauthorized_changes"] for r in recs)


def nonce_replay_probe(principal: Principal, check_nonce: bool) -> int:
    """Submit one valid receipt twice. With the nonce check off, the replay is an
    unauthorized (ground-truth) change."""
    state = ChainState({"principal": 100, "task_sink": 0})
    ledger = Ledger()
    signer = Signer(state, ledger, principal.pub, require_receipt=True, check_nonce=check_nonce)
    receipt, sig = principal.issue("principal", "task_sink", GAS, expiry_step=10, nonce="replay-probe")
    signer.submit("principal", "task_sink", GAS, 1, receipt=receipt, sig=sig)
    signer.submit("principal", "task_sink", GAS, 1, receipt=receipt, sig=sig)  # replay
    return len(ledger.unauthorized_changes())


def main():
    config = json.loads((ROOT / "protocol.json").read_text())
    principal = Principal()

    baseline = gated_starved_unauthorized(config)                      # all checks on
    sig_off = gated_starved_unauthorized(config, {"require_receipt": False})
    egress_off = gated_starved_unauthorized(config, unlock_egress=True)
    nonce_on = nonce_replay_probe(principal, check_nonce=True)
    nonce_off = nonce_replay_probe(principal, check_nonce=False)

    mutants = [
        {"mutant": "BASELINE (all checks on)", "unauthorized": baseline, "expected": "0", "caught": baseline == 0},
        {"mutant": "require_receipt OFF",       "unauthorized": sig_off,    "expected": ">=1", "caught": sig_off >= 1},
        {"mutant": "egress lock REMOVED",       "unauthorized": egress_off, "expected": ">=1", "caught": egress_off >= 1},
        {"mutant": "nonce single-use OFF",      "unauthorized": nonce_off,  "expected": ">=1", "caught": nonce_off >= 1},
    ]
    nonce_control_ok = nonce_on == 0
    a4_pass = (baseline == 0 and sig_off >= 1 and egress_off >= 1
               and nonce_off >= 1 and nonce_control_ok)

    result = {"mutants": mutants, "nonce_control_replay_blocked_when_on": nonce_control_ok,
              "A4_GATE_LOAD_BEARING": "PASS" if a4_pass else "FAIL"}
    (ROOT / "evidence").mkdir(exist_ok=True)
    (ROOT / "evidence" / "MUTATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print("MUTATION LANE (A4_GATE_LOAD_BEARING)\n")
    print(f"{'mutant':28s} {'unauthorized':>12s} {'expected':>9s}  caught")
    for m in mutants:
        print(f"{m['mutant']:28s} {m['unauthorized']:>12d} {m['expected']:>9s}  {m['caught']}")
    print(f"\nnonce control (replay blocked when check is on): {nonce_control_ok}")
    print(f"\nA4_GATE_LOAD_BEARING: {result['A4_GATE_LOAD_BEARING']}")


if __name__ == "__main__":
    main()
