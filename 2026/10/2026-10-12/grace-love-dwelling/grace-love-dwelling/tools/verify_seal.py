#!/usr/bin/env python3
"""Verify the 2026-10-12 seal: every listed file is byte-identical, and the manifest hashes to SEAL_HASH.txt.
Standard library only."""
import hashlib, sys
from pathlib import Path

SEAL = Path(__file__).resolve().parent.parent / "seal" / "2026-10-12"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    manifest = SEAL / "SEAL_MANIFEST.sha256"
    want = (SEAL / "SEAL_HASH.txt").read_text().strip()
    ok = True
    got = sha(manifest)
    print(("OK  " if got == want else "BAD ") + f"SEAL_MANIFEST.sha256 -> {got[:12]}… (expected {want[:12]}…)")
    ok &= got == want
    for line in manifest.read_text().splitlines():
        h, name = line.split(maxsplit=1)
        p = SEAL / name
        if not p.exists():
            print(f"MISSING {name}"); ok = False; continue
        good = sha(p) == h
        ok &= good
        print(("OK  " if good else "BAD ") + f"{h[:12]}  {name}")
    print("\nSEAL INTACT" if ok else "\nSEAL BROKEN")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
