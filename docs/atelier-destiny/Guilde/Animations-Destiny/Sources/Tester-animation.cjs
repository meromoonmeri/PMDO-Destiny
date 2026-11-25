'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),home=require('node:os').homedir();
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(home,'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const exe=process.env.CHROMIUM||path.join(home,'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const url=process.env.ATLAS_TEST_URL||'http://127.0.0.1:4177',out=path.resolve(__dirname,'..');
const cv='.atlas-map';
const redraw=p=>p.evaluate(()=>new Promise(ok=>requestAnimationFrame(()=>requestAnimationFrame(ok))));
const waitAtlas=async(p,n)=>{await redraw(p);await p.waitForFunction(([cv,n])=>{const el=[...document.querySelectorAll(cv)];return el.length===15&&el.every(c=>c.dataset.scene?.endsWith(':'+n+':0:0'));},[cv,n],{timeout:10000});};
const captures=(p,s)=>p.locator(s).evaluateAll(nodes=>nodes.map(c=>{
 const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let h=2166136261;
 for(let i=0;i<d.length;i++)h=Math.imul(h^d[i],16777619);return h;
}));
const change=(p,s,states,n=states.length)=>p.waitForFunction(([s,states,n])=>{
 let k=0;for(const [j,c] of [...document.querySelectorAll(s)].entries()){
  const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let h=2166136261;for(let i=0;i<d.length;i++)h=Math.imul(h^d[i],16777619);
  if(h!==states[j])k++;
 }return k>=n;
},[s,states,n],{timeout:4500});
const assets=(p,id)=>p.locator('[data-asset="'+id+'"]');
const clickPhase=(p,n)=>p.locator(`[data-atlas-phase="${n}"]`).click();
const mapReady=async(p,phase,count)=>{await redraw(p);await p.waitForFunction(([phase,count])=>document.querySelector('#map').dataset.scene?.endsWith(':'+phase+':0:'+count),[phase,count],{timeout:10000});};
(async()=>{
 const b=await chromium.launch({executablePath:exe,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  const p=await b.newPage({viewport:{width:1590,height:1450},acceptDownloads:true}),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(url,{waitUntil:'domcontentloaded'});await waitAtlas(p,3);assert.match(await p.title(),/Nuit vivante/);
  const dims=await p.evaluate(()=>{const d=JSON.parse(document.getElementById('donnees').textContent),l=Object.values(d.lianes);return {salles:d.rooms.length,passages:d.rooms.reduce((m,r)=>m+r.gates.length,0),cadrages:d.rooms.filter(x=>x.south?.band).length,poteaux:l.reduce((t,v)=>t+v.v,0),gestes:l.every(x=>x.g.length===4&&x.o.length===2),variantes:Object.keys(d.etoffes).length};});
  assert.equal(dims.salles,15);assert.equal(dims.passages,29);assert.equal(dims.variantes,12);assert(dims.gestes&&dims.poteaux>=38);
  const on=await captures(p,cv);await change(p,cv,on);console.log('PASS · les 15 salles varient en Nuit, sans placement préalable.');
  const motion=p.locator('#motion-toggle');await motion.click();await redraw(p);assert.equal(await motion.getAttribute('aria-pressed'),'false');const frozen=await captures(p,cv);
  await new Promise(done=>setTimeout(done,420));assert.deepEqual(await captures(p,cv),frozen);
  const withLights=await p.locator(cv).evaluateAll(nodes=>nodes.map(c=>c.toDataURL()));
  await p.locator('#toggle-lianes').click();await waitAtlas(p,3);const plain=await captures(p,cv);
  // Geometry and actual lighting in the browser: compare gates/camera, and count reflected light on bare wood.
  const pixels=await p.evaluate(async(active)=>{
   const layers=JSON.parse(document.getElementById('donnees').textContent);const grid=[...document.querySelectorAll('.atlas-map')];
   const load=async src=>{const im=new Image();im.src=src;await im.decode();return im;};
   return Promise.all(layers.rooms.map(async(r,i)=>{
    const w=r.w,h=r.h,off=grid[i].getContext('2d').getImageData(0,0,w,h).data,cv=document.createElement('canvas');cv.width=w;cv.height=h;const c=cv.getContext('2d');
    c.drawImage(await load(active[i]),0,0);const on=c.getImageData(0,0,w,h).data;c.clearRect(0,0,w,h);c.drawImage(await load(layers.lianes[r.id].s),0,0);c.drawImage(await load(layers.lianes[r.id].t),0,0);const vine=c.getImageData(0,0,w,h).data;
    let board=0,gate=0,edge=0;
    for(let y=0;y<h;y++)for(let x=0;x<w;x++){
     const j=4*(y*w+x),dr=on[j]-off[j],dg=on[j+1]-off[j+1],db=on[j+2]-off[j+2];if((dr|dg|db)===0)continue;
     if(r.gates.some(({rect:[a,b,w,h]})=>x>=a&&y>=b&&x<a+w&&y<b+h))gate++;
     if(r.south?.band&&y>=r.south.bottom)edge++;
     if(!vine[j+3]&&r.floor[y>>3]?.[x>>3]==='1'&&.2126*dr+.7152*dg+.0722*db>=5)board++;
    }
    return {salle:r.id,plancher_eclaire:board,px_seuils_changes:gate,px_bande_sud_changes:edge};
   }));
  },withLights);
  assert(pixels.every(x=>x.plancher_eclaire>1200&&!x.px_seuils_changes&&!x.px_bande_sud_changes),JSON.stringify(pixels));
  const ref=await b.newPage({viewport:{width:1590,height:1450}});await ref.goto(url+'/reference-sans-lianes');await clickPhase(ref,3);await waitAtlas(ref,3);assert.deepEqual(await captures(ref,cv),plain);
  let phases=1;for(const i of [0,1,2]){await clickPhase(p,i);await clickPhase(ref,i);await Promise.all([waitAtlas(p,i),waitAtlas(ref,i)]);assert.deepEqual(await captures(ref,cv),await captures(p,cv));phases++;}await ref.close();
  console.log('PASS · 60 plans sans lianes identiques, 29 passages intacts, les halos atteignent les planchers.');
  await p.locator('#toggle-lianes').click();await clickPhase(p,3);await p.locator('#tab-south').click();await redraw(p);await p.waitForFunction(()=>[...document.querySelectorAll('.atlas-crop')].every(c=>c.dataset.scene));
  const overlap=await p.locator('.atlas-pair').evaluateAll(nodes=>{const d=JSON.parse(document.getElementById('donnees').textContent);return nodes.map(box=>{
   const q=d.rooms.find(r=>r.id===box.dataset.south);const [a,b]=box.querySelectorAll('canvas');const m=q.south.band;
   if(!a||!b||a.width!==320||b.width!==320||a.height!==240||b.height!==240)return false;
   const i=a.getContext('2d').getImageData(0,0,320,240-m).data,j=b.getContext('2d').getImageData(0,m,320,240-m).data;return i.every((v,k)=>v===j[k]);
  });});assert.equal(overlap.length,7);assert(overlap.every(Boolean));
  await p.locator('#tab-work').click();await p.locator('#phases [data-phase="0"]').click();await mapReady(p,0,0);
  assert.equal(await p.locator('#catalog [data-anime]').count(),12);await p.locator('#palette-pmu').selectOption('grenat');assert.equal(await p.locator('#catalog [data-anime]').count(),3);
  const flag='destiny_hampe_grenat',thumb='[data-asset="'+flag+'"] canvas';await p.locator(thumb).waitFor({state:'visible'});
  const t0=await captures(p,thumb);await motion.click();await change(p,thumb,t0);
  await assets(p,flag).click();await p.getByRole('button',{name:'Poser au centre'}).click();await mapReady(p,0,1);const placed=await captures(p,'#map');await change(p,'#map',placed);
  await motion.click();await redraw(p);const mp=await captures(p,'#map');await new Promise(done=>setTimeout(done,260));assert.deepEqual(mp,await captures(p,'#map'));
  await p.locator('#export').click();assert(await p.locator('#download-ground').isDisabled());
  const [png]=await Promise.all([p.waitForEvent('download'),p.locator('#download-png').click()]);const bytes=fs.readFileSync(await png.path());assert.equal(bytes.readUInt32BE(16),512);assert.equal(bytes.readUInt32BE(20),384);
  const [j]=await Promise.all([p.waitForEvent('download'),p.locator('#download-plan').click()]);assert.equal(JSON.parse(fs.readFileSync(await j.path())).salles.guilde_destiny_accueil[0].meuble,flag);
  const mobile=await b.newPage({viewport:{width:395,height:844},reducedMotion:'reduce'});await mobile.goto(url);await waitAtlas(mobile,3);assert.equal(await mobile.locator('#motion-toggle').getAttribute('aria-pressed'),'false');
  assert(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  const reduced=await captures(mobile,cv);await new Promise(done=>setTimeout(done,300));assert.deepEqual(await captures(mobile,cv),reduced);
  await mobile.locator('#tab-work').click();assert(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  // Same offline viewer constraints: no data connection or storage required.
  const full=fs.readFileSync(path.resolve(out,'../Guilde-Destiny-Nuit-Vivante.html'),'utf8');
  await mobile.setContent('<iframe sandbox="allow-scripts" id="offline" style="width:100%;height:690px;border:none"></iframe>');await mobile.locator('#offline').evaluate((el,content)=>{el.srcdoc=content;},full);
  const sub=mobile.frameLocator('#offline');await sub.locator(cv).first().waitFor();assert.equal(await sub.locator(cv).count(),15);
  await sub.locator(cv).first().evaluate(el=>new Promise((resolve,reject)=>{const deadline=performance.now()+7500;function ready(){if(el.dataset.scene?.endsWith(':3:0:0'))resolve();else if(performance.now()>deadline)reject(new Error('Rendu nocturne dans iframe'));else requestAnimationFrame(ready);}ready();}));
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'Tests-nuit-vivante.json'),JSON.stringify({statut:'PASS',...dims,plans_sans_lianes_identiques:phases*15,salles_animees:15,phase_initiale:'Nuit',cadrages_identiques_dans_zone_commune:overlap.length,illumination:pixels,native_ground:'anciens objets seulement',atelier:'aperçu animé, pose manuelle, animation en Jour, arrêt lecture, export PNG et JSON',mobile_395:true,mouvement_reduit:true,iframe_hors_ligne:true},null,2)+'\n');
  console.log('PASS · 7 cadres · tissus en pose et catalogue · Pause · PNG/JSON · mobile et iframe autonome.');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
