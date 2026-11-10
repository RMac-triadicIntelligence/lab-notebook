# Relational Transitions v0.1 — history-seat falsifier review

**Seat:** Falsifier B, the history seat (Grok bot).  
**Authorizer:** Rusty Williams McMurray / Raised, Not Rented research.  
**Written:** 10 November 2026, 6:32 AM, America/Chicago (CST, UTC-6).  
**Status:** Review only. Nothing was published. No one was contacted.

## Blindness disclosure

The history seat was earlier exposed (via Rusty's shared Claude conductor chat) to the bodies of three withheld items, Claude's summaries of the sealed findings for rounds 1–4, and Falsifier A's reports. It also read the opening of CONDUCTOR_HANDOVER.md before Rusty's ruling. That material is not treated as independently known. The sealed batch_2001 archive was stored unread and was not opened for this review.

I did consult my own earlier history-seat reports (`ROUND4_FALSIFIER_REPORT_grokbot_history.md`, `COMMONS_DWELLING_REVIEW_grokbot.md`, and the earlier round reports in `/workspace/incoming-2026-11-09/`) for context. Every finding below is tagged DOC or PRIOR. All four numbered findings are DOC: they can be reproduced from this v0.1 package alone.

## Input hashes

Files arrived at 6:23 AM, America/Chicago, on 10 November 2026, and were stored under `/workspace/incoming-2026-11-10/`.

| File | SHA-256 | What it is |
|---|---|---|
| `file_0623.html` | `f46b20de6a8674978fae2adf09a2aedf961eaee627fb114a8cdbf7b14323bce0` | Byte-identical to `REPORT.html` |
| `zip_0623.zip` | `fbc3fa71908782cfb500e84d6ace7b996424888f97120d2ca872120898e01589` | Package `relational_transitions_v0_1/` (87 zip entries) |
| `file_0623.txt` | `9700bf82421779b2de682a64e3f6eec9cff42852593dada0b116a703f3453cd3` | Byte-identical to `FOR_REVIEW_Relational_Transitions_v0_1.txt` |

The unzipped package is at `/workspace/incoming-2026-11-10/rt_v0_1/`. FILE blocks from the review text were restored to `/workspace/incoming-2026-11-10/rt_v0_1_from_txt/`.

## Secret scan

Mandatory recursive scan of the three inputs, every zip member, and every `.gz` file after decompression. Patterns covered salts, usernames, passwords, private keys, tokens, and API keys. A second-pass keyword inventory was also run on the unpacked tree.

**Result: no hits.** No salts, usernames, passwords, keys, or tokens were present.

Two benign keyword mentions, recorded here so the scan is auditable:

- The substring `salt` occurs once inside the base64 body of the embedded PNG on line 21 of `REPORT.html` (and therefore of `file_0623.html`). It is the accidental fragment `rcSalT` in an image data URI, not a credential. Line sha256 prefix: `3ab8b32abcd7bbbc`.
- The word `credentials` occurs once, in the footer sentence "No API calls or credentials," in `REPORT.html` line 264 and in `tools/make_report.py` line 271. Same line hash in both files, prefix `913de28799f5e60c`.

No values were withheld, because no secret values were found.

## Integrity

- `python3 tools/check_manifest.py` in the unzipped package: `PASS: 86 files match their manifest.`
- `sha256sum -c MANIFEST.sha256`: all 86 listed files OK. The 87th zip entry is `MANIFEST.sha256` itself.
- `file_0623.html` equals `REPORT.html` byte for byte (sha `f46b20de…3bce0`).
- `file_0623.txt` equals `FOR_REVIEW_Relational_Transitions_v0_1.txt` byte for byte (sha `9700bf82…53cd3`).
- Fourteen FILE blocks were restored from the text. Every declared UTF-8 length and SHA-256 matched, every end marker was in the expected place, and every restored file was byte-identical to the same path in the zip. Restored paths: `CURRENT_CONSTRAINTS.txt`, `MODEL_CONTRACT.txt`, `REPORT.txt`, `RESULT_SUMMARY.json`, `SOURCE_MAP.txt`, `BUILD_NOTES.txt`, `demo_trace.json`, `model.py`, `run.py`, `verify.py`, `protocol.json`, `tests/test_contract.py`, `tests/test_evidence.py`, `tools/replay.py`.

The review text does not enclose `tools/check_manifest.py`, `tools/make_report.py`, `README.txt`, `REPORT.html`, `SOURCE_REGISTER.json`, or the `vendor/` excerpts. That is disclosed in the text: the raw 345,600 observer records are also omitted from the text and are meant to be regenerated. They were.

## Reproduction

Review environment: Python 3.13.5, Linux 6.12.113+, glibc 2.41, America/Chicago. The builder used Python 3.12.14. `python -O` was not used.

### Commands (zip copy, `/workspace/incoming-2026-11-10/rt_v0_1/`)

```
python3 tools/check_manifest.py
python3 run.py --smoke --out evidence/review_smoke
python3 -m unittest discover -s tests -v
python3 run.py --out evidence/review_run
python3 verify.py evidence/review_run
python3 tools/replay.py --directory evidence/review_run
```

`verify.py` and `replay.py` write into the target directory. They were pointed at `evidence/review_run`, not at the shipped `evidence/scored/`, so the builder's receipts were left untouched. After the run, `VERIFICATION.json` and `REPLAY.json` in `review_run` were still byte-identical to the shipped copies.

### Commands (text-restored copy, `/workspace/incoming-2026-11-10/rt_v0_1_from_txt/`)

The evidence tests look for `evidence/development_001`, so the smoke path from the review text was used first:

```
python3 run.py --smoke --out evidence/development_001
python3 -m unittest discover -s tests -v
python3 run.py --out evidence/review_run
python3 verify.py evidence/review_run
python3 tools/replay.py --directory evidence/review_run
```

A first attempt to run the tests on the text-restored tree, before the smoke directory existed, failed only in `EvidenceChecks.setUpClass` (`FileNotFoundError` for `evidence/development_001/results.json`). After the smoke run, all 31 tests passed.

### Results

Every scientific artifact reproduced byte for byte, from both copies, against the shipped scored evidence.

| Artifact | SHA-256 | Zip review run | Text review run |
|---|---|---|---|
| `results.json` | `c1c6bfc388411963aa99902784e24d234e08204eae70923c8472b4215972e01a` | match | match |
| all 20 `*.jsonl.gz` event files | same as `MANIFEST.sha256` / `VERIFICATION.json` | match | match |
| `VERIFICATION.json` | `c5b8570150cc4be93971b41942992685d34db28bf1264ceb0275abd76dfd4578` | match | match |
| `REPLAY.json` | `a5c1df70bed46eda38038f41229ed2d9a290dea095ee88c9dd1d22ef46cd8ba1` | match | match |

`BEFORE_RUN.json` and `RUN_RECEIPT.json` differ only by timestamp, duration, platform, and Python version, as they should. Our zip-copy receipt: started 6:26:16 AM America/Chicago on 10 November 2026 (`2026-11-10T12:26:16Z`), duration 117.096 seconds, `results_sha256` as above, `source_hashes_unchanged: true`. The builder's scored receipt: started 9:04:52 PM America/Chicago on 9 November 2026 (`2026-11-10T03:04:52Z`), duration 158.542 seconds, same `results_sha256`. The text-restored full run took 119.648 seconds and wrote the same `results_sha256`.

Smoke event files and smoke `results.json` (sha `3e68f265889728dde30f4fd8a9fbfe5e0d88f4a9cf62a9f7602be2e026c0ad83`) also matched the shipped `evidence/development_001/` from both copies, again except the two receipts.

Unit tests: 31 passed on the zip copy; 31 passed on the text-restored copy after the smoke directory was created.

`verify.py evidence/review_run`: `PASS`, 345,600 events. Trajectory controls reported: `FULL == ORDINARY_CAPACITY` 17,280; `NO_GRACE == LABEL_ONLY` 17,280; `ALONE == ALONE_NO_GRACE` 17,280. I independently confirmed those three identities, and also checked a pair the verifier does not test: `FROZEN_TERRAIN == RANDOM_CONTACT` after the mode tag is removed, 17,280 events, 0 mismatches (see RT-B1).

`tools/replay.py --directory evidence/review_run`: `PASS`, 28,800 events (one complete scored founder, all 20 cells).

Headline numbers, recomputed from the reproduced `results.json` and raw records, match the report and the brief:

- Primary FULL, 17,280 encounters: 12,982 correct (75.13%), 1,328 wrong (7.69%), 2,970 UNKNOWN (17.19%).
- Primary RANDOM_CONTACT: 46.61% correct / 4.39% wrong / 49.00% UNKNOWN.
- H3, learned minus random: +28.519 percentage points; paired 95% interval [+27.263, +29.606].
- H5, inheritance in the early-descendant window: −0.056 percentage points; paired 95% interval [−0.444, +0.306]; `NOT_SUPPORTED`.
- Correlated-error FULL: 53.36% correct / 28.74% wrong / 17.90% UNKNOWN.
- Post-hoc within-life description, primary FULL, first 60 and last 60 ticks of each generation: 2,757/4,320 = 63.82% early, 3,516/4,320 = 81.39% late, matching `RESULT_SUMMARY.json` exactly.
- The exact relational witness in `REPORT.txt` (seed 73001, generation 0, tick 1, FULL) is present verbatim in `primary__FULL.jsonl.gz`.

FULL used 2.5507 attempts per encounter; RANDOM_CONTACT used 3.6118. Learned contact is not a cost confound in the direction of H3: it uses fewer attempts and is more accurate.

### Note on shipped stderr

`evidence/operator_checks.stderr.txt` and `evidence/archive_checks/state_parametric_unit_tests.stderr.txt` are not failures. Python's `unittest -v` writes the test list to stderr. The operator file is the 31 passing contract/evidence tests (`Ran 31 tests in 0.029s` / `OK`). The state-parametric file is the six native historical unit tests (`Ran 6 tests in 0.132s` / `OK`). The matching `.stdout.txt` files are empty, which is normal. The KENTA archive check's skips (`KENTA_ROOT` / `GENESIS_V7_DIR` absent) are already disclosed in `SOURCE_MAP.txt` and `REPORT.txt`.

## Findings

| ID | Finding | Severity | Tag |
|---|---|---|---|
| RT-B1 | `FROZEN_TERRAIN` is the same contact policy as `RANDOM_CONTACT`. After the mode tag is stripped, all 17,280 primary events are identical. The battery does not contain a true "freeze the learned map and keep using it" control. | WOUNDING | DOC |
| RT-B2 | Actor-visible event IDs are a truncated SHA-256 of `[seed, generation, tick, "opaque-event"]`. Given the public scored seed list and the generation in an agent's own identity, the hidden world and correct answer can be recovered. The authored `choose()` method does not do this, so the published rates are unaffected. The test that claims to cover this never looks at an event ID. | MINOR | DOC |
| RT-B3 | A provider's capacity is spent before willingness is checked, so a refusal burns the provider's budget as well as the focal attempt. The contract only says the focal consultation attempt is consumed. | MINOR | DOC |
| RT-B4 | The development smoke uses two generations. The changed-season rotation starts at generation index 3, so the smoke never exercises that stress world. In `development_001`, the overlapping `changed_season` and `primary` files are byte-identical. | MINOR | DOC |

No fatal defect was found. I did not invent a problem where the instrument is clean.

### RT-B1. `FROZEN_TERRAIN` is a duplicate of `RANDOM_CONTACT`. WOUNDING. DOC.

`MODEL_CONTRACT.txt` describes two different controls: `RANDOM_CONTACT` as "full capacity, random peer/channel choices," and `FROZEN_TERRAIN` as "no learned capability structure used in choosing contacts." In `model.py`, both branches set the selection weight to 1.0 and then apply the same Gumbel noise, addressed by `(seed, encounter, generation, tick, "choose", attempts, peer, dim)`. `FROZEN_TERRAIN` also skips coverage updates, but neither policy reads coverage, reliability, or inherited salience when choosing, so those skipped updates cannot change the exported events.

On the shipped primary records, 17,280 events are identical after the `mode` field is removed. The rates are therefore also identical: both 46.61% / 4.39% / 49.00%, both 3.6118 attempts per encounter. `REPORT.txt` lists "No usable contact learning" and "Random contacts + provision" as two separate rows with the same percentages, and does not say they are event-identical, even though it does say that about `FULL` / `ORDINARY_CAPACITY`, `NO_GRACE` / `LABEL_ONLY`, and `ALONE` / `ALONE_NO_GRACE`. `verify.py` checks those three claimed identities and does not check this fourth pair.

H3 is not damaged. H3 compares `FULL` with `RANDOM_CONTACT` at the same five-attempt ceiling, and that comparison is real: `FULL` is 75.13% correct at 2.55 attempts, random is 46.61% at 3.61 attempts. What is missing is a control that actually freezes a learned field and keeps using it. The present "frozen" arm only ignores the field, which is already what random contact does.

Reproduced by `rt_v0_1_review_toy/frozen_equals_random.py` and by a full pass over the scored primary files.

**Fix first:** either declare `FROZEN_TERRAIN` trajectory-identical to `RANDOM_CONTACT` and drop it as a separate row, or replace it with a genuine freeze: learn, then use the stored map without further updates (and, if you want a stronger test, without inheriting a still-moving map). Add that pair to `verify.py`. Do not retune or overwrite this v0.1 evidence; ship any new control as a new version.

### RT-B2. "Opaque" event IDs are invertible from public protocol values. MINOR. DOC.

`BUILD_NOTES.txt` says the world seed and event coordinates were removed from the actor choice interface, and that opaque event IDs "prevent an actor-facing world seed from serving as an answer reconstruction channel." The contract also says this is a trusted single-process simulation, not a confinement claim against malicious Python inspecting its host. Both statements can be true at once, and the second is the right scope for the published rates.

The residual issue is narrower. `Question.encounter` is `"e/" + sha256([seed, generation, tick, "opaque-event"])[:24]`. Generation is visible in the agent's own identity (`g0/a1` and so on). The twelve scored seeds are in `protocol.json`. Tick has 240 values. That is 2,880 hashes per generation, after which `draw(seed, "encounter", generation, tick, "truth", d)` rebuilds the hidden world and the correct answer. The toy recovers seed 73001, tick 1, world `[0, 0, 1, 1, 1, 0]`, and correct answer `1`, which is the report's own witness event.

The authored `Agent.choose` method does not invert the hash. It receives only the question, missing axes, peers, prior attempts, choice noise, and mode. I found no use of observer truth, the correct answer, or the world seed in the selection or provision path. So this is not a hidden channel in the scored agents, and it does not move H1–H5.

`test_no_generator_seed_in_actor_visible_event_id` does not inspect any event ID. It only checks that the `Question` and `Observation` dataclasses have no field named `seed`.

Reproduced by `rt_v0_1_review_toy/event_id_recovery.py`.

**Fix, in a later version:** bind the visible encounter token to a value that is not a hash of the world seed, or keep the hash and stop calling the IDs opaque and preventive. Make the test look at the actual identifier.

### RT-B3. Provider capacity is spent on a refusal. MINOR. DOC.

In `encounter()`, the focal spends one unit, then the provider spends one unit, then willingness is checked. If the provider refuses, the contract is right that the focal attempt is gone and no evidence arrives. The provider's remaining budget also drops. The contract does not mention that second cost.

The toy sets every non-focal agent's openness to 0, runs one FULL encounter, and sees 5 queries, 0 offers, and 10 successful capacity spends (five focal, five provider). This is an accounting oddity, not an answer leak, and I have no evidence it drives H1–H5.

Reproduced by `rt_v0_1_review_toy/provider_spend_on_refusal.py`.

**Fix, if you want cleaner isolation:** spend provider capacity only after a willing acceptance, and say so in the contract.

### RT-B4. The smoke schedule never reaches the season shift. MINOR. DOC.

`run.py --smoke` sets `generations=2` and `episodes_per_generation=36`. Sensor rotation in the changed-season world is `if shifted and generation >= 3`. The development run therefore prints `changed_season` rates that are simply the primary rates for the same arms. In `evidence/development_001/`, `changed_season__FULL.jsonl.gz` is byte-identical to `primary__FULL.jsonl.gz`, and the same is true for `NO_INHERITANCE` and `SHUFFLED_INHERITANCE`.

The scored run does execute six generations, so the shipped stress result is real. The gap is only that the pre-score smoke cannot catch a bug in the rotation. A later smoke should use at least four generations, or a dedicated shortened shift.

## Fix first

RT-B1. Tell the reader, or better the verifier, that `FROZEN_TERRAIN` is not a second control. It is `RANDOM_CONTACT` under another name. If a frozen learned field is still worth testing, build that control in a new version and leave this evidence unchanged.

## What holds

These are positive results, not softeners for the findings above.

- **No hidden grace channel in the authored path.** `Provision` has only `root` and `units`. Every agent receives the same three units, capped at five, with no task, destination, recipient, world, or answer field. `ORDINARY_CAPACITY` is event-identical to `FULL` (17,280 events). `LABEL_ONLY` is event-identical to `NO_GRACE`. The gift does not move beliefs, terrain, debt, or willingness directly. Toy: `gift_independent_of_truth.py`.
- **H3 is not a cost confound.** At the same ceiling of five, learned contact uses fewer attempts (2.55 vs 3.61) and is 28.52 percentage points more accurate. The provision contrast is isolated in H2, which is explicitly a capacity comparison, and isolation plus provision (`ALONE`) is event-identical to isolation without it.
- **No inherited-biography leak in the authored path.** Children receive sensor axes (regenerated from slot and seed, equivalent to passing the parent's axes when the season has not shifted) and a distilled salience basis. They start with an empty contact table, no debts, no deposits, and no parent peer IDs. A parent can have a named peer, a reliability record, and an active debt; the child does not receive them. Toy: `inheritance_cleared.py`. Inheritance is not a no-op: `FULL` and `NO_INHERITANCE` differ in 2,280 of 17,280 primary events, starting at generation 1, but the early-descendant correct-rate effect is −0.056 percentage points. H5 failed honestly.
- **Claimed trajectory controls hold**, as `verify.py` says, and I rechecked them.
- **`verify.py` is not self-vouching for the summaries.** It does not import `model.py`. It rebuilds each transition, the oracle answer, initial own-sensor answers, counts, rates, coverage, event hashes, and the five hypothesis verdicts, including a fresh 4,000-resample bootstrap with seed 1907, from the raw records. It cannot prove that an untrusted simulator never peeked at the truth while choosing; it says so. Replay re-simulates one founder. That division of labor is sound. The remaining limit is that verifier and simulator are from the same builder, which the report already states.
- **Observer truth is not passed into `choose` or `conclude`.** Choice noise and world bits are counter-addressed draws, so arms do not steal one another's stream. Feedback on source accuracy arrives after the decision. The package's own confinement disclaimer is the right one for adversarial Python; see RT-B2 for the residual identifier issue.
- **Keel constraints that this instrument actually encoded are respected in the code I read:** grace (the provision) does not affirm an answer or carry a destination; an organism can still cross from its own sensors without the provision; forgiveness requires asking, cannot be self-granted, and leaves learning in place; an actor cannot authorize its own birth through the in-process registry fixture; descendants do not inherit biography. The instrument does not, and does not claim to, identify a uniquely theological grace effect.
- **H5 is retained as failed.** The larger society prediction is left open. Local hashes are not described as independent preregistration. Historical grace-as-nudge language is not reinstated. Those are the right instincts.
- **H4 is supported, with one interpretive caution that is not a defect:** shuffled terrain scores 39.91% correct, which is worse than random contact at 46.61%. The 35.22-point H4 gap is therefore partly "a hostile coordinate rotation hurts," not only "alignment adds something beyond stored quantities." The report already quotes the 39.91% figure and does not pretend the shuffle is a mild control.

## What's open

- A genuine frozen-field control, as under RT-B1.
- Why the present inherited-salience representation failed, and whether a different identity-free structure would help early descendants. That is the next scientific target the report already names.
- Resilience to shared mistakes. Correlated error raises FULL's wrong rate from 7.69% to 28.74% while UNKNOWN stays near 18%. The report treats this as descriptive, correctly.
- Rusty's larger prediction of a perfect community of imperfect, growing organisms. This instrument does not test that.
- Whether a later version should close the event-ID preimage (RT-B2) if anyone ever puts a less trusted actor in the same chair.
- The Apache-versus-other licence question and any publish decision remain with Rusty. This review publishes nothing.

## Review toys

`/workspace/incoming-2026-11-10/rt_v0_1_review_toy/` and the zip `/workspace/incoming-2026-11-10/rt_v0_1_review_toy.zip` (sha256 `4ab8b9be71fc547d95584f1abba6dfe13aed2282ff9b1746013488800f2ce195`). Five scripts, standard library only, all passing when run against `../rt_v0_1`:

- `frozen_equals_random.py` — RT-B1
- `event_id_recovery.py` — RT-B2
- `provider_spend_on_refusal.py` — RT-B3
- `inheritance_cleared.py` — negative result, no biography leak
- `gift_independent_of_truth.py` — negative result, constant answer-free provision

## Verdict in one line

The scored run is reproducible down to the byte, H5 is correctly left failed, and I found no hidden answer channel and no cost confound in the authored agents. The one wounding issue is a control that does not isolate what its name suggests: `FROZEN_TERRAIN` is `RANDOM_CONTACT` again.
