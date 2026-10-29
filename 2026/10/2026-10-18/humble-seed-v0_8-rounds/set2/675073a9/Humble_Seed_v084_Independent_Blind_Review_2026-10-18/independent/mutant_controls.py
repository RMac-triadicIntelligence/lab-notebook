#!/usr/bin/env python3
import importlib.util,json,sys,tempfile,time,subprocess
from pathlib import Path
p=Path(__file__).resolve().parent/'probes.py';spec=importlib.util.spec_from_file_location('probes',p);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
H,K=P.H,P.K
D=json.loads((P.PKG/'DECLARED_v0_8_4.json').read_text());out={}
with tempfile.TemporaryDirectory() as t:
 d=Path(t);name='XD4a_attest_without_replay';M=H.build_mutant(name,[tuple(e) for e in D['mutants'][name]['edits']],d)
 s,o=H.born(M,d/'case');H.apply_ok(M,s,o,H.propose(s,'verbosity'),attest=False);seen=[];real=o.witness.begin
 def begin(cp,sig):
  seen.append(subprocess.run([sys.executable,'-I','-c',H.LOCK_PROBE,str(o.lock_path)],capture_output=True,text=True,check=True).stdout.strip());return real(cp,sig)
 o.witness.begin=begin;assert o.attest(s);assert seen==['locked'];out['XD4a_lock_at_witness_begin']=seen
for name in ['candidate','XS2_ledger_not_reread']:
 with tempfile.TemporaryDirectory() as t:
  d=Path(t);M=K if name=='candidate' else H.build_mutant(name,[tuple(e) for e in D['mutants'][name]['edits']],d)
  s,o=H.born(M,d/'case',reading_ttl_seconds=10.0);b=H.reopen(M,o,d/'case');r=H.propose(s,'verbosity');at=time.time()
  o.clock=lambda:at;sig=o.sign_proposal(r['payload_to_sign']);b.clock=lambda:at+11;b.sign_proposal(r['payload_to_sign'])
  assert s.authorize_and_apply(r['proposal_id'],sig) is not None
  fresh=H.reopen(M,o,d/'case');fresh.clock=lambda:at+11;out[name+'_fresh_lifetime_check']=P.outcome(lambda:fresh.attest(s))
assert out['candidate_fresh_lifetime_check']['exception']=='AttestationRefused'
assert out['XS2_ledger_not_reread_fresh_lifetime_check']=={'returned':True}
print(json.dumps(out,indent=2,sort_keys=True))
