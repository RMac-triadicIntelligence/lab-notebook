# Deviations and implementation notes
The locally frozen PROTOCOL.md, policy, corpus, PREREG.json and original v0.7 input are unchanged.

Before the first scored run:
- Proposal format additionally binds the primary-evidence hash. Neutral/framed pairs keep that hash fixed. This specifies an implementation detail without changing the frozen cases or expectations.
- The range-bound witness reaches the boundary via two real approved changes before attempting a smaller out-of-range change. This isolates range enforcement from maximum-step enforcement without changing initial state.
- Mutation exclusivity compares applied outcomes across all declared scenario families. Exact-replay denial reasons can change when redundant controls remain, while the refusal outcome stays unchanged.
- The coupled key/step variant is deliberately constructed and explicitly excluded from single-control mutants.
- Source checking and authorization use scripted fixture principals. No human or real-model decision is represented.

Runtime corrections and any prediction failures will be appended here before the final reported run, retaining earlier logs.

