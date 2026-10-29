#!/usr/bin/env python3
"""
Differential test: the Lean witness model against the real OwnerWitness.

Generates random record / check_current / check_successor scenarios, runs each
through the real Python witness, and through the compiled Lean model
(`lake exe diffmodel`), then compares the verdict of every operation, including
WHICH rejection fired.

Usage:
    python3 -I differential_test.py <humble_seed module> <v07|v071> <N> <seed> <lean project dir>

Writes <out>/vectors_<variant>.txt and <out>/python_<variant>.txt beside this
script. If Lean is not installed, it stops after the Python side (exit 3) so the
Lean side can be run later against the same vectors.
"""
from __future__ import annotations

import collections
import importlib.util
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PREFIXES = [
    ("Identity fork", "identityFork"),
    ("Rollback:", "rollback"),
    ("Unwitnessed advance", "unwitnessedAdvance"),
    ("Fork:", "fork"),
    ("Unknown organism must start", "enrollmentSequence"),
    ("Invalid enrollment", "enrollmentParent"),
    ("Non-successor", "nonSuccessor"),
    ("Forked parent", "forkedParent"),
    ("Unenrolled organism", "unenrolledOrganism"),
]


def load_module(path):
    spec = importlib.util.spec_from_file_location("hs_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["hs_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def verdict_of(hs, fn):
    try:
        fn()
        return "ok"
    except hs.RollbackDetected as ex:
        msg = str(ex)
        for prefix, name in PREFIXES:
            if msg.startswith(prefix):
                return name
        return "UNMAPPED"
    except Exception as ex:  # surfaced, never silently mapped
        return f"PYERR_{type(ex).__name__}"


def gen(rng):
    n_orgs = rng.randint(1, 3)
    cps = []
    n_cps = rng.randint(3, 10)
    for _ in range(n_cps):
        if cps and rng.random() < 0.6:
            j = rng.randrange(len(cps))
            oid, seq, _, _, birth, _ = cps[j]
            new = [oid, seq + 1, 1, j, birth if rng.random() < 0.85 else birth ^ 1, rng.randint(0, 2)]
            r = rng.random()
            if r < 0.1:
                new[1] = rng.randint(0, 4)
            elif r < 0.2:
                new[2], new[3] = 2, 0
        else:
            oid = rng.randint(1, n_orgs)
            seq = 0 if rng.random() < 0.6 else rng.randint(0, 4)
            pk = 0 if (not cps or rng.random() < 0.6) else rng.choice([1, 2])
            pa = rng.randrange(len(cps)) if pk == 1 else 0
            birth = oid * 10 + (0 if rng.random() < 0.85 else 1)
            new = [oid, seq, pk, pa, birth, rng.randint(0, 2)]
        cps.append(new)
    ops, ptr = [], 0
    for _ in range(rng.randint(5, 20)):
        r = rng.random()
        if r < 0.5:
            idx = ptr if (ptr < n_cps and rng.random() < 0.6) else rng.randrange(n_cps)
            ptr += 1
            ops.append((0, idx))
        elif r < 0.8:
            ops.append((1, rng.randrange(n_cps)))
        else:
            ops.append((2, rng.randrange(n_cps)))
    return cps, ops


def run_python(hs, cps, ops, ledger_path):
    built = []
    for oid, seq, pk, pa, birth, body in cps:
        if pk == 0:
            prev = "0" * 64
        elif pk == 1:
            prev = hs._sha256(hs.HumbleSeed.checkpoint_payload(built[pa]))
        else:
            prev = hs._sha256("junk-parent")
        built.append(hs.Checkpoint(
            organism_id=f"org-{oid}", sequence=seq, prev_checkpoint_hash=prev,
            birth_root=hs._sha256(f"birth-{birth}"), constitution_root="c",
            gates_root="g", character_root=hs._sha256(f"body-{body}"),
            consumed_root="x", trace_head="t", attested_trace_len=0,
            mutation_sequence=0, timestamp=0.0))
    w = hs.OwnerWitness(ledger_path)
    out = []
    for code, idx in ops:
        cp = built[idx]
        if code == 0:
            out.append(verdict_of(hs, lambda: w.record(cp)))
        elif code == 1:
            out.append(verdict_of(hs, lambda: w.check_current(cp)))
        else:
            out.append(verdict_of(hs, lambda: w.check_successor(cp)))
    return out


def main():
    module, variant, n, seed, lean_dir = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    hs = load_module(module)
    rng = random.Random(seed)
    here = Path(__file__).resolve().parent
    vec_path = here / f"vectors_{variant}.txt"
    py_path = here / f"python_{variant}.txt"
    tmp = Path(tempfile.mkdtemp(prefix="hs_diff_"))
    lines, py_out = [], []
    try:
        for i in range(n):
            cps, ops = gen(rng)
            lines.append(f"{variant}|" + ";".join(",".join(map(str, c)) for c in cps)
                         + "|" + ";".join(f"{a},{b}" for a, b in ops))
            py_out.append(",".join(run_python(hs, cps, ops, tmp / f"w{i}.json")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    vec_path.write_text("\n".join(lines) + "\n")
    py_path.write_text("\n".join(py_out) + "\n")

    counts = collections.Counter(v for line in py_out for v in line.split(","))
    print(f"module {module}  variant {variant}  scenarios {n}  seed {seed}")
    print(f"operations {sum(counts.values())}  verdict coverage {dict(sorted(counts.items()))}")
    bad = {k: v for k, v in counts.items() if k.startswith(("PYERR", "UNMAPPED"))}
    if bad:
        print(f"PYTHON-SIDE ERRORS: {bad}")
        sys.exit(2)

    lake = shutil.which("lake") or str(Path.home() / ".elan" / "bin" / "lake")
    if not os.path.exists(lake):
        print("Lean not installed: Python side written; run the Lean side later.")
        sys.exit(3)
    proc = subprocess.run([lake, "exe", "diffmodel"], cwd=lean_dir, input="\n".join(lines) + "\n",
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        print("diffmodel failed:\n" + proc.stderr[-2000:])
        sys.exit(4)
    lean_out = proc.stdout.strip("\n").split("\n")
    (here / f"lean_{variant}.txt").write_text(proc.stdout)
    mism = [(i, a, b) for i, (a, b) in enumerate(zip(py_out, lean_out)) if a != b]
    if len(lean_out) != len(py_out):
        print(f"LINE COUNT MISMATCH: python {len(py_out)} lean {len(lean_out)}")
        sys.exit(5)
    print(f"mismatching scenarios: {len(mism)} of {n}")
    for i, a, b in mism[:10]:
        print(f"  #{i}\n    vector {lines[i]}\n    python {a}\n    lean   {b}")
    summary = {"variant": variant, "scenarios": n, "seed": seed,
               "operations": sum(counts.values()), "mismatches": len(mism),
               "coverage": dict(sorted(counts.items()))}
    (here / f"diff_summary_{variant}.json").write_text(json.dumps(summary, indent=2) + "\n")
    sys.exit(0 if not mism else 1)


if __name__ == "__main__":
    main()
