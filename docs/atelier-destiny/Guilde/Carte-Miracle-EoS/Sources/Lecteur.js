(() => {
 'use strict';
 const D=JSON.parse(document.getElementById('assets').textContent), E=window.AtlasEos;
 const $=id=>document.getElementById(id), map=$('map'), gfx=map.getContext('2d',{alpha:false});
 const imgs=new Map(),fps=D.fps,units=document.querySelectorAll('[data-layer]');
 let part='film',route='blizzard',P=E.makePlan(D,part,route),base='eos',view='ds',rate=1;
 let cursor=0,poster=true,ended=false,playing=false,pending=false,muted=false,active=false;
 let tickRendered=-1,lastFrame=null,clock=null,version=0,raf=0;
 let ac=null,output=null,analyser=null,sources=[],audioLog=[];
 const cacheAudio=new Map();
 const sourceImg=a=>imgs.get(a.fichier);
 const timeString=seconds=>{
   const d=Math.floor(Math.max(0,seconds)*10),m=Math.floor(d/600);
   return `${m}:${String(Math.floor(d/10)%60).padStart(2,'0')}.${d%10}`;
 };
 const elapsedSeconds=t=>t/fps;
 const text=(el,s)=>{if(el.textContent!==s)el.textContent=s;};
 function changeButton(b,yes){b.setAttribute('aria-pressed',String(yes));}
 function buttons(){
   const on=playing||pending;
   $('play-use').setAttribute('href',on?'#pause-icon':'#play-icon');
   text($('play-word'),on?'Pause':ended?'Rejouer':'Lire');
   $('toggle-play').setAttribute('aria-label',on?'Mettre en pause':ended?'Rejouer le passage':'Lire le passage');
   changeButton($('mute'),muted);$('mute').title=muted?'Réactiver le son':'Couper le son';$('mute').setAttribute('aria-label',$('mute').title);
   $('sound-use').setAttribute('href',muted?'#silent-icon':'#sound-icon');
   changeButton($('rate'),rate<1);text($('rate'),rate<1?'½×':'1×');$('rate').title=rate<1?'Revenir à la vitesse normale':'Passer au ralenti';$('rate').setAttribute('aria-label',$('rate').title);
   changeButton($('view'),view==='entier');text($('view-word'),view==='entier'?'Écran DS':'Vue entière');$('view').title=view==='entier'?'Revenir au cadrage DS':'Afficher la carte entière';
   for(const b of units)changeButton(b,b.dataset.layer===base);
 }
 function updateChapters(f){
   const isTravel=f.part==='voyage';
   text($('scene-no'),isTravel?'02':'01');text($('scene-kind'),isTravel?'Voyage':'Déblocage');
   text($('scene-title'),isTravel?P.T.nom:'Île Blizzard');
   $('chapter-unlock').classList.toggle('active',!isTravel);changeButton($('chapter-unlock'),!isTravel);
   $('chapter-travel').classList.toggle('active',isTravel);changeButton($('chapter-travel'),isTravel);
   const r=route==='blizzard';text($('route-card-title'),r?'Vers l’Île Blizzard':'Vers la Caverne Saline');
   text($('route-detail'),r?'De Bourg-Trésor à l’Île Blizzard, entre deux points natifs. Ce trajet est recomposé.':'De Bourg-Trésor à la Caverne Saline, comme dans la scène du jeu. Le trajet est très court : essaie ½×.');
 }
 function initTimeline(){
   $('seek').max=String(P.total-1);text($('duration'),`${(P.total/fps).toFixed(1).replace('.',',')} s`);
   $('notches').replaceChildren(...P.marks.filter(a=>a.key!=='rouge').map(m=>{const i=document.createElement('i');i.style.left=`${100*m.t/(P.total-1)}%`;return i;}));
   $('moments').replaceChildren(...P.marks.map(m=>{
     const b=document.createElement('button');b.type='button';b.dataset.key=m.key;b.textContent=m.label;
     b.addEventListener('click',()=>jump(m.t,m.key==='jingle'));return b;
   }));
 }
 function draw(t,force=false){
   const d=poster ? P.U.jingle : E.clip(Math.floor(t),0,P.total-1);
   if(!force&&d===tickRendered)return;
   tickRendered=d;const f=E.frame(D,P,d,{base,view}), c=f.cam;lastFrame=f;
   if(map.width!==c.w||map.height!==c.h){map.width=c.w;map.height=c.h;}
   gfx.imageSmoothingEnabled=false;gfx.globalAlpha=1;gfx.fillStyle='#000';gfx.fillRect(0,0,c.w,c.h);
   const layer=base==='nu'?D.fond_nu:D.terrain;
   gfx.drawImage(sourceImg(layer),-c.x,-c.y,...D.carte);
   gfx.drawImage(sourceImg(D.masques[String(f.level)]),-c.x,-c.y);
   for(const sp of f.sprites){const a=E.poseDef(D,sp);gfx.drawImage(sourceImg(a),sp.x+a.coin_relatif[0]-c.x,sp.y+a.coin_relatif[1]-c.y);}
   if(f.black){gfx.globalAlpha=f.black;gfx.fillRect(0,0,c.w,c.h);gfx.globalAlpha=1;}
   $('stage').dataset.view=view;
   const label=view==='ds'?'Écran DS · 256 × 192':'Carte entière · 504 × 336';
   text($('screen-label'),label);text($('map-coords'),base==='nu'?'Parchemin seul':`S01P01A · palier ${f.level}`);
   text($('phase-title'),ended?'Fin du passage':f.kind);text($('caption'),ended?'Rejoue la scène ou choisis un moment dans la frise.':f.caption);
   map.setAttribute('aria-label',`${label}. ${f.kind}. ${f.caption}`);
   $('me-badge').hidden=f.phase!=='jingle'||ended;
   $('blank-stage').hidden=!ended;
   $('stage').dataset.phase=ended?'fin':f.phase;
   $('stage').dataset.flash=f.highlight||'';
   let timeOnUI=poster?0:ended?P.total:d;
   const input=$('seek');input.value=String(Math.min(P.total-1,timeOnUI));
   input.style.setProperty('--pct',`${100*timeOnUI/P.total}%`);
   input.setAttribute('aria-valuetext',`${timeString(elapsedSeconds(timeOnUI))} · ${f.kind}`);
   text($('clock'),`${timeString(elapsedSeconds(timeOnUI))} / ${timeString(elapsedSeconds(P.total))}`);
   for(const b of $('moments').children){
     const m=P.marks.find(x=>x.key===b.dataset.key);
     b.classList.toggle('is-current',!poster&&(f.phase===m.key&&m.key!=='rouge'||m.key==='rouge'&&d===m.t));
   }
   updateChapters(f);
 }
 function stopSources(){for(const s of sources){try{s.stop();}catch{} try{s.disconnect();}catch{}} sources=[];}
 const tNow=()=>clock?.ac?clock.ac.currentTime:performance.now()/1000;
 function liveTick(){return clock ? E.clip(clock.pos+(Math.max(0,tNow()-clock.at))*fps*clock.rate,0,P.total) : cursor;}
 function pause(){
   if(playing)cursor=liveTick();
   version++; playing=false;pending=false;clock=null;cancelAnimationFrame(raf);stopSources();buttons();
 }
 function ensureContext(){
   const Api=window.AudioContext||window.webkitAudioContext;
   if(!Api)throw Error('Web Audio non disponible');
   if(!ac){ac=new Api();output=ac.createGain();output.gain.value=muted?0:.92;
     analyser=ac.createAnalyser();analyser.fftSize=512;output.connect(analyser);analyser.connect(ac.destination);}
   return ac.resume();
 }
 function audioFor(speed){
   const sid=String(speed);
   if(!cacheAudio.has(sid)){
     const from=(uri)=>{const b=atob(uri.slice(uri.indexOf(',')+1));const a=new Uint8Array(b.length);for(let i=0;i<a.length;i++)a[i]=b.charCodeAt(i);return ac.decodeAudioData(a.buffer);};
     cacheAudio.set(sid,Promise.all(['me','bgm'].map(k=>from(D.audio[k][sid].uri))).then(a=>({me:a[0],bgm:a[1]})).catch(e=>{cacheAudio.delete(sid);throw e;}));
   }
   return cacheAudio.get(sid);
 }
 function schedule(buffers){
   audioLog=[];
   for(const e of P.events){
     const first=Math.max(e.at,cursor),last=e.until;
     if(first>=last)continue;
     const scale=1/(fps*rate), offset=(first-e.at)*scale, at=clock.at+(first-cursor)*scale;
     const len=Math.min(buffers[e.key].duration-offset,(last-first)*scale);
     if(len<=0)continue;
     const gain=ac.createGain(),s=ac.createBufferSource();s.buffer=buffers[e.key];s.connect(gain);gain.connect(output);s.onended=()=>gain.disconnect();
     const v=e.fadeAt===null||first<=e.fadeAt?e.gain:e.gain*E.clip((last-first)/(last-e.fadeAt),0,1);
     gain.gain.setValueAtTime(v,at);
     if(e.fadeAt!==null){
       if(first<e.fadeAt)gain.gain.setValueAtTime(e.gain,at+(e.fadeAt-first)*scale);
       gain.gain.linearRampToValueAtTime(0,clock.at+(last-cursor)*scale);
     }
     s.start(at,offset,len);sources.push(s);audioLog.push({id:e.key,tick:e.at,at,offset,duree:len});
   }
 }
 async function begin(){
   if(!active||playing||pending)return;
   const ticket=++version;pending=true;
   if(poster||ended)cursor=0;poster=false;ended=false;
   buttons();draw(cursor,true);
   let buffers=null,hasAudio=false,prepTimeout;
   try{
     const result=await Promise.race([Promise.all([ensureContext(),audioFor(rate)]),new Promise((_,reject)=>{prepTimeout=setTimeout(()=>reject(Error('Audio non autorisé')),1200);})]);
     buffers=result[1];hasAudio=ac.state==='running';
   }catch{}finally{clearTimeout(prepTimeout);}
   if(ticket!==version)return;
   pending=false;playing=true;
   text($('sound-hint'),!hasAudio?'Son indisponible · utiliser le MP4':muted?'Son coupé':'Son activé');
   clock={pos:cursor,at:(hasAudio?ac.currentTime:performance.now()/1000)+.035,rate,ac:hasAudio?ac:null};
   if(hasAudio)schedule(buffers);
   buttons();rafa();
 }
 function rafa(){
   if(!playing)return;
   const f=liveTick();
   if(f>=P.total){pause();cursor=P.total;ended=true;buttons();draw(cursor,true);return;}
   draw(f);raf=requestAnimationFrame(rafa);
 }
 function choose(p,position=0,start=false){
   pause();P=E.makePlan(D,part=p,route);cursor=position;poster=false;ended=false;
   initTimeline();draw(cursor,true);buttons();if(start)void begin();
 }
 function jump(t,play=false){
   pause();poster=false;ended=false;cursor=E.clip(Number(t),0,P.total-1);draw(cursor,true);buttons();if(play)void begin();
 }
 function showScreen(){
   const y=$('stage').getBoundingClientRect();
   if(y.bottom<=90||y.top>=window.innerHeight-85){$('stage').scrollIntoView({block:'center',behavior:'instant'});}
 }
 const replay=()=>choose(part,0,true);
 $('play-all').addEventListener('click',()=>{choose('film',0,true);showScreen();});
 $('toggle-play').addEventListener('click',()=>{if(playing||pending){pause();draw(cursor,true);}else void begin();});
 $('chapter-unlock').addEventListener('click',()=>{choose('deblocage',0,true);showScreen();});
 $('chapter-travel').addEventListener('click',()=>{choose('voyage',0,true);showScreen();});
 $('route').addEventListener('change',()=>{
   const prev=lastFrame?.part;
   route=$('route').value;
   if(poster){P=E.makePlan(D,part,route);initTimeline();draw(0,true);return;}
   const pos=Math.floor(playing?liveTick():cursor), was=playing||pending;
   if(prev==='voyage'){choose(part,part==='film'?D.deblocage.ticks:0,was);}
   else choose(part,pos,was);
 });
 $('jingle-now').addEventListener('click',()=>{choose('deblocage',D.deblocage.jingle,true);showScreen();});
 $('replay').addEventListener('click',replay);$('replay-stage').addEventListener('click',replay);
 $('seek').addEventListener('input',e=>jump(e.target.value));
 $('mute').addEventListener('click',()=>{muted=!muted;buttons();if(output)output.gain.setTargetAtTime(muted?0:.92,ac.currentTime,.012);text($('sound-hint'),muted?'Son coupé':ac&&ac.state==='running'?'Son activé':'Son au premier clic');});
 $('rate').addEventListener('click',()=>{const on=playing||pending;pause();rate=rate===1?.5:1;buttons();if(on)void begin();});
 for(const u of units)u.addEventListener('click',()=>{base=u.dataset.layer;buttons();draw(playing?liveTick():cursor,true);});
 $('view').addEventListener('click',()=>{view=view==='ds'?'entier':'ds';buttons();draw(playing?liveTick():cursor,true);});
 window.addEventListener('keydown',e=>{
   if(/^(?:BUTTON|INPUT|SELECT|TEXTAREA|SUMMARY|A)$/.test(e.target.tagName))return;
   if(e.code==='Space'){e.preventDefault();$('toggle-play').click();}
   if(e.code==='ArrowRight'||e.code==='ArrowLeft'){e.preventDefault();jump((poster?0:Math.floor(playing?liveTick():cursor))+(e.code==='ArrowRight'?1:-1));}
   if(e.key.toLowerCase()==='m')$('mute').click();
 });
 function image(a){return new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{imgs.set(a.fichier,im);resolve();};im.onerror=reject;im.src=a.uri;});}
 const allImages=[D.fond_nu,D.terrain,...Object.values(D.masques),...Object.values(D.reperes),...Object.values(D.brume_mobile),...Object.values(D.pikachu.poses)];
 for(const [id,a] of [['chapter-arrow',D.reperes['5']],['chapter-hero',D.pikachu.poses['0']],['pin-yellow',D.reperes['2']],['pin-yellow-alt',D.reperes['2']],['pin-red',D.reperes['4']]])$(id).src=a.uri;
 const ready=Promise.all(allImages.map(image)).then(()=>{active=true;$('play-all').disabled=false;$('toggle-play').disabled=false;initTimeline();draw(0,true);buttons();document.documentElement.dataset.ready='yes';}).catch(e=>{text($('sound-hint'),'Le lecteur n’a pas pu s’ouvrir. Utiliser le MP4.');throw e;});
 // Small read-only inspection surface for verification and frame capture.
 window.carteMiracle={ready,
   snapshot:()=>({t:playing?liveTick():cursor,playing,pending,poster,ended,base,view,part,route,rate,muted,frame:lastFrame,active,acState:ac?.state||null,log:audioLog.map(x=>({...x}))}),
   rms:()=>{
     if(!analyser)return 0;
     const x=new Float32Array(analyser.fftSize);analyser.getFloatTimeDomainData(x);return Math.sqrt(x.reduce((n,i)=>n+i*i,0)/x.length);
   }
 };
})();
