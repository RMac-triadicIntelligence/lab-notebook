#!/usr/bin/env python3
"""Writes and freezes DECLARED_v0_8_6.json. Run once, before the harness exists."""
import copy
import datetime
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(sys.argv[1]).resolve()
PREV = json.loads((HERE / "v0_8_5_record" / "DECLARED_v0_8_5.json").read_text(encoding="utf-8"))
CAND = HERE / "humble_seed_v0_8_6_candidate.py"
src = CAND.read_text(encoding="utf-8")
LINES = src.splitlines()
if (HERE / "falsify_v0_8_6.py").exists() or (HERE / "DECLARED_v0_8_6.json").exists():
    raise SystemExit("harness or declaration already exists; refusing to freeze")


def check(name, edits):
    for old, _ in edits:
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{name}: anchor occurs {n} times")


def ln(text):
    hits = [i + 1 for i, line in enumerate(LINES) if text in line]
    if len(hits) != 1:
        raise SystemExit(f"trace anchor {text!r} found on {len(hits)} lines")
    return f"L{hits[0]}"


TEST_NAMES = list(PREV["tests"]) + [
    "T62_stale_object_cannot_overwrite_newer_state", "T63_stale_write_during_attest_is_refused",
    "T64_interrupted_commit_then_stale_write_keeps_signoff", "T65_failure_after_replace_keeps_memory_with_disk",
    "T66_recovery_refuses_a_saved_state_that_does_not_verify", "T67_hatch_cannot_overwrite_an_existing_organism",
    "T68_attest_refuses_a_stale_object_before_signing", "T69_organism_lock_held_for_saves_and_attest"]
T = lambda *ns: [t for t in TEST_NAMES if t.split("_")[0] in ns]  # noqa: E731

M = {}
REANCHOR = {"XR4_install_keeps_memory_on_failed_save": [[
    "                self.checkpoint, self.checkpoint_sig, n, self._trace_head = kept   # [INSTALL-ROLLBACK]\n"
    "                del self.trace[n:]\n", "                pass\n"]]}
for name, spec in PREV["mutants"].items():
    spec = copy.deepcopy(spec)
    if name in REANCHOR:
        spec["edits"] = REANCHOR[name]
        spec["re_anchored"] = "v0.8.6: the rollback now sits under the landed-or-not condition; same mutation."
    check(name, spec["edits"])
    spec["carried_from"] = spec.get("carried_from", "v0.8.5")
    M[name] = spec


def setk(name, tests, note=None):
    M[name]["exact_kill_set"] = sorted(tests)
    if note:
        M[name]["note"] = note


setk("X10_unattested_tail_check_removed", T("T22"),
     "v0.8.6: corrected (v0.8.5 E2). In T57 the category-sequence check refuses first, so removing the tail check changes nothing there.")
setk("XR4_install_keeps_memory_on_failed_save", T("T57"), "v0.8.6: T57 now passes on the candidate (v0.8.5 E1 corrected).")
setk("XR1_recovery_never_completes", T("T54", "T58", "T64", "T65"),
     "v0.8.6: T64 and T65 must complete an installed intent from a saved state that verifies.")
setk("XR2_recovery_never_abandons", T("T55", "T57", "T66"),
     "v0.8.6: T57 passes again; T66 must abandon after the original file is restored.")
setk("XR3_no_write_ahead_intent", T("T54", "T58", "T63", "T64", "T65", "T66"),
     "v0.8.6: T63/T64 act at witness.commit, which this mutant never calls; T65 and T66 require a pending intent after the interruption, and this mutant writes none.")
setk("XR5_recovery_trusts_the_object", T("T58", "T66"),
     "v0.8.6: in T66 the live object still holds checkpoint 0, so recovery abandons and audit then refuses on category sequences.")
setk("XS1_owner_lock_not_taken", T("T56", "T69"),
     "v0.8.6: the organism lock uses the same flock class, so T69's probes also see it free.")

# New mutants (v0.8.6)
mut_specs = [
    ("XO1_save_skips_generation_check",
     [("            if saved != self._generation:                    # [SAVE-CAS]\n", "            if False:\n")],
     "A save writes even when the saved generation has moved on (v0.8.5 behaviour).",
     T("T62", "T63", "T64", "T67"), "ChatGPT round 6 F1"),
    ("XO2_attest_skips_currency_check",
     [("        seed._require_current()                 # [ATTEST-CURRENT]\n", "        pass\n")],
     "attest does not refuse a stale object before signing.", T("T68"), None),
    ("XO3_attest_without_organism_lock",
     [("        with seed._organism_lock():\n            return self._attest_under_organism_lock(seed)\n",
       "        return self._attest_under_organism_lock(seed)\n")],
     "attest does not hold the organism lock between its checks and the witness commit.", T("T69"), None),
    ("XO4_organism_lock_is_a_no_op",
     [('        return _OwnerLock(self.data_dir / "organism.lock")      # [ORGANISM-LOCK]\n',
       "        return contextlib.nullcontext()\n")],
     "The organism lock is never taken.", T("T69"), None),
    ("XI1_install_rolls_back_even_when_saved",
     [("            if self._generation == gen_before:     # v0.8.6 (ChatGPT r6 F2): roll back only if nothing landed\n",
       "            if True:\n")],
     "install rolls memory back on any save exception, landed or not (v0.8.5 behaviour).", T("T65"), "ChatGPT round 6 F2"),
    ("XG1_landed_save_not_recorded",
     [("                        self._generation = new_gen               # [SAVE-LANDED]\n", "                        pass\n")],
     "A save that fails after its replace landed is not recorded as landed.", T("T65"), "ChatGPT round 6 F2"),
    ("XC1_recovery_completes_without_verifying",
     [("            why = self._saved_state_refusal(seed)                 # [RECOVER-VERIFIES]\n", "            why = None\n")],
     "Recovery completes from a saved state that names the intent without checking that it verifies (v0.8.5 behaviour).",
     T("T66"), "author A1 (sealed 2026-10-19T12:34Z)"),
]
for name, edits, desc, exact, credit in mut_specs:
    check(name, edits)
    spec = {"expect": "KILLED", "mutation": desc, "edits": [[o, n] for o, n in edits],
            "killer": exact[0], "exact_kill_set": sorted(exact)}
    if credit:
        spec["credit"] = credit
    M[name] = spec

SEAL_LINE = ln('raise IntegrityError("State seal mismatch')
DWELL_STALE = (f"dwell_or_propose -> derive raises ValueError -> _dwell ({ln('self._dwell(category, str(why))')}) -> "
               f"_save -> generation check ({ln('[SAVE-CAS]')}) raises StaleOrganism 'stale organism object'")
TRACE = {
    "T57_failed_checkpoint_save_changes_nothing": (
        f"audit -> _recover abandons ({ln('self.witness.abandon(oid)')}) -> verify -> _verify_attestation "
        f"({ln('self._verify_attestation()')}) -> category-sequence check ({ln('if cp.gates_root != self._gates_root')}) "
        "raises first. Every earlier check in verify passes for a legitimately unattested state; the "
        f"unattested-tail check ({ln('Unattested authorizing event at trace')}) comes later."),
    "T62_stale_object_cannot_overwrite_newer_state": DWELL_STALE,
    "T63_stale_write_during_attest_is_refused": DWELL_STALE + " (inside the witness.commit hook; the lock is reentrant within the thread, so the generation check decides)",
    "T64_interrupted_commit_then_stale_write_keeps_signoff": (
        DWELL_STALE + f"; then audit -> _recover -> saved state verifies ({ln('[RECOVER-VERIFIES]')}) -> commit "
        f"({ln('self.witness.commit(pending_cp)')})"),
    "T65_failure_after_replace_keeps_memory_with_disk": (
        f"_save -> _durable_write -> injected directory-fsync OSError after os.replace -> landed generation recorded "
        f"({ln('[SAVE-LANDED]')}) -> install keeps memory (rollback {ln('[INSTALL-ROLLBACK]')} not taken) -> OSError "
        f"propagates; retry -> _recover verifies ({ln('[RECOVER-VERIFIES]')}) and commits -> _require_current passes "
        f"({ln('[ATTEST-CURRENT]')})"),
    "T66_recovery_refuses_a_saved_state_that_does_not_verify": (
        f"audit -> _recover -> saved state names the intent -> _saved_state_refusal -> load -> verify: earlier "
        f"checks pass (0.99 is in range), seal check ({SEAL_LINE}) raises -> "
        f"RollbackDetected 'claims it but does not verify' ({ln('claims it but does not verify')})"),
    "T67_hatch_cannot_overwrite_an_existing_organism": (
        f"hatch builds everything in memory and saves on the line after {ln('del private_key')} "
        f"-> generation check ({ln('[SAVE-CAS]')}): the saved generation is 0, this object's is None"),
    "T68_attest_refuses_a_stale_object_before_signing": (
        f"attest -> organism lock -> _recover (nothing pending) -> _require_current ({ln('[ATTEST-CURRENT]')}) "
        f"raises StaleOrganism ({ln('def _require_current')}) before checkpoint_request or any signature"),
}

C, O = "carried", "new"
tests = {}
for name, spec in PREV["tests"].items():
    spec = copy.deepcopy(spec)
    spec["status"] = C
    tests[name] = spec
tests["T57_failed_checkpoint_save_changes_nothing"].update({
    "status": "corrected",
    "asserts": tests["T57_failed_checkpoint_save_changes_nothing"]["asserts"].replace(
        "'Unattested authorizing event'", "'Category sequences do not match the attested checkpoint'")
    + " CORRECTED (v0.8.5 DEVIATIONS E1; Grok and ChatGPT r6)."})
assert "Category sequences do not match" in tests["T57_failed_checkpoint_save_changes_nothing"]["asserts"]
NEW = {
    "T62_stale_object_cannot_overwrite_newer_state": ("ChatGPT round 6 F1 (sequential)",
        "Genesis attested. A second object `old` is loaded at checkpoint 0. On the live object a verbosity crossing "
        "is applied and attested (saved checkpoint 1). `old` dwells (formality, 'hmm ok'): StaleOrganism containing "
        "'stale organism object'. The saved state is still at checkpoint 1; a fresh load has verbosity 0.25 and "
        "audits; a freshly loaded object then dwells normally."),
    "T63_stale_write_during_attest_is_refused": ("ChatGPT round 6 F1 (during attest)",
        "Genesis attested; `old` loaded. A verbosity crossing is applied on the live object. During attest, inside "
        "witness.commit, `old` dwells: StaleOrganism containing 'stale organism object' (recorded by the hook, which "
        "then lets the commit proceed). attest returns True; saved checkpoint 1 equals witness 1; a fresh load audits."),
    "T64_interrupted_commit_then_stale_write_keeps_signoff": ("ChatGPT round 6 F1 (interrupted commit + stale write)",
        "Genesis attested; `old` loaded. A verbosity crossing is applied; attest is interrupted (OSError at "
        "witness.commit) after the install. `old` dwells: StaleOrganism. A fresh load is at checkpoint 1 with verbosity "
        "0.25; a reopened owner tool's audit completes the intent: witness at 1, no pending intent."),
    "T65_failure_after_replace_keeps_memory_with_disk": ("ChatGPT round 6 F2",
        "A crossing is applied. During attest, the directory fsync after the organism's replace raises OSError "
        "(injected once). attest raises OSError; the object and the saved state are both at checkpoint 1; the witness "
        "is at 0 with a pending intent. Retrying attest on the same object returns True; a fresh load audits with "
        "the witness at 2."),
    "T66_recovery_refuses_a_saved_state_that_does_not_verify": ("author A1 (sealed 2026-10-19T12:34Z)",
        "A crossing is applied; attest is interrupted before the install (OSError), leaving a pending intent. The pending checkpoint and "
        "signature are copied into the saved file and its formality set to 0.99. audit on the live object raises "
        "RollbackDetected containing 'claims it but does not verify'; the witness stays at 0 with the intent pending. "
        "The original saved file is restored; attest then abandons the intent and succeeds (witness 1); a fresh load "
        "audits."),
    "T67_hatch_cannot_overwrite_an_existing_organism": (None,
        "An organism is born and attested. A new object on the same directory hatches: StaleOrganism containing "
        "'stale organism object'; the saved file is byte-identical afterwards; the original reloads and audits."),
    "T68_attest_refuses_a_stale_object_before_signing": (None,
        "Genesis attested; `old` loaded. The live object dwells (the saved generation advances; no crossing). "
        "attest(old) raises StaleOrganism containing 'stale organism object'; the witness is still at 0 with no "
        "pending intent. attest on the live object then succeeds."),
    "T69_organism_lock_held_for_saves_and_attest": (None,
        "During an ordinary save (a dwell; probed from _durable_write for the organism's state file) and at every "
        "witness.check_successor call during attest, another process cannot take organism.lock (LOCK_NB fails): every "
        "probe reports 'locked', and there is at least one of each. After attest it reports 'free'."),
}
for name, (credit, asserts) in NEW.items():
    spec = {"expect": "PASS", "status": O, "asserts": asserts}
    if credit:
        spec["credit"] = credit
    tests[name] = spec
for name, trace in TRACE.items():
    tests[name]["refusal_trace"] = trace
assert list(tests) == TEST_NAMES

rules = list(PREV["rules"]) + [
    "v0.8.6 (process fix after three check-order mispredictions: T26 in v0.8.3; T57 and X10 in v0.8.5): every "
    "declared refusal in a new or corrected test records the line traced to raise it ('refusal_trace'), traced "
    "statically through the candidate before the freeze."]

decl = {
    "artifact": "humble_seed_v0_8_6_candidate falsification harness",
    "date": "2026-10-19",
    "authorship": PREV["authorship"].replace("round 5 F1-F5)", "round 5 F1-F5; round 6 F1, F2)").replace(
        "T61's later-crossing case)", "T61's later-crossing case, v0.8.5 A1 and A2)")
    + " Built at Rusty's 'Go', 2026-10-19 08:14 CT.",
    "candidate_sha256_at_freeze": hashlib.sha256(CAND.read_bytes()).hexdigest(),
    "frozen_before": ("the v0.8.6 harness was written. Before the freeze: a compile check; one smoke run of the "
                      "basic flow (hatch, propose, sign, apply, attest, reload, audit), which passes through the "
                      "generation-checked save and the organism lock on their accepting paths; an exact-once check of "
                      "every mutant anchor; and the static refusal traces. No harness test, stale-object path, "
                      "injected failure, recovery path or mutant had been run on v0.8.6."),
    "status_key": PREV["status_key"],
    "rules": rules,
    "controls_without_a_mutant": PREV["controls_without_a_mutant"] + [
        "The owner's refusal wording (M, author A2): display only; tests match \"owner's position\".",
        "load()'s refusal of a non-integer saved generation: not exercised.",
        "_saved_generation's refusal of an unreadable saved state on save: not exercised."],
    "retired": PREV["retired"],
    "tests": tests,
    "mutants": M,
}
out = HERE / "DECLARED_v0_8_6.json"
out.write_text(json.dumps(decl, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
sha = hashlib.sha256(out.read_bytes()).hexdigest()
(HERE / "DECLARED_v0_8_6.sha256").write_text(f"{sha}  DECLARED_v0_8_6.json\n")
(HERE / "CANDIDATE_v0_8_6_AT_FREEZE.sha256").write_text(
    f"{decl['candidate_sha256_at_freeze']}  humble_seed_v0_8_6_candidate.py\n")
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
(HERE / "DECLARED_v0_8_6.frozen_at").write_text(stamp + "\n")
print(len(tests), "tests;", len(M), "mutants; declared", sha, "frozen", stamp)
for k, v in TRACE.items():
    print(" ", k.split("_")[0], "->", v[:150])
