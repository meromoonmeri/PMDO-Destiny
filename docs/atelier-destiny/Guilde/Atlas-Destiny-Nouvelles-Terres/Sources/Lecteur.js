'use strict';
const A=JSON.parse(document.getElementById('data').textContent);
const $=s=>document.getElementById(s), nw=A.size[0], nh=A.size[1], stage=$('stage'), map=$('world'), sea=$('seaways');
const regionBy=Object.fromEntries(A.regions.map(r=>[r.id,r])), siteBy=Object.fromEntries(A.sites.map(p=>[p.id,p]));
const S={z:1,x:nw/2,y:nh/2,names:true,pins:false,routes:false,region:null,site:null};
let box={w:0,h:0,s:1,tx:0,ty:0};
const LIM=8, drag=new Map(); let click=null;
const clamp=(n,lo,hi)=>Math.max(lo,Math.min(hi,n));
function el(kind,cls='',txt=''){const e=document.createElement(kind);if(cls)e.className=cls;if(txt)e.textContent=txt;return e;}
function tag(cls,txt,tagName){const b=el('button',cls,txt);b.type='button';if(tagName)b.setAttribute('aria-label',tagName);return b;}
function glyph(known){const g=el('i','pin-icon'+(known?' known':''));g.setAttribute('aria-hidden','true');return g;}
function img(src,cls=''){const i=el('img',cls);i.src=src;i.alt='';i.draggable=false;return i;}
function press(e,yn){e.setAttribute('aria-pressed',String(yn));}
function current(e,yn){if(yn)e.setAttribute('aria-current','true');else e.removeAttribute('aria-current');}
const labels=A.regions.map(r=>{
  const b=tag('label',r.nom,'Voir '+r.nom);b.dataset.id=r.id;b.addEventListener('click',()=>choose(r.id));$('names').append(b);return [b,r];
});
const pins=A.sites.map(p=>{
  const b=tag('pin','',p.nom);b.dataset.id=p.id;b.title=p.nom;b.append(glyph(p.existe_dans_le_projet));b.addEventListener('click',()=>place(p.id));$('pins').append(b);return [b,p];
});
function setMarkers(pairs,key,show,id,group){
  for(const [b,o] of pairs){
    const [x,y]=o[key],left=box.tx+x*box.s,top=box.ty+y*box.s;
    b.style.left=left+'px';b.style.top=top+'px';
    b.hidden=!show||(S.region&&group(o)!==S.region)||left<0||top<0||left>box.w||top>box.h;
    current(b,id===o.id);
  }
}
function draw(){
  const w=stage.clientWidth,h=stage.clientHeight;if(!w||!h)return;
  const f=Math.min(w/nw,h/nh),s=f*S.z;
  const rx=Math.min(nw/2,w/(2*s)),ry=Math.min(nh/2,h/(2*s));
  S.x=clamp(S.x,rx,nw-rx); S.y=clamp(S.y,ry,nh-ry);
  box={w,h,s,tx:w/2-S.x*s,ty:h/2-S.y*s};
  for(const layer of [map,sea]){layer.style.width=nw*s+'px';layer.style.height=nh*s+'px';layer.style.transform=`translate(${box.tx}px,${box.ty}px)`;}
  sea.hidden=!S.routes;press($('showRoutes'),S.routes);const guide=$('guideRoutes');if(guide)press(guide,S.routes);
  $('names').hidden=!S.names; $('pins').hidden=!S.pins;
  setMarkers(labels,'label',S.names,S.region,r=>r.id);setMarkers(pins,'position',S.pins,S.site,p=>p.region);
  $('percent').value=Math.round(S.z*100)+' %';
  $('less').disabled=S.z<=1.001;$('more').disabled=S.z>=LIM-.001;
  press($('showNames'),S.names); press($('showPins'),S.pins);press($('worldBtn'),!S.region&&S.z<=1.001);press($('reverieBtn'),S.region==='reve');
  $('viewTitle').textContent=S.region ? regionBy[S.region].nom : (S.z>1.001 ? 'Carte du monde' : 'Vue du monde');
}
function zoom(z,u=box.w/2,v=box.h/2){
  const nz=clamp(z,1,LIM);if(Math.abs(nz-S.z)<.0001)return false;
  const sx=(u-box.tx)/box.s,sy=(v-box.ty)/box.s;
  const ns=box.s*nz/S.z;S.z=nz;
  S.x=sx-(u-box.w/2)/ns;S.y=sy-(v-box.h/2)/ns;
  draw();return true;
}
function world(){S.region=null;S.site=null;S.x=nw/2;S.y=nh/2;S.z=1;S.pins=false;panel();draw();}
function focus(x,y,k){S.x=x;S.y=y;S.z=clamp(k,1,LIM);draw();}
function choose(id){
  const r=regionBy[id];S.region=id;S.site=null;S.pins=true;
  const [x,y,u,v]=id==='reve'?A.reverie_box:r.bounds;
  const zx=id==='reve'?3.48:Math.min(nw/(u-x+64),nh/(v-y+70));
  focus((x+u)/2,(y+v)/2,clamp(zx,1.34,3.5));panel();
}
function place(id){
  const p=siteBy[id];S.region=p.region;S.site=id;S.pins=true;
  const [x,y]=p.position;focus(x,(y+p.boite[1])/2,Math.max(S.z,4.05));panel(true);
}
const ordered=[regionBy.reve,...A.regions.filter(r=>r.id!=='reve')];
function panel(retain=false){
  const c=$('catalog'),top=retain?c.scrollTop:0;c.replaceChildren();$('back').hidden=!S.region;
  $('indexTitle').textContent=S.region?'Fiche de région':'Répertoire';
  if(!S.region){
    const wrap=el('div','catalog-grid');
    for(const r of ordered){
      const b=tag('region '+r.id,'','Explorer '+r.nom);b.dataset.region=r.id;
      const tx=el('span');tx.append(el('strong','',r.nom),el('small','',r.biome));
      b.append(img(r.image,'mini'),tx,el('span','num',r.num));b.addEventListener('click',()=>choose(r.id));wrap.append(b);
    }
    c.append(wrap);
    const note=el('div','route-note');note.append(el('h3','','Traversées proposées'),el('p','description','Des itinéraires maritimes relient la crique de Réverie, Orival, les Haltes et les estuaires d’Estrel.'));
    const list=el('ul');for(const route of A.routes)list.append(el('li','',route.nom));note.append(list);
    const toggle=tag('','Afficher les routes');toggle.id='guideRoutes';press(toggle,S.routes);toggle.addEventListener('click',toggleRoutes);note.append(toggle);c.append(note);c.scrollTop=top;return;
  }
  const r=regionBy[S.region],card=el('div','record');
  card.append(img(r.image,'banner'),el('h3','',r.nom),el('p','biome',r.biome),el('p','description',r.texte),el('h4','','Lieux sur la carte'));
  const list=el('div','site-list');
  for(const p of A.sites.filter(o=>o.region===r.id)){
    const yes=p.id===S.site;
    const b=tag('site-line','',p.nom);b.dataset.site=p.id;current(b,yes);
    b.append(img(p.image),el('strong','',p.nom),glyph(p.existe_dans_le_projet));
    if(yes){const desc=el('span','description',p.description);desc.append(el('span','place-note',p.existe_dans_le_projet?'Lieu documenté · position illustrative':'Lieu proposé pour Destiny'));b.append(desc);}
    b.addEventListener('click',()=>{place(p.id);c.querySelector(`[data-site="${p.id}"]`)?.focus({preventScroll:true});});list.append(b);
  }
  card.append(list);c.append(card);c.scrollTop=top;
}
function toLocal(e){const r=stage.getBoundingClientRect();return {x:e.clientX-r.left,y:e.clientY-r.top};}
function inPoly(poly,x,y){let b=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){
  const [a,c]=poly[i],[k,l]=poly[j];if((c>y)!==(l>y)&&x<a+(k-a)*(y-c)/(l-c))b=!b;
}return b;}
function hit(q){
  const x=(q.x-box.tx)/box.s,y=(q.y-box.ty)/box.s;
  const r=A.regions.find(o=>[o.cote,...o.aires].some(coast=>inPoly(coast,x,y)));if(r&&r.id!==S.region)choose(r.id);
}
function pan(dx,dy){S.x-=dx/box.s;S.y-=dy/box.s;draw();}
function midpoint(a,b){return [(a.x+b.x)/2,(a.y+b.y)/2,Math.hypot(a.x-b.x,a.y-b.y)];}
stage.addEventListener('pointerdown',e=>{
  if(e.button!==0||e.target.closest('button'))return;
  const q=toLocal(e);if(!drag.size)click={x:q.x,y:q.y,id:e.pointerId};else click=null;
  drag.set(e.pointerId,q);stage.setPointerCapture?.(e.pointerId);
  if(e.pointerType==='mouse'){stage.focus({preventScroll:true});e.preventDefault();}
});
stage.addEventListener('pointermove',e=>{
  if(!drag.has(e.pointerId))return;
  const q=toLocal(e),a=drag.get(e.pointerId);
  if(click&&Math.hypot(click.x-q.x,click.y-q.y)>4){click=null;stage.classList.add('dragging');}
  const b=[...drag].find(([id])=>id!==e.pointerId)?.[1];
  if(b){
    const [mx,my,len]=midpoint(a,b),[nx,ny,len2]=midpoint(q,b);
    if(len>8)zoom(S.z*len2/len,mx,my);pan(nx-mx,ny-my);
  }else if(!click)pan(q.x-a.x,q.y-a.y);
  drag.set(e.pointerId,q);
});
function up(e){
  if(!drag.has(e.pointerId))return;
  const maybeClick=click?.id===e.pointerId&&e.type==='pointerup';click=null;drag.delete(e.pointerId);
  if(!drag.size)stage.classList.remove('dragging');if(maybeClick)hit(toLocal(e));
}
for(const type of ['pointerup','pointercancel','lostpointercapture'])stage.addEventListener(type,up);
stage.addEventListener('wheel',e=>{
  const p=toLocal(e); const delta=clamp(e.deltaY*(e.deltaMode===1?15:1),-110,110);
  if(zoom(S.z*Math.exp(-delta*.0038),p.x,p.y))e.preventDefault();
},{passive:false});
stage.addEventListener('keydown',e=>{
  if(e.target!==stage)return;
  const f={'ArrowLeft':()=>pan(44,0),'ArrowRight':()=>pan(-44,0),'ArrowUp':()=>pan(0,44),'ArrowDown':()=>pan(0,-44),'+':()=>zoom(S.z*1.3),'=':()=>zoom(S.z*1.3),'-':()=>zoom(S.z/1.3),'0':world,'Home':world};
  if(f[e.key]){e.preventDefault();f[e.key]();}
});
$('less').addEventListener('click',()=>zoom(S.z/1.3));$('more').addEventListener('click',()=>zoom(S.z*1.3));
$('showNames').addEventListener('click',()=>{S.names=!S.names;draw();});$('showPins').addEventListener('click',()=>{S.pins=!S.pins;draw();});
function toggleRoutes(){S.routes=!S.routes;draw();}
$('showRoutes').addEventListener('click',toggleRoutes);
$('worldBtn').addEventListener('click',world);$('reverieBtn').addEventListener('click',()=>choose('reve'));
$('back').addEventListener('click',()=>{world();$('worldBtn').focus({preventScroll:true});});
new ResizeObserver(draw).observe(stage);map.src=A.image;sea.src=A.seaways;panel();draw();
window.atlasDestiny={snapshot:()=>({...S,viewport:{...box},carteChargee:map.complete&&map.naturalWidth===nw,regions:A.regions.length,lieux:A.sites.length})};
