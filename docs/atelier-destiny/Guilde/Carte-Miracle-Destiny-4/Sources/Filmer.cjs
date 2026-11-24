'use strict';
const {chromium}=require(process.env.PLAYWRIGHT||'playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..'),work=path.resolve(process.argv[2]);fs.mkdirSync(work,{recursive:true});
const file=pathToFileURL(path.join(root,'Carte-Miracle-Destiny-4.html')).href+'?capture=1';
const atlas=JSON.parse(fs.readFileSync(path.join(root,'Atlas.json'),'utf8'));
// Film excerpts of the actual 23-zone journey, skipping frames rather than skipping any discovery.
const show=new Set(['grotte-ocre','grotte-givre','phare-alizes','refuge-falaises','bastion-boreal','port-austral']);
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--no-sandbox']});
 try{
  const fps=20, dimensions=[1280,868],p=await b.newPage({viewport:{width:dimensions[0],height:dimensions[1]},deviceScaleFactor:1,offline:true});
  await p.goto(file);await p.waitForFunction(()=>window.carteMiracle?.snapshot().ready);await p.mouse.move(1267,140);
  await p.screenshot({path:path.join(root,'Destiny-4-Depart-Voile.png')});
  const observed=new Set(),signals=[];let frames=0,after=0,world=false,poster=false;
  for(let i=0;i<1800;i++){
   if(i===24){await p.locator('#speed').selectOption('4');await p.locator('#circuitNuages').click();await p.mouse.move(1267,140);}
   const s=await p.evaluate(ms=>window.carteMiracle.advance(ms),1000/fps);
   for(const e of s.events)if(e.type==='ouverture-zone'&&!observed.has(e.id)){
    observed.add(e.id);if(show.has(e.site))signals.push({zone:e.id,site:e.site,ms:Math.round(1000*frames/fps)});
   }
   if(!world&&s.worldUnlocked&&s.phase==='idle'){
    assert.equal(observed.size,23);await p.locator('#world').click();await p.mouse.move(1267,140);world=true;
   }
   if( i<24||show.has(s.selected)||world){
    if(s.opening?.zone==='seracine'&&s.opening.progress>.68&&!poster){await p.screenshot({path:path.join(root,'Destiny-4-Ouverture-Givre.png')});poster=true;}
    await p.screenshot({path:path.join(work,`${String(frames++).padStart(5,'0')}.jpg`),type:'jpeg',quality:90});
   }
   if(world&&++after>=57){assert.ok(s.camera.z<1.005&&s.openedZones.length===24);break;}
  }
  assert.deepEqual([...observed],atlas.circuits.nuages.map(id=>atlas.sites.find(a=>a.id===id).area));assert.ok(poster&&world&&signals.length===6);
  fs.writeFileSync(path.join(work,'capture.json'),JSON.stringify({fps,frames,dimensions,signals,zones_reellement_ouvertes:['reve',...observed],montage:true,finale_apres_deblocage:true},null,2));console.log(`${frames} images, 24 zones ouvertes avant la vue complète`);
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
