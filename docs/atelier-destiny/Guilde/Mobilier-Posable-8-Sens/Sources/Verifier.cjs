'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url'),{createHash}=require('node:crypto');
const h=os.homedir(),W=path.join(h,'.cache','atelier-destiny-8-sens'),K=path.join(W,'Kit'),R=path.resolve(__dirname,'..'),V=path.join(W,'Film');fs.mkdirSync(V,{recursive:true});
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(h,'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const executablePath=process.env.CHROMIUM||path.join(h,'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const file=pathToFileURL(path.join(K,'Atelier.html')).href;const C='guilde_destiny_',init=C+'cuisine',U='halcyon-bureau-rouleau-lierre';
const two=pg=>pg.evaluate(()=>new Promise(ok=>requestAnimationFrame(()=>requestAnimationFrame(ok))));
async function where(pg,target){const c=pg.locator('#map'),q=await c.boundingBox(),r=await pg.evaluate(()=>poseTest.room());return {x:q.x+target.x*q.width/r.w,y:q.y+target.y*q.height/r.h};}
async function art(pg,fn,which='#map'){await pg.waitForFunction(()=>poseTest.ready());await two(pg);const s=await pg.locator(which).evaluate(c=>c.toDataURL('image/png').split(',').at(-1));const b=Buffer.from(s,'base64');fs.writeFileSync(path.join(V,fn+'.png'),b);return createHash('sha256').update(b).digest('hex');}
async function find(pg,center,d=0,mir=true){return pg.evaluate(({cx,cy,d,mir})=>{
 const {w,h}=poseTest.room(),id=document.getElementById('map').dataset.asset;let ans=null;let v=Infinity;
 for(let y=28;y<h-10;y+=8)for(let x=4;x<w-10;x+=8){const ds=(x-cx)**2+(y-cy)**2;if(ds>=v)continue;let good=true;for(let k=0;k<8;k++)if(poseTest.error({id,x,y,d:k,m:false})||mir&&poseTest.error({id,x,y,d:k,m:true})){good=false;break;}if(good){v=ds;ans={x,y};}}
 return ans;
 },{cx:center[0],cy:center[1],d,mir});}
async function clickObj(p,id){await p.locator('#query').fill(id);const b=p.locator(`#catalog button[data-id="${id}"]`);await b.first().click();await p.waitForFunction(i=>document.getElementById('map').dataset.asset===i,id);}
async function place(p,point){assert(point,'aucun pivot commun aux huit poses');const target=await where(p,point);await p.locator('#place').click();await p.mouse.click(target.x,target.y);const out=await p.evaluate(()=>poseTest.pose());assert(out,'objet non posé');assert.equal(out.x,point.x);assert.equal(out.y,point.y);return out;}
async function download(p,b){await p.waitForFunction(()=>poseTest.ready());await two(p);const q=p.waitForEvent('download');await p.locator(b).click();const d=await q;return {name:d.suggestedFilename(),bytes:fs.readFileSync(await d.path())};}
(async()=>{
 const errors=[];const run=await chromium.launch({executablePath,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  const p=await run.newPage({viewport:{width:1440,height:990},offline:true,reducedMotion:'reduce',acceptDownloads:true});p.on('pageerror',e=>errors.push(e.stack));p.setDefaultTimeout(9000);await p.goto(file);await p.waitForFunction(()=>window.poseTest&&poseTest.ready());
  const proof=await p.evaluate(()=>{
    const bank=window.DESTINY_POSE,pts=poseTest.assets();if(pts.length!==1108||pts.some(p=>p[1]!==8))throw Error('Couverture');
    document.getElementById('salle').value='table-vide';document.getElementById('salle').dispatchEvent(new Event('change'));
    let c=0;for(const a of bank.ob)for(let d=0;d<8;d++)for(const m of [true,false]){const v=a.v[d],x=324,y=300;const err=poseTest.error({id:a.id,x,y,d,m});if(err)throw Error(a.id+' '+d+' '+err);if(v.some(q=>!Number.isInteger(q))||!bank.pages[v[0]])throw Error('Atlas '+a.id);c++;}return c;
  });assert.equal(proof,17728);
  await p.locator('#salle').selectOption(init);
  // Same visual objects across all eight samples. None of the previous ateliers are altered.
  const aux=await p.evaluate(()=>window.DESTINY_POSE.ob.filter(a=>a.famille==='PMU de Destiny'&&a.gabarit==='plante').map(a=>a.id).slice(0,4));
  const placeAux=async(id,x)=>{await clickObj(p,id);return place(p,await find(p,x));};
  await placeAux('coffre_bois_bleu',[360,243]);await placeAux(aux[0],[118,194]);
  await clickObj(p,U);await p.locator('[data-dir="DownRight"]').click();const o=await place(p,await find(p,[215,220]));assert.equal(o.d,1);
  const records=[];
  for(let i=0;i<8;i++){
    await p.locator(`[data-dir="${['Down','DownRight','Right','UpRight','Up','UpLeft','Left','DownLeft'][i]}"]`).click();
    const q=await p.evaluate(()=>poseTest.pose());assert.deepEqual([q.x,q.y,q.d],[o.x,o.y,i]);const hash=await art(p,'Bibliotheque-'+i);await art(p,'Sprite-'+i,'#sprite');records.push({i,x:q.x,y:q.y,hash});
  }
  assert(new Set(records.map(t=>t.hash)).size>=6);
  await p.locator('[data-dir="DownRight"]').click();const a=await download(p,'#png');assert(a.name.endsWith('-DownRight.png'));
  await p.keyboard.press('m');assert.equal((await p.evaluate(()=>poseTest.pose())).m,true);assert.equal(await p.locator('#map').getAttribute('data-pivot'),`${o.x},${o.y}`);const b=await download(p,'#png');assert(b.name.endsWith('-miroir.png'));fs.writeFileSync(path.join(V,'Miroir-avant.png'),a.bytes);fs.writeFileSync(path.join(V,'Miroir-apres.png'),b.bytes);
  await art(p,'Bibliotheque-Miroir');await p.screenshot({path:path.join(V,'Atelier-bureau.png'),fullPage:false});
  await p.keyboard.press('m');assert.equal((await p.evaluate(()=>poseTest.pose())).m,false);
  const center0=await p.evaluate(()=>poseTest.pose());const xy=await where(p,center0);await p.mouse.move(xy.x-2,xy.y-8);await p.mouse.down();await p.mouse.move(xy.x+10,xy.y+3,{steps:3});await p.mouse.up();const center1=await p.evaluate(()=>poseTest.pose());assert(center1&&((center1.x!==center0.x)||(center1.y!==center0.y)),'déplacement par glisser');
  const d=await download(p,'#save');assert(d.name.endsWith('.json'));const saved=JSON.parse(d.bytes);assert.equal(saved.items[init].length,3);await p.locator('#load').setInputFiles({name:d.name,mimeType:'application/json',buffer:d.bytes});await p.waitForFunction(()=>document.getElementById('status').textContent.includes('restauré'));
  const z=await download(p,'#planpng');assert(z.name.endsWith('.png')&&z.bytes.readUInt32BE(16)===480);
  await p.reload();await p.waitForFunction(()=>poseTest.scene().items['guilde_destiny_cuisine']?.length===3);assert.equal(await p.locator('#map').getAttribute('data-items'),'3');
  await p.locator('#salle').selectOption(C+'refectoire');await clickObj(p,'Guilde_Imm_halcyon_comptoir_cloche');await place(p,await find(p,[334,263]));await p.locator('[data-dir="DownLeft"]').click();await p.locator('#night').click();await art(p,'Refectoire-Nuit');
  await p.locator('#salle').selectOption(C+'accueil');await clickObj(p,'etendard');await place(p,await find(p,[149,214]));await p.locator('[data-dir="UpRight"]').click();await p.locator('#night').click();await art(p,'Etendard-Accueil');
  const mt=await run.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true,offline:true,reducedMotion:'reduce'});mt.on('pageerror',e=>errors.push(e.stack));await mt.goto(file);assert(await mt.locator('html').evaluate(e=>e.scrollWidth<=innerWidth+1));await mt.locator('[data-dir="DownRight"]').tap();assert.equal(await mt.locator('#map').getAttribute('data-direction'),'DownRight');await mt.close();
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(R,'Verification-poses.json'),JSON.stringify({statut:'PASS',banque:1108,vues:8864,tests_pose_avec_ou_sans_miroir:proof,plan_ok:true,pivots_verifies:records,glisser:true,import_export:true,export_png_et_plan:true,hors_ligne:true,mobile:true},null,2)+'\n');console.log('PASS · 17 728 poses et miroirs admissibles, rotations sur plan et exports, mobile hors ligne.');
 }finally{await run.close();}
})().catch(e=>{console.error(e);process.exit(1)});
