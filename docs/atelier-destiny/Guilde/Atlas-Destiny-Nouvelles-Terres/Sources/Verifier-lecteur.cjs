'use strict';
// Run with Playwright installed, or PLAYWRIGHT and CHROME set to local paths.
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');const {pathToFileURL}=require('node:url');
const root=path.join(__dirname,'..');const target=path.join(root,'Explorer-Nouvelles-Terres.html');
const prep=process.argv[2];let pass=0;const ok=(v,l)=>{assert.ok(v,l);pass++};
const snap=p=>p.evaluate(()=>window.atlasDestiny.snapshot());
const ready=async p=>{await p.waitForFunction(()=>window.atlasDestiny?.snapshot().carteChargee);return snap(p)};
(async()=>{
  const browser=await chromium.launch({executablePath:process.env.CHROME||undefined,headless:true,args:['--no-sandbox']});
  const faults=[],externes=[];const watch=p=>{p.on('pageerror',e=>faults.push(e.message));p.on('request',e=>{if(/^https?:/.test(e.url()))externes.push(e.url())});};
  try{
    const a=await browser.newContext({viewport:{width:1440,height:970},offline:true});const page=await a.newPage();watch(page);
    await page.goto(pathToFileURL(target).href);let s=await ready(page);
    ok(s.z===1&&s.names&&!s.pins&&s.regions===6&&s.lieux===34,'Default world and data');
    ok(await page.locator('.region').count()===6,'All regions in index');
    ok(await page.locator('.label:not([hidden])').count()===6,'All names at world view');
    ok(!await page.locator('#less').isEnabled(),'Zoom out disabled at min');
    if(prep)await page.screenshot({path:path.join(prep,'Atlas-bureau.png'),fullPage:true});
    await page.locator('#showNames').click();ok(!await page.locator('#names').isVisible(),'Names off');
    await page.locator('#showNames').click();ok(await page.locator('#names').isVisible(),'Names on');
    await page.locator('#showPins').click();ok(await page.locator('.pin:not([hidden])').count()===34,'34 markers');
    await page.locator('#showPins').click();ok(!await page.locator('#pins').isVisible(),'Pins off');
    await page.locator('#showRoutes').click();ok((await snap(page)).routes&&await page.locator('#seaways').isVisible(),'Routes on');
    if(prep)await page.screenshot({path:path.join(prep,'Atlas-traversees.png'),fullPage:true});
    await page.locator('#guideRoutes').click();ok(!(await snap(page)).routes&&!await page.locator('#seaways').isVisible(),'Routes off via the index');
    await page.locator('#more').click();s=await snap(page);ok(s.z>1.2,'Zoom button');
    const b=await page.locator('#stage').boundingBox();await page.mouse.move(b.x+b.width*.5,b.y+b.height*.54);await page.mouse.wheel(0,-110);
    let w=await snap(page);ok(w.z>s.z,'Wheel zoom');
    await page.mouse.down();await page.mouse.move(b.x+b.width*.54,b.y+b.height*.59,{steps:4});await page.mouse.up();
    s=await snap(page);ok(Math.abs(s.x-w.x)>10&&Math.abs(s.y-w.y)>10,'Pointer drag');
    await page.locator('#stage').focus();await page.keyboard.press('ArrowRight');w=await snap(page);ok(w.x>s.x,'Keyboard pan');
    await page.keyboard.press('+');s=await snap(page);ok(s.z>w.z,'Keyboard zoom');await page.keyboard.press('0');
    s=await snap(page);ok(s.z===1&&s.x===556&&s.y===366&&!s.region,'Keyboard reset');
    await page.locator('button.label[data-id=seracine]').click();s=await snap(page);ok(s.region==='seracine'&&s.z>1.55,'Label focus');
    ok(await page.locator('.site-line').count()===6,'Useful regional fiche');
    await page.locator('#back').click();ok(await page.locator('.region').count()===6,'Index reset');
    await page.locator('#reverieBtn').click();s=await snap(page);ok(s.region==='reve'&&s.z>=2.5&&s.pins,'Réverie focus');
    ok(await page.locator('.site-line').count()===6,'Six places on Réverie');
    ok(await page.locator('.pin:not([hidden])').count()===6,'All 6 markers in map bounds and no distractors');
    if(prep)await page.screenshot({path:path.join(prep,'Atlas-reverie-bureau.png'),fullPage:true});
    await page.locator('.pin[data-id=fosse]').click();s=await snap(page);ok(s.site==='fosse'&&s.z>=4,'Click a location pin');
    ok(await page.locator('.site-line[data-site=fosse] .description').textContent().then(t=>t.includes('Lieu documenté')),'Lore notation');
    await page.locator('.site-line[data-site=passage]').click();ok((await snap(page)).site==='passage','Choose place from index');
    await page.locator('#worldBtn').click();await page.mouse.click(b.x+b.width*852/1112,b.y+b.height*469/732);
    ok((await snap(page)).region==='estrel','Click land to focus');
    ok(await page.locator('.site-line[data-site=ecluses]').isVisible(),'Écluses');
    await page.locator('.site-line[data-site=ecluses]').click();ok(await page.locator('.site-line[data-site=ecluses] .place-note').textContent()==='Lieu proposé pour Destiny','Original POI marked as such');
    await page.locator('#worldBtn').click();await page.mouse.click(b.x+b.width*521/1112,b.y+b.height*348/732);
    ok((await snap(page)).region==='haltes','Hit second island in the archipelago');
    ok(await page.locator('.site-line').count()===3,'Three original Haltes beacons');
    await a.close();
    for(const width of [320,390]){
      const mobile=await browser.newContext({viewport:{width,height:838},isMobile:true,hasTouch:true,deviceScaleFactor:1,offline:true});const mp=await mobile.newPage();watch(mp);
      await mp.goto(pathToFileURL(target).href);await ready(mp);
      ok(await mp.evaluate(()=>document.documentElement.scrollWidth===innerWidth),'Fits mobile '+width);
      ok(await mp.locator('#stage').isVisible(),'Map in mobile viewport '+width);
      if(width===390){
        if(prep)await mp.screenshot({path:path.join(prep,'Atlas-mobile.png'),fullPage:true});
        const cd=await mobile.newCDPSession(mp),m=await mp.locator('#stage').boundingBox();
        const p=(id,dx)=>({id,x:Math.round(m.x+m.width*.5+dx),y:Math.round(m.y+m.height*.49)});
        await cd.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[p(0,-24),p(1,24)]});
        await cd.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[p(0,-47),p(1,47)]});
        await cd.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
        ok((await snap(mp)).z>1.6,'Two-finger pinch zoom on mobile');
        await mp.locator('#worldBtn').tap();
      }
      await mp.locator('#reverieBtn').tap();ok((await snap(mp)).region==='reve','Réverie mobile '+width);
      await mp.locator('.site-line[data-site=bois]').tap();ok((await snap(mp)).site==='bois','Site mobile '+width);
      await mobile.close();
    }
    const c=await browser.newContext({viewport:{width:1160,height:870},offline:true}),p=await c.newPage();watch(p);
    const html=fs.readFileSync(target,'utf8');await p.setContent('<iframe sandbox="allow-scripts" style="width:100%;height:836px;border:0" title="Carte" srcdoc="'+html.replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;')+'"></iframe>');
    const frame=p.frames()[1];const z=await ready(frame);ok(z.carteChargee&&z.regions===6,'Viewer sandbox, no network');
    await frame.locator('#reverieBtn').click();ok((await snap(frame)).region==='reve','Viewer functions in sandbox');await c.close();
    ok(faults.length===0,'No page errors: '+faults.join(', '));ok(externes.length===0,'No network dependency');
    fs.writeFileSync(path.join(root,'Verification-lecteur.json'),JSON.stringify({statut:'PASS',tests:pass,viewport:[1440,320,390],autonome:true,iframe:'sandbox=allow-scripts',requetes_externes:externes,erreurs:faults},null,2)+'\n');console.log(`${pass} PASS`);
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
