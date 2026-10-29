"""Write FREEZE.json. The freeze receipt is over file checksums and the pinned environment
ONLY -- never a timestamp -- so re-running freeze.py on unchanged files reproduces the same
receipt (fixing the v0.1 issue where the rewritten timestamp made a re-freeze look new).
The timestamp is recorded separately and is not part of the receipt.
"""
import datetime
import hashlib
import json
import platform
from pathlib import Path

import cryptography

ROOT = Path(__file__).resolve().parent
FILES = ["protocol.json", "ed25519_strict.py", "receipts.py", "world.py", "common.py",
         "handle.py", "agent_proc.py", "agents.py", "runner.py", "probes.py",
         "battery.py", "mutate.py"]


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def main():
    digests = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in FILES}
    env = {"python": platform.python_version(), "cryptography": cryptography.__version__}
    receipt = hashlib.sha256(canonical({"sha256": digests, "env": env})).hexdigest()
    lock = {"frozen_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "registration": "Local pre-execution lock, not external preregistration.",
            "note": "freeze_receipt excludes frozen_utc by construction.",
            "env": env, "sha256": digests, "freeze_receipt": receipt}
    (ROOT / "FREEZE.json").write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")
    (ROOT / "MANIFEST.sha256").write_text("".join(f"{d}  {f}\n" for f, d in sorted(digests.items())))
    print("Frozen at:", lock["frozen_utc"], "(informational, not in the receipt)")
    print("Environment:", env)
    print("Freeze receipt (post this before running):", receipt)


if __name__ == "__main__":
    main()
