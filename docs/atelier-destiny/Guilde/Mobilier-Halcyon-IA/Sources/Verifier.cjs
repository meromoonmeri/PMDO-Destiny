'use strict';
const A=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{homedir}=require('node:os'),{createHash}=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(homedir(),'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const exe=process.env.CHROMIUM||path.join(homedir(),'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const O=path.resolve(__dirname,'..'),G=path.dirname(O),W=path.join(homedir(),'.cache/halcyon-ia');
const file=f=>fs.readFileSync(f,'utf8'),parse=h=>JSON.parse(h.split('<script id="donnees" type="application/json">')[1].split('</script>')[0]);
const text=file(path.join(G,'Guilde-Destiny-Mobilier-Halcyon-IA.html')),base=file(path.join(G,'Guilde-Destiny-Mobilier-Halcyon.html'));
const d=parse(text),b=parse(base),k=JSON.parse(file(path.join(O,'Index.json'))),sha=x=>createHash('sha256').update(x).digest('hex');
const {catalog,halcyon,...rest}=d;A.deepEqual({...rest,catalog:catalog.slice(0,647),halcyon:{...halcyon,modele:halcyon.modele.slice(0,49),demo:b.halcyon.demo}},b);
const ids=new Map(catalog.slice(647).map(a=>[a.id,a]));A.equal(ids.size,30);A.equal(sha(base),'a45b4f07580fe23648bc2f0e5a3f77b6a2f552e62c2c9415cfb677db9c871e5a');
for(const v of k.variantes){const a=ids.get(v.id);A(a.previewOnly);A.equal(a.collection,'halcyon-ia');A.equal(a.generation,v.traitement);
 const p=Buffer.from(a.m[0],'base64');A.deepEqual(p,fs.readFileSync(path.join(O,v.png)));A.equal(sha(p),v.sha256);}
const m=k.modeles,room=d.halcyon.demo.salle,cross=d.balade_nuit.depart,store='pmd-destiny:guilde:mobilier-halcyon-ia:077:v1';
const demo=(p,n)=>p.locator(`#hal-scene[data-scene="${room}:${n}:48:7"]`).waitFor({state:'visible'});
const scene=(p,r,n,num)=>p.locator(`#map[data-scene="${r}:${n}:0:${num}"]`).waitFor({state:'visible'});
const png=(p,q)=>p.locator(q).getAttribute('src');
const readLayout=p=>p.evaluate(key=>JSON.parse(localStorage.getItem(key)||'{"salles":{}}').salles,store);
const ref=p=>p.locator('#hal-detail-image');

(async()=>{
 const browser=await chromium.launch({executablePath:exe,args:['--no-sandbox','--disable-dev-shm-usage']});
 const errors=[];const reg=p=>{p.on('pageerror',e=>errors.push(e.message));return p;};
 try{
  fs.mkdirSync(W,{recursive:true});const p=reg(await browser.newPage({viewport:{width:1380,height:970},reducedMotion:'reduce',acceptDownloads:true}));await p.goto(process.env.PREVIEW_URL||'http://127.0.0.1:4185/');await demo(p,0);
  A.equal(await p.locator('[data-origin="ia"]').getAttribute('aria-pressed'),'true');A.equal(await p.locator('.hal-card').count(),3);
  A.equal(await p.getByText('Génération retenue',{exact:false}).count(),4);A.deepEqual(await readLayout(p),{});
  await p.screenshot({path:path.join(W,'Galerie-IA.png')});
  await p.locator('[data-model="ia-coffre"]').click();const selected=await png(p,'#hal-detail-image');
  A.equal(selected,'data:image/png;base64,'+ids.get('halcyon-ia-coffre-minuit').m[0]);
  A.equal(await p.locator('#hal-size').textContent(),'36 × 31 px');
  await p.locator('#hal-original').click();A.equal(await p.locator('#hal-size').textContent(),'32 × 31 px');A.notEqual(await png(p,'#hal-detail-image'),selected);
  await p.locator('#hal-original').click();const [f]=await Promise.all([p.waitForEvent('download'),p.locator('#hal-png').click()]);
  A.equal(f.suggestedFilename(),'halcyon-ia-coffre-minuit.png');A.deepEqual(fs.readFileSync(await f.path()),Buffer.from(ids.get('halcyon-ia-coffre-minuit').m[0],'base64'));
  await p.locator('[data-tone="miel"]').click();A.match(await p.locator('#hal-ia-note').textContent(),/dérivée/);A.notEqual(await png(p,'#hal-detail-image'),selected);
  await p.locator('#hal-chosen').click();A.equal(await png(p,'#hal-detail-image'),selected);
  await p.locator('#hal-night').click();await demo(p,3);A.equal(await p.locator('#hal-scene').getAttribute('data-lueur'),'0');
  await p.locator('#hal-day').click();await demo(p,0);
  await p.locator('#hal-place').click();await scene(p,room,0,0);A.deepEqual(await readLayout(p),{});
  A.equal(await p.locator('#collection').inputValue(),'halcyon-ia');A.equal(await p.locator('#palette-pmu').inputValue(),'minuit');
  await p.getByRole('button',{name:'Poser au centre',exact:true}).click();await scene(p,room,0,1);
  const a=(await readLayout(p))[room][0];A.equal(a.meuble,'halcyon-ia-coffre-minuit');A(await p.locator('#download-ground').isDisabled());
  await p.locator('#hal-recolor').selectOption('ronce');A.deepEqual((await readLayout(p))[room][0],{...a,meuble:'halcyon-ia-coffre-ronce'});
  await p.locator('#tab-halcyon').click();await p.locator('[data-origin="guilde"]').click();A.match(await p.locator('#hal-count').textContent(),/^42 modèles/);
  await p.locator('[data-origin="metano"]').click();A.equal(await p.locator('.hal-card').count(),7);
  await p.locator('#hal-visit').click();await scene(p,cross,3,0);await p.locator('#accesses [title="SortieNord"]').click();await scene(p,'guilde_destiny_cuisine',3,0);
  await p.locator('#tab-all').click();A.equal(await p.locator('.atlas-map').count(),15);A(await p.locator('#grille-passer').isDisabled());
  await p.locator('#grille-lever').click();A(await p.locator('#grille-passer').isEnabled());await p.close();
  const q=reg(await browser.newPage({offline:true,viewport:{width:390,height:844},reducedMotion:'reduce'}));await q.setContent('<iframe sandbox="allow-scripts" style="width:100%;height:818px;border:0"></iframe>');await q.locator('iframe').evaluate((f,s)=>f.srcdoc=s,text);
  const ff=q.frameLocator('iframe');await demo(ff,0);await ff.locator('[data-model="ia-bureau"]').click();A.match(await ff.locator('#hal-detail-palette').textContent(),/Ronce/);
  A(await ff.locator('html').evaluate(e=>e.scrollWidth<=innerWidth+1));await ff.locator('#hal-place').click();await scene(ff,room,0,0);await ff.getByRole('button',{name:'Poser au centre'}).click();await scene(ff,room,0,1);
  A.deepEqual(errors,[]);
  const report={statut:'PASS',images_selectionnees:m.length,variants:ids.size,donnees_precedentes_intactes:true,export_png_identique:true,rayon_ia_separe:true,pose:true,recoloration_sans_deplacement:true,balade_nuit:true,grille:true,iframe_hors_ligne:true,sha256_apercu:sha(text),sha256_atelier_precedent:sha(base)};
  fs.writeFileSync(path.join(O,'Verification-atelier.json'),JSON.stringify(report,null,2)+'\n');console.log('PASS · sélections IA, déclinaisons, PNG, pose, Nuit et mobile hors ligne ; ancien atelier conservé.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
