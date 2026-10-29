#!/usr/bin/env python3
"""
Build the v0.7.1 candidate from the frozen v0.7 file by exact, asserted
replacements, so the diff is exactly the two fixes and nothing else.

Usage: python3 -I make_v0_7_1.py <humble_seed_v0_7.py> <out humble_seed_v0_7_1.py>
"""
import sys

src_path, out_path = sys.argv[1], sys.argv[2]
src = open(src_path, encoding="utf-8").read()

EDITS = [
    # 0. Header note (docstring only).
    (
        '#!/usr/bin/env python3\n"""\n',
        '#!/usr/bin/env python3\n"""\n'
        'Humble Seed v0.7.1 (candidate) — two changes to canonical v0.7, nothing else:\n'
        '\n'
        '  K1  OwnerWitness.check_current fails closed on an organism id the witness\n'
        '      never enrolled. v0.7 returned success, so a state file replaced\n'
        '      wholesale by a fresh, self-consistent organism (new id, attacker key,\n'
        '      any constitution) passed OwnerTool.audit.\n'
        '  K2  OwnerTool.audit checks the organism it is auditing is the one the owner\n'
        '      expects (passed in, or the one this tool attested). K1 alone is not\n'
        '      enough once a witness holds more than one organism: an enrolled\n'
        '      sibling\'s genuine state passes.\n'
        '\n'
        '  Found by stating the witness invariants in Lean and attempting the proofs.\n'
        '  State-file format and SCHEMA_VERSION are unchanged.\n'
        '\n'
        '-----------------------------------------------------------------------------\n',
    ),
    # 1. Version marker.
    (
        'SCHEMA_VERSION = "0.7"\n',
        'SCHEMA_VERSION = "0.7"\nCODE_VERSION = "0.7.1-candidate"\n',
    ),
    # 2. K1: fail closed on an unenrolled id.
    (
        '        known = self.ledger.get(cp.organism_id)\n'
        '        if known is None:\n'
        '            return\n'
        '        self._check_identity(cp, known)\n'
        '        if cp.sequence < known["sequence"]:\n',
        '        known = self.ledger.get(cp.organism_id)\n'
        '        if known is None:\n'
        '            # K1 (v0.7.1): v0.7 returned here, accepting any checkpoint for an\n'
        '            # id this witness never enrolled. A current-state check on an\n'
        '            # organism with no recorded chain has nothing to compare against,\n'
        '            # so it cannot pass.\n'
        '            raise RollbackDetected(\n'
        '                f"Unenrolled organism: {cp.organism_id} has no recorded chain at "\n'
        '                f"this witness — nothing attests this state"\n'
        '            )\n'
        '        self._check_identity(cp, known)\n'
        '        if cp.sequence < known["sequence"]:\n',
    ),
    # 3. K2: OwnerTool remembers the organism it attested.
    (
        '    def __init__(self, private_key_pem: str, witness: OwnerWitness):\n'
        '        self._pem = private_key_pem\n'
        '        self.witness = witness\n',
        '    def __init__(self, private_key_pem: str, witness: OwnerWitness):\n'
        '        self._pem = private_key_pem\n'
        '        self.witness = witness\n'
        '        self.organism_id: Optional[str] = None   # K2: set on first attestation\n',
    ),
    (
        '        if not seed.install_checkpoint(cp, sig):\n'
        '            return False\n'
        '        self.witness.record(cp)\n'
        '        return True\n',
        '        if not seed.install_checkpoint(cp, sig):\n'
        '            return False\n'
        '        self.witness.record(cp)\n'
        '        if self.organism_id is None:\n'
        '            self.organism_id = cp.organism_id\n'
        '        return True\n',
    ),
    # 4. K2: audit is about a specific organism.
    (
        '    def audit(self, seed: HumbleSeed) -> bool:\n'
        '        """Full external audit of a loaded organism, including rollback."""\n'
        '        seed.verify()\n'
        '        if seed.checkpoint is None:\n'
        '            raise IntegrityError("No checkpoint to audit")\n'
        '        self.witness.check_current(seed.checkpoint)\n'
        '        return True\n',
        '    def audit(self, seed: HumbleSeed,\n'
        '              expected_organism_id: Optional[str] = None) -> bool:\n'
        '        """Full external audit of a loaded organism, including rollback.\n'
        '\n'
        '        K2 (v0.7.1): the audit is about a specific organism, given here or\n'
        '        remembered from this tool\'s first attestation.\n'
        '        """\n'
        '        seed.verify()\n'
        '        if seed.checkpoint is None:\n'
        '            raise IntegrityError("No checkpoint to audit")\n'
        '        expected = (expected_organism_id if expected_organism_id is not None\n'
        '                    else self.organism_id)\n'
        '        if expected is None:\n'
        '            raise IntegrityError(\n'
        '                "Audit needs the expected organism id: none given, and this tool "\n'
        '                "has attested none"\n'
        '            )\n'
        '        if seed.checkpoint.organism_id != expected:\n'
        '            raise RollbackDetected(\n'
        '                f"Wrong organism: state presents {seed.checkpoint.organism_id}, "\n'
        '                f"owner expects {expected}"\n'
        '            )\n'
        '        self.witness.check_current(seed.checkpoint)\n'
        '        return True\n',
    ),
]

out = src
for i, (old, new) in enumerate(EDITS):
    n = out.count(old)
    if n != 1:
        sys.exit(f"edit {i}: expected exactly one match, found {n}")
    out = out.replace(old, new)

open(out_path, "w", encoding="utf-8").write(out)
print(f"wrote {out_path}: {len(EDITS)} edits applied")
