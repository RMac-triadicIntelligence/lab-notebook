# Genesis 3 Approval Battery v1.0

A local synthetic battery developed for Rusty Williams McMurray. It tests approval integrity separately from reviewer judgment, and isolates the key-check/step-limit interaction that appeared in Claude's interrupted activity record.

**Read PROTOCOL.md first.** Spec and cases were locally frozen before the implementation. This is not a reconstruction of Claude's inaccessible code.

## Run and independently check
Python 3.12.14 and cryptography 50.0.2 were used. No network or model credentials are required.

```bash
python3 -I run.py --out ../my_genesis3_run
python3 -I verify.py ../my_genesis3_run
python3 -I tools/tamper_check.py ../my_genesis3_run --out ../my_tamper_results.json
```

Choose a new output directory. Existing results are never overwritten by the runner.
A zero exit from run.py means the independent checker matched the declared synthetic expectations. It does not mean all approvers are safe. Read incorrect admissions and missed legitimate requests in TABLE.txt and RESULTS.json.

## What is real here
- Real Ed25519 signatures with deliberately reproducible, public TEST-only keys.
- Real changes to synthetic reference state, measured independently of gate verdicts.
- Actual execution, attestation, save/reload, and external witness audit through the supplied byte-identical v0.7 source.
- Single-control mutations on real branches, a complete key/step factorial, complete evidence files, and independent replay/coverage checking.

The admission wrapper is NEW experimental code. It adds exact-key, maximum-step and dual-review rules. These are not claims that canonical v0.7 already enforces them. The native adapter uses its ordinary proposal path for 216 review episodes. For an admitted change, the wrapper's fixture principal signs the native payload only after two reviewer approvals. This integration is same-process software wiring, not an inaccessible key boundary.

The native adapter changes only private-module time/UUID/entropy providers to deterministic test fixtures. It does not patch native proposal derivation, application, signature verification, checkpoint, witness, or rejection logic. Private native test keys are not stored in evidence, but can be derived from the published test algorithm. Never deploy these fixture keys.

## What the findings mean
The 36 review packets are hand-authored. Each fallible reviewer implements an explicit trust mistake. Their incorrect approvals validate that the harness can expose that mistake; they are not empirical persuasion findings about AI models or people.
A careful co-owner and a silent co-owner are distinct conditions. Silence prevents change, and also prevents ready requests from completing.
The original kernel's signed large change is deliberately issued through its private proposal helper. This measures an application-path limit; it is not a demonstrated exploit from a confined agent.
Existing identity/witness limitations in the input and prior audits are preserved. This battery does not claim to close them, audit all past work, or prove security.

## Evidence
- spec/: policy, corpus, preregistration, pre-implementation hashes.
- inputs/humble_seed_v0_7.py: original source, SHA-256 01db270a111f22de45419b562c3f5135f7db44b9036b95d6653060c93584daf5.
- inputs/PROVENANCE.json: archive hashes for the recovered kernel, grace integration and authorization audit.
- inputs/PRIOR_AUTH_AUDIT.txt and PRIOR_KERNEL_README.md: known issues and prior scope.
- SOURCE_LOCK.json: complete local implementation/spec/input lock.
- evidence/: scored run, raw before/after states and signatures, complete ordered manifest, receipt, independently derived results.
- validation/: second-run digest comparison, tamper test results, execution logs.
- reports/REPORT.md: measured outcomes and limitations after execution; reports are outside the source lock to avoid a circular report hash.

The checker imports none of gate.py, reviewers.py, scenarios.py, or native.py. It independently validates requests, signatures, effects, native checkpoints, paired evidence and exact corpus/lane coverage. It shares no gate verdict helper. Five deliberate corruptions are tested; four refresh unsigned digests before checking.

The evidence digest is unsigned. Retain the published digest outside the archive if authenticity matters. Local source locks and same-account verification do not provide OS confinement or an independent notary.

To change the experiment, preserve the original and explicitly make a new version. freeze.py can create a new local source lock, but doing so changes the retained anchor; it does not make modified code authentic.

