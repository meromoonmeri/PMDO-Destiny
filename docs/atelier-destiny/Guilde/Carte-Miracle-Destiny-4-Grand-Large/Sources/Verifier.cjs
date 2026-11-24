'use strict';
const {chromium}=require(process.env.PLAYWRIGHT||'playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..'),fn=path.join(root,'Carte-Miracle-Destiny-4.html'),atlas=JSON.parse(fs.readFileSync(path.join(root,'Atlas.json'),'utf8')),url=pathToFileURL(fn).href+'?capture=1';
const checks=[], errors=[], network=[];const ok=(x,message)=>{assert.ok(x,message);checks.push(message);};const by=Object.fromEntries(atlas.sites.map(s=>[s.id,s]));const wan=atlas.nuages.skyTemple;
const snap=p=>p.evaluate(()=>window.carteMiracle.snapshot()),step=(p,ms)=>p.evaluate(n=>window.carteMiracle.advance(n),ms);
const ready=p=>p.waitForFunction(()=>window.carteMiracle?.snapshot().ready);
const draw=p=>p.locator('#chart').evaluate(c=>c.toDataURL());
const button=(p,id)=>p.locator('#'+id);const lock=p=>button(p,'world').isDisabled();
function watch(p){p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url());});}
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--no-sandbox']});
 try{
  const cx=await b.newContext({viewport:{width:1280,height:870},offline:true});const p=await cx.newPage();watch(p);await p.goto(url);await ready(p);let s=await snap(p);
  ok(s.current==='reverie'&&s.openedZones.join(',')==='reve'&&s.totalZones===32&&s.total===95,'Réverie seule au départ ; 32 zones, 95 lieux');
  ok(s.found.join(',')==='reverie'&&s.visibles===6,'Repères trouvés et zones dégagées distincts');
  ok(await lock(p)&&!s.worldUnlocked&&!(await p.locator('#repere-etang-saules').isVisible()),'Grand Large voilé au départ');
  ok(await p.locator('#destination optgroup[label^="Grand Large"]').count()===8,'8 groupes indépendants dans le carnet');
  ok(atlas.sites.filter(x=>x.realm==='Grand Large'&&x.motif_ds).length===50,'50 repères reliés aux dessins sur la grille DS');
  ok(atlas.placements.heritage.silhouettes===101,'Les 101 silhouettes historiques sont présentes');
  ok(atlas.nuages.duree===(wan.noir_sortie+wan.compteur)/wan.fps&&wan.compteur===240&&wan.delai===30&&wan.noir_sortie===16&&wan.noir_entree===16,'Horloge native : noir 16/16, compteur 240, délai 30');
  ok(wan.objets.length===5&&wan.objets.map(o=>o.pose).join(',')==='1,1,1,0,15','Grand banc WAN 15 et quatre petits nuages natifs');
  const still=await draw(p);await step(p,650);ok(still===await draw(p),'Les terrains et le voile restent fixes au repos');
  await button(p,'world').evaluate(el=>el.dispatchEvent(new MouseEvent('click',{bubbles:true})));s=await step(p,950);ok(s.camera.z>=s.minZoom&&!s.worldUnlocked,'Le clic forcé ne montre pas la carte entière');
  await button(p,'stage').focus();await p.keyboard.press('0');await step(p,550);ok(await lock(p),'Le raccourci 0 n’enlève pas le voile');
  await button(p,'reset').click();await button(p,'depart').click();s=await step(p,300);ok(s.transport==='terre'&&s.phase==='travel','Réverie : départ à pied');
  await button(p,'pause').click();let q=await step(p,500);ok(q.paused&&q.elapsed===s.elapsed,'La pause immobilise l’équipe');await button(p,'pause').click();
  s=await step(p,s.totalTime*1000+1700);ok(s.found.includes('fosse')&&s.openedZones.length===1,'Une arrivée dans une zone connue ne rejoue pas les nuages');
  await button(p,'reset').click();await button(p,'speed').selectOption('4');await button(p,'destination').selectOption('etang-saules');await button(p,'depart').click();s=await snap(p);
  s=await step(p,Math.max(0,s.totalTime*250-143));ok(s.phase==='travel'&&!s.opening&&s.events.some(x=>x.type==='transport'&&x.mode==='mer'),'La barque précède l’ouverture d’une nouvelle île');
  s=await step(p,211);ok(s.opening?.zone==='sylverive'&&s.opening.tick<16&&s.opening.objets.length===0,'Le fondu démarre à l’arrivée');
  s=await step(p,550);ok(s.opening.tick>=16&&s.opening.tick<46&&s.opening.objets.length===5,'Les cinq nuages arrivent mais ne se déplacent pas avant le délai');
  ok(s.opening.objets.every((o,i)=>o.origin.join()===wan.objets[i].origine.join()),'Origines des objets = données SkyTemple');
  s=await step(p,950);const age=s.opening.tick-16-wan.delai;
  ok(age>0&&s.opening.objets.every((o,i)=>o.origin.every((v,j)=>v===Math.trunc((wan.objets[i].origine[j]*256+wan.objets[i].vitesse[j]*age)/256))),'Déplacement exact en coordonnées fixes 8.8');
  ok(!(await p.locator('#repere-chute-sylverive').isVisible())&&await lock(p),'Aucun repère de l’île en cours d’ouverture n’est montré prématurément');
  const mid=await draw(p);await button(p,'pause').click();q=await step(p,630);ok(q.opening.tick===s.opening.tick&&mid===await draw(p),'Pause des nuages : image inchangée');await button(p,'pause').click();
  s=await step(p,4000);ok(s.openedZones.join(',')==='reve,sylverive'&&s.phase==='idle'&&!s.worldUnlocked,'Seule Sylverive est dévoilée à la première escale');
  ok(await p.locator('#repere-chute-sylverive').isVisible()&&!(await p.locator('#repere-grotte-frimas').isVisible()),'La cascade visible, le Frimas reste masqué');
  await p.reload();await ready(p);s=await snap(p);ok(s.current==='etang-saules'&&!s.opening&&s.openedZones.length===2,'Sauvegarde complète après la levée');
  await button(p,'reset').click();await button(p,'speed').selectOption('4');await button(p,'circuitGrandLarge').click();s=await snap(p);ok(s.selected==='lac-veilles'&&s.sequence.length===7,'Le circuit Grand Large route huit escales');
  await button(p,'reset').click();await button(p,'speed').selectOption('4');await button(p,'circuitNuages').click();
  let late=false;const observed=new Set(),arrived=new Set();
  for(let i=0;i<1000;i++){
   s=await step(p,250);for(const e of s.events){if(e.type==='ouverture-zone')observed.add(e.id);if(e.type==='arrive')arrived.add(e.id);}
   if(s.openedZones.length===31&&!late){ok(await lock(p)&&!s.worldUnlocked,'À 31/32, vue entière encore verrouillée');late=true;}
   if(s.openedZones.length===32&&s.opening){ok(await lock(p)&&!s.worldUnlocked,'À 32/32, attendre la fin du dernier nuage');break;}
  }
  const expected=atlas.circuits.nuages.map(i=>by[i].area);ok(late&&s.opening?.zone==='cendres'&&[...observed].join()===expected.join()&&arrived.size===31,'Les 31 arrivées ont réellement déclenché les 31 ouvertures attendues');
  await p.reload();await ready(p);s=await snap(p);ok(s.opening?.zone==='cendres'&&!s.worldUnlocked&&await lock(p),'Recharger au dernier nuage ne contourne pas le verrou');
  s=await step(p,4900);ok(s.worldUnlocked&&s.openedZones.length===32&&s.found.length===32&&s.phase==='idle','Vue complète après la dernière transition uniquement');
  await button(p,'world').click();s=await step(p,1440);ok(s.camera.z<1.005&&s.visibles===95&&!s.follow,'La vue débloquée contient les 95 repères');
  if(process.argv[2]){fs.mkdirSync(process.argv[2],{recursive:true});await p.screenshot({path:path.join(process.argv[2],'Monde-debloque.png')});}
  await button(p,'reset').click();s=await snap(p);ok(s.openedZones.join()=== 'reve'&&await lock(p),'Recommencer referme le monde');await cx.close();
  for(const width of [320,390]){
   const mobile=await b.newContext({viewport:{width,height:850},isMobile:true,deviceScaleFactor:1,hasTouch:true,offline:true});const m=await mobile.newPage();watch(m);await m.goto(url);await ready(m);
   ok(await m.evaluate(()=>document.documentElement.scrollWidth===innerWidth)&&await lock(m),`Voile verrouillé, sans débordement à ${width}px`);await button(m,'depart').tap();s=await step(m,6000);ok(s.found.includes('fosse'),`Voyage jouable sur écran ${width}px`);await mobile.close();
  }
  const frameCtx=await b.newContext({viewport:{width:1000,height:864},offline:true});const fp=await frameCtx.newPage();watch(fp);
  await fp.setContent('<iframe sandbox="allow-scripts" title="Destiny 4" style="width:100%;height:820px;border:0" srcdoc="'+fs.readFileSync(fn,'utf8').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;')+'"></iframe>');
  const frame=fp.frames()[1];await ready(frame);ok((await snap(frame)).openedZones.join()==='reve'&&await lock(frame),'L’aperçu sandbox fonctionne hors ligne');await button(frame,'speed').selectOption('4');await button(frame,'depart').click();await frame.waitForFunction(()=>window.carteMiracle.snapshot().found.includes('fosse'));ok(true,'L’iframe permet une vraie arrivée');await frameCtx.close();
  const motion=await b.newContext({offline:true,reducedMotion:'reduce'});const m=await motion.newPage();watch(m);await m.goto(url);await ready(m);await button(m,'speed').selectOption('4');await button(m,'destination').selectOption('lac-veilles');await button(m,'depart').click();s=await step(m,10000);ok(!s.opening&&s.openedZones.includes('nacrebrune')&&!s.worldUnlocked,'Mouvement réduit : vraie arrivée sans animation, verrou préservé');await motion.close();
  ok(!errors.length,'Aucune erreur JavaScript : '+errors.join());ok(!network.length,'Aucune requête réseau');
  fs.writeFileSync(path.join(root,'Verification-lecteur.json'),JSON.stringify({statut:'PASS',tests:checks.length,details:checks,zones:32,lieux:95,ouvertures:31,wan,aucune_requete_externe:true},null,2)+'\n');console.log(checks.length+' contrôles PASS');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
