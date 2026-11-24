'use strict';
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..'),work=path.resolve(process.argv[2]);fs.mkdirSync(work,{recursive:true});
const config=JSON.parse(fs.readFileSync(path.join(__dirname,'Nuages.json'),'utf8'));
const target=pathToFileURL(path.join(root,'Carte-Miracle-Destiny.html')).href+'?capture=1';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--no-sandbox']});
 try{
  const dimensions=[1280,900],page=await browser.newPage({viewport:{width:dimensions[0],height:dimensions[1]},deviceScaleFactor:1,offline:true});
  await page.goto(target);await page.waitForFunction(()=>window.carteMiracle?.snapshot().ready);
  await page.mouse.move(1264,139);
  const fps=20,frames=fps*37,signals=[],opened=new Set(),shown=new Set();let ending=false,nav=false,stilled=false;
  const rect=await page.locator('#stage').boundingBox();
  for(let i=0;i<frames;i++){
   if(i===26){await page.locator('#speed').selectOption('4');await page.locator('#circuitNuages').click();await page.mouse.move(1264,139);}
   const s=await page.evaluate(t=>window.carteMiracle.advance(t),1000/fps);
   if(s.phase==='travel'&&s.transport==='mer')nav=true;
   if(s.opening&&s.opening.progress>.42)shown.add(s.opening.zone);
   for(const e of s.events)if(e.type==='ouverture-zone'&&!opened.has(e.id)){
    signals.push({id:e.site,zone:e.id,ms:Math.round(i/fps*1000)});opened.add(e.id);
   }
   if(!ending&&opened.size===config.circuit.length&&s.phase==='idle'){
    await page.locator('#world').click();await page.mouse.move(1264,139);ending=true;
   }
   if(ending&&s.camera.z<1.005)stilled=true;
   await page.screenshot({path:path.join(work,`${String(i).padStart(5,'0')}.jpg`),type:'jpeg',quality:89});
  }
  assert.deepEqual(signals.map(s=>s.id),config.circuit,'Every scripted stay opens its region');
  assert.ok(nav&&ending&&stilled&&shown.size===config.circuit.length,'All cloud motions and the fully revealed map must be visible');
  fs.writeFileSync(path.join(work,'capture.json'),JSON.stringify({edition:'nuages',fps,frames,signals,dimensions,
   carte:[Math.ceil(rect.x),Math.ceil(rect.y),Math.floor(rect.width/2)*2-2,Math.floor(rect.height/2)*2-2],vue_complete_finale:true},null,2));
  console.log('Ouvertures filmées :',signals);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
