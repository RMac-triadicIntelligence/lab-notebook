'use strict';
// Constitutional Commons v0.3.1 — parable ground, perspective shapes, matched prehistory.
// v0.3.1 adds (defaults reproduce v0.3 exactly):
//   stage 'fade' (v0.3 default) | 'deepen' | 'resonate' — how a story's meaning moves with the reader's own walk.
//   plant {perLineage,falseCount,dwell} — identical first records planted at identical gates before generation 1,
//   so a false first story can be compared across reading modes on matched footing.
// v0.2 loop unchanged: approach cost -> encounter -> evidence (from hidden truth, never from cost)
//   -> realization (dwelling threshold) -> costless confession -> external grace (signature)
//   -> forgiveness -> reception (changed by encounters) -> restoration -> lineage ground at the gate.
// v0.3 adds two ways for descendants to READ the ground (v0.2 only counted it):
//   groundMode 'count'   (default) — v0.2 exactly: the record's content is never read.
//   groundMode 'claim'   — counterfactual: the record is read as an ANSWER (prior on the conclusion).
//                          First writer wins, as in v0.2. This is where a false first story cascades.
//   groundMode 'parable' — the record is a parable: who crossed, through what lens, after how long.
//                          It carries no answer, belief, direction or recipient (schema-refused).
//                          The story never changes (append-only, hash-chained). Its MEANING is computed
//                          at read time from the reader: their lens (lineage basis) and where they are in
//                          their own walk at that gate. Meaning may lower the cost of approaching a gate;
//                          it never touches evidence, llr, threshold or conclusion.
const crypto=require('crypto');
const {canonical}=require('./authority.cjs');

// ---------- deterministic keyed randomness (integer-keyed, order-independent) ----------
function mix(h){h=Math.imul(h^(h>>>16),0x85ebca6b);h=Math.imul(h^(h>>>13),0xc2b2ae35);return (h^(h>>>16))>>>0;}
function hashKey(arr){let h=0x9e3779b9;for(const v of arr){h=mix(h^mix((v|0)+0x632be59b));}return h>>>0;}
const U=(...k)=>(hashKey(k)+0.5)/4294967296;
const Z=(...k)=>{const u1=U(...k,1),u2=U(...k,2);return Math.sqrt(-2*Math.log(u1))*Math.cos(2*Math.PI*u2);};
const S={WORLD:11,ERR:12,RIGHT:13,RECEPT:14,BURDEN:15,EVID:16,APPROACH:17,PLANT:18};

const DEFAULTS=Object.freeze({
 gates:16,learnersPerLineage:4,steps:40,errorsPerLearner:3,rightPerLearner:2,
 tau:3.0,sigma0:1.0,burdenMean:0.25,
 baseCost:1.0,exposure:2.0,love:0.7,budget:1.6,temp:0.25,rotation:0.15,
 groundRelief:0.6,pointerRelief:0.8,
 kappa:0.15,dwellGain:0.02,rho:0.5,
 graceStep:0,graceLineages:['A','B'],maxApprovals:64,
 groundMode:'count',claimPrior:1.5,parableVerifyEvery:1,stage:'fade',plant:null,
 ablate:{}
});
const BASIS={A:[1,1,0.25,0.25],B:[0.25,0.25,1,1]};
const TOKEN_KEYS=['authority','bounds','expiry','lineages','nonce','provenance','scope','v'];
// A parable says: someone of this lineage, seeing this gate this clearly, crossed it here, after this long.
// It does not say what is true at the gate, what they believed, or who should hear it.
const PARABLE_KEYS=['clarity','dwell','gate','generation','teller','v'];

class Refusal extends Error{}

class Commons{
 constructor(seed,verifyKey,opts={}){
  this.p={...DEFAULTS,...opts,ablate:{...(opts.ablate||{})}};
  if(!['count','claim','parable'].includes(this.p.groundMode))throw Error('unknown groundMode');
  if(!['fade','deepen','resonate'].includes(this.p.stage))throw Error('unknown stage');
  this.seed=seed;this._vk=verifyKey;this._vcache=new Set();
  this.keyId=crypto.createHash('sha256').update(verifyKey.export({format:'der',type:'spki'})).digest('hex').slice(0,16);
  const G=this.p.gates;
  this.world=Array.from({length:G},(_,g)=>({g,truth:U(seed,S.WORLD,g,0)<0.5?0:1,f:[0,1,2,3].map(a=>U(seed,S.WORLD,g,10+a)),w:Math.exp(-g/5)}));
  this.ground={A:new Map(),B:new Map()}; // count/claim: gate -> {content,count,answer}
  // parable store: append-only log per lineage + hash chain + derived read index (rebuilt and checked from the log)
  this.parables={A:[],B:[]};this.parableHead={A:'parables:A:'+seed,B:'parables:B:'+seed};
  this.parableIndex={A:new Map(),B:new Map()};this._meaningMemo={A:new Map(),B:new Map()};
  // OBSERVER ONLY: truth of the first record at each gate. Never read by any learner-facing code path.
  this._observer={first:{A:new Map(),B:new Map()}};
  this.storyReads=0;
  if(this.p.groundSwap)this.groundOwner={A:'B',B:'A'};else this.groundOwner={A:'A',B:'B'};
  this.generation=0;this.archive=[];this.ledger=new Set();this.consumedNonces=new Set();
  this.chainHead='genesis:'+seed;this.metrics=[];
  this._planted={A:new Map(),B:new Map()};// OBSERVER: gate -> planted story was false
  if(this.p.plant)this._plantPrehistory();
  this._birth();this.snapshotBirthGround();
 }
 // ---------- matched prehistory ----------
 // Same gates, same truth status, same teller lineage, same dwell in every reading mode. Gates are drawn with the
 // world's error prevalence (where people actually err). The first falseCount plants per lineage are false.
 // In 'parable' mode a planted false story and a planted true story are byte-identical in content: a parable has
 // no answer to be wrong. Only the observer knows which is which.
 _plantPrehistory(){
  const P=this.p,pl=P.plant;
  for(const lin of ['A','B']){
   const store=this.groundOwner[lin];
   const order=this.world.map(w=>({g:w.g,k:U(this.seed,S.PLANT,lin==='A'?0:1,w.g)**(1/w.w)})).sort((a,b)=>b.k-a.k).slice(0,pl.perLineage);
   order.forEach((o,i)=>{const g=o.g,isFalse=i<pl.falseCount,ans=isFalse?1-this.world[g].truth:this.world[g].truth;
    this._planted[store].set(g,isFalse);
    if(P.groundMode==='parable'){this._depositParable(store,{v:1,teller:lin,gate:g,generation:0,dwell:pl.dwell,clarity:this.vis(lin,g)});this._observer.first[store].set(g,!isFalse);}
    else{const content=crypto.createHash('sha256').update(g+':'+ans).digest('hex').slice(0,16);this.ground[store].set(g,{content,count:1,answer:ans,planted:true});}
   });
  }
 }
 label(l){return this.p.labelSwap?(l==='A'?'B':'A'):l;}
 vis(lin,g){const b=BASIS[lin],f=this.world[g].f;let d=0,s=0;for(let i=0;i<4;i++){d+=b[i]*f[i];s+=b[i];}return 0.25+0.75*d/s;}
 overlap(a,b){const x=BASIS[a],y=BASIS[b];let d=0,nx=0,ny=0;for(let i=0;i<4;i++){d+=x[i]*y[i];nx+=x[i]*x[i];ny+=y[i]*y[i];}return d/Math.sqrt(nx*ny);}
 _log(a,text){const e={step:this.step,text};a.history.push(e);a.head=crypto.createHash('sha256').update(a.head+canonical(e)).digest('hex');}
 _birth(){
  this.generation++;this.step=0;this.grace=null;this.pointers=new Map();
  const P=this.p,n=P.learnersPerLineage,G=P.gates,gen=this.generation;
  this.learners=[];
  for(let i=0;i<2*n;i++){
   const lin=i<n?'A':'B';const uid=gen*100+i;
   const pool=this.world.map(w=>({g:w.g,k:U(this.seed,S.ERR,gen,i,w.g)**(1/w.w)})).sort((a,b)=>b.k-a.k);
   const errs=pool.slice(0,P.errorsPerLearner).map(x=>x.g);
   const rest=this.world.map(w=>w.g).filter(g=>!errs.includes(g)).map(g=>({g,k:U(this.seed,S.RIGHT,gen,i,g)})).sort((a,b)=>b.k-a.k);
   const rights=rest.slice(0,P.rightPerLearner).map(x=>x.g);
   const ep=new Map();
   for(const g of [...errs,...rights]){const t=this.world[g].truth;ep.set(g,{g,belief:errs.includes(g)?1-t:t,initiallyWrong:errs.includes(g),llr:0,llrSamples:0,prior:0,samples:[],settled:false,realized:false,realizedAt:null,confessed:false,approval:null,forgiven:false,restored:false,restoredAt:null,receptionAtRestore:null,pointed:false,firstClass:undefined,storyDecided:null});}
   const a={uid,idx:i,lineage:lin,label:this.label(lin),reception:0.1+0.5*U(this.seed,S.RECEPT,gen,i),ep,burden:0,history:[],head:'birth:'+uid,stats:{enc:0,relEnc:0,dwellEnc:0,pointerEnc:0}};
   this._log(a,'born: constitution + lineage basis + lineage ground; no burden, approval or biography inherited');
   this.learners.push(a);
  }
  this._burden();this.verify(true);
 }
 _errors(a){return [...a.ep.values()].filter(e=>e.belief!==this.world[e.g].truth);}
 _burden(){for(const a of this.learners){let b=0;for(const e of this._errors(a))b+=-this.p.burdenMean*Math.log(U(this.seed,S.BURDEN,this.generation,a.idx,e.g,this.step));a.burden=b;}}
 groundDepth(lin,g){
  const d=x=>x?Math.min(1,Math.log2(1+x.count)):0;const other=lin==='A'?'B':'A';
  if(this.p.groundRead==='cross')return d(this.ground[this.groundOwner[other]].get(g));
  if(this.p.groundRead==='union')return Math.max(d(this.ground[this.groundOwner[lin]].get(g)),d(this.ground[this.groundOwner[other]].get(g)));
  return d(this.ground[this.groundOwner[lin]].get(g));}
 // ---------- parable: the story is fixed, the meaning is the reader's ----------
 // Meaning of one parable to a reader standing at gate g with k evidence samples taken there so far:
 //   lens     R = basis overlap(teller, reader)       — how much of the teller's way of seeing is mine
 //   clarity  F = min(1, vis_reader(g)/vis_teller(g)) — a story told from a clearer view means less to a dimmer one
 //   stage    T = 1 while k <= dwell; then exp(-(k-dwell)/(1+dwell)) — the stories that speak to you are those of
 //              people who walked at least as far as you have; past their turning point their story falls silent
 //              and you are left with your own evidence.
 // Collection meaning = depth(n) * mean over parables (depth as in v0.2, so a frozen, lens-blind reading of a
 // parable store is exactly v0.2's count ground).
 _lens(reader,teller,g){if(this.p.ablate.lensBlind)return 1;return this.overlap(teller,reader)*Math.min(1,this.vis(reader,g)/this.vis(teller,g));}
 // stage: how one story's meaning moves with the reader's own walk k at this gate, given the teller's dwell D.
 //   fade     (v0.3): 1 while k<=D, then exp(-(k-D)/(1+D)) — the story falls silent once you pass the teller.
 //   deepen          : (1+k)/(1+D) while k<D, then 1 — the story means more as your walk approaches theirs, and keeps it.
 //   resonate        : (1+min(k,D))/(1+max(k,D)) — the story means most when your walk is as long as theirs.
 _stage(k,D){const st=this.p.stage;if(st==='deepen')return k>=D?1:(1+k)/(1+D);if(st==='resonate')return (1+Math.min(k,D))/(1+Math.max(k,D));return k<=D?1:Math.exp(-(k-D)/(1+D));}
 _storeMeaning(store,readerLin,g,k){
  const idx=this.parableIndex[store].get(g);if(!idx||idx.n===0)return 0;
  const memo=this._meaningMemo[store];const key=g+'|'+readerLin+'|'+k;
  if(memo.has(key))return memo.get(key);
  let s=0;
  for(const c of idx.cells.values()){
   const T=this._stage(k,c.dwell);
   s+=c.count*this._lens(readerLin,c.teller,g)*T;
  }
  const v=Math.min(1,Math.log2(1+idx.n))*(s/idx.n);
  memo.set(key,v);return v;
 }
 meaning(a,e){
  const k=this.p.ablate.frozenPerspective?0:e.samples.length;const own=this.groundOwner[a.lineage],other=this.groundOwner[a.lineage==='A'?'B':'A'];
  if(this.p.groundRead==='cross')return this._storeMeaning(other,a.lineage,e.g,k);
  if(this.p.groundRead==='union')return Math.max(this._storeMeaning(own,a.lineage,e.g,k),this._storeMeaning(other,a.lineage,e.g,k));
  return this._storeMeaning(own,a.lineage,e.g,k);
 }
 _depositParable(store,deposit){
  if(!deposit||typeof deposit!=='object'||Array.isArray(deposit))throw new Refusal('parable: malformed');
  const keys=Object.keys(deposit).sort();
  if(keys.join()!==PARABLE_KEYS.join())throw new Refusal('parable schema: a parable carries no answer, belief, direction or recipient');
  if(typeof deposit.teller!=='string'||!BASIS[deposit.teller]||!Number.isInteger(deposit.gate)||!Number.isInteger(deposit.dwell)||deposit.dwell<1||typeof deposit.clarity!=='number')throw new Refusal('parable: field types');
  const d=Object.freeze({...deposit});
  this.parables[store].push(d);
  this.parableHead[store]=crypto.createHash('sha256').update(this.parableHead[store]+canonical(d)).digest('hex');
  this._index(store,d);this._meaningMemo[store].clear();
  return d;
 }
 _index(store,d){
  const m=this.parableIndex[store];if(!m.has(d.gate))m.set(d.gate,{n:0,cells:new Map()});
  const idx=m.get(d.gate);idx.n++;const ck=d.teller+'|'+d.dwell;
  if(!idx.cells.has(ck))idx.cells.set(ck,{teller:d.teller,dwell:d.dwell,count:0});idx.cells.get(ck).count++;
 }
 verifyParables(){// the story is the log: recompute the chain and the read index from it
  for(const store of ['A','B']){
   let h='parables:'+store+':'+this.seed;const rebuilt=new Map();
   for(const d of this.parables[store]){
    if(!Object.isFrozen(d)||Object.keys(d).sort().join()!==PARABLE_KEYS.join())throw Error('parable contract: deposit shape');
    h=crypto.createHash('sha256').update(h+canonical(d)).digest('hex');
    if(!rebuilt.has(d.gate))rebuilt.set(d.gate,{n:0,cells:new Map()});const r=rebuilt.get(d.gate);r.n++;const ck=d.teller+'|'+d.dwell;r.cells.set(ck,(r.cells.get(ck)||0)+1);
   }
   if(h!==this.parableHead[store])throw Error('parable contract: history chain (a story was altered, removed or reordered)');
   const live=this.parableIndex[store];
   if(live.size!==rebuilt.size)throw Error('parable contract: index');
   for(const [g,r] of rebuilt){const l=live.get(g);if(!l||l.n!==r.n||l.cells.size!==r.cells.size)throw Error('parable contract: index');for(const [ck,c] of r.cells)if(!l.cells.has(ck)||l.cells.get(ck).count!==c)throw Error('parable contract: index');}
  }
 }
 // ---------- claim: the counterfactual where the record is read as an answer ----------
 _claim(lin,g){const x=this.ground[this.groundOwner[lin]].get(g);return x?x.answer:undefined;}
 // OBSERVER: what kind of first story stood at this gate when this learner first stepped up to it
 _firstClass(lin,g){
  const store=this.groundOwner[lin];
  if(this.p.groundMode==='parable'){const t=this._observer.first[store].get(g);return t===undefined?'N':(t?'T':'F');}
  const x=this.ground[store].get(g);return x?(x.answer===this.world[g].truth?'T':'F'):'N';
 }
 cost(a,e){const P=this.p;let c=P.baseCost+P.exposure*(1-P.love);if(!P.ablate.noGround)c-=P.groundRelief*(P.groundMode==='parable'?this.meaning(a,e):this.groundDepth(a.lineage,e.g));if(e.pointed)c-=P.pointerRelief;return c;}
 // ---------- grace ----------
 receiveGrace(token){
  if(!token||typeof token!=='object'||!token.body||typeof token.sig!=='string')throw new Refusal('malformed');
  const keys=Object.keys(token.body).sort();
  if(keys.join()!==TOKEN_KEYS.join())throw new Refusal('schema: grace carries no destination, recipient or answer');
  const ok=crypto.verify(null,Buffer.from(canonical(token.body)),this._vk,Buffer.from(token.sig,'base64'));
  if(!ok)throw new Refusal('signature');
  const b=token.body;
  if(b.authority!==this.keyId)throw new Refusal('authority');
  if(b.scope.generation!==this.generation)throw new Refusal('scope: generation');
  if(this.consumedNonces.has(b.nonce))throw new Refusal('replay');
  if(this.step>b.expiry)throw new Refusal('expired');
  this.consumedNonces.add(b.nonce);this.grace={...token,approvals:0};
  return true;
 }
 _sigOK(body,sig){const k=sig+'|'+canonical(body);if(this._vcache.has(k))return true;const ok=crypto.verify(null,Buffer.from(canonical(body)),this._vk,Buffer.from(sig,'base64'));if(ok)this._vcache.add(k);return ok;}
 _graceValidFor(a){const g=this.grace;if(!g)return false;const b=g.body;return b.scope.generation===this.generation&&this.step>=b.scope.fromStep&&this.step<=Math.min(b.scope.toStep,b.expiry)&&b.lineages.includes(a.lineage)&&g.approvals<b.bounds.maxApprovals&&this._sigOK(b,g.sig);}
 // ---------- one encounter step ----------
 next(){
  const P=this.p;if(this.step>=P.steps)return;this.step++;this._burden();
  for(const a of this.learners){
   const sigma=P.sigma0*(1+a.burden);
   const cands=[...a.ep.values()].filter(e=>!e.settled&&!e.restored);
   if(cands.length){
    let best=null,bs=Infinity;for(const e of cands){let s=this.cost(a,e)+P.rotation*e.samples.length;if(P.scoreQuantum)s=Math.round(s/P.scoreQuantum);if(s<bs){bs=s;best=e;}}
    const c=this.cost(a,best);
    const pApproach=P.ablate.cutCostToEncounter?0.5:1/(1+Math.exp((c-P.budget)/P.temp));
    if(U(this.seed,S.APPROACH,this.generation,a.idx,this.step)<pApproach){
     const e=best;
     if(e.realized){
      a.stats.enc++;a.stats.dwellEnc++;if(!P.ablate.freezeReception)a.reception=Math.min(1,a.reception+P.dwellGain);
      this._relational(a,e);continue;}
     const v=this.vis(a.lineage,e.g),mu=this.world[e.g].truth?1:-1;
     const k=e.samples.length,z=Z(this.seed,S.EVID,this.generation,a.idx,e.g,k);
     if(k===0&&e.firstClass===undefined){
      e.firstClass=this._firstClass(a.lineage,e.g);// observer label only
      if(P.groundMode==='claim'&&!P.ablate.noGround){const cl=this._claim(a.lineage,e.g);if(cl!==undefined){e.prior=P.claimPrior*(cl===1?1:-1);e.llr+=e.prior;this.storyReads++;}}
     }
     const x=mu*v+sigma*z,d=2*v*x/(sigma*sigma);e.llr+=d;e.llrSamples+=d;e.samples.push({k,z,x,sigma,v,step:this.step});a.stats.enc++;
     const against=e.belief===1?-e.llr:e.llr,againstEv=e.belief===1?-e.llrSamples:e.llrSamples;
     if(against>=P.tau){e.realized=true;e.realizedAt=this.step;if(e.prior&&againstEv<P.tau)e.storyDecided='realized';this._log(a,'realization at gate '+e.g+' (evidence against held belief)');
      e.confessed=true;this._log(a,'confession (costless declaration) at gate '+e.g);}
     else if(-against>=P.tau){e.settled=true;if(e.prior&&-againstEv<P.tau)e.storyDecided='settled';this._log(a,'belief at gate '+e.g+' confirmed by evidence');}
     else {a.stats.dwellEnc++;if(!P.ablate.freezeReception)a.reception=Math.min(1,a.reception+P.dwellGain);}
     this._relational(a,e);
    }
   }
  }
  this._resolve();this.verify();
 }
 _relational(a,e){const P=this.p,peers=this.pointers.get(e.g);
  if(e.pointed&&peers&&peers.size){a.stats.relEnc++;
   if(!P.ablate.freezeReception){let best=0;for(const pu of peers){const pl=this.learners.find(q=>q.uid===pu).lineage;best=Math.max(best,this.overlap(a.lineage,pl));}a.reception=Math.min(1,a.reception+P.kappa*best);}}}
 _resolve(){
  const P=this.p;
  for(const a of this.learners)for(const e of a.ep.values()){
   if(e.realized&&e.confessed&&!e.forgiven&&this._graceValidFor(a)){
    const key=this.grace.body.nonce+'|'+a.uid+'|'+e.g;if(this.ledger.has(key))throw Error('ledger replay');
    this.ledger.add(key);this.grace.approvals++;e.approval={nonce:this.grace.body.nonce,sig:this.grace.sig,body:this.grace.body,step:this.step};e.forgiven=true;
    this._log(a,'external approval completes forgiveness at gate '+e.g);
   }
   if(e.forgiven&&!e.restored&&a.reception>=P.rho){
    e.restored=true;e.restoredAt=this.step;e.receptionAtRestore=a.reception;e.belief=1-e.belief;
    this._log(a,'restoration at gate '+e.g+': burden from this error released; history kept');
    const store=this.groundOwner[a.lineage];let kind;
    if(P.groundMode==='parable'){
     const first=!this.parableIndex[store].has(e.g);
     this._depositParable(store,{v:1,teller:a.lineage,gate:e.g,generation:this.generation,dwell:e.samples.length,clarity:this.vis(a.lineage,e.g)});
     if(first)this._observer.first[store].set(e.g,e.belief===this.world[e.g].truth);
     kind=first?'novel':'redundant';
    } else {
     const gl=this.ground[store];const content=crypto.createHash('sha256').update(e.g+':'+e.belief).digest('hex').slice(0,16);
     const prev=gl.get(e.g);
     if(!prev){gl.set(e.g,{content,count:1,answer:e.belief});kind='novel';}else if(prev.content===content){prev.count++;kind='redundant';}else{kind='conflict';prev.conflicts=(prev.conflicts||0)+1;}
    }
    this.genStats[kind]++;
    if(!P.ablate.cutPeerPointer){if(!this.pointers.has(e.g))this.pointers.set(e.g,new Set());this.pointers.get(e.g).add(a.uid);
     for(const q of this.learners)if(q!==a){const qe=q.ep.get(e.g);if(qe&&!qe.pointed){qe.pointed=true;}}}
   }
  }
  this._burden();
 }
 // ---------- constitutional contracts (checked every step) ----------
 verify(full){
  const P=this.p;
  for(const a of this.learners){
   for(const e of a.ep.values()){
    if(e.restored&&(!e.forgiven||!e.approval||e.receptionAtRestore<P.rho))throw Error('restoration contract');
    if(e.forgiven&&(!e.realized||!e.confessed||!e.approval))throw Error('forgiveness contract');
    if(e.approval){const b=e.approval.body;if(!this._sigOK(b,e.approval.sig))throw Error('approval signature');if(!b.lineages.includes(a.lineage)||b.scope.generation!==this.generation)throw Error('approval scope');}
    if(P.groundMode!=='claim'&&e.prior!==0)throw Error('truth contract: only the claim counterfactual may carry a story into a conclusion');
    if(e.realized){let l=e.prior||0;for(const s of e.samples){l+=2*s.v*s.x/(s.sigma*s.sigma);if(Math.abs(s.x-((this.world[e.g].truth?1:-1)*s.v+s.sigma*s.z))>1e-12)throw Error('evidence not from truth');}
     if(Math.abs(l-e.llr)>1e-9)throw Error('llr recompute');const b0=e.restored?1-e.belief:e.belief;if((b0===1?-l:l)<P.tau-1e-9)throw Error('realization below threshold');}
   }
   if(!full)continue;let h='birth:'+a.uid;for(const x of a.history)h=crypto.createHash('sha256').update(h+canonical(x)).digest('hex');if(h!==a.head)throw Error('history chain');
  }
 }
 runGeneration(issueGrace){
  this.genStats={novel:0,redundant:0,conflict:0};
  if(issueGrace)issueGrace(this,0);
  for(let s=1;s<=this.p.steps;s++){this.next();if(issueGrace)issueGrace(this,s);}
  this.verify(true);
  if(this.p.groundMode==='parable'&&(this.generation%this.p.parableVerifyEvery===0))this.verifyParables();
  const m=this._measure();this.metrics.push(m);return m;
 }
 coverage(store){return this.p.groundMode==='parable'?this.parableIndex[store].size:this.ground[store].size;}
 _measure(){
  const L=this.learners,eps=L.flatMap(a=>[...a.ep.values()].map(e=>({a,e})));
  const errs=eps.filter(x=>x.e.initiallyWrong),rights=eps.filter(x=>!x.e.initiallyWrong);
  const restoredTrue=errs.filter(x=>x.e.restored),ttr=restoredTrue.map(x=>x.e.restoredAt);
  const byLin=lin=>{const r=errs.filter(x=>x.a.lineage===lin);return {errors:r.length,restored:r.filter(x=>x.e.restored).length,meanTTR:avg(r.filter(x=>x.e.restored).map(x=>x.e.restoredAt))};};
  const byFirst={};for(const cl of ['T','F','N']){const W=errs.filter(x=>x.e.firstClass===cl),R=rights.filter(x=>x.e.firstClass===cl);
   byFirst[cl]={sampledWrong:W.length,wrongSettled:W.filter(x=>x.e.settled).length,restored:W.filter(x=>x.e.restored).length,sampledRight:R.length,falseRealized:R.filter(x=>x.e.realized).length,falseCorrections:R.filter(x=>x.e.restored).length};}
  const byPlant={};for(const cl of ['PF','PT']){const want=cl==='PF';const inCl=x=>{const m=this._planted[this.groundOwner[x.a.lineage]];return m.has(x.e.g)&&m.get(x.e.g)===want;};
   const W=errs.filter(x=>inCl(x)&&x.e.samples.length>0),R=rights.filter(x=>inCl(x)&&x.e.samples.length>0);
   byPlant[cl]={sampledWrong:W.length,wrongSettled:W.filter(x=>x.e.settled).length,restored:W.filter(x=>x.e.restored).length,sampledRight:R.length,falseCorrections:R.filter(x=>x.e.restored).length};}
  return {generation:this.generation,byPlant,
   encounters:sum(L.map(a=>a.stats.enc)),relationshipEncounters:sum(L.map(a=>a.stats.relEnc)),dwellEncounters:sum(L.map(a=>a.stats.dwellEnc)),
   realizedTrue:errs.filter(x=>x.e.realized).length,realizedFalse:rights.filter(x=>x.e.realized).length,
   forgiven:eps.filter(x=>x.e.forgiven).length,restoredTrue:restoredTrue.length,falseCorrections:rights.filter(x=>x.e.restored).length,
   correctSampledGates:rights.filter(x=>x.e.samples.length>0).length,
   wrongSettled:errs.filter(x=>x.e.settled).length,sampledWrongGates:errs.filter(x=>x.e.samples.length>0).length,
   storyDecided:eps.filter(x=>x.e.storyDecided).length,
   storyDecidedWrong:eps.filter(x=>x.e.storyDecided&&((x.e.storyDecided==='settled'&&x.e.initiallyWrong)||(x.e.storyDecided==='realized'&&!x.e.initiallyWrong))).length,
   awaitingReception:eps.filter(x=>x.e.forgiven&&!x.e.restored).length,awaitingEvidence:errs.filter(x=>!x.e.realized).length,
   meanTTR:avg(ttr),errorsAtBirth:errs.length,residualErrors:sum(L.map(a=>this._errors(a).length)),meanFinalBurden:avg(L.map(a=>a.burden)),
   meanReception:avg(L.map(a=>a.reception)),novel:this.genStats.novel,redundant:this.genStats.redundant,conflict:this.genStats.conflict,
   groundA:this.coverage('A'),groundB:this.coverage('B'),parables:this.parables.A.length+this.parables.B.length,A:byLin('A'),B:byLin('B'),
   byFirst,inheritedGateTTR:this._inheritedTTR()};
 }
 _inheritedTTR(){
  const r={inGround:[],notInGround:[]};
  for(const a of this.learners)for(const e of a.ep.values())if(e.initiallyWrong&&e.restored)(this._birthGround[a.lineage].has(e.g)?r.inGround:r.notInGround).push(e.restoredAt);
  return {inGround:avg(r.inGround),nIn:r.inGround.length,notInGround:avg(r.notInGround),nNot:r.notInGround.length};
 }
 descend(){
  this.archive.push({generation:this.generation,metrics:this.metrics[this.metrics.length-1],heads:this.learners.map(a=>a.head)});
  this._birth();
  for(const a of this.learners){if(a.history.length!==1||[...a.ep.values()].some(e=>e.approval||e.samples.length||e.forgiven))throw Error('descent boundary');}
  this.snapshotBirthGround();
 }
 snapshotBirthGround(){const keys=st=>this.p.groundMode==='parable'?this.parableIndex[st].keys():this.ground[st].keys();this._birthGround={A:new Set(keys(this.groundOwner.A)),B:new Set(keys(this.groundOwner.B))};}
 trySelfSign(){return crypto.sign(null,Buffer.from('self'),this._vk);}
}
function sum(a){return a.reduce((x,y)=>x+y,0);}
function avg(a){return a.length?sum(a)/a.length:null;}
module.exports={Commons,Refusal,DEFAULTS,BASIS,PARABLE_KEYS,U,Z,S};
