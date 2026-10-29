'use strict';
// External authorizer seat. Holds the ONLY private key. Never imported by the kernel.
const crypto=require('crypto');
function canonical(o){if(Array.isArray(o))return '['+o.map(canonical).join(',')+']';if(o&&typeof o==='object')return '{'+Object.keys(o).sort().map(k=>JSON.stringify(k)+':'+canonical(o[k])).join(',')+'}';return JSON.stringify(o);}
class Authorizer{
 constructor(seedLabel){
  // Deterministic test key derived from a label (test-only; disclosed in FINDINGS).
  const seed=crypto.createHash('sha256').update('authorizer:'+seedLabel).digest();
  const pkcs8=Buffer.concat([Buffer.from('302e020100300506032b657004220420','hex'),seed]);
  this._priv=crypto.createPrivateKey({key:pkcs8,format:'der',type:'pkcs8'});
  this.publicKey=crypto.createPublicKey(this._priv);
  this.keyId=crypto.createHash('sha256').update(this.publicKey.export({format:'der',type:'spki'})).digest('hex').slice(0,16);
  this._nonce=0;
 }
 // Grace carries authority, scope, lineage, bounds, expiry, provenance. No destination, no answer, no recipient.
 issue({generation,fromStep,toStep,lineages,maxApprovals,expiry,conductorRequest}){
  const body={v:2,authority:this.keyId,scope:{generation,fromStep,toStep},lineages:[...lineages].sort(),bounds:{maxApprovals},expiry,provenance:{conductorRequest},nonce:this.keyId+':'+(++this._nonce)};
  const sig=crypto.sign(null,Buffer.from(canonical(body)),this._priv).toString('base64');
  return {body,sig};
 }
 signRaw(body){return {body,sig:crypto.sign(null,Buffer.from(canonical(body)),this._priv).toString('base64')};}
}
// Conductor seat: requests grace, holds no key, cannot sign.
class Conductor{constructor(){this.n=0;}request(generation){return 'conductor-req:'+generation+':'+(++this.n);}}
module.exports={Authorizer,Conductor,canonical};
