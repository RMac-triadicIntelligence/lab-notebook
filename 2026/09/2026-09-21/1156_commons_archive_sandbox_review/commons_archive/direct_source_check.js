// Executes functions extracted verbatim from archived HTML, without rendering.
const fs = require('fs');
const vm = require('vm');
const results = { sampler: {}, actual_v2_1_core: [] };
for (const file of ['the_commons_v1_0.html','the_commons_v1_1.html','the_commons_ii_v2_0.html','the_commons_ii_v2_1.html']) {
  const html = fs.readFileSync(file, 'utf8');
  const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
  const prefix = script.slice(0, script.indexOf('function renderGround('));
  const second = file.includes('_ii_');
  const elements = new Map();
  const context = vm.createContext({document:{getElementById(id) {
    if (!elements.has(id)) elements.set(id,{width:800,height:500,value:'0',getContext:()=>({})});
    return elements.get(id);
  }}, emit:(x)=>{results.sampler[file]=x;}, emitCore:(x)=>results.actual_v2_1_core.push(x)});
  const check = `
    const testWorld = ${second ? "new World('test','test',1)" : 'null'};
    const testT = ${second ? 'testWorld.T' : 'T'};
    for(let j=0;j<GY;j++)for(let i=0;i<GX;i++)testT[j*GX+i]=0.2*(i/(GX-1)*2*XR-XR)-0.3*(j/(GY-1)*2*YR-YR);
    let maxError=0, zeroX=0, zeroY=0;
    for(let k=0;k<1000;k++){
      const x=-1.8+3.6*((k*0.61803398875)%1),y=-1+2*((k*0.41421356237)%1);
      const o={x,y,ev:0,ground:1,lesson:1,lessons:[]};
      const [fx,fy]=${second ? 'forceOn(testWorld,o)' : 'forceOn(o)'};
      const tx=fx+2*x*(x*x-1),ty=fy+0.7*y;
      maxError=Math.max(maxError,Math.abs(tx+0.2),Math.abs(ty-0.3));
      zeroX+=Math.abs(tx)<1e-10;zeroY+=Math.abs(ty)<1e-10;
    }
    emit({planar_force_max_abs_error:maxError,zero_x_fraction:zeroX/1000,zero_y_fraction:zeroY/1000,points:1000});
  `;
  const actualCore = file === 'the_commons_ii_v2_1.html' ? `
    for(const sd of [0,1,2,3]) {
      const f=new World('founders','',11+sd);
      LINEAGES.forEach(L=>{for(let k=0;k<4;k++)f.spawn(L,1,f.rand);});
      windEl.value=0.75;
      for(let s=0;s<1500;s++){
        graceT=[[400,460],[900,960],[1300,1360]].some(([a,b])=>a<=s&&s<b)?1:0;
        stepWorld(f,0.0256);
      }
      const row={seed:sd,saturation:f.T.filter(v=>v<-.9).length/f.T.length,founder_crossings:f.tally.crossed,worlds:{}};
      for(const kind of ['lived','fresh','shifted']){
        const w=new World(kind,'',77+sd);
        if(kind==='lived')w.T.set(f.T);
        if(kind==='shifted')for(let j=0;j<GY;j++)for(let i=0;i<GX;i++)w.T[((j+Math.floor(GY*.35))%GY)*GX+i]=f.T[j*GX+i];
        const jit=rng(4242+sd);LINEAGES.forEach(L=>{for(let k=0;k<3;k++)w.spawn(L,2,jit);});
        const reached=new Set();windEl.value=0.55;graceT=0;
        for(let s=0;s<1200;s++){
          stepWorld(w,0.0256);
          w.orgs.forEach(o=>{if(Math.abs(o.x)<.05)reached.add(o.id);});
        }
        row.worlds[kind]={reached:reached.size,closed_gate_crossings:w.tally.crossed};
      }
      emitCore(row);
    }
  ` : '';
  vm.runInContext(prefix + check + actualCore + '\n})();',context,{timeout:120000});
}
results.actual_v2_1_means = Object.fromEntries(['lived','fresh','shifted'].map(k=>[k,results.actual_v2_1_core.reduce((s,r)=>s+r.worlds[k].reached,0)/4]));
console.log(JSON.stringify(results,null,2));
