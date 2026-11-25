/* Browser smoke test. Install Playwright + Chromium, or set PLAYWRIGHT_MODULE / CHROMIUM_BIN. */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path=require('node:path');
const { pathToFileURL } = require('node:url');
const assert=require('node:assert/strict');
const root = path.resolve(__dirname,'..');
const file = path.join(root,'Fond-nu-et-nuages-EoS.html');
const html = fs.readFileSync(file,'utf8');
const screenshot = process.env.SCREENSHOTS;
let checks=0;
function same(a,b,message){assert.deepEqual(a,b,message);checks++;}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BIN||undefined,args:['--no-sandbox']});
 try {
 const ctx=await browser.newContext({viewport:{width:1360,height:890},offline:true,acceptDownloads:true});
 const errors=[],external=[];
 const page=await ctx.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
 await page.goto(pathToFileURL(file).href);await page.waitForSelector('html[data-ready=true]');
 const snap=()=>page.evaluate(()=>{const c=document.querySelector('canvas'),x=c.getContext('2d');const a=x.getImageData(0,0,c.width,c.height).data;let h=2166136261,rgb=0;for(let i=0;i<a.length;i+=4){h=Math.imul((h^(a[i]|a[i+1]<<8|a[i+2]<<16)),16777619);rgb+=a[i]+a[i+1]+a[i+2];}return [c.width,c.height,h,rgb];});
 const blank=await snap();same(blank.slice(0,2),[556,366],'dimensions native');
 same(await page.locator('#tab-base').getAttribute('aria-pressed'),'true','opens without cloud layer');
 const [dl]=await Promise.all([page.waitForEvent('download'),page.locator('#png').click()]);
 same(fs.readFileSync(await dl.path()).equals(fs.readFileSync(path.join(root,'Fond-nu-EoS-556x366.png'))),true,'download byte identical');
 if(screenshot)await page.screenshot({path:path.join(screenshot,'Atelier-Fond.png'),animations:'disabled'});
 await page.locator('#tab-states').click();
 const st=[];
 for(let i=1;i<=8;i++){
   await page.getByRole('button',{name:`Palier ${i}`,exact:true}).click();
   const s=await snap();same(s.slice(0,2),[504,336],`state ${i}`);st.push(s[2]);
 }
 same(new Set(st).size,8,'eight distinct states');
 same((await page.locator('#coverage').textContent()).replace(/\s/g,''),'0%','last state transparent');
 const seek=n=>page.locator('#timeline').evaluate((x,v)=>{x.value=v;x.dispatchEvent(new Event('input',{bubbles:true}));},n);
 await page.locator('#tab-demo').click();
 for(let i=2;i<=8;i++){
   await page.locator('#transition').selectOption(String(i));
   same((await snap())[2],st[i-2],`before ${i}`);
   await seek(16);same((await snap())[3],0,`black at swap ${i}`);
   await seek(33);const hold1=(await snap())[2];await seek(46);
   same((await snap())[2],hold1,`cloud bank stationary ${i}`);
   await seek(116);assert.notStrictEqual((await snap())[2],hold1,`bank visibly moving ${i}`);checks++;
   await seek(256);same((await snap())[2],st[i-1],`after ${i}`);
 }
 await page.locator('#transition').selectOption('2');await seek(120);
 if(screenshot)await page.screenshot({path:path.join(screenshot,'Atelier-Nuages.png'),animations:'disabled'});
 await page.locator('#viewport').click();same((await snap()).slice(0,2),[256,192],'DS viewport');
 same((await page.locator('#image-caption').textContent()).includes('Cible 15'),true,'uses marker 15');
 if(screenshot)await page.screenshot({path:path.join(screenshot,'Atelier-DS.png'),animations:'disabled'});
 await page.locator('#play').click();await page.waitForFunction(()=>Number(document.querySelector('#timeline').value)>131);
 await page.locator('#play').click();const paused=await page.locator('#timeline').inputValue();
 await page.waitForTimeout(200);same(await page.locator('#timeline').inputValue(),paused,'pause persists');
 await page.locator('#reset').click();same(await page.locator('#timeline').inputValue(),'0','reset');
 await seek(230);await page.locator('#play').click();await page.waitForFunction(()=>document.querySelector('#timeline').value==='256');
 same((await page.locator('#play').textContent()).includes('Rejouer'),true,'finishes');
 await page.locator('#tab-base').click();same(await snap(),blank,'base unmodified after demo');
 const mobile=await ctx.newPage({});mobile.on('pageerror',e=>errors.push(e.message));await mobile.setViewportSize({width:390,height:844});
 await mobile.goto(pathToFileURL(file).href);await mobile.waitForSelector('html[data-ready=true]');await mobile.locator('#tab-demo').click();await mobile.locator('#viewport').click();
 same(await mobile.evaluate(()=>document.documentElement.scrollWidth),390,'no horizontal desktop overflow on mobile');
 if(screenshot)await mobile.screenshot({path:path.join(screenshot,'Atelier-Mobile.png'),fullPage:true});
 const iframe=await ctx.newPage();iframe.on('pageerror',e=>errors.push(e.message));
 await iframe.setContent('<iframe id="preview" sandbox="allow-scripts" style="width:100%;height:700px"></iframe>');
 await iframe.locator('iframe').evaluate((f,s)=>{f.srcdoc=s;},html);
 const f=iframe.frameLocator('iframe');await f.locator('html[data-ready=true]').waitFor();await f.getByRole('button',{name:'Animation',exact:true}).click();
 same(await f.locator('#details-demo').isVisible(),true,'viewer sandbox runs offline');
 same(errors,[],'page errors');same(external,[],'external network requests');
 const report={controle:'PASS',assertions:checks,transitions:7,vues:['fond nu','états fixes','animation','cadre DS'],byte_identical_download:true,mode_hors_ligne:true,iframe_sandbox_allow_scripts:true,viewport_mobile_px:390,erreurs:errors,requêtes_HTTP:external};
 fs.writeFileSync(path.join(root,'Verification-apercu.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
