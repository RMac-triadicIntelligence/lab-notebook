"""Write FREEZE.json: a local pre-execution lock over the protocol and code.
Not an external preregistration. Post the printed receipt publicly before the scored run.
"""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = ["protocol.json", "core.py", "agents.py", "battery.py", "mutate.py"]


def main():
    digests = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in FILES}
    lock = {"frozen_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "registration": "Local pre-execution lock, not external preregistration.",
            "sha256": digests}
    (ROOT / "FREEZE.json").write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")
    receipt = hashlib.sha256(json.dumps(digests, sort_keys=True).encode()).hexdigest()
    (ROOT / "MANIFEST.sha256").write_text(
        "".join(f"{d}  {f}\n" for f, d in sorted(digests.items())))
    print("Frozen:", lock["frozen_utc"])
    print("Freeze receipt (post this before running):", receipt)


if __name__ == "__main__":
    main()
