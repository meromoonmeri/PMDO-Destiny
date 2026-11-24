'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{homedir}=require('node:os');
const {createHash}=require('node:crypto');
const {data,horsRaccords}=require('./Verifier-donnees.cjs');
const chromium=require(process.env.PLAYWRIGHT_MODULE||path.join(homedir(),'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright')).chromium;
const exe=process.env.CHROMIUM||path.join(homedir(),'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const dir=path.resolve(__dirname,'../Verdure'),root=path.resolve(dir,'../..'),work=path.join(homedir(),'.cache/retouches-rives-destiny');
const current=fs.readFileSync(path.join(root,'Guilde-Destiny-Bourgeons-PMD.html'),'utf8');
const old=fs.readFileSync(process.argv[2]||path.join(work,'Avant-rives-et-ombre.html'),'utf8');
const masks=JSON.parse(fs.readFileSync(path.join(work,'Masques-controle.json'),'utf8'));
const report=JSON.parse(fs.readFileSync(path.join(dir,'Index-raccords.json'),'utf8'));
const sha=s=>createHash('sha256').update(s).digest('hex');
const live=sha(current)===report.html_sha256;
// When a later revision is active, audit this stage against its archived build.
const html=live?current:fs.readFileSync(process.argv[3]||path.join(homedir(),'.cache/fonds-ronces-nuit/Avant-fonds-ronces-nuit.html'),'utf8');
const d=data(html),b=data(old),fix=d.raccords_bois,id=fix.escalier;
assert.equal(sha(html),report.html_sha256);assert.equal(sha(old),report.source_sha256);
assert.deepEqual(horsRaccords(d,b),b);
assert.equal(report.rives_recalees,27);assert.equal(report.salles_verifiees,15);
assert.equal(Object.keys(fix.rives).length,14);assert.equal(d.rooms.length,15);
assert.equal(d.rooms.reduce((n,r)=>n+r.gates.length,0),29);assert.equal(d.rooms.filter(r=>r.south?.band).length,7);
assert.deepEqual(d.lianes[id],b.lianes[id]);assert.notEqual(d.rooms[0].base,b.rooms[0].base);
for(const [rid,n] of Object.entries(fix.rives)){
 assert(n>0);assert.notDeepEqual(d.lianes[rid],b.lianes[rid]);
}
for(const n of ['bureau_maitre','carrefour','dortoir_nord_1','dortoir_nord_2','dortoir_sud_1','dortoir_sud_2','chambre_heros'])assert.equal(fix.rives['guilde_destiny_'+n],2,n);
const url=process.env.PREVIEW_URL||'http://127.0.0.1:4179/';
const selectors={grid:'.atlas-card .atlas-map',shade:'#grille-plan',map:'#map',south:'#seuil-detail'};
const scene=(p,selector,rid,phase,y=0)=>p.locator(`${selector}[data-scene="${rid}:${phase}:${y}:0"]`).waitFor({state:'visible'});
const snap=(p,selector)=>p.locator(selector).evaluate(c=>c.toDataURL());
const shoot=(p,sel,file)=>p.locator(sel).screenshot({path:path.join(work,file)});
const ready=(p,phase)=>Promise.all(d.rooms.map(r=>scene(p,`${selectors.grid}`,r.id,phase)));
const phaseSel=(phase)=>`#atlas-phases [data-atlas-phase="${phase}"]`;

// Compare the composed RGBA outside strict artwork masks, not entire canvases via toDataURL.
async function checksums(p){
 return p.locator(selectors.grid).evaluateAll(async (rows,scopes)=>{
  return Object.fromEntries(await Promise.all(rows.map(async c=>{
   const key=c.closest('article').dataset.plan,w=c.width,h=c.height,[ax,ay,bit]=scopes[key];
   const im=new Image();im.src=bit;await im.decode();
   const k=document.createElement('canvas');k.width=im.naturalWidth;k.height=im.naturalHeight;
   const g=k.getContext('2d');g.drawImage(im,0,0);const alpha=g.getImageData(0,0,k.width,k.height).data;
   const rgb=c.getContext('2d').getImageData(0,0,w,h).data;
   let outside=2166136261,inBox=2166136261,n=0;
   for(let y=0,i=0;y<h;y++)for(let x=0;x<w;x++,i+=4){
    const xx=x-ax,yy=y-ay,marked=xx>=0&&yy>=0&&xx<k.width&&yy<k.height&&alpha[4*(yy*k.width+xx)+3]>0;
    const rgb32=rgb[i]|(rgb[i+1]<<8)|(rgb[i+2]<<16)|(rgb[i+3]<<24);
    if(marked){inBox=Math.imul(inBox^rgb32,16777619);n++;}
    else outside=Math.imul(outside^rgb32,16777619);
   }
   return [key,{outside,inBox,n}];
  })));
 },masks);
}

async function atlas(p){
 await p.locator('#grille-lever').click();
 await p.locator(`${selectors.shade}[data-grille-image="15"]`).waitFor({state:'visible'});
 const rows=[],south=[];
 for(let i=0;i<4;i++){
  if(i)await p.locator(phaseSel(i)).click();
  await ready(p,i);await scene(p,selectors.shade,id,i,d.grille_accueil.vues.y);
  await scene(p,selectors.south,id,i,d.seuil_accueil.detail.y);
  rows.push(await checksums(p));south.push(await snap(p,selectors.south));
 }
 return {rows,south};
}

async function download(p,selector){
 const exact=Buffer.from((await snap(p,selector)).split(',')[1],'base64');
 await p.locator('#export').click();
 const [file]=await Promise.all([p.waitForEvent('download'),p.locator('#download-png').click()]);
 assert.deepEqual(fs.readFileSync(await file.path()),exact);
 await p.locator('#export-box .close-dialog').click();
}

(async()=>{
 const br=await chromium.launch({executablePath:exe,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  const opts={viewport:{width:1320,height:950},reducedMotion:'reduce',acceptDownloads:true};
  let p=await br.newPage({...opts,offline:true});
  await p.setContent(old,{waitUntil:'domcontentloaded'});
  const prev=await atlas(p);await p.close();
  p=await br.newPage(opts);const errors=[];p.on('pageerror',e=>errors.push(e.message));
  if(live)await p.goto(url);else await p.setContent(html,{waitUntil:'domcontentloaded'});
  const now=await atlas(p);
  for(let ph=0;ph<4;ph++)for(const room of d.rooms){
   const {id,label}=room,a=now.rows[ph][id],b=prev.rows[ph][id];
   assert.equal(a.outside,b.outside,`${label} · hors retouche · ${ph}`);
   assert.notEqual(a.inBox,b.inBox,`${label} · retouche visible · ${ph}`);
   assert.equal(a.n,report.salles[room.n-1].pixels_modifies||report.escalier.pixels_modifies);
  }
  assert.deepEqual(now.south,prev.south);
  await p.locator(phaseSel(0)).click();await ready(p,0);await shoot(p,'#grille-demo','Accueil-ombre-ouverte.png');
  await p.locator('#grille-voir-plan').click();await scene(p,selectors.map,id,0);
  assert(await p.locator('#accesses button[title="EscalierNord"]').isEnabled());
  await download(p,selectors.map);
  const master='guilde_destiny_bureau_maitre';
  await p.locator(`#rooms button[data-room="${master}"]`).click();await scene(p,selectors.map,master,0);
  await shoot(p,selectors.map,'Bureau-rives-jour.png');
  const x=await snap(p,selectors.map);await p.locator('#toggle-lianes').click();
  await p.waitForFunction(x=>document.querySelector('#map').toDataURL()!==x,x);
  await p.locator('#toggle-lianes').click();
  await p.waitForFunction(x=>document.querySelector('#map').toDataURL()===x,x);
  await p.locator('#phases [data-phase="3"]').click();await scene(p,selectors.map,master,3);
  const night=await snap(p,selectors.map);assert.notEqual(night,x);
  await shoot(p,selectors.map,'Bureau-rives-nuit.png');await download(p,selectors.map);
  await p.locator('#tab-south').click();assert.equal(await p.locator('.atlas-pair').count(),7);
  assert.deepEqual(errors,[]);await p.close();
  const mobile=await br.newPage({viewport:{width:390,height:820},offline:true,reducedMotion:'reduce'});
  await mobile.setContent('<iframe sandbox="allow-scripts" style="width:100%;height:805px;border:0;display:block"></iframe>');
  await mobile.locator('iframe').evaluate((e,doc)=>{e.srcdoc=doc;},html);
  const m=mobile.frameLocator('iframe');await ready(m,0);
  await m.locator('#grille-lever').click();await m.locator(`${selectors.shade}[data-grille-image="15"]`).waitFor();
  assert(await m.locator('#grille-passer').isEnabled());
  const vis=await checksums(m);assert.deepEqual(vis,now.rows[0]);
  assert(await m.locator('html').evaluate(e=>e.scrollWidth<=innerWidth+1));
  await shoot(m,selectors.shade,'Accueil-ombre-mobile.png');
  const tested={statut:'PASS',salles:15,ambiances:4,plans_ambiances_composes:60,pixels_changes_hors_masques:0,
   seuil_sud_identique_en_quatre_ambiances:true,export_png_identique:['Accueil · Jour','Bureau du maître · Nuit'],
   controle_lianes_reversible:true,grille_nord_franchissable_levee:true,apercu_mobile_sandbox_hors_ligne:true,sha256:sha(html)};
  fs.writeFileSync(path.join(dir,'Verification-raccords.json'),JSON.stringify(tested,null,2)+'\n');
  console.log('PASS · 60 rendus avant/après · aucun changement hors masque · deux exports exacts · version mobile hors ligne.');
 }finally{await br.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
