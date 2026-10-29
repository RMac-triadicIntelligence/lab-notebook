#!/usr/bin/env python3
"""Derives humble_seed_v0_8_7_candidate.py from v0.8.6 by exact-once replacements."""
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


def span(start_marker, end_marker, new):
    """Replace from start_marker up to and including end_marker (each exactly once)."""
    global src
    for m in (start_marker, end_marker):
        if src.count(m) != 1:
            raise SystemExit(f"span marker occurs {src.count(m)} times:\n{m[:200]}")
    a = src.index(start_marker)
    b = src.index(end_marker) + len(end_marker)
    if b <= a:
        raise SystemExit("span markers out of order")
    src = src[:a] + new + src[b:]


start = src.index('"""')
end_marker = 'Run the falsification harness:  python3 -I falsify_v0_8_6.py\n"""'
end = src.index(end_marker) + len(end_marker)
DOC = '''"""
Humble Seed v0.8.7 CANDIDATE — One Operation at a Time, and Restore
====================================================================

STATUS: candidate, not canonical. Parent: humble_seed_v0_8_6_candidate.py
(sha256 3711074f...). Round 7 (ChatGPT claims battery) showed that v0.8.6's
persistence protocol did not hold for one organism object used from two
threads: a save took its snapshot before the lock, and its generation check
compared a number the other thread had already advanced. An update could be
lost, or a signed-off checkpoint rewound with the witness left ahead and no
recovery. It happens without instrumentation. Everything not listed is
carried from v0.8.6 unchanged.

CHANGES

  Q  ONE OPERATION AT A TIME PER ORGANISM.
     - hatch, load, dwell_or_propose, record_owner_answer, authorize_and_apply
       and install_checkpoint each hold the organism lock (organism.lock: POSIX
       flock across processes, serialized across threads, reentrant within a
       thread) from a currency check, through every change to memory, to the
       save.
     - A save takes its snapshot and its new generation under the lock.
     - A stale object is refused before it changes anything in memory.
     - The owner's answer, attest, audit and restore hold the same lock.
     - The save's own generation check stays: it catches a write that lands
       during an operation through a callback in the same thread (the reader).

  U  A SAVE WHOSE OUTCOME CANNOT BE CONFIRMED LEAVES THE OBJECT UNUSABLE. If a
     save fails and the saved generation cannot be re-read, the object refuses
     every operation until it is reloaded. install_checkpoint does not roll
     memory back on a guess.

  G  A SAVED FILE WITHOUT A VALID GENERATION REFUSES EVERY WRITE, including a
     new hatch (author A1: a hatch replaced such a file).

  A  AN ANSWER THROUGH A STALE OBJECT IS REFUSED BEFORE ANY RECORD CHANGES.
     Neither the owner's ledger nor the organism records it, and the error
     says so.

  R  RESTORE TO THE LAST ATTESTED STATE (R20). OwnerTool.restore first resolves
     any pending commit, then rebuilds the organism at the witness head from
     the attested prefix of its saved trace (replayed and verified before
     anything is written), discards everything after it and every pending
     reading, keeps the discarded file beside the state, and records a
     non-authorizing "restored" event. The witness does not move.

  H  HOUSEKEEPING (declaration). The rules name v0.8.7's files; refusal traces
     cite the raise line.

FINDINGS CLOSED
  ChatGPT r7 F1  One object, two threads: lost update; signed-off checkpoint
                 rewound -> Q.
  ChatGPT r7 F2  Save outcome unconfirmed: memory rolled back while disk held
                 the new checkpoint -> U.
  ChatGPT r7 F3  A stale object took the owner's answer into memory before
                 refusing -> Q, A.
  Author  A1     A hatch replaced a saved file without a generation -> G.
  Author  A2     R31's wording -> R31 (revised).
  Author  A3     The stale-answer error did not say what was recorded -> A.
  R20            A crossing that missed its lifetime could never be attested
                 and could not be undone -> R (Rusty's ruling, 2026-10-19).

LIMITS. R1-R30, R32 and R34 as in v0.8.6, except:
  R20 (revised) A crossing must be attested within its reading's lifetime, by
      the owner's clock. If it is not, OwnerTool.restore brings the organism
      back to its last attested state; the crossing must be read and signed
      again.
  R31 (revised) Only install_checkpoint is transactional in memory. If another
      operation's save fails before landing, the object is ahead of its disk;
      its next operation writes that state unless another object has saved
      first, in which case it is refused as stale and the unsaved change is
      lost on reload. No object writes over a newer saved state.
  R33 (revised) A stale object must reload, and its unsaved changes are lost.
      It is refused before it changes anything. An answer given through a
      stale object is recorded nowhere.
  R35 Operations are serialized per organism data directory. Reading an
      object's attributes, or calling its private methods, outside these
      operations is not. A callback that runs inside an operation (the reader)
      runs under the lock; a write it makes through another object is caught
      by the save's generation check, and the operation is refused as stale.
  R36 Restore needs the attested prefix intact in the saved file. An
      unreadable file, or one truncated below the prefix, cannot be restored;
      no separate backup is kept. The basin (unattested evidence) is kept.

Run the falsification harness:  python3 -I falsify_v0_8_7.py
"""'''
src = src[:start] + DOC + src[end:]

once('SCHEMA_VERSION = "0.8.6-candidate"\n', 'SCHEMA_VERSION = "0.8.7-candidate"\n')
once('NON_AUTHORIZING_EVENTS = {"dwelling", "authorization_rejected", "checkpoint", "owner_answer", "reading_held"}\n',
     'NON_AUTHORIZING_EVENTS = {"dwelling", "authorization_rejected", "checkpoint", "owner_answer", "reading_held",\n'
     '                          "restored"}\n')

# Q: one operation at a time
once('''def _owner_locked(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with _OwnerLock(self.lock_path):
            return method(self, *args, **kwargs)
    return wrapper
''', '''def _owner_locked(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with _OwnerLock(self.lock_path):
            return method(self, *args, **kwargs)
    return wrapper


_UNUSABLE = -1      # v0.8.7: the generation of an object whose last save could not be confirmed


def _organism_op(method):
    """v0.8.7 (ChatGPT r7 F1, F3): one operation at a time per organism, across threads and
    processes. The organism lock is held from the currency check, through every change to
    memory, to the save, so no other operation interleaves with it or sees it half done;
    a stale or unusable object is refused before it changes anything."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._organism_lock():                     # [OP-LOCK]
            if self.organism_id is not None:
                self._check_current()                   # [OP-CURRENT]
            return method(self, *args, **kwargs)
    return wrapper
''')

once('''    def hatch(self, reading_ttl_seconds: float = GENESIS_READING_TTL_SECONDS
''', '''    @_organism_op
    def hatch(self, reading_ttl_seconds: float = GENESIS_READING_TTL_SECONDS
''')
once('''            raise RuntimeError("This seed has already hatched.")
''', '''            raise RuntimeError("This seed has already hatched.")
        self._check_current()                   # [HATCH-CURRENT] v0.8.7: refuse before generating anything
''')
once('''    def install_checkpoint(self, cp: Checkpoint, signature_b64: str) -> bool:
''', '''    @_organism_op
    def install_checkpoint(self, cp: Checkpoint, signature_b64: str) -> bool:
''')
once('''    def dwell_or_propose(self, category: str, event: str, transcript: str) -> dict:
''', '''    @_organism_op
    def dwell_or_propose(self, category: str, event: str, transcript: str) -> dict:
''')
once('''    def record_owner_answer(self, proposal_id: str, answer: str, text: str = "") -> dict:
''', '''    @_organism_op
    def record_owner_answer(self, proposal_id: str, answer: str, text: str = "") -> dict:
''')
once('''    def authorize_and_apply(
        self, proposal_id: str, signature_b64: str, annotation: str = "",
''', '''    @_organism_op
    def authorize_and_apply(
        self, proposal_id: str, signature_b64: str, annotation: str = "",
''')

# G: a saved file without a valid generation refuses every write
once('''        try:
            return _strict_loads(path.read_text(encoding="utf-8")).get("generation")
        except (ValueError, AttributeError) as why:
            raise StaleOrganism(f"the saved state is unreadable ({type(why).__name__}); refusing to write over it")
''', '''        try:
            g = _strict_loads(path.read_text(encoding="utf-8")).get("generation")
        except (ValueError, AttributeError) as why:
            raise StaleOrganism(f"the saved state is unreadable ({type(why).__name__}); refusing to write over it")
        if isinstance(g, bool) or not isinstance(g, int) or g < 0:          # [GEN-REQUIRED] v0.8.7 (author A1)
            raise StaleOrganism("the saved state has no valid generation; refusing to write over it")
        return g
''')

# Q, U: currency check, and the save under one lock
span('''    def _require_current(self) -> None:''',
     '''            self._generation = new_gen

    def load(self) -> None:
        path = self._state_path()
''', '''    def _check_current(self) -> None:
        """v0.8.7: the caller holds the organism lock. Refuse an object that is unusable
        or stale before it changes anything."""
        if self._generation == _UNUSABLE:                       # [UNUSABLE]
            raise StaleOrganism("organism object is unusable: a save failed and whether it landed "
                                "could not be confirmed; reload it")
        saved = self._saved_generation()
        if saved != self._generation:
            raise StaleOrganism(f"stale organism object: the saved state is at generation {saved}, "
                                f"this object last saw {self._generation}; reload it")

    def _require_current(self) -> None:
        """v0.8.6 (ChatGPT r6 F1): refuse to act on a stale object."""
        with self._organism_lock():
            self._check_current()

    def _save(self) -> None:
        if self.organism_id is None or self.birth is None:
            return
        with self._organism_lock():            # [SAVE-LOCK] v0.8.7 (ChatGPT r7 F1): check, snapshot and write under one lock
            if self._generation == _UNUSABLE:
                raise StaleOrganism("organism object is unusable: a save failed and whether it landed "
                                    "could not be confirmed; reload it")
            saved = self._saved_generation()
            if saved != self._generation:                    # [SAVE-CAS]
                raise StaleOrganism(f"stale organism object: the saved state is at generation {saved}, "
                                    f"this object last saw {self._generation}; reload it")
            new_gen = 0 if self._generation is None else self._generation + 1
            state = {
                "schema_version": SCHEMA_VERSION,
                "generation": new_gen,
                "organism_id": self.organism_id,
                "birth": asdict(self.birth),
                "constitution": self.constitution,
                "character": self.character,
                "basin": [asdict(p) for p in self.basin],
                "pending": {pid: asdict(p) for pid, p in self.pending.items()},
                "consumed": sorted(self.consumed),
                "trace": self.trace,
                "category_sequence": self.category_sequence,
                "mutation_sequence": self.mutation_sequence,
                "trace_head": self._trace_head,
                "checkpoint": asdict(self.checkpoint) if self.checkpoint else None,
                "checkpoint_sig": self.checkpoint_sig,
                "state_seal": self._compute_seal(),
            }
            text = _canonical_json(state)          # raises before anything is written
            try:
                _durable_write(self._state_path(), text)
            except BaseException:
                # v0.8.6 (ChatGPT r6 F2): the replace may already have landed; record what did.
                # v0.8.7 (ChatGPT r7 F2): if that cannot be confirmed, the object is unusable.
                try:
                    landed = self._saved_generation() == new_gen
                except Exception:
                    landed = None
                if landed is None:
                    self._generation = _UNUSABLE                 # [SAVE-INDETERMINATE]
                elif landed:
                    self._generation = new_gen                   # [SAVE-LANDED]
                raise
            self._generation = new_gen

    def load(self) -> None:
        """v0.8.7: under the organism lock, so no operation on this object interleaves with it."""
        with self._organism_lock():
            self._load_locked()

    def _load_locked(self) -> None:
        path = self._state_path()
''')

# R: restore mechanics on the organism side
once('''    def _verify_policy(self) -> None:
''', '''    def _restore_attested(self, expected_checkpoint_hash: str, owner_public_b64: str) -> Dict[str, Any]:
        """v0.8.7 (R20). Rebuild the last attested state from the saved file and discard
        everything after it. Called by OwnerTool.restore, which supplies the witness head:
        the restored checkpoint must be exactly that head. The restored state is replayed
        and verified before anything is written, and the discarded file is kept."""
        with self._organism_lock():
            raw = self._state_path().read_text(encoding="utf-8")
            try:
                data = _strict_loads(raw)
                g = data["generation"]
                cp = Checkpoint(**data["checkpoint"])
                sig = data["checkpoint_sig"]
                birth = BirthRecord(**data["birth"])
                constitution = data["constitution"]
                trace = data["trace"]
                basin = [PreTrace(**p) for p in data.get("basin", [])]
            except (ValueError, KeyError, TypeError, AttributeError) as why:
                raise IntegrityError(f"restore refused: the saved state cannot be read ({type(why).__name__}: {why})")
            if isinstance(g, bool) or not isinstance(g, int) or g < 0:
                raise IntegrityError("restore refused: the saved state has no valid generation")
            if birth.public_key_b64 != owner_public_b64:
                raise AttestationRefused("restore refused: organism is not keyed to this owner")
            if _sha256(HumbleSeed.checkpoint_payload(cp)) != expected_checkpoint_hash:      # [RESTORE-HEAD]
                raise RollbackDetected("restore refused: the saved checkpoint is not the witness head")
            n = cp.attested_trace_len
            prefix = [dict(e) for e in trace[:n]] if isinstance(trace, list) else []
            try:
                prefix_head = _check_chain(prefix)
            except (ValueError, AttributeError, TypeError):
                prefix_head = None
            if n < 1 or len(prefix) != n or prefix_head != cp.trace_head:                   # [RESTORE-PREFIX]
                raise IntegrityError("restore refused: the saved trace's attested prefix does not match the checkpoint")
            public_key = Ed25519PublicKey.from_public_bytes(base64.urlsafe_b64decode(birth.public_key_b64))
            try:
                st = replay_signed_history(constitution, prefix, public_key, data.get("organism_id"))
            except (AttestationRefused, KeyError, TypeError, ValueError) as why:
                raise IntegrityError(f"restore refused: the attested prefix does not replay ({why})")
            r = HumbleSeed(self.data_dir, reader=self.reader)
            r.clock = self.clock
            r.organism_id = data["organism_id"]
            r.birth, r.public_key, r.constitution = birth, public_key, constitution
            r.character = st["character"]
            r.category_sequence = st["category_sequence"]
            r.consumed = set(st["consumed"])
            r.mutation_sequence = st["mutation_sequence"]
            r.basin = basin
            r.pending = {}                                                                     # [RESTORE-PENDING]
            r.trace, r._trace_head = prefix, prefix_head
            r.checkpoint, r.checkpoint_sig = cp, sig
            r._append_trace({
                "event": "checkpoint",
                "sequence": cp.sequence,
                "birth_root": cp.birth_root,
                "constitution_root": cp.constitution_root,
                "gates_root": cp.gates_root,
                "character_root": cp.character_root,
                "timestamp": cp.timestamp,
            })
            digest = _sha256(raw)
            keep = self.data_dir / f"pre_restore_gen{g}_{digest[:12]}.json"
            r._append_trace({
                "event": "restored",
                "checkpoint_sequence": cp.sequence,
                "discarded_entries": len(trace) - n if isinstance(trace, list) else None,
                "discarded_file_sha256": digest,
                "kept_as": keep.name,
                "timestamp": r.clock(),
            })
            try:
                r.verify()
            except IntegrityError as why:
                raise IntegrityError(f"restore refused: the restored state does not verify ({why})")
            _durable_write(keep, raw)                                                        # [RESTORE-KEEP]
            r._generation = g
            r._save()
            self.load()
            return {"status": "restored", "checkpoint_sequence": cp.sequence,
                    "discarded_entries": len(trace) - n, "kept_as": keep.name}

    def _verify_policy(self) -> None:
''')

# R: the witness head, read under the owner lock
once('''    @_owner_locked
    def pending_for(self, organism_id: str) -> Optional[Dict[str, Any]]:
''', '''    @_owner_locked
    def head_for(self, organism_id: str) -> Optional[Dict[str, Any]]:
        """v0.8.7: the witness head for this organism, re-read from disk."""
        self._refresh()
        h = self.ledger.get(organism_id)
        return copy.deepcopy(h) if h is not None else None

    @_owner_locked
    def pending_for(self, organism_id: str) -> Optional[Dict[str, Any]]:
''')

# A: answers through a stale object are refused before any record changes
once('''        if answer not in OWNER_ANSWERS:
            raise ValueError(f"Answer must be one of {OWNER_ANSWERS}")
        if proposal_id not in seed.pending:
            raise ValueError("No pending reading with that id")
        category = _strict_loads(seed.pending[proposal_id].payload_to_sign)["category"]
        self.ledger.record_answer(seed.organism_id, proposal_id, category, answer, self.clock())
        return seed.record_owner_answer(proposal_id, answer, text)
''', '''        if answer not in OWNER_ANSWERS:
            raise ValueError(f"Answer must be one of {OWNER_ANSWERS}")
        with seed._organism_lock():
            try:
                seed._check_current()                   # [ANSWER-CURRENT] v0.8.7 (author A3; ChatGPT r7 F3)
            except StaleOrganism as why:
                raise StaleOrganism(f"{why}. The answer was not recorded anywhere: reload the organism "
                                    "and answer again")
            if proposal_id not in seed.pending:
                raise ValueError("No pending reading with that id")
            category = _strict_loads(seed.pending[proposal_id].payload_to_sign)["category"]
            self.ledger.record_answer(seed.organism_id, proposal_id, category, answer, self.clock())
            return seed.record_owner_answer(proposal_id, answer, text)
''')

# R: recovery can be told the organism id (restore works from an object that has not loaded)
once('''    def _recover(self, seed: HumbleSeed) -> Optional[str]:
''', '''    def _recover(self, seed: HumbleSeed, oid: Optional[str] = None) -> Optional[str]:
''')
once('''        oid = seed.organism_id
        p = self.witness.pending_for(oid)
''', '''        oid = oid or seed.organism_id
        p = self.witness.pending_for(oid)
''')

# Q: audit under the organism lock; R: OwnerTool.restore
once('''    @_owner_locked
    def audit(self, seed: HumbleSeed) -> bool:
        self._recover(seed)
        seed.verify()
        if seed.checkpoint is None:
            raise IntegrityError("No checkpoint to audit")
        self.witness.check_current(seed.checkpoint)
        return True
''', '''    @_owner_locked
    def audit(self, seed: HumbleSeed) -> bool:
        with seed._organism_lock():            # v0.8.7: no organism operation interleaves with an audit
            self._recover(seed)
            seed.verify()
            if seed.checkpoint is None:
                raise IntegrityError("No checkpoint to audit")
            self.witness.check_current(seed.checkpoint)
            return True

    @_owner_locked
    def restore(self, seed: HumbleSeed) -> Dict[str, Any]:
        """v0.8.7 (R20; Rusty's ruling 2026-10-19). Bring the organism back to its last
        attested state: the witness head. A pending commit is resolved first; then the
        organism rebuilds that state from the attested prefix of its saved trace,
        discarding everything after it. The witness does not move. Works from an
        object that has not loaded (an unattested state does not load)."""
        with seed._organism_lock():
            try:
                oid = _strict_loads(seed._state_path().read_text(encoding="utf-8"))["organism_id"]
            except (OSError, ValueError, KeyError, TypeError) as why:
                raise RollbackDetected(f"restore refused: the organism's saved state is unreadable ({type(why).__name__})")
            self._recover(seed, oid)                     # [RESTORE-RECOVERS]
            head = self.witness.head_for(oid)
            if head is None:
                raise RollbackDetected("restore refused: the witness holds no checkpoint for this organism")
            return seed._restore_attested(head["checkpoint_hash"], self._public_b64)
''')

once('''    print("Run the harness: python3 -I falsify_v0_8_6.py")''', '''    print("Run the harness: python3 -I falsify_v0_8_7.py")''')

out_path.write_text(src, encoding="utf-8")
print("written", out_path, len(src.splitlines()), "lines")
