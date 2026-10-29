#!/usr/bin/env python3
"""Re-derive all sealed results from the sealed code, in a scratch copy (never in place).

Copies seal/2026-10-12 to a temporary directory, runs test_S.py, test_T.py and test_G2.py unchanged,
and compares each new results_*.json with the sealed one: byte-identical first, then value-by-value
(a different numpy build can change float bytes without changing a verdict). Needs numpy and scipy.
"""
import hashlib, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path

SEAL = Path(__file__).resolve().parent.parent / "seal" / "2026-10-12"
TESTS = [("test_S.py", "results_S.json"), ("test_T.py", "results_T.json"), ("test_G2.py", "results_G2.json")]


def same(a, b, tol=1e-9):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k], tol) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return a is not None and b is not None and math.isclose(a, b, rel_tol=tol, abs_tol=tol)
    return a == b


def main():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "seal"
        shutil.copytree(SEAL, work)
        for script, result in TESTS:
            (work / result).unlink()
            print(f"running {script} …", flush=True)
            r = subprocess.run([sys.executable, script], cwd=work, capture_output=True, text=True)
            if r.returncode != 0:
                print(r.stderr); print(f"FAIL  {script} exited {r.returncode}"); ok = False; continue
            new, old = work / result, SEAL / result
            hn, ho = (hashlib.sha256(p.read_bytes()).hexdigest() for p in (new, old))
            if hn == ho:
                print(f"OK    {result} byte-identical ({hn[:12]}…)")
            elif same(json.loads(new.read_text()), json.loads(old.read_text())):
                print(f"OK    {result} same values, different bytes (numpy build)")
            else:
                print(f"FAIL  {result} differs from the sealed result"); ok = False
    print("\nREPRODUCTION OK" if ok else "\nREPRODUCTION FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
