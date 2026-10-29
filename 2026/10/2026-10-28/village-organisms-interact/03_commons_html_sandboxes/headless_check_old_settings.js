const XR=2.2,YR=1.4,GX=76,GY=48,h=2*XR/(GX-1);
const rng=s=>()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};
function W(seed){return{T:new Float32Array(GX*GY),r:rng(seed),o:[]};}
function terr(w,x,y){const fi=Math.min(GX-1.001,Math.max(0,(x+XR)/(2*XR)*(GX-1))),fj=Math.min(GY-1.001,Math.max(0,(y+YR)/(2*YR)*(GY-1)));
 const i=Math.floor(fi),j=Math.floor(fj),u=fi-i,v=fj-j,T=w.T;return(1-u)*(1-v)*T[j*GX+i]+u*(1-v)*T[j*GX+i+1]+(1-u)*v*T[(j+1)*GX+i]+u*v*T[(j+1)*GX+i+1];}
function dep(w,x,y,amt,rad){const R=rad*3;for(let j=0;j<GY;j++)for(let i=0;i<GX;i++){const px=i/(GX-1)*2*XR-XR,py=j/(GY-1)*2*YR-YR,d2=(px-x)**2+(py-y)**2;if(d2<R*R)w.T[j*GX+i]=Math.max(-.95,w.T[j*GX+i]-amt*Math.exp(-d2/(2*rad*rad)));}}
const L=[[1.3,.6,-1.1,-.8],[.7,1.7,-1.1,.8],[1.0,1.1,-.8,0],[1.8,.4,-1.4,.2]];
function spawn(w,jit,n){for(const[ev,gr,hx,hy]of L)for(let k=0;k<n;k++){const m=()=>1+(jit()-.5)*.25;w.o.push({x:hx+(jit()-.5)*.5,y:hy+(jit()-.5)*.5,ev:ev*m(),gr:gr*m(),wear:0,reached:false});}}
function run(w,steps,graceAt,wind){const dt=.016*1.6;for(let s=0;s<steps;s++){const open=graceAt.some(([a,b])=>s>=a&&s<b);
 for(const o of w.o){let fx=-2*o.x*(o.x*o.x-1)-o.gr*(terr(w,o.x+h,o.y)-terr(w,o.x-h,o.y))/(2*h)+o.ev*wind,fy=-.7*o.y-o.gr*(terr(w,o.x,o.y+h)-terr(w,o.x,o.y-h))/(2*h);
  let nx=o.x+dt*fx+Math.sqrt(dt)*.18*(w.r()*2-1),ny=Math.max(-YR+.05,Math.min(YR-.05,o.y+dt*fy+Math.sqrt(dt)*.18*(w.r()*2-1)));nx=Math.max(-XR+.05,Math.min(XR-.05,nx));
  const c=(o.x<=0)!==(nx<=0);if(c&&!open)nx=o.x<=0?-.004:.004;else if(c&&open)dep(w,0,ny,.055,.17);
  if(Math.abs(nx)<.05)o.reached=true;o.x=nx;o.y=ny;o.wear+=dt;if(o.wear>.12){o.wear=0;dep(w,nx,ny,.010,.28);}}}}
const f=W(11);spawn(f,f.r,4);run(f,1500,[[400,460],[900,960],[1300,1360]],0.60);
const sat=f.T.filter(v=>v<-.9).length/f.T.length;console.log('founders: saturated fraction',sat.toFixed(3),'min',Math.min(...f.T).toFixed(2));
const lived=W(77);lived.T.set(f.T);const fresh=W(77);const sc=W(77);const r=rng(9),ord=[...f.T.keys()];for(let i=ord.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[ord[i],ord[j]]=[ord[j],ord[i]];}ord.forEach((k,i)=>sc.T[i]=f.T[k]);
for(const[n,w]of[['lived',lived],['fresh',fresh],['scattered',sc]]){spawn(w,rng(4242),3);run(w,1200,[],0.60);console.log(n,'reached fence',w.o.filter(o=>o.reached).length+'/12');}
