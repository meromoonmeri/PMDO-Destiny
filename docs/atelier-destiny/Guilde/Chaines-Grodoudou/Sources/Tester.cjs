'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{homedir}=require('node:os');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(homedir(),'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const exe=process.env.CHROMIUM||path.join(homedir(),'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const folder=path.resolve(__dirname,'..'),root=path.dirname(folder),cache=path.join(homedir(),'.cache/chaines-entree-destiny');
const url=process.env.PREVIEW_URL||'http://127.0.0.1:4179/',html=fs.readFileSync(path.join(root,'Guilde-Destiny-Bourgeons-PMD.html'),'utf8');
const data=s=>JSON.parse(s.split('<script id="donnees" type="application/json">')[1].split('</script>')[0]);
const d=data(html), ca=d.chaines_accueil,{id,vue}=ca, index=JSON.parse(fs.readFileSync(path.join(folder,'Index-tilesheet.json'),'utf8'));
const before=path.join(cache,'Avant-chaines.html');
if(fs.existsSync(before)){const a={...d};delete a.chaines_accueil;assert.deepEqual(a,data(fs.readFileSync(before,'utf8')));}
assert.equal(d.rooms.length,15);assert.equal(d.rooms.reduce((n,r)=>n+r.gates.length,0),29);assert.equal(d.rooms.filter(r=>r.south?.band).length,7);
assert.deepEqual(Buffer.from(ca.planche.split(',')[1],'base64'),fs.readFileSync(path.join(folder,index.planche)));
assert.equal(index.sprites.length,8);assert.deepEqual(index.taille,[192,112]);
assert.deepEqual(index.escalier.rectangle,[232,104,48,16]);
assert.equal(ca.phases.length,4);assert(ca.phases.every(p=>p.length===2));assert.equal(new Set(ca.phases.map(q=>q[0][2])).size,4);
const snap=(p,q)=>p.locator(q).evaluate(c=>c.toDataURL());
const ready=(p,q,phase)=>p.locator(`${q}[data-scene="${id}:${phase}:${q==='#chaines-plan'?vue.y:0}:0"]`).waitFor({state:'visible'});
const cut=(p,selector)=>p.locator(selector).evaluate((c,{x,y,w,h})=>{
 const o=document.createElement('canvas');o.width=w;o.height=h;o.getContext('2d').drawImage(c,x,y,w,h,0,0,w,h);return o.toDataURL();
},vue);
function delta(p,src){return p.locator('#seuil-salle').evaluate(async(c,src)=>{
 const p=new Image();p.src=src;await p.decode();const o=document.createElement('canvas');o.width=c.width;o.height=c.height;
 o.getContext('2d').drawImage(p,0,0);const a=o.getContext('2d').getImageData(0,0,c.width,c.height).data, b=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
 let left=0,right=0,bad=0;for(let i=0;i<a.length;i+=4){
  if(a[i]===b[i]&&a[i+1]===b[i+1]&&a[i+2]===b[i+2])continue;
  const x=i/4%c.width,y=Math.floor(i/4/c.width);
  if(y<98||y>=147||x<210||x>=302||(x>=232&&x<280))bad++;
  else if(x<256)left++;else right++;
 }
 return {left,right,bad};
},src);}
(async()=>{
 const b=await chromium.launch({executablePath:exe,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  fs.mkdirSync(cache,{recursive:true});
  const p=await b.newPage({viewport:{width:1365,height:990},reducedMotion:'reduce'}),err=[];
  p.on('pageerror',e=>err.push(e.message));await p.goto(url);await ready(p,'#chaines-plan',0);
  assert(await p.locator('#chaines-tilesheet').evaluate(im=>im.complete&&im.naturalWidth===192));
  await p.locator('.chaines-source summary').click();
  assert(await p.locator('#chaines-source').evaluate(im=>im.complete&&im.naturalHeight===194));
  await p.locator('.chaines-source summary').click();
  const stats=[];
  for(let i=0;i<4;i++){
   await p.locator(`[data-seuil-phase="${i}"]`).click();await ready(p,'#chaines-plan',i);await ready(p,'#seuil-salle',i);
   const full=await snap(p,'#seuil-salle'),north=await snap(p,'#chaines-plan'),south=await snap(p,'#seuil-detail');
   assert.equal(north,await cut(p,'#seuil-salle'));
   await p.locator('#toggle-chaines').click();
   await p.waitForFunction(s=>document.querySelector('#chaines-plan').toDataURL()!==s,north);
   const q=await delta(p,full);assert(q.left>175&&q.right>175);assert.equal(q.bad,0);stats.push(q);
   assert.equal(await snap(p,'#seuil-detail'),south);
   await p.locator('#toggle-chaines').click();
   await p.waitForFunction(s=>document.querySelector('#chaines-plan').toDataURL()===s,north);
  }
  await p.locator('[data-seuil-phase="0"]').click();await ready(p,'#chaines-plan',0);
  const north=await snap(p,'#chaines-plan');await p.locator('#chaines-demo').screenshot({path:path.join(cache,'Panneau-final.png')});
  await p.locator('#ouvrir-chaines').click();await ready(p,'#map',0);assert.equal(await cut(p,'#map'),north);
  assert.equal(await p.locator('#accesses button[title="EscalierNord"]').count(),1);
  assert.deepEqual(err,[]);await p.close();
  const m=await b.newPage({viewport:{width:390,height:820},offline:true,reducedMotion:'reduce'});
  await m.setContent('<iframe sandbox="allow-scripts" style="display:block;width:100%;height:796px;border:0"></iframe>');
  await m.locator('iframe').evaluate((e,s)=>e.srcdoc=s,html);
  const f=m.frameLocator('iframe');await ready(f,'#chaines-plan',0);
  assert.equal(await snap(f,'#chaines-plan'),north);assert(await f.locator('html').evaluate(el=>el.scrollWidth<=innerWidth+1));
  assert(await f.locator('#chaines-tilesheet').evaluate(im=>im.complete&&im.naturalHeight===112));
  fs.writeFileSync(path.join(folder,'Verification.json'),JSON.stringify({statut:'PASS',sprites:8,ambiance:4,pixels_par_phase:stats,passage_nord_libre_px:48,seuil_sud_identique:true,apercu_hors_ligne_mobile:true},null,2)+'\n');
  console.log('PASS · 8 sprites transparents, barrières réversibles dans les 4 ambiances, accès et seuil sud intacts, iframe mobile hors ligne.');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
