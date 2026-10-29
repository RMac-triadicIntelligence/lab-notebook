# Deviations from PREREG.md

None in the sealed files. `sealed.sha256` verifies Types.lean, Spec.lean, the v0.7
source, the attack script and PREREG.md as unchanged.

## Notes

- **Model.lean was revised after sealing and before any build.** The revision
  joins the ten apply-path guards into one conjunction, adds `applied`, and
  reorders `V071.audit` to verify, then check the identity, then consult the
  witness, matching the Python candidate. Model.lean was not sealed; only Spec and
  Types were. The predictions do not depend on guard order.
- **K1-only attack runs use a wrapper** (`attack_fail_closed_only.py`). The wrapper
  patches v0.7's `check_current` in memory and then calls the sealed attack script
  unchanged.
- **Lean was not available in the build workspace**, because GitHub is blocked
  there. Every Lean prediction is untested until `run_all.sh` runs where Lean can be
  installed. Blind-written proofs may need tactic-level repair. Any repair is logged
  here, and Spec.lean is not touched.
