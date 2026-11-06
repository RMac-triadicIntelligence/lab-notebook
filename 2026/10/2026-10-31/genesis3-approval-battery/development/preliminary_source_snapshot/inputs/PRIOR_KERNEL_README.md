# Humble Seed v0.7: a kernel under the witness

**Status (2026-10-28):** Python side complete. Lean side written but **not yet
kernel-checked**: this workspace could not download Lean (GitHub is blocked here).
Nothing below is marked *proved* until `./run_all.sh` has built the Lean
library cleanly on a machine with Lean.

## What was done

1. **Reproduced the defect live** in your v0.7 file (sha256 `01db270a…daf5`). The
   attacker writes the state file but has neither your key nor your witness ledger.
   They hatch a fresh organism under their own key, give it the constitution
   *"The organism may authorize its own growth"*, and copy it over yours.
   `OwnerTool.audit` returns **True**. The attacker then signs a mutation with
   their key, it applies, and the audit still passes.
2. **Sealed a spec and predictions** (`PREREG.md`, 2026-10-28T00:37:37Z) before any
   model or proof existed: 14 properties × 3 versions, each predicted *holds* or *FAILS*.
3. **Wrote a Lean model** of the witness, the audit, and `authorize_and_apply`,
   plus proofs and kernel-checkable counterexamples. Core Lean only, no Mathlib.
4. **Wrote a candidate fix**, `humble_seed_v0_7_1.py`. It is two changes, built
   from v0.7 by asserted string edits (`v0_7_to_v0_7_1.diff`).
5. **Built a differential test.** It runs 2,000 random witness scenarios through
   the real `OwnerWitness` and through the compiled Lean model, and compares
   which rejection fires on every operation.

## Results so far

| Check | Predicted | Observed |
| --- | --- | --- |
| S1 fresh-identity substitution, v0.7 | accepted | **accepted** (observed before sealing) |
| S2 enrolled sibling, v0.7 | accepted | **accepted** (observed before sealing) |
| S3 victim id under new key, v0.7 | rejected | rejected (M1 birth-root pin) |
| S1 / S2 / S3 on v0.7 + K1 only | R / A / R | **R / A / R** |
| S1 / S2 / S3 on v0.7.1 | R / R / R | **R / R / R** |
| v0.7 demo tests 1–16 on v0.7.1 | identical | identical (107 lines, UUIDs normalized) |
| v0.7.1 T1 K1 alone, T2 liveness, T3 rollback, T4 needs id | pass | pass |
| Only witness behavior change v0.7 → v0.7.1 | check_current ok→reject, unenrolled ids only | exactly that: 4,000 of 25,142 ops, all check_current |
| Lean build, no `sorry`, standard axioms only | yes | **pending: Lean not available** |
| 14 properties × 3 versions (see PREREG) | as sealed | **pending** |
| v0.7 W4 proof attempt gets stuck on the unenrolled branch | stuck | **pending** |
| Differential test, Lean model vs Python | 0 mismatches | **pending** (Python side run; vectors frozen) |

A Python transliteration of the Lean witness model matched the real witness on
all 2,000 scenarios for both versions. That checks the model's design against the
code. It is not the kernel, and it is not the differential test.

## The defect, plainly

`check_current` has one branch that never looks at the checkpoint: line 1110–1111,
`if known is None: return`. `audit` never says which organism it is auditing, so
any self-consistent organism the witness has never heard of passes. Every other
check in `verify()` still runs, but the attacker built the organism, so every one passes.

The model localizes this. Every other witness property is predicted to hold on
v0.7, including rollback and fork detection for enrolled organisms. The hole is
that one branch, plus the audit having no expected identity.

## The fix (v0.7.1 candidate)

- **K1:** `check_current` raises on an unenrolled id.
- **K2:** `OwnerTool.audit(seed, expected_organism_id=None)` rejects a state whose
  organism id is not the expected one. The expected id is passed in, or remembered
  from this tool's first attestation.

K1 alone is not enough if a witness holds more than one organism. The ledger is a
dict keyed by organism id, so that is a supported configuration. An enrolled
sibling's genuine state passes (S2, and `v071a_not_W5` in Lean). K2 closes it.
**Behavior change:** a fresh `OwnerTool` that attested nothing now refuses to
audit unless given the id (T4).

## What the Lean side claims, once built

- **B1–B4:** a character change happens only under a valid signature by the
  organism's key, over the re-derived payload, and it is exactly the signed change.
  Only the proposed category moves. The proposal is single-use and bound to the
  state it was read from.
- **W1–W3, W6:** `record` writes only what `check_successor` accepts. A successor
  is the exact next link with the pinned identity. Over any successful history, the
  only checkpoint accepted for an enrolled organism is its last recorded one, so
  there is no rollback and no fork.
- **W4, W5, E1:** fail on v0.7 with concrete counterexamples, and hold on v0.7.1.
- **Headline:** `v071_audited_changes_need_enrolled_key`. On v0.7.1, if the audit
  passes, every character change the organism accepts was signed under the key you
  enrolled. The only assumption is that the birth root is collision-free.

## Honest bounds

- **Lean proves the model, not the Python.** The bridge is the differential test
  (witness only) and the attack runs. The apply-path model has no differential test.
  Its correspondence rests on reading the code and on your v0.7 demo tests.
- **Cryptography is abstract.** No crypto assumption is a Lean `axiom`.
  Collision-freedom appears as an explicit `Inj` hypothesis only where a theorem needs it.
- **`StateView` collapses every non-identity check** in `verify()` into one flag. An
  attacker satisfies them by construction; S1 shows this live.
- **The apply model joins the ten guards into one conjunction.** This is
  observationally identical because every guard calls the same `_reject`.
  Rejection *reasons* are not modeled.
- **Not modeled:** `install_checkpoint`, the seal, the hash chain, the unattested
  trace tail (R8), basin and pending attestation (R9). Also not modeled: the
  v0.7.1 fallback to the tool's remembered id; the model always takes the expected id.
- **R1 is unchanged.** The witness is still a local file.
- **Stale header in v0.7:** the docstring still says v0.6 and
  `humble_seed_v0_5.py`, while `SCHEMA_VERSION` is 0.7 and the witness is the
  merged M1–M4 version.

## Run it

```
pip install cryptography      # if needed
./run_all.sh                  # installs Lean via elan on first run (GitHub access)
cat receipts/SUMMARY.txt
```

## Files

| Path | What |
| --- | --- |
| `PREREG.md`, `PREREG.sha256`, `sealed.sha256` | sealed spec, predictions, input hashes |
| `source/humble_seed_v0_7.py` | your v0.7, byte-identical to the attachment |
| `lean/HumbleSeedKernel/Types.lean`, `Spec.lean` | vocabulary and the 14 properties (sealed) |
| `lean/HumbleSeedKernel/Model.lean` | v0.7 model, V071a (K1), V071 (K1+K2) |
| `lean/HumbleSeedKernel/Proofs.lean` | properties that hold |
| `lean/HumbleSeedKernel/Refutations.lean` | counterexamples, evaluated by `decide` |
| `lean/Audit.lean` | `#print axioms` for every result |
| `lean/attempts/V07_W4_attempt.lean` | expected to fail: the stuck goal |
| `lean/Diff.lean` | model executable for the differential test |
| `python/humble_seed_v0_7_1.py`, `make_v0_7_1.py`, `v0_7_to_v0_7_1.diff` | candidate fix |
| `python/attack_*.py`, `test_v0_7_1.py`, `differential_test.py` | tests |
| `python/vectors_*.txt`, `python_*.txt` | frozen differential inputs and Python verdicts |
| `receipts/` | outputs and hashes from the last `run_all.sh` |
