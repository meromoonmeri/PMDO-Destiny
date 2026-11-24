'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{homedir}=require('node:os');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(homedir(),'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const exe=process.env.CHROMIUM||path.join(homedir(),'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const folder=path.resolve(__dirname,'..'),root=path.dirname(folder),cache=path.join(homedir(),'.cache/grille-grodoudou-destiny');
const url=process.env.PREVIEW_URL||'http://127.0.0.1:4179/',html=fs.readFileSync(path.join(root,'Guilde-Destiny-Bourgeons-PMD.html'),'utf8');
const {data,horsRaccords}=require('../../Bourgeons-PMD/Sources/Verifier-donnees.cjs');
const d=data(html),g=d.grille_accueil,{id,dest,vues:v}=g,last=g.positions.length-1;
assert(!d.chaines_accueil);assert.equal(g.calques.length,4);assert.equal(g.positions.length,16);assert.equal(g.positions[last],66);
assert.equal(d.rooms.length,15);assert.equal(d.rooms.reduce((n,r)=>n+r.gates.length,0),29);assert.equal(d.rooms.filter(r=>r.south?.band).length,7);
assert.deepEqual(g.liens,[[id,'EscalierNord'],[dest,'EscalierSud']]);
assert.deepEqual(Buffer.from(g.calques[0].split(',')[1],'base64'),fs.readFileSync(path.join(folder,'Tilesheet-Grille-Escalier.png')));
const prev=path.join(cache,'Avant-grille.html');
if(fs.existsSync(prev)){
 const b=data(fs.readFileSync(prev,'utf8')),a={...horsRaccords(d,b)};
 delete a.grille_accueil;delete b.chaines_accueil;assert.deepEqual(a,b);
}
const snap=(p,sel)=>p.locator(sel).evaluate(c=>c.toDataURL());
const lever='#grille-lever',passer='#grille-passer',cv='#grille-plan',south='#seuil-detail';
const ready=(p,n=0)=>p.locator(`${cv}[data-scene="${id}:0:${v.y}:0"][data-grille-image="${n}"]`).waitFor({state:'visible'});
const room=(p,x)=>p.locator(`#map[data-scene="${x}:0:0:0"]`).waitFor({state:'visible'});
const portal=(p,x)=>p.locator(`#accesses button[title="${x}"]`);
const crop=(p,selector)=>p.locator(selector).evaluate((c,{x,y,w,h})=>{
 const q=document.createElement('canvas');q.width=w;q.height=h;q.getContext('2d').drawImage(c,x,y,w,h,0,0,w,h);return q.toDataURL();
},v);
(async()=>{
 const b=await chromium.launch({executablePath:exe,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  fs.mkdirSync(cache,{recursive:true});
  const p=await b.newPage({viewport:{width:1365,height:985},reducedMotion:'no-preference'}),errors=[];
  p.on('pageerror',e=>errors.push(e.message));await p.goto(url);await ready(p);
  assert(await p.locator(passer).isDisabled());assert.match(await p.locator('#grille-etat').textContent(),/Fermée/);
  const closed=await snap(p,cv), s0=await snap(p,south);
  await p.locator('#grille-demo').screenshot({path:path.join(cache,'Panneau-fermee.png')});
  await p.locator('#grille-voir-plan').click();await room(p,id);
  assert(await portal(p,'EscalierNord').isDisabled());assert.equal(await crop(p,'#map'),closed);
  await portal(p,'EscalierNord').dispatchEvent('click');assert.equal(await p.locator('#room-select').inputValue(),id);
  await p.locator('#tab-all').click();await ready(p);
  await p.locator(cv).evaluate(c=>{
   const motion=new Set([Number(c.dataset.grilleImage)]);window.vuesGrille=motion;
   new MutationObserver(()=>motion.add(Number(c.dataset.grilleImage))).observe(c,{attributeFilter:['data-grille-image']});
  });
  await p.locator(lever).click();
  await p.waitForFunction(()=>{
   const k=Number(document.querySelector('#grille-plan').dataset.grilleImage);return k>=3&&k<14;
  });
  const mid=await snap(p,cv);assert.notEqual(mid,closed);assert(await p.locator(passer).isDisabled());
  await ready(p,last);await p.waitForFunction(()=>!document.querySelector('#grille-passer').disabled);
  const opened=await snap(p,cv);assert.notEqual(opened,closed);assert.notEqual(opened,mid);
  const seen=await p.evaluate(()=>[...window.vuesGrille]);assert(seen.length>=12&&seen.includes(last),String(seen));
  assert.equal(await snap(p,south),s0);assert.match(await p.locator('#grille-etat').textContent(),/passage libre/);
  await p.locator('#grille-demo').screenshot({path:path.join(cache,'Panneau-ouverte.png')});
  await p.locator(passer).click();await room(p,dest);
  assert(await portal(p,'EscalierSud').isEnabled());await portal(p,'EscalierSud').click();await room(p,id);
  assert.equal(await crop(p,'#map'),opened);
  await p.locator('#grille-editor-lever').click();assert(await portal(p,'EscalierNord').isDisabled());
  await p.waitForFunction(()=>document.querySelector('#grille-editor-status').textContent.startsWith('Fermée'));
  assert.equal(await crop(p,'#map'),closed);
  await p.locator(`#rooms button[data-room="${dest}"]`).click({timeout:6000});await room(p,dest);
  assert(await portal(p,'EscalierSud').isDisabled());
  assert.deepEqual(errors,[]);await p.close();
  const m=await b.newPage({viewport:{width:390,height:826},offline:true,reducedMotion:'reduce'});
  await m.setContent('<iframe sandbox="allow-scripts" style="display:block;width:100%;height:807px;border:0"></iframe>');
  const set=async h=>m.locator('iframe').evaluate((e,h)=>{e.srcdoc=h;},h);
  await set(html);const frame=m.frameLocator('iframe');await ready(frame);
  assert.equal(await snap(frame,cv),closed);assert(await frame.locator('html').evaluate(e=>e.scrollWidth<=innerWidth+1));
  await frame.locator(lever).click();await ready(frame,last);assert(await frame.locator(passer).isEnabled());
  assert.equal(await snap(frame,cv),opened);
  const baseline=path.join(homedir(),'.cache/chaines-entree-destiny/Avant-chaines.html');
  let checked=null;
  if(fs.existsSync(baseline)){
   await set(fs.readFileSync(baseline,'utf8'));
   const under=frame.locator(`#seuil-salle[data-scene="${id}:0:0:0"]`);await under.waitFor({state:'visible'});
   if(!d.raccords_bois){assert.equal(await crop(frame,'#seuil-salle'),opened);checked=0;}
   else{
    const file=fs.readFileSync(path.join(folder,'Calques','Ombre-Interieure.png'));
    const [dx,dy]=g.rect;
    const result=await under.evaluate(async(c,{v,opened,patch,dx,dy})=>{
     const get=async url=>{const a=new Image();a.src=url;await a.decode();return a;};
     const after=await get(opened),mask=await get(patch),cv=document.createElement('canvas');
     cv.width=v.w;cv.height=v.h;const a=cv.getContext('2d',{willReadFrequently:true});
     a.drawImage(mask,dx-v.x,dy-v.y);const m=a.getImageData(0,0,v.w,v.h).data;
     a.clearRect(0,0,v.w,v.h);a.drawImage(after,0,0);
     const n=a.getImageData(0,0,v.w,v.h).data,b=c.getContext('2d').getImageData(v.x,v.y,v.w,v.h).data;
     let diff=0,err=0;for(let i=0;i<m.length;i+=4){if(n[i]===b[i]&&n[i+1]===b[i+1]&&n[i+2]===b[i+2]&&n[i+3]===b[i+3])continue;diff++;if(!m[i+3])err++;}
     return {diff,err};
    },{v,opened,patch:'data:image/png;base64,'+file.toString('base64'),dx,dy});
    assert(result.diff>1300);assert.equal(result.err,0);checked=result.diff;
   }
  }
  fs.writeFileSync(path.join(folder,'Verification.json'),JSON.stringify({statut:'PASS',images:16,images_observees_en_montee:seen.length,course_px:66,desactivation_pendant_le_mouvement:true,bloque_dans_les_deux_sens:true,passage_autorise_en_haut:true,ouverture_pixels_retouche_interieure:checked,seuil_sud_identique:true,apercu_mobile_hors_ligne:true,modifie_le_jeu:false},null,2)+'\n');
  console.log('PASS · grille mobile, passage fermé pendant le déplacement, franchissement autorisé en haut, retour et seuil sud intacts.');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
