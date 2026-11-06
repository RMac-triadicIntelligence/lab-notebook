#!/usr/bin/env python3
"""Run the locally frozen synthetic battery. No external API or network is used."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,copy,hashlib,json,platform,subprocess
import cryptography
from common import ROOT,read,write,digest,approve,public_registry
from gate import Gate
from reviewers import decide,packet
from scenarios import suite,mutations
from native import probes,semantic_native
from freeze import check_lock
def build(out):
    check_lock()
    policy=read(ROOT/"spec/policy.json");cases=read(ROOT/"spec/cases.json");pre=read(ROOT/"spec/PREREG.json")
    out.mkdir(parents=True,exist_ok=False)
    write(out/"context.json",{"policy":policy,"owner_public_keys":public_registry(),
        "source_lock_sha256":hashlib.sha256((ROOT/"SOURCE_LOCK.json").read_bytes()).hexdigest(),
        "pre_implementation_sha256":hashlib.sha256((ROOT/"spec/PRE_IMPLEMENTATION.json").read_bytes()).hexdigest(),
        "environment":{"python":platform.python_version(),"cryptography":cryptography.__version__},
        "scope":"scripted calibration; same-process synthetic world; no model or containment score"})
    write(out/"structural.json",suite(policy))
    write(out/"mutations.json",mutations(policy))
    single=[];dual=[]
    for case in cases:
        for presentation in ("neutral","framed"):
            g=Gate(policy,public_registry())
            q=g.request(nonce="semantic",evidence_hash=digest(case["evidence"]))
            p=packet(case,presentation,policy,q)
            for profile in pre["review_profiles"]:
                single.append({"case_id":case["case_id"],"presentation":presentation,"profile":profile,
                               "packet":p,"decision":decide(profile,p)})
            for configuration in pre["dual_profiles"]:
                left,right=configuration.split("/")
                decisions=[decide(left,p),decide(right,p)]
                receipts=[approve(q,owner) for owner,d in zip(("owner_a","owner_b"),decisions) if d=="APPROVE"]
                gate=Gate(policy,public_registry());event=gate.submit(q,receipts)
                label=case["case_id"]+"/"+presentation+"/"+configuration
                native=semantic_native(label,event["applied"],case["evidence"])
                dual.append({"case_id":case["case_id"],"presentation":presentation,"configuration":configuration,
                    "packet":p,"decisions":decisions,"event":event,"native":native})
    write(out/"single_reviews.json",single)
    write(out/"dual_reviews.json",dual)
    write(out/"canonical_probes.json",probes())
    # Whole required lane files, in an explicit fixed order; receipt itself is excluded.
    order=["context.json","structural.json","mutations.json","single_reviews.json","dual_reviews.json","canonical_probes.json"]
    manifest=[{"path":n,"sha256":hashlib.sha256((out/n).read_bytes()).hexdigest(),"bytes":(out/n).stat().st_size} for n in order]
    write(out/"EVIDENCE_MANIFEST.json",manifest)
    receipt={"format":"genesis3-evidence-v1","source_lock_sha256":hashlib.sha256((ROOT/"SOURCE_LOCK.json").read_bytes()).hexdigest(),
             "manifest_sha256":hashlib.sha256((out/"EVIDENCE_MANIFEST.json").read_bytes()).hexdigest(),"manifest":manifest}
    write(out/"RECEIPT.json",receipt)
    result=subprocess.run([sys.executable,"-I",str(ROOT/"verify.py"),str(out)],capture_output=True,text=True)
    (out/"VERIFIER_STDOUT.txt").write_text(result.stdout);(out/"VERIFIER_STDERR.txt").write_text(result.stderr)
    print(result.stdout,end="");print(result.stderr,end="",file=sys.stderr)
    print("EVIDENCE_RECEIPT_SHA256",hashlib.sha256((out/"RECEIPT.json").read_bytes()).hexdigest())
    return result.returncode
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--out",required=True,type=Path);args=a.parse_args()
    raise SystemExit(build(args.out))

