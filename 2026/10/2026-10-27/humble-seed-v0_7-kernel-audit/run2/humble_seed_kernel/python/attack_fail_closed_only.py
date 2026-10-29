#!/usr/bin/env python3
"""
Run the sealed attack script against v0.7 with ONLY fix K1 applied
(check_current fails closed on an unenrolled id), to test the claim that K1
alone is insufficient once a witness holds more than one organism.

Usage: python3 -I attack_fail_closed_only.py <humble_seed_v0_7.py>
"""
import runpy
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
attack = runpy.run_path(str(here / "attack_identity_substitution.py"), run_name="attack_lib")

hs = attack["load_module"](sys.argv[1])
original = hs.OwnerWitness.check_current


def check_current_fail_closed(self, cp):
    if self.ledger.get(cp.organism_id) is None:
        raise hs.RollbackDetected(f"Unenrolled organism: {cp.organism_id}")
    return original(self, cp)


hs.OwnerWitness.check_current = check_current_fail_closed
# Make the attack script's load_module return the patched module.
attack["main"].__globals__["load_module"] = lambda _path: hs
sys.argv = [sys.argv[0], sys.argv[1] + " (+K1 only)"]
attack["main"]()
