/-!
# Humble Seed v0.7 — kernel model: shared vocabulary

Source under model: `humble_seed_v0_7.py`
(sha256 01db270a111f22de45419b562c3f5135f7db44b9036b95d6653060c93584daf5).

Modeling decisions (each one is a place the model could diverge from the code):

* Hashes, keys, messages and signatures are `Nat`. No cryptographic assumption is a
  Lean `axiom`. Where a theorem needs collision resistance it takes an explicit
  hypothesis `Inj f`, so `#print axioms` stays at Lean's standard three.
* `Checkpoint` keeps the four fields `OwnerWitness` reads (organism id, sequence,
  parent hash, birth root). Every other attested field (constitution, gates,
  character, consumed roots, trace head and length, mutation sequence, timestamp)
  is collapsed into `body`. The witness only ever sees those through the hash.
* `StateView` is what `OwnerTool.audit` sees of a loaded organism: the birth
  record, the installed checkpoint and its signature. Every `verify()` check that
  does not bear on identity (constitution hash, genesis re-derivation, character
  range, hash chain, seal) is collapsed into `otherChecksPass`. An attacker who
  builds a fresh organism satisfies all of them by construction.
* Python dicts become functions or association lists. `first_commit_pending.get(c, True)`
  becomes `(gates c).getD true`.
-/

namespace HumbleSeedKernel

/-- Injectivity, stated locally so the development needs only core Lean. -/
def Inj {α β : Type} (f : α → β) : Prop := ∀ a b, f a = f b → a = b

/-- `Checkpoint` (lines 278–292), reduced to what the witness reads plus `body`. -/
structure Checkpoint where
  organismId : Nat
  sequence   : Nat
  prevHash   : Nat
  birthRoot  : Nat
  body       : Nat
  deriving DecidableEq, Repr

/-- Python's `"0" * 64` parent. -/
def zeroHash : Nat := 0

/-- One witness ledger row: `{"sequence", "checkpoint_hash", "birth_root"}`.
    `birthRoot` is optional because `_check_identity` reads it with `.get`. -/
structure Entry where
  sequence       : Nat
  checkpointHash : Nat
  birthRoot      : Option Nat
  deriving DecidableEq, Repr

/-- `OwnerWitness.ledger : Dict[organism_id, entry]`. -/
abbrev Ledger := Nat → Option Entry

def Ledger.empty : Ledger := fun _ => none

/-- `self.ledger[o] = e`. -/
def Ledger.set (L : Ledger) (o : Nat) (e : Entry) : Ledger :=
  fun o' => if o' = o then some e else L o'

/-- Each distinct `raise` in the witness and audit path. The last three are only
    produced by the patched variants. -/
inductive Reject where
  | identityFork        -- "Identity fork: ..."
  | rollback            -- "Rollback: ..."
  | unwitnessedAdvance  -- "Unwitnessed advance: ..."
  | fork                -- "Fork: ..."
  | enrollmentSequence  -- "Unknown organism must start at sequence 0 ..."
  | enrollmentParent    -- "Invalid enrollment: ..."
  | nonSuccessor        -- "Non-successor checkpoint: ..."
  | forkedParent        -- "Forked parent at sequence ..."
  | stateInvalid        -- any IntegrityError from seed.verify()
  | unenrolledOrganism  -- patched: check_current on an id the witness never enrolled
  | wrongOrganism       -- patched: audit of an organism other than the one expected
  deriving DecidableEq, Repr

inductive Verdict where
  | ok
  | reject (r : Reject)
  deriving DecidableEq, Repr

/-- `BirthRecord` (lines 223–229); genesis hash, created_at and constitution hash
    are collapsed into `rest`. -/
structure Birth where
  organismId : Nat
  pubKey     : Nat
  rest       : Nat
  deriving DecidableEq, Repr

/-- What `OwnerTool.audit` sees of a loaded organism. -/
structure StateView where
  organismId      : Nat
  birth           : Birth
  checkpoint      : Checkpoint
  checkpointSig   : Nat
  otherChecksPass : Bool
  deriving DecidableEq, Repr

inductive Field where
  | verbosity
  | formality
  | curiosity
  deriving DecidableEq, Repr

/-- Every field `_recompute_payload` covers (lines 876–895). Evidence and
    distribution are carried raw; the encoder hashes them, as the code does. -/
structure PayloadFields where
  organismId         : Nat
  proposalId         : Nat
  category           : Field
  change             : List (Field × Nat)
  evidence           : Nat
  distribution       : Nat
  firstCommit        : Bool
  priorCharacterRoot : Nat
  priorTraceHead     : Nat
  mutationSequence   : Nat
  nonce              : Nat
  timestamp          : Nat
  expiresAt          : Nat
  deriving DecidableEq, Repr

/-- `PendingProposal`: the payload fields plus the stored `payload_to_sign`. -/
structure Proposal where
  fields        : PayloadFields
  payloadToSign : Nat
  deriving DecidableEq, Repr

abbrev Character := Field → Nat

/-- The organism state `authorize_and_apply` reads and writes. -/
structure Org where
  organismId       : Nat
  pubKey           : Nat
  character        : Character
  pending          : Nat → Option Proposal
  consumed         : List (Nat × Nat)
  gates            : Field → Option Bool
  mutationSequence : Nat
  traceHead        : Nat

/-- `for k, v in change.items(): character[k] = v`, in order. -/
def applyChange (ch : Character) : List (Field × Nat) → Character
  | [] => ch
  | (k, v) :: rest => applyChange (fun f => if f = k then v else ch f) rest

/-- The primitives everything is parameterised over. Properties quantify over
    every `Crypto`; nothing about these functions is assumed unless a theorem
    states it as a hypothesis. -/
structure Crypto where
  hashCp    : Checkpoint → Nat        -- sha256(checkpoint_payload(cp))
  cpMsg     : Checkpoint → Nat        -- checkpoint_payload(cp): the signed bytes
  birthRoot : Birth → Nat             -- _birth_root()
  charRoot  : Character → Nat         -- _character_root()
  encode    : PayloadFields → Nat     -- _recompute_payload(p)
  verify    : Nat → Nat → Nat → Bool  -- Ed25519 verify(public_key, message, signature)
  inRange   : Nat → Bool              -- numeric and VALUE_MIN ≤ v ≤ VALUE_MAX
  nextHead  : Nat → Nat               -- trace head after one _append_trace

end HumbleSeedKernel
