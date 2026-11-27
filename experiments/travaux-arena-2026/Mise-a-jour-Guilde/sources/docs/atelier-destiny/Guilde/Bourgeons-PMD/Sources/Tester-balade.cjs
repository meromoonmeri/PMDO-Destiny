'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{homedir}=require('node:os');
const {createHash}=require('node:crypto');
const {data,horsBalade}=require('./Verifier-donnees.cjs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(homedir(),'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const exe=process.env.CHROMIUM||path.join(homedir(),'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const pkg=path.resolve(__dirname,'..'),root=path.dirname(pkg),work=path.join(homedir(),'.cache/fonds-ronces-nuit');
const html=fs.readFileSync(path.join(root,'Guilde-Destiny-Bourgeons-PMD.html'),'utf8');
const before=fs.readFileSync(process.argv[2]||path.join(work,'Avant-fonds-ronces-nuit.html'),'utf8');
const report=JSON.parse(fs.readFileSync(path.join(pkg,'Verdure/Index-balade-nuit.json'),'utf8'));
const scopes=JSON.parse(fs.readFileSync(path.join(work,'Masques-balade-test.json'),'utf8'));
const sha=x=>createHash('sha256').update(x).digest('hex');
const d=data(html),b=data(before),meta=d.balade_nuit;const cross=meta.depart,hall=d.rooms[0].id;
assert.equal(sha(html),report.html_sha256);assert.equal(sha(before),report.source_sha256);
assert.deepEqual(horsBalade(d,b),b);assert.equal(d.rooms.length,15);
assert.deepEqual(meta.fonds[hall].rgb[0],[31,31,63]);assert.deepEqual(meta.fonds[cross].rgb[0],[23,23,63]);
assert.deepEqual(meta.fonds[cross].rgb[3],[15,15,47]);assert.equal(meta.lumieres[cross].length,4);
assert.deepEqual(d.seuil_accueil,b.seuil_accueil);assert.deepEqual(d.grille_accueil,b.grille_accueil);
for(const r of d.rooms){
 const id=r.id,points=meta.lumieres[id];
 assert.equal(points.length,id===cross?4:2);
 assert.deepEqual(points.slice(0,2).map(q=>[q.x,q.y]),b.lianes[id].points.map(q=>[q.x,q.y]));
 assert(points.every(v=>v.images.length===4));
 assert(report.salles[id].images.every(v=>v.reflet_alpha_max<=53&&v.plancher_delta_luma_6>2.2*v.ancienne_version));
}
const pics='.atlas-map',main='#map',url=process.env.PREVIEW_URL||'http://127.0.0.1:4179/';
const roomIds=new Set(d.rooms.map(r=>r.id)),rooms=new Map(d.rooms.map(r=>[r.id,r]));
const phase=(px)=>`#atlas-phases [data-atlas-phase="${px}"]`;
const readyAtlas=(scope,p)=>Promise.all(d.rooms.map(r=>scope.locator(`${pics}[data-scene="${r.id}:${p}:0:0"]`).waitFor({state:'visible'})));
const readyRoom=(p,id,x=3)=>p.locator(`${main}[data-scene="${id}:${x}:0:0"]${x===3?'[data-lueur]':':not([data-lueur])'}`).waitFor({state:'visible'});
const att=(p,s)=>p.locator(main).getAttribute(s);
const take=(p,file)=>p.locator(main).screenshot({path:path.join(work,file)});
const snap=(p,sel)=>p.locator(sel).evaluate(c=>c.toDataURL());

async function audit(p,g,active){
 const settings=Object.fromEntries(Object.entries(scopes).map(([k,v])=>[k,{zone:v[g===3?'nuit':'jour'],matte:active?meta.fonds[k].matte:null,rgb:meta.fonds[k].rgb[g]}]));
 return p.locator(pics).evaluateAll(async(cvs,settings)=>{
  async function image(bit){const i=new Image();i.src=bit;await i.decode();return i;}
  function stencil(img,w,h,x=0,y=0){
   const m=document.createElement('canvas');m.width=w;m.height=h;const c=m.getContext('2d');c.drawImage(img,x,y);return c.getImageData(0,0,w,h).data;
  }
  return Object.fromEntries(await Promise.all(cvs.map(async cv=>{
   const id=cv.closest('[data-plan]').dataset.plan,{zone:[x,y,src],matte,rgb}=settings[id],w=cv.width,h=cv.height;
   const pixels=cv.getContext('2d').getImageData(0,0,w,h).data;
   const allowed=stencil(await image(src),w,h,x,y),bg=matte?stencil(await image(matte),w,h):null;
   let outside=2166136261,paint=2166136261,bad=0,count=0;
   for(let i=0;i<pixels.length;i+=4){
    const a=pixels[i],b=pixels[i+1],c=pixels[i+2],v=(a<<16)|(b<<8)|c;
    if(!allowed[i+3])outside=Math.imul(outside^v,16777619);else paint=Math.imul(paint^v,16777619);
    if(bg?.[i+3]){count++;if(a!==rgb[0]||b!==rgb[1]||c!==rgb[2])bad++;}
   }
   return [id,{outside,paint,bad,count}];
  })));
 },settings);
}

async function tourAtlas(p,live){
 const out=[];
 for(let i=0;i<4;i++){
  if(i)await p.locator(phase(i)).click();await readyAtlas(p,i);out.push(await audit(p,i,live));
 }
 return out;
}

function pathTo(start,dest){
 const agenda=[[start,[]]],seen=new Set([start]);
 while(agenda.length){
  const [id,path]=agenda.shift();if(id===dest)return path;
  for(const e of rooms.get(id).gates){if(!roomIds.has(e.dest)||seen.has(e.dest))continue;seen.add(e.dest);agenda.push([e.dest,[...path,[id,e]]]);}
 }
 throw Error(`Pas de chemin vers ${dest}`);
}

async function floorSample(p,id){
 const [x,y]=report.salles[id].sonde_plancher;
 return p.locator(main).evaluate((c,[x,y])=>{const [,g]=c.getContext('2d').getImageData(x,y,1,1).data;return g;},[x,y]);
}

async function comparePng(p){
 const known=Buffer.from((await snap(p,main)).split(',')[1],'base64');
 await p.locator('#export').click();const [f]=await Promise.all([p.waitForEvent('download'),p.locator('#download-png').click()]);
 assert.deepEqual(known,fs.readFileSync(await f.path()));await p.locator('#export-box .close-dialog').click();
}

(async()=>{
 const br=await chromium.launch({executablePath:exe,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  const common={viewport:{width:1340,height:965},reducedMotion:'reduce',acceptDownloads:true};
  let p=await br.newPage({...common,offline:true});await p.setContent(before,{waitUntil:'domcontentloaded'});
  const old=await tourAtlas(p,false);await p.close();
  p=await br.newPage(common);const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(url);const now=await tourAtlas(p,true);
  for(let i=0;i<4;i++)for(const r of d.rooms){
   const a=now[i][r.id],b=old[i][r.id];assert.equal(a.bad,0,`${r.label}: fond · phase ${i}`);
   assert.equal(a.count,report.salles[r.id].pixels);assert.equal(a.outside,b.outside,`${r.label}: hors retouche · phase ${i}`);
   assert.notEqual(a.paint,b.paint);
  }
  await p.locator('#visite-nuit').click();await readyRoom(p,cross);
  assert.equal(await p.locator('#phases [data-phase="3"]').getAttribute('aria-pressed'),'true');
  assert.match(await p.locator('#foliage-status').textContent(),/4 bourgeons/);
  await take(p,'Carrefour-nuit.png');
  const full=await snap(p,main),lit=await floorSample(p,cross);
  await p.locator('#toggle-lianes').click();await p.locator(`${main}:not([data-lueur])`).waitFor({state:'visible'});
  const unlit=await floorSample(p,cross);assert(lit-unlit>=7,JSON.stringify({lit,unlit}));
  await p.locator('#toggle-lianes').click();await readyRoom(p,cross);
  assert.equal(await snap(p,main),full);
  await comparePng(p);
  const direct=[];let here=cross;const seen=new Set([here]);
  for(const target of d.rooms.map(r=>r.id)){
   if(seen.has(target))continue;
   for(const [from,g] of pathTo(here,target)){
    assert.equal(from,here);const control=p.locator(`#accesses button[title="${g.id}"]`);
    if(await control.isDisabled())await p.locator('#grille-editor-lever').click();
    await control.click();here=g.dest;await readyRoom(p,here);seen.add(here);
    assert.equal(await p.locator('#phases [data-phase="3"]').getAttribute('aria-pressed'),'true');
    direct.push(g.id);
   }
  }
  assert.equal(seen.size,15);
  await p.locator(main).scrollIntoViewIfNeeded();
  await p.locator(main).evaluate(cv=>{window.boucle=new Set([cv.dataset.lueur]);new MutationObserver(()=>window.boucle.add(cv.dataset.lueur)).observe(cv,{attributeFilter:['data-lueur']});});
  await p.locator('#motion-toggle').click();await p.waitForFunction(()=>window.boucle.size===4);
  const frames=await p.evaluate(()=>Array.from(window.boucle).sort());assert.deepEqual(frames,['0','1','2','3']);
  await p.locator('#motion-toggle').click();await p.locator('#phases [data-phase="0"]').click();await readyRoom(p,here,0);
  assert.equal(await att(p,'data-lueur'),null);assert.deepEqual(errors,[]);await p.close();
  const mobile=await br.newPage({viewport:{width:390,height:835},offline:true,reducedMotion:'reduce'});
  await mobile.setContent('<iframe sandbox="allow-scripts" style="display:block;width:100%;height:810px;border:0"></iframe>');
  await mobile.locator('iframe').evaluate((el,html)=>el.srcdoc=html,html);
  const m=mobile.frameLocator('iframe');await m.locator('#visite-nuit').click();await readyRoom(m,cross);
  assert.equal(await snap(m,main),full);assert(await m.locator('html').evaluate(el=>el.scrollWidth<=innerWidth+1));
  await take(m,'Carrefour-nuit-mobile.png');
  await m.locator('#accesses button[title="SortieNord"]').click();await readyRoom(m,'guilde_destiny_cuisine');
  const proof={statut:'PASS',salles:seen.size,check_fonds_ambiances:60,hors_masques:0,passages_suivis:direct.length,ambiance_nuit_conservee:true,
   eclairage_plancher_carrefour_delta_vert:lit-unlit,images_du_cycle_observees:frames.length,lumiere_eteinte_de_jour:true,
   export_png_identique:true,iframe_mobile_hors_ligne:true,jeu_modifie:false,sha256:sha(html)};
  fs.writeFileSync(path.join(pkg,'Verdure/Verification-balade-nuit.json'),JSON.stringify(proof,null,2)+'\n');
  console.log(`PASS · 60 fonds exacts, 15 salles reliées, ${direct.length} franchissements en Nuit, 4 images de lumière, PNG et mobile hors ligne.`);
 }finally{await br.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
