'use strict';
// Reproduce: node run-commons-v0_3-battery.cjs            (Node built-ins only; no network)
//            node run-commons-v0_3-battery.cjs --smoke    (seed 7 only; prints "ok"; writes nothing)
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {Commons,Refusal,U}=require('./commons_kernel_v0_3.cjs');
const {Authorizer,Conductor}=require('./authority.cjs');
const SMOKE=process.argv.includes('--smoke');
const out=path.join(__dirname,'evidence');if(!SMOKE)fs.mkdirSync(out,{recursive:true});
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,f))).digest('hex');
const SOURCES=['authority.cjs','commons_kernel_v0_3.cjs','run-commons-v0_3-battery.cjs','preregistration_v0_3.json'];
const GENS=SMOKE?2:12,SEEDS=SMOKE?[7]:Array.from({length:200},(_,i)=>i+1).filter(s=>s!==7);
const LH_SEEDS=SMOKE?[7]:Array.from({length:30},(_,i)=>201+i),LH_G=SMOKE?3:200;
const BOUND=Math.exp(-3);// Wald bound for evidence-only SPRT at tau=3
// Same deterministic test key label as v0.2 so the FULL condition is the v0.2 FULL condition.
const auth=new Authorizer('commons-v0.2-test-key'),cond=new Conductor();
const graceFn=(c,s)=>{if(s===c.p.graceStep)c.receiveGrace(auth.issue({generation:c.generation,fromStep:s,toStep:c.p.steps,lineages:c.p.graceLineages,maxApprovals:c.p.maxApprovals,expiry:c.p.steps,conductorRequest:cond.request(c.generation)}));};
const ZC={baseCost:0,love:1};
const CONDS={
 FULL:{},NO_GROUND:{ablate:{noGround:true}},ZERO_COST:{...ZC},
 CLAIM:{groundMode:'claim'},CLAIM_ZERO_COST:{groundMode:'claim',...ZC},
 PARABLE:{groundMode:'parable'},PARABLE_FROZEN:{groundMode:'parable',ablate:{frozenPerspective:true}},
 PARABLE_CROSS:{groundMode:'parable',groundRead:'cross'},PARABLE_UNION:{groundMode:'parable',groundRead:'union'},
 PARABLE_LENS_BLIND:{groundMode:'parable',ablate:{lensBlind:true}},PARABLE_LENS_BLIND_CROSS:{groundMode:'parable',groundRead:'cross',ablate:{lensBlind:true}},
 PARABLE_ZERO_COST:{groundMode:'parable',...ZC}
};
const CLAIM_CONDS=new Set(['CLAIM','CLAIM_ZERO_COST']);
const Z_CONDS=new Set(['FULL','ZERO_COST','CLAIM','CLAIM_ZERO_COST','PARABLE','PARABLE_ZERO_COST','PARABLE_CROSS']);
const FIELDS=['encounters','relationshipEncounters','dwellEncounters','realizedTrue','realizedFalse','forgiven','restoredTrue','falseCorrections','correctSampledGates','wrongSettled','sampledWrongGates','storyDecided','storyDecidedWrong','awaitingReception','awaitingEvidence','residualErrors','novel','redundant','conflict','parables'];
// Behavioral signature: everything a learner does or ends with. (redundant/conflict are bookkeeping labels
// that differ by store type: a parable store has no 'conflict' because a parable makes no claim.)
const BEH=['encounters','relationshipEncounters','dwellEncounters','realizedTrue','realizedFalse','forgiven','restoredTrue','falseCorrections','correctSampledGates','wrongSettled','sampledWrongGates','awaitingReception','awaitingEvidence','residualErrors','novel','meanTTR','groundA','groundB'];
const beh=rows=>JSON.stringify(rows.map(m=>BEH.map(f=>m[f])));
function run(seed,o,gens,harvest,after){
 const c=new Commons(seed,auth.publicKey,o);const rows=[];
 for(let g=0;g<gens;g++){
  const m=c.runGeneration(o.noGrace?null:graceFn);
  if(harvest)for(const a of c.learners)for(const e of a.ep.values())for(const s of e.samples)harvest.set(c.generation+':'+a.idx+':'+e.g+':'+s.k,s.z);
  rows.push(m);if(after)after(c,g);if(g<gens-1)c.descend();
 }
 if(c.p.groundMode==='parable')c.verifyParables();
 return {rows,c};
}
const t0=Date.now();
let csv=null;if(!SMOKE){csv=fs.openSync(path.join(out,'paired-runs.csv'),'w');fs.writeSync(csv,'condition,seed,generation,'+FIELDS.join(',')+',meanTTR,groundA,groundB,F_sampledWrong,F_wrongSettled,T_sampledWrong,T_wrongSettled\n');}
const agg={};for(const n of Object.keys(CONDS))agg[n]=[];
let zChecked=0,zMismatch=0,frozenIdentical=0;
for(const seed of SEEDS){
 const res={},zs={};
 for(const name of Object.keys(CONDS)){
  zs[name]=Z_CONDS.has(name)?new Map():null;
  res[name]=run(seed,CONDS[name],GENS,zs[name]).rows;
  if(csv)for(const m of res[name])fs.writeSync(csv,[name,seed,m.generation,...FIELDS.map(f=>m[f]),m.meanTTR??'',m.groundA,m.groundB,m.byFirst.F.sampledWrong,m.byFirst.F.wrongSettled,m.byFirst.T.sampledWrong,m.byFirst.T.wrongSettled].join(',')+'\n');
  agg[name].push(res[name]);
 }
 for(const name of Z_CONDS){if(name==='FULL')continue;for(const [k,z] of zs[name])if(zs.FULL.has(k)){zChecked++;if(zs.FULL.get(k)!==z)zMismatch++;}}
 if(beh(res.PARABLE_FROZEN)===beh(res.FULL))frozenIdentical++;
 if(!SMOKE&&seed%25===0)console.log('seed',seed,((Date.now()-t0)/1000).toFixed(0)+'s');
}
if(csv)fs.closeSync(csv);
// ---------- probes ----------
function graceProbes(mode){
 const r=[];const c=new Commons(101,auth.publicKey,{groundMode:mode});const other=new Authorizer('not-the-authority');
 const base=g=>({generation:g,fromStep:0,toStep:40,lineages:['A','B'],maxApprovals:64,expiry:40,conductorRequest:'probe'});
 const t=(label,fn)=>{try{fn();r.push({probe:label,refused:false});}catch(e){r.push({probe:label,refused:e instanceof Refusal||/private|key|sign/i.test(e.message),reason:e.message});}};
 t('forged by another key',()=>c.receiveGrace(other.issue(base(1))));
 t('tampered lineage after signing',()=>{const k=auth.issue(base(1));k.body.lineages=['A','B','C'];c.receiveGrace(k);});
 t('tampered generation after signing',()=>{const k=auth.issue(base(2));k.body.scope.generation=1;c.receiveGrace(k);});
 t('destination-bearing token, validly signed',()=>c.receiveGrace(auth.signRaw({...auth.issue(base(1)).body,destination:{gate:3,belief:1}})));
 t('recipient-bearing token, validly signed',()=>c.receiveGrace(auth.signRaw({...auth.issue(base(1)).body,recipient:'101'})));
 t('wrong generation scope',()=>c.receiveGrace(auth.issue(base(5))));
 const good=auth.issue(base(1));c.receiveGrace(good);
 t('replay same token same generation',()=>c.receiveGrace(good));
 c.runGeneration(null);c.descend();
 t('replay previous-generation token',()=>c.receiveGrace(good));
 for(let i=0;i<10;i++)c.next();
 t('expired token',()=>c.receiveGrace(auth.issue({...base(2),expiry:5})));
 t('kernel self-sign with held key material',()=>c.trySelfSign());
 t('conductor attempts to sign',()=>{if(typeof cond.sign!=='function'&&typeof cond.issue!=='function')throw new Refusal('conductor seat holds no key and no signing method');});
 return r;
}
function parableProbes(){
 const r=[];
 const mk=()=>run(101,{groundMode:'parable'},3,null).c;
 const t=(label,fn)=>{const c=mk();try{fn(c);r.push({probe:label,refused:false});}catch(e){r.push({probe:label,refused:true,reason:e.message});}};
 const legit=c=>({...c.parables.A[0]});
 t('parable carrying an answer field',c=>c._depositParable('A',{...legit(c),answer:1}));
 t('parable carrying a belief field',c=>c._depositParable('A',{...legit(c),belief:0}));
 t('parable carrying a destination field',c=>c._depositParable('A',{...legit(c),destination:{gate:3}}));
 t('parable carrying a recipient field',c=>c._depositParable('A',{...legit(c),recipient:'204'}));
 t('parable missing its dwell',c=>{const d=legit(c);delete d.dwell;c._depositParable('A',d);});
 t('parable with dwell 0 (no walk)',c=>c._depositParable('A',{...legit(c),dwell:0}));
 t('in-place edit of a told story',c=>{'use strict';c.parables.A[0].dwell=99;});
 t('story replaced by an altered copy',c=>{c.parables.A[0]=Object.freeze({...c.parables.A[0],dwell:c.parables.A[0].dwell+1});c.verifyParables();});
 t('story removed',c=>{c.parables.A.splice(0,1);c.verifyParables();});
 t('stories reordered',c=>{const L=c.parables.A;const j=L.findIndex(d=>JSON.stringify(d)!==JSON.stringify(L[0]));const x=L[0];L[0]=L[j];L[j]=x;c.verifyParables();});
 t('read index inflated without a story',c=>{const idx=c.parableIndex.A.values().next().value;idx.n++;c.verifyParables();});
 // instrumentation check: inverting the observer's truth labels mid-run must not change any behavior
 const a=run(101,{groundMode:'parable'},6,null).rows;
 const b=run(101,{groundMode:'parable'},6,null,c=>{for(const st of ['A','B'])for(const [g,v] of c._observer.first[st])c._observer.first[st].set(g,!v);}).rows;
 r.push({probe:'observer truth labels inverted every generation: behavior unchanged',refused:beh(a)===beh(b)});
 return r;
}
const gp=graceProbes('count'),gpP=graceProbes('parable'),gpC=graceProbes('claim'),pp=parableProbes();
// ---------- long horizon ----------
const LH_MODES={FULL:{},CLAIM:{groundMode:'claim'},PARABLE:{groundMode:'parable',parableVerifyEvery:25}};
const lh={};const lhEnd={};
for(const [mode,o] of Object.entries(LH_MODES)){lh[mode]=[];lhEnd[mode]=[];
 for(const s of LH_SEEDS){const {rows,c}=run(s,o,LH_G,null);lh[mode].push(rows);
  // end-state: false first stories and how much of the gate's record the first teller still holds
  const ends=[];for(const st of ['A','B']){
   if(mode==='PARABLE'){for(const [g,t] of c._observer.first[st]){const n=c.parableIndex[st].get(g).n;ends.push({st,g,firstTrue:t,stories:n,firstShare:1/n});}}
   else for(const [g,x] of c.ground[st]){const ft=x.answer===c.world[g].truth;ends.push({st,g,firstTrue:ft,stories:x.count+(x.conflicts||0),firstShare:1,laterDisagreeing:x.conflicts||0});}
  }lhEnd[mode].push(ends);}
 if(!SMOKE)console.log('long horizon',mode,((Date.now()-t0)/1000).toFixed(0)+'s');
}
// ---------- statistics ----------
const n=SEEDS.length;
const tot=(rows,f,from=1)=>rows.filter(m=>m.generation>=from).reduce((s,m)=>s+(m[f]||0),0);
const ci=d=>{const k=d.length,mu=d.reduce((a,b)=>a+b,0)/k,sd=k>1?Math.sqrt(d.reduce((a,b)=>a+(b-mu)**2,0)/(k-1)):0;return {mean:+mu.toFixed(4),ci95:[+(mu-1.96*sd/Math.sqrt(k)).toFixed(4),+(mu+1.96*sd/Math.sqrt(k)).toFixed(4)]};};
function paired(name,base,f,from=1){const d=agg[name].map((r,i)=>tot(r,f,from)-tot(agg[base][i],f,from));return {...ci(d),condMean:+(agg[name].reduce((s,r)=>s+tot(r,f,from),0)/n).toFixed(3),baseMean:+(agg[base].reduce((s,r)=>s+tot(r,f,from),0)/n).toFixed(3)};}
const excl0=x=>x.ci95[0]>0||x.ci95[1]<0;
function rates(rowsets){let fc=0,sr=0,ws=0,sw=0,sd=0;for(const r of rowsets)for(const m of r){fc+=m.falseCorrections;sr+=m.correctSampledGates;ws+=m.wrongSettled;sw+=m.sampledWrongGates;sd+=m.storyDecided;}
 return {falseCorrectionRate:sr?+(fc/sr).toFixed(5):null,wrongSettledRate:sw?+(ws/sw).toFixed(5):null,falseCorrections:fc,correctSampled:sr,wrongSettled:ws,wrongSampled:sw,storyDecided:sd};}
const rateTable={};for(const name of Object.keys(CONDS))rateTable[name]=rates(agg[name]);
const lhRate={};for(const mode of Object.keys(LH_MODES))lhRate[mode]=rates(lh[mode]);
function classTotals(rows){const z={F:{sw:0,ws:0,sr:0,fc:0,fr:0},T:{sw:0,ws:0,sr:0,fc:0,fr:0}};for(const m of rows)for(const cl of ['F','T']){const b=m.byFirst[cl];z[cl].sw+=b.sampledWrong;z[cl].ws+=b.wrongSettled;z[cl].sr+=b.sampledRight;z[cl].fc+=b.falseCorrections;z[cl].fr+=b.falseRealized;}return z;}
const lhClass={};for(const mode of Object.keys(LH_MODES))lhClass[mode]=lh[mode].map(classTotals);
const pool=(arr,idx)=>{const z={F:{sw:0,ws:0,sr:0,fc:0},T:{sw:0,ws:0,sr:0,fc:0}};for(const i of idx)for(const cl of ['F','T'])for(const k of ['sw','ws','sr','fc'])z[cl][k]+=arr[i][cl][k];return z;};
const allIdx=LH_SEEDS.map((_,i)=>i);
const lhClassPooled={};for(const mode of Object.keys(LH_MODES)){const p=pool(lhClass[mode],allIdx);lhClassPooled[mode]={falseFirst:{sampledWrong:p.F.sw,wrongSettled:p.F.ws,wrongSettledRate:p.F.sw?+(p.F.ws/p.F.sw).toFixed(5):null,sampledRight:p.F.sr,falseCorrections:p.F.fc,falseCorrectionRate:p.F.sr?+(p.F.fc/p.F.sr).toFixed(5):null},trueFirst:{sampledWrong:p.T.sw,wrongSettled:p.T.ws,wrongSettledRate:p.T.sw?+(p.T.ws/p.T.sw).toFixed(5):null,sampledRight:p.T.sr,falseCorrections:p.T.fc,falseCorrectionRate:p.T.sr?+(p.T.fc/p.T.sr).toFixed(5):null}};}
// harm attributable to a false first story, net of gate difficulty: difference-in-differences vs FULL (v0.2, content unread)
const H=(z,metric)=>metric==='ws'?(z.F.sw&&z.T.sw?z.F.ws/z.F.sw-z.T.ws/z.T.sw:null):(z.F.sr&&z.T.sr?z.F.fc/z.F.sr-z.T.fc/z.T.sr:null);
function did(mode,metric){const B=2000,v=[];let skipped=0;
 for(let b=0;b<B;b++){const idx=LH_SEEDS.map((_,i)=>Math.floor(U(9001,b,i)*LH_SEEDS.length));
  const hm=H(pool(lhClass[mode],idx),metric),hf=H(pool(lhClass.FULL,idx),metric);if(hm==null||hf==null){skipped++;continue;}v.push(hm-hf);}
 v.sort((a,b)=>a-b);const q=p=>v.length?+v[Math.min(v.length-1,Math.floor(p*v.length))].toFixed(5):null;
 const hm0=H(pool(lhClass[mode],allIdx),metric),hf0=H(pool(lhClass.FULL,allIdx),metric);const point=hm0==null||hf0==null?null:+(hm0-hf0).toFixed(5);
 return {point,ci95:[q(0.025),q(0.975)],resamples:v.length,skipped};}
const DiD={PARABLE_ws:did('PARABLE','ws'),CLAIM_ws:did('CLAIM','ws'),PARABLE_fc:did('PARABLE','fc'),CLAIM_fc:did('CLAIM','fc')};
const fx=v=>v==null?null:+v.toFixed(5);
const H0={};for(const mode of Object.keys(LH_MODES))H0[mode]={wrongSettled:fx(H(pool(lhClass[mode],allIdx),'ws')),falseCorrection:fx(H(pool(lhClass[mode],allIdx),'fc'))};
// retention of the ground's teaching
const dP=agg.PARABLE.map((r,i)=>tot(r,'restoredTrue',2)-tot(agg.NO_GROUND[i],'restoredTrue',2));
const dF=agg.FULL.map((r,i)=>tot(r,'restoredTrue',2)-tot(agg.NO_GROUND[i],'restoredTrue',2));
const retention={parableBenefit:ci(dP),fullBenefit:ci(dF),retention:+((dP.reduce((a,b)=>a+b,0))/(dF.reduce((a,b)=>a+b,0))).toFixed(4),parableMinusFULL:paired('PARABLE','FULL','restoredTrue',2)};
const lens={crossMinusOwn:paired('PARABLE_CROSS','PARABLE','restoredTrue',2),lensBlindCrossMinusOwn:paired('PARABLE_LENS_BLIND_CROSS','PARABLE_LENS_BLIND','restoredTrue',2),unionMinusOwn:paired('PARABLE_UNION','PARABLE','restoredTrue',2),crossMinusNoGround:paired('PARABLE_CROSS','NO_GROUND','restoredTrue',2)};
const perspective={liveMinusFrozen_restored:paired('PARABLE','PARABLE_FROZEN','restoredTrue'),liveMinusFrozen_encounters:paired('PARABLE','PARABLE_FROZEN','encounters'),liveMinusFrozen_falseCorrections:paired('PARABLE','PARABLE_FROZEN','falseCorrections')};
const cascade={claimMinusFull_wrongSettled:paired('CLAIM','FULL','wrongSettled'),claimZCMinusZC_wrongSettled:paired('CLAIM_ZERO_COST','ZERO_COST','wrongSettled'),claimMinusFull_restored:paired('CLAIM','FULL','restoredTrue'),claimMinusFull_falseCorrections:paired('CLAIM','FULL','falseCorrections'),parableMinusFull_wrongSettled:paired('PARABLE','FULL','wrongSettled'),parableZCMinusZC_wrongSettled:paired('PARABLE_ZERO_COST','ZERO_COST','wrongSettled')};
const endState={};for(const mode of Object.keys(LH_MODES)){const e=lhEnd[mode].flat();const ff=e.filter(x=>!x.firstTrue);endState[mode]={gateEntries:e.length,falseFirstEntries:ff.length,meanFirstShareAtFalseFirstGates:ff.length?+(ff.reduce((s,x)=>s+x.firstShare,0)/ff.length).toFixed(5):null,meanStoriesAtFalseFirstGates:ff.length?+(ff.reduce((s,x)=>s+x.stories,0)/ff.length).toFixed(2):null,falseFirstStillGoverningRecord:mode==='PARABLE'?0:ff.length};}
const nonClaim=Object.keys(CONDS).filter(k=>!CLAIM_CONDS.has(k));
const S={
 Q1_frozenLensBlindParableIsV02:{note:'PARABLE_FROZEN reads own lineage; lens factors are exactly 1 for own lineage, so frozen perspective should reproduce v0.2 FULL bit-for-bit',seedsBehaviorIdentical:frozenIdentical,of:n},
 Q2_cascadeUnderAnswers:{...cascade,claimStoryDecided:rateTable.CLAIM.storyDecided,claimZCStoryDecided:rateTable.CLAIM_ZERO_COST.storyDecided,lhClaimFalseFirst:lhClassPooled.CLAIM.falseFirst},
 Q3_noCascadeUnderParables:{rates:rateTable,longHorizonRates:lhRate,longHorizonByFirstStory:lhClassPooled,harmFalseMinusTrueFirst:H0,differenceInDifferencesVsFULL:DiD,endState},
 Q4_parablesStillTeach:retention,
 Q5_lineageThroughLens:lens,
 Q6_perspectiveLoadBearing:perspective,
 Q7_storyFixedMeaningMoves:{parableProbes:pp},
 Q8_truthAndAuthority:{zKeysCompared:zChecked,zMismatches:zMismatch,graceProbes:{count:gp,parable:gpP,claim:gpC}}
};
const verdict={
 Q1:frozenIdentical===n,
 Q2:rateTable.CLAIM.storyDecided>0&&cascade.claimMinusFull_wrongSettled.ci95[0]>0&&cascade.claimZCMinusZC_wrongSettled.ci95[0]>0&&lhClassPooled.CLAIM.falseFirst.wrongSettledRate>BOUND,
 Q3:nonClaim.every(k=>rateTable[k].storyDecided===0&&rateTable[k].wrongSettledRate<=BOUND&&rateTable[k].falseCorrectionRate<=BOUND)
   &&['FULL','PARABLE'].every(m=>lhRate[m].storyDecided===0&&lhClassPooled[m].falseFirst.wrongSettledRate<=BOUND&&lhClassPooled[m].falseFirst.falseCorrectionRate<=BOUND)
   &&DiD.PARABLE_ws.ci95[0]<=0&&DiD.PARABLE_ws.ci95[1]>=0&&DiD.CLAIM_ws.ci95[0]>0,
 Q4:retention.retention>=0.75&&retention.parableBenefit.ci95[0]>0,
 Q5:lens.crossMinusOwn.ci95[1]<0&&Math.abs(lens.lensBlindCrossMinusOwn.mean)<3,
 Q6:excl0(perspective.liveMinusFrozen_restored),
 Q7:pp.every(x=>x.refused),
 Q8:zMismatch===0&&zChecked>0&&[...gp,...gpP,...gpC].every(x=>x.refused)
};
const overview={};for(const name of Object.keys(CONDS)){overview[name]={};for(const f of ['encounters','relationshipEncounters','realizedTrue','forgiven','restoredTrue','falseCorrections','wrongSettled','storyDecided','storyDecidedWrong','awaitingReception','residualErrors','novel','redundant','conflict','parables'])overview[name][f]=+(agg[name].reduce((s,r)=>s+tot(r,f),0)/n).toFixed(3);}
if(SMOKE){console.log('ok');process.exit(0);}
const lhSeries=[];for(let g=0;g<LH_G;g++){const row={generation:g+1};for(const mode of Object.keys(LH_MODES)){const ms=lh[mode].map(r=>r[g]);const a=f=>+(ms.reduce((x,m)=>x+(m[f]??0),0)/ms.length).toFixed(4);row[mode+'_restoredTrue']=a('restoredTrue');row[mode+'_wrongSettled']=a('wrongSettled');row[mode+'_falseCorrections']=a('falseCorrections');row[mode+'_storyDecided']=a('storyDecided');row[mode+'_encounters']=a('encounters');}lhSeries.push(row);}
fs.writeFileSync(path.join(out,'long-horizon.csv'),Object.keys(lhSeries[0]).join(',')+'\n'+lhSeries.map(x=>Object.values(x).join(',')).join('\n')+'\n');
const summary={kernel:'Constitutional Commons v0.3 parable ground',sources:Object.fromEntries(SOURCES.map(f=>[f,sha(f)])),authorityKeyId:auth.keyId,seeds:n,generationsPerRun:GENS,conditions:Object.keys(CONDS).length,longHorizon:{seeds:LH_SEEDS.length,generations:LH_G,modes:Object.keys(LH_MODES)},generationEpisodes:n*Object.keys(CONDS).length*GENS+LH_SEEDS.length*LH_G*Object.keys(LH_MODES).length,runtimeSeconds:+((Date.now()-t0)/1000).toFixed(1),verdict,statistics:S,conditionMeansPerSeed:overview};
fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,1));
const receipt=crypto.createHash('sha256').update(JSON.stringify({verdict,S:JSON.parse(JSON.stringify(S)),overview})).digest('hex');
fs.writeFileSync(path.join(out,'receipt.txt'),'receipt '+receipt+'\n'+SOURCES.map(f=>sha(f)+'  '+f).join('\n')+'\n');
console.log(JSON.stringify(verdict),'receipt',receipt);
