'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{homedir}=require('node:os'),{createHash}=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(homedir(),'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const executablePath=process.env.CHROMIUM||path.join(homedir(),'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const out=path.resolve(__dirname,'..'),root=path.dirname(out),url=process.env.PREVIEW_URL||'http://127.0.0.1:4184/';
const ref=fs.readFileSync(path.join(root,'Guilde-Destiny-Bourgeons-PMD.html'),'utf8'),text=fs.readFileSync(path.join(root,'Guilde-Destiny-Mobilier-Halcyon.html'),'utf8');
const sha=b=>createHash('sha256').update(b).digest('hex'),data=t=>JSON.parse(t.split('<script id="donnees" type="application/json">')[1].split('</script>')[0]);
const old=data(ref),d=data(text),{halcyon,catalog,...rest}=d,index=JSON.parse(fs.readFileSync(path.join(out,'Index.json'),'utf8'));
assert.deepEqual({...rest,catalog:catalog.slice(0,157)},old);
assert.equal(catalog.length,647);assert.equal(d.rooms.length,15);
assert.equal(d.rooms.reduce((n,r)=>n+r.gates.length,0),29);assert.equal(d.rooms.filter(r=>r.south?.band).length,7);
assert.equal(halcyon.modele.length,49);assert.equal(halcyon.palettes.length,10);assert.equal(index.variantes.length,490);
const db=new Map(catalog.map(a=>[a.id,a])),vs=new Map(index.variantes.map(v=>[v.id,v]));
for(const v of index.variantes){const a=db.get(v.id);assert.equal(a.previewOnly,true);assert.equal(a.halcyon,v.modele);
 const png=Buffer.from(a.m[0],'base64');assert.equal(sha(png),v.sha256);assert.deepEqual(png,fs.readFileSync(path.join(out,v.png)));
 assert.equal(v.origine==='guilde'?'halcyon':'metano',a.collection);
}
const room=halcyon.demo.salle, cross=d.balade_nuit.depart,hall=d.grille_accueil.id,next=d.grille_accueil.dest;
const rmap=new Map(d.rooms.map(r=>[r.id,r])),sel=(id)=>`#rooms [data-room="${id}"]`,phase=n=>`#atlas-phases [data-atlas-phase="${n}"]`;
const ready=(z,id,p=0,n=0)=>z.locator(`#map[data-scene="${id}:${p}:0:${n}"]`).waitFor({state:'visible'});
const stage=(z,p)=>z.locator(`#hal-scene[data-scene="${room}:${p}:48:7"]`).waitFor({state:'visible'});
const snap=(z,css='#map')=>z.locator(css).evaluate(c=>c.toDataURL());
const at=(z,css)=>z.locator(css).getAttribute('src');
const portal=(z,g)=>z.locator(`#accesses button[title="${g}"]`);
const snapAtlas=async(p,which)=>{
 if(which)await p.locator('#tab-all').click();const result=[];
 for(let i=0;i<4;i++){
  if(i)await p.locator(phase(i)).click();
  await p.waitForFunction(i=>[...document.querySelectorAll('.atlas-map')].every(c=>c.dataset.scene?.endsWith(`:${i}:0:0`)),i);
  result.push(await p.locator('.atlas-map').evaluateAll(list=>list.map(c=>{
   const a=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let hash=2166136261;
   for(let i=0;i<a.length;i+=4)hash=Math.imul(hash^((a[i]<<16)|(a[i+1]<<8)|a[i+2]),16777619);
   return hash;
  })));
 }
 return result;
};
function route(a,b){const queue=[[a,[]]],seen=new Set([a]);while(queue.length){const [n,p]=queue.shift();if(n===b)return p;
 for(const g of rmap.get(n).gates)if(rmap.has(g.dest)&&!seen.has(g.dest)){seen.add(g.dest);queue.push([g.dest,[...p,[n,g]]]);}}
 throw Error(`Chemin introuvable ${a} → ${b}`);}
async function df(p,btn){const [f]=await Promise.all([p.waitForEvent('download'),p.locator(btn).click()]);return [f.suggestedFilename(),fs.readFileSync(await f.path())];}
async function exportFile(p,btn){await p.locator('#export').click();const f=await df(p,btn);await p.locator('#export-box .close-dialog').click();return f;}
const storage='pmd-destiny:guilde:mobilier-halcyon:077:v1';
const saved=p=>p.evaluate(storage=>JSON.parse(localStorage.getItem(storage)||'{"salles":{}}'),storage);

(async()=>{
 const b=await chromium.launch({executablePath,args:['--no-sandbox','--disable-dev-shm-usage']});
 const errors=[],cfg={viewport:{width:1350,height:955},reducedMotion:'reduce',acceptDownloads:true};
 try{
  const reference=await b.newPage({...cfg,offline:true});await reference.setContent(ref,{waitUntil:'domcontentloaded'});
  const a0=await snapAtlas(reference,false);await reference.close();console.log('Référence : empreintes pixel des 60 rendus établies.');
  const p=await b.newPage(cfg);p.on('pageerror',e=>errors.push(e.message));await p.goto(url);await stage(p,0);
  assert.match(await p.title(),/Halcyon/);assert.equal(await p.locator('#tab-halcyon').getAttribute('aria-pressed'),'true');
  assert.equal(await p.locator('.hal-tone').count(),10);assert.equal(await p.locator('.hal-card').count(),12);
  assert.deepEqual((await saved(p)).salles,{});
  const im=await at(p,'#hal-detail-image');await p.locator('#hal-original').click();assert.notEqual(await at(p,'#hal-detail-image'),im);
  await p.locator('#hal-original').click();assert.equal(await at(p,'#hal-detail-image'),im);
  await p.locator('#hal-next').click();assert.match(await p.locator('#hal-paging-top').textContent(),/^13–24/);await p.locator('#hal-prev').click();
  await p.locator('[data-origin="metano"]').click();assert.equal(await p.locator('.hal-card').count(),7);
  await p.locator('#hal-family').selectOption('Meubles');assert.equal(await p.locator('.hal-card').count(),3);
  await p.locator('#hal-search').fill('écu');assert.equal(await p.locator('.hal-card').count(),0);assert(await p.locator('#hal-detail').isHidden());
  await p.locator('#hal-family').selectOption('');assert.equal(await p.locator('.hal-card').count(),1);assert.match(await p.locator('#hal-detail-provenance').textContent(),/Auberge/);
  await p.locator('[data-origin="guilde"]').click();await p.locator('#hal-search').fill('table banquet');
  assert.equal(await p.locator('.hal-card').count(),1);assert.equal(await p.locator('#hal-detail-name').textContent(),'Table de banquet');
  await p.locator('[data-mini="minuit"]').click();assert.equal(await p.locator('[data-tone="minuit"]').getAttribute('aria-pressed'),'true');
  assert.equal(await p.locator('.hal-mini').count(),10);assert.notEqual(await at(p,'#hal-detail-image'),im);
  const [nm,raw]=await df(p,'#hal-png');const id=nm.replace(/\.png$/,'');assert.equal(id,'halcyon-banquet-minuit');assert.equal(sha(raw),vs.get(id).sha256);
  await p.locator('#hal-night').click();await stage(p,3);assert.equal(await p.locator('#hal-scene').getAttribute('data-lueur'),'0');
  await p.locator('#hal-day').click();await stage(p,0);
  assert.deepEqual((await saved(p)).salles,{});console.log('Catalogue : rayons, teintes et export d’un vrai PNG transparent contrôlés.');
  await p.locator('#hal-room').selectOption(room);await p.locator('#hal-place').click();await ready(p,room);
  assert.deepEqual((await saved(p)).salles,{});assert.equal(await p.locator('#collection').inputValue(),'halcyon');assert.equal(await p.locator('#palette-pmu').inputValue(),'minuit');
  assert(await p.locator('#catalog [data-asset="halcyon-banquet-minuit"][aria-pressed=true]').isVisible());
  const native=p.locator('#download-ground');assert.equal(await native.isDisabled(),false);
  const beforeRoom=await snap(p);const rr=rmap.get(room), map=p.locator('#map');
  await map.scrollIntoViewIfNeeded();const dims=await map.boundingBox();await map.click({position:{x:1+(284/rr.w)*(dims.width-2),y:1+(222/rr.h)*(dims.height-2)}});await ready(p,room,0,1);
  assert(await native.isDisabled());const init=(await saved(p)).salles[room][0];assert.equal(init.meuble,id);
  await p.locator('#hal-recolor').selectOption('ronce');const alt=(await saved(p)).salles[room][0];assert.deepEqual(alt,{...init,meuble:'halcyon-banquet-ronce'});
  await p.locator('#undo').click();assert.deepEqual((await saved(p)).salles[room][0],init);
  await p.locator('#redo').click();assert.deepEqual((await saved(p)).salles[room][0],alt);
  await ready(p,room,0,1);const drawn=await snap(p);assert.notEqual(drawn,beforeRoom);
  const [nplan,plan]=await exportFile(p,'#download-plan');assert.equal(nplan,'Mon-plan-Destiny-077.json');
  assert.deepEqual(JSON.parse(plan).salles,{[room]:[alt]});
  const [,png]=await exportFile(p,'#download-png');assert.deepEqual(png,Buffer.from(drawn.split(',')[1],'base64'));
  await p.reload();await stage(p,0);await p.locator('#tab-work').click();await p.locator(sel(room)).click();await ready(p,room,0,1);
  assert.equal(await snap(p),drawn);assert.deepEqual((await saved(p)).salles,{[room]:[alt]});
  const imported=await b.newPage(cfg);imported.on('pageerror',e=>errors.push(e.message));await imported.goto(url);await stage(imported,0);
  await imported.locator('#layout-file').setInputFiles({name:nplan,mimeType:'application/json',buffer:plan});
  await imported.locator('#tab-work').click();await imported.locator(sel(room)).click();await ready(imported,room,0,1);
  assert.equal(await snap(imported),drawn);assert(await imported.locator('#download-ground').isDisabled());await imported.close();
  console.log('Atelier : pose, re-teinte sans déplacement, annuler/rétablir, import/export et copie locale contrôlés.');
  await p.locator('#layout-file').setInputFiles({name:nplan,mimeType:'application/json',buffer:Buffer.from(JSON.stringify({format:'destiny-guilde-mobilier-v1',jeu:d.game,salles:{}}))});
  await p.waitForFunction(key=>!Object.keys(JSON.parse(localStorage.getItem(key)).salles).length,storage);
  const a1=await snapAtlas(p,true);assert.deepEqual(a1,a0);
  await p.locator('#tab-south').click();assert.equal(await p.locator('.atlas-pair').count(),7);
  await p.locator('#tab-all').click();assert(await p.locator('#grille-passer').isDisabled());await p.locator('#visite-nuit').click();await ready(p,cross,3);
  assert.equal(await p.locator('#map').getAttribute('data-lueur'),'0');
  const seen=new Set([cross]);let here=cross,count=0,closedTest=false;
  for(const target of d.rooms.map(r=>r.id)){
   if(seen.has(target))continue;
   for(const [from,g] of route(here,target)){
    assert.equal(from,here);const link=portal(p,g.id);
    if(await link.isDisabled()){
     assert((from===hall&&g.dest===next)||(from===next&&g.dest===hall));closedTest=true;
     await p.locator('#grille-editor-lever').click();assert(await link.isEnabled());
    }
    await link.click();here=g.dest;await ready(p,here,3);assert.equal(await p.locator('#map').getAttribute('data-lueur'),'0');seen.add(here);count++;
   }
  }
  assert.equal(seen.size,15);assert(closedTest);assert.deepEqual(errors,[]);
  const m=await b.newPage({viewport:{width:390,height:844},offline:true,reducedMotion:'reduce',hasTouch:true});
  m.on('pageerror',e=>errors.push(e.message));await m.setContent('<iframe sandbox="allow-scripts" style="display:block;width:100%;height:826px;border:0"></iframe>');
  await m.locator('iframe').evaluate((el,t)=>el.srcdoc=t,text);const f=m.frameLocator('iframe');await stage(f,0);
  await f.locator('[data-origin="metano"]').click();await f.locator('[data-model="banc-metano"]').click();await f.locator('[data-mini="bruyere"]').click();
  assert.equal(await f.locator('#hal-detail-name').textContent(),'Banc et pots fleuris');
  assert(await f.locator('html').evaluate(e=>e.scrollWidth<=innerWidth+1));
  await f.locator('#hal-place').click();await ready(f,room);await f.getByRole('button',{name:'Poser au centre'}).click();await ready(f,room,0,1);
  await f.locator('#tab-halcyon').click();await f.locator('#hal-visit').click();await ready(f,cross,3);
  await portal(f,'SortieNord').click();await ready(f,'guilde_destiny_cuisine',3);assert.deepEqual(errors,[]);
  const proof={statut:'PASS',sha256_apercu:sha(text),sha256_reference:sha(ref),variantes_png_controlees:vs.size,
    salles_preservees:15,passages_preserves:29,cadres_sud_preserves:7,rendus_nus_pixel_identiques:60,grille_verrouillee_avant_levage:true,
    franchissements_de_nuit:count,filtres_et_palette:true,pose_ecran:true,retouche_palette_sans_deplacement:true,export_png_identique:true,
    export_png_sprite_identique:true,import_export_json:true,sauvegarde_locale:true,iframe_mobile_hors_ligne:true,installation_du_jeu_modifiee:false};
  fs.writeFileSync(path.join(out,'Verification-atelier.json'),JSON.stringify(proof,null,2)+'\n');
  console.log(`PASS · 490 PNG · 60 rendus identiques · ${count} passages en nuit · mobile hors ligne.`);
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
