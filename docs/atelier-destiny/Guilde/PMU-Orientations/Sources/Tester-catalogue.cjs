'use strict';
const fs=require('node:fs'),p=require('node:path'),os=require('node:os'),{pathToFileURL}=require('node:url'),assert=require('node:assert/strict'),{createHash}=require('node:crypto');
const H=os.homedir(),W=process.env.PMU_TRAVAIL||p.join(H,'.cache/pmu-orientations'),K=p.join(W,'Kit'), ROOT=p.resolve(__dirname,'..');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||p.join(H,'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const executablePath=process.env.CHROMIUM||p.join(H,'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const pageURL=pathToFileURL(p.join(K,'Catalogue.html')).href;
const idx=JSON.parse(fs.readFileSync(p.join(K,'Index-PMU-8.json'),'utf8'));
const digest=b=>createHash('sha256').update(b).digest('hex');
(async()=>{
 const b=await chromium.launch({executablePath,args:['--no-sandbox','--disable-dev-shm-usage']});
 const errors=[],network=[];
 try {
  const context=await b.newContext({viewport:{width:1320,height:920},offline:true,acceptDownloads:true,reducedMotion:'reduce'}), pg=await context.newPage();
  pg.on('pageerror',e=>errors.push(e.message));pg.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url());});
  await pg.goto(pageURL);await pg.waitForSelector('#sprite[data-direction="Down"]');
  assert.match(await pg.locator('#results').textContent(),/^360 modèles/);
  assert.equal(await pg.locator('#dirs button').count(),8);
  assert.equal(await pg.locator('#object-name').textContent(),'Pupitre aux cartes');
  await pg.screenshot({path:p.join(W,'Catalogue-bureau.png')});
  await pg.locator('#page-next').click();assert.equal(await pg.locator('#page-n').textContent(),'2 / 36');
  await pg.locator('#family').selectOption('pmu');assert.match(await pg.locator('#results').textContent(),/^346 modèles/);
  await pg.locator('#search').fill('mob_017');assert.match(await pg.locator('#results').textContent(),/^1 modèle /);
  assert.equal(await pg.locator('#object-name').textContent(),'Bibliothèque');
  for(const [i,label] of idx.projection.ordre.entries()){
   await pg.locator('#dirs button').nth(i).click();await pg.waitForSelector('#sprite[data-direction="'+label+'"]');
   assert.match(await pg.locator('#download').getAttribute('href'),new RegExp('/Mob_017/'+label+'\\.png$'));
  }
  await pg.locator('#dir-next').click();await pg.waitForSelector('#sprite[data-direction="Down"]');
  await pg.locator('#spin').click();await pg.waitForSelector('#sprite[data-direction="DownRight"]');await pg.locator('#spin').click();assert.equal(await pg.locator('#spin').getAttribute('aria-pressed'),'false');
  await pg.locator('#dirs button').nth(4).click();await pg.waitForSelector('#sprite[data-direction="Up"]');
  const target=idx.objets.find(o=>o.repere==='Mob_017');
  for(const [selector,fileInfo] of [['#download',target.vues[4]],['#atlas',target.atlas]]){
    const newPage=context.waitForEvent('page');await pg.locator(selector).click();const opened=await newPage;
    await opened.waitForLoadState();assert.equal(opened.url(),pathToFileURL(p.join(K,fileInfo.fichier)).href);
    const size=await opened.locator('img').evaluate(img=>[img.naturalWidth,img.naturalHeight]);assert.deepEqual(size,fileInfo.taille);
    assert.equal(digest(fs.readFileSync(p.join(K,fileInfo.fichier))),fileInfo.sha256);await opened.close();
  }
  await pg.locator('#search').fill('');await pg.locator('#family').selectOption('new');assert.match(await pg.locator('#results').textContent(),/^4 modèles/);
  await pg.locator('#search').fill('grainotheque');assert.equal(await pg.locator('#object-name').textContent(),'Grainothèque');
  await pg.locator('#search').fill('pomme-de-terreabsente');assert.equal(await pg.locator('.empty').count(),1);
  await pg.locator('#search').fill('');await pg.locator('#family').selectOption('ai');assert.match(await pg.locator('#results').textContent(),/^10 modèles/);
  await pg.setViewportSize({width:390,height:840});await pg.goto(pageURL);await pg.waitForSelector('#sprite[data-direction="Down"]');
  const sizes=await pg.evaluate(()=>[document.documentElement.scrollWidth,innerWidth]);assert.ok(sizes[0]<=sizes[1]);
  assert.equal(await pg.locator('#dirs button').count(),8);await pg.screenshot({path:p.join(W,'Catalogue-mobile.png'),fullPage:true});
  assert.deepEqual(errors,[]);assert.deepEqual(network,[]);
  fs.writeFileSync(p.join(ROOT,'Verification-catalogue.json'),JSON.stringify({statut:'PASS',catalogue:360,sources_pmu:346,nouveautes:4,bonus:10,appariement_profil_et_png:8,rotation:true,fichiers_ouverts_et_sha256:['PNG','atlas 4×2'],mobile_390_px:true,ressources_HTTP:network.length},null,2)+'\n');
  console.log('Catalogue hors ligne PASS · filtre, recherche, 8 directions, ouverture des PNG et atlas 1× et mobile.');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exit(1);});
