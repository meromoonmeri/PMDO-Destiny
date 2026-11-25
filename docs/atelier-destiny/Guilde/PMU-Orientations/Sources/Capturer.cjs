'use strict';
// Video-only renderer. The bridge runs in an ephemeral copy of the prior atelier.
const fs=require('node:fs'),p=require('node:path'),os=require('node:os'),{pathToFileURL}=require('node:url'),{createHash}=require('node:crypto');
const H=os.homedir(), S=__dirname, R=p.resolve(S,'../..'), W=process.env.PMU_TRAVAIL||p.join(H,'.cache/pmu-orientations'), K=p.join(W,'Kit');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||p.join(H,'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const executablePath=process.env.CHROMIUM||p.join(H,'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const base=p.join(R,'Guilde-Destiny-Drapeaux-Foyers-Bibliotheque.html'), html=fs.readFileSync(base,'utf8'), idx=JSON.parse(fs.readFileSync(p.join(K,'Index-PMU-8.json'),'utf8'));
const refs=new Map(idx.objets.map(a=>[a.repere,a]));
const sha=s=>createHash('sha256').update(s).digest('hex');
const out=p.join(W,'Scenes');fs.mkdirSync(out,{recursive:true});
const SEAM='setupMotion();\n})();';if(!html.includes(SEAM))throw Error('Le moteur de départ a changé.');
const bridge=`setupMotion();
window.pmuPose=async function({id,pp=0,ms=0,q=[]}){
  const r=gameMap.get('guilde_destiny_'+id), c=make('canvas'),items=[];
  for(const o of q){const [k,a,b]=o.key;const id='pmu-video-'+k+'-'+a;const a0={id,label:k,w:o.w,h:o.h,category:o.flat?'tapis':'meubles',wall:false,previewOnly:true,m:[o.png]};
    assets.set(id,a0);const x=o.x-o.px,y=o.y-o.py;
    const err=why(r,a0,x,y,null,items);if(err)throw Error(k+' '+a+' ('+x+','+y+'), '+r.label+' : '+err);
    const floor=r.floor[Math.floor(o.y/8)]?.[Math.floor(o.x/8)];if(floor!=='1')throw Error(k+' : pivot hors sol praticable.');
    items.push({id,meuble:id,x,y});}
  resize(c,r.w,r.h);extState.fire='allumees';extState.shelves=true;
  for(let j=0;j<120;j++){
    drawScene(c.getContext('2d'),r,pp,planVue(r),{items,ms,lianes:true});
    if(c.dataset.scene)return {png:c.toDataURL('image/png').split(',')[1],layout:items,calque:c.dataset.architecture};
    await new Promise(resolve=>setTimeout(resolve,15));
  }throw Error('Rendu incomplet '+r.label);
};
})();`;
const plans={cuisine:[['tapis_bleu',1,149,205],['Creation_Pupitre-aux-cartes',1,149,201],['Creation_Horloge-lunaire',7,369,187],['coffre_bois_bleu',7,321,241]],
refectoire:[['Mob_038',1,169,211],['Mob_030',2,94,260],['Creation_Grainotheque',7,431,217],['Creation_Chariot-a-the',1,336,286],['DecB_259',0,426,284]]};
function objects(conf){return conf.map(([key,i,x,y])=>{const r=refs.get(key), a=r.vues[i];return {key:[key,a.direction],x,y,w:a.taille[0],h:a.taille[1],px:a.pivot[0],py:a.pivot[1],flat:r.gabarit==='sol',png:fs.readFileSync(p.join(K,a.fichier)).toString('base64')};});}
(async()=>{
 const temp=p.join(out,'Moteur-temporaire.html');fs.writeFileSync(temp,html.replace(SEAM,bridge));
 const b=await chromium.launch({executablePath,args:['--no-sandbox','--disable-dev-shm-usage']});
 try {
  const ctx=await b.newContext({offline:true,viewport:{width:1320,height:880},reducedMotion:'reduce'}), page=await ctx.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.stack));await page.goto(pathToFileURL(temp).href);await page.waitForFunction(()=>typeof window.pmuPose==='function');
  const report=[];
  async function capture(file,id,pp,ms,poses){
   const got=await page.evaluate(x=>window.pmuPose(x),{id,pp,ms,q:objects(poses)});const png=Buffer.from(got.png,'base64');fs.writeFileSync(p.join(out,file+'.png'),png);report.push({file,id,pp,ms,poses,layout:got.layout,calque:got.calque,sha256:sha(png)});
  }
  for(let i=0;i<8;i++){
    const bib=plans.cuisine.map((p,k)=>k===1?[p[0],i,p[2],p[3]]:p);
    const ref=plans.refectoire.map((p,k)=>k===3?[p[0],i,p[2],p[3]]:p);
    await capture('Bibliotheque-'+i,'cuisine',0,0,bib);await capture('Refectoire-'+i,'refectoire',0,0,ref);
  }
  for(let i=0;i<4;i++)await capture('Refectoire-Nuit-'+i,'refectoire',3,i*100+.1,plans.refectoire);
  if(errors.length)throw Error(errors.join('\n'));await ctx.close();
  fs.writeFileSync(p.join(R,'PMU-Orientations','Verification-poses-video.json'),JSON.stringify({statut:'PASS',rendus:report.length,source_sha256:sha(html),copie_temporaire:true,scenes:report},null,2)+'\n');
  console.log(report.length+' scènes du moteur Destiny, pivots et seuils contrôlés.');
 }finally{fs.rmSync(temp,{force:true});await b.close();}
})().catch(e=>{console.error(e);process.exit(1);});
