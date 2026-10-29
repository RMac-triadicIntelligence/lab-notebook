import HumbleSeedKernel.Spec
import HumbleSeedKernel.Model

/-!
# Properties that hold

V071a and V071 reuse `V07.record`, `V07.checkSuccessor` and `V07.authorizeAndApply`
unchanged, so every theorem below about those functions is a theorem about all
three versions.
-/

namespace HumbleSeedKernel

/-! ## Lemmas about the authorization path -/

namespace V07

/-- The guards, named. -/
structure Guards (c : Crypto) (now : Nat) (s : Org) (p : Proposal) (sig : Nat) : Prop where
  notConsumed : consumeKey p ∉ s.consumed
  org         : p.fields.organismId = s.organismId
  unexpired   : now ≤ p.fields.expiresAt
  charRoot    : p.fields.priorCharacterRoot = c.charRoot s.character
  traceHead   : p.fields.priorTraceHead = s.traceHead
  mutSeq      : p.fields.mutationSequence = s.mutationSequence
  firstCommit : p.fields.firstCommit = (s.gates p.fields.category).getD true
  schema      : schemaOk c p = true
  payload     : c.encode p.fields = p.payloadToSign
  verify      : c.verify s.pubKey (c.encode p.fields) sig = true

theorem guards_of_checksPass {c : Crypto} {now : Nat} {s : Org} {p : Proposal} {sig : Nat}
    (h : checksPass c now s p sig = true) : Guards c now s p sig := by
  unfold checksPass at h
  simp only [Bool.and_eq_true, Bool.not_eq_true', decide_eq_true_eq, decide_eq_false_iff_not] at h
  obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9, h10⟩ := h
  exact ⟨h1, h2, by omega, h4, h5, h6, h7, h8, h9, h10⟩

theorem apply_true {c : Crypto} {now : Nat} {s : Org} {pid sig : Nat} {s' : Org}
    (h : authorizeAndApply c now s pid sig = (s', true)) :
    ∃ p, s.pending pid = some p ∧ checksPass c now s p sig = true ∧ s' = applied c s pid p := by
  unfold authorizeAndApply at h
  split at h
  · unfold rejectOrg at h
    injection h with _ h2
    cases h2
  · rename_i p hp
    refine ⟨p, hp, ?_⟩
    by_cases hc : checksPass c now s p sig = true
    · rw [if_pos hc] at h
      injection h with h1 _
      exact ⟨hc, h1.symm⟩
    · rw [if_neg hc] at h
      unfold rejectOrg at h
      injection h with _ h2
      cases h2

theorem apply_false {c : Crypto} {now : Nat} {s : Org} {pid sig : Nat} {s' : Org}
    (h : authorizeAndApply c now s pid sig = (s', false)) :
    s' = { s with traceHead := c.nextHead s.traceHead } := by
  unfold authorizeAndApply at h
  split at h
  · unfold rejectOrg at h
    injection h with h1 _
    exact h1.symm
  · split at h
    · injection h with _ h2
      cases h2
    · unfold rejectOrg at h
      injection h with h1 _
      exact h1.symm

theorem schemaOk_spec {c : Crypto} {p : Proposal} (h : schemaOk c p = true) :
    p.fields.change ≠ [] ∧
    ∀ kv ∈ p.fields.change, kv.1 = p.fields.category ∧ c.inRange kv.2 = true := by
  unfold schemaOk at h
  rw [Bool.and_eq_true] at h
  obtain ⟨h1, h2⟩ := h
  refine ⟨?_, ?_⟩
  · intro hnil
    rw [hnil] at h1
    simp at h1
  · intro kv hkv
    have hk := List.all_eq_true.mp h2 kv hkv
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hk
    exact hk

end V07

theorem applyChange_other (l : List (Field × Nat)) (cat f : Field) (hf : f ≠ cat) :
    ∀ (ch : Character), (∀ kv ∈ l, kv.1 = cat) → applyChange ch l f = ch f := by
  induction l with
  | nil => intro ch _; rfl
  | cons kv rest ih =>
    intro ch hall
    obtain ⟨k, v⟩ := kv
    have hk : k = cat := hall (k, v) (by simp)
    have hrest : ∀ kv ∈ rest, kv.1 = cat := fun kv hkv => hall kv (by simp [hkv])
    simp only [applyChange]
    rw [ih _ hrest]
    subst hk
    simp [hf]

theorem applyChange_cat (P : Nat → Bool) (cat : Field) (l : List (Field × Nat)) :
    ∀ (ch : Character), l ≠ [] → (∀ kv ∈ l, kv.1 = cat ∧ P kv.2 = true) →
      P (applyChange ch l cat) = true := by
  induction l with
  | nil => intro ch hne _; exact absurd rfl hne
  | cons kv rest ih =>
    intro ch _ hall
    obtain ⟨k, v⟩ := kv
    have hrest : ∀ kv ∈ rest, kv.1 = cat ∧ P kv.2 = true := fun kv hkv => hall kv (by simp [hkv])
    by_cases hr : rest = []
    · subst hr
      obtain ⟨h1, h2⟩ := hall (k, v) (by simp)
      simp only at h1 h2
      subst h1
      simp [applyChange, h2]
    · simp only [applyChange]
      exact ih _ hr hrest

/-! ## B: the authorization path (all three versions) -/

theorem v07_B1 : NoChangeWithoutExactSignature V07.authorizeAndApply := by
  intro c now s pid sig s' h
  obtain ⟨p, hp, hc, rfl⟩ := V07.apply_true h
  have g := V07.guards_of_checksPass hc
  exact ⟨p, hp, g.verify, g.org, rfl⟩

theorem v07_B1' : RejectionPreservesAuthority V07.authorizeAndApply := by
  intro c now s pid sig s' h
  have h' := V07.apply_false h
  subst h'
  exact ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem v07_B2 : OnlyProposedCategory V07.authorizeAndApply := by
  intro c now s pid sig s' h
  obtain ⟨p, hp, hc, rfl⟩ := V07.apply_true h
  have g := V07.guards_of_checksPass hc
  obtain ⟨hne, hall⟩ := V07.schemaOk_spec g.schema
  refine ⟨p, hp, ?_, ?_⟩
  · intro f hf
    exact applyChange_other p.fields.change p.fields.category f hf s.character
      (fun kv hkv => (hall kv hkv).1)
  · exact applyChange_cat c.inRange p.fields.category p.fields.change s.character hne hall

theorem v07_B3 : SingleUse V07.authorizeAndApply := by
  intro c now s pid sig s' h
  obtain ⟨p, hp, _, rfl⟩ := V07.apply_true h
  have hnone : (V07.applied c s pid p).pending pid = none := by simp [V07.applied]
  refine ⟨hnone, ⟨p, hp, by simp [V07.applied, V07.consumeKey]⟩, ?_⟩
  intro now' sig'
  unfold V07.authorizeAndApply
  simp [hnone, V07.rejectOrg]

theorem v07_B3' : ConsumedNeverApplies V07.authorizeAndApply := by
  intro c now s pid sig p hp hmem
  have hc : V07.checksPass c now s p sig ≠ true := fun hc =>
    (V07.guards_of_checksPass hc).notConsumed hmem
  unfold V07.authorizeAndApply
  simp [hp, hc, V07.rejectOrg]

theorem v07_B4 : BoundToReadState V07.authorizeAndApply := by
  intro c now s pid sig s' h
  obtain ⟨p, hp, hc, rfl⟩ := V07.apply_true h
  have g := V07.guards_of_checksPass hc
  exact ⟨p, hp, g.charRoot, g.traceHead, g.mutSeq, g.unexpired, g.firstCommit, rfl⟩

/-! ## Lemmas about the witness -/

namespace V07

theorem known_ok {c : Crypto} {cp : Checkpoint} {k : Entry}
    (h : checkCurrentKnown c cp k = .ok) :
    c.hashCp cp = k.checkpointHash ∧ cp.sequence = k.sequence ∧
    (∀ b, k.birthRoot = some b → cp.birthRoot = b) := by
  unfold checkCurrentKnown checkIdentity at h
  cases hb : k.birthRoot with
  | none =>
    simp only [hb] at h
    by_cases h1 : cp.sequence < k.sequence
    · simp [h1] at h
    by_cases h2 : k.sequence < cp.sequence
    · simp [h1, h2] at h
    by_cases h3 : c.hashCp cp = k.checkpointHash
    · exact ⟨h3, by omega, fun b hb' => by cases hb'⟩
    · simp [h1, h2, h3] at h
  | some pinned =>
    simp only [hb] at h
    by_cases h0 : cp.birthRoot = pinned
    · by_cases h1 : cp.sequence < k.sequence
      · simp [h0, h1] at h
      by_cases h2 : k.sequence < cp.sequence
      · simp [h0, h1, h2] at h
      by_cases h3 : c.hashCp cp = k.checkpointHash
      · exact ⟨h3, by omega, fun b hb' => by cases hb'; exact h0⟩
      · simp [h0, h1, h2, h3] at h
    · simp [h0] at h

theorem record_frame (c : Crypto) (L : Ledger) (cp : Checkpoint) (o : Nat)
    (ho : o ≠ cp.organismId) : (record c L cp).1 o = L o := by
  unfold record
  cases hs : checkSuccessor c L cp with
  | ok => simp [Ledger.set, ho]
  | reject r => rfl

theorem record_ok_at (c : Crypto) (L : Ledger) (cp : Checkpoint)
    (h : (record c L cp).2 = .ok) :
    (record c L cp).1 cp.organismId = some (entryOf c cp) := by
  unfold record at h ⊢
  cases hs : checkSuccessor c L cp with
  | ok => simp [Ledger.set]
  | reject r => simp [hs] at h

theorem verifyState_ok {c : Crypto} {s : StateView} (h : verifyState c s = .ok) :
    s.birth.organismId = s.organismId ∧ s.otherChecksPass = true ∧
    c.verify s.birth.pubKey (c.cpMsg s.checkpoint) s.checkpointSig = true ∧
    s.checkpoint.organismId = s.organismId ∧
    s.checkpoint.birthRoot = c.birthRoot s.birth := by
  unfold verifyState at h
  by_cases hc : (s.birth.organismId = s.organismId ∧ s.otherChecksPass = true ∧
      c.verify s.birth.pubKey (c.cpMsg s.checkpoint) s.checkpointSig = true ∧
      s.checkpoint.organismId = s.organismId ∧
      s.checkpoint.birthRoot = c.birthRoot s.birth)
  · exact hc
  · rw [if_neg hc] at h
    cases h

end V07

theorem lastFor_cons_none {o : Nat} {cp : Checkpoint} {rest : List Checkpoint}
    (h : lastFor o (cp :: rest) = none) : lastFor o rest = none ∧ cp.organismId ≠ o := by
  unfold lastFor at h
  cases hr : lastFor o rest with
  | some x => simp [hr] at h
  | none =>
    simp [hr] at h
    exact ⟨rfl, h⟩

theorem lastFor_cons_some {o : Nat} {cp x : Checkpoint} {rest : List Checkpoint}
    (h : lastFor o (cp :: rest) = some x) :
    lastFor o rest = some x ∨ (lastFor o rest = none ∧ cp.organismId = o ∧ x = cp) := by
  unfold lastFor at h
  cases hr : lastFor o rest with
  | some y =>
    simp [hr] at h
    left; rw [h]
  | none =>
    simp [hr] at h
    right
    exact ⟨rfl, h.1, h.2.symm⟩

theorem runRecords_cons (record : RecordFn) (c : Crypto) (L : Ledger) (cp : Checkpoint)
    (rest : List Checkpoint) :
    runRecords record c L (cp :: rest) =
      ((runRecords record c (record c L cp).1 rest).1,
       decide ((record c L cp).2 = .ok) && (runRecords record c (record c L cp).1 rest).2) := rfl

theorem v07_run_frame (c : Crypto) : ∀ (hist : List Checkpoint) (L : Ledger) (o : Nat),
    lastFor o hist = none → (runRecords V07.record c L hist).1 o = L o := by
  intro hist
  induction hist with
  | nil => intro L o _; rfl
  | cons cp rest ih =>
    intro L o h
    obtain ⟨hrest, hne⟩ := lastFor_cons_none h
    rw [runRecords_cons]
    dsimp only
    rw [ih _ o hrest]
    exact V07.record_frame c L cp o (fun h' => hne h'.symm)

theorem v07_run_last (c : Crypto) : ∀ (hist : List Checkpoint) (L : Ledger),
    (runRecords V07.record c L hist).2 = true →
    ∀ o x, lastFor o hist = some x →
      (runRecords V07.record c L hist).1 o = some (V07.entryOf c x) := by
  intro hist
  induction hist with
  | nil => intro L _ o x h; simp [lastFor] at h
  | cons cp rest ih =>
    intro L hok o x hx
    rw [runRecords_cons] at hok ⊢
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hok
    obtain ⟨hrec, htail⟩ := hok
    dsimp only
    rcases lastFor_cons_some hx with hsome | ⟨hnone, hoid, hxc⟩
    · exact ih _ htail o x hsome
    · rw [v07_run_frame c rest _ o hnone, hxc, ← hoid]
      exact V07.record_ok_at c L cp hrec

/-! ## W: the witness -/

theorem v07_W1 : RecordValidated V07.record V07.checkSuccessor := by
  intro c L cp
  unfold V07.record
  cases hs : V07.checkSuccessor c L cp with
  | ok => exact ⟨rfl, fun hne => absurd rfl hne⟩
  | reject r => exact ⟨rfl, fun _ => rfl⟩

theorem v07_W2 : RecordWrites V07.record := by
  intro c L cp L' h
  unfold V07.record at h
  cases hs : V07.checkSuccessor c L cp with
  | reject r => simp [hs] at h
  | ok =>
    simp [hs] at h
    subst h
    refine ⟨?_, ?_⟩
    · simp [Ledger.set, V07.entryOf]
    · intro o ho
      simp [Ledger.set, ho]

theorem v07_W3 : SuccessorIsExactNextLink V07.checkSuccessor := by
  intro c L cp h
  unfold V07.checkSuccessor at h
  cases hL : L cp.organismId with
  | none =>
    simp only [hL] at h
    show cp.sequence = 0 ∧ cp.prevHash = zeroHash
    by_cases h1 : cp.sequence = 0
    · by_cases h2 : cp.prevHash = zeroHash
      · exact ⟨h1, h2⟩
      · simp [h1, h2] at h
    · simp [h1] at h
  | some k =>
    simp only [hL] at h
    show cp.sequence = k.sequence + 1 ∧ cp.prevHash = k.checkpointHash ∧
      (∀ b, k.birthRoot = some b → cp.birthRoot = b)
    unfold V07.checkIdentity at h
    cases hb : k.birthRoot with
    | none =>
      simp only [hb] at h
      by_cases h1 : cp.sequence = k.sequence + 1
      · by_cases h2 : cp.prevHash = k.checkpointHash
        · exact ⟨h1, h2, fun b hb' => by cases hb'⟩
        · simp [h1, h2] at h
      · simp [h1] at h
    | some pinned =>
      simp only [hb] at h
      by_cases h0 : cp.birthRoot = pinned
      · by_cases h1 : cp.sequence = k.sequence + 1
        · by_cases h2 : cp.prevHash = k.checkpointHash
          · exact ⟨h1, h2, fun b hb' => by cases hb'; exact h0⟩
          · simp [h0, h1, h2] at h
        · simp [h0, h1] at h
      · simp [h0] at h

/-- W4 holds once `check_current` fails closed. -/
theorem v071a_W4 : CurrentIsRecordedHead V071a.checkCurrent := by
  intro c L cp h
  unfold V071a.checkCurrent at h
  cases hL : L cp.organismId with
  | none => simp [hL] at h
  | some k =>
    simp only [hL] at h
    exact ⟨k, rfl, V07.known_ok h⟩

theorem v071_W4 : CurrentIsRecordedHead V071.checkCurrent := by
  intro c L cp h
  exact v071a_W4 c L cp h

/-- W5 on a witness holding only the expected organism: the one-line fix suffices. -/
theorem v071a_W5s : AuditBindsExpectedSingle V071a.audit := by
  intro c L expected s hone hexp h
  unfold V071a.audit at h
  cases hv : V07.verifyState c s with
  | reject r => simp [hv] at h
  | ok =>
    simp only [hv] at h
    obtain ⟨k, hk, hhash, -, -⟩ := v071a_W4 c L s.checkpoint h
    have hsome : (L s.checkpoint.organismId).isSome = true := by simp [hk]
    have heq : s.checkpoint.organismId = expected := hone _ _ hsome hexp
    refine ⟨heq, k, ?_, hhash⟩
    rw [← heq]
    exact hk

/-- W5 in general: needs the audit bound to the expected organism. -/
theorem v071_W5 : AuditBindsExpected V071.audit := by
  intro c L expected s h
  unfold V071.audit at h
  cases hv : V07.verifyState c s with
  | reject r => simp [hv] at h
  | ok =>
    simp only [hv] at h
    by_cases he : s.checkpoint.organismId = expected
    · rw [if_pos he] at h
      obtain ⟨k, hk, hhash, -, -⟩ := v071_W4 c L s.checkpoint h
      refine ⟨he, k, ?_, hhash⟩
      rw [← he]
      exact hk
    · rw [if_neg he] at h
      cases h

theorem v071_W5s : AuditBindsExpectedSingle V071.audit := by
  intro c L expected s _ _ h
  exact v071_W5 c L expected s h

/-- W6: no rollback and no fork for any enrolled organism. Holds on v0.7 already;
    the defect is confined to the unenrolled branch. -/
theorem v07_W6 : NoRollbackOverHistory V07.record V07.checkCurrent := by
  intro c hist cp hinj hok hsome hcur
  cases hlf : lastFor cp.organismId hist with
  | none => simp [hlf] at hsome
  | some x =>
    have hL := v07_run_last c hist Ledger.empty hok cp.organismId x hlf
    unfold V07.checkCurrent at hcur
    simp only [hL] at hcur
    have hcx : cp = x := hinj _ _ (V07.known_ok hcur).1
    rw [hcx]

theorem v071a_W6 : NoRollbackOverHistory V07.record V071a.checkCurrent := by
  intro c hist cp hinj hok hsome hcur
  cases hlf : lastFor cp.organismId hist with
  | none => simp [hlf] at hsome
  | some x =>
    have hL := v07_run_last c hist Ledger.empty hok cp.organismId x hlf
    unfold V071a.checkCurrent at hcur
    simp only [hL] at hcur
    have hcx : cp = x := hinj _ _ (V07.known_ok hcur).1
    rw [hcx]

theorem v071_W6 : NoRollbackOverHistory V07.record V071.checkCurrent :=
  v071a_W6

/-! ## E: end to end -/

theorem v071_E1 : BirthPinned V071.audit := by
  intro c L expected s k r₀ hk hr h
  unfold V071.audit at h
  cases hv : V07.verifyState c s with
  | reject r => simp [hv] at h
  | ok =>
    simp only [hv] at h
    by_cases he : s.checkpoint.organismId = expected
    · rw [if_pos he] at h
      obtain ⟨k', hk', -, -, hpin⟩ := v071_W4 c L s.checkpoint h
      rw [he, hk] at hk'
      cases hk'
      rw [← (V07.verifyState_ok hv).2.2.2.2]
      exact hpin r₀ hr
    · rw [if_neg he] at h
      cases h

/-- The composed guarantee, on v0.7.1. If the owner enrolled birth record `b₀`,
    the audit passes, and the organism was loaded from the audited state (its
    verifying key is the birth record's, as `load()` does on line 643), then every
    character change it accepts was signed under `b₀`'s key, and is exactly the
    signed change. Assumes only that the birth root is collision-free. -/
theorem v071_audited_changes_need_enrolled_key
    (c : Crypto) (hinj : Inj c.birthRoot)
    (L : Ledger) (expected : Nat) (s : StateView) (k : Entry) (b₀ : Birth)
    (hk : L expected = some k) (hr : k.birthRoot = some (c.birthRoot b₀))
    (haudit : V071.audit c L expected s = .ok)
    (o : Org) (hload : o.pubKey = s.birth.pubKey)
    (now pid sig : Nat) (o' : Org)
    (happ : V07.authorizeAndApply c now o pid sig = (o', true)) :
    ∃ p, o.pending pid = some p ∧
      c.verify b₀.pubKey (c.encode p.fields) sig = true ∧
      o'.character = applyChange o.character p.fields.change := by
  have hroot := v071_E1 c L expected s k (c.birthRoot b₀) hk hr haudit
  have hb : s.birth = b₀ := hinj _ _ hroot
  obtain ⟨p, hp, hv, -, hch⟩ := v07_B1 c now o pid sig o' happ
  refine ⟨p, hp, ?_, hch⟩
  rw [← hb, ← hload]
  exact hv

end HumbleSeedKernel
