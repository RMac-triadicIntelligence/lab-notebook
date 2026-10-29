#!/usr/bin/env python3
"""Derives humble_seed_v0_8_6_candidate.py from v0.8.5 by exact-once replacements."""
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
end_marker = 'Run the falsification harness:  python3 -I falsify_v0_8_5.py\n"""'
end = src.index(end_marker) + len(end_marker)
DOC = '''"""
Humble Seed v0.8.6 CANDIDATE — One Organism Persistence Protocol
================================================================

STATUS: candidate, not canonical. Parent: humble_seed_v0_8_5_candidate.py
(sha256 e505d432...). Round 6 (ChatGPT, blind) showed that the organism's saved
file had many writers and no protocol, and that recovery trusted it. A stale
organism object's ordinary save could erase newer, signed-off state. Everything
not listed is carried from v0.8.5 unchanged: the three rulings, the serialized
owner authority, saved-state recovery (V), apply = replay (A) and the
owner-verifiable category window (W).

CHANGES

  O  ONE ORGANISM PERSISTENCE PROTOCOL.
     - The saved state carries a generation number.
     - Every save runs under the organism's own lock (organism.lock, POSIX flock,
       reentrant within a thread). It writes only if the saved generation is still
       the one this object last loaded or wrote. Otherwise it raises
       StaleOrganism, and the object must reload.
     - A new hatch cannot overwrite an existing organism.
     - attest holds the organism lock from recovery to the witness commit. It
       refuses a stale object before signing anything.

  I  INDETERMINATE SAVES ARE RESOLVED, NOT ASSUMED. A save can fail after its
     replace has already landed: the directory fsync comes last. On a failure,
     the saved generation is re-read. install_checkpoint rolls memory back only
     if the new state did not land, so memory always matches disk.

  C  RECOVERY COMPLETES ONLY FROM A SAVED STATE THAT VERIFIES. A pending intent
     counts as installed only if the saved state names it and also loads and
     verifies on its own. A saved state that claims the intent but does not
     verify is neither completed nor abandoned. Abandoning still requires the
     saved checkpoint to be the witness head.

  M  The owner's refusal names its own window ("its latest answer in verbosity
     since it signed the previous verbosity crossing is 'no'"), not the
     organism's.

  H  HOUSEKEEPING (declaration). T57 expects the check that actually fires
     first; X10's set is {T22}. Every declared refusal now records the line
     traced to raise it.

FINDINGS CLOSED
  ChatGPT r6 F1  A stale object's ordinary save erased newer saved state. All
                 three schedules: sequential; during attest; interrupted commit
                 followed by a stale write -> O.
  ChatGPT r6 F2  A failure after the replace left memory behind disk -> I.
  Author  A1     Recovery completed from a saved file that does not load -> C.
                 Sealed 2026-10-19T12:34Z, before round 6.
  Author  A2     The owner's refusal text contradicted itself -> M.

LIMITS. R1-R29 as in v0.8.5, except:
  R30 (revised) Recovery completes an intent only from a saved state that
      verifies, and abandons one only if the saved checkpoint is the witness
      head. An edit made outside the protocol (writing the file directly) is not
      prevented. A rewind to the exact pre-install file looks the same as an
      install that never happened, and is abandoned.
  R31 (revised) Only install_checkpoint is transactional in memory. If another
      operation's save fails before landing, the object is ahead of its disk and
      its next save writes that state. Because of the generation check, no other
      object can write over it.
  R32 The organism lock is POSIX flock, like the owner lock (R26). Writers that
      bypass HumbleSeed._save are not serialized.
  R33 A stale object must reload, and its unsaved changes are lost. An answer
      given through a stale object reaches the owner's ledger, which is
      authoritative, but not the organism.
  R34 Every save re-reads the saved state to check its generation, a cost that
      grows with the trace (see also the apply-side replay, author A3).
  W's justification, corrected: answers given before the owner signed the
  previous crossing were already checked when that crossing was attested, so
  the window holds without assuming when the organism issued the reading.

Run the falsification harness:  python3 -I falsify_v0_8_6.py
"""'''
src = src[:start] + DOC + src[end:]

once('SCHEMA_VERSION = "0.8.5-candidate"\n', 'SCHEMA_VERSION = "0.8.6-candidate"\n')
once("import base64\nimport copy\n", "import base64\nimport contextlib\nimport copy\n")

once('''class AttestationRefused(RuntimeError):''', '''class StaleOrganism(RuntimeError):
    """v0.8.6: this organism object is not the saved state's latest reader or writer."""


class AttestationRefused(RuntimeError):''')

once('''        self._trace_head: str = "0" * 64
''', '''        self._trace_head: str = "0" * 64
        self._generation: Optional[int] = None   # v0.8.6: the saved generation this object last saw
''')

# I: install keeps memory in line with what actually landed
once('''        try:
            self._save()
        except BaseException:
            self.checkpoint, self.checkpoint_sig, n, self._trace_head = kept   # [INSTALL-ROLLBACK]
            del self.trace[n:]
            raise
        return True
''', '''        gen_before = self._generation
        try:
            self._save()
        except BaseException:
            if self._generation == gen_before:     # v0.8.6 (ChatGPT r6 F2): roll back only if nothing landed
                self.checkpoint, self.checkpoint_sig, n, self._trace_head = kept   # [INSTALL-ROLLBACK]
                del self.trace[n:]
            raise
        return True
''')

# O: generation-checked saves under the organism lock
once('''    def _save(self) -> None:
        if self.organism_id is None or self.birth is None:
            return
        state = {
            "schema_version": SCHEMA_VERSION,
''', '''    def _organism_lock(self):
        """v0.8.6: the organism's own lock file (POSIX flock, reentrant within a thread)."""
        return _OwnerLock(self.data_dir / "organism.lock")      # [ORGANISM-LOCK]

    def _saved_generation(self) -> Optional[int]:
        path = self._state_path()
        if not path.exists():
            return None
        try:
            return _strict_loads(path.read_text(encoding="utf-8")).get("generation")
        except (ValueError, AttributeError) as why:
            raise StaleOrganism(f"the saved state is unreadable ({type(why).__name__}); refusing to write over it")

    def _require_current(self) -> None:
        """v0.8.6 (ChatGPT r6 F1): refuse to act on a stale object."""
        with self._organism_lock():
            saved = self._saved_generation()
            if saved != self._generation:
                raise StaleOrganism(f"stale organism object: the saved state is at generation {saved}, "
                                    f"this object last saw {self._generation}; reload it")

    def _save(self) -> None:
        if self.organism_id is None or self.birth is None:
            return
        new_gen = 0 if self._generation is None else self._generation + 1
        state = {
            "schema_version": SCHEMA_VERSION,
            "generation": new_gen,
''')
once('''        text = _canonical_json(state)          # raises before anything is written
        _durable_write(self._state_path(), text)
''', '''        text = _canonical_json(state)          # raises before anything is written
        with self._organism_lock():            # v0.8.6 (ChatGPT r6 F1): one writer, and only a current one
            saved = self._saved_generation()
            if saved != self._generation:                    # [SAVE-CAS]
                raise StaleOrganism(f"stale organism object: the saved state is at generation {saved}, "
                                    f"this object last saw {self._generation}; reload it")
            try:
                _durable_write(self._state_path(), text)
            except BaseException:
                # v0.8.6 (ChatGPT r6 F2): the replace may already have landed; record what did.
                try:
                    if self._saved_generation() == new_gen:
                        self._generation = new_gen               # [SAVE-LANDED]
                except StaleOrganism:
                    pass
                raise
            self._generation = new_gen
''')
once('''        self.checkpoint_sig = data.get("checkpoint_sig")

        self.verify(expected_seal=data.get("state_seal"))''', '''        self.checkpoint_sig = data.get("checkpoint_sig")
        g = data.get("generation")
        if isinstance(g, bool) or not isinstance(g, int) or g < 0:
            raise IntegrityError("Saved generation is not a non-negative integer")
        self._generation = g

        self.verify(expected_seal=data.get("state_seal"))''')

# M: the owner's refusal names its own window
once('''        # v0.8.5 (ChatGPT round 5, F1): the owner's category window starts where the owner
        # can verify it: its own signature of the previous crossing in this category, or
        # the start of its record for the first. That signature precedes this reading's
        # issuance, so every answer given since the reading was taken is inside the window.
''', '''        # v0.8.5 (ChatGPT round 5, F1): the owner's category window starts where the owner
        # can verify it: its own signature of the previous crossing in this category, or
        # the start of its record for the first. Answers before that signature were checked
        # when the previous crossing was attested; answers after it are checked here.
''')
once('''        held = answer_position(self.ledger.answers_to(oid, pid),
                               self.ledger.answers_in_category_after(oid, cat, window_start))
        if held is not None:
            raise AttestationRefused(f"trace index {i}: owner's position: {held} "
                                     f"(owner's window: its answers in {cat} {window})")
''', '''        to_reading = self.ledger.answers_to(oid, pid)
        held = answer_position(to_reading, self.ledger.answers_in_category_after(oid, cat, window_start))
        if held is not None:
            which = ("its latest answer to this reading is 'no'" if to_reading and to_reading[-1] == "no"
                     else f"its latest answer in {cat} {window} is 'no'")    # v0.8.6 (author A2)
            raise AttestationRefused(f"trace index {i}: owner's position: {which}")
''')

# C: complete only from a saved state that verifies
once('''        saved_cp, saved_sig = self._saved_checkpoint(seed)       # [RECOVER-FROM-DISK]
        installed = (saved_cp is not None and saved_sig == p["signature_b64"]
                     and HumbleSeed.checkpoint_payload(saved_cp)
                     == HumbleSeed.checkpoint_payload(pending_cp))
        if installed:
''', '''        saved_cp, saved_sig = self._saved_checkpoint(seed)       # [RECOVER-FROM-DISK]
        installed = (saved_cp is not None and saved_sig == p["signature_b64"]
                     and HumbleSeed.checkpoint_payload(saved_cp)
                     == HumbleSeed.checkpoint_payload(pending_cp))
        if installed:                       # v0.8.6 (author A1): the saved state must also verify
            why = self._saved_state_refusal(seed)                 # [RECOVER-VERIFIES]
            if why is not None:
                raise RollbackDetected("A pending checkpoint commit cannot be completed: the saved state "
                                       f"claims it but does not verify ({why})")
        if installed:
''')
once('''    def _recover(self, seed: HumbleSeed) -> Optional[str]:
''', '''    def _saved_state_refusal(self, seed: HumbleSeed) -> Optional[str]:
        """v0.8.6 (author A1): None if the organism's saved state loads and verifies on its own."""
        probe = HumbleSeed(seed.data_dir)
        try:
            probe.load()
        except (IntegrityError, ValueError, KeyError, TypeError, FileNotFoundError) as why:
            return f"{type(why).__name__}: {why}"
        return None

    def _recover(self, seed: HumbleSeed) -> Optional[str]:
''')

# O: attest holds the organism lock from recovery to commit, and refuses a stale object first
once('''    @_owner_locked
    def attest(self, seed: HumbleSeed) -> bool:
        self._recover(seed)
        cp = seed.checkpoint_request()          # built now, at signing time
''', '''    @_owner_locked
    def attest(self, seed: HumbleSeed) -> bool:
        # v0.8.6 (ChatGPT r6 F1): the organism lock is held from recovery to the witness
        # commit, so no organism write can land between the checks and the commit.
        with seed._organism_lock():
            return self._attest_under_organism_lock(seed)

    def _attest_under_organism_lock(self, seed: HumbleSeed) -> bool:
        self._recover(seed)
        seed._require_current()                 # [ATTEST-CURRENT]
        cp = seed.checkpoint_request()          # built now, at signing time
''')

once('''    print("Run the harness: python3 -I falsify_v0_8_5.py")''', '''    print("Run the harness: python3 -I falsify_v0_8_6.py")''')

out_path.write_text(src, encoding="utf-8")
print("written", out_path, len(src.splitlines()), "lines")
