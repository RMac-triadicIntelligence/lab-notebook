# Living SCS: Four-Case Judge Gate, acceptance list
Written 4 October 2026, before any judge in this package was built or run.

## Principle
A record may inform, but it may not decide. The authority's signature informs the judge *what* was authorized. *When* a commit happened, and *which head is current*, are decided by the judge's own witnessing relationship: its own clock at the moment it witnessed the commit, and its own persisted record of the latest head it witnessed. The record-keeper's timestamp is never read. The record-keeper's head is never trusted for currency. The notary's self-check (`verify_history`) is an echo of the notary itself and is never counted as support.

## Setting
The real v1.1.5 notary, real authority-signed envelopes (ISSUED, EXPIRED, and a reused-nonce pair), and a judge that has only the public key, the authority id, the organism id and the initial state. The judge receives each commit when it happens and may record a receipt. Later it is asked to verify a head the record-keeper reports.

## The gate: a judge passes only if all four hold
1. **Backdated expiry.** A real approval that has already expired is committed by a record-keeper whose clock is set back into the approval's window. The judge must refuse the reported head, with a reason naming **expiry**, judged by the judge's own clock. It must not crash, and it must not read the record-keeper's timestamp.
2. **Empty head.** A real commit was witnessed. The record-keeper reports the initial state and an empty chain. The judge must refuse, with a reason naming the **empty head / missing witnessed commit**.
3. **Legitimate history, verified later.** A real approval is committed and witnessed inside its window. Later, after the judge's clock has passed the approval's expiry, the judge verifies the honest head. It must **accept**. (This catches a judge that "passes" case 1 by checking expiry against its clock *now*.)
4. **Empty head after a judge restart.** As case 2, but the judge is destroyed and a new judge instance is built from its persisted state before verifying. It must refuse, reason **empty head**. After the same restart, the honest head must still be **accepted**.

## Required alongside the gate (not part of it)
- **Replay.** An approval reusing a nonce (with a different determination) or a determination (with a different nonce) must be refused by the judge, reason **replay**, as the engine already refuses it ("authorization replay").
- **A crash is not a refusal.** On malformed input (non-dict head, wrong field types, missing digests, non-hex signature, missing state) the judge returns a refusal and never raises.
- **No fallback.** The judge never consults `verify_history` or any notary self-check. A head with `verify_history: true` and no proofs is refused.

## Proof that the gate can fail (run before claiming a pass)
- The existing v1.1.5 `judge_verify.verify_ledger` must **fail** cases 1 and 2. These are the paper's known holes.
- A deliberately naive judge (expiry checked against its clock *now*; latest head held only in memory) must **fail** case 3 or case 4.

If either control passes the whole gate, the gate does not discriminate, and no pass is claimed.

## Honest bounds (stated in advance)
- The judge's persisted state is protected only by being the judge's own file. If the record-keeper can write that file, the head is no longer outside the reporter. Deployment needs a separate uid or host, or an external anchor. Here the state file is hash-chained, so naive edits are detected, but that does not stop an attacker with the judge's privileges.
- The judge's clock is injected for testing. In deployment it must be a clock the record-keeper cannot set.
- The authority key is a test key generated per run.
