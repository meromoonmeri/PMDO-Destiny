'use strict';
// Bake deterministic video frames with the actual workshop rasterizer. The capture
// bridge is only in a temporary page, never in the delivered atelier.
const fs=require('node:fs'),path=require('node:path'),{homedir}=require('node:os'),{pathToFileURL}=require('node:url');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(homedir(),'.cache/guildhouse-mega-remixes/test-navigateur/node_modules/playwright'));
const exe=process.env.CHROMIUM||path.join(homedir(),'.cache/ms-playwright/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell');
const root=path.resolve(__dirname,'..'), w=path.join(homedir(),'.cache/destiny-feux-rayons');
const h=fs.readFileSync(path.join(root,'..','Guilde-Destiny-Drapeaux-Foyers-Bibliotheque.html'),'utf8');
const seam='setupMotion();\n})();';if(!h.includes(seam))throw Error('Atelier incompatible');
const bridge=`setupMotion();
window.captureVideo=async function({type,p=0,ms=0,fire='allumees',show=true,alt=false}){
 let id=type==='flag'?ext.accueil:type==='foyer'?fireplaces.salle:shelves.salle,r=gameMap.get(id),items=[];
 extState.fire=fire;extState.shelves=show;for(const v of shelves.slots)extState.slots[v.id]=v.defaut;
 if(alt)Object.assign(extState.slots,{ouest:'atlas',centre:'herbiers',est:'archives'});
 if(type==='flag')for(const [key,px,py] of [['etendard-downright',156,217],['etendard-downleft',356,217]]){
  const v=flagSpecs.get(key),a=assets.get(key),x=px-v.pivot[0],y=py-v.pivot[1];if(why(r,a,x,y))throw Error('Pose de drapeau inexploitable');items.push({id:key,meuble:key,x,y});
 }
 const c=make('canvas');resize(c,r.w,r.h);
 for(let j=0;j<150;j++){
  drawScene(c.getContext('2d'),r,p,planVue(r),{items,ms});
  if(c.dataset.scene)return c.toDataURL('image/png');
  await new Promise(q=>setTimeout(q,12));
 }throw Error('Calques indisponibles');
};
})();`;
(async()=>{
 fs.mkdirSync(w,{recursive:true});const tmp=path.join(w,'Captures-video.html');fs.writeFileSync(tmp,h.replace(seam,bridge));
 const browser=await chromium.launch({executablePath:exe,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{const p=await browser.newPage({viewport:{width:1250,height:920},reducedMotion:'reduce'});
  const errors=[];p.on('pageerror',e=>errors.push(e.stack));await p.goto(pathToFileURL(tmp).href);await p.waitForFunction(()=>typeof captureVideo==='function');
  const send=async (name,args)=>{
   const t=await p.evaluate(args=>window.captureVideo(args),args);const f=Buffer.from(t.split(',')[1],'base64');fs.writeFileSync(path.join(w,'Video-'+name+'.png'),f);
  };
  for(let k=0;k<4;k++)await send('foyer-'+k,{type:'foyer',p:3,ms:k*100+.2});
  await send('foyer-off',{type:'foyer',p:3,fire:'eteintes'});await send('foyer-jour',{type:'foyer',p:0});
  for(let k=0;k<6;k++)await send('flag-'+k,{type:'flag',ms:k*125});
  for(const [n,o] of [['bib',{type:'shelves'}],['bib-alt',{type:'shelves',alt:true}],['bib-nuit',{type:'shelves',p:3}],['bib-sans',{type:'shelves',show:false}]])await send(n,o);
  if(errors.length)throw Error(errors.join('\n'));console.log('16 images par le moteur d’atelier, dont 4 poses des cheminées de nuit.');
 }finally{fs.rmSync(tmp,{force:true}); await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
