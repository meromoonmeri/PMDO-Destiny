(() => {
'use strict';
const $=id=>document.getElementById(id), D=JSON.parse($('atlas-data').textContent), W=D.width,H=D.height;
const scene=$('stage'), canvas=$('chart'), ctx=canvas.getContext('2d',{alpha:false}), options=$('destination'), by=Object.fromEntries(D.sites.map(s=>[s.id,s]));
const pages={}, pins={}, edges={}, reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const capture=new URLSearchParams(location.search).has('capture'), stateKey='destiny.carte-miracle.expedition.v1';
const speed={terre:59,mer:127,port:10}, phaseText={terre:'Sur le sentier',mer:'En traversée',port:'À l’embarcadère'};
const full={z:1,x:W/2,y:H/2}; const clamp=(n,a,b)=>Math.max(a,Math.min(b,n)), mix=(a,b,t)=>a+(b-a)*t;
const veil=D.nuages, zones=veil.zones, zoned=Object.keys(zones);
const banks=Object.fromEntries(zoned.map(id=>[id,zones[id].bancs.map(([cx,cy,w,pose,dx,dy])=>{
 const [u,v]=veil.poses[pose],h=Math.round(w*v/u);return {art:'cloud'+pose,x:cx-w/2,y:cy-h/2,w,h,dx,dy};
})]));
const coords=(x,y)=>[Math.round(x*100)/100,Math.round(y*100)/100];
let ready=false, art={}, dat=readState(), found=new Set(dat.found), current=dat.current, selected=current==='reverie'?'fosse':current;
let cloudsOn=true, opened=areasFrom(found);
let pose=by[current].point.slice(), route=null, preview=null, phase='idle', movement='terre', elapsed=0, reveal=null, toastLeft=0;
let camera={...full}, goal={...full}, follow=true, routes=true, paused=false, audioOn=false, rate=1, trail=0, ticks=0, queue=[], events=[];
let dims={w:1,h:1,dpr:1}, direction=0, last=0, frameHandle=0, touch=new Map(), grip=null, wasPan=false, suppressClick=0;
const unlock=new Audio(D.son);unlock.preload='auto';unlock.volume=.67;
function readState(){
 try{const s=JSON.parse(localStorage.getItem(stateKey)||'null');if(s&&s.version===1&&by[s.current]&&Array.isArray(s.found))return {current:s.current,found:[...new Set(['reverie',s.current,...s.found.filter(k=>by[k])])]};}catch{}
 return {current:'reverie',found:['reverie']};
}
function areasFrom(discovered){return new Set([...discovered].map(id=>by[id].area).filter(area=>zones[area]));}
function opening(){return cloudsOn&&!reduced&&phase==='reveal'&&reveal?.zone&&reveal.clock<veil.duree?reveal.zone:null;}
function setClouds(on){cloudsOn=on;if(ready){updateUI();render(0);}}
function save(){try{localStorage.setItem(stateKey,JSON.stringify({version:1,current,found:[...found]}));}catch{}}
function announce(type,id,extra={}){events.push({type,id,...extra});if(events.length>120)events.shift();}
function attr(e,n,v){const s=String(v);if(e.getAttribute(n)!==s)e.setAttribute(n,s);}
function text(e,v){v=String(v);if(e.textContent!==v)e.textContent=v;}
function press(id,on){attr($(id),'aria-pressed',on);}
function nodeImage(uri){return new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=reject;img.src=uri;});}
function dist(a,b){return Math.hypot(b[0]-a[0],b[1]-a[1]);}
for(const e of D.edges){(edges[e.a]??=[]).push({to:e.b,e,reverse:false});(edges[e.b]??=[]).push({to:e.a,e,reverse:true});}
function path(start,end){
 if(start===end)return null;
 const used=new Set(), cost={[start]:0}, incoming={};
 for(;;){
  let u=null,lo=Infinity;for(const k of Object.keys(cost))if(!used.has(k)&&cost[k]<lo){u=k;lo=cost[k];}
  if(u===null)return null;if(u===end)break;used.add(u);
  for(const p of edges[u]||[]){const t=p.e.distance/speed[p.e.mode]+(p.e.mode==='port'?.34:0);
    if(lo+t<(cost[p.to]??Infinity)){cost[p.to]=lo+t;incoming[p.to]={...p,prev:u};}}
 }
 let k=end, chain=[];while(k!==start){const m=incoming[k];chain.push(m);k=m.prev;}chain.reverse();
 const legs=[],bits=[];let total=0,sea=0;
 for(const {e,reverse} of chain){
  const p=reverse?e.p.slice().reverse():e.p;
  if(p.length<2)continue;
  legs.push({p,mode:e.mode});if(e.mode==='mer')sea+=e.distance;
  for(let i=1;i<p.length;i++){const t=dist(p[i-1],p[i])/speed[e.mode];if(t<.0001)continue;bits.push({p:p[i-1],q:p[i],a:total,b:total+t,mode:e.mode});total+=t;}
 }
 if(!bits.length){bits.push({p:by[start].point,q:by[end].point,a:0,b:.42,mode:'terre'});total=.42;}
 return {end,start,legs,bits,total,sea};
}
function setup(){
 for(const [id,name] of Object.entries(D.regions)){const group=document.createElement('optgroup');group.label=name;pages[id]=group;options.append(group);}
 for(const s of D.sites){const opt=document.createElement('option');opt.value=s.id;opt.textContent=s.name;pages[s.area].append(opt);
  const b=document.createElement('button');b.className='pin';b.type='button';b.id=`repere-${s.id}`;b.dataset.site=s.id;b.title=s.name;
  const label=document.createElement('span');label.className='p-name';label.textContent=s.name;b.append(label);b.addEventListener('click',()=>{if(performance.now()<suppressClick)return;select(s.id);});$('pins').append(b);pins[s.id]=b;
 }
 $('discTrack').setAttribute('aria-valuemax',D.sites.length);
}
function updateUI(){
 const busy=phase!=='idle', site=by[selected], minSel=ready&&!busy;
 options.value=selected;options.disabled=!minSel;
 for(const s of D.sites){attr(pins[s.id],'aria-label',s.name+(found.has(s.id)?' — débloqué':' — à découvrir'));attr(pins[s.id],'aria-pressed',s.id===selected);pins[s.id].disabled=busy;}
 for(const o of options.options){text(o,`${found.has(o.value)?'●':'○'}  ${by[o.value].name}`);}
 text($('where'),by[current].name);text($('discoverCount'),`${found.size} / ${D.sites.length}`);
 const remaining=zoned.length-opened.size, summary=remaining?`${remaining} ${remaining===1?'zone voilée':'zones voilées'}`:'Toutes les zones sont dévoilées';
 text($('veilCount'),cloudsOn?summary:'Nuages masqués');text($('veilEdition'),summary);
 const chip=$('siteVeil'), siteOpen=opened.has(site.area);chip.hidden=!zones[site.area];
 text(chip,siteOpen?'Dévoilée':'Voilée');chip.classList.toggle('open',siteOpen);
 attr($('circuitNuages'),'title',remaining?'Un voyage vers chaque zone encore voilée.':'Recommence l’expédition pour revoir les ouvertures.');
 text($('circuitVeilCount'),remaining?`${remaining} ${remaining===1?'zone':'zones'}`:'Tout dévoilé');
 $('discTrack').firstElementChild.style.width=100*found.size/D.sites.length+'%';attr($('discTrack'),'aria-valuenow',found.size);
 text($('siteKind'),site.category);text($('siteArea'),site.region);text($('siteTitle'),site.name);text($('siteText'),site.text);
 const ref=site.origine==='eos'?'Lieu d’Explorateurs du Ciel · adaptation Destiny':site.new?'Île originale Destiny':site.lore?'Lieu du projet':'Lieu proposé';text($('siteCaption'),`${found.has(selected)?'Débloqué':'À découvrir'} · ${ref}`);
 $('depart').disabled=!minSel||current===selected||!preview;
 text($('depart').querySelector('span'),current===selected?'Tu es à ce repère':busy?'Expédition en cours':'Partir vers ce repère');
 $('circuitRive').disabled=!minSel;$('circuitMer').disabled=!minSel;$('circuitArchipels').disabled=!minSel;$('circuitNuages').disabled=!minSel||!remaining;$('pause').disabled=!busy;text($('pause').querySelector('span'),paused?'Reprendre':'Pause');
 $('pause').querySelector('use').setAttribute('href',paused?'#i-play':'#i-pause');
 press('sound',audioOn);press('follow',follow);press('routes',routes);press('clouds',cloudsOn);
 const tag=$('placeTag');tag.hidden=phase==='idle'||!route;
 if(route)text(tag.lastElementChild,by[route.end].name);
 updateProgress();
}
function updateProgress(){
 const pct=phase==='travel'&&route?Math.min(99,Math.round(100*elapsed/route.total)):reveal?100:0;
 const status=paused?'Simulation en pause':phase==='travel'?phaseText[movement]:phase==='reveal'?(reveal.fresh?'Découverte !':'Arrivée'):reveal?(reveal.fresh?'Repère débloqué':'Étape atteinte'):(preview?.sea>0?'À pied puis en bateau':'Prêt au départ');
 text($('journeyPercent'),pct+' %');text($('travelStatus'),status);$('travelTrack').firstElementChild.style.width=pct+'%';attr($('travelTrack'),'aria-valuenow',pct);
 const clearing=opening(), zoneNotice=$('arrival-zone');
 if(reveal?.zone)text(zoneNotice,(clearing?'Les nuages s’écartent · ':'Zone dévoilée · ')+D.regions[reveal.zone]);
 const tag=$('modeTag'), label=phase==='travel'?(movement==='mer'?'TRAVERSÉE EN MER':movement==='port'?'EMBARCADÈRE':'MARCHE EN COURS'):clearing?'LES NUAGES SE LÈVENT':phase==='reveal'?'DÉCOUVERTE':'CARTE DU MONDE';
 if(tag.textContent.trim()!==label)tag.replaceChildren(document.createElement('span'),document.createTextNode(label));tag.classList.toggle('boat',phase==='travel'&&movement==='mer');
}
function select(id){if(!ready||phase!=='idle'||!by[id])return;selected=id;preview=path(current,id);hideArrival();reveal=null;updateUI();}
function hideArrival(){toastLeft=0;$('arrival').hidden=true;}
function bringMapIntoView(){
 if(!capture&&matchMedia('(max-width:795px)').matches&&scene.getBoundingClientRect().top<0)scene.scrollIntoView({block:'start',behavior:reduced?'auto':'smooth'});
}
function begin(id, scripted=false){
 if(!ready||phase!=='idle'||!by[id])return false;
 if(!scripted)queue=[];if(id===current)return false;
 route=path(current,id);if(!route)return false;
 selected=id;preview=route;elapsed=0;trail=0;movement=route.bits[0].mode;phase='travel';paused=false;reveal=null;hideArrival();
 if(follow){const s=by[current].island, same=s!==0&&s===by[id].island;goal={x:pose[0],y:pose[1],z:same?1.78:1.25};}
 announce('depart',id,{from:current,segments:route.legs.length});updateUI();
 if(!scripted)bringMapIntoView();
 return true;
}
function next(){while(queue.length){const k=queue.shift();if(begin(k,true))return;}queue=[];}
function circuit(id){
 if(!ready||phase!=='idle')return;
 if(id==='nuages'){
  if(opened.size===zoned.length)return;
  setClouds(true);queue=D.circuits.nuages.filter(k=>!opened.has(by[k].area));
 }else queue=[...D.circuits[id]];
 next();bringMapIntoView();
}
function appear(){
 const id=route.end, site=by[id];pose=site.point.slice();const newly=!found.has(id);
 const zone=zones[site.area]&&!opened.has(site.area)?site.area:null;
 if(zone)opened.add(zone);
 current=id;found.add(id);save();reveal={id,fresh:newly,clock:0,zone};phase='reveal';paused=false;
 announce('arrive',id);if(newly){announce('deblocage',id);if(audioOn){unlock.currentTime=0;unlock.play().catch(()=>{});}}
 if(zone)announce('ouverture-zone',zone,{site:id});
 text($('arrival-kind'),newly?'REPÈRE DÉBLOQUÉ !':'ÉTAPE ATTEINTE');text($('arrival-name'),site.name);
 $('arrival-zone').hidden=!zone;$('arrival').hidden=false;toastLeft=4.1;
 if(follow){
  const focus=zone&&cloudsOn?zones[zone].vue:[pose[0],pose[1],site.new?2.44:site.island===18?2.22:1.74];
  goal={x:focus[0],y:focus[1],z:focus[2]};
 }
 updateUI();
}
function stopReveal(){phase='idle';paused=false;route=null;preview=path(current,selected);updateUI();if(queue.length)next();}
function pause(){if(phase==='idle')return;paused=!paused;updateUI();}
function reset(){
 current='reverie';selected='fosse';pose=by[current].point.slice();found=new Set([current]);opened=areasFrom(found);route=null;preview=path(current,selected);reveal=null;
 queue=[];events=[];phase='idle';paused=false;elapsed=0;trail=0;follow=true;movement='terre';camera={...full};goal={...full};hideArrival();save();updateUI();
}
function orient(dx,dy){const x=Math.abs(dx),y=Math.abs(dy);if(y>x*2)return dy<0?4:0;if(x>y*2)return dx<0?6:2;return dx<0?(dy<0?5:7):(dy<0?3:1);}
function frameTravel(dt){
 elapsed=Math.min(route.total,elapsed+dt*rate);trail+=dt;
 if(elapsed>=route.total-1e-7){appear();return;}
 const s=route.bits.find(x=>x.b>elapsed)||route.bits.at(-1), a=clamp((elapsed-s.a)/(s.b-s.a),0,1);
 pose=[mix(s.p[0],s.q[0],a),mix(s.p[1],s.q[1],a)];direction=orient(s.q[0]-s.p[0],s.q[1]-s.p[1]);
 if(movement!==s.mode){movement=s.mode;announce('transport',route.end,{mode:movement});}
 if(follow){goal.x=pose[0];goal.y=pose[1];const local=by[current].island!==0&&by[current].island===by[route.end].island;goal.z=local?1.87:(movement==='mer'?1.16:1.43);}
 updateProgress();
}
function constrain(v){const hw=W/(2*v.z),hh=H/(2*v.z);v.x=clamp(v.x,hw,W-hw);v.y=clamp(v.y,hh,H-hh);return v;}
function changeFollow(on){follow=on;press('follow',follow);if(on){goal.x=pose[0];goal.y=pose[1];if(phase==='idle')goal.z=Math.max(goal.z,1.74);}}
function world(){goal={...full};changeFollow(false);render(0);}
function screen(){const k=Math.min(dims.w/W,dims.h/H)*camera.z;return {k,x:dims.w/2-camera.x*k,y:dims.h/2-camera.y*k};}
function relative(ev){const a=scene.getBoundingClientRect();return [ev.clientX-a.left-scene.clientLeft,ev.clientY-a.top-scene.clientTop];}
function zoom(to,at,immediate=false){
 const from=screen(),q=at||[dims.w/2,dims.h/2];const p=[(q[0]-from.x)/from.k,(q[1]-from.y)/from.k];const z=clamp(to,1,4);
 const k=Math.min(dims.w/W,dims.h/H)*z;goal=constrain({x:p[0]-(q[0]-dims.w/2)/k,y:p[1]-(q[1]-dims.h/2)/k,z});changeFollow(false);
 if(immediate)camera={...goal};
}
function resize(){
 const w=scene.clientWidth,h=scene.clientHeight;if(w<2||h<2)return;const dpr=Math.min(2,window.devicePixelRatio||1);
 if(w!==dims.w||h!==dims.h||dpr!==dims.dpr){dims={w,h,dpr};canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}
}
function drawImg(k,x,y,w,h,a=1){const im=art[k];if(!im)return;ctx.globalAlpha=a;ctx.drawImage(im,Math.round(x),Math.round(y),Math.round(w),Math.round(h));ctx.globalAlpha=1;}
// Only the reversible cloud overlay moves at a first regional arrival. No terrain texture is changed.
function drawClouds(){
 if(!cloudsOn)return;
 const animated=opening();
 const drawBank=(id,off,alpha)=>{for(const b of banks[id])drawImg(b.art,b.x+b.dx*off,b.y+b.dy*off,b.w,b.h,alpha);};
 for(const id of zoned){if(!opened.has(id))drawBank(id,0,veil.opacite);}
 if(animated){
  const u=clamp(reveal.clock/veil.duree,0,1),ease=x=>x*x*(3-2*x);
  const fade=1-ease(clamp((u-.20)/.80,0,1));
  drawBank(animated,ease(u),veil.opacite*fade);
 }
}
function decal(k){const d=D.glyphs[k];drawImg(k,d.x,d.y,d.w,d.h);}
function drawRoute(){
 const rd=route||preview;if(!routes||!rd)return;const p=phase==='travel'||phase==='reveal';
 for(const g of rd.legs){if(g.p.length<2)continue;
  ctx.beginPath();for(let i=0;i<g.p.length;i++){const [x,y]=g.p[i];if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}
  ctx.lineCap='round';ctx.lineJoin='round';const boat=g.mode==='mer';
  ctx.setLineDash(boat?[8,6]:[3,5]);ctx.lineDashOffset=0;
  ctx.lineWidth=boat?2.9:2.4;ctx.strokeStyle=boat?(p?'#2e6763':'#32645e99'):(p?'#6e4728':'#785132aa');ctx.stroke();
  ctx.lineDashOffset-=1;ctx.lineWidth=1;ctx.strokeStyle=p?(boat?'#bddabb':'#ffe9a7'):'#f3d38a99';ctx.stroke();
 }
 ctx.setLineDash([]);ctx.lineDashOffset=0;
}
function pixelDisc(x,y,rx,ry,color){ctx.fillStyle=color;ctx.beginPath();ctx.ellipse(Math.round(x),Math.round(y),rx,ry,0,0,2*Math.PI);ctx.fill();}
function player(){
 const [x,y]=pose,moving=phase==='travel', sailing=moving&&(movement==='mer'||movement==='port');
 const bob=sailing&&!reduced?Math.sin(trail*6.4)*1.8:0;
 pixelDisc(x,y+1,9,3,'#51381d45');
 if(sailing){
  const r=trail*2.7%1;ctx.strokeStyle='#335955';ctx.globalAlpha=.37;ctx.lineWidth=1.2;ctx.beginPath();ctx.ellipse(x,y+2,9+r*6,3+r*3,0,0,Math.PI*2);ctx.stroke();ctx.globalAlpha=1;
  const b=art.barque;
  drawImg('barque',x-b.width/2,y-b.height/2+bob,b.width,b.height);
 }
 const seq=D.walk[direction];let k=seq[0].pose;
 if(moving&&!sailing&&!reduced){let f=Math.floor(trail*59.8261*Math.min(rate,2))%36;for(const a of seq){if(f<a.ticks){k=a.pose;break;}f-=a.ticks;}}
 const im=D.poses[k], z=1.52;drawImg('p'+k,x+im.offset[0]*z,y+im.offset[1]*z+bob,im.size[0]*z,im.size[1]*z);
}
function render(dt){
 if(!ready)return;resize();
 const t=reduced?1:1-Math.exp(-Math.max(.0,dt)*6.9);
 for(const k of ['x','y','z'])camera[k]=mix(camera[k],goal[k],t);
 constrain(camera);const {k,x,y}=screen(), dr=dims.dpr;
 ctx.setTransform(dr,0,0,dr,0,0);ctx.fillStyle='#ecb676';ctx.fillRect(0,0,dims.w,dims.h);
 ctx.setTransform(k*dr,0,0,k*dr,x*dr,y*dr);ctx.imageSmoothingEnabled=false;
 drawImg('fond',0,0,W,H);drawImg('terrain',0,0,W,H);drawImg('archipels',0,0,W,H);
 decal('fosse');decal('houle');decal('spirale');
 drawClouds();drawRoute();
 for(const s of D.sites){
  const [px,py]=s.loc, on=found.has(s.id), chosen=s.id===selected, pin=pins[s.id], xx=px*k+x, yy=py*k+y;
  const shown=xx>6&&yy>6&&xx<dims.w-6&&yy<dims.h-6;pin.hidden=!shown;if(!shown)continue;
  pin.style.left=xx.toFixed(2)+'px';pin.style.top=yy.toFixed(2)+'px';pin.classList.toggle('left',xx>dims.w*.78);
  const mark=on?'red':chosen?'yellow':'dim';
  if(chosen){
   ctx.strokeStyle=on?'#ffedbbad':'#fff2aed8';ctx.lineWidth=1.55;ctx.beginPath();ctx.arc(px,py,11,0,Math.PI*2);ctx.stroke();
  }
  const scale=on||chosen?1.92:1.42;drawImg(mark,px-4*scale,py-4*scale,8*scale,8*scale,on||chosen?1:.77);
  if(chosen&&!on&&phase==='travel')drawImg('arrowA',px+5,py-23,14,16,.98);
 }
 player();
 const scale=Math.round(camera.z*100);text($('zoomVal'),scale+' %');$('minus').disabled=goal.z<=1.001;$('plus').disabled=goal.z>=3.999;
}
function stepFrame(dt){
 if(!ready)return;dt=clamp(dt,0,.08);if(!paused){ticks+=dt;
  if(phase==='travel')frameTravel(dt);
  else if(phase==='reveal'&&reveal){
   const showing=opening();reveal.clock+=dt;
   if(showing&&!opening())updateProgress();
   if(reveal.clock>=1.63)stopReveal();
  }
  if(toastLeft>0){toastLeft-=dt;if(toastLeft<=0&&phase!=='reveal')hideArrival();}
 }
 render(dt);
}
function animate(t){if(!last)last=t;const dt=(t-last)/1000;last=t;stepFrame(dt);frameHandle=requestAnimationFrame(animate);}
function snapshot(){return {ready,phase,current,selected,found:Array.from(found),total:D.sites.length,pos:coords(...pose),transport:movement,paused,rate,
  camera:{z:camera.z,x:camera.x,y:camera.y},targetCamera:{...goal},follow,routes,sound:audioOn,elapsed,totalTime:route?.total??0,sequence:queue.slice(),
  clouds:cloudsOn,openedZones:[...opened],totalZones:zoned.length,opening:opening()?{zone:reveal.zone,progress:clamp(reveal.clock/veil.duree,0,1)}:null,
  revealed:reveal?.id??null,toast:!$('arrival').hidden,visibles:Object.values(pins).filter(b=>!b.hidden).length,events:events.slice(),clock:ticks};}
window.carteMiracle={snapshot};
if(capture){window.carteMiracle.advance=ms=>{let left=clamp(Number(ms)||0,0,60000)/1000;while(left>1e-6){const t=Math.min(.033333,left);stepFrame(t);left-=t;}return snapshot();};}

options.addEventListener('change',()=>select(options.value));$('depart').addEventListener('click',()=>begin(selected));
$('circuitRive').addEventListener('click',()=>circuit('rive'));$('circuitMer').addEventListener('click',()=>circuit('marees'));$('circuitArchipels').addEventListener('click',()=>circuit('archipels'));$('circuitNuages').addEventListener('click',()=>circuit('nuages'));$('pause').addEventListener('click',pause);$('reset').addEventListener('click',reset);
$('speed').addEventListener('change',e=>rate=Number(e.target.value)||1);
$('sound').addEventListener('click',()=>{audioOn=!audioOn;press('sound',audioOn);if(audioOn){unlock.currentTime=0;unlock.play().catch(()=>{});}else unlock.pause();});
$('follow').addEventListener('click',()=>changeFollow(!follow));$('routes').addEventListener('click',()=>{routes=!routes;press('routes',routes);render(0);});
$('clouds').addEventListener('click',()=>setClouds(!cloudsOn));$('world').addEventListener('click',world);$('plus').addEventListener('click',()=>zoom(goal.z*1.31));$('minus').addEventListener('click',()=>zoom(goal.z/1.31));
scene.addEventListener('wheel',e=>{if(!ready)return;e.preventDefault();zoom(camera.z*Math.exp(clamp(-e.deltaY,-180,180)*.00235),relative(e),true);render(0);},{passive:false});
function gripSet(){
 if(touch.size===0){grip=null;scene.classList.remove('dragging');return;}
 const a=[...touch.values()];
 if(a.length>=2){const x=(a[0][0]+a[1][0])/2,y=(a[0][1]+a[1][1])/2;const v=screen();grip={f:2,d:dist(a[0],a[1]),z:camera.z,p:[(x-v.x)/v.k,(y-v.y)/v.k]};}
 else grip={f:1,p:a[0],x:camera.x,y:camera.y,k:screen().k};
}
scene.addEventListener('pointerdown',e=>{
 const pin=e.target.closest('button');
 if(!ready||e.button>0||(pin&&e.pointerType!=='touch'))return;
 if(touch.size===0)wasPan=false;touch.set(e.pointerId,relative(e));
 // Touch capture on a pin is implicit. Its events bubble so a pinch can begin on a pin,
 // without moving capture to the stage and preventing an ordinary tap from selecting it.
 if(!pin)scene.setPointerCapture(e.pointerId);gripSet();
});
scene.addEventListener('pointermove',e=>{
 if(!touch.has(e.pointerId)||!grip)return;touch.set(e.pointerId,relative(e));const a=[...touch.values()];
 if(grip.f===1&&dist(a[0],grip.p)>3){wasPan=true;scene.classList.add('dragging');changeFollow(false);goal=constrain({x:grip.x-(a[0][0]-grip.p[0])/grip.k,y:grip.y-(a[0][1]-grip.p[1])/grip.k,z:camera.z});}
 else if(grip.f===2&&a.length>=2){wasPan=true;changeFollow(false);const nz=clamp(grip.z*dist(a[0],a[1])/Math.max(1,grip.d),1,4),x=(a[0][0]+a[1][0])/2,y=(a[0][1]+a[1][1])/2,k=Math.min(dims.w/W,dims.h/H)*nz;goal=constrain({z:nz,x:grip.p[0]-(x-dims.w/2)/k,y:grip.p[1]-(y-dims.h/2)/k});}
 else return;camera={...goal};render(0);
});
function release(e){if(!touch.delete(e.pointerId))return;if(wasPan)suppressClick=performance.now()+200;gripSet();}
scene.addEventListener('pointerup',release);scene.addEventListener('pointercancel',release);scene.addEventListener('lostpointercapture',release);
scene.addEventListener('keydown',e=>{
 if(e.target!==scene)return;
 if(e.key==='+'||e.key==='='){e.preventDefault();zoom(goal.z*1.31);}
 else if(e.key==='-'){e.preventDefault();zoom(goal.z/1.31);}
 else if(e.key==='0'){e.preventDefault();world();}
 else if(e.key===' '&&phase!=='idle'){e.preventDefault();pause();}
 else if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();changeFollow(false);const d=45/Math.sqrt(goal.z);goal=constrain({z:goal.z,x:goal.x+(e.key==='ArrowLeft'?-d:e.key==='ArrowRight'?d:0),y:goal.y+(e.key==='ArrowUp'?-d:e.key==='ArrowDown'?d:0)});}
});
new ResizeObserver(()=>render(0)).observe(scene);
Promise.all(Object.entries(D.images).map(async ([k,v])=>[k,await nodeImage(v)])).then(rows=>{
 art=Object.fromEntries(rows);setup();preview=path(current,selected);ready=true;$('loading').hidden=true;updateUI();render(0);
 if(!capture)frameHandle=requestAnimationFrame(animate);
}).catch(err=>{text($('loading'),'Impossible de charger le calque de la carte.');console.error(err);});
})();
