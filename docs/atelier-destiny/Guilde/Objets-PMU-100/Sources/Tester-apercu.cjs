'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const os=require('node:os');const path=require('node:path');const crypto=require('node:crypto');
const H=os.homedir(),O=path.resolve(__dirname,'..'),W=path.join(H,'.cache/guilde-objets');
const pw=process.env.PLAYWRIGHT_MODULE||path.join(H,'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright');
const {chromium}=require(pw);const base=process.env.ATLAS_TEST_URL||'http://127.0.0.1:4176';const exe=process.env.CHROMIUM||path.join(H,'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const digest=a=>crypto.createHash('sha256').update(a).digest('hex');
const phase=(p,n)=>p.locator(`[data-atlas-phase="${n}"]`).click();
const frame=async(p)=>p.evaluate(()=>new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done))));
async function atl(p,i){await frame(p);await p.waitForFunction(i=>{const a=[...document.querySelectorAll('.atlas-map')];return a.length===15&&a.every(c=>c.dataset.scene?.split(':')[1]===String(i));},i);}
async function caps(p){return p.locator('canvas.atlas-map').evaluateAll(c=>c.map(x=>x.toDataURL()));}
async function scene(p,id){await frame(p);await p.waitForFunction(id=>document.querySelector('#map').dataset.scene===id,id);}
async function download(p,button){const [item]=await Promise.all([p.waitForEvent('download'),p.locator(button).click()]);const file=await item.path();assert.equal(await item.failure(),null);return [item.suggestedFilename(),fs.readFileSync(file)];}
(async()=>{
const browser=await chromium.launch({executablePath:exe,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
try{
 const c=await browser.newContext({viewport:{width:1430,height:950},acceptDownloads:true});const p=await c.newPage(),ref=await c.newPage();const errors=[];
 p.on('pageerror',e=>errors.push(e.message));ref.on('pageerror',e=>errors.push(e.message));
 await p.goto(base);await ref.goto(base+'/reference-sans-verdure');
 assert.match(await p.title(),/Reverie/);assert.equal(await p.locator('#toggle-lianes').getAttribute('aria-pressed'),'true');
 const metadata=await p.evaluate(()=>{const d=JSON.parse(document.querySelector('#donnees').textContent);return {rooms:d.rooms.length,gates:d.rooms.reduce((n,r)=>n+r.gates.length,0),cuts:d.rooms.filter(r=>r.south?.band).length,newObjects:d.catalog.filter(o=>o.collection==='pmu100').length,oldObjects:d.catalog.filter(o=>!o.collection).length};});
 assert.deepEqual(metadata,{rooms:15,gates:29,cuts:7,newObjects:100,oldObjects:33});
 await p.locator('#toggle-lianes').click();const different=[],exact=[];let nightBare=[];
 for(let i=0;i<4;i++){
  await Promise.all([phase(p,i),phase(ref,i)]);await Promise.all([atl(p,i),atl(ref,i)]);
  const [no,orig]=await Promise.all([caps(p),caps(ref)]);assert.deepEqual(no.map(digest),orig.map(digest));exact.push(no.length);
  await p.locator('#toggle-lianes').click();await atl(p,i);const withVines=await caps(p);
  let n=0;for(let k=0;k<15;k++)if(digest(no[k])!==digest(withVines[k]))n++;assert.equal(n,15);different.push(n);
  if(i===3)nightBare=no;
  else await p.locator('#toggle-lianes').click();
 }
 const illumination=await p.evaluate(async(old)=>{
  const d=JSON.parse(document.querySelector('#donnees').textContent);const maps=[...document.querySelectorAll('.atlas-map')];const load=async src=>{const im=new Image();im.src=src;await im.decode();return im;};
  return Promise.all(d.rooms.map(async(r,i)=>{
    const w=r.w,h=r.h,out=maps[i].getContext('2d').getImageData(0,0,w,h).data;
    const cv=document.createElement('canvas');cv.width=w;cv.height=h;const g=cv.getContext('2d',{willReadFrequently:true});g.drawImage(await load(old[i]),0,0);const off=g.getImageData(0,0,w,h).data;
    g.clearRect(0,0,w,h);const v=d.lianes[r.id];g.drawImage(await load(v.s),0,0);g.drawImage(await load(v.t),0,0);const mask=g.getImageData(0,0,w,h).data;
    let boards=0,total=0,gate=0,bottom=0;
    for(let y=0;y<h;y++)for(let x=0;x<w;x++){
      const j=(y*w+x)*4;let diff=0;for(let k=0;k<3;k++)diff+=([.2126,.7152,.0722][k])*(out[j+k]-off[j+k]);
      if(!mask[j+3]&&diff>=7){total++;if(r.floor[y>>3]?.[x>>3]==='1')boards++;}
      if(out[j]!==off[j]||out[j+1]!==off[j+1]||out[j+2]!==off[j+2]){
        if(r.gates.some(({rect:[rx,ry,a,b]})=>x>=rx&&y>=ry&&x<rx+a&&y<ry+b))gate++;
        if(r.south&&r.south.band&&y>=r.south.bottom)bottom++;
      }
    }
    return {nom:r.label,plancher:boards,decor:total,pixels_seuils_changes:gate,pixels_bande_sud_changes:bottom};
  }));
 },nightBare);
 assert.equal(illumination.length,15);assert(illumination.every(r=>r.decor>2400&&r.plancher>1000&&r.pixels_seuils_changes===0&&r.pixels_bande_sud_changes===0),JSON.stringify(illumination));
 await p.screenshot({path:path.join(W,'Nuit-ensemble.png')});
 await p.locator('#tab-south').click();await frame(p);await p.waitForFunction(()=>[...document.querySelectorAll('.atlas-crop')].length===14&&[...document.querySelectorAll('.atlas-crop')].every(c=>c.dataset.scene));
 const cuts=await p.evaluate(()=>Array.from(document.querySelectorAll('.atlas-pair'),p=>{
  const r=JSON.parse(document.querySelector('#donnees').textContent).rooms.find(r=>r.id===p.dataset.south);
  const [a,b]=p.querySelectorAll('canvas'),n=r.south.band;
  const old=a.getContext('2d').getImageData(0,0,320,240-n).data;const now=b.getContext('2d').getImageData(0,n,320,240-n).data;
  return a.width===320&&a.height===240&&b.width===320&&b.height===240&&old.every((n,j)=>n===now[j]);
 }));assert.equal(cuts.length,7);assert(cuts.every(Boolean));
 await p.locator('#tab-work').click();await scene(p,'guilde_destiny_accueil:3:0:0');
 assert.equal(await p.locator('#catalog button.asset').count(),100);
 await p.locator('#collection').selectOption('origine');assert.equal(await p.locator('#catalog button.asset').count(),33);assert(await p.locator('#palette-pmu').isDisabled());
 await p.locator('#collection').selectOption('pmu100');await p.locator('#palette-pmu').selectOption('sauge');assert.equal(await p.locator('#catalog button.asset').count(),25);
 await p.locator('#filters').getByRole('button',{name:'Tapis',exact:true}).click();assert.equal(await p.locator('#catalog button.asset').count(),5);
 await p.locator('#filters').getByRole('button',{name:'Tout',exact:true}).click();await p.locator('#query').fill('lampe');assert.equal(await p.locator('#catalog button.asset').count(),1);
 await p.locator('#compare').click();await frame(p);await p.waitForFunction(()=>[...document.querySelectorAll('#compare-view canvas')].every(c=>c.dataset.scene));
 assert.equal(await p.locator('#compare-view canvas:visible').count(),4);await p.locator('#compare').click();
 await p.locator('[data-asset="pmu100_lampe_sauge"]').click();await p.getByRole('button',{name:'Poser au centre'}).click();await scene(p,'guilde_destiny_accueil:3:0:1');
 await p.locator('#export').click();assert(await p.locator('#download-ground').isDisabled());
 const [pn,px]=await download(p,'#download-png');assert.match(pn,/-lianes\.png$/);assert.equal(px.readUInt32BE(16),512);assert.equal(px.readUInt32BE(20),384);
 const [jn,jx]=await download(p,'#download-plan');assert.match(jn,/\.json$/);const saved=JSON.parse(jx);assert.equal(saved.salles.guilde_destiny_accueil[0].meuble,'pmu100_lampe_sauge');
 await p.locator('#export-box .close-dialog').click();await p.locator('#toggle-lianes').click();await p.locator('#export').click();
 const [nn,nx]=await download(p,'#download-png');assert(!nn.includes('-lianes'));assert.notEqual(digest(px),digest(nx));
 await p.locator('#export-box .close-dialog').click();await p.locator('#undo').click();await scene(p,'guilde_destiny_accueil:3:0:0');
 await p.locator('#layout-file').setInputFiles({name:'test-plan.json',mimeType:'application/json',buffer:jx});await scene(p,'guilde_destiny_accueil:3:0:1');
 const mob=await c.newPage();await mob.setViewportSize({width:390,height:844});await mob.goto(base);await atl(mob,0);
 const fit=async q=>q.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1);
 assert(await fit(mob));await mob.locator('#tab-work').click();assert(await fit(mob));await mob.locator('#room-select').selectOption('guilde_destiny_refectoire');await scene(mob,'guilde_destiny_refectoire:0:0:0');
 const content=fs.readFileSync(path.join(O,'..','Guilde-Destiny-Lianes-et-PMU-100.html'),'utf8');
 await mob.setContent('<iframe id="preview" sandbox="allow-scripts" style="width:100%;height:720px;border:0"></iframe>');
 await mob.locator('#preview').evaluate((el,h)=>el.srcdoc=h,content);const f=mob.frameLocator('#preview');await f.locator('.atlas-map').last().waitFor();
 await f.locator('[data-atlas-phase="3"]').click();await f.locator('.atlas-map').last().evaluate(el=>new Promise((done,reject)=>{function ready(){if(el.dataset.scene?.split(':')[1]==='3')done();else requestAnimationFrame(ready);}ready();setTimeout(()=>reject(new Error('Attente de la Nuit dans le cadre sandbox')),7000);}));
 assert.deepEqual(errors,[]);
 const report={statut:'PASS',...metadata,phases:4,vues_identiques_reference_sans_lianes:exact.reduce((a,b)=>a+b,0),vues_lianes:different.reduce((a,b)=>a+b,0),cadrages_nuit_320x240:cuts.length,illumination,atelier:'Filtres, pose, annulation, import JSON, exports PNG avec/sans, blocage natif des nouveaux sprites',mobile_390px:true,iframe_autonome:true};
 fs.writeFileSync(path.join(O,'Tests-apercu.json'),JSON.stringify(report,null,2)+'\n');console.log('PASS · 60 vues identiques sans lianes ; 60 vues enrichies ; 15 sols éclairés ; 7 cadres sud intacts ; atelier, PNG, mobile et iframe.');
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
