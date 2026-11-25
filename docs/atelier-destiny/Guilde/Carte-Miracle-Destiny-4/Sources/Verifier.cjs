'use strict';
const {chromium}=require(process.env.PLAYWRIGHT||'playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..'),atlas=JSON.parse(fs.readFileSync(path.join(root,'Atlas.json'))),url=pathToFileURL(path.join(root,'Carte-Miracle-Destiny-4.html')).href;
const faults=[],external=[],checks=[];const ok=(condition,message)=>{assert.ok(condition,message);checks.push(message);};
const snap=p=>p.evaluate(()=>window.carteMiracle.snapshot());const step=(p,t)=>p.evaluate(t=>window.carteMiracle.advance(t),t);
const ready=p=>p.waitForFunction(()=>window.carteMiracle?.snapshot().ready);
function watch(p){p.on('pageerror',x=>faults.push(x.message));p.on('request',x=>{if(/^https?:/.test(x.url()))external.push(x.url());});}
const swatch=p=>p.locator('#chart').evaluate(c=>c.toDataURL());
async function fogPixel(p,site){return p.evaluate(async id=>{
 const d=JSON.parse(document.getElementById('atlas-data').textContent),c=document.getElementById('chart'),f=window.carteMiracle.snapshot();
 const [x,y]=d.sites.find(s=>s.id===id).loc,k=Math.min(c.width/d.width,c.height/d.height)*f.camera.z,a=c.width/2-f.camera.x*k,b=c.height/2-f.camera.y*k;
 const qx=Math.round(x*k+a)-3,qy=Math.round(y*k+b)-3; if(qx<0||qy<0||qx+7>=c.width||qy+7>=c.height)return {onscreen:false,equal:false};
 const expected=document.createElement('canvas');expected.width=c.width;expected.height=c.height;const ctx=expected.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.setTransform(k,0,0,k,a,b);
 const fog=new Image();await new Promise((res,rej)=>{fog.onload=res;fog.onerror=rej;fog.src=d.images.voile;});ctx.drawImage(fog,0,0);
 const pix=z=>Array.from(z.getImageData(qx,qy,7,7).data).join(',');return {onscreen:true,equal:pix(ctx)===pix(c.getContext('2d'))};
 },site);}
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--no-sandbox']});
 try{
  const context=await b.newContext({viewport:{width:1280,height:868},deviceScaleFactor:1,offline:true});const p=await context.newPage();watch(p);
  await p.goto(url+'?capture=1');await ready(p);let s=await snap(p);
  ok(s.current==='reverie'&&s.openedZones.join(',')==='reve'&&s.totalZones===24&&s.total===45&&s.visibles===6,'Start in Réverie with exactly one of 24 areas unveiled');
  ok(s.found.join(',')==='reverie','Found pins are separate from opened regions');
  ok(atlas.placements.heritage.silhouettes===101&&atlas.placements.alizes.silhouettes>=10&&atlas.placements.emeraude.silhouettes>=10,'Full geography inventory includes both original additional archipelagos');
  ok(await p.locator('#world').isDisabled()&&!s.worldUnlocked,'Whole-world control is locked');
  ok(await p.locator('#clouds').count()===0,'No visibility bypass button');
  ok(!(await p.locator('#repere-grotte-ocre').isVisible())&&!(await p.locator('#repere-bassin-anciens').isVisible()),'Unknown markers are not visible in the reader');
  let f=await fogPixel(p,'grotte-ocre');ok(f.onscreen&&f.equal,'Desert pixels are opaque original cloud pixels before discovery');
  const still=await swatch(p);await step(p,680);ok(still===await swatch(p),'Cloud and terrain are both static at rest');
  await p.locator('#world').evaluate(el=>el.dispatchEvent(new MouseEvent('click',{bubbles:true})));s=await step(p,920);
  ok(s.camera.z>=s.minZoom&&!s.worldUnlocked,'Even a synthetic click cannot switch into the whole atlas');
  await p.locator('#stage').focus();await p.keyboard.press('0');await step(p,990);
  ok((await snap(p)).camera.z>=2.65,'Keyboard zero only recentres when locked');
  const r=await p.locator('#stage').boundingBox();await p.mouse.move(r.x+r.width*.55,r.y+r.height*.63);
  for(let i=0;i<11;i++)await p.mouse.wheel(0,220);s=await step(p,800);
  ok(s.camera.z>=2.65&&await p.locator('#minus').isDisabled(),'Wheel-out respects the locked zoom floor');
  for(let i=0;i<35;i++)await p.keyboard.press('ArrowRight');s=await step(p,1020);
  f=await fogPixel(p,'port-austral');ok(f.onscreen&&f.equal&&s.openedZones.length===1,'Panning east does not expose the historical continent');
  await p.locator('#reset').click();await p.locator('#depart').click();s=await step(p,420);
  ok(s.phase==='travel'&&s.transport==='terre'&&s.current==='reverie','Walk within the starter region still plays');
  await p.locator('#pause').click();let t=await step(p,420);ok(t.paused&&t.elapsed===s.elapsed,'Pause holds the team');
  await p.locator('#pause').click();s=await step(p,(s.totalTime-s.elapsed)*1000+110);
  ok(s.current==='fosse'&&s.found.includes('fosse')&&s.openedZones.length===1&&!s.opening,'First local marker unlocks without reopening Réverie');
  await step(p,1700);await p.locator('#reset').click();
  await p.locator('#destination').selectOption('grotte-ocre');await p.locator('#follow').click();await p.locator('#speed').selectOption('4');
  await p.locator('#depart').click();let depart=await snap(p);s=await step(p,Math.max(0,depart.totalTime*250-160));
  ok(s.events.some(e=>e.type==='transport'&&e.mode==='mer')&&s.phase==='travel'&&!s.opening,'Boat travels to the desert before opening the cloud layer');
  f=await fogPixel(p,'vrille');ok(f.onscreen&&f.equal,'A different marker on the target territory remains covered until arrival');
  s=await step(p,290);ok(s.opening?.zone==='torselune'&&s.found.includes('grotte-ocre'),'Only the targeted region opens upon arrival');
  ok(await p.locator('#arrival-kind').textContent()==='REPÈRE DÉBLOQUÉ !','Immediate unlocked status');
  const mid=await swatch(p);await p.locator('#pause').click();t=await step(p,520);ok(t.opening.progress===s.opening.progress&&mid===await swatch(p),'Paused clouds and terrain remain pixel-identical');await p.locator('#pause').click();
  s=await step(p,1540);ok(s.phase==='idle'&&!s.opening&&!s.worldUnlocked,'The reveal ends, but the whole atlas is still locked');
  f=await fogPixel(p,'grotte-ocre');ok(f.onscreen&&!f.equal,'The new desert is visible after the bank has cleared');
  await p.reload();await ready(p);s=await snap(p);
  ok(s.current==='grotte-ocre'&&s.openedZones.join(',')==='reve,torselune'&&!s.opening,'Save restores exactly the discovered territories without reanimation');
  await p.locator('#reset').click();await p.locator('#speed').selectOption('4');await p.locator('#circuitNuages').click();
  let lateSeen=false;
  for(let i=0;i<630;i++){
   s=await step(p,150);
   if(s.openedZones.length===23&&!lateSeen){ok(!s.worldUnlocked&&await p.locator('#world').isDisabled(),'One missing zone keeps the overview locked');lateSeen=true;}
   if(s.openedZones.length===24&&s.opening){ok(!s.worldUnlocked&&await p.locator('#world').isDisabled(),'Last cloud transition must finish before whole-map access');break;}
  }
  ok(lateSeen&&s.opening?.zone==='austral','The actual route has reached the last historical region');
  s=await step(p,1700);
  ok(s.worldUnlocked&&s.openedZones.length===24&&s.phase==='idle','All 24 areas have been unveiled');
  const ordered=atlas.circuits.nuages.map(id=>atlas.sites.find(a=>a.id===id).area);
  ok(s.events.filter(e=>e.type==='ouverture-zone').map(e=>e.id).join(',')===ordered.join(','),'Every regional reveal happened exactly once, in route order');
  ok(s.found.length===24&&s.total===45,'All areas are open without forcing discovery of every repère');
  await p.locator('#world').click();s=await step(p,1280);ok(s.camera.z<1.005&&!s.follow&&s.visibles===45,'Unlocked view shows the entire accessible atlas');
  ok(await p.locator('#veilCount').textContent()==='Carte entière déverrouillée','Unlock status is visible');
  await p.locator('#reset').click();s=await snap(p);ok(s.openedZones.length===1&&await p.locator('#world').isDisabled(),'Reset restores the veil and lock');
  await context.close();
  for(const width of [320,390]){
   const cx=await b.newContext({viewport:{width,height:850},isMobile:true,deviceScaleFactor:1,hasTouch:true,offline:true});const m=await cx.newPage();watch(m);await m.goto(url+'?capture=1');await ready(m);
   ok(await m.evaluate(()=>document.documentElement.scrollWidth===innerWidth),`No mobile overflow at ${width}px`);
   ok(await m.locator('#world').isDisabled()&&await m.locator('#stage').isVisible(),`Locked cloud view fits ${width}px`);
   await m.locator('#depart').tap();s=await step(m,4000);ok(s.found.includes('fosse'),`Playable regional discovery on mobile ${width}px`);await cx.close();
  }
  const box=await b.newContext({viewport:{width:980,height:850},offline:true});const page=await box.newPage();watch(page);
  const source=fs.readFileSync(path.join(root,'Carte-Miracle-Destiny-4.html'),'utf8').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
  await page.setContent('<iframe sandbox="allow-scripts" title="Destiny 4" style="width:100%;height:823px;border:0" srcdoc="'+source+'"></iframe>');const frame=page.frames()[1];await ready(frame);
  ok((await snap(frame)).openedZones.join(',')==='reve'&&await frame.locator('#world').isDisabled(),'File preview works offline and keeps the atlas locked');
  await frame.locator('#speed').selectOption('4');await frame.locator('#depart').click();await frame.waitForFunction(()=>window.carteMiracle.snapshot().found.includes('fosse'));
  ok((await snap(frame)).found.length===2,'Offline iframe reaches a genuine discovery');await box.close();
  ok(faults.length===0,'No JS errors: '+faults.join(', '));ok(external.length===0,'No external requests');
  fs.writeFileSync(path.join(root,'Verification-lecteur.json'),JSON.stringify({statut:'PASS',tests:checks.length,détails:checks,zones:24,repères:45,carte_entière_uniquement_après_dernier_voile:true,calques_géographiques_immobiles:true,hors_ligne:true,mobiles:[320,390]},null,2)+'\n');console.log(checks.length+' contrôles réussis');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
