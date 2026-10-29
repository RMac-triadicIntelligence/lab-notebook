import HumbleSeedKernel.Spec
import HumbleSeedKernel.Model

/-!
# Properties that fail, as kernel-checked counterexamples

Every property in `Spec` quantifies over all `Crypto`, so one concrete
instantiation suffices to refute it. None of the counterexamples below relies on a
hash collision: the unenrolled-id case never reads a hash, and the sibling case
presents the sibling's genuine head. Signatures are a toy scheme in which
`sig = key + msg`, so each state is signed by its own key-holder and nobody else's.
-/

namespace HumbleSeedKernel
namespace Counterexample

def crypto : Crypto where
  hashCp    := fun cp => cp.organismId + cp.sequence + cp.prevHash + cp.birthRoot + cp.body
  cpMsg     := fun cp => cp.body
  birthRoot := fun b => b.organismId * 1000 + b.pubKey
  charRoot  := fun _ => 0
  encode    := fun _ => 0
  verify    := fun key msg sig => decide (sig = key + msg)
  inRange   := fun v => decide (v ≤ 100)
  nextHead  := fun h => h + 1

/-- The owner's organism A: id 1, owner key 11, genesis checkpoint, enrolled. -/
def birthA : Birth := ⟨1, 11, 0⟩
def cpA : Checkpoint := ⟨1, 0, zeroHash, crypto.birthRoot birthA, 0⟩
def stateA : StateView := ⟨1, birthA, cpA, 11 + crypto.cpMsg cpA, true⟩
def ledgerA : Ledger := Ledger.set Ledger.empty 1 (V07.entryOf crypto cpA)

/-- Attack S1: a fresh organism, id 2, under the attacker's key 99, with its own
    self-signed genesis checkpoint. `body := 5` stands for whatever character and
    constitution the attacker chose. -/
def birthX : Birth := ⟨2, 99, 0⟩
def cpX : Checkpoint := ⟨2, 0, zeroHash, crypto.birthRoot birthX, 5⟩
def stateX : StateView := ⟨2, birthX, cpX, 99 + crypto.cpMsg cpX, true⟩

/-- Attack S2: a genuine, enrolled sibling B sharing the owner's witness. -/
def birthB : Birth := ⟨2, 22, 0⟩
def cpB : Checkpoint := ⟨2, 0, zeroHash, crypto.birthRoot birthB, 0⟩
def stateB : StateView := ⟨2, birthB, cpB, 22 + crypto.cpMsg cpB, true⟩
def ledgerAB : Ledger := Ledger.set ledgerA 2 (V07.entryOf crypto cpB)

/-- Control S3: the victim's id under the attacker's key. -/
def birthX1 : Birth := ⟨1, 99, 0⟩
def cpX1 : Checkpoint := ⟨1, 0, zeroHash, crypto.birthRoot birthX1, 5⟩
def stateX1 : StateView := ⟨1, birthX1, cpX1, 99 + crypto.cpMsg cpX1, true⟩

theorem ledgerA_single : AtMostOneEnrolled ledgerA := by
  intro a b ha hb
  have h1 : a = 1 := by
    by_cases h : a = 1
    · exact h
    · simp [ledgerA, Ledger.set, Ledger.empty, h] at ha
  have h2 : b = 1 := by
    by_cases h : b = 1
    · exact h
    · simp [ledgerA, Ledger.set, Ledger.empty, h] at hb
  rw [h1, h2]

/-! ## The defect, stated generally -/

/-- On v0.7, `check_current` accepts EVERY checkpoint whose organism id the
    witness never enrolled, whatever it contains. -/
theorem v07_accepts_any_unenrolled (c : Crypto) (L : Ledger) (cp : Checkpoint)
    (h : L cp.organismId = none) : V07.checkCurrent c L cp = .ok := by
  simp [V07.checkCurrent, h]

/-! ## The attacks, evaluated by the kernel -/

theorem attack_S1_passes_v07_audit : V07.audit crypto ledgerA 1 stateX = .ok := by decide
theorem attack_S2_passes_v07_audit : V07.audit crypto ledgerAB 1 stateB = .ok := by decide
theorem attack_S2_passes_v071a_audit : V071a.audit crypto ledgerAB 1 stateB = .ok := by decide

example : V07.audit crypto ledgerA 1 stateX1 = .reject .identityFork := by decide
example : V071a.audit crypto ledgerA 1 stateX = .reject .unenrolledOrganism := by decide
example : V071.audit crypto ledgerA 1 stateX = .reject .wrongOrganism := by decide
example : V071.audit crypto ledgerAB 1 stateB = .reject .wrongOrganism := by decide
example : V071.audit crypto ledgerA 1 stateX1 = .reject .identityFork := by decide
-- Liveness: the owner's own genuine state still passes every version.
example : V07.audit crypto ledgerA 1 stateA = .ok := by decide
example : V071a.audit crypto ledgerA 1 stateA = .ok := by decide
example : V071.audit crypto ledgerA 1 stateA = .ok := by decide
example : V071.audit crypto ledgerAB 1 stateA = .ok := by decide

/-! ## Refutations -/

theorem v07_not_W4 : ¬ CurrentIsRecordedHead V07.checkCurrent := by
  intro hW
  obtain ⟨k, hk, -⟩ := hW crypto Ledger.empty cpX (v07_accepts_any_unenrolled _ _ _ rfl)
  simp [Ledger.empty] at hk

theorem v07_not_W5 : ¬ AuditBindsExpected V07.audit := by
  intro h
  have h1 := (h crypto ledgerA 1 stateX attack_S1_passes_v07_audit).1
  exact absurd h1 (by decide)

theorem v07_not_W5s : ¬ AuditBindsExpectedSingle V07.audit := by
  intro h
  have h1 := (h crypto ledgerA 1 stateX ledgerA_single (by decide)
    attack_S1_passes_v07_audit).1
  exact absurd h1 (by decide)

theorem v07_not_E1 : ¬ BirthPinned V07.audit := by
  intro h
  have h1 := h crypto ledgerA 1 stateX (V07.entryOf crypto cpA) (crypto.birthRoot birthA)
    (by decide) rfl attack_S1_passes_v07_audit
  exact absurd h1 (by decide)

/-- The one-line fix is not enough when the witness holds more than one organism. -/
theorem v071a_not_W5 : ¬ AuditBindsExpected V071a.audit := by
  intro h
  have h1 := (h crypto ledgerAB 1 stateB attack_S2_passes_v071a_audit).1
  exact absurd h1 (by decide)

theorem v071a_not_E1 : ¬ BirthPinned V071a.audit := by
  intro h
  have h1 := h crypto ledgerAB 1 stateB (V07.entryOf crypto cpA) (crypto.birthRoot birthA)
    (by decide) rfl attack_S2_passes_v071a_audit
  exact absurd h1 (by decide)

end Counterexample
end HumbleSeedKernel
