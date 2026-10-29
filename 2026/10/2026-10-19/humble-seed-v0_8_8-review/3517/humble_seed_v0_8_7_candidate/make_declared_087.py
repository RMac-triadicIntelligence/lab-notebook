#!/usr/bin/env python3
"""Writes and freezes DECLARED_v0_8_7.json. Run once, before the harness exists."""
import copy
import datetime
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(sys.argv[1]).resolve()
PREV = json.loads((HERE / "v0_8_6_record" / "DECLARED_v0_8_6.json").read_text(encoding="utf-8"))
CAND = HERE / "humble_seed_v0_8_7_candidate.py"
src = CAND.read_text(encoding="utf-8")
LINES = src.splitlines()
if (HERE / "falsify_v0_8_7.py").exists() or (HERE / "DECLARED_v0_8_7.json").exists():
    raise SystemExit("harness or declaration already exists; refusing to freeze")


def check(name, edits):
    mutated = src
    for old, new in edits:
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{name}: anchor occurs {n} times")
        mutated = mutated.replace(old, new)
    compile(mutated, name, "exec")          # construction check only: the mutant must compile


def ln(prefix):
    """The one line that starts with `prefix` (indentation included). v0.8.7: a cited refusal is its raise line."""
    hits = [i + 1 for i, line in enumerate(LINES) if line.startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit(f"trace anchor {prefix!r} starts {len(hits)} lines")
    if prefix.lstrip().startswith("raise") and not LINES[hits[0] - 1].lstrip().startswith("raise"):
        raise SystemExit(f"trace anchor {prefix!r} is not a raise line")
    return f"L{hits[0]}"


NEW_TESTS = [
    "T70_two_threads_one_object_lose_no_dwelling", "T71_two_threads_attest_cannot_be_rewound",
    "T72_operation_is_atomic_across_threads", "T73_unconfirmed_save_leaves_object_unusable",
    "T74_stale_object_refused_before_memory_changes", "T75_answer_through_stale_object_records_nothing",
    "T76_write_landing_during_an_operation_is_not_overwritten", "T77_hatch_refuses_a_file_without_generation",
    "T78_restore_after_lifetime_lapse", "T79_restore_refuses_when_saved_checkpoint_is_not_witness_head",
    "T80_restore_refuses_a_rewritten_attested_prefix", "T81_restore_completes_a_pending_commit_first"]
TEST_NAMES = list(PREV["tests"]) + NEW_TESTS
T = lambda *ns: [t for t in TEST_NAMES if t.split("_")[0] in ns]  # noqa: E731

M = {}
REANCHOR = {
    "XG1_landed_save_not_recorded": [[
        "                    self._generation = new_gen                   # [SAVE-LANDED]\n", "                    pass\n"]],
    "XL6_answer_not_recorded_by_owner": [[
        "            self.ledger.record_answer(seed.organism_id, proposal_id, category, answer, self.clock())\n",
        "            pass\n"]],
    "XD2a_owner_answer_counted_as_authorizing": [[
        'NON_AUTHORIZING_EVENTS = {"dwelling", "authorization_rejected", "checkpoint", "owner_answer", "reading_held",\n',
        'NON_AUTHORIZING_EVENTS = {"dwelling", "authorization_rejected", "checkpoint", "reading_held",\n']],
}
REANCHOR_NOTE = {
    "XG1_landed_save_not_recorded": "v0.8.7: the landed branch moved inside the save lock; same mutation.",
    "XL6_answer_not_recorded_by_owner": "v0.8.7: answer now runs under the organism lock (one indent deeper); same mutation.",
    "XD2a_owner_answer_counted_as_authorizing": "v0.8.7: the set gained 'restored' and wraps onto two lines; same mutation.",
}
for name, spec in PREV["mutants"].items():
    spec = copy.deepcopy(spec)
    if name in REANCHOR:
        spec["edits"] = REANCHOR[name]
        spec["re_anchored"] = REANCHOR_NOTE[name]
    check(name, spec["edits"])
    spec["carried_from"] = spec.get("carried_from", "v0.8.6")
    M[name] = spec


def setk(name, tests, note=None):
    M[name]["exact_kill_set"] = sorted(tests)
    if note:
        M[name]["note"] = note


setk("XO1_save_skips_generation_check", T("T76"),
     "v0.8.7: re-predicted. The operation's currency check now refuses a stale object before its save, so T62-T64 "
     "and T67 no longer reach the save's check. Only a write that lands during an operation (T76: through the "
     "reader, same thread, reentrant lock) reaches it.")
setk("XO4_organism_lock_is_a_no_op", T("T69", "T70", "T71", "T72"),
     "v0.8.7: without any organism lock, thread B finishes while A is paused in T70-T72.")
setk("XI1_install_rolls_back_even_when_saved", T("T65", "T73"),
     "v0.8.7: in T73 the object is marked unusable and keeps the checkpoint that is on disk; this mutant rolls it back.")
setk("XR1_recovery_never_completes", T("T54", "T58", "T64", "T65", "T73", "T81"),
     "v0.8.7: T73's audit and T81's restore must complete an installed intent.")
setk("XR3_no_write_ahead_intent", T("T54", "T58", "T63", "T64", "T65", "T66", "T73", "T81"),
     "v0.8.7: in T73 no intent exists, so the audit meets an unwitnessed advance; in T81 the injected commit "
     "failure is never reached, because this mutant records instead of committing.")
setk("XL2_owner_clock_lifetime_check_removed", T("T42", "T53", "T78"),
     "v0.8.7: T78's first attest must be refused on the lifetime.")
M["XD4a_attest_without_replay"]["exact_kill_set"] = sorted(M["XD4a_attest_without_replay"]["exact_kill_set"] + T("T78"))
M["XD4a_attest_without_replay"]["note"] = "v0.8.7: T78 added (the lifetime check runs inside the replay's owner checks)."
setk("XL6_answer_not_recorded_by_owner", T("T41", "T47", "T49", "T60", "T61", "T75"),
     "v0.8.7: T75's final answer through a current object must reach the ledger.")

mut_specs = [
    ("XQ1_save_takes_no_lock_itself",
     [("        with self._organism_lock():            # [SAVE-LOCK] v0.8.7 (ChatGPT r7 F1): check, snapshot and write under one lock\n",
       "        with contextlib.nullcontext():\n")],
     "The save's own lock is dropped (its check, snapshot and write run unlocked inside _save).",
     "SURVIVES", None,
     "Equivalent under the public API: every save runs inside an operation, attest or restore, all of which hold the "
     "organism lock. Kept to show that the operation lock carries ChatGPT r7 F1's fix; the save's own lock remains "
     "for direct callers of _save."),
    ("XQ2_operation_lock_not_taken",
     [("        with self._organism_lock():                     # [OP-LOCK]\n", "        with contextlib.nullcontext():\n")],
     "Operations check currency but do not hold the organism lock (the save still locks its own write).",
     "KILLED", T("T72"),
     "ChatGPT's two schedules (T70, T71) pause A inside its save, under the save's own lock, so they pass; only a "
     "pause between A's changes to memory (T72) shows the operation is not atomic."),
    ("XQ3_operation_currency_check_removed",
     [("                self._check_current()                   # [OP-CURRENT]\n", "                pass\n")],
     "Operations take the lock but do not check currency first; a stale object changes memory before its save "
     "refuses it.", "KILLED", T("T74"),
     "The save's generation check still refuses every stale write (T62-T64), and hatch has its own check (T67)."),
    ("XQ4_answer_skips_currency_check",
     [("                seed._check_current()                   # [ANSWER-CURRENT] v0.8.7 (author A3; ChatGPT r7 F3)\n",
       "                pass\n")],
     "The owner's answer reaches its ledger before the stale organism refuses it (v0.8.6 behaviour).",
     "KILLED", T("T75"), None),
    ("XU1_unconfirmed_save_not_marked_unusable",
     [("                    self._generation = _UNUSABLE                 # [SAVE-INDETERMINATE]\n", "                    pass\n")],
     "A save whose outcome cannot be confirmed leaves the generation as it was; install then rolls memory back "
     "(v0.8.6 behaviour).", "KILLED", T("T73"), "ChatGPT round 7 F2"),
    ("XU2_unusable_object_not_named",
     [("        if self._generation == _UNUSABLE:                       # [UNUSABLE]\n", "        if False:\n")],
     "The currency check does not name an unusable object; it is refused as an ordinary stale one.",
     "KILLED", T("T73"), "T73 requires the refusal to say 'unusable'."),
    ("XV1_generation_not_required",
     [("        if isinstance(g, bool) or not isinstance(g, int) or g < 0:          # [GEN-REQUIRED] v0.8.7 (author A1)\n",
       "        if False:\n")],
     "A saved file without a valid generation reads as 'no file' (v0.8.6 behaviour).", "KILLED", T("T77"), "author A1"),
    ("XT1_restore_skips_witness_head_check",
     [("            if _sha256(HumbleSeed.checkpoint_payload(cp)) != expected_checkpoint_hash:      # [RESTORE-HEAD]\n",
       "            if False:\n")],
     "Restore rebuilds whatever checkpoint the saved file holds, even one behind the witness.",
     "KILLED", T("T79"), None),
    ("XT2_restore_skips_pending_recovery",
     [("            self._recover(seed, oid)                     # [RESTORE-RECOVERS]\n", "            pass\n")],
     "Restore does not resolve a pending commit first.", "KILLED", T("T81"), None),
    ("XT3_restore_keeps_pending_readings",
     [("            r.pending = {}                                                                     # [RESTORE-PENDING]\n",
       "            r.pending = {pid: PendingProposal(**p) for pid, p in data.get(\"pending\", {}).items()}\n")],
     "Restore keeps the pending readings of the discarded state.", "KILLED", T("T78"), None),
    ("XT4_restore_keeps_no_copy",
     [("            _durable_write(keep, raw)                                                        # [RESTORE-KEEP]\n",
       "            pass\n")],
     "Restore discards the file without keeping a copy.", "KILLED", T("T78"), None),
    ("XT5_restore_skips_prefix_check",
     [("            if n < 1 or len(prefix) != n or prefix_head != cp.trace_head:                   # [RESTORE-PREFIX]\n",
       "            if False:\n")],
     "Restore does not check the attested prefix against the checkpoint before replaying it.",
     "KILLED", T("T80"),
     "Without it the rewritten prefix is still refused, by the restored state's own verify, so nothing is written; "
     "T80 fails on the refusal's message, which must name the attested prefix."),
]
for name, edits, desc, expect, exact, note in mut_specs:
    check(name, edits)
    spec = {"expect": expect, "mutation": desc, "edits": [[o, n] for o, n in edits], "new_in": "v0.8.7"}
    if expect == "KILLED":
        spec["killer"] = exact[0]
        spec["exact_kill_set"] = sorted(exact)
    if note:
        spec["note"] = note
    M[name] = spec

TRACE = {
    "T73_unconfirmed_save_leaves_object_unusable": (
        f"attest -> install_checkpoint -> _save -> _durable_write: the injected directory fsync raises after os.replace "
        f"({ln('        os.fsync(dfd)')}) -> the re-read of the generation raises (injected) -> object marked unusable "
        f"({ln('                    self._generation = _UNUSABLE')}) -> the OSError propagates; install does not roll back "
        f"(the condition above {ln('                self.checkpoint, self.checkpoint_sig, n, self._trace_head = kept')} is false). "
        f"The next dwell -> _organism_op -> _check_current raises StaleOrganism 'unusable' "
        f"({ln('            raise StaleOrganism(\"organism object is unusable')})."),
    "T74_stale_object_refused_before_memory_changes": (
        f"dwell_or_propose -> _organism_op ({ln('                self._check_current()                   # [OP-CURRENT]')}) -> "
        f"_check_current raises StaleOrganism 'stale organism object' "
        f"({ln('            raise StaleOrganism(f\"stale organism object')}) before the method body runs."),
    "T75_answer_through_stale_object_records_nothing": (
        f"OwnerTool.answer -> organism lock -> _check_current raises "
        f"({ln('            raise StaleOrganism(f\"stale organism object')}) -> answer re-raises StaleOrganism with "
        f"'was not recorded' ({ln('                raise StaleOrganism(f\"{why}. The answer was not recorded')}) before "
        "the ledger or the organism records anything."),
    "T76_write_landing_during_an_operation_is_not_overwritten": (
        f"authorize_and_apply -> _consult_reader -> the reader has b dwell (reentrant lock; b is current; b's save lands) "
        f"-> the live object's _save -> generation check raises StaleOrganism "
        f"({ln('                raise StaleOrganism(f\"stale organism object')})."),
    "T77_hatch_refuses_a_file_without_generation": (
        f"hatch -> _check_current ({ln('        self._check_current()                   # [HATCH-CURRENT]')}) -> "
        f"_saved_generation raises StaleOrganism 'no valid generation' "
        f"({ln('            raise StaleOrganism(\"the saved state has no valid generation')}); the dwell on the "
        f"original object -> _organism_op -> _check_current -> the same raise."),
    "T78_restore_after_lifetime_lapse": (
        f"attest -> verify_consequence -> _check_owner_acts: signed through this owner tool, then the lifetime check "
        f"raises AttestationRefused 'past its lifetime' "
        f"({ln('            raise AttestationRefused(f\"trace index {i}: reading is past its lifetime')})."),
    "T79_restore_refuses_when_saved_checkpoint_is_not_witness_head": (
        f"OwnerTool.restore -> _recover (nothing pending) -> head_for -> _restore_attested: the file reads, its "
        f"generation is valid, it is keyed to this owner, then the head check raises RollbackDetected "
        f"({ln('                raise RollbackDetected(\"restore refused: the saved checkpoint is not the witness head')})."),
    "T80_restore_refuses_a_rewritten_attested_prefix": (
        f"OwnerTool.restore -> _restore_attested: the checkpoint is the witness head (only the trace was rewritten), the "
        f"rebuilt chain verifies but its head differs from the checkpoint's, so the prefix check raises IntegrityError "
        f"({ln('                raise IntegrityError(\"restore refused: the saved trace')})."),
}

C, O = "carried", "new"
tests = {}
for name, spec in PREV["tests"].items():
    spec = copy.deepcopy(spec)
    spec["status"] = C
    tests[name] = spec
PAUSE = ("Errors raised in either thread are re-raised unchanged (an ERROR, never a FAIL). If thread A finishes "
         "without reaching its pause point: FAIL. Thread B gets 0.25 s while A is paused; after A is released both "
         "must finish within 30 s.")
NEW = {
    "T70_two_threads_one_object_lose_no_dwelling": ("ChatGPT round 7 F1 (schedule 1)",
        "Genesis attested. Thread A dwells (curiosity, 'hmm ok') on the live object and is paused inside its save, "
        "where the state is serialized (K._canonical_json called with the state dict, in thread A). Thread B then "
        "dwells (formality) on the same object. B does not finish while A is paused. After A is released both finish "
        "without error. The saved trace holds both dwellings (curiosity and formality); the saved generation is two "
        "above its value before A started; a fresh load audits. " + PAUSE),
    "T71_two_threads_attest_cannot_be_rewound": ("ChatGPT round 7 F1 (schedule 2)",
        "Genesis attested. Thread A dwells (curiosity) and is paused at the same point as in T70. Thread B calls "
        "owner.attest on the same object. B does not finish while A is paused; after release both finish without "
        "error and attest returns True. The saved checkpoint sequence equals the witness sequence, 1; the saved trace "
        "holds A's dwelling; a fresh load audits. " + PAUSE),
    "T72_operation_is_atomic_across_threads": ("author (third schedule)",
        "Genesis attested. Thread A dwells (curiosity) and is paused at its second call of the object's clock (after "
        "its basin entry is added, before its trace entry). Thread B dwells (formality) on the same object. B does not "
        "finish while A is paused; after release both finish without error. The saved trace holds both dwellings; the "
        "saved generation is two above its starting value; a fresh load audits. " + PAUSE),
    "T73_unconfirmed_save_leaves_object_unusable": ("ChatGPT round 7 F2",
        "Genesis attested. During attest, after the organism's replace has landed (saved checkpoint 1), the directory "
        "fsync raises OSError (once) and the re-read of the saved generation then raises OSError (once). attest raises "
        "OSError. The object's checkpoint sequence equals the saved one, 1. The next dwell on the object raises "
        "StaleOrganism containing 'unusable'. A fresh load audits (completing the pending intent), and the witness is "
        "then at 1."),
    "T74_stale_object_refused_before_memory_changes": ("ChatGPT round 7 F3",
        "Genesis attested; `old` loaded. The live object dwells. On `old`, a dwell (formality, 'hmm ok') and a reading "
        "(verbosity, a proposal) each raise StaleOrganism containing 'stale organism object', and afterwards `old`'s "
        "trace length, basin length, pending reading ids and character are exactly as before."),
    "T75_answer_through_stale_object_records_nothing": ("author A3; ChatGPT round 7 F3",
        "Genesis attested. A verbosity reading is issued on the live object; `old` is loaded (it holds the reading); "
        "the live object dwells. owner.answer(old, reading, 'no') raises StaleOrganism containing 'stale organism "
        "object' and 'was not recorded'. The owner ledger holds no answer to the reading; the saved trace (read from "
        "the file) holds no owner_answer event; `old`'s trace length is unchanged. A freshly loaded object then "
        "answers 'no': the ledger holds ['no'] and the saved trace (read from the file) ends with that owner_answer."),
    "T76_write_landing_during_an_operation_is_not_overwritten": (None,
        "Genesis attested. A verbosity reading is issued on the live object and signed; `b` is loaded (current). The "
        "live object's reader is replaced by one that, on its first call, has `b` dwell (formality) and returns None. "
        "authorize_and_apply on the live object raises StaleOrganism containing 'stale organism object'. The saved "
        "file (read directly) holds b's formality dwelling, mutation_sequence 0 and verbosity 0.5; a fresh load audits."),
    "T77_hatch_refuses_a_file_without_generation": ("author A1 (sealed 2026-10-19T14:33:59Z)",
        "Genesis attested. The 'generation' field is removed from the saved file. A new object's hatch raises "
        "StaleOrganism containing 'no valid generation'; a dwell on the original object raises StaleOrganism "
        "containing 'no valid generation'; the file is byte-identical throughout."),
    "T78_restore_after_lifetime_lapse": ("R20 (Rusty's ruling, 2026-10-19 11:09 CT)",
        "Genesis attested. A verbosity crossing is applied (unattested) and a formality reading is left pending. The "
        "owner's clock is set to the crossing reading's first signing plus twice the attested lifetime. attest raises "
        "AttestationRefused containing 'past its lifetime'. owner.restore(live object), through restore_ok, returns "
        "status 'restored'. The object is at checkpoint 0 with verbosity 0.5, mutation_sequence 0 and no pending "
        "readings; its last trace event is 'restored', naming a kept file that exists beside the state and whose "
        "sha256 equals the event's discarded_file_sha256. The witness is still at 0. A fresh load audits. A new "
        "verbosity reading on the restored object is then applied and attested (witness 1), and a fresh load audits."),
    "T79_restore_refuses_when_saved_checkpoint_is_not_witness_head": (None,
        "Genesis attested; the saved file's bytes are kept. attest again (witness 1). The kept bytes are written back "
        "(saved checkpoint 0). owner.restore raises RollbackDetected containing 'not the witness head'; the file is "
        "byte-identical afterwards; the witness is at 1."),
    "T80_restore_refuses_a_rewritten_attested_prefix": (None,
        "Genesis attested; the live object dwells; attest (witness 1; the dwelling is inside the attested prefix). The "
        "dwelling's reason is rewritten in the saved file, the chain rebuilt and the seal recomputed (_reseal_attack, "
        "rechain=True). owner.restore raises IntegrityError containing 'attested prefix does not match the "
        "checkpoint'; the file is byte-identical afterwards."),
    "T81_restore_completes_a_pending_commit_first": (None,
        "Genesis attested. attest is interrupted (OSError injected at witness.commit) after the organism installed "
        "checkpoint 1: the witness is at 0 with an intent pending. owner.restore(live object), through restore_ok, "
        "returns status 'restored' with checkpoint_sequence 1; the witness is at 1 with no intent pending; a fresh "
        "load audits."),
}
for name, (credit, asserts) in NEW.items():
    spec = {"expect": "PASS", "status": O, "asserts": asserts}
    if credit:
        spec["credit"] = credit
    tests[name] = spec
for name, trace in TRACE.items():
    tests[name]["refusal_trace"] = trace
assert list(tests) == TEST_NAMES

rules = []
for r in PREV["rules"]:
    r = r.replace("differs from DECLARED_v0_8_5.sha256", "differs from DECLARED_v0_8_7.sha256")
    r = r.replace("re-checked as exact-once anchors on v0.8.5;",
                  "applied as exact-once anchors on v0.8.7 (build_mutant refuses otherwise, at run time);")
    rules.append(r)
assert not any("v0_8_5" in r or "anchors on v0.8.5" in r for r in rules), rules
rules += [
    "v0.8.7 (v0.8.6 DEVIATIONS): refusal traces cite the line of the raise statement, not the check's if line.",
    "restore_ok is an expected-success helper: restore's refusal types (RollbackDetected, IntegrityError, "
    "AttestationRefused) become FAIL.",
    "Threaded tests (T70-T72) re-raise any exception from a thread unchanged, so a crash in a thread is an ERROR, "
    "never a FAIL. Their only timing assumption is that B, if not blocked, finishes one dwell or one attest within "
    "0.25 s.",
    "candidate_only_checks run once, on the candidate only, after the suite, and are compared with their declared "
    "outcome (a mismatch counts). They are not run on mutants: S1 is a timed stress run, so a mutant's outcome there "
    "would not be deterministic. Their statuses enter the receipt.",
]

decl = {
    "artifact": "humble_seed_v0_8_7_candidate falsification harness",
    "date": "2026-10-19",
    "authorship": PREV["authorship"].replace("round 6 F1, F2)", "round 6 F1, F2; round 7 F1-F3)").replace(
        "v0.8.5 A1 and A2)", "v0.8.5 A1 and A2; v0.8.6 A1-A3)").replace(
        " Built at Rusty's 'Go', 2026-10-19 08:14 CT.", "")
    + " v0.8.7 built at Rusty's ruling, 2026-10-19 11:09 CT ('Build it into 8.7. Restore from last signed off state').",
    "candidate_sha256_at_freeze": hashlib.sha256(CAND.read_bytes()).hexdigest(),
    "frozen_before": ("the v0.8.7 harness was written. Before the freeze: a compile check; one smoke run (smoke087.py) of "
                      "the basic flow (hatch, propose, sign, apply, attest, reload, audit) and of restore's accepting path "
                      "(an unattested crossing restored to checkpoint 1, reload, audit), which pass through the operation "
                      "lock, the generation-checked save and restore on their accepting paths; an exact-once check of "
                      "every mutant anchor; and the static refusal traces. No harness test, thread schedule, stale-object "
                      "path, injected failure, restore refusal or mutant had been run on v0.8.7."),
    "status_key": {"carried": "Passed on v0.8.6; predicted on v0.8.7.",
                   "corrected": "Test corrected after a recorded deviation; predicted on v0.8.7.",
                   "new": "Not run on any version when this file was frozen."},
    "rules": rules,
    "controls_without_a_mutant": PREV["controls_without_a_mutant"] + [
        "hatch's early currency check ([HATCH-CURRENT]): _save's generation check refuses the same hatches, after the keys are generated.",
        "_save's own unusable check: every save runs inside an operation whose currency check refuses an unusable object first.",
        "load()'s and audit()'s organism lock: no test probes them (T69 probes the save and attest; T70-T72 the operation lock).",
        "restore's refusals of an unreadable file, a file without a valid generation, another owner's organism, a prefix "
        "that does not replay, and a restored state that does not verify: not exercised.",
        "OwnerWitness.head_for's re-read: the witness re-read is covered by XS3; no separate mutant.",
    ],
    "candidate_only_checks": {
        "S1_two_threads_stress": {
            "expect": "PASS",
            "asserts": ("Two threads share one organism object for 3 s: A dwells (formality, 'hmm ok') in a loop; B issues a "
                        "verbosity reading, has it signed, applies it and attests, in a loop. Neither thread raises. Every "
                        "dwelling A returned is in the saved trace; the saved checkpoint sequence equals the witness "
                        "sequence; a fresh load audits."),
        }
    },
    "retired": PREV["retired"],
    "tests": tests,
    "mutants": M,
}
out = HERE / "DECLARED_v0_8_7.json"
out.write_text(json.dumps(decl, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
sha = hashlib.sha256(out.read_bytes()).hexdigest()
(HERE / "DECLARED_v0_8_7.sha256").write_text(f"{sha}  DECLARED_v0_8_7.json\n")
(HERE / "CANDIDATE_v0_8_7_AT_FREEZE.sha256").write_text(
    f"{decl['candidate_sha256_at_freeze']}  humble_seed_v0_8_7_candidate.py\n")
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
(HERE / "DECLARED_v0_8_7.frozen_at").write_text(stamp + "\n")
print(len(tests), "tests;", len(M), "mutants; declared", sha, "frozen", stamp)
for k, v in TRACE.items():
    print(" ", k.split("_")[0], "->", v[:170])
