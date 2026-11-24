'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{homedir}=require('node:os');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(homedir(),'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const exe=process.env.CHROMIUM||path.join(homedir(),'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const out=path.resolve(__dirname,'..'),project=path.dirname(out),cache=path.join(homedir(),'.cache/accueil-grodoudou-destiny');
const html=fs.readFileSync(path.join(project,'Guilde-Destiny-Bourgeons-PMD.html'),'utf8'), url=process.env.PREVIEW_URL||'http://127.0.0.1:4179/';
const {data,horsRaccords}=require('../../Bourgeons-PMD/Sources/Verifier-donnees.cjs');
const d=data(html),a=d.seuil_accueil,id=a.id;
const oldPath=path.join(cache,'Bourgeons-avant-seuil.html');
if(fs.existsSync(oldPath)){
  const old=data(fs.readFileSync(oldPath,'utf8')),current={...horsRaccords(d,old)};
  delete current.seuil_accueil;delete current.chaines_accueil;delete current.grille_accueil;
  assert.deepEqual(current,old);
}
assert.equal(d.rooms.length,15);assert.equal(d.rooms.reduce((n,r)=>n+r.gates.length,0),29);assert.equal(d.rooms.filter(r=>r.south?.band).length,7);
assert.equal(d.catalog.length,157);assert.equal(a.phases.length,4);assert(a.phases.every(p=>p.length===2));
const bb=a.detail;assert.deepEqual(bb,{x:212,y:304,w:88,h:56});
const proof=JSON.parse(fs.readFileSync(path.join(out,'Index-seuil.json'),'utf8'));
const area=proof.seuil_visible.zone;assert.deepEqual(area,{x:224,y:313,w:64,h:39});
assert.equal(proof.halo.ancrage_bord_clair_y,349);assert.equal(proof.tapis.lisiere_bas_y,348);
const full='#seuil-salle', detail='#seuil-detail';
const snapshot=(p,selector)=>p.locator(selector).evaluate(c=>c.toDataURL());
const crop=(p,selector,x,y,w,h)=>p.locator(selector).evaluate((c,[x,y,w,h])=>{
  const o=document.createElement('canvas');o.width=w;o.height=h;o.getContext('2d').drawImage(c,x,y,w,h,0,0,w,h);return o.toDataURL();
},[x,y,w,h]);
function wait(p,sel,scene){return p.locator(`${sel}[data-scene="${scene}"]`).waitFor({state:'visible'});}
async function verifyDelta(p,old){
  return p.locator(full).evaluate(async(c,{src,area})=>{
    const im=new Image();im.src=src;await im.decode();
    const o=document.createElement('canvas');o.width=c.width;o.height=c.height;o.getContext('2d').drawImage(im,0,0);
    const before=o.getContext('2d').getImageData(0,0,c.width,c.height).data;
    const after=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
    let n=0,bad=0,l=c.width,r=0,t=c.height,b=0;for(let i=0;i<before.length;i+=4){
      if(before[i]===after[i]&&before[i+1]===after[i+1]&&before[i+2]===after[i+2])continue;
      n++;const pixel=i/4,x=pixel%c.width,y=Math.floor(pixel/c.width);
      if(x<area.x||x>=area.x+area.w||y<area.y||y>=area.y+area.h)bad++;
      l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);b=Math.max(b,y);
    }
    return [n,bad,[l,t,r,b]];
  },{src:old,area});
}
(async()=>{
  const b=await chromium.launch({executablePath:exe,args:['--no-sandbox','--disable-dev-shm-usage']});
  try{
    const p=await b.newPage({viewport:{width:1365,height:980},reducedMotion:'reduce',acceptDownloads:true}), errors=[];
    p.on('pageerror',e=>errors.push(e.message));await p.goto(url);await wait(p,full,id+':0:0:0');
    assert(await p.locator('#seuil-source').evaluate(im=>im.complete&&im.naturalWidth===88));
    assert.equal(await p.locator('.atlas-map').count(),15);
    const others=()=>p.locator(`.atlas-card:not([data-plan="${id}"]) .atlas-map`).evaluateAll(rows=>rows.map(c=>{
      const bytes=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
      let h=2166136261;
      for(let i=0;i<bytes.length;i++)h=Math.imul(h^bytes[i],16777619);
      return h;
    }));
    const pixels=[];
    for(let i=0;i<4;i++){
      await p.locator(`[data-seuil-phase="${i}"]`).click();await wait(p,full,`${id}:${i}:0:0`);
      await p.waitForFunction(phase=>[...document.querySelectorAll('.atlas-map')].every(c=>c.dataset.scene?.endsWith(`:${phase}:0:0`)),i);
      const baseline=await others(), lit=await snapshot(p,full);
      assert.equal(await snapshot(p,detail),await crop(p,full,bb.x,bb.y,bb.w,bb.h));
      await p.locator('#seuil-toggle').click();await p.waitForFunction(lit=>document.querySelector('#seuil-salle').toDataURL()!==lit,lit);
      const [count,bad,bbox]=await verifyDelta(p,lit);assert(count>2350);assert.equal(bad,0);
      assert.deepEqual(bbox,[224,313,287,351]);pixels.push(count);
      assert.deepEqual(await others(),baseline);
      await p.locator('#seuil-toggle').click();await p.waitForFunction(lit=>document.querySelector('#seuil-salle').toDataURL()===lit,lit);
    }
    await p.locator('[data-seuil-phase="0"]').click();await wait(p,full,id+':0:0:0');
    await p.locator('#seuil-demo').screenshot({path:path.join(cache,'Panneau-final.png')});
    const show=await snapshot(p,full);
    await p.locator('#ouvrir-accueil').click();await wait(p,'#map',id+':0:0:0');
    assert(await p.locator('#seuil-demo').isHidden());assert.equal(await snapshot(p,'#map'),show);
    await p.locator('#export').click();
    const [file]=await Promise.all([p.waitForEvent('download'),p.locator('#download-png').click()]);
    const actual=fs.readFileSync(await file.path());
    assert.deepEqual(actual,Buffer.from(show.split(',')[1],'base64'));
    await p.locator('#export-box .close-dialog').click();
    await p.locator('#camera').click();await wait(p,'#map',id+':0:112:0');
    assert.equal(await snapshot(p,'#map'),await crop(p,full,96,112,320,240));
    await p.locator('#tab-south').click();assert.equal(await p.locator('.atlas-pair').count(),7);
    assert.deepEqual(errors,[]);
    const m=await b.newPage({viewport:{width:390,height:835},offline:true,reducedMotion:'reduce'});
    await m.setContent('<iframe sandbox="allow-scripts" style="display:block;width:100%;height:810px;border:0"></iframe>');
    await m.locator('iframe').evaluate((el,s)=>el.srcdoc=s,html);
    const frame=m.frameLocator('iframe');await wait(frame,full,id+':0:0:0');
    assert.equal(await snapshot(frame,full),show);assert(await frame.locator('html').evaluate(el=>el.scrollWidth<=innerWidth+1));
    await frame.locator('#seuil-detail').screenshot({path:path.join(cache,'Seuil-mobile.png')});
    fs.writeFileSync(path.join(out,'Verification.json'),JSON.stringify({statut:'PASS',ambiance_jour_par_defaut:true,pixels_changes_par_ambiance:pixels,changements_hors_seuil:0,seuil_px:64,liseret_clair_y:349,autres_salles_stables_pendant_bascule:14,plans:15,passages:29,cadres_sud:7,export_png_identique:true,apercu_mobile_hors_ligne:true},null,2)+'\n');
    console.log('PASS · halo et tapis en quatre ambiances, 14 autres salles stables pendant la bascule du halo, plan/cadre et export PNG, aperçu mobile hors ligne.');
  } finally {await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
