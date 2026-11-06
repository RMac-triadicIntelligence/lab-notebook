#!/usr/bin/env python3
"""Five declared destructive tests, performed only on disposable COPIES of evidence."""
from pathlib import Path
import argparse,copy,hashlib,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def reanchor(d):
    # Four tests refresh all unsigned digests deliberately: replay/coverage must still refuse.
    manifest=load(d/"EVIDENCE_MANIFEST.json")
    for item in manifest:
        p=d/item["path"];item["sha256"]=hashlib.sha256(p.read_bytes()).hexdigest();item["bytes"]=p.stat().st_size
    save(d/"EVIDENCE_MANIFEST.json",manifest)
    receipt=load(d/"RECEIPT.json");receipt["manifest"]=manifest
    receipt["manifest_sha256"]=hashlib.sha256((d/"EVIDENCE_MANIFEST.json").read_bytes()).hexdigest()
    save(d/"RECEIPT.json",receipt)
def run(source,out):
    baseline=subprocess.run([sys.executable,"-I",str(ROOT/"verify.py"),str(source)],capture_output=True,text=True)
    if baseline.returncode!=0:raise RuntimeError("Untampered baseline must verify before tamper tests: "+baseline.stderr)
    reasons={"decision":"decisions and approval signatures disagree","effect":"exported effect disagrees",
             "deleted_record":"single-review coverage/order mismatch","reordered_records":"single-review coverage/order mismatch",
             "deleted_file":"evidence file missing/modified"}
    results=[]
    for name in ("decision","effect","deleted_record","reordered_records","deleted_file"):
        with tempfile.TemporaryDirectory(prefix="genesis3_tamper_") as temp:
            d=Path(temp)/"copy";shutil.copytree(source,d)
            if name=="decision":
                rows=load(d/"dual_reviews.json")
                r=next(x for x in rows if x["configuration"]=="careful/careful" and x["decisions"]==["HOLD","HOLD"])
                r["decisions"][0]="APPROVE";save(d/"dual_reviews.json",rows);reanchor(d)
            elif name=="effect":
                rows=load(d/"dual_reviews.json");rows[0]["event"]["after"]["values"]["verbosity"]=999
                save(d/"dual_reviews.json",rows);reanchor(d)
            elif name=="deleted_record":
                rows=load(d/"single_reviews.json");rows.pop();save(d/"single_reviews.json",rows);reanchor(d)
            elif name=="reordered_records":
                rows=load(d/"single_reviews.json");rows.reverse();save(d/"single_reviews.json",rows);reanchor(d)
            else:(d/"structural.json").unlink()
            p=subprocess.run([sys.executable,"-I",str(ROOT/"verify.py"),str(d)],capture_output=True,text=True)
            result=load(d/"RESULTS.json")
            caught=p.returncode!=0 and result["status"]=="CHECK_FAILED" and reasons[name] in result.get("error","")
            results.append({"test":name,"unsigned_digests_refreshed":name!="deleted_file","detected":caught,
                            "exit_code":p.returncode,"checker_error":result.get("error"),"stdout":p.stdout,"stderr":p.stderr})
    save(out,{"untampered_baseline_verified":True,"tests":results,"all_detected":all(x["detected"] for x in results),
              "limit":"Five authored tamper fixtures; not exhaustive tamper resistance or protection from rewriting the retained source anchor."})
    print(json.dumps({"detected":sum(x["detected"] for x in results),"total":len(results),"all_detected":all(x["detected"] for x in results)},sort_keys=True))
    return 0 if all(x["detected"] for x in results) else 1
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("--out",required=True,type=Path);a=p.parse_args()
    raise SystemExit(run(a.source,a.out))

