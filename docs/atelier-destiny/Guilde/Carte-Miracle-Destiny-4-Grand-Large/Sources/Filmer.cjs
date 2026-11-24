'use strict';
const {chromium}=require(process.env.PLAYWRIGHT||'playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..'),out=path.resolve(process.argv[2]);fs.mkdirSync(out,{recursive:true});
const url=pathToFileURL(path.join(root,'Carte-Miracle-Destiny-4.html')).href+'?capture=1',fps=20,dimensions=[1160,836];
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:dimensions[0],height:dimensions[1]},offline:true});await p.goto(url);await p.waitForFunction(()=>window.carteMiracle?.snapshot().ready);await p.mouse.move(1149,120);let i=0;const sig=[];
 const tick=ms=>p.evaluate(t=>window.carteMiracle.advance(t),ms),img=()=>p.screenshot({path:path.join(out,`${String(i++).padStart(5,'0')}.jpg`),type:'jpeg',quality:86});
 await p.screenshot({path:path.join(root,'Destiny-4-Depart-Voile.png')});for(let k=0;k<13;k++){await tick(50);await img();}
 await p.locator('#speed').selectOption('4');
 for(const [site,zone] of [['chute-sylverive','sylverive'],['grotte-frimas','grand-frimas']]){
  await p.locator('#destination').selectOption(site);await p.locator('#depart').click();await p.mouse.move(1149,120);
  const r=await tick(0);let s=await tick(Math.max(0,r.totalTime*250-920)),started=false,finished=false,after=0;
  for(let k=0;k<155;k++){
   s=await tick(50);if(s.opening?.zone===zone)started=true;
   if(started&&!finished&&!s.opening){finished=true;sig.push({zone,site,ms:Math.round(i/fps*1000)});}
   if(s.opening?.zone==='grand-frimas'&&s.opening.tick>=102&&s.opening.tick<=104)await p.screenshot({path:path.join(root,'Destiny-4-Ouverture-Givre.png')});
   await img();if(finished&&++after===24)break;
  }
  assert.equal(s.current,site);assert.ok(started&&finished&&!s.worldUnlocked);
 }
 fs.writeFileSync(path.join(out,'capture.json'),JSON.stringify({fps,frames:i,dimensions,signals:sig,carte_entiere_non_affichee:true,ouvertures_reelles:true},null,2));console.log(i+' images');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1)});
