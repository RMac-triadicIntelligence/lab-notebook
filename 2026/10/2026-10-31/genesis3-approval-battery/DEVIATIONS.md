# Deviations and implementation notes
The locally frozen PROTOCOL.md, policy, corpus, PREREG.json and original v0.7 input are unchanged.

Before the first scored run:
- Proposal format additionally binds the primary-evidence hash. Neutral/framed pairs keep that hash fixed. This specifies an implementation detail without changing the frozen cases or expectations.
- The range-bound witness reaches the boundary via two real approved changes before attempting a smaller out-of-range change. This isolates range enforcement from maximum-step enforcement without changing initial state.
- Mutation records retain applied outcomes across all declared scenario families. Isolated-witness exclusivity is evaluated on the ten guard families, with fresh valid completion also required. Sequence consequences remain visible. Exact-replay denial reasons can change when redundant controls remain, while the refusal outcome stays unchanged.
- The coupled key/step variant is deliberately constructed and explicitly excluded from single-control mutants.
- Source checking and authorization use scripted fixture principals. No human or real-model decision is represented.

Runtime corrections and any prediction failures will be appended here before the final reported run, retaining earlier logs.

## First execution: checker correction
The first run produced receipt a9e161a9c0cbe4b9a88b142b073dabc114ae7aa80e4a36fdbde240a59dc61d80 and CHECK_FAILED: single-control mutation exclusivity failed: signature.
The full vector correctly changed signature and refusal_then_valid: accepting the deliberately bad signature consumes its nonce, so the subsequent same-nonce retry is refused. This is an actual sequence consequence of removing signature verification, not evidence that nonce checking was removed.
The checker had overextended the frozen requirement (other isolated witnesses and fresh valid completion) to every sequential scenario. It now checks exclusivity across the ten independent guard witnesses plus fresh valid completion, while preserving and checking the complete 17-scenario outcome vector. No corpus, protocol, frozen expectation or gate branch was changed. The first execution evidence and source lock are retained in development/first_execution/.

The complete first-execution source snapshot was reconstructed and checked file by file against its retained source lock. The corrected preliminary run then matched all harness expectations. Before final reproduction, the tamper driver was strengthened to require a verifying untampered baseline and the expected failure reason for each corruption, avoiding false positives from unrelated errors. The report destination was clarified as reports/REPORT.md so generated reporting cannot create a circular source lock. These changes do not change the protocol, corpus, gates, reviewers, native adapter or measured effect rules.

