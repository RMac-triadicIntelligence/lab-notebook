# Pre-registration — Humble Seed v0.7 kernel model

Sealed: 2026-10-28T00:37:37Z, before any model, proof, refutation, patch or
differential-test code existed. Only the files hashed below existed at seal time.

## Sealed inputs

| File | SHA-256 |
| --- | --- |
| `source/humble_seed_v0_7.py` (the code under model, as attached) | `01db270a111f22de45419b562c3f5135f7db44b9036b95d6653060c93584daf5` |
| `lean/HumbleSeedKernel/Types.lean` | `67ec02b0ec3a5e16e6ff84dc038ca3141cc0b709757453e9c9284209d32a35d3` |
| `lean/HumbleSeedKernel/Spec.lean` | `dd3f311dafb7a3235813d97cad77f1402e3c231f68ea13b58130eb028d52f7a5` |
| `python/attack_identity_substitution.py` | `b83852eb17205288c46b98abde4c563d3a0cd34263179e6ea2e641a2492bed8d` |

Already observed before sealing (so not a prediction): on the real v0.7 code,
attack S1 (fresh organism, attacker's own key, permissive constitution) and
S2 (an enrolled sibling's state) both pass `OwnerTool.audit`; control S3 (the
victim's id under a new key) is rejected by the M1 birth-root pin. Output in
`python/attack_v0_7_output.txt`.

## Implementations

- **V07**: faithful model of v0.7.
- **V071a**: V07 with one change: `check_current` fails closed on an unenrolled id.
- **V071**: V071a, plus `audit` rejects a state whose organism id is not the one the owner expects.

## Predictions

"holds" = a kernel-checked proof will be produced. "FAILS" = a kernel-checked
refutation (`¬ Property impl`) will be produced. Any other outcome is a deviation.

| Property | V07 | V071a | V071 |
| --- | --- | --- | --- |
| B1 NoChangeWithoutExactSignature | holds | holds | holds |
| B1' RejectionPreservesAuthority | holds | holds | holds |
| B2 OnlyProposedCategory | holds | holds | holds |
| B3 SingleUse | holds | holds | holds |
| B3' ConsumedNeverApplies | holds | holds | holds |
| B4 BoundToReadState | holds | holds | holds |
| W1 RecordValidated | holds | holds | holds |
| W2 RecordWrites | holds | holds | holds |
| W3 SuccessorIsExactNextLink | holds | holds | holds |
| W4 CurrentIsRecordedHead | **FAILS** (unenrolled id) | holds | holds |
| W5 AuditBindsExpected | **FAILS** | **FAILS** (enrolled sibling) | holds |
| W5s AuditBindsExpectedSingle | **FAILS** | holds | holds |
| W6 NoRollbackOverHistory | holds | holds | holds |
| E1 BirthPinned | **FAILS** | **FAILS** (enrolled sibling) | holds |

The B rows are identical across versions because the patches do not touch
`authorize_and_apply`. The failures should be localized: on V07 every
witness property except W4 holds, meaning the defect lives only in the unenrolled
branch of `check_current` and in `audit` not knowing which organism it is auditing.

An attempted *proof* of W4 on V07 is predicted to get stuck on exactly one
goal: the `L cp.organismId = none` branch, where the hypothesis is `Verdict.ok = Verdict.ok`
and the goal demands an enrolled entry.

## Planned tests beyond the proofs

1. **Python attacks** S1–S3 on v0.7, on v0.7 with fail-closed-only `check_current`, and on the
   v0.7.1 candidate. Predicted accept/reject: v0.7 = A/A/R; fail-closed-only = R/A/R; v0.7.1 = R/R/R.
2. **v0.7.1 candidate** runs the unmodified v0.7 demo harness (tests 1–16) with the same results.
3. **Differential test**: random record / check_current / check_successor scenarios run through the
   Lean model (compiled `#eval` executable) and the real `OwnerWitness`; the verdict, including
   which rejection fired, must match on every operation. Predicted mismatches: 0 for V07 vs v0.7
   and 0 for V071 vs v0.7.1.

## Rules

- Spec and Types are not edited after sealing. If a modeling error forces a change, the old
  file is kept, the change is logged in `DEVIATIONS.md` with the reason, and affected results
  are reported against both.
- A property is reported as proved only if `lake build` succeeds with no `sorry` and
  `#print axioms` lists only `propext`, `Classical.choice` and `Quot.sound` (or a subset).
- Lean proves the model, not the Python. Model-to-code correspondence is evidenced only by the
  differential test and the Python attack runs, and is reported as such.
