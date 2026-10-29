#!/usr/bin/env python3
"""Derives humble_seed_v0_8_5_candidate.py from v0.8.4 by exact-once replacements."""
import sys
from pathlib import Path

src_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
src = src_path.read_text(encoding="utf-8")


def once(old, new):
    global src
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"anchor occurs {n} times:\n{old[:300]}")
    src = src.replace(old, new)


start = src.index('"""')
end_marker = 'Run the falsification harness:  python3 -I falsify_v0_8_4.py\n"""'
end = src.index(end_marker) + len(end_marker)
DOC = '''"""
Humble Seed v0.8.5 CANDIDATE — Saved-State Recovery, Apply = Replay, Owner Window
==================================================================================

STATUS: candidate, not canonical. Parent: humble_seed_v0_8_4_candidate.py
(sha256 d66c10e4...). Round 5 (ChatGPT, blind) found four defects in v0.8.4.
Recovery trusted the organism object it was handed. Apply accepted what replay
refuses. The owner's category window began at its own signature. Everything
not listed is carried from v0.8.4 unchanged, including the three rulings and
the one serialized owner authority.

CHANGES

  V  RECOVERY READS THE ORGANISM'S SAVED STATE. attest and audit decide
     whether an interrupted commit was installed from the checkpoint and
     signature in the organism's saved state file, re-read under the owner lock,
     not from the object handed in, which may be stale or ahead of its own disk.
     install_checkpoint changes nothing in memory unless its save succeeds.

  A  APPLY = REPLAY. Before changing any state, authorize_and_apply runs the
     owner's replay function on the crossing it is about to make, from its live
     state, and refuses ("replay would refuse this crossing: ...") whatever that
     replay refuses. This covers an annotation that is not a short string, an
     authorized_at outside the reading's window (e.g. a clock behind issuance),
     and every other record check. One clock reading now serves both the expiry
     check and the record.

  W  OWNER-VERIFIABLE CATEGORY WINDOW. The owner counts its answers in a
     category from its own signature of the previous crossing in that category,
     or from the start of its record for the first, not from its signature of
     this reading. The round-5 disposition planned "from the last attested
     crossing". This was built from the previous crossing's signature instead: it
     needs no new owner state, and it is never later, so it holds at least as
     often.

  H  HOUSEKEEPING (harness and declaration). T53 signs off from a freshly
     opened session (v0.8.4 DEVIATIONS E2). T56 probes the lock from the
     organism's install, outside the replay (E1). XP1 is renamed to what it
     removes, and XP1b removes the protection itself (ChatGPT r5 F5).

FINDINGS CLOSED (all ChatGPT, round 5, blind)
  F1  A category "no" given before signing was outside the owner's window, so
      an organism-only "yes" cleared the only veto that saw it -> W.
  F2  Recovery committed a checkpoint that existed only in memory -> V.
  F3  A stale organism object abandoned an installed intent -> V.
  F4  A 2001-character annotation applied but could never be attested -> A.
  F5  XP1's kill was a refusal-message change -> renamed; XP1b added.

CREDIT CORRECTION (carried from REVIEWS.md, 2026-10-18). The v0.8.4 docstring
and declaration, both frozen, credit the author's A1 and A2 as "sealed first".
They were sealed after ChatGPT's in-progress screen had named both lines of
attack. Credit for both goes to ChatGPT.

LIMITS. R1-R28 as in v0.8.4, except:
  R18 (revised) On the organism, a "no" given before a reading was taken does
      not hold it. On the owner side it now can. An owner "no" in the category
      since the owner signed the previous crossing there (ever, for the first)
      blocks attestation until the owner answers again in that category.
  R22 (revised) The two sides still use different windows. The organism's
      window runs from the reading's issuance (its own claim). The owner's runs
      from its own signature of the previous crossing in the category, which is
      never later. The owner's check is the authority.
  R29 Apply checks its new crossing from the live state. If the live state does
      not itself replay (tampering), apply can still make a crossing the owner
      will refuse. That refusal is the design.
  R30 Recovery trusts the organism's saved file only to choose between
      completing and abandoning a checkpoint the owner itself signed after
      replay. A forged file can at worst advance the witness to that
      owner-approved checkpoint, and the organism then loads only if its content
      matches it.
  R31 Only install_checkpoint is transactional in memory. If another organism
      operation's save fails, the object is left ahead of its disk. The next
      successful save, or a reload, reconciles the two.

Run the falsification harness:  python3 -I falsify_v0_8_5.py
"""'''
src = src[:start] + DOC + src[end:]

once('SCHEMA_VERSION = "0.8.4-candidate"\n', 'SCHEMA_VERSION = "0.8.5-candidate"\n')

# V: install_checkpoint changes nothing in memory unless its save succeeds
once('''        self.checkpoint = cp
        self.checkpoint_sig = signature_b64
        self._append_trace({
            "event": "checkpoint",
            "sequence": cp.sequence,
            "birth_root": cp.birth_root,
            "constitution_root": cp.constitution_root,
            "gates_root": cp.gates_root,
            "character_root": cp.character_root,
            "timestamp": cp.timestamp,
        })
        self._save()
        return True
''', '''        # v0.8.5 (ChatGPT round 5, F2): nothing changes in memory unless the save succeeds.
        kept = (self.checkpoint, self.checkpoint_sig, len(self.trace), self._trace_head)
        self.checkpoint = cp
        self.checkpoint_sig = signature_b64
        self._append_trace({
            "event": "checkpoint",
            "sequence": cp.sequence,
            "birth_root": cp.birth_root,
            "constitution_root": cp.constitution_root,
            "gates_root": cp.gates_root,
            "character_root": cp.character_root,
            "timestamp": cp.timestamp,
        })
        try:
            self._save()
        except BaseException:
            self.checkpoint, self.checkpoint_sig, n, self._trace_head = kept   # [INSTALL-ROLLBACK]
            del self.trace[n:]
            raise
        return True
''')

# A: one clock reading
once('''        if self.clock() > p.expires_at:
            self._reject(proposal_id, "proposal expired")
''', '''        now = self.clock()                 # v0.8.5: one clock reading, for expiry and for the record
        if now > p.expires_at:
            self._reject(proposal_id, "proposal expired")
''')

# A: build the record first, check it with the owner's replay, then change state
once('''        prior = dict(self.character)
        self.character[p.category] = float(destination)
        self.category_sequence[p.category] = current_seq + 1
        self.consumed.add(consume_key)
        self.mutation_sequence += 1
        del self.pending[proposal_id]

        record = MutationRecord(
            proposal_id=p.proposal_id, category=p.category, lead=lead, delta=delta,
            prior_value=p.prior_value, change={p.category: float(destination)},
            distribution=p.distribution, evidence=p.evidence,
            first_commit=p.first_commit,
            category_sequence=self.category_sequence[p.category],
            mutation_sequence=self.mutation_sequence,
            authorized_at=self.clock(), signature_b64=signature_b64,
            signed_payload=recomputed,
            prior_character_snapshot=prior, unverified_annotation=annotation,
        )
        self._append_trace({
            "event": "authorized_mutation",
            "record": asdict(record),
            "timestamp": record.authorized_at,
        })
        self.basin = [q for q in self.basin if q.category != p.category]
''', '''        # v0.8.5: the record is built before anything changes, so it can be checked first.
        prior = dict(self.character)
        record = MutationRecord(
            proposal_id=p.proposal_id, category=p.category, lead=lead, delta=delta,
            prior_value=p.prior_value, change={p.category: float(destination)},
            distribution=p.distribution, evidence=p.evidence,
            first_commit=p.first_commit,
            category_sequence=current_seq + 1,
            mutation_sequence=self.mutation_sequence + 1,
            authorized_at=now, signature_b64=signature_b64,
            signed_payload=recomputed,
            prior_character_snapshot=prior, unverified_annotation=annotation,
        )
        entry = {
            "event": "authorized_mutation",
            "record": asdict(record),
            "timestamp": record.authorized_at,
        }
        # v0.8.5 (ChatGPT round 5, F4): apply refuses anything the owner's replay would
        # refuse in this crossing, before any state changes. Same function, same checks.
        apply_refusal = self._replay_refusal(entry)
        if apply_refusal is not None:                        # [APPLY=REPLAY]
            self._reject(proposal_id, f"replay would refuse this crossing: {apply_refusal}")
            return None

        self.character[p.category] = float(destination)
        self.category_sequence[p.category] = current_seq + 1
        self.consumed.add(consume_key)
        self.mutation_sequence += 1
        del self.pending[proposal_id]
        self._append_trace(entry)
        self.basin = [q for q in self.basin if q.category != p.category]
''')

once('''    def _reject(self, proposal_id: str, reason: str) -> None:
''', '''    def _replay_refusal(self, entry: Dict[str, Any]) -> Optional[str]:
        """v0.8.5 (ChatGPT round 5, F4). Run the owner's replay on this one crossing,
        from the live state, as if it were already the next trace entry.
        None means the replay accepts it; otherwise the replay's reason."""
        probe = dict(entry)
        probe["prev_hash"] = self._trace_head
        try:
            probe["entry_hash"] = _sha256(_canonical_json(probe))
            replay_signed_history(
                self.constitution, self.trace + [probe], self.public_key, self.organism_id,
                resume={"character": self.character, "category_sequence": self.category_sequence,
                        "consumed": self.consumed, "mutation_sequence": self.mutation_sequence,
                        "from_index": len(self.trace)})
        except (AttestationRefused, ValueError) as why:
            return str(why)
        return None

    def _reject(self, proposal_id: str, reason: str) -> None:
''')

# A: replay can resume from a given state (used by apply for its next crossing)
once('''def replay_signed_history(constitution: Dict[str, Any], trace: List[Dict[str, Any]],
                          owner_public_key: Ed25519PublicKey, organism_id: str) -> Dict[str, Any]:
    """D4. Rebuild character, category sequences, consumed ledger and mutation
    count from the genesis character in the attested constitution, applying only
    readings this owner signed. Raises AttestationRefused on anything else."""
''', '''def replay_signed_history(constitution: Dict[str, Any], trace: List[Dict[str, Any]],
                          owner_public_key: Ed25519PublicKey, organism_id: str,
                          resume: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """D4. Rebuild character, category sequences, consumed ledger and mutation
    count from the genesis character in the attested constitution, applying only
    readings this owner signed. Raises AttestationRefused on anything else.
    v0.8.5: with `resume`, start from the given state at trace index from_index
    (the organism uses this to check its next crossing before applying it)."""
''')
once('''    mseq = 0
    applied: List[Tuple[int, Dict[str, Any]]] = []

    for i, entry in enumerate(trace[1:], start=1):
''', '''    mseq = 0
    applied: List[Tuple[int, Dict[str, Any]]] = []
    first = 1
    if resume is not None:
        character = {k: float(v) for k, v in resume["character"].items()}
        gates = dict(resume["category_sequence"])
        consumed = set(resume["consumed"])
        mseq = int(resume["mutation_sequence"])
        first = int(resume["from_index"])

    for i, entry in enumerate(trace[first:], start=first):
''')

# W: owner-verifiable category window
once('''    def _check_owner_acts(self, seed: HumbleSeed, i: int, rec: Dict[str, Any],
                          now: float, ttl: float) -> None:
        """Rulings 1-3 for one crossing applied since the last attestation."""
''', '''    def _check_owner_acts(self, seed: HumbleSeed, i: int, rec: Dict[str, Any],
                          now: float, ttl: float, prev: Optional[Dict[str, Any]] = None) -> None:
        """Rulings 1-3 for one crossing applied since the last attestation. `prev` is
        the previous crossing in the same category, from the replay (None: the first)."""
''')
once('''        held = answer_position(self.ledger.answers_to(oid, pid),
                               self.ledger.answers_in_category_after(oid, cat, entry["seq"]))
        if held is not None:
            raise AttestationRefused(f"trace index {i}: owner's position: {held}")
''', '''        # v0.8.5 (ChatGPT round 5, F1): the owner's category window starts where the owner
        # can verify it: its own signature of the previous crossing in this category, or
        # the start of its record for the first. That signature precedes this reading's
        # issuance, so every answer given since the reading was taken is inside the window.
        if prev is None:
            window_start = 0
            window = "since its record began"
        else:
            prev_signed = self.ledger.signed(oid, _sha256(prev["signed_payload"]))
            if prev_signed is None:
                raise AttestationRefused(
                    f"trace index {i}: the previous {cat} crossing was not signed through this owner tool")
            window_start = prev_signed["seq"]                # [OWNER-WINDOW]
            window = f"since it signed the previous {cat} crossing"
        held = answer_position(self.ledger.answers_to(oid, pid),
                               self.ledger.answers_in_category_after(oid, cat, window_start))
        if held is not None:
            raise AttestationRefused(f"trace index {i}: owner's position: {held} "
                                     f"(owner's window: its answers in {cat} {window})")
''')
once('''        for i, rec in st["applied"]:
            if i >= since:
                self._check_owner_acts(seed, i, rec, now, ttl)
''', '''        previous: Dict[str, Dict[str, Any]] = {}
        for i, rec in st["applied"]:
            if i >= since:
                self._check_owner_acts(seed, i, rec, now, ttl, previous.get(rec["category"]))
            previous[rec["category"]] = rec
''')

# V: recovery decided from the organism's saved state
once('''    def _recover(self, seed: HumbleSeed) -> Optional[str]:
        """Complete or abandon a checkpoint commit that was interrupted between
        the witness intent and the witness advance (ChatGPT round 4, F4)."""
        oid = seed.organism_id
        p = self.witness.pending_for(oid)
        if p is None:
            return None
        pending_cp = Checkpoint(**p["checkpoint"])
        installed = (seed.checkpoint is not None and seed.checkpoint_sig == p["signature_b64"]
                     and HumbleSeed.checkpoint_payload(seed.checkpoint)
                     == HumbleSeed.checkpoint_payload(pending_cp))
        if installed:
            self.witness.commit(pending_cp)
            return "completed"
        head = self.witness.ledger.get(oid)
        at_head = ((head is None and seed.checkpoint is None)
                   or (head is not None and seed.checkpoint is not None
                       and OwnerWitness._checkpoint_hash(seed.checkpoint) == head["checkpoint_hash"]))
        if at_head:
            self.witness.abandon(oid)
            return "abandoned"
        raise RollbackDetected("A pending checkpoint commit matches neither the organism nor the witness head")
''', '''    def _saved_checkpoint(self, seed: HumbleSeed) -> Tuple[Optional[Checkpoint], Optional[str]]:
        """v0.8.5 (ChatGPT round 5, F2/F3): the checkpoint and signature in the
        organism's saved state, re-read now under the owner lock, not the object's."""
        try:
            data = _strict_loads(seed._state_path().read_text(encoding="utf-8"))
            cp = data.get("checkpoint")
            return (Checkpoint(**cp) if cp else None), data.get("checkpoint_sig")
        except (OSError, ValueError, TypeError, AttributeError) as why:
            raise RollbackDetected("A pending checkpoint commit cannot be resolved: the organism's "
                                   f"saved state is unreadable ({type(why).__name__})")

    def _recover(self, seed: HumbleSeed) -> Optional[str]:
        """Complete or abandon a checkpoint commit that was interrupted between
        the witness intent and the witness advance (ChatGPT round 4, F4).
        v0.8.5: decided from the organism's saved state, never from the object
        handed in, which may be stale or ahead of its own disk."""
        oid = seed.organism_id
        p = self.witness.pending_for(oid)
        if p is None:
            return None
        pending_cp = Checkpoint(**p["checkpoint"])
        saved_cp, saved_sig = self._saved_checkpoint(seed)       # [RECOVER-FROM-DISK]
        installed = (saved_cp is not None and saved_sig == p["signature_b64"]
                     and HumbleSeed.checkpoint_payload(saved_cp)
                     == HumbleSeed.checkpoint_payload(pending_cp))
        if installed:
            self.witness.commit(pending_cp)
            return "completed"
        head = self.witness.ledger.get(oid)
        at_head = ((head is None and saved_cp is None)
                   or (head is not None and saved_cp is not None
                       and OwnerWitness._checkpoint_hash(saved_cp) == head["checkpoint_hash"]))
        if at_head:
            self.witness.abandon(oid)
            return "abandoned"
        raise RollbackDetected("A pending checkpoint commit matches neither the organism's saved state "
                               "nor the witness head")
''')

once('''    print("Run the harness: python3 -I falsify_v0_8_4.py")''', '''    print("Run the harness: python3 -I falsify_v0_8_5.py")''')

out_path.write_text(src, encoding="utf-8")
print("written", out_path, len(src.splitlines()), "lines")
