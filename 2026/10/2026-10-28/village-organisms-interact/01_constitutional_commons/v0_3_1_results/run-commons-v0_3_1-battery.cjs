'use strict';
// Reproduce: node run-commons-v0_3_1-battery.cjs            (Node built-ins only; no network)
//            node run-commons-v0_3_1-battery.cjs --smoke    (seed 7 only; prints "ok"; writes nothing)
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {Commons,Refusal,U}=require('./commons_kernel_v0_3_1.cjs');
const {Authorizer,Conductor}=require('./authority.cjs');
const SMOKE=process.argv.includes('--smoke');
const out=path.join(__dirname,'evidence');if(!SMOKE)fs.mkdirSync(out,{recursive:true});
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,f))).digest('hex');
const SOURCES=['authority.cjs','commons_kernel_v0_3_1.cjs','run-commons-v0_3_1-battery.cjs','preregistration_v0_3_1.json'];
const GENS=SMOKE?2:12,SEEDS=SMOKE?[7]:Array.from({length:200},(_,i)=>i+1).filter(s=>s!==7);
const LH_SEEDS=SMOKE?[7]:Array.from({length:30},(_,i)=>201+i),LH_G=SMOKE?3:200;
const BOUND=Math.exp(-3),MARGIN=0.02;
const auth=new Authorizer('commons-v0.2-test-key'),cond=new Conductor();
const graceFn=(c,s)=>{if(s===c.p.graceStep)c.receiveGrace(auth.issue({generation:c.generation,fromStep:s,toStep:c.p.steps,lineages:c.p.graceLineages,maxApprovals:c.p.maxApprovals,expiry:c.p.steps,conductorRequest:cond.request(c.generation)}));};
const PLANT={perLineage:4,falseCount:2,dwell:4};
const PAR={groundMode:'parable'};
const CONDS={
 // Stage B — perspective shapes, unplanted
 FULL:{},NO_GROUND:{ablate:{noGround:true}},
 FADE:{...PAR},FROZEN:{...PAR,ablate:{frozenPerspective:true}},
 DEEPEN:{...PAR,stage:'deepen'},RESONATE:{...PAR,stage:'resonate'},
 DEEPEN_CROSS:{...PAR,stage:'deepen',groundRead:'cross'},
 // Stage A — matched prehistory: identical first records at identical gates
 FULL_P:{plant:PLANT},CLAIM_P:{groundMode:'claim',plant:PLANT},
 FADE_P:{...PAR,plant:PLANT},DEEPEN_P:{...PAR,stage:'deepen',plant:PLANT},RESONATE_P:{...PAR,stage:'resonate',plant:PLANT}
};
const PARABLE_CONDS=['FADE','FROZEN','DEEPEN','RESONATE','DEEPEN_CROSS','FADE_P','DEEPEN_P','RESONATE_P'];
const FIELDS=['encounters','relationshipEncounters','dwellEncounters','realizedTrue','realizedFalse','forgiven','restoredTrue','falseCorrections','correctSampledGates','wrongSettled','sampledWrongGates','storyDecided','awaitingReception','residualErrors','novel','redundant','conflict','parables'];
const BEH=['encounters','relationshipEncounters','dwellEncounters','realizedTrue','realizedFalse','forgiven','restoredTrue','falseCorrections','correctSampledGates','wrongSettled','sampledWrongGates','awaitingReception','awaitingEvidence','residualErrors','novel','meanTTR','groundA','groundB'];
const beh=rows=>JSON.stringify(rows.map(m=>BEH.map(f=>m[f])));
function run(seed,o,gens,harvest,after){
 const c=new Commons(seed,auth.publicKey,o);const rows=[];
 for(let g=0;g<gens;g++){
  const m=c.runGeneration(graceFn);
  if(harvest)for(const a of c.learners)for(const e of a.ep.values())for(const s of e.samples)harvest.set(c.generation+':'+a.idx+':'+e.g+':'+s.k,s.z);
  rows.push(m);if(after)after(c,g);if(g<gens-1)c.descend();
 }
 if(c.p.groundMode==='parable')c.verifyParables();
 return {rows,c};
}
const t0=Date.now();
let csv=null;if(!SMOKE){csv=fs.openSync(path.join(out,'paired-runs.csv'),'w');fs.writeSync(csv,'condition,seed,generation,'+FIELDS.join(',')+',meanTTR,PF_sampledWrong,PF_wrongSettled,PF_sampledRight,PF_falseCorrections,PT_sampledWrong,PT_wrongSettled,PT_sampledRight,PT_falseCorrections\n');}
const agg={};for(const n of Object.keys(CONDS))agg[n]=[];
let zChecked=0,zMismatch=0,frozenIdentical=0;
for(const seed of SEEDS){
 const res={},zs={};
 for(const name of Object.keys(CONDS)){
  zs[name]=new Map();
  res[name]=run(seed,CONDS[name],GENS,zs[name]).rows;
  if(csv)for(const m of res[name]){const p=m.byPlant;fs.writeSync(csv,[name,seed,m.generation,...FIELDS.map(f=>m[f]),m.meanTTR??'',p.PF.sampledWrong,p.PF.wrongSettled,p.PF.sampledRight,p.PF.falseCorrections,p.PT.sampledWrong,p.PT.wrongSettled,p.PT.sampledRight,p.PT.falseCorrections].join(',')+'\n');}
  agg[name].push(res[name]);
 }
 for(const name of Object.keys(CONDS)){if(name==='FULL')continue;for(const [k,z] of zs[name])if(zs.FULL.has(k)){zChecked++;if(zs.FULL.get(k)!==z)zMismatch++;}}
 if(beh(res.FROZEN)===beh(res.FULL))frozenIdentical++;
 if(!SMOKE&&seed%25===0)console.log('seed',seed,((Date.now()-t0)/1000).toFixed(0)+'s');
}
if(csv)fs.closeSync(csv);
// ---------- probes: a refusal counts only with the RIGHT reason (a crash is not a check) ----------
function graceProbes(mode){
 const r=[];const c=new Commons(101,auth.publicKey,{groundMode:mode});const other=new Authorizer('not-the-authority');
 const base=g=>({generation:g,fromStep:0,toStep:40,lineages:['A','B'],maxApprovals:64,expiry:40,conductorRequest:'probe'});
 const t=(label,fn,want)=>{try{fn();r.push({probe:label,refused:false});}catch(e){const ok=e instanceof Refusal&&(!want||want.test(e.message));r.push({probe:label,refused:ok,reason:e.message,errorType:e.constructor.name});}};
 t('forged by another key',()=>c.receiveGrace(other.issue(base(1))),/signature/);
 t('tampered lineage after signing',()=>{const k=auth.issue(base(1));k.body.lineages=['A','B','C'];c.receiveGrace(k);},/signature/);
 t('tampered generation after signing',()=>{const k=auth.issue(base(2));k.body.scope.generation=1;c.receiveGrace(k);},/signature/);
 t('destination-bearing token, validly signed',()=>c.receiveGrace(auth.signRaw({...auth.issue(base(1)).body,destination:{gate:3,belief:1}})),/schema/);
 t('recipient-bearing token, validly signed',()=>c.receiveGrace(auth.signRaw({...auth.issue(base(1)).body,recipient:'101'})),/schema/);
 t('wrong generation scope',()=>c.receiveGrace(auth.issue(base(5))),/scope/);
 const good=auth.issue(base(1));c.receiveGrace(good);
 t('replay same token same generation',()=>c.receiveGrace(good),/replay/);
 c.runGeneration(null);c.descend();
 t('replay previous-generation token',()=>c.receiveGrace(good),/scope|replay/);
 for(let i=0;i<10;i++)c.next();
 t('expired token',()=>c.receiveGrace(auth.issue({...base(2),expiry:5})),/expired/);
 // self-sign: the ONLY acceptable outcome is the crypto layer refusing because the kernel holds a public key
 try{c.trySelfSign();r.push({probe:'kernel self-sign with held key material',refused:false});}
 catch(e){r.push({probe:'kernel self-sign with held key material',refused:e.code==='ERR_CRYPTO_INVALID_KEY_OBJECT_TYPE'&&c._vk.type==='public',reason:e.message,errorCode:e.code,heldKeyType:c._vk.type});}
 t('conductor attempts to sign',()=>{if(typeof cond.sign!=='function'&&typeof cond.issue!=='function')throw new Refusal('conductor seat holds no key and no signing method');},/no key/);
 return r;
}
function parableProbes(){
 const r=[];
 const mk=()=>run(101,{groundMode:'parable',stage:'deepen'},3,null).c;
 const t=(label,fn,want)=>{const c=mk();try{fn(c);r.push({probe:label,refused:false});}catch(e){r.push({probe:label,refused:want.test(e.message),reason:e.message,errorType:e.constructor.name});}};
 const legit=c=>({...c.parables.A[0]});
 t('parable carrying an answer field',c=>c._depositParable('A',{...legit(c),answer:1}),/parable schema/);
 t('parable carrying a belief field',c=>c._depositParable('A',{...legit(c),belief:0}),/parable schema/);
 t('parable carrying a destination field',c=>c._depositParable('A',{...legit(c),destination:{gate:3}}),/parable schema/);
 t('parable carrying a recipient field',c=>c._depositParable('A',{...legit(c),recipient:'204'}),/parable schema/);
 t('parable missing its dwell',c=>{const d=legit(c);delete d.dwell;c._depositParable('A',d);},/parable schema/);
 t('parable with dwell 0 (no walk)',c=>c._depositParable('A',{...legit(c),dwell:0}),/field types/);
 t('in-place edit of a told story',c=>{c.parables.A[0].dwell=99;},/read only|read-only/);
 t('story replaced by an altered copy',c=>{c.parables.A[0]=Object.freeze({...c.parables.A[0],dwell:c.parables.A[0].dwell+1});c.verifyParables();},/history chain/);
 t('story removed',c=>{c.parables.A.splice(0,1);c.verifyParables();},/history chain/);
 t('stories reordered',c=>{const L=c.parables.A;const j=L.findIndex(d=>JSON.stringify(d)!==JSON.stringify(L[0]));const x=L[0];L[0]=L[j];L[j]=x;c.verifyParables();},/history chain/);
 t('read index inflated without a story',c=>{const idx=c.parableIndex.A.values().next().value;idx.n++;c.verifyParables();},/index/);
 const a=run(101,{groundMode:'parable',stage:'deepen',plant:PLANT},6,null).rows;
 const b=run(101,{groundMode:'parable',stage:'deepen',plant:PLANT},6,null,c=>{for(const st of ['A','B']){for(const [g,v] of c._observer.first[st])c._observer.first[st].set(g,!v);for(const [g,v] of c._planted[st])c._planted[st].set(g,!v);}}).rows;
 r.push({probe:'observer truth and plant labels inverted every generation: behavior unchanged',refused:beh(a)===beh(b)});
 return r;
}
const gp={count:graceProbes('count'),parable:graceProbes('parable'),claim:graceProbes('claim')},pp=parableProbes();
// ---------- long horizon (descriptive) ----------
const LH_MODES={FULL:{},FADE:{...PAR,parableVerifyEvery:25},DEEPEN:{...PAR,stage:'deepen',parableVerifyEvery:25},RESONATE:{...PAR,stage:'resonate',parableVerifyEvery:25}};
const lh={};
for(const [mode,o] of Object.entries(LH_MODES)){lh[mode]=LH_SEEDS.map(s=>run(s,o,LH_G,null).rows);if(!SMOKE)console.log('long horizon',mode,((Date.now()-t0)/1000).toFixed(0)+'s');}
// ---------- statistics ----------
const n=SEEDS.length;
const tot=(rows,f,from=1)=>rows.filter(m=>m.generation>=from).reduce((s,m)=>s+(m[f]||0),0);
const ci=d=>{const k=d.length,mu=d.reduce((a,b)=>a+b,0)/k,sd=k>1?Math.sqrt(d.reduce((a,b)=>a+(b-mu)**2,0)/(k-1)):0;return {mean:+mu.toFixed(4),ci95:[+(mu-1.96*sd/Math.sqrt(k)).toFixed(4),+(mu+1.96*sd/Math.sqrt(k)).toFixed(4)]};};
function paired(name,base,f,from=1){const d=agg[name].map((r,i)=>tot(r,f,from)-tot(agg[base][i],f,from));return {...ci(d),condMean:+(agg[name].reduce((s,r)=>s+tot(r,f,from),0)/n).toFixed(3),baseMean:+(agg[base].reduce((s,r)=>s+tot(r,f,from),0)/n).toFixed(3)};}
function rates(rowsets){let fc=0,sr=0,ws=0,sw=0,sd=0;for(const r of rowsets)for(const m of r){fc+=m.falseCorrections;sr+=m.correctSampledGates;ws+=m.wrongSettled;sw+=m.sampledWrongGates;sd+=m.storyDecided;}
 return {falseCorrectionRate:sr?+(fc/sr).toFixed(5):null,wrongSettledRate:sw?+(ws/sw).toFixed(5):null,storyDecided:sd};}
const rateTable={};for(const name of Object.keys(CONDS))rateTable[name]=rates(agg[name]);
// matched prehistory: per-seed planted-class totals
const plantTotals=rows=>{const z={PF:{sw:0,ws:0,sr:0,fc:0},PT:{sw:0,ws:0,sr:0,fc:0}};for(const m of rows)for(const cl of ['PF','PT']){const b=m.byPlant[cl];z[cl].sw+=b.sampledWrong;z[cl].ws+=b.wrongSettled;z[cl].sr+=b.sampledRight;z[cl].fc+=b.falseCorrections;}return z;};
const PCONDS=['FULL_P','CLAIM_P','FADE_P','DEEPEN_P','RESONATE_P'];
const pt={};for(const k of PCONDS)pt[k]=agg[k].map(plantTotals);
const pool=(arr,idx)=>{const z={PF:{sw:0,ws:0,sr:0,fc:0},PT:{sw:0,ws:0,sr:0,fc:0}};for(const i of idx)for(const cl of ['PF','PT'])for(const k of ['sw','ws','sr','fc'])z[cl][k]+=arr[i][cl][k];return z;};
const allIdx=SEEDS.map((_,i)=>i);
const H=(z,m)=>m==='ws'?(z.PF.sw&&z.PT.sw?z.PF.ws/z.PF.sw-z.PT.ws/z.PT.sw:null):(z.PF.sr&&z.PT.sr?z.PF.fc/z.PF.sr-z.PT.fc/z.PT.sr:null);
const fx=v=>v==null?null:+v.toFixed(5);
function did(mode,m){const B=2000,v=[];let skipped=0;
 for(let b=0;b<B;b++){const idx=SEEDS.map((_,i)=>Math.floor(U(9031,b,i)*SEEDS.length));const hm=H(pool(pt[mode],idx),m),hf=H(pool(pt.FULL_P,idx),m);if(hm==null||hf==null){skipped++;continue;}v.push(hm-hf);}
 v.sort((a,b)=>a-b);const q=p=>v.length?+v[Math.min(v.length-1,Math.floor(p*v.length))].toFixed(5):null;
 const hm0=H(pool(pt[mode],allIdx),m),hf0=H(pool(pt.FULL_P,allIdx),m);return {point:hm0==null||hf0==null?null:fx(hm0-hf0),ci95:[q(0.025),q(0.975)],resamples:v.length,skipped};}
const plantedRates={};for(const k of PCONDS){const z=pool(pt[k],allIdx);plantedRates[k]={plantedFalse:{sampledWrong:z.PF.sw,wrongSettledRate:z.PF.sw?fx(z.PF.ws/z.PF.sw):null,sampledRight:z.PF.sr,falseCorrectionRate:z.PF.sr?fx(z.PF.fc/z.PF.sr):null},plantedTrue:{sampledWrong:z.PT.sw,wrongSettledRate:z.PT.sw?fx(z.PT.ws/z.PT.sw):null,sampledRight:z.PT.sr,falseCorrectionRate:z.PT.sr?fx(z.PT.fc/z.PT.sr):null}};}
const DiD={};for(const k of ['CLAIM_P','FADE_P','DEEPEN_P','RESONATE_P'])DiD[k]={wrongSettled:did(k,'ws'),falseCorrection:did(k,'fc')};
const within=(x,m)=>x.ci95[0]!=null&&x.ci95[0]>=-m&&x.ci95[1]<=m;
const shapes={deepenMinusFade:paired('DEEPEN','FADE','restoredTrue'),resonateMinusFade:paired('RESONATE','FADE','restoredTrue'),
 deepenMinusFrozen:paired('DEEPEN','FROZEN','restoredTrue'),resonateMinusFrozen:paired('RESONATE','FROZEN','restoredTrue'),fadeMinusFrozen:paired('FADE','FROZEN','restoredTrue'),
 deepenMinusNoGround:paired('DEEPEN','NO_GROUND','restoredTrue'),resonateMinusNoGround:paired('RESONATE','NO_GROUND','restoredTrue'),
 encounters:{deepenMinusFade:paired('DEEPEN','FADE','encounters'),resonateMinusFade:paired('RESONATE','FADE','encounters')},
 falseCorrections:{deepenMinusFade:paired('DEEPEN','FADE','falseCorrections'),resonateMinusFade:paired('RESONATE','FADE','falseCorrections')}};
const lens={deepenCrossMinusOwn:paired('DEEPEN_CROSS','DEEPEN','restoredTrue',2)};
const win=(rowsets,f,a,b)=>rowsets.reduce((s,r)=>s+r.slice(a-1,b).reduce((x,m)=>x+(m[f]||0),0),0)/rowsets.length/(b-a+1);
const lhSummary={};for(const mode of Object.keys(LH_MODES))lhSummary[mode]={restoredPerGen_1_10:+win(lh[mode],'restoredTrue',1,10).toFixed(3),restoredPerGen_101_200:+win(lh[mode],'restoredTrue',101,200).toFixed(3),encountersPerGen_101_200:+win(lh[mode],'encounters',101,200).toFixed(2),...rates(lh[mode])};
const S={
 B1_deepenBeatsFade:shapes.deepenMinusFade,B2_resonateBeatsFade:shapes.resonateMinusFade,shapeDetail:shapes,
 B3_lensUnderDeepening:lens,
 B4_truth:{frozenBitIdenticalToFULL:frozenIdentical,of:n,rates:rateTable,zKeysCompared:zChecked,zMismatches:zMismatch},
 A1_A2_matchedPrehistory:{plant:PLANT,plantedRates,differenceInDifferencesVsFULL_P:DiD,equivalenceMargin:MARGIN},
 A3_probes:{grace:gp,parable:pp},
 longHorizonDescriptive:lhSummary
};
const allProbes=[...gp.count,...gp.parable,...gp.claim,...pp];
const verdict={
 B1:shapes.deepenMinusFade.ci95[0]>0,
 B2:shapes.resonateMinusFade.ci95[0]>0,
 B3:lens.deepenCrossMinusOwn.ci95[1]<0,
 B4:frozenIdentical===n&&zMismatch===0&&zChecked>0&&PARABLE_CONDS.every(k=>rateTable[k].storyDecided===0&&rateTable[k].wrongSettledRate<=BOUND&&rateTable[k].falseCorrectionRate<=BOUND)&&Object.values(lhSummary).every(x=>x.storyDecided===0),
 A1:plantedRates.CLAIM_P.plantedFalse.wrongSettledRate>BOUND&&DiD.CLAIM_P.wrongSettled.ci95[0]>0,
 A2:['FADE_P','DEEPEN_P','RESONATE_P'].every(k=>within(DiD[k].wrongSettled,MARGIN)&&within(DiD[k].falseCorrection,MARGIN)),
 A3:allProbes.every(x=>x.refused)
};
const overview={};for(const name of Object.keys(CONDS)){overview[name]={};for(const f of ['encounters','realizedTrue','restoredTrue','falseCorrections','wrongSettled','storyDecided','residualErrors','parables'])overview[name][f]=+(agg[name].reduce((s,r)=>s+tot(r,f),0)/n).toFixed(3);}
if(SMOKE){console.log('ok');process.exit(0);}
const lhSeries=[];for(let g=0;g<LH_G;g++){const row={generation:g+1};for(const mode of Object.keys(LH_MODES)){const ms=lh[mode].map(r=>r[g]);const a=f=>+(ms.reduce((x,m)=>x+(m[f]??0),0)/ms.length).toFixed(4);row[mode+'_restoredTrue']=a('restoredTrue');row[mode+'_encounters']=a('encounters');row[mode+'_wrongSettled']=a('wrongSettled');row[mode+'_falseCorrections']=a('falseCorrections');}lhSeries.push(row);}
fs.writeFileSync(path.join(out,'long-horizon.csv'),Object.keys(lhSeries[0]).join(',')+'\n'+lhSeries.map(x=>Object.values(x).join(',')).join('\n')+'\n');
const summary={kernel:'Constitutional Commons v0.3.1 perspective shapes + matched prehistory',sources:Object.fromEntries(SOURCES.map(f=>[f,sha(f)])),authorityKeyId:auth.keyId,seeds:n,generationsPerRun:GENS,conditions:Object.keys(CONDS).length,longHorizon:{seeds:LH_SEEDS.length,generations:LH_G,modes:Object.keys(LH_MODES)},generationEpisodes:n*Object.keys(CONDS).length*GENS+LH_SEEDS.length*LH_G*Object.keys(LH_MODES).length,runtimeSeconds:+((Date.now()-t0)/1000).toFixed(1),verdict,statistics:S,conditionMeansPerSeed:overview};
fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,1));
const receipt=crypto.createHash('sha256').update(JSON.stringify({verdict,S:JSON.parse(JSON.stringify(S)),overview})).digest('hex');
fs.writeFileSync(path.join(out,'receipt.txt'),'receipt '+receipt+'\n'+SOURCES.map(f=>sha(f)+'  '+f).join('\n')+'\n');
console.log(JSON.stringify(verdict),'receipt',receipt);
