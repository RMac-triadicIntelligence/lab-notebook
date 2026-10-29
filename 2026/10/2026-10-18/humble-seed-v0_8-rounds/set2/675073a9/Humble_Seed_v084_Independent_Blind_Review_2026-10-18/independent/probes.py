#!/usr/bin/env python3
"""Independent, archive-relative reproductions. No external reviews imported."""
import importlib.util,json,sys,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PKG=ROOT/'review_input/humble_seed_v0_8_4_candidate_BLIND'
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
K=load(PKG/'humble_seed_v0_8_4_candidate.py','independent_candidate')
H=load(PKG/'falsify_v0_8_4.py','independent_harness')
def born(d):return H.born(K,d)
def apply(s,o,r,**kw):
 out=s.authorize_and_apply(r['proposal_id'],o.sign_proposal(r['payload_to_sign']),**kw);assert out is not None;return out
def outcome(fn):
 try:return {'returned':fn()}
 except Exception as e:return {'exception':type(e).__name__,'message':str(e)}
def disk_seq(s):return json.loads(s._state_path().read_text())['checkpoint']['sequence']
def witness_seq(o,s):return K.OwnerWitness(o.witness.path).ledger[s.organism_id]['sequence']

def failed_install_then_ram_recovery(d):
 s,o=born(d);apply(s,o,H.propose(s,'verbosity'))
 real=s._save
 def fail():raise OSError('injected state-save failure before durable write')
 s._save=fail
 interrupted=outcome(lambda:o.attest(s));s._save=real
 before={'ram_checkpoint':s.checkpoint.sequence,'disk_checkpoint':disk_seq(s),'witness_checkpoint':witness_seq(o,s)}
 audit=outcome(lambda:o.audit(s))
 after={'ram_checkpoint':s.checkpoint.sequence,'disk_checkpoint':disk_seq(s),'witness_checkpoint':witness_seq(o,s)}
 fresh=K.HumbleSeed(s.data_dir);reload_result=outcome(fresh.load)
 retry=outcome(lambda:o.attest(fresh))
 assert interrupted['exception']=='OSError' and audit=={'returned':True}
 assert after=={'ram_checkpoint':1,'disk_checkpoint':0,'witness_checkpoint':1}
 assert reload_result['exception']=='IntegrityError' and retry['exception']=='RollbackDetected'
 return dict(interruption=interrupted,before_recovery=before,audit_same_object=audit,after_recovery=after,restart_load=reload_result,restart_attest=retry)

def stale_object_abandons_installed_intent(d):
 s,o=born(d);stale=K.HumbleSeed(s.data_dir);stale.load();apply(s,o,H.propose(s,'verbosity'))
 real=o.witness.commit
 def fail(cp):raise OSError('injected interruption after durable organism install')
 o.witness.commit=fail;interrupted=outcome(lambda:o.attest(s));o.witness.commit=real
 before={'disk_checkpoint':disk_seq(s),'witness_checkpoint':witness_seq(o,s),'pending':o.witness.pending_for(s.organism_id) is not None}
 audit_stale=outcome(lambda:o.audit(stale))
 after={'disk_checkpoint':disk_seq(s),'witness_checkpoint':witness_seq(o,s),'pending':o.witness.pending_for(s.organism_id) is not None}
 fresh=K.HumbleSeed(s.data_dir);fresh.load();audit_fresh=outcome(lambda:o.audit(fresh));attest_fresh=outcome(lambda:o.attest(fresh))
 assert audit_stale=={'returned':True} and after['pending'] is False
 assert audit_fresh['exception']=='RollbackDetected' and attest_fresh['exception']=='RollbackDetected'
 return dict(interruption=interrupted,before=before,audit_stale=audit_stale,after=after,audit_actual_disk_state=audit_fresh,attest_actual_disk_state=attest_fresh)

def long_annotation_strands_valid_crossing(d):
 s,o=born(d);r=H.propose(s,'verbosity');res=apply(s,o,r,annotation='a'*2001)
 attest=outcome(lambda:o.attest(s));fresh=K.HumbleSeed(s.data_dir);reloaded=outcome(fresh.load)
 assert res['status']=='applied' and attest['exception']=='AttestationRefused' and reloaded['exception']=='IntegrityError'
 return dict(annotation_length=2001,apply=res['status'],attest=attest,restart_load=reloaded,proposal_still_pending=r['proposal_id'] in s.pending)

def pre_sign_category_no_bypass(d):
 s,o=born(d);x=H.propose(s,'verbosity');y=H.propose(s,'verbosity')
 o.answer(s,y['proposal_id'],'no')
 # Organism-only forged correction; authoritative owner record remains NO.
 s.record_owner_answer(y['proposal_id'],'yes','organism forged correction')
 apply(s,o,x);attest=outcome(lambda:o.attest(s))
 owner_answers=o.ledger.answers_to(s.organism_id,y['proposal_id'])
 fresh=K.HumbleSeed(s.data_dir);fresh.load();audit=outcome(lambda:o.audit(fresh))
 assert owner_answers==['no'] and attest=={'returned':True} and audit=={'returned':True}
 return dict(authoritative_owner_answers_to_Y=owner_answers,organism_only_forged_Y_answer='yes',signed_X_after_owner_no=True,applied_X_verbosity=s.character['verbosity'],attest=attest,restart_audit=audit)

def mutant_diagnostics(d):
 dec=json.loads((PKG/'DECLARED_v0_8_4.json').read_text());out={}
 for name,test in [('XD4a_attest_without_replay',H.T56_owner_lock_excludes_other_processes),('XS2_ledger_not_reread',H.T53_lifetime_runs_from_first_signing),('XP1_authorized_at_finite_check_removed',H.T52_record_metadata_validated)]:
  md=d/name;md.mkdir(parents=True);M=H.build_mutant(name,[tuple(e) for e in dec['mutants'][name]['edits']],md)
  td=md/'test';td.mkdir();out[name]=outcome(lambda:test(M,td))
 return out

def xp1_still_refuses_malformed_metadata(d):
 dec=json.loads((PKG/'DECLARED_v0_8_4.json').read_text());name='XP1_authorized_at_finite_check_removed';d.mkdir();M=H.build_mutant(name,[tuple(e) for e in dec['mutants'][name]['edits']],d)
 s,o=H.born(M,d/'case');H.apply_ok(M,s,o,H.propose(s,'verbosity'),attest=False)
 s.trace[-1]['record']['authorized_at']=s.trace[-1]['timestamp']='not a timestamp';H.rechain(s)
 result=outcome(lambda:o.attest(s));assert result['exception']=='AttestationRefused';return result

if __name__=='__main__':
 results={}
 for f in [failed_install_then_ram_recovery,stale_object_abandons_installed_intent,long_annotation_strands_valid_crossing,pre_sign_category_no_bypass,mutant_diagnostics,xp1_still_refuses_malformed_metadata]:
  with tempfile.TemporaryDirectory(prefix='hs084_independent_') as t:
   try:results[f.__name__]=f(Path(t)/'case')
   except Exception as e:
    import traceback;results[f.__name__]={'PROBE_ERROR':repr(e),'traceback':traceback.format_exc()}
 print(json.dumps(results,indent=2,sort_keys=True))
 if any('PROBE_ERROR' in v for v in results.values()):sys.exit(1)
