'use strict';
(() => {
const $=id=>document.getElementById(id), cv=$('map'), cx=cv.getContext('2d',{alpha:false}), stage=$('viewport');
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
const smooth=(a,b,v)=>{const u=clamp((v-a)/(b-a),0,1);return u*u*(3-2*u);};
const lerp=(a,b,t)=>a+(b-a)*t;
const normalize=s=>String(s).toLowerCase().normalize('NFD').replace(/\p{Mark}/gu,'').replace(/[^a-z0-9]/g,' ').trim();
const el=(tag,cl,text)=>{const x=document.createElement(tag);if(cl)x.className=cl;if(text!==undefined)x.textContent=text;return x;};
const img=url=>new Promise((ok,no)=>{const i=new Image();i.decoding='async';i.onload=()=>ok(i);i.onerror=()=>no(Error('Image indisponible : '+url));i.src=url;});
const load=async()=>{
 const embedded=window.atlasLocal;
 const manifest=embedded?Promise.resolve(embedded.index):fetch('assets/Lieux.json').then(r=>{if(!r.ok)throw Error('Index indisponible');return r.json();});
 const asset=name=>img(embedded?embedded.files[name]:'assets/'+name);
 const [d,world,terrain,sprites,anim,fog]=await Promise.all([manifest,embedded?Promise.resolve(null):asset('Monde-150.png'),asset('Terrain.png'),asset('Lieux-150.png'),asset('Animations.png'),asset('Nuages.png')]);
 if(embedded)delete window.atlasLocal;
 if(d.nb!==150||d.lieux.length!==d.nb)throw Error('Index incomplet');
 if(!world){
   const paper=document.createElement('canvas');[paper.width,paper.height]=d.taille;
   const pc=paper.getContext('2d',{alpha:false});pc.imageSmoothingEnabled=false;pc.drawImage(terrain,0,0);
   for(const p of [...d.lieux].sort((a,b)=>a.ancre[1]-b.ancre[1])){const [x,y,w,h]=p.sprite;pc.drawImage(sprites,x,y,w,h,p.rect[0],p.rect[1],w,h);}
   const png=$('map-png');png.href='#';png.download='Monde-Destiny-150-Lieux.png';png.onclick=()=>{if(!png.href.startsWith('data:'))png.href=paper.toDataURL('image/png');};
   setup(d,{world:paper,terrain,sprites,anim,fog});
 }else setup(d,{world,terrain,sprites,anim,fog});
};
load().catch(e=>{const l=$('loading');l.replaceChildren(el('span',null,'Le carnet ne s’est pas chargé. Recharge l’aperçu.'));console.error(e);});

function setup(d,assets){
const [mw,mh]=d.taille,[sx,sy]=d.depart.centre,b0=d.depart.cadre,pitch=d.grille_atlas;
const start= d.lieux.filter(o=>o.premiere_zone), all = [...start,...d.lieux.filter(o=>!o.premiere_zone).sort((a,b)=>a.nom.localeCompare(b.nom,'fr'))], by=new Map(all.map(p=>[p.id,p]));
const searchIndex=new Map(all.map(p=>[p.id,normalize([p.nom,p.original,p.jeu,d.regions[p.region],d.types[p.type]].join(' '))]));
const moving=all.filter(p=>Number.isInteger(p.animation));
const mobile=matchMedia('(max-width: 770px)');const scrollBehavior=reduced?'instant':'smooth';
const state={w:0,h:0,dpr:1,fit:.5,cam:{x:mw/2,y:mh/2,s:.5},mode:'monde',fog:0,tween:null,reveal:null,selected:null,hover:null,pins:false,dirty:true,phase:-1,first:true};
let listed=all;const buttons=new Map();const touch=new Map();let gest=null;
const fcv=document.createElement('canvas');fcv.width=mw;fcv.height=mh;const fc=fcv.getContext('2d');let made=-1;
const fullCam=()=>({x:mw/2,y:mh/2,s:state.fit});
const startCam=()=>({x:(b0[0]+b0[2])/2,y:(b0[1]+b0[3])/2,s:Math.min(state.w/(b0[2]-b0[0]),state.h/(b0[3]-b0[1]))*.98});
const anchor=p=>[(p.rect[0]+p.rect[2])/2,(p.rect[1]+p.rect[3])/2];
const pressed=(n,v)=>$(n).setAttribute('aria-pressed',String(!!v));
function dirty(){state.dirty=true;}
function cap(a){const l=state.w/(2*a.s),t=state.h/(2*a.s),g=36/a.s;a.x=l>mw/2?mw/2:clamp(a.x,l-g,mw-l+g);a.y=t>mh/2?mh/2:clamp(a.y,t-g,mh-t+g);return a;}
function modeInfo(){
 pressed('world',state.mode==='monde');pressed('start',state.mode==='depart');pressed('reveal',state.mode==='reveal');
 const v=state.reveal;const title=v?(v.paused?'▷ Reprendre':'Ⅱ Pause'):'▷ Dévoiler';$('reveal').textContent=title;
 $('chart-h').textContent=state.mode==='depart'?'DÉPART / 5 LIEUX':state.mode==='reveal'?'DÉVOILEMENT / PARCHEMIN':'PARCHEMIN / SANS TEXTE';
 cv.dataset.mode=state.mode;
}
function transition(cam,ms=560){cam=cap({...cam});state.tween=null;if(reduced||!ms){state.cam=cam;dirty();return;}state.tween={from:{...state.cam},to:cam,t:performance.now(),ms};dirty();}
function setMode(m){state.mode=m;state.reveal=null;state.tween=null;state.fog=m==='depart'?102:0;state.hover=null;modeInfo();dirty();}
function moveMode(m){setMode(m);transition(m==='depart'?startCam():fullCam());}
function putSize(){const b=stage.getBoundingClientRect();if(b.width<20||b.height<20)return;const old=state.fit;
 state.w=b.width;state.h=b.height;state.dpr=Math.min(2,window.devicePixelRatio||1);
 const w=Math.round(state.w*state.dpr),h=Math.round(state.h*state.dpr);if(cv.width!==w||cv.height!==h){cv.width=w;cv.height=h;}
 state.fit=Math.min((state.w-18)/mw,(state.h-16)/mh);if(state.first||Math.abs(state.cam.s-old)<.02&&state.mode==='monde')state.cam=fullCam();else if(state.mode==='depart'&&!state.selected)state.cam=startCam();else state.cam=cap(state.cam);
 state.first=false;dirty();
}
function thumbs(c,p){const g=c.getContext('2d'),[x,y,w,h]=p.sprite;g.clearRect(0,0,c.width,c.height);const s=Math.min((c.width-4)/w,(c.height-4)/h,3);
 g.imageSmoothingEnabled=false;g.drawImage(assets.sprites,x,y,w,h,Math.round((c.width-w*s)/2),Math.round((c.height-h*s)/2),Math.round(w*s),Math.round(h*s));
}
function tileRow(p){
 let b=buttons.get(p.id);if(b)return b;
 b=el('button','site');b.type='button';b.dataset.lieu=p.id;b.setAttribute('aria-pressed','false');b.setAttribute('aria-label',p.nom+' — '+d.regions[p.region]);const c=el('canvas');c.width=70;c.height=53;c.setAttribute('aria-hidden','true');thumbs(c,p);
 const labels=el('span');labels.append(el('strong',null,p.nom),el('small',null,d.regions[p.region]));b.append(c,labels,el('i',null,'›'));
 b.addEventListener('click',()=>{show(p,true);goMap();});b.addEventListener('pointerenter',()=>{state.hover=p.id;dirty();});b.addEventListener('pointerleave',()=>{state.hover=null;dirty();});buttons.set(p.id,b);return b;
}
function list(){const q=normalize($('search').value).split(/\s+/).filter(Boolean),r=$('region').value,t=$('type').value;
 listed=all.filter(p=>(!r||p.region===r)&&(!t||p.type===t)&&q.every(w=>searchIndex.get(p.id).includes(w)));
 const a=document.createDocumentFragment();for(const p of listed){const b=tileRow(p);b.setAttribute('aria-pressed',String(p.id===state.selected));a.append(b);}
 if(!listed.length)a.append(el('p','empty','Aucun lieu ne correspond. Essaie un autre nom ou efface les filtres.'));
 $('result').replaceChildren(a);$('count').textContent=`${listed.length} / ${d.nb} ${listed.length===1?'lieu':'lieux'}`;$('clear').hidden=!(q.length||r||t);dirty();
}
function href(id){try{history.replaceState(null,'',id?'#'+encodeURIComponent(id):location.pathname+location.search);}catch{}}
function goMap(){if(mobile.matches)document.querySelector('.chart').scrollIntoView({behavior:scrollBehavior,block:'start'});}
function show(p,zoom){
 if(!p)return;const before=state.selected;state.selected=p.id;state.hover=null;
 if((!p.premiere_zone&&state.mode!=='monde')||state.mode==='reveal')setMode('monde');
 $('detail').hidden=false;$('picked').hidden=false;$('picked').textContent=p.nom+' · Fiche ↓';thumbs($('tile'),p);$('detail-name').textContent=p.nom;$('detail-region').textContent=d.regions[p.region];
 $('detail-copy').textContent=p.note||p.info;$('source').hidden=!(p.lien&&/^https:\/\//.test(p.lien));if(!$('source').hidden)$('source').href=p.lien;
 if(before)buttons.get(before)?.setAttribute('aria-pressed','false');buttons.get(p.id)?.setAttribute('aria-pressed','true');href(p.id);
 if(zoom){const [x,y]=anchor(p),s=clamp(Math.min(state.w/215,state.h/155),Math.max(state.fit*1.8,1.5),5.8);transition({x,y,s});}
 cv.dataset.lieu=p.id;dirty();
}
function close(){if(state.selected)buttons.get(state.selected)?.setAttribute('aria-pressed','false');state.selected=null;delete cv.dataset.lieu;$('detail').hidden=true;$('picked').hidden=true;href(null);dirty();}
function progress(t){const v=state.reveal;if(!v)return;const dt=v.paused?v.elapsed:t-v.begin;const c=startCam(),w=fullCam();
 const u=smooth(4800,16800,dt),re=dt<4800?lerp(28,105,smooth(380,4200,dt)):lerp(105,1630,smooth(4800,16600,dt));
 state.fog=re;state.cam=cap({x:lerp(c.x,w.x,u),y:lerp(c.y,w.y,u),s:Math.exp(lerp(Math.log(c.s),Math.log(w.s),u))});
 if(dt>=16800){setMode('monde');state.cam=fullCam();}
}
function reveal(){
 if(reduced){moveMode(state.mode==='depart'?'monde':'depart');return;}
 if(state.reveal){const a=state.reveal;a.paused=!a.paused;if(a.paused)a.elapsed=performance.now()-a.begin;else a.begin=performance.now()-a.elapsed;modeInfo();dirty();return;}
 close();setMode('reveal');state.reveal={begin:performance.now(),elapsed:0,paused:false};state.fog=28;state.cam=startCam();modeInfo();dirty();
}
function fogLayer(r){if(r>=1580||r<=0)return false;const k=Math.round(r/4)*4;if(k===made)return true;made=k;fc.clearRect(0,0,mw,mh);fc.drawImage(assets.fog,0,0);fc.globalCompositeOperation='destination-out';
 function opening(extra,alpha){fc.globalAlpha=alpha;fc.beginPath();for(let i=0;i<=180;i++){
   const t=i*2*Math.PI/180,j=r+extra+6.8*Math.sin(t*11+.55)+4.9*Math.sin(t*19+1.2)+3*Math.cos(t*6+1),x=sx+Math.cos(t)*j*1.17,y=sy+Math.sin(t)*j;
   i===0?fc.moveTo(x,y):fc.lineTo(x,y);
 }fc.closePath();fc.fillStyle='#000';fc.fill();}
 opening(11,.43);opening(5,.68);opening(-1,1);fc.globalAlpha=1;fc.globalCompositeOperation='source-over';return true;
}
function visible(p){return state.mode==='monde'||state.mode==='depart'&&p.premiere_zone||state.mode==='reveal'&&(p.premiere_zone||state.fog>=116)&&Math.hypot((p.ancre[0]-sx)*.85,p.ancre[1]-sy)<=state.fog+2;}
function draw(t){const {w,h,dpr,cam}=state,s=cam.s,left=w/2-cam.x*s,top=h/2-cam.y*s;
 cx.setTransform(dpr,0,0,dpr,0,0);cx.fillStyle='#161f19';cx.fillRect(0,0,w,h);cx.imageSmoothingEnabled=false;
 cx.save();cx.translate(left,top);cx.scale(s,s);
 const expansion=state.mode==='monde'?1:state.mode==='depart'?0:smooth(105,210,state.fog);
 if(expansion<1){cx.drawImage(assets.terrain,0,0);for(const p of start){const [x,y,a,b]=p.sprite;cx.drawImage(assets.sprites,x,y,a,b,p.rect[0],p.rect[1],a,b);}}
 if(expansion>0){cx.globalAlpha=expansion;cx.drawImage(assets.world,0,0);cx.globalAlpha=1;}
 const k=reduced?0:Math.floor(t/125)%8;
 if(k)for(const p of moving){if(!expansion&&!p.premiere_zone)continue;
  const [x,y,a,b]=p.rect;const ww=a-x,hh=b-y;if(left+a*s<0||top+b*s<0||left+x*s>w||top+y*s>h)continue;
  cx.globalAlpha=p.premiere_zone?1:expansion;cx.drawImage(assets.anim,k*pitch+1,p.animation*pitch+1,ww,hh,x,y,ww,hh);cx.globalAlpha=1;
 }
 if(fogLayer(state.fog))cx.drawImage(fcv,0,0);
 cx.restore();
 if(state.pins){const a=Math.min(4,Math.max(2,1.7*s));for(const p of listed){if(!visible(p))continue;const [x,y]=p.ancre;const l=left+x*s,t=top+y*s+3;cx.fillStyle=p.premiere_zone?'#fae29c':'#ebe4b3';cx.strokeStyle='#675137';cx.lineWidth=1;cx.beginPath();cx.arc(l,t,a,0,Math.PI*2);cx.fill();cx.stroke();}}
 for(const id of [state.hover,state.selected]){const p=by.get(id);if(!p||!visible(p))continue;const [x,y,a,b]=p.rect,l=left+x*s-4,t=top+y*s-4,ww=(a-x)*s+8,hh=(b-y)*s+8,sz=Math.min(9,ww/3,hh/3);cx.strokeStyle=id===state.selected?'#fff1bd':'#ecdfb3';cx.lineWidth=1.6;cx.beginPath();for(const [px,py,dx,dy] of [[l,t,1,1],[l+ww,t,-1,1],[l,t+hh,1,-1],[l+ww,t+hh,-1,-1]]){cx.moveTo(px,py+sz*dy);cx.lineTo(px,py);cx.lineTo(px+sz*dx,py);}cx.stroke();}
 const val=Math.round(state.cam.s/state.fit*100);$('zoom-level').value=val+' %';cv.dataset.zoom=String(val);cv.dataset.visibles=String(state.mode==='depart'?5:state.mode==='monde'?d.nb:all.filter(visible).length);
}
function tick(t){
 if(state.reveal&&!state.reveal.paused){progress(t);dirty();}
 if(state.tween){const o=state.tween,u=smooth(0,o.ms,t-o.t);state.cam={x:lerp(o.from.x,o.to.x,u),y:lerp(o.from.y,o.to.y,u),s:Math.exp(lerp(Math.log(o.from.s),Math.log(o.to.s),u))};if(u>=1)state.tween=null;dirty();}
 const p=reduced?0:Math.floor(t/125)%8;
 if(state.w>0&&(state.dirty||p!==state.phase)){state.dirty=false;state.phase=p;draw(t);}requestAnimationFrame(tick);
}
function pos(e){const b=cv.getBoundingClientRect();return {x:e.clientX-b.left,y:e.clientY-b.top};}
function hit(z){const c=state.cam,w=state.w,h=state.h;const x=(z.x-w/2)/c.s+c.x,y=(z.y-h/2)/c.s+c.y;let ans=null,best=Infinity;
 for(const p of all){if(!visible(p))continue;const [a,b,r,t]=p.rect,[px,py]=anchor(p),slack=clamp(9/c.s,2,14);if(x<a-slack||x>r+slack||y<b-slack||y>t+slack)continue;const v=Math.hypot(x-px,y-py);if(v<best){best=v;ans=p;}}
 return ans;
}
function stopTween(){state.tween=null;if(state.reveal&&!state.reveal.paused){state.reveal.paused=true;state.reveal.elapsed=performance.now()-state.reveal.begin;modeInfo();}}
function zoomAt(q,z={x:state.w/2,y:state.h/2}){stopTween();const c=state.cam,s=clamp(q,state.fit,8),k=1/c.s-1/s;state.cam=cap({x:c.x+(z.x-state.w/2)*k,y:c.y+(z.y-state.h/2)*k,s});dirty();}
function move(dx,dy){stopTween();state.cam=cap({x:state.cam.x-dx/state.cam.s,y:state.cam.y-dy/state.cam.s,s:state.cam.s});dirty();}
cv.addEventListener('wheel',e=>{e.preventDefault();zoomAt(state.cam.s*Math.exp(-e.deltaY*.0019),pos(e));},{passive:false});
cv.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse'&&e.button!==0)return;stopTween();cv.setPointerCapture(e.pointerId);const z=pos(e);touch.set(e.pointerId,z);if(touch.size===1)gest={start:z,last:z,changed:false};else if(touch.size===2){const [a,b]=touch.values();gest={changed:true,len:Math.hypot(a.x-b.x,a.y-b.y),mid:{x:(a.x+b.x)/2,y:(a.y+b.y)/2}};}});
cv.addEventListener('pointermove',e=>{const z=pos(e);if(!touch.has(e.pointerId)){if(e.pointerType==='mouse'){state.hover=hit(z)?.id||null;dirty();}return;}
 touch.set(e.pointerId,z);
 if(touch.size===2){const [a,b]=touch.values(),len=Math.hypot(a.x-b.x,a.y-b.y),mid={x:(a.x+b.x)/2,y:(a.y+b.y)/2};if(gest.len>1)zoomAt(state.cam.s*len/gest.len,gest.mid);if(gest.mid)move(mid.x-gest.mid.x,mid.y-gest.mid.y);gest={changed:true,len,mid};}
 else if(touch.size===1&&gest?.last){const ga=gest;if(ga.changed||Math.hypot(z.x-ga.start.x,z.y-ga.start.y)>3){ga.changed=true;state.hover=null;move(z.x-ga.last.x,z.y-ga.last.y);}ga.last=z;}
});
function end(e){if(!touch.has(e.pointerId))return;const click=touch.size===1&&!gest?.changed&&e.type==='pointerup';touch.delete(e.pointerId);
 if(click){const p=hit(pos(e));if(p)show(p,state.cam.s<2.1);else close();}
 if(touch.size===1){const [q]=touch.values();gest={changed:true,last:q,start:q};}else gest=null;
}
cv.addEventListener('pointerup',end);cv.addEventListener('pointercancel',end);cv.addEventListener('lostpointercapture',end);cv.addEventListener('pointerleave',()=>{state.hover=null;dirty();});
cv.addEventListener('keydown',e=>{if(e.key==='+'||e.key==='=')zoomAt(state.cam.s*1.29);else if(e.key==='-')zoomAt(state.cam.s/1.29);else if(e.key==='0')moveMode('monde');else if(e.key.startsWith('Arrow'))move(e.key==='ArrowLeft'?55:e.key==='ArrowRight'?-55:0,e.key==='ArrowUp'?55:e.key==='ArrowDown'?-55:0);else return;e.preventDefault();});
$('world').onclick=()=>{close();moveMode('monde');};$('start').onclick=()=>{close();moveMode('depart');};$('reveal').onclick=reveal;
$('picked').onclick=()=>{if(document.body.classList.contains('immersive'))$('wide').click();$('detail-name').focus({preventScroll:true});$('detail').scrollIntoView({behavior:scrollBehavior,block:'nearest'});};
$('plus').onclick=()=>zoomAt(state.cam.s*1.3);$('minus').onclick=()=>zoomAt(state.cam.s/1.3);
$('reset').onclick=()=>{state.mode==='depart'?moveMode('depart'):moveMode('monde');};$('wide').onclick=()=>pressed('wide',document.body.classList.toggle('immersive'));
$('pins').onclick=()=>{state.pins=!state.pins;pressed('pins',state.pins);dirty();};$('close').onclick=close;$('center').onclick=()=>{show(by.get(state.selected),true);goMap();};
$('search').oninput=list;$('search').onkeydown=e=>{if(e.key==='Enter'&&listed.length===1){e.preventDefault();show(listed[0],true);goMap();}else if(e.key==='Escape'&&$('search').value){$('search').value='';list();}};$('region').onchange=list;$('type').onchange=list;$('clear').onclick=()=>{$('search').value=$('region').value=$('type').value='';list();$('search').focus();};
for(const [k,v] of Object.entries(d.regions))$('region').append(new Option(v,k));for(const [k,v] of Object.entries(d.types))$('type').append(new Option(v,k));
$('site-total').textContent=d.nb;modeInfo();list();putSize();new ResizeObserver(putSize).observe(stage);$('loading').hidden=true;cv.dataset.ready='true';
let linked;try{linked=by.get(decodeURIComponent(location.hash.slice(1)));}catch{}if(linked)show(linked,true);
requestAnimationFrame(tick);
}
})();
