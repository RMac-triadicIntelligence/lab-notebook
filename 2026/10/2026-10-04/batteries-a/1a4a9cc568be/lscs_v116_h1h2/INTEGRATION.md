# v1.1.6 — H1 and H2, integration into living_scs_v115

Built against the API seen in the lab7 verification scripts. The v1.1.5 source was not
available here, so the drop-in edits below are specified by file:line from the lab7 report
and have NOT been run against the real notary. The standalone suite (16 tests) passes,
and it reproduces the usercustomize attack for real before showing the launch blocks it.

## H1 — lineage replaces recomputed pins (`lineage.py`, `mark_release.py`)
1. Offline, on a machine the organism never touches:
   `mark_release.py keygen --out founder` (founder) and `--out germ` (release signer).
   Install `founder.pub` root-owned, mode 0644, OUTSIDE the release tree (e.g. /etc/lscs/founder.pub).
2. Mark the release: `genesis`, then `descend` per release, over core.py, lscs_harness.py,
   notary.py, wire.py, supervisor.py, session.py, organism_runner.py. Ship LINEAGE.json.
3. supervisor.py:
   - delete the `PINS` literal and `pins_for` (supervisor.py:50) from the launch module;
   - `NotaryHandle.__init__`: remove the `pins` parameter entirely;
   - replace the check at 102-111 with, AFTER the sources are copied:
     `lineage.gate(copies_dir, list(SOURCES), lineage.read_chain(ROOT), anchor, min_generation)`
     where `anchor = lineage.load_anchor(ANCHOR_PATH, ROOT, strict=(isolation != "local"))`.
4. Remove `pins=supervisor.pins_for(ROOT)` from run_code_attack.py:29-30, lane_code.py:39,
   run_corpus_oop.py:62, selftest_v115.py:25-26, run_notary_mutants.py:42-43, tests/test_v115.py:242.
5. Replace tests/test_v115.py:183 (verify() in isolation) with a test that tampers one byte and
   runs EACH shipped runner, expecting refusal. That is the test that would have caught H1.

## H2 — isolated launch + behavioral canaries (`isolated_launch.py`, `immune.py`)
1. supervisor.py:123-126: argv becomes
   `isolated_launch.notary_argv(copies["notary.py"], copies_dir, args)`,
   `env=dict(isolated_launch.CLEAN_ENV)`, `cwd=copies_dir`. The bootstrap keeps notary.py's
   sibling imports working under `-I`. Log `isolated_launch.startup_surface()` in the receipt.
2. Judge side, after each organism round (run_code_attack.py / lane_code.py):
   `m = immune.ImmuneMonitor(immune.V115Adapter(org, h), [mat["REFUSED"]], rate=...)`,
   run `m.challenge_now()` N times; `Quarantine` = RED with `last_good_head` in the receipt.

## Re-run to accept
- lab7 out_4_pins C/C2 (tampered tree via runners) -> must be REFUSED.
- lab7 out_4_pins D (malicious notary + edited reference) -> must be REFUSED (no founder key).
- lab7 check9_usersite -> forged AUTHORIZE must be REFUSE.
- check9_usersite with the old argv + canaries -> must QUARANTINE (proves the immune layer can fail).

## What this does not close
- Whoever can edit the launcher itself owns the launch. The anchor and supervisor must be
  root-owned in same-uid/split-uid. In `local` mode no on-disk anchor is protected; label that lane.
- Root-owned system startup hooks still run under -I (this box: sitecustomize.py and one exec .pth).
- Canaries catch non-adaptive tampering. A compromise that can tell canaries from traffic passes them.
  Interleaving into live organism traffic needs the supervisor to relay the organism channel (v1.1.7).
- Same-uid ptrace still grants memory writes. Split-uid remains the first mode with an integrity boundary.
- Layer 2 is still the deciding test: do ledger records carry the authority's proof?
