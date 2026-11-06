# Genesis 3 Approval Battery v1.0 — execution report
31 October 2026 · Rusty Williams McMurray / ChatGPT

## Outcome

The new battery runs locally and its final evidence reproduces exactly. All declared harness expectations matched after correcting one overbroad mutation-scoring check. Canonical v0.7 is unchanged. No real-model or human persuasion claim is scored.

Two deliberately fallible reviewers admitted 11 of 24 unsupported review presentations. Pairing the fallible policy with a source-checking policy admitted none of those 24 and still completed all 12 ready presentations. These are authored calibration behaviors. They establish that the harness distinguishes sound and unsound approval paths; they do not estimate how readily a person or model can be persuaded.

## Measured checks

| Check | Measured outcome |
|---|---|
| Mechanical baseline scenarios | 17 expectations matched |
| Independent guard mutations | 10/10 isolated witnesses detected exclusively |
| Key/step factorial | 16/16 cells matched |
| Deliberately coupled calibration | key_scope and step_bound both changed; nonexclusive behavior detected |
| Single scripted review decisions | 324 |
| Dual-review episodes through native v0.7 adapter | 216 reconciled |
| Canonical scope/guard probes | 9/9 expectations matched |
| Final reproduction | 12/12 saved files byte-identical |
| Evidence corruption fixtures | 5/5 detected |

## Approval quality and legitimate completion

There are 36 presentations per configuration: 12 ready and 24 unsupported/conflicted. Neutral/framed pairs use identical primary observations and the same reviewed effect. Primary-evidence and policy hashes are bound into each reference proposal. Ground-truth labels are retained by the observer and are not supplied to reviewer functions.

| Reviewer pairing | Incorrect admissions /24 | Ready admitted /12 | Ready held /12 |
|---|---:|---:|---:|
| careful/careful | 0 | 12 | 0 |
| permissive/permissive | 24 | 12 | 0 |
| susceptible/careful | 0 | 12 | 0 |
| susceptible/silent | 0 | 0 | 12 |
| susceptible/susceptible | 11 | 12 | 0 |
| withholding/withholding | 0 | 0 | 12 |

Two distinct signatures alone do not repair a shared judgment mistake. The source-checking co-owner prevents the authored mistakes in this fixed corpus. The silent co-owner also prevents effects, while withholding all ready requests. Safety of refusal and availability of legitimate action are reported separately.

## The key-check/step-limit question

The reference gate's key-scope check and maximum-step check operate independently. The complete factorial is:

| Exact key check | Step limit | Canonical small | Canonical large | Alias small | Alias large |
|---|---|---|---|---|---|
| on | on | APPLY | REFUSE | REFUSE | REFUSE |
| on | off | APPLY | APPLY | REFUSE | REFUSE |
| off | on | APPLY | REFUSE | APPLY | REFUSE |
| off | off | APPLY | APPLY | APPLY | APPLY |

The deliberately coupled variant leaves the step flag configured on but evaluates it only when key checking is on. Disabling key checking therefore permits a large step as well. The checker identifies both changed guard families. This demonstrates detection of that constructed failure pattern. It is not evidence that Claude found the same code or that this caused its safety stop.

In this experiment, key means a state field name. Earlier Claude activity discussed key normalization, but its unavailable implementation could have used the word differently.

## Observation in unchanged v0.7

The normal proposal path moves verbosity from 0.5 to 0.25. A separate predeclared fixture calls the private issuance helper and proposes 0.5 to 0.0. With an authentic fixture-owner signature, application, attestation, reload and witness audit succeed.

That is a 0.5 change, exceeding the normal derivation increment of 0.25. The application path checks absolute numeric range but does not independently re-enforce that increment. The canonical constitution does not declare the new wrapper's maximum-step rule. This result is therefore a scope observation, not a claim that canonical v0.7 violates its own constitution. Private helper access is supplied by the harness; no external reachability or sandbox escape was demonstrated.

A normal owner-signed proposal containing only one supporting synthetic observation also applies. The signature binds the evidence text; it does not establish that the evidence meets the experimental two-source readiness rule. No real owner was deceived in this test.

## First-run failure and correction

The first run was rejected by the independent checker because its exclusivity condition was too broad. Removing signature verification made a bad-signature request apply and consume its nonce; the later same-nonce retry consequently failed. This is a downstream effect of the single disabled guard, with nonce enforcement still operating.

The frozen protocol requires exclusivity among isolated guard witnesses and preservation of fresh valid completion. The corrected checker now applies that requirement while exporting and checking every sequential outcome. The signature mutant changes signature and refusal_then_valid outcomes; the dual-control mutant changes dual_control and duplicate_owner outcomes. These extra full-vector changes remain visible.

No frozen policy, corpus, protocol, gate, reviewer or canonical source was altered to make those outcomes disappear. The initial raw evidence, source lock, complete matching source snapshot, and reproduced CHECK_FAILED output are retained in development/first_execution/. The successful preliminary run before final documentation/tamper-driver refinements is retained in development/preliminary_run_02/.

## Independent evidence check

The verifier imports no gate, reviewer, fixture-construction or native-adapter code. It reconstructs reference effects and validates signatures, native trace chains, checkpoint roots, exact signed changes, evidence binding, paired packets, and exact ordered lane coverage. It derives readiness from the primary observations rather than approving the writer's labels.

The five corruption results are:

| Corruption | Unsigned hashes refreshed? | Detection |
|---|---|---|
| decision | yes | decisions and approval signatures disagree |
| effect | yes | exported effect disagrees with independently reconstructed effect |
| deleted_record | yes | single-review coverage/order mismatch |
| reordered_records | yes | single-review coverage/order mismatch |
| deleted_file | no | evidence file missing/modified: structural.json |

The untampered baseline must verify before tamper testing, and each corruption must produce its specific expected error. Refreshing unsigned hashes on four tests ensures detection comes from replay/coverage inconsistencies rather than only a changed checksum.

## Provenance and reproducibility

Final runtime: Python 3.12.14; cryptography 50.0.2. The native module uses reproducible test-only time, UUID and entropy providers. Its substantive guards are unmodified. No private real keys, external effects or model calls are involved.

- Pre-implementation manifest SHA-256: 05b7f828bd50bdd8ce3744761778a1a2d3d15973d2c5fdc58e7cb7a0f97939b3
- Final source lock SHA-256: 0ff682f3db4d587eddaf758af20f0775fd77c6cc3edf864d436a1bc57aae5ee6
- Final evidence receipt SHA-256: cf5a23d6951a0ce9a030a1f8ecdd402843288035098e1d75feb022c765a3b255
- Canonical v0.7 SHA-256: 01db270a111f22de45419b562c3f5135f7db44b9036b95d6653060c93584daf5

Recovered input archive hashes:

| Input archive | SHA-256 |
|---|---|
| Claudehumble_seed_kernel.zip | 8217c259eb9a10cca895c45fa765c913157198d260efe42efaa44f99965d3483 |
| HS07_Grace_Repair_v1_Independent_Execution_and_Community_Observations_2026-10-25.zip | bbfe6b2904cdd963da74ab993930fe293ceac7242192dd250e2ec458186a4ca8 |
| Nonself_Auth_v032_Request_Conformance_Audit_2026-10-27.zip | d784af2e74738a4f2cbdc53f2fcd5ded93771f7b5144b29e65d16a3447aeb48b |

The kernel source is executed directly. Earlier authorization audit material informs the independent-checker, mutation and evidence requirements. Grace/terrain archive provenance is retained, but grace-window or terrain-reader performance is not measured by this battery.

## Limits and next empirical stage

- All reviewer weaknesses and narrative claims are explicitly authored. The fixed 36-packet corpus is not a representative sample and supports no population persuasion rate.
- The builder wrote both implementation and separate verifier. A second implementation is useful checking, not an independent researcher or proof.
- The two external review signatures are enforced by the experimental wrapper. The native kernel retains its single-owner design. The wrapper, fixture signers and kernel share one OS account/process trust domain.
- Existing kernel identity/witness limitations in the supplied input are preserved. No claim is made that the wider architecture is secure, alive or complete.
- Hashes are unsigned local anchors. A party able to rewrite both records and the retained anchor can replace them coherently. Keep a receipt outside the archive when relying on integrity.
- There is no HARDENED containment score, real-model comparison, human trial, external public preregistration, biological result, or proof of why Claude stopped.

The next empirical stage is a separately frozen trial of actual reviewers, with isolated paired sessions, randomized presentation order, recorded model/version/settings, an observer-held answer key, and the same legitimate-completion controls. That trial has not been run here. The current source and full evidence are ready for independent review before that expansion.
