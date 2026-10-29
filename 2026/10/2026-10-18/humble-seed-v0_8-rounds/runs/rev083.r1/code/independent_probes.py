#!/usr/bin/env python3
"""Independent v0.8.3 probes. No edits to the candidate or owner storage.
Usage: python3 -I independent_probes.py CANDIDATE.py OUTPUT_DIRECTORY
The optional metadata mutation probe edits only unattested organism history.
All time shifts and fault injections are explicit; files live under TemporaryDirectory.
"""
import copy, hashlib, importlib.util, json, pathlib, sys, tempfile, traceback
from collections import Counter
P=pathlib.Path(sys.argv[1]).resolve(); OUT=pathlib.Path(sys.argv[2]).resolve(); OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('independent_kernel',P)
K=importlib.util.module_from_spec(spec);sys.modules[spec.name]=K;spec.loader.exec_module(K)

def born(d, ttl=604800):
    s=K.HumbleSeed(d/'org');_,pem,_=s.hatch(reading_ttl_seconds=ttl)
    o=K.OwnerTool(pem,K.OwnerWitness(d/'witness.json'));assert o.attest(s)
    return s,o

def reopen(o):
    return K.OwnerTool(o._pem,K.OwnerWitness(o.witness.path))

def proposal(s,cat='verbosity'):
    r=s.dwell_or_propose(cat,'evt','I always prefer shorter answers');assert r['status']=='proposal';return r

def sign(o,r):return o.sign_proposal(r['payload_to_sign'])
def apply(s,r,sig):
    r=s.authorize_and_apply(r['proposal_id'],sig);assert r is not None;return r

def loaded(s):
    x=K.HumbleSeed(s.data_dir);x.load();return x

def refusal(fn):
    try:r=fn()
    except (K.AttestationRefused,K.RollbackDetected,K.IntegrityError) as e:return type(e).__name__+': '+str(e)
    raise AssertionError('expected refusal, accepted '+str(r))

def rechain(s):
    prev='0'*64
    for e in s.trace:
        e['prev_hash']=prev;e.pop('entry_hash',None)
        e['entry_hash']=K._sha256(K._canonical_json(e));prev=e['entry_hash']
    s._trace_head=prev;s._save()

def fresh_owner_control(d):
    s,o=born(d);r=proposal(s);sig=sign(o,r);o2=reopen(o)
    o2.answer(s,r['proposal_id'],'no');s.record_owner_answer(r['proposal_id'],'yes','forged organism-only yes')
    apply(s,r,sig)
    why=refusal(lambda:o2.attest(s))
    assert "owner's position" in why
    return {'refused':why,'witness_sequence':o2.witness.ledger[s.organism_id]['sequence']}

def stale_owner_veto_bypass(d):
    s,o=born(d);r=proposal(s);sig=sign(o,r);o2=reopen(o)
    o2.answer(s,r['proposal_id'],'no','real answer in independent owner session')
    s.record_owner_answer(r['proposal_id'],'yes','forged organism-only yes')
    apply(s,r,sig);assert o.attest(s)
    fresh=reopen(o);f=loaded(s)
    answers=fresh.ledger.answers_to(s.organism_id,r['proposal_id']);assert answers[-1]=='no'
    assert fresh.audit(f)
    return {'owner_files_edited_by_probe':False,'durable_owner_answers':answers,
            'attestation_accepted':True,'fresh_reload_and_audit':True,'verbosity':f.character['verbosity'],
            'witness_sequence':fresh.witness.ledger[s.organism_id]['sequence']}

def stale_owner_erases_signature(d):
    s,o=born(d);r=proposal(s);o2=reopen(o);sig=sign(o,r)
    payload_hash=K._sha256(r['payload_to_sign'])
    assert reopen(o).ledger.signed(s.organism_id,payload_hash) is not None
    o2.answer(s,r['proposal_id'],'yes','ordinary yes from another open session')
    fresh=reopen(o);missing=fresh.ledger.signed(s.organism_id,payload_hash) is None;assert missing
    apply(s,r,sig);why=refusal(lambda:fresh.attest(s))
    assert 'not signed through this owner tool' in why
    return {'owner_files_edited_by_probe':False,'signature_lost_after_ordinary_yes':missing,'attestation':why}

def stale_witness_fork(d):
    s,o=born(d);r1=proposal(s,'verbosity');r2=proposal(s,'formality')
    sig1=sign(o,r1);sig2=sign(o,r2);o2=reopen(o)
    branch1=loaded(s);branch2=loaded(s)
    apply(branch1,r1,sig1);assert o.attest(branch1);cp1=copy.deepcopy(branch1.checkpoint)
    apply(branch2,r2,sig2);assert o2.attest(branch2);cp2=branch2.checkpoint
    assert cp1.sequence==cp2.sequence==1
    assert cp1.prev_checkpoint_hash==cp2.prev_checkpoint_hash
    h1=K.OwnerWitness._checkpoint_hash(cp1);h2=K.OwnerWitness._checkpoint_hash(cp2);assert h1!=h2
    branch1.verify();branch2.verify()
    assert o.audit(branch1) and o2.audit(branch2)
    fresh=reopen(o2);why=refusal(lambda:fresh.audit(branch1))
    assert fresh.audit(branch2)
    return {'owner_files_edited_by_probe':False,'two_attestations_accepted':True,'both_checkpoint_sequences':1,
            'same_parent':True,'different_checkpoint_hashes':True,'both_sessions_audit_own_branch':True,
            'fresh_session_refuses_first_branch':why,'branch1_character':branch1.character,'branch2_character':branch2.character}

def forged_record_metadata(d):
    s,o=born(d);r=proposal(s);apply(s,r,sign(o,r))
    rec=s.trace[-1]['record'];before={'authorized_at':rec['authorized_at'],'note':rec['note'],'event_timestamp':s.trace[-1]['timestamp']}
    rec['authorized_at']='not a timestamp';rec['note']={'forged':'owner said yes; real owner note was empty'}
    s.trace[-1]['timestamp']=-123456789.0
    rechain(s);assert o.attest(s);f=loaded(s);assert o.audit(f)
    final=[e for e in f.trace if e['event']=='authorized_mutation'][-1]
    return {'original_note_was_empty':before['note']=='','original_authorized_at_was_numeric':isinstance(before['authorized_at'],(int,float)),
            'attested_record_authorized_at':final['record']['authorized_at'],'attested_note':final['record']['note'],
            'attested_event_timestamp':final['timestamp'],'fresh_reload_and_audit':True,
            'character_was_not_forged':f.character['verbosity']==0.25}

def ordinary_corrected_answer(d):
    s,o=born(d);r=proposal(s);sig=sign(o,r)
    o.answer(s,r['proposal_id'],'no');o.answer(s,r['proposal_id'],'yes');apply(s,r,sig)
    assert o.attest(s);f=loaded(s);assert reopen(o).audit(f)
    return {'corrected_answer_applies_attests_reloads':True}

def signing_does_not_refresh_lifetime(d):
    s,o=born(d,ttl=10);r=proposal(s);t0=s.pending[r['proposal_id']].timestamp;o.clock=lambda:t0;sig=sign(o,r)
    o.clock=lambda:t0+11.;assert sign(o,r)==sig
    # Simulates an organism retaining a timely local clock; owner alone must object.
    apply(s,r,sig);why=refusal(lambda:o.attest(s));assert 'past its lifetime' in why
    return {'same_instance_resigning_does_not_extend':True,'attestation':why}

def stale_signer_refreshes_lifetime(d):
    s,o=born(d,ttl=10);r=proposal(s);o2=reopen(o)
    t0=s.pending[r['proposal_id']].timestamp;o.clock=lambda:t0;sig=sign(o,r);o2.clock=lambda:t0+11.;assert sign(o2,r)==sig
    apply(s,r,sig);assert o2.attest(s)
    entry=reopen(o2).ledger.signed(s.organism_id,K._sha256(r['payload_to_sign']))
    assert entry['signed_at']==t0+11.
    return {'clock_injection':'owner1=t0 then owner2=t0+11; ttl=10; organism remains at issuance time',
            'first_signing_time_shift_seconds':entry['signed_at']-t0,'attestation_accepted':True}

def witness_write_failure(d):
    s,o=born(d);r=proposal(s);apply(s,r,sign(o,r))
    original_persist=o.witness._persist
    def fail():raise OSError('injected witness write failure')
    o.witness._persist=fail
    try:o.attest(s)
    except OSError as e:error=str(e)
    else:raise AssertionError('injected failure did not fire')
    o.witness._persist=original_persist
    fresh=reopen(o);f=loaded(s)
    audit=refusal(lambda:fresh.audit(f));retry=refusal(lambda:fresh.attest(f))
    assert f.checkpoint.sequence==1 and fresh.witness.ledger[f.organism_id]['sequence']==0
    return {'fault_injection':error,'organism_checkpoint':1,'durable_witness_checkpoint':0,
            'fresh_audit':audit,'ordinary_attest_retry':retry,
            'scope':'crash consistency / availability, not unauthorized character change'}

cases=[fresh_owner_control,stale_owner_veto_bypass,stale_owner_erases_signature,stale_witness_fork,
       forged_record_metadata,ordinary_corrected_answer,signing_does_not_refresh_lifetime,
       stale_signer_refreshes_lifetime,witness_write_failure]
results={}
for fn in cases:
    with tempfile.TemporaryDirectory(prefix='independent083_') as td:
        try:
            detail=fn(pathlib.Path(td));results[fn.__name__]={'status':'OBSERVATION_CONFIRMED','detail':detail}
        except Exception:
            results[fn.__name__]={'status':'ERROR','traceback':traceback.format_exc()}
    print(fn.__name__+': '+json.dumps(results[fn.__name__],sort_keys=True))
(OUT/'independent_probe_results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
print('SUMMARY '+json.dumps(dict(Counter(r['status'] for r in results.values())),sort_keys=True))
sys.exit(1 if any(r['status']=='ERROR' for r in results.values()) else 0)
