#!/usr/bin/env python3
import importlib.util,sys,json,tempfile
from pathlib import Path
p=Path(__file__).resolve().parent/'probes.py';spec=importlib.util.spec_from_file_location('probes',p);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
K,H=P.K,P.H
results={}
for mode in ['no_forgery','signed_before_no','signed_after_no','direct_no_signed_after']:
 with tempfile.TemporaryDirectory() as t:
  s,o=P.born(Path(t));x=H.propose(s,'verbosity');y=H.propose(s,'verbosity')
  if mode=='signed_before_no':sig=o.sign_proposal(x['payload_to_sign'])
  target=x if mode=='direct_no_signed_after' else y
  o.answer(s,target['proposal_id'],'no')
  if mode!='no_forgery':s.record_owner_answer(target['proposal_id'],'yes','organism-only forged answer')
  if mode!='signed_before_no':sig=o.sign_proposal(x['payload_to_sign'])
  res=s.authorize_and_apply(x['proposal_id'],sig)
  att=P.outcome(lambda:o.attest(s)) if res else {'not_attempted':'organism held reading'}
  results[mode]={'applied':res is not None,'attest':att}
with tempfile.TemporaryDirectory() as t:
 s,o=P.born(Path(t));P.apply(s,o,H.propose(s,'verbosity'),annotation='a'*2000)
 results['annotation_2000_control']={'attest':P.outcome(lambda:o.attest(s))}
assert results['no_forgery']['applied'] is False
assert results['signed_before_no']['attest']['exception']=='AttestationRefused'
assert results['signed_after_no']['attest']=={'returned':True}
assert results['direct_no_signed_after']['attest']['exception']=='AttestationRefused'
assert results['annotation_2000_control']['attest']=={'returned':True}
print(json.dumps(results,indent=2,sort_keys=True))
