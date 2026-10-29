import HumbleSeedKernel

/-! Run with `lake env lean Audit.lean`. Every line must list only a subset of
    `propext`, `Classical.choice`, `Quot.sound`. Any `sorryAx` or custom axiom
    means the corresponding result is not proved. -/

open HumbleSeedKernel
open HumbleSeedKernel.Counterexample

-- B: authorization path (all versions share V07.authorizeAndApply)
#print axioms v07_B1
#print axioms v07_B1'
#print axioms v07_B2
#print axioms v07_B3
#print axioms v07_B3'
#print axioms v07_B4
-- W: witness
#print axioms v07_W1
#print axioms v07_W2
#print axioms v07_W3
#print axioms v071a_W4
#print axioms v071_W4
#print axioms v071a_W5s
#print axioms v071_W5
#print axioms v071_W5s
#print axioms v07_W6
#print axioms v071a_W6
#print axioms v071_W6
-- E: end to end
#print axioms v071_E1
#print axioms v071_audited_changes_need_enrolled_key
-- Refutations
#print axioms v07_accepts_any_unenrolled
#print axioms attack_S1_passes_v07_audit
#print axioms attack_S2_passes_v07_audit
#print axioms attack_S2_passes_v071a_audit
#print axioms v07_not_W4
#print axioms v07_not_W5
#print axioms v07_not_W5s
#print axioms v07_not_E1
#print axioms v071a_not_W5
#print axioms v071a_not_E1
