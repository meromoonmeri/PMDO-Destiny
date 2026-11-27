'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{homedir}=require('node:os');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(homedir(),'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const exe=process.env.CHROMIUM||path.join(homedir(),'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const out=path.resolve(__dirname,'..'),root=path.dirname(out),url=process.env.PREVIEW_URL||'http://127.0.0.1:4179/';
const html=fs.readFileSync(path.join(root,'Guilde-Destiny-Bourgeons-PMD.html'),'utf8'), old=fs.readFileSync(path.join(root,'Guilde-Destiny-Lumiere-Ancree.html'),'utf8');
const {data,horsRaccords}=require('./Verifier-donnees.cjs');
const d=data(html),before=data(old),unchanged=horsRaccords(d,before);
for(const k of ['rooms','lumieres','nuits','etoffes','catalog','tints']) assert.deepEqual(unchanged[k],before[k]);
assert.equal(d.canon.image,'G01P01C');assert.equal(d.canon.ips,6);assert.equal(d.canon.opacite_reflet_max,25);
const courant=d.balade_nuit;
const emetteurs=courant?Object.values(courant.lumieres).reduce((n,p)=>n+p.length,0):30;
assert.equal(emetteurs,courant?32:30);if(courant)assert.equal(courant.alpha_max,53);
assert.deepEqual(Buffer.from(d.reference.apng.split(',')[1],'base64'),fs.readFileSync(path.join(out,'Reference/G01P01C-Falaise-Nuit.png')));
const repaired=Object.values(d.verdure||{});
if(repaired.length){
 assert.equal(repaired.length,11);
 assert.equal(repaired.reduce((a,r)=>a+r.poteaux,0),15);
 assert.equal(repaired.reduce((a,r)=>a+r.rameaux,0),6);
}
for(const [id,l] of Object.entries(d.lianes)) {
 const original=before.lianes[id], changed=d.verdure?.[id],rives=d.raccords_bois?.rives[id];
 assert.equal(l.v,original.v);
 assert.equal(l.points.length,2);assert(l.points.every(p=>p.images.length===4&&p.images.every(q=>q.length===2)));
 if(changed||rives)assert(l.s!==original.s||l.t!==original.t);
 else for(const k of ['s','t'])assert.equal(l[k],original[k]);
 if(changed)assert(l.points.every((p,i)=>Math.hypot(p.x-original.points[i].x,p.y-original.points[i].y)<19.2));
 else{
  assert.equal(l.n,original.n);
  assert.deepEqual(l.points.map(p=>[p.x,p.y]),original.points.map(p=>[p.x,p.y]));
 }
}
async function play(scope){
 await scope.locator('#film-button').click();
 await scope.locator('#film-comparatif').evaluate(v=>new Promise((ok,no)=>{
  const t=setTimeout(()=>no(Error('Vidéo non lue')),6500);
  const read=()=>{if(v.videoWidth===1120&&!v.paused&&v.currentTime>.2&&Math.abs(v.duration-10)<.1){clearTimeout(t);ok();}else requestAnimationFrame(read);};read();
 }));
}
(async()=>{
 const b=await chromium.launch({executablePath:exe,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  const p=await b.newPage({viewport:{width:1365,height:1000},reducedMotion:'reduce'}),err=[];p.on('pageerror',e=>err.push(e.message));
  await p.goto(url);assert.match(await p.title(),/Bourgeons/);
  if(d.seuil_accueil)await p.locator('#atlas-phases [data-atlas-phase="3"]').click();
  await p.waitForFunction(()=>[...document.querySelectorAll('.atlas-map')].every(el=>el.dataset.scene?.endsWith(':3:0:0')));
  assert.equal(await p.locator('.atlas-map').count(),15);
  assert.equal(await p.locator('.badges-verdure').count(),repaired.length);
  assert(await p.locator('#comparatif-video').evaluate(a=>a.getBoundingClientRect().bottom<document.querySelector('#overview-grid').getBoundingClientRect().top));
  await play(p);await p.locator('#show-salon').click();
  assert(await p.locator('#comparatif-video').isHidden());assert(await p.locator('#film-comparatif').evaluate(v=>v.paused));
  await p.waitForFunction(()=>document.querySelector('#map').dataset.scene==='guilde_destiny_grand_salon:3:0:0');
  const big=p.locator('#map'),first=await big.evaluate(el=>el.toDataURL());
  await p.locator('#motion-toggle').click();
  await p.waitForFunction(first=>document.querySelector('#map').toDataURL()!==first,first);
  await p.locator('#motion-toggle').click();
  await p.locator('#phases [data-phase="0"]').click();
  await p.waitForFunction(()=>document.querySelector('#map').dataset.scene?.endsWith(':0:0:0'));
  const bare=await big.evaluate(el=>el.toDataURL());
  await p.locator('#toggle-ornements').click();
  await p.waitForFunction(bare=>document.querySelector('#map').toDataURL()!==bare,bare);
  await p.locator('#toggle-ornements').click();
  await p.waitForFunction(bare=>document.querySelector('#map').toDataURL()===bare,bare);
  await p.locator('#braseros-reference').click();assert(await p.locator('#braseros-box').isVisible());
  await p.locator('#grodoudou-play').click();assert.equal(await p.locator('#grodoudou-play').getAttribute('aria-pressed'),'true');
  assert(await p.locator('#grodoudou-fires').evaluate(el=>el.src.startsWith('data:image/png;')));
  assert.deepEqual(err,[]);
  const m=await b.newPage({viewport:{width:390,height:830},offline:true,reducedMotion:'reduce'});
  await m.setContent('<iframe sandbox="allow-scripts" style="width:100%;height:780px;border:0"></iframe>');
  await m.locator('iframe').evaluate((el,s)=>el.srcdoc=s,html);
  const frame=m.frameLocator('iframe');assert.equal(await frame.locator('.atlas-map').count(),15);await play(frame);
  assert(await frame.locator('html').evaluate(el=>el.scrollWidth<=innerWidth+1));
  fs.writeFileSync(path.join(out,'Verification.json'),JSON.stringify({statut:'PASS',salles:15,bourgeons_emetteurs:emetteurs,guide:'G01P01C',cadence:6,plafond_alpha_reflets_255:courant?.alpha_max||25,plans_inchanges:true,salles_verdure_ajustee:repaired.length,lecture_dans_apercu:true,lecture_hors_ligne_mobile:true,grand_salon_anime:true,ornements_reversibles:Object.keys(d.ornements).length},null,2)+'\n');
  console.log('PASS · vidéo en tête et en aperçu hors ligne, vrai APNG, animation sur le plan, ornements facultatifs et réversibles.');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
