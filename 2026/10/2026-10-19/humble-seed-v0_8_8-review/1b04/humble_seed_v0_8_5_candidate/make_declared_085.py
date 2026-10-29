#!/usr/bin/env python3
"""Writes and freezes DECLARED_v0_8_5.json. Run once, before the harness exists."""
import copy
import datetime
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(sys.argv[1]).resolve()
PREV = json.loads((HERE / "v0_8_4_record" / "DECLARED_v0_8_4.json").read_text(encoding="utf-8"))
CAND = HERE / "humble_seed_v0_8_5_candidate.py"
src = CAND.read_text(encoding="utf-8")
if (HERE / "falsify_v0_8_5.py").exists() or (HERE / "DECLARED_v0_8_5.json").exists():
    raise SystemExit("harness or declaration already exists; refusing to freeze")


def check(name, edits):
    for old, _ in edits:
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"{name}: anchor occurs {n} times")


TEST_NAMES = list(PREV["tests"]) + [
    "T57_failed_checkpoint_save_changes_nothing", "T58_stale_object_cannot_abandon_an_installed_intent",
    "T59_apply_refuses_what_replay_would_refuse", "T60_owner_no_before_signing_holds_first_crossing",
    "T61_owner_no_before_signing_holds_later_crossing"]
T = lambda *ns: [t for t in TEST_NAMES if t.split("_")[0] in ns]  # noqa: E731

M = {}
RENAME = {"XP1_authorized_at_finite_check_removed": "XP1_finite_check_removed_window_still_refuses"}
REANCHOR = {"XM1_invalid_authorized_at": [[
    "            authorized_at=now, signature_b64=signature_b64,\n",
    '            authorized_at="not a timestamp", signature_b64=signature_b64,\n']]}
for name, spec in PREV["mutants"].items():
    spec = copy.deepcopy(spec)
    if name in REANCHOR:
        spec["edits"] = REANCHOR[name]
        spec["re_anchored"] = "v0.8.5: apply now reads the clock once (`now`); same mutation."
    check(name, spec["edits"])
    spec["carried_from"] = spec.get("carried_from", "v0.8.4")
    if name in RENAME:
        spec["renamed_from"] = name
        name = RENAME[name]
    M[name] = spec


def setk(name, tests, note=None):
    M[name]["exact_kill_set"] = sorted(tests)
    if note:
        M[name]["note"] = note


# Carried mutants whose exact sets change in v0.8.5 (reasons in the notes)
setk("X4_K1_prior_value_check_removed", T("T21"),
     "v0.8.5: T23 no longer kills it. With the explicit check removed, the apply-side replay check (A) "
     "still refuses the crossing, so T23 never reaches attestation and the tamper is caught at load as "
     "before. T21 still kills it on the refusal's reason. X4b removes both.")
setk("X10_unattested_tail_check_removed", T("T22", "T57"),
     "v0.8.5: T57 expects audit to refuse a state with an unattested crossing.")
setk("XD2a_owner_answer_counted_as_authorizing",
     T("T30", "T34", "T35", "T41", "T45", "T47", "T48", "T49", "T50", "T60", "T61"),
     "v0.8.5: T60, T61 record owner answers on the organism, so replay meets an 'authorizing' answer.")
setk("XD2c_answer_is_a_permanent_event", T("T45", "T47", "T49", "T60", "T61"),
     "v0.8.5: in T60/T61 the organism then holds X on the earlier 'no' to Y, so X never applies.")
setk("XD2f_category_clause_removed", T("T45", "T60", "T61"),
     "v0.8.5: T60/T61 depend on the category clause on the owner side.")
setk("XD4a_attest_without_replay",
     T("T26", "T39", "T41", "T42", "T43", "T44", "T46", "T47", "T48", "T49", "T52", "T53", "T60", "T61"),
     "v0.8.5: T56 no longer probes from the replay (v0.8.4 E1), so it is not killed; T60, T61 added.")
setk("XL1_owner_position_check_removed", T("T41", "T47", "T49", "T60", "T61"))
setk("XL6_answer_not_recorded_by_owner", T("T41", "T47", "T49", "T60", "T61"))
setk("XS2_ledger_not_reread", T("T49", "T50", "T53"),
     "v0.8.5: unchanged set; T53 now signs off from a fresh session, so it detects the stale overwrite (v0.8.4 E2).")
setk("XR1_recovery_never_completes", T("T54", "T58"),
     "v0.8.5: in T58 recovery must complete from the saved state; with completion removed it refuses.")
setk("XR2_recovery_never_abandons", T("T55", "T57"),
     "v0.8.5: in T57 recovery must abandon the intent the failed save never installed.")
setk("XR3_no_write_ahead_intent", T("T54", "T58"),
     "v0.8.5: T58 injects its interruption at witness.commit, which this mutant never calls.")
setk("XP3_annotation_type_unchecked", T("T52", "T59"),
     "v0.8.5: the replay check is shared with apply, so apply then accepts a bad annotation too.")
setk("XP4_authorized_at_window_unchecked", T("T52", "T59"),
     "v0.8.5: shared with apply, so apply then accepts a clock behind issuance.")
M["XP1_finite_check_removed_window_still_refuses"].update({
    "mutation": ("The named finite-number refusal is removed. A non-numeric authorized_at is still refused: the "
                 "window check's float() raises and the replay reports a malformed record. The kill is on the "
                 "refusal's name, not on acceptance (ChatGPT r5 F5). XP1b removes the protection itself."),
    "note": "Renamed in v0.8.5 from XP1_authorized_at_finite_check_removed; edits unchanged."})


def mut(name, edits, expect, desc, killer=None, exact=None, credit=None, note=None):
    check(name, edits)
    spec = {"expect": expect, "mutation": desc, "edits": [[o, n] for o, n in edits]}
    if killer:
        spec["killer"] = killer
    if exact is not None:
        spec["exact_kill_set"] = sorted(exact)
    if credit:
        spec["credit"] = credit
    if note:
        spec["note"] = note
    M[name] = spec


XA1_EDIT = ("        if apply_refusal is not None:                        # [APPLY=REPLAY]\n", "        if False:\n")
X4_EDIT = tuple(PREV["mutants"]["X4_K1_prior_value_check_removed"]["edits"][0])
XP1_EDIT = tuple(PREV["mutants"]["XP1_authorized_at_finite_check_removed"]["edits"][0])
XP4_EDIT = tuple(PREV["mutants"]["XP4_authorized_at_window_unchecked"]["edits"][0])

# V — recovery reads the organism's saved state
mut("XR4_install_keeps_memory_on_failed_save", [(
    "            self.checkpoint, self.checkpoint_sig, n, self._trace_head = kept   # [INSTALL-ROLLBACK]\n"
    "            del self.trace[n:]\n", "            pass\n")], "KILLED",
    "install_checkpoint leaves the new checkpoint in memory when its save fails (v0.8.4 behaviour).",
    killer=T("T57")[0], exact=T("T57"), credit="ChatGPT round 5 F2")
mut("XR5_recovery_trusts_the_object", [(
    "        saved_cp, saved_sig = self._saved_checkpoint(seed)       # [RECOVER-FROM-DISK]\n",
    "        saved_cp, saved_sig = seed.checkpoint, seed.checkpoint_sig\n")], "KILLED",
    "Recovery decides from the object handed in, not the saved state (v0.8.4 behaviour).",
    killer=T("T58")[0], exact=T("T58"), credit="ChatGPT round 5 F3",
    note="T57 does not kill it: with the install rollback in place the object and its disk agree there.")

# A — apply = replay
mut("XA1_apply_skips_replay_check", [XA1_EDIT], "KILLED",
    "Apply no longer runs the replay's check on its new crossing (v0.8.4 behaviour).",
    killer=T("T59")[0], exact=T("T59"), credit="ChatGPT round 5 F4")
mut("XP1b_finite_and_window_checks_removed", [XP1_EDIT, XP4_EDIT], "KILLED",
    "Both the finite-number and the window checks on authorized_at are removed: a non-numeric or "
    "out-of-window authorized_at is accepted.", killer=T("T52")[0], exact=T("T52", "T59"),
    credit="ChatGPT round 5 F5 (the protection XP1 was named for)")
mut("X4b_prior_value_unchecked_at_apply", [X4_EDIT, XA1_EDIT], "KILLED",
    "Both the explicit prior-value check and the apply-side replay check are removed.",
    killer=T("T21")[0], exact=T("T21", "T23", "T59"),
    note="Shows the two layers jointly: X4 alone is now caught by the replay check (see X4's note).")

# W — owner-verifiable category window
mut("XW1a_first_crossing_window_from_own_signing", [(
    "            window_start = 0\n", '            window_start = entry["seq"]\n')], "KILLED",
    "For a category's first crossing, the owner counts category answers only after its own signature "
    "(v0.8.4 behaviour).", killer=T("T60")[0], exact=T("T60"), credit="ChatGPT round 5 F1")
mut("XW1b_later_crossing_window_from_own_signing", [(
    '            window_start = prev_signed["seq"]                # [OWNER-WINDOW]\n',
    '            window_start = entry["seq"]\n')], "KILLED",
    "For later crossings, the owner counts category answers only after its own signature (v0.8.4 behaviour).",
    killer=T("T61")[0], exact=T("T61"), credit="ChatGPT round 5 F1 (extended to later crossings by the author)")

C, O = "carried", "new"
tests = {}
for name, spec in PREV["tests"].items():
    spec = copy.deepcopy(spec)
    spec["status"] = C
    tests[name] = spec
tests["T53_lifetime_runs_from_first_signing"].update({
    "status": "corrected",
    "asserts": ("CORRECTED (v0.8.4 DEVIATIONS E2; ChatGPT r5). Hatched with a 10 s lifetime. Session B opens. "
                "A signs at owner time t0; B re-signs the same payload at t0+11. The organism applies. A freshly "
                "opened session C, at owner time t0+11, attests: AttestationRefused containing \"past its lifetime "
                "by the owner's clock\".")})
tests["T56_owner_lock_excludes_other_processes"].update({
    "status": "corrected",
    "asserts": ("CORRECTED (v0.8.4 DEVIATIONS E1; ChatGPT r5). During attest, probed once from inside the "
                "organism's install_checkpoint (called while attest holds the lock, outside the replay), another "
                "process cannot take the owner lock: the probe reports 'locked'. After attest it reports 'free'.")})
tests.update({
    "T57_failed_checkpoint_save_changes_nothing": {"expect": "PASS", "status": O, "credit": "ChatGPT round 5 F2",
        "asserts": ("A crossing is applied. The organism's save is made to fail (OSError) during attest's install. "
                    "Afterwards the organism object and its saved state both hold checkpoint 0. audit on the same "
                    "object raises IntegrityError containing 'Unattested authorizing event'; the witness stays at 0 "
                    "with no pending intent. Retrying attest succeeds; the state reloads and a reopened owner tool "
                    "audits it; the witness is at 1.")},
    "T58_stale_object_cannot_abandon_an_installed_intent": {"expect": "PASS", "status": O,
        "credit": "ChatGPT round 5 F3",
        "asserts": ("An organism object is loaded at checkpoint 0 and kept (stale). On the live object a crossing is "
                    "applied; attest is interrupted (OSError at witness.commit) after the organism saved checkpoint 1 "
                    "and before the witness advanced. audit on the stale object raises RollbackDetected containing "
                    "'Rollback: organism presents sequence 0, witness holds 1'. Recovery has completed the intent "
                    "from the saved state: no pending intent, witness at 1. The saved state reloads, a reopened owner "
                    "tool audits it, and the next crossing (formality) applies and attests.")},
    "T59_apply_refuses_what_replay_would_refuse": {"expect": "PASS", "status": O, "credit": "ChatGPT round 5 F4",
        "asserts": ("A verbosity reading is signed. authorize_and_apply with (i) a 2001-character annotation and "
                    "(ii) a dict annotation each returns None with an authorization_rejected event whose reason "
                    "contains 'replay would refuse' and 'unverified_annotation is not a short string'. (iii) With the "
                    "organism's clock 100 s before the reading's issuance, the reason contains \"authorized_at outside "
                    "the reading's own window\". After each, character, sequences, consumed set and mutation count are "
                    "unchanged and the reading is still pending. With a 2000-character annotation at the real time it "
                    "applies, attests, reloads and audits.")},
    "T60_owner_no_before_signing_holds_first_crossing": {"expect": "PASS", "status": O,
        "credit": "ChatGPT round 5 F1 (pre_sign_category_no_bypass)",
        "asserts": ("Readings X and Y (verbosity) are issued. The owner answers Y 'no' through its tool; a 'yes' to Y "
                    "is forged on the organism only. The owner signs X; the organism applies X. attest raises "
                    "AttestationRefused containing \"owner's position\"; a fresh witness stays at 0. The owner then "
                    "answers Y 'yes'; attest succeeds; verbosity 0.25.")},
    "T61_owner_no_before_signing_holds_later_crossing": {"expect": "PASS", "status": O,
        "credit": "ChatGPT round 5 F1, extended to a category's later crossings (author)",
        "asserts": ("A first verbosity crossing X1 is applied and attested. Readings X2 and Y2 (verbosity) are issued. "
                    "The owner answers Y2 'no'; a 'yes' to Y2 is forged on the organism only. The owner signs X2; the "
                    "organism applies it. attest raises AttestationRefused containing \"owner's position\"; a fresh "
                    "witness stays at 1.")},
})
assert list(tests) == TEST_NAMES

rules = [r.replace("DECLARED_v0_8_2.sha256", "DECLARED_v0_8_5.sha256") for r in PREV["rules"]]
rules = [r.replace("Mutants carried from v0.8.2 use the same edits, re-checked as exact-once anchors on v0.8.3.",
                   "Carried mutants use the same edits, re-checked as exact-once anchors on v0.8.5; re-anchored "
                   "or renamed mutants say so.") for r in rules]

decl = {
    "artifact": "humble_seed_v0_8_5_candidate falsification harness",
    "date": "2026-10-19",
    "authorship": ("Claude (Opus 5.5 session), at Rusty McMurray's direction ('Go', 2026-10-19). Credits by finder: "
                   "Grok (round 1: T21, T22), ChatGPT (round 2 #1-#5; round 3 F1a, F1b, F2; round 4 F1-F4, A1 and "
                   "A2 by priority (see the credit correction in REVIEWS.md), mutants XM1-XM3; round 5 F1-F5), "
                   "author (lifetime, 1e999, R19, corrected answer, T26 correction, T61's later-crossing case)."),
    "candidate_sha256_at_freeze": hashlib.sha256(CAND.read_bytes()).hexdigest(),
    "frozen_before": ("the v0.8.5 harness was written. Before the freeze: a compile check; one smoke run of the "
                      "basic flow (hatch, propose, sign, apply, attest, reload, audit), which passes through the new "
                      "apply-side replay check on its accepting path; and an exact-once check of every mutant anchor. "
                      "No harness test, rejection path, recovery path, owner-window path or mutant had been run on "
                      "v0.8.5."),
    "status_key": {"carried": "Passed on v0.8.4; predicted on v0.8.5.",
                   "corrected": "Test corrected after a recorded deviation; predicted on v0.8.5.",
                   "new": "Not run on any version when this file was frozen."},
    "rules": rules,
    "controls_without_a_mutant": PREV["controls_without_a_mutant"] + [
        "Recovery's refusal when the organism's saved state is unreadable: not exercised.",
        "The owner's refusal when the previous crossing in a category is unknown to its ledger: not exercised.",
        "The single clock reading in apply (expiry and record from one value): no test separates the two reads."],
    "retired": PREV["retired"],
    "tests": tests,
    "mutants": M,
}
out = HERE / "DECLARED_v0_8_5.json"
out.write_text(json.dumps(decl, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
sha = hashlib.sha256(out.read_bytes()).hexdigest()
(HERE / "DECLARED_v0_8_5.sha256").write_text(f"{sha}  DECLARED_v0_8_5.json\n")
(HERE / "CANDIDATE_v0_8_5_AT_FREEZE.sha256").write_text(
    f"{decl['candidate_sha256_at_freeze']}  humble_seed_v0_8_5_candidate.py\n")
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
(HERE / "DECLARED_v0_8_5.frozen_at").write_text(stamp + "\n")
print(len(tests), "tests;", len(M), "mutants; declared", sha, "frozen", stamp)
