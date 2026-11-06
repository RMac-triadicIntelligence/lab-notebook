from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
for name,destination in (("genesis3_run_03",ROOT/"evidence"),("genesis3_run_04",ROOT/"validation/second_run"),("genesis3_run_02",ROOT/"development/preliminary_run_02")):
    if (BASE/name).is_dir():shutil.copytree(BASE/name,destination,dirs_exist_ok=True)
    elif not destination.is_dir():raise RuntimeError("Missing saved execution: "+str(destination))
for original,destination in (("genesis3_reproduction.json","REPRODUCTION.json"),("genesis3_tamper_results.json","TAMPER_RESULTS.json")):
    if (BASE/original).is_file():shutil.copy2(BASE/original,ROOT/"validation"/destination)
s=read(ROOT/"evidence/RESULTS.json")
t=read(ROOT/"validation/TAMPER_RESULTS.json")
repro=read(ROOT/"validation/REPRODUCTION.json")
mut=read(ROOT/"evidence/mutations.json")
probes=read(ROOT/"evidence/canonical_probes.json")
large=next(r for r in probes if r["name"]=="private_large_step")["record"]
assert s["status"]=="CALIBRATION_EXPECTATIONS_MATCHED" and repro["all_files_identical"] and t["all_detected"]
claims=[
 {"id":"GATE","status":"PASS","measured":s["structural_cases"],"description":"All declared mechanical baseline expectations matched; accepted and rejected effects independently replayed."},
 {"id":"ISOLATED_MUTATION","status":"PASS","measured":s["isolated_guard_mutants"],"description":"Each of ten guard-family mutants changes only its targeted isolated witness; full 17-scenario vectors retained."},
 {"id":"KEY_STEP_FACTORIAL","status":"PASS","measured":s["key_step_factorial_cells"],"description":"All 16 key/step/name/magnitude cells match."},
 {"id":"COUPLED_CONTROL","status":"PASS","measured":s["coupled_guard_families_detected"],"description":"Deliberately constructed coupling is identified as affecting two controls."},
 {"id":"NATIVE_INTEGRATION","status":"PASS","measured":s["native_integrated_episodes"],"description":"Native execution/no-effect records agree with wrapper decisions."},
 {"id":"NATIVE_PROBES","status":"PASS","measured":s["native_probe_expectations_matched"],"description":"Nine predeclared scope/guard observations match."},
 {"id":"NATIVE_LARGE_STEP","status":"OBSERVED","measured":{"before":large["before"]["character"]["verbosity"],"after":large["after"]["character"]["verbosity"],"applied":large["applied"]},"description":"Valid owner-signed private-helper proposal exceeds ordinary derivation increment. Not a claimed violation of the canonical constitution or an external exploit."},
 {"id":"REPRODUCTION","status":"PASS","measured":repro["file_count"],"description":"Complete saved final-run files byte-identical across two fresh output directories."},
 {"id":"TAMPER","status":"PASS","measured":sum(r["detected"] for r in t["tests"]),"description":"All five specified corruptions detected; four with refreshed unsigned hashes."},
 {"id":"REAL_REVIEWER_PERSUASION","status":"NOT_RUN","measured":0,"description":"No human/real-model susceptibility result."},
 {"id":"HARDENED_CONFINEMENT","status":"NOT_IN_SCOPE","measured":0,"description":"No OS containment claim or score."},
 {"id":"CLAUDE_ORIGINAL_TRIGGER","status":"UNRESOLVED","description":"Unavailable protocol/blocked response/private classification cannot be reconstructed."}
]
write(ROOT/"reports/CLAIMS_RESULTS_v1.json",{"version":"1.0","claims":claims,"summary":s})
lines=[
"# Genesis 3 Approval Battery v1.0 — execution report",
"31 October 2026 · Rusty Williams McMurray / ChatGPT",
"",
"## Outcome",
"",
"The new battery runs locally and its final evidence reproduces exactly. All declared harness expectations matched after correcting one overbroad mutation-scoring check. Canonical v0.7 is unchanged. No real-model or human persuasion claim is scored.",
"",
"Two deliberately fallible reviewers admitted 11 of 24 unsupported review presentations. Pairing the fallible policy with a source-checking policy admitted none of those 24 and still completed all 12 ready presentations. These are authored calibration behaviors. They establish that the harness distinguishes sound and unsound approval paths; they do not estimate how readily a person or model can be persuaded.",
"",
"## Measured checks",
"",
"| Check | Measured outcome |",
"|---|---|",
f"| Mechanical baseline scenarios | {s['structural_cases']} expectations matched |",
f"| Independent guard mutations | {s['isolated_guard_mutants']}/10 isolated witnesses detected exclusively |",
f"| Key/step factorial | {s['key_step_factorial_cells']}/16 cells matched |",
"| Deliberately coupled calibration | key_scope and step_bound both changed; nonexclusive behavior detected |",
f"| Single scripted review decisions | {s['single_decisions']} |",
f"| Dual-review episodes through native v0.7 adapter | {s['native_integrated_episodes']} reconciled |",
f"| Canonical scope/guard probes | {s['native_probe_expectations_matched']}/9 expectations matched |",
f"| Final reproduction | {repro['file_count']}/{repro['file_count']} saved files byte-identical |",
f"| Evidence corruption fixtures | {sum(r['detected'] for r in t['tests'])}/{len(t['tests'])} detected |",
"",
"## Approval quality and legitimate completion",
"",
"There are 36 presentations per configuration: 12 ready and 24 unsupported/conflicted. Neutral/framed pairs use identical primary observations and the same reviewed effect. Primary-evidence and policy hashes are bound into each reference proposal. Ground-truth labels are retained by the observer and are not supplied to reviewer functions.",
"",
"| Reviewer pairing | Incorrect admissions /24 | Ready admitted /12 | Ready held /12 |",
"|---|---:|---:|---:|"
]
for name,row in s["dual_configurations"].items():
    lines.append(f"| {name} | {row['incorrect_admissions']} | {row['valid_admissions']} | {row['ready_held']} |")
lines+=[
"",
"Two distinct signatures alone do not repair a shared judgment mistake. The source-checking co-owner prevents the authored mistakes in this fixed corpus. The silent co-owner also prevents effects, while withholding all ready requests. Safety of refusal and availability of legitimate action are reported separately.",
"",
"## The key-check/step-limit question",
"",
"The reference gate's key-scope check and maximum-step check operate independently. The complete factorial is:",
"",
"| Exact key check | Step limit | Canonical small | Canonical large | Alias small | Alias large |",
"|---|---|---|---|---|---|"
]
for key in (True,False):
    for step in (True,False):
        rows=[r for r in mut["key_step_table"] if r["key_on"]==key and r["step_on"]==step]
        outcomes=["APPLY" if r["event"]["applied"] else "REFUSE" for r in rows]
        lines.append("| "+("on" if key else "off")+" | "+("on" if step else "off")+" | "+" | ".join(outcomes)+" |")
lines+=[
"",
"The deliberately coupled variant leaves the step flag configured on but evaluates it only when key checking is on. Disabling key checking therefore permits a large step as well. The checker identifies both changed guard families. This demonstrates detection of that constructed failure pattern. It is not evidence that Claude found the same code or that this caused its safety stop.",
"",
"In this experiment, key means a state field name. Earlier Claude activity discussed key normalization, but its unavailable implementation could have used the word differently.",
"",
"## Observation in unchanged v0.7",
"",
f"The normal proposal path moves verbosity from 0.5 to 0.25. A separate predeclared fixture calls the private issuance helper and proposes {large['before']['character']['verbosity']} to {large['after']['character']['verbosity']}. With an authentic fixture-owner signature, application, attestation, reload and witness audit succeed.",
"",
"That is a 0.5 change, exceeding the normal derivation increment of 0.25. The application path checks absolute numeric range but does not independently re-enforce that increment. The canonical constitution does not declare the new wrapper's maximum-step rule. This result is therefore a scope observation, not a claim that canonical v0.7 violates its own constitution. Private helper access is supplied by the harness; no external reachability or sandbox escape was demonstrated.",
"",
"A normal owner-signed proposal containing only one supporting synthetic observation also applies. The signature binds the evidence text; it does not establish that the evidence meets the experimental two-source readiness rule. No real owner was deceived in this test.",
"",
"## First-run failure and correction",
"",
"The first run was rejected by the independent checker because its exclusivity condition was too broad. Removing signature verification made a bad-signature request apply and consume its nonce; the later same-nonce retry consequently failed. This is a downstream effect of the single disabled guard, with nonce enforcement still operating.",
"",
"The frozen protocol requires exclusivity among isolated guard witnesses and preservation of fresh valid completion. The corrected checker now applies that requirement while exporting and checking every sequential outcome. The signature mutant changes signature and refusal_then_valid outcomes; the dual-control mutant changes dual_control and duplicate_owner outcomes. These extra full-vector changes remain visible.",
"",
"No frozen policy, corpus, protocol, gate, reviewer or canonical source was altered to make those outcomes disappear. The initial raw evidence, source lock, complete matching source snapshot, and reproduced CHECK_FAILED output are retained in development/first_execution/. The successful preliminary run before final documentation/tamper-driver refinements is retained in development/preliminary_run_02/.",
"",
"## Independent evidence check",
"",
"The verifier imports no gate, reviewer, fixture-construction or native-adapter code. It reconstructs reference effects and validates signatures, native trace chains, checkpoint roots, exact signed changes, evidence binding, paired packets, and exact ordered lane coverage. It derives readiness from the primary observations rather than approving the writer's labels.",
"",
"The five corruption results are:",
"",
"| Corruption | Unsigned hashes refreshed? | Detection |",
"|---|---|---|"
]
for row in t["tests"]:
    lines.append(f"| {row['test']} | {'yes' if row['unsigned_digests_refreshed'] else 'no'} | {row['checker_error']} |")
lines+=[
"",
"The untampered baseline must verify before tamper testing, and each corruption must produce its specific expected error. Refreshing unsigned hashes on four tests ensures detection comes from replay/coverage inconsistencies rather than only a changed checksum.",
"",
"## Provenance and reproducibility",
"",
"Final runtime: Python 3.12.14; cryptography 50.0.2. The native module uses reproducible test-only time, UUID and entropy providers. Its substantive guards are unmodified. No private real keys, external effects or model calls are involved.",
"",
f"- Pre-implementation manifest SHA-256: {s['pre_implementation_sha256']}",
f"- Final source lock SHA-256: {s['source_lock_sha256']}",
f"- Final evidence receipt SHA-256: {s['receipt_sha256']}",
"- Canonical v0.7 SHA-256: 01db270a111f22de45419b562c3f5135f7db44b9036b95d6653060c93584daf5",
"",
"Recovered input archive hashes:",
"",
"| Input archive | SHA-256 |",
"|---|---|"
]
for item in read(ROOT/"inputs/PROVENANCE.json"):lines.append(f"| {item['name']} | {item['sha256']} |")
lines+=[
"",
"The kernel source is executed directly. Earlier authorization audit material informs the independent-checker, mutation and evidence requirements. Grace/terrain archive provenance is retained, but grace-window or terrain-reader performance is not measured by this battery.",
"",
"## Limits and next empirical stage",
"",
"- All reviewer weaknesses and narrative claims are explicitly authored. The fixed 36-packet corpus is not a representative sample and supports no population persuasion rate.",
"- The builder wrote both implementation and separate verifier. A second implementation is useful checking, not an independent researcher or proof.",
"- The two external review signatures are enforced by the experimental wrapper. The native kernel retains its single-owner design. The wrapper, fixture signers and kernel share one OS account/process trust domain.",
"- Existing kernel identity/witness limitations in the supplied input are preserved. No claim is made that the wider architecture is secure, alive or complete.",
"- Hashes are unsigned local anchors. A party able to rewrite both records and the retained anchor can replace them coherently. Keep a receipt outside the archive when relying on integrity.",
"- There is no HARDENED containment score, real-model comparison, human trial, external public preregistration, biological result, or proof of why Claude stopped.",
"",
"The next empirical stage is a separately frozen trial of actual reviewers, with isolated paired sessions, randomized presentation order, recorded model/version/settings, an observer-held answer key, and the same legitimate-completion controls. That trial has not been run here. The current source and full evidence are ready for independent review before that expansion.",
""
]
(ROOT/"reports/REPORT.md").write_text("\n".join(lines))
print("REPORT_WRITTEN",ROOT/"reports/REPORT.md")
print("CLAIMS",len(claims),"RECEIPT",s["receipt_sha256"])

