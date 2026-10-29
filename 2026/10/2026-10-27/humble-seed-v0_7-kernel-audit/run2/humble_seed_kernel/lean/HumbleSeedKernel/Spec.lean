import HumbleSeedKernel.Types

/-!
# Humble Seed — invariants under test (FROZEN before any model or proof)

Every property is stated over an implementation's *signature*, not over any
particular implementation. This file imports only `Types`. It was hashed and
sealed in `PREREG.md` before `Model.lean`, `Proofs.lean` or `Refutations.lean`
existed, together with a predicted verdict for each property on each version.

Implementations under test:
* `V07`  — faithful model of humble_seed_v0_7.py
* `V071a` — v0.7 with one change: `check_current` fails closed on an unknown id
* `V071`  — V071a plus `audit` bound to the organism the owner expects
-/

namespace HumbleSeedKernel

abbrev CheckFn  := Crypto → Ledger → Checkpoint → Verdict
abbrev RecordFn := Crypto → Ledger → Checkpoint → Ledger × Verdict
/-- `audit c L expected s`: the owner audits state `s`, meaning organism `expected`. -/
abbrev AuditFn  := Crypto → Ledger → Nat → StateView → Verdict
/-- `apply c now s proposalId signature = (s', applied)`. -/
abbrev ApplyFn  := Crypto → Nat → Org → Nat → Nat → Org × Bool

/-! ## Authorization path: `authorize_and_apply` -/

/-- B1. Character changes only under a valid signature, by the organism's key,
    over the re-derived payload, and the change applied is exactly the signed one. -/
def NoChangeWithoutExactSignature (apply : ApplyFn) : Prop :=
  ∀ (c : Crypto) (now : Nat) (s : Org) (pid sig : Nat) (s' : Org),
    apply c now s pid sig = (s', true) →
    ∃ p, s.pending pid = some p ∧
      c.verify s.pubKey (c.encode p.fields) sig = true ∧
      p.fields.organismId = s.organismId ∧
      s'.character = applyChange s.character p.fields.change

/-- B1'. A rejected authorization leaves every authority-bearing field untouched. -/
def RejectionPreservesAuthority (apply : ApplyFn) : Prop :=
  ∀ (c : Crypto) (now : Nat) (s : Org) (pid sig : Nat) (s' : Org),
    apply c now s pid sig = (s', false) →
    s'.character = s.character ∧ s'.consumed = s.consumed ∧
    s'.mutationSequence = s.mutationSequence ∧ s'.gates = s.gates ∧
    s'.pending = s.pending ∧ s'.pubKey = s.pubKey ∧ s'.organismId = s.organismId

/-- B2. Only the proposed category moves, and it lands in range. -/
def OnlyProposedCategory (apply : ApplyFn) : Prop :=
  ∀ (c : Crypto) (now : Nat) (s : Org) (pid sig : Nat) (s' : Org),
    apply c now s pid sig = (s', true) →
    ∃ p, s.pending pid = some p ∧
      (∀ f, f ≠ p.fields.category → s'.character f = s.character f) ∧
      c.inRange (s'.character p.fields.category) = true

/-- B3. An applied proposal is consumed and cannot be applied again. -/
def SingleUse (apply : ApplyFn) : Prop :=
  ∀ (c : Crypto) (now : Nat) (s : Org) (pid sig : Nat) (s' : Org),
    apply c now s pid sig = (s', true) →
    s'.pending pid = none ∧
    (∃ p, s.pending pid = some p ∧ (p.fields.proposalId, p.fields.nonce) ∈ s'.consumed) ∧
    ∀ (now' sig' : Nat), (apply c now' s' pid sig').2 = false

/-- B3'. A proposal whose (proposal_id, nonce) is consumed is rejected, wherever
    it is re-inserted. -/
def ConsumedNeverApplies (apply : ApplyFn) : Prop :=
  ∀ (c : Crypto) (now : Nat) (s : Org) (pid sig : Nat) (p : Proposal),
    s.pending pid = some p →
    (p.fields.proposalId, p.fields.nonce) ∈ s.consumed →
    (apply c now s pid sig).2 = false

/-- B4. An applied proposal was read from the current state, is unexpired, and
    its first-commit flag matches the gate. -/
def BoundToReadState (apply : ApplyFn) : Prop :=
  ∀ (c : Crypto) (now : Nat) (s : Org) (pid sig : Nat) (s' : Org),
    apply c now s pid sig = (s', true) →
    ∃ p, s.pending pid = some p ∧
      p.fields.priorCharacterRoot = c.charRoot s.character ∧
      p.fields.priorTraceHead = s.traceHead ∧
      p.fields.mutationSequence = s.mutationSequence ∧
      now ≤ p.fields.expiresAt ∧
      p.fields.firstCommit = (s.gates p.fields.category).getD true ∧
      s'.mutationSequence = s.mutationSequence + 1

/-! ## Witness: `OwnerWitness` -/

/-- W1. `record` writes only what `check_successor` accepts. -/
def RecordValidated (record : RecordFn) (succ : CheckFn) : Prop :=
  ∀ (c : Crypto) (L : Ledger) (cp : Checkpoint),
    (record c L cp).2 = succ c L cp ∧
    (succ c L cp ≠ .ok → (record c L cp).1 = L)

/-- W2. A successful `record` writes exactly one row, pinning the birth root. -/
def RecordWrites (record : RecordFn) : Prop :=
  ∀ (c : Crypto) (L : Ledger) (cp : Checkpoint) (L' : Ledger),
    record c L cp = (L', .ok) →
    L' cp.organismId = some (Entry.mk cp.sequence (c.hashCp cp) (some cp.birthRoot)) ∧
    ∀ o, o ≠ cp.organismId → L' o = L o

/-- W3. An accepted successor is a parentless genesis or the exact next link,
    with the pinned identity. -/
def SuccessorIsExactNextLink (succ : CheckFn) : Prop :=
  ∀ (c : Crypto) (L : Ledger) (cp : Checkpoint),
    succ c L cp = .ok →
    match L cp.organismId with
    | none   => cp.sequence = 0 ∧ cp.prevHash = zeroHash
    | some k => cp.sequence = k.sequence + 1 ∧ cp.prevHash = k.checkpointHash ∧
                (∀ b, k.birthRoot = some b → cp.birthRoot = b)

/-- W4. An accepted "current" checkpoint IS the recorded head of an enrolled organism. -/
def CurrentIsRecordedHead (cur : CheckFn) : Prop :=
  ∀ (c : Crypto) (L : Ledger) (cp : Checkpoint),
    cur c L cp = .ok →
    ∃ k, L cp.organismId = some k ∧ c.hashCp cp = k.checkpointHash ∧
      cp.sequence = k.sequence ∧ (∀ b, k.birthRoot = some b → cp.birthRoot = b)

/-- W5. A passing audit is about the organism the owner asked about, at its recorded head. -/
def AuditBindsExpected (audit : AuditFn) : Prop :=
  ∀ (c : Crypto) (L : Ledger) (expected : Nat) (s : StateView),
    audit c L expected s = .ok →
    s.checkpoint.organismId = expected ∧
    ∃ k, L expected = some k ∧ c.hashCp s.checkpoint = k.checkpointHash

def AtMostOneEnrolled (L : Ledger) : Prop :=
  ∀ a b, (L a).isSome = true → (L b).isSome = true → a = b

/-- W5 restricted to a witness that holds exactly the expected organism. -/
def AuditBindsExpectedSingle (audit : AuditFn) : Prop :=
  ∀ (c : Crypto) (L : Ledger) (expected : Nat) (s : StateView),
    AtMostOneEnrolled L → (L expected).isSome = true →
    audit c L expected s = .ok →
    s.checkpoint.organismId = expected ∧
    ∃ k, L expected = some k ∧ c.hashCp s.checkpoint = k.checkpointHash

/-- Replay `record` over a history from a given ledger; the flag is true iff
    every record succeeded. -/
def runRecords (record : RecordFn) (c : Crypto) : Ledger → List Checkpoint → Ledger × Bool
  | L, [] => (L, true)
  | L, cp :: rest =>
    let r := record c L cp
    let tail := runRecords record c r.1 rest
    (tail.1, decide (r.2 = .ok) && tail.2)

/-- The last checkpoint recorded for organism `o` in a history. -/
def lastFor (o : Nat) : List Checkpoint → Option Checkpoint
  | [] => none
  | cp :: rest =>
    match lastFor o rest with
    | some x => some x
    | none => if cp.organismId = o then some cp else none

/-- W6. After any fully-successful history, the only checkpoint `check_current`
    accepts for an enrolled organism is the last one recorded for it (no
    rollback, no fork), assuming the checkpoint hash is collision-free. -/
def NoRollbackOverHistory (record : RecordFn) (cur : CheckFn) : Prop :=
  ∀ (c : Crypto) (hist : List Checkpoint) (cp : Checkpoint),
    Inj c.hashCp →
    (runRecords record c Ledger.empty hist).2 = true →
    (lastFor cp.organismId hist).isSome = true →
    cur c (runRecords record c Ledger.empty hist).1 cp = .ok →
    lastFor cp.organismId hist = some cp

/-! ## End to end: does a passing audit pin the key the organism verifies with? -/

/-- E1. If the owner enrolled organism `expected` with birth root `r₀`, a passing
    audit means the audited state's birth record hashes to `r₀`. With a
    collision-free birth root this is the enrolled birth record, hence the
    enrolled public key — the key every later authorization is checked against. -/
def BirthPinned (audit : AuditFn) : Prop :=
  ∀ (c : Crypto) (L : Ledger) (expected : Nat) (s : StateView) (k : Entry) (r₀ : Nat),
    L expected = some k → k.birthRoot = some r₀ →
    audit c L expected s = .ok →
    c.birthRoot s.birth = r₀

end HumbleSeedKernel
