'use strict';
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const fs=require('node:fs'), path=require('node:path'), {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..'), work=path.resolve(process.argv[2]);fs.mkdirSync(work,{recursive:true});
const target=pathToFileURL(path.join(root,'Carte-Miracle-Destiny.html')).href+'?capture=1';
const order=JSON.parse(fs.readFileSync(path.join(root,'Atlas.json'),'utf8')).circuits.archipels;
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:868},deviceScaleFactor:1,offline:true});
  await page.goto(target);await page.waitForFunction(()=>window.carteMiracle?.snapshot().ready);
  if(await page.locator('#clouds').getAttribute('aria-pressed')==='true')await page.locator('#clouds').click();
  await page.mouse.move(1252,133);
  const fps=24, frames=fps*22, signals=[];let ending=false, got=new Set(), ship=false, foot=false;
  for(let i=0;i<frames;i++){
   const t=i/fps;
   if(i===30){
    await page.locator('#speed').selectOption('4');await page.locator('#circuitArchipels').click();
    await page.mouse.move(1252,133);
   }
   const s=await page.evaluate(ms=>window.carteMiracle.advance(ms),1000/fps);
   ship||=s.phase==='travel'&&s.transport==='mer';foot||=s.phase==='travel'&&s.transport==='terre';
   for(const e of s.events)if(e.type==='deblocage'&&!got.has(e.id)){signals.push({id:e.id,ms:Math.round(1000*t)});got.add(e.id);}
   if(!ending&&t>=18.5&&got.size===order.length&&s.phase==='idle'){
    await page.locator('#world').click();await page.mouse.move(1252,133);ending=true;
   }
   await page.screenshot({path:path.join(work,`${String(i).padStart(5,'0')}.jpg`),type:'jpeg',quality:90});
  }
  if(!ship||!foot||!ending||signals.map(e=>e.id).join(',')!==order.join(','))throw Error('Capture incomplète : '+JSON.stringify({signals,ship,foot,ending}));
  fs.writeFileSync(path.join(work,'capture.json'),JSON.stringify({fps,frames,signals,dimensions:[1280,868],marche:foot,navigation:ship,vue_complete_finale:ending},null,2));console.log('Capture:',signals);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
