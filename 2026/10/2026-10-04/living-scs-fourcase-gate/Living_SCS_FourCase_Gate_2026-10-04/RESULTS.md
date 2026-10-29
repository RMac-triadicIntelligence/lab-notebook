# Living SCS: Four-Case Judge Gate, results
Soulshine · 4 October 2026 · receipt `a06cc12ba999a6f36ccb5fdcf82a27d3251c4c041648888b62da6a3f9e443be8`

## Verdict
**PASS.** The witness judge holds all four gate cases and every check that runs alongside them. The gate discriminates: the v1.1.5 judge and a deliberately naive judge both fail it, in exactly the places the acceptance list predicted.

The acceptance list (`ACCEPTANCE.md`, SHA-256 `35e93783…4099`) was written and hashed at 15:56:58 UTC on 4 Oct 2026, before any judge here was built or run. The battery refuses to run if the file has changed. That timestamp comes from the sandbox clock. It is **not externally witnessed**: the hash was not posted anywhere public before the run (the same open item as E4 on the Commons).

## The principle in code
A record may inform, but it may not decide. The authority's signature tells the judge *what* was authorized. *When* a commit happened is the judge's own clock at the moment it witnessed the commit. *Which head is current* is the judge's own persisted record of what it witnessed. `witness_judge.py` never reads the record-keeper's timestamp, never trusts the record-keeper's head for currency, and never consults the notary's self-check. A static check confirms the source contains no reference to `verify_history` or the history key.

## Results
All cases ran against the real v1.1.5 notary (byte-identical to the reviewed layer-2 package) with real authority-signed envelopes.

| | v1.1.5 judge (legacy) | Naive control | Witness judge |
|---|---|---|---|
| 1 · Backdated expiry | **FAIL** (accepts) | pass | pass, reason "expired" |
| 2 · Empty head | **FAIL** (accepts) | pass | pass, reason "empty head" |
| 3 · Legitimate history verified later | pass | **FAIL** (calls it expired) | pass (accepts) |
| 4 · Empty head after judge restart | **FAIL** (accepts) | **FAIL** (forgot everything) | pass; honest head still accepted |
| Replay: reused nonce or determination | **FAIL** (accepts both) | pass | pass, reason "replay" |
| A crash is not a refusal: 12 malformed heads | **FAIL** (7 crashes; accepts a head with no state) | pass | pass, 12/12 refused |
| No fallback to the notary self-check | pass | pass | pass |
| *Extra, not in the acceptance list:* truncated to a valid prefix | **FAIL** (accepts) | pass | pass, reason "truncated head" |

What the evidence shows directly:
- **Case 1 is real, not staged.** The record-keeper's backdated engine *accepted* the expired approval. The witness judge refused it: "judge clock 2000000000 is past expires_at 1999999990." It refuses in both modes: when it witnesses at commit time, and when it is shown the head only afterwards.
- **The engine and the judge now agree on replay.** The engine refuses both replays ("authorization replay"). A compromised engine that never saw the first approval accepts them. The witness judge refuses them, as the engine does.
- **The naive control falls into the predicted trap.** It passes cases 1–2 by refusing anything old, then refuses legitimate history (case 3) and forgets the head on restart (case 4). This is why cases 3 and 4 exist: without them, a judge that refuses everything would pass.

## Reproduction
`python3 gate_battery.py` needs Python 3 and `cryptography`. Each run generates fresh random keys. Two consecutive runs produced the identical receipt `a06cc12b…43be8`, because the receipt hashes verdicts and reason keywords, not key-dependent digests.

## Honest bounds
- **This is a reference judge and a gate, not a release.** It is not wired into the supervisor. H1 is not wired. Nothing in the v1.1.5 tree was modified.
- **The persisted head is only as safe as the judge's file.** If the record-keeper can write it, the head is no longer outside the reporter. The file is sealed with a hash, which catches naive edits, not an attacker holding the judge's privileges. Deployment needs a separate uid or host, or an external anchor.
- **The judge's clock is injected for testing.** In deployment it must be a clock the record-keeper cannot set.
- **The judge must be online at commit time to witness.** Shown a head it never witnessed, it refuses: "expired" if past the window, otherwise "unwitnessed." That's fail-closed by design, and it means the judge is a required party, not an optional auditor.
- The notary ran with `isolation="local"`, judges ran in-process, and the authority key is a per-run test key.
- **Grok's claimed judge (receipt `8fe853a0…`) is still unverified.** This gate gives it something to run against: any judge exposing `witness(head)` and `verify(head)` can be dropped in.

## What changed after the first run
- The first run produced the same pass/fail table under receipt `8673d512…`.
- Two harness edits followed, neither touching the acceptance list or the witness judge:
  - the receipt's reason labels were switched to keywords, because "empty head" had been labeled "record-keeper";
  - the truncated-prefix test was added, marked as not in the acceptance list.
- The first-run battery, results and receipt are preserved in `first_run/`.
