import HumbleSeedKernel

/-!
NOT part of the build. This file is EXPECTED TO FAIL.

It attempts to prove W4 (`CurrentIsRecordedHead`) for the faithful v0.7 model,
using the same steps that prove it for v0.7.1a. The enrolled branch closes.
The unenrolled branch cannot: the hypothesis carries no information (v0.7
returns `.ok` without looking at the checkpoint) and the goal demands an
enrolled ledger entry for an id the ledger says is absent.

Run: `lake env lean attempts/V07_W4_attempt.lean`; the error shows the stuck goal.
-/

open HumbleSeedKernel

theorem attempt_v07_W4 : CurrentIsRecordedHead V07.checkCurrent := by
  intro c L cp h
  unfold V07.checkCurrent at h
  cases hL : L cp.organismId with
  | some k =>
    simp only [hL] at h
    exact ⟨k, rfl, V07.known_ok h⟩
  | none =>
    simp only [hL] at h
    done
