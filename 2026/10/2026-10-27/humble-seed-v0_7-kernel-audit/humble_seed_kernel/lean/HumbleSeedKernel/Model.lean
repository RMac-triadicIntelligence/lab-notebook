import HumbleSeedKernel.Types

/-!
# Humble Seed v0.7 — the model, and the two patched variants

Each definition names the Python it models. Witness branches follow the code's
order, so the differential test can compare *which* rejection fires, not only
whether one does.
-/

namespace HumbleSeedKernel

namespace V07

/-- `OwnerWitness._check_identity` (lines 1088–1105). -/
def checkIdentity (cp : Checkpoint) (k : Entry) : Verdict :=
  match k.birthRoot with
  | none => .ok
  | some pinned => if cp.birthRoot = pinned then .ok else .reject .identityFork

/-- The enrolled branch of `check_current` (lines 1112–1126). -/
def checkCurrentKnown (c : Crypto) (cp : Checkpoint) (k : Entry) : Verdict :=
  match checkIdentity cp k with
  | .reject r => .reject r
  | .ok =>
    if cp.sequence < k.sequence then .reject .rollback
    else if k.sequence < cp.sequence then .reject .unwitnessedAdvance
    else if c.hashCp cp = k.checkpointHash then .ok
    else .reject .fork

/-- `OwnerWitness.check_current` (lines 1107–1126).
    Lines 1110–1111 read `if known is None: return`. -/
def checkCurrent (c : Crypto) (L : Ledger) (cp : Checkpoint) : Verdict :=
  match L cp.organismId with
  | none => .ok
  | some k => checkCurrentKnown c cp k

/-- `OwnerWitness.check_successor` (lines 1128–1159). -/
def checkSuccessor (_c : Crypto) (L : Ledger) (cp : Checkpoint) : Verdict :=
  match L cp.organismId with
  | none =>
    if cp.sequence = 0 then
      if cp.prevHash = zeroHash then .ok else .reject .enrollmentParent
    else .reject .enrollmentSequence
  | some k =>
    match checkIdentity cp k with
    | .reject r => .reject r
    | .ok =>
      if cp.sequence = k.sequence + 1 then
        if cp.prevHash = k.checkpointHash then .ok else .reject .forkedParent
      else .reject .nonSuccessor

def entryOf (c : Crypto) (cp : Checkpoint) : Entry :=
  Entry.mk cp.sequence (c.hashCp cp) (some cp.birthRoot)

/-- `OwnerWitness.record` (lines 1068–1086): validate, then write. -/
def record (c : Crypto) (L : Ledger) (cp : Checkpoint) : Ledger × Verdict :=
  match checkSuccessor c L cp with
  | .ok => (Ledger.set L cp.organismId (entryOf c cp), .ok)
  | .reject r => (L, .reject r)

/-- The identity-bearing checks of `HumbleSeed.verify` and `_verify_attestation`
    (lines 661–721 and 519–563). Every other check is `otherChecksPass`. -/
def verifyState (c : Crypto) (s : StateView) : Verdict :=
  if s.birth.organismId = s.organismId ∧ s.otherChecksPass = true ∧
     c.verify s.birth.pubKey (c.cpMsg s.checkpoint) s.checkpointSig = true ∧
     s.checkpoint.organismId = s.organismId ∧
     s.checkpoint.birthRoot = c.birthRoot s.birth
  then .ok else .reject .stateInvalid

/-- `OwnerTool.audit` (lines 1181–1187): `seed.verify()`, then
    `witness.check_current(seed.checkpoint)`. It takes no expected organism, so
    `_expected` is accepted and ignored. -/
def audit (c : Crypto) (L : Ledger) (_expected : Nat) (s : StateView) : Verdict :=
  match verifyState c s with
  | .reject r => .reject r
  | .ok => checkCurrent c L s.checkpoint

/-- `consume_key = f"{p.proposal_id}|{p.nonce}"`. -/
def consumeKey (p : Proposal) : Nat × Nat := (p.fields.proposalId, p.fields.nonce)

/-- Apply-time schema re-check (lines 950–963): change keys are exactly
    `{category}` and every value is numeric and in range. -/
def schemaOk (c : Crypto) (p : Proposal) : Bool :=
  !p.fields.change.isEmpty &&
  p.fields.change.all (fun kv => decide (kv.1 = p.fields.category) && c.inRange kv.2)

/-- The ten guards of `authorize_and_apply` after the pending lookup, in code
    order (lines 920–981). Every failing guard calls the same `_reject`, whose
    only state effect is one trace append, so a conjunction is observationally
    identical to the code's `if … return None` chain. -/
def checksPass (c : Crypto) (now : Nat) (s : Org) (p : Proposal) (sig : Nat) : Bool :=
  !(decide (consumeKey p ∈ s.consumed)) &&
  (decide (p.fields.organismId = s.organismId) &&
  (!(decide (p.fields.expiresAt < now)) &&
  (decide (p.fields.priorCharacterRoot = c.charRoot s.character) &&
  (decide (p.fields.priorTraceHead = s.traceHead) &&
  (decide (p.fields.mutationSequence = s.mutationSequence) &&
  (decide (p.fields.firstCommit = (s.gates p.fields.category).getD true) &&
  (schemaOk c p &&
  (decide (c.encode p.fields = p.payloadToSign) &&
  c.verify s.pubKey (c.encode p.fields) sig))))))))

/-- The state after a successful apply (lines 983–1012). -/
def applied (c : Crypto) (s : Org) (pid : Nat) (p : Proposal) : Org :=
  { s with
      character := applyChange s.character p.fields.change
      gates := fun f => if f = p.fields.category then some false else s.gates f
      consumed := consumeKey p :: s.consumed
      mutationSequence := s.mutationSequence + 1
      pending := fun q => if q = pid then none else s.pending q
      traceHead := c.nextHead s.traceHead }

/-- `_reject`: one trace append, nothing else. -/
def rejectOrg (c : Crypto) (s : Org) : Org × Bool :=
  ({ s with traceHead := c.nextHead s.traceHead }, false)

/-- `HumbleSeed.authorize_and_apply` (lines 901–1012). -/
def authorizeAndApply (c : Crypto) (now : Nat) (s : Org) (pid sig : Nat) : Org × Bool :=
  match s.pending pid with
  | none => rejectOrg c s
  | some p => if checksPass c now s p sig then (applied c s pid p, true) else rejectOrg c s

end V07

/-- v0.7.1a: the one-line fix. `check_current` fails closed on an unenrolled id. -/
namespace V071a

def checkCurrent (c : Crypto) (L : Ledger) (cp : Checkpoint) : Verdict :=
  match L cp.organismId with
  | none => .reject .unenrolledOrganism
  | some k => V07.checkCurrentKnown c cp k

def audit (c : Crypto) (L : Ledger) (_expected : Nat) (s : StateView) : Verdict :=
  match V07.verifyState c s with
  | .reject r => .reject r
  | .ok => checkCurrent c L s.checkpoint

end V071a

/-- v0.7.1: fail closed, and audit the organism the owner expects.
    Order matches the Python candidate: verify, then identity, then witness. -/
namespace V071

def checkCurrent (c : Crypto) (L : Ledger) (cp : Checkpoint) : Verdict :=
  V071a.checkCurrent c L cp

def audit (c : Crypto) (L : Ledger) (expected : Nat) (s : StateView) : Verdict :=
  match V07.verifyState c s with
  | .reject r => .reject r
  | .ok =>
    if s.checkpoint.organismId = expected then checkCurrent c L s.checkpoint
    else .reject .wrongOrganism

end V071

end HumbleSeedKernel
