'use strict';
const A=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{homedir}=require('node:os'),{createHash}=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(homedir(),'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const exe=process.env.CHROMIUM||path.join(homedir(),'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const O=path.resolve(__dirname,'..'),G=path.dirname(O),W=path.join(homedir(),'.cache/comptoirs-et-falaise');
const read=n=>fs.readFileSync(n,'utf8'),parse=h=>JSON.parse(h.split('<script id="donnees" type="application/json">')[1].split('</script>')[0]);
const text=read(path.join(G,'Guilde-Destiny-Comptoirs-et-Falaise.html')),base=read(path.join(G,'Guilde-Destiny-Mobilier-Halcyon-IA.html')),b=parse(base);
const {comptoirs,cliff,catalog,...d}=parse(text),k=JSON.parse(read(path.join(O,'Index-Comptoirs.json'))).orientations;
const sha=x=>createHash('sha256').update(x).digest('hex');
A.deepEqual({...d,catalog:catalog.slice(0,677)},b);A.equal(sha(base),'0f249392c60360f3c65e5db6b1ba7b691857445d7d4c9d50df0948889304204b');
const added=catalog.slice(677);A.equal(added.length,8);A.equal(new Set(added.map(v=>v.m[0])).size,8);A.equal(d.rooms.length,15);
for(const v of k){const a=added.find(a=>a.id===v.id),x=Buffer.from(a.m[0],'base64');A(a.previewOnly);A.deepEqual(x,fs.readFileSync(path.join(O,v.png)));A.equal(sha(x),v.sha256);}
const rooms=Object.keys(comptoirs.exemples),[hall,refectoire,cuisine]=rooms,carrefour=d.balade_nuit.depart, store='pmd-destiny:guilde:comptoirs-cliff:077:v1';
const demo=(p,r,n)=>p.locator(`#cf-plan[data-scene="${r}:${n}:0:1"]`).waitFor({state:'visible'});
const scene=(p,r,n,N=0)=>p.locator(`#map[data-scene="${r}:${n}:0:${N}"]`).waitFor({state:'visible'});
const outside=(p,n,s='0')=>p.locator(`#cliff-map[data-scene^="cliff:${n}:"][data-scene$=":${s}"]`).waitFor({state:'visible'});
const readLayout=p=>p.evaluate(k=>JSON.parse(localStorage.getItem(k)||'{"salles":{}}').salles,store);
const button=(p,name)=>p.getByRole('button',{name,exact:true});
const isVisible=(p,s)=>p.locator(s).isVisible();
const drawWait=p=>p.evaluate(()=>new Promise(res=>requestAnimationFrame(()=>requestAnimationFrame(res))));
const hashes=(p,sel)=>p.locator(sel).evaluateAll(cs=>cs.map(c=>{
 const p=new Uint32Array(c.getContext('2d').getImageData(0,0,c.width,c.height).data.buffer);
 let a=0x811c9dc5,b=5381;for(const v of p){a=Math.imul((a^v),16777619);b=Math.imul(b,31)+v|0;}return [a,b];
}));
async function activateAndWait(p,select,r,phase){await p.locator('#cf-room').selectOption(r);await p.locator(`[data-dir="${select}"]`).click();await demo(p,r,phase);}

(async()=>{
 const browser=await chromium.launch({executablePath:exe,args:['--no-sandbox','--disable-dev-shm-usage']});const errors=[];const reg=p=>{p.on('pageerror',e=>errors.push(e.stack));return p;};
 try{
  const p=reg(await browser.newPage({viewport:{width:1380,height:995},reducedMotion:'reduce',acceptDownloads:true}));p.setDefaultTimeout(7000);await p.goto(process.env.PREVIEW_URL||'http://127.0.0.1:4186/');await demo(p,hall,0);
  A.equal(await p.locator('[data-dir]').count(),8);A.deepEqual(await readLayout(p),{});
  const pngs=[];for(const v of k){
    await p.locator(`[data-dir="${v.direction}"]`).click();await drawWait(p);await demo(p,hall,0);pngs.push((await hashes(p,'#cf-plan'))[0]);
    A.equal(await p.locator(`[data-dir="${v.direction}"]`).getAttribute('aria-pressed'),'true');
  }
  A.equal(new Set(pngs.map(x=>String(x))).size,8);
  for(const r of rooms.slice(1)){await activateAndWait(p,'UpLeft',r,0);await p.locator('#cf-show-access').click();await drawWait(p);await p.locator('#cf-show-access').click();}
  A.deepEqual(await readLayout(p),{});const [png]=await Promise.all([p.waitForEvent('download'),p.locator('#cf-png').click()]);
  A.equal(png.suggestedFilename(),'Comptoir-Destiny-UpLeft.png');A.deepEqual(fs.readFileSync(await png.path()),fs.readFileSync(path.join(O,'PNG-1x/UpLeft.png')));
  await activateAndWait(p,'Down',hall,0);await p.locator('#cf-try').click();await scene(p,hall,0);A.deepEqual(await readLayout(p),{});
  A.equal(await p.locator('#collection').inputValue(),'comptoirs');A.equal(await p.locator('#catalog .asset').count(),8);
  const cv=p.locator('#map');
  async function clickPlan(x,y){const {w,h,cw,ch}=await cv.evaluate(c=>({w:c.width,h:c.height,cw:c.getBoundingClientRect().width,ch:c.getBoundingClientRect().height}));await cv.click({position:{x:1+x*(cw-2)/w,y:1+y*(ch-2)/h}});}
  await clickPlan(22,193);A((await p.locator('#toast').getAttribute('class')).includes('error'));A.deepEqual(await readLayout(p),{});
  await clickPlan(255,183);A.match(await p.locator('#toast').textContent(),/allée|seuil/);A.deepEqual(await readLayout(p),{});
  await button(p,'Poser comme dans l’exemple').click();await scene(p,hall,0,1);
  const a0=(await readLayout(p))[hall][0],d0=k[0];A.equal(a0.meuble,d0.id);A.deepEqual([a0.x,a0.y],comptoirs.exemples[hall][d0.id]);
  A(await p.locator('#download-ground').isDisabled());
  await p.locator('#cf-orientation').selectOption('comptoir-downright');
  const a1=(await readLayout(p))[hall][0],d1=k[1];A.equal(a1.meuble,d1.id);A.equal(a0.id,a1.id);A.deepEqual([a0.x+d0.pivot[0],a0.y+d0.pivot[1]],[a1.x+d1.pivot[0],a1.y+d1.pivot[1]]);
  await p.locator('#undo').click();A.deepEqual((await readLayout(p))[hall][0],a0);
  await p.locator('#redo').click();A.deepEqual((await readLayout(p))[hall][0],a1);
  await p.locator('#export').click();const [plan]=await Promise.all([p.waitForEvent('download'),p.locator('#download-plan').click()]);const json=fs.readFileSync(await plan.path());A.deepEqual(JSON.parse(json).salles[hall],[a1]);await p.keyboard.press('Escape');
  await p.locator('#undo').click();await p.locator('#undo').click();A.deepEqual(await readLayout(p),{});
  await p.locator('#layout-file').setInputFiles({name:'comptoir-layout.json',mimeType:'application/json',buffer:json});await scene(p,hall,0,1);
  A.deepEqual((await readLayout(p))[hall][0],a1);await p.reload();await p.locator('#tab-work').click();await scene(p,hall,0,1);
  await p.locator('#phases [data-phase="3"]').click();await scene(p,hall,3,1);
  A(await p.locator('#accesses [data-passage="EscalierNord"]').isDisabled());
  await p.locator('#accesses [data-passage="SortieGuilde"]').click();await outside(p,3);
  A.equal(await p.locator('#cliff-state').textContent(),'Deux braseros allumés');
  const getCliff=async()=>p.locator('#cliff-map').evaluate(c=>{const data=c.getContext('2d').getImageData(0,0,480,520).data;let h=2166136261,m=5381;for(let i=0;i<data.length;i+=4){const x=i/4%480,y=(i/4-x)/480;const a=data[i]+256*data[i+1]+65536*data[i+2];h=Math.imul(h^a,16777619);if(y>=346||y<228||x>=218&&x<263)m=Math.imul(m,31)+a|0;}return {h,m};});
  const yes=await getCliff();await p.locator('#cliff-toggle').click();await outside(p,3,'nu');const no=await getCliff();A.notEqual(yes.h,no.h);A.equal(yes.m,no.m);
  await p.locator('#cliff-toggle').click();await outside(p,3);A.deepEqual(await getCliff(),yes);
  await p.locator('#braseros-reference').click();await p.waitForFunction(()=>document.querySelector('#destiny-foyers').complete&&document.querySelector('#destiny-foyers').naturalHeight===520);A.equal(await p.locator('#grodoudou-fires').evaluate(i=>i.naturalHeight),408);await p.keyboard.press('Escape');
  const [photo]=await Promise.all([p.waitForEvent('download'),p.locator('#cliff-save').click()]);const pic=fs.readFileSync(await photo.path());A.deepEqual([pic.readUInt32BE(16),pic.readUInt32BE(20)],[480,520]);A.equal(photo.suggestedFilename(),'Cliff-Destiny-nuit-braseros.png');
  await p.locator('#motion-toggle').click();
  const anim=await p.evaluate(()=>new Promise(resolve=>{const poses=new Set(),mer=new Set(),t=performance.now(),cv=document.querySelector('#cliff-map');function tick(){const [,p,m,f]=cv.dataset.scene.split(':');if(p==='3'){poses.add(f);mer.add(m);}if((poses.size===4&&mer.size>=6)||performance.now()-t>1500)resolve([Array.from(poses),Array.from(mer)]);else requestAnimationFrame(tick);}tick();}));A.deepEqual(anim[0].sort(),['0','1','2','3']);A(anim[1].length>=6);
  await p.locator('#motion-toggle').click();await drawWait(p);const still=await p.locator('#cliff-map').getAttribute('data-scene');await p.waitForTimeout(320);A.equal(await p.locator('#cliff-map').getAttribute('data-scene'),still);
  for(const n of [0,1,2]){await p.locator(`#cliff-phases [data-cf-phase="${n}"]`).click();await outside(p,n);A.equal(await p.locator('#cliff-map').getAttribute('data-flamme'),'éteinte');}
  await p.locator('#cliff-door').click();await scene(p,hall,2,1);
  await p.locator('#accesses [data-passage="SortieGuilde"]').click();await outside(p,2);
  await p.locator('#cliff-return').click();await scene(p,hall,2,1);
  // The old writing, workshop data and canvases all match when rendered without new items.
  await p.evaluate(k=>localStorage.removeItem(k),store);await p.reload();await p.locator('#tab-all').click();
  const collect=async(q)=>{const out=[];for(const phase of [0,1,2,3]){
    await q.locator(`[data-atlas-phase="${phase}"]`).evaluate(b=>b.click());
    await q.waitForFunction(n=>[...document.querySelectorAll('.atlas-map')].filter(c=>c.dataset.scene?.split(':')[1]===String(n)).length===15,phase,{timeout:16000});
    out.push(await hashes(q,'.atlas-map'));
  }return out;};
  const newHash=await collect(p);
  await p.locator('#tab-south').click();A.equal(await p.locator('.atlas-pair').count(),7);
  await p.locator('#tab-all').click();A(await p.locator('#grille-passer').isDisabled());await p.locator('#grille-lever').click();A(await p.locator('#grille-passer').isEnabled());
  await p.locator('#visite-nuit').click();await scene(p,carrefour,3);await p.locator('#accesses [data-passage="SortieNord"]').click();await scene(p,cuisine,3);
  await p.locator('#tab-halcyon').click();A.equal(await p.locator('.hal-card').count(),3);await p.close();
  const r=reg(await browser.newPage({reducedMotion:'reduce',viewport:{width:1380,height:995}}));await r.goto('file://'+path.join(G,'Guilde-Destiny-Mobilier-Halcyon-IA.html'));await r.locator('#tab-all').click();
  A.deepEqual(newHash,await collect(r));await r.close();
  // The sandbox preview has no network or same-origin storage; all artwork is embedded.
  const m=reg(await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1,offline:true,reducedMotion:'reduce',isMobile:true,hasTouch:true}));m.setDefaultTimeout(9000);
  await m.setContent('<meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}</style><iframe sandbox="allow-scripts" style="width:100%;height:840px;border:0"></iframe>');
  await m.locator('iframe').evaluate((f,s)=>f.srcdoc=s,text);const f=m.frameLocator('iframe');await demo(f,hall,0);
  A(await f.locator('html').evaluate(e=>e.scrollWidth<=innerWidth+1));
  await f.locator('#cf-go-night').tap();await outside(f,3);A(await f.locator('html').evaluate(e=>e.scrollWidth<=innerWidth+1));
  await f.locator('#cliff-return').tap();await scene(f,hall,3);await f.locator('#tab-cf').tap();await f.locator('[data-dir="UpLeft"]').tap();await demo(f,hall,3);
  await f.locator('#cf-try').tap();await scene(f,hall,3);await button(f,'Poser comme dans l’exemple').tap();await scene(f,hall,3,1);
  A.deepEqual(errors,[]);
  fs.writeFileSync(path.join(O,'Verification-atelier.json'),JSON.stringify({statut:'PASS',orientations:8,plans_identiques:60,cadres_sud:7,accessibilite_cliff_et_retour:true,quatre_ambiances:true,phases_originales_animees:anim[0],mer_animee:true,gel_animation:true,respect_perimetre_lueur:true,garde_seuil_et_allee:true,rotation_ancree:true,png_identique:true,import_export_et_reprise_locaux:true,grille_et_balade_nuit:true,halcyon_preserve:true,sandbox_mobile_hors_ligne:true,longueur_px_cliff:520,sha256_atelier:sha(text),sha256_base:sha(base)},null,2)+'\n');
  console.log('PASS · 8 vues, pose/ancrage et sauvegarde, 60 plans identiques, falaise 4 ambiances/4 images, accès aller-retour, grille et mobile hors ligne.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
