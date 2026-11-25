// Off-line animation. The room blueprints and the position/origin of every item remain static.
const boundedMotion=matchMedia('(prefers-reduced-motion: reduce)');
const clock={ms:0,play:!boundedMotion.matches,chosen:false,prev:null,next:0,raf:0};
const TAU=2*Math.PI, stageFrames=new Map();
let clothPreviews=[];
function nightBits(r,p,active){
  if(p!==3||!active)return [];
  const v=data.lianes[r.id];return [...v.g.flatMap(q=>[q.l[2],q.b[2]]),...v.o.map(q=>q[2])];
}
const lightSpot=(c,[x,y,image],alpha)=>{c.globalAlpha=alpha;drawPicture(c,image,x,y);};
function illuminate(c,r,ms){
  const f=data.lianes[r.id],n=r.n;
  c.save();c.globalCompositeOperation='screen';
  for(const [i,q] of f.g.entries()){
    const [period,offset]=data.cadence.cadences_ms[i],w=TAU*ms/period;
    const gain=.84+.103*Math.sin(w+offset+.103*n)+.039*Math.sin(.61*w-.8*offset+.013*n);
    lightSpot(c,q.l,gain);
  }
  // Opposed, gently dissolved penumbras: they are not moved across decorative geometry or exits.
  c.globalCompositeOperation='multiply';
  const orientation=.50+.42*Math.sin(TAU*ms/data.cadence.ombre_periode_ms+.12*n);
  lightSpot(c,f.o[0],.90*(1-orientation));lightSpot(c,f.o[1],.90*orientation);
  c.globalCompositeOperation='source-over';
  for(const [i,q] of f.g.entries()){
    const [period,offset]=data.cadence.cadences_ms[i],w=TAU*ms/period;
    lightSpot(c,q.b,.83+.110*Math.sin(w+offset+.103*n)+.038*Math.cos(w/1.6+offset+.049*n));
  }
  c.restore();
}
function spriteForScene(a,p,r){
  const f=data.etoffes[a.id];if(!f)return sprite(a,p,r);
  const colors=ambiance(r,p);if(!colors)return f.s;
  const key=a.id+'|'+r.nuit+'|'+p;
  if(!stageFrames.has(key))stageFrames.set(key,{source:f.s,lut:colors.lut,patches:[]});
  return stageFrames.get(key);
}
function stand(c,a,source,x,y,ms,phaseOffset=0){
  const spec=data.etoffes[a.id];
  const pic=picture(source);if(!pic.ready)return false;
  const index=Math.floor((Math.max(0,ms)+phaseOffset)/spec.dt)%spec.n;
  c.drawImage(pic.pic,(index%spec.c)*a.w,Math.floor(index/spec.c)*a.h,a.w,a.h,x,y,a.w,a.h);
  return true;
}
function drawObjet(c,a,p,r,x,y,ms){
  if(data.etoffes[a.id]&&stand(c,a,spriteForScene(a,p,r),x,y,ms,r.n*73+3*x+y))return;
  drawPicture(c,sprite(a,p,r),x,y);
}
function buildClothThumb(a,cover,img){
  if(!data.etoffes[a.id])return;
  const cv=make('canvas','apercu-etoffe');resize(cv,a.w,a.h);cv.style.width=a.w+'px';cv.setAttribute('aria-hidden','true');cv.hidden=true;
  cover.append(cv,make('small','badge-anime','Animé'));clothPreviews.push([a,cv,img]);
}
const inWindow=(c,clip=null)=>{
  const r=c.getBoundingClientRect();return r.width>0&&r.height>0&&r.bottom>Math.max(0,clip?.top??0)&&r.top<Math.min(innerHeight,clip?.bottom??innerHeight);
};
function showCloth(onlyVisible=false){
  if(s.page!=='atelier')return;
  const b=onlyVisible?$('catalog').getBoundingClientRect():null;
  for(const [a,cv,img] of clothPreviews){
    if(onlyVisible&&!inWindow(cv.hidden?img:cv,b))continue;
    const p=picture(data.etoffes[a.id].s);if(!p.ready)continue;
    const c=cv.getContext('2d');c.clearRect(0,0,a.w,a.h);c.imageSmoothingEnabled=false;
    stand(c,a,data.etoffes[a.id].s,0,0,clock.ms,a.n*113);cv.hidden=false;img.hidden=true;
  }
}
function drawMotion(){
  if(s.page!=='atelier'){
    if(s.phase!==3||!s.lianes)return;
    for(const [r,c,v] of (s.page==='sud'?southPairs:atlasCards))if(inWindow(c))drawScene(c.getContext('2d'),r,3,v,{gates:s.gates});
    return;
  }
  const r=s.room,v=viewport(),cloth=dataFor(r).some(o=>data.etoffes[o.meuble])||data.etoffes[s.tool];
  if(s.compare){
    for(const [i,c] of comparison.entries())if((cloth||(i===3&&s.lianes))&&inWindow(c))drawScene(c.getContext('2d'),r,i,v,{grid:s.grid,gates:s.gates});
  }else if((cloth||(s.phase===3&&s.lianes))&&inWindow(canvas))drawScene(ctx,r,s.phase,v,{grid:s.grid,gates:s.gates,interactive:s.mode==='plan'});
  if(clothPreviews.length)showCloth(true);
}
function advance(now){
  clock.raf=0;if(!clock.play||document.hidden){clock.prev=null;return;}
  clock.ms+=clock.prev===null?0:Math.min(now-clock.prev,100);clock.prev=now;
  if(now>=clock.next){clock.next=now+73;if(!queued)drawMotion();}
  clock.raf=requestAnimationFrame(advance);
}
function syncMotion(){
  const t=$('motion-toggle');t.setAttribute('aria-pressed',String(clock.play));t.querySelector('span').textContent=clock.play?'Animations : actives':'Animations : en pause';
  const n=t.querySelector('use');n.setAttribute('href',clock.play?'#i-pause-motion':'#i-play-motion');
  t.title=clock.play?'Figer les étoffes, les halos et les ombres':'Relancer les étoffes, les halos et les ombres';
  if(clock.play&&!document.hidden){if(!clock.raf){clock.prev=null;clock.next=0;clock.raf=requestAnimationFrame(advance);}}
  else{if(clock.raf)cancelAnimationFrame(clock.raf);clock.raf=0;clock.prev=null;}
  invalidate();
}
function setupMotion(){
  $('motion-toggle').onclick=()=>{clock.chosen=true;clock.play=!clock.play;syncMotion();};
  boundedMotion.addEventListener?.('change',e=>{if(!clock.chosen){clock.play=!e.matches;syncMotion();}});
  document.addEventListener('visibilitychange',syncMotion);
  syncMotion();
}
