(() => {
'use strict';
const data = JSON.parse(document.getElementById('donnees').textContent);
const $ = (id) => document.getElementById(id);
const make = (tag, cls, value) => { const e = document.createElement(tag); if (cls) e.className = cls; if (value !== undefined) e.textContent = value; return e; };
const svg = (name) => { const e = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); const u = document.createElementNS(e.namespaceURI, 'use'); u.setAttribute('href', '#i-' + name); e.setAttribute('aria-hidden','true'); e.append(u); return e; };
const button = (cls,text,action,icon) => {const a=make('button',cls);a.type='button';if(icon)a.append(svg(icon));if(text)a.append(make('span','',text));if(action)a.addEventListener('click',action);return a;};
const phases = [
  {name:'Jour',icon:'sun',tone:'#efc786',tint:'#413526',title:'Bois doré et vitres claires des intérieurs de Grodoudou'},
  {name:'Aube',icon:'dawn',tone:'#f1c0a8',tint:'#47332c',title:'Une lumière pêche, déclinée de la palette de Grodoudou'},
  {name:'Crépuscule',icon:'dusk',tone:'#eda775',tint:'#482f24',title:'Les tons orangés de la façade au crépuscule'},
  {name:'Nuit',icon:'moon',tone:'#adccf5',tint:'#2c3c4d',title:'Palette de nuit de la guilde de Grodoudou'},
];
const groups=['Accès principal','Aile ouest','Couloirs & chambres'];
const cats=[['tout','Tout'],['meubles','Meubles'],['panneaux','Panneaux'],['tapis','Tapis']];
const gameMap = new Map(data.rooms.map(r => [r.id,r]));
const assets = new Map(data.catalog.map(a => [a.id,a]));
const STORE='pmd-destiny:guilde:atelier:077:v1', FORM='destiny-guilde-mobilier-v1', GROD_FORM='destiny-guilde-grodoudou-v2', MAX=128;
const grodLayouts = new Set(['bureau_maitre','refectoire','dortoir_nord_1','dortoir_nord_2','dortoir_sud_1','dortoir_sud_2'].map(n=>'guilde_destiny_'+n));
const s={page:'atlas',room:data.rooms[0],phase:0,mode:'plan',before:false,compare:false,grid:false,gates:false,snap:true,category:'tout',tool:null,selected:null,ghost:null,drag:null};
let layout=Object.create(null), back=[], forwards=[], saveAvailable=true, flash, queued=false;
const canvas=$('map'), ctx=canvas.getContext('2d'), roomButtons=[], phaseButtons=[], filterButtons=[], comparison=[];
const storeImages=new Map();
const uri=(b) => b.startsWith('data:') ? b : 'data:image/png;base64,'+b;
// All four phases shade the decor and props with the same per-room palette.
const ambiance=(r,p)=>p===3 ? data.nuits?.[r.nuit] : data.lumieres?.[r.nuit]?.[p];
const spritesAmbiance=new Map();
function sprite(a,p,r){
  const n=ambiance(r,p);if(!n)return a.m[p];
  const key=a.id+'|'+r.nuit+'|'+p;
  if(!spritesAmbiance.has(key))spritesAmbiance.set(key,{source:a.m[0],lut:n.lut,patches:[]});
  return spritesAmbiance.get(key);
}
for(const r of data.rooms)r.m=data.tints.map((tint,i)=>{
  const n=ambiance(r,i);if(!n&&!i)return [r.base,r.front];
  const couleurs=n?{lut:n.lut}:{tint};
  return [{source:r.base,...couleurs,patches:r.patches[i]}, {source:r.front,...couleurs,patches:[]}];
});
const blank=() => Object.create(null);
const within=(n,a,b)=>Math.max(a,Math.min(b,n));
const overlaps=(a,b)=>a[0]<b[0]+b[2]&&a[0]+a[2]>b[0]&&a[1]<b[1]+b[3]&&a[1]+a[3]>b[1];
const normalized=(text)=>text.toLocaleLowerCase('fr').normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim();
const clampInt=(n)=>Math.round(n);
function dataFor(r=s.room){return layout[r.id] || [];}
function current(){ return dataFor().find(x=>x.id===s.selected); }
function viewport(r=s.room){
  if (s.mode==='plan'||!r.south) return {x:0,y:0,w:r.w,h:r.h};
  return {x:within(r.south.x-160,0,r.w-320),y:(s.before?r.h:r.south.bottom)-240,w:320,h:240};
}
function why(r,a,x,y){
  if (!Number.isInteger(x)||!Number.isInteger(y)||x<0||y<0||x+a.w>r.w||y+a.h>(r.south?.bottom??r.h)) return 'Place le meuble à l’intérieur du plan, avant le bord sud.';
  const shape=[x,y,a.w,a.h];
  if (r.gates.some(g=>overlaps(shape,g.rect))||r.mark.some(m=>overlaps(shape,m))) return 'Garde le seuil et son arrivée libres.';
  const tx=Math.floor((x+a.w/2)/8),ty=Math.floor((y+a.h-5)/8);
  if (!a.wall && r.floor[ty]?.[tx]!=='1') return 'Le pied de ce meuble doit être sur le sol praticable.';
  return '';
}
function toast(text,err=false){
  clearTimeout(flash);$('toast').textContent=text;$('toast').hidden=false;$('toast').classList.toggle('error',err);
  flash=setTimeout(()=>$('toast').hidden=true,err?6400:4200);
}
function save(){
  if (saveAvailable) {try{localStorage.setItem(STORE,JSON.stringify(payload()));return;}catch{saveAvailable=false;}}
}
function payload(){return {format:FORM,jeu:data.game,salles:layout};}
function parseLayout(d){
  if(!d || ![FORM,GROD_FORM].includes(d.format) || d.jeu!==data.game || !d.salles || Array.isArray(d.salles) || typeof d.salles!=='object') throw new Error('Ce JSON n’est pas un plan de l’atelier Destiny 0.7.7.');
  const result=blank();
  for (const [n,objects] of Object.entries(d.salles)) {
    const r=gameMap.get(n);
    if(!r||!Array.isArray(objects)||objects.length>MAX) throw new Error('Salle ou nombre d’objets incompatible.');
    if(grodLayouts.has(n) && d.format===GROD_FORM && objects.length) throw new Error(r.label+' : ce placement utilise le plan Grodoudou. Ouvre ton projet dans la variante Grodoudou pour ne rien déplacer.');
    const ids=new Set();
    const cleaned=objects.map(o=>{
      const a=o&&assets.get(o.meuble);
      if(!a||typeof o.id!=='string'||!/^[a-z0-9-]{1,80}$/i.test(o.id)||ids.has(o.id)) throw new Error('Objet PMU inconnu ou identifiant en double.');
      const note=why(r,a,o.x,o.y);if(note)throw new Error(r.label+' : '+note);
      ids.add(o.id);return {id:o.id,meuble:o.meuble,x:o.x,y:o.y};
    });
    if(cleaned.length)result[n]=cleaned;
  }
  return result;
}
function remember(next){
  back.push(layout);if(back.length>60)back.shift();forwards=[];layout=next;save();refresh();
}
function setRoomItems(items){const next=Object.assign(blank(),layout);if(items.length)next[s.room.id]=items;else delete next[s.room.id];remember(next);}
function cancel(){s.ghost=null;s.drag=null;s.tool=null;canvas.classList.remove('dragging');}
function undo(){if(!back.length)return;forwards.push(layout);layout=back.pop();s.selected=null;cancel();save();refresh();}
function redo(){if(!forwards.length)return;back.push(layout);layout=forwards.pop();s.selected=null;cancel();save();refresh();}
function selectRoom(id){const r=gameMap.get(id);if(!r)return;s.room=r;cancel();s.selected=null;s.before=false;if(!r.south)s.mode='plan';refresh();}
function setPhase(i){s.phase=i;s.compare=false;refresh();}
function activateTool(a){
  s.selected=null;s.drag=null;s.ghost=null;s.tool=s.tool===a.id?null:a.id;
  if(s.tool){s.mode='plan';s.compare=false;}
  refresh();
  if(s.tool&&matchMedia('(max-width:655px)').matches)$('view').scrollIntoView({block:'nearest',behavior:'smooth'});
}
function unique(){return globalThis.crypto?.randomUUID?.()??(Date.now().toString(36)+'-'+Math.random().toString(36).slice(2));}
function pos(a,x,y,snap=s.snap){const step=snap?8:1;return {x:Math.round(x/step)*step,y:Math.round(y/step)*step};}
function place(a,p){
  const issue=why(s.room,a,p.x,p.y);if(issue){toast(issue,true);return false;}
  if(dataFor().length>=MAX){toast('Maximum : '+MAX+' objets par salle.',true);return false;}
  const o={id:unique(),meuble:a.id,x:p.x,y:p.y};s.tool=null;s.ghost=null;s.selected=o.id;setRoomItems([...dataFor(),o]);return true;
}
function move(o,p){
  const a=assets.get(o.meuble),issue=why(s.room,a,p.x,p.y);if(issue){toast(issue,true);refresh();return false;}
  if(o.x===p.x&&o.y===p.y){refresh();return true;}
  setRoomItems(dataFor().map(t=>t.id===o.id?{...o,...p}:t));return true;
}
function remove(o){s.selected=null;setRoomItems(dataFor().filter(t=>t.id!==o.id));toast('Meuble retiré. Tu peux annuler cette action.');}
function duplicate(o){
  const a=assets.get(o.meuble);const tries=[[24,0],[-24,0],[0,24],[0,-24],[16,16],[-16,16],[16,-16],[-16,-16]];
  const p=tries.map(([dx,dy])=>pos(a,o.x+dx,o.y+dy)).find(q=>!why(s.room,a,q.x,q.y));
  if(p)place(a,p);else{ s.tool=a.id;s.selected=null;s.ghost=null;refresh();toast('Choisis un emplacement pour la copie.'); }
}
function center(a){
  const r=s.room,ox=Math.round((r.w-a.w)/16)*8,oy=Math.round((r.h*.64-a.h)/8)*8;
  const candidates=[];
  for(let y=0;y<=r.h-a.h;y+=8)for(let x=0;x<=r.w-a.w;x+=8){if(!why(r,a,x,y))candidates.push([x,y,(x-ox)**2+(y-oy)**2]);}
  candidates.sort((u,v)=>u[2]-v[2]);
  if(candidates.length)place(a,{x:candidates[0][0],y:candidates[0][1]});else toast('Pas assez de place pour cet objet dans cette salle.',true);
}

function picture(b){
  if(storeImages.has(b))return storeImages.get(b);
  const raw=typeof b==='string',pic=raw?new Image():make('canvas');let done;
  const promise=new Promise(resolve=>{done=resolve;});
  const row={pic,ready:false,promise};storeImages.set(b,row);
  const success=()=>{row.ready=true;done(true);invalidate();};
  const fail=()=>{done(false);toast('Une image n’a pas pu être chargée.',true);};
  if(raw){pic.onload=success;pic.onerror=fail;pic.src=uri(b);return row;}
  const src=picture(b.source),parts=b.patches.map(([x,y,p])=>[x,y,picture(p)]);
  Promise.all([src.promise,...parts.map(([, ,p])=>p.promise)]).then(results=>{
    if(results.includes(false)){fail();return;}
    pic.width=src.pic.width;pic.height=src.pic.height;
    const c=pic.getContext('2d',{willReadFrequently:true});c.imageSmoothingEnabled=false;c.drawImage(src.pic,0,0);
    const im=c.getImageData(0,0,pic.width,pic.height),pixels=im.data;
    if(b.lut){const [red,green,blue]=b.lut;
      for(let i=0;i<pixels.length;i+=4){pixels[i]=red[pixels[i]];pixels[i+1]=green[pixels[i+1]];pixels[i+2]=blue[pixels[i+2]];}
    }else{const [red,green,blue]=b.tint;
      for(let i=0;i<pixels.length;i+=4){pixels[i]=Math.round(pixels[i]*red/255);pixels[i+1]=Math.round(pixels[i+1]*green/255);pixels[i+2]=Math.round(pixels[i+2]*blue/255);}
    }
    c.putImageData(im,0,0);
    for(const [x,y,p] of parts){c.clearRect(x,y,p.pic.width,p.pic.height);c.drawImage(p.pic,x,y);}
    success();
  }).catch(fail);
  return row;
}
function drawPicture(c,b,x,y){const p=picture(b);if(p.ready)c.drawImage(p.pic,x,y);}
function box(c,x,y,w,h,col,dash=false){c.strokeStyle=col;c.lineWidth=1;c.setLineDash(dash?[3,2]:[]);c.strokeRect(x+.5,y+.5,w,h);c.setLineDash([]);}
function drawScene(c,r,p,view,opts={}){
  const {grid=false,gates=false,interactive=false,items=dataFor(r)}=opts;
  c.clearRect(0,0,view.w,view.h);c.save();c.imageSmoothingEnabled=false;
  const n=ambiance(r,p);c.fillStyle=n?`rgb(${n.fond.join(',')})`:'#20221b';c.fillRect(0,0,view.w,view.h);c.translate(-view.x,-view.y);
  drawPicture(c,r.m[p][0],0,0);
  for(const o of items){const a=assets.get(o.meuble);const q=interactive&&s.drag?.id===o.id ? s.drag.position : o;c.globalAlpha=q.bad?.42:1;drawPicture(c,sprite(a,p,r),q.x,q.y);c.globalAlpha=1;}
  if(interactive&&s.ghost&&s.tool){const a=assets.get(s.tool),q=s.ghost;c.globalAlpha=q.bad?.42:.76;drawPicture(c,sprite(a,p,r),q.x,q.y);c.globalAlpha=1;}
  drawPicture(c,r.m[p][1],0,0);
  if(grid){c.strokeStyle='#fff1d541';c.lineWidth=.5;c.beginPath();for(let x=0;x<r.w;x+=8){c.moveTo(x+.5,0);c.lineTo(x+.5,r.h);}for(let y=0;y<r.h;y+=8){c.moveTo(0,y+.5);c.lineTo(r.w,y+.5);}c.stroke();}
  if(gates){for(let i=0;i<r.gates.length;i++){
    const [x,y,w,h]=r.gates[i].rect;c.fillStyle='#eebd554c';c.fillRect(x,y,w,h);box(c,x,y,w-1,h-1,'#ffe3a3',true);
    c.font='bold 9px monospace';c.textAlign='center';c.textBaseline='middle';c.fillStyle='#20190e';c.fillRect(x+w/2-6,y+h/2-6,12,12);c.fillStyle='#ffe8bb';c.fillText(i+1,x+w/2,y+h/2+.4);
  }}
  if(interactive){
    const o=current();if(o){const a=assets.get(o.meuble),q=s.drag?.position??o;box(c,q.x,q.y,a.w-1,a.h-1,q.bad?'#f3a18d':'#f8d099',!!s.drag);}
    if(s.ghost&&s.tool){const a=assets.get(s.tool),q=s.ghost;box(c,q.x,q.y,a.w-1,a.h-1,q.bad?'#f3a18d':'#f8d099',true);}
  }
  c.restore();
  c.canvas.dataset.scene=[...r.m[p],...items.map(o=>sprite(assets.get(o.meuble),p,r))].every(b=>picture(b).ready)?`${r.id}:${p}:${view.y}:${items.length}`:'';
}
function resize(c,w,h){if(c.width!==w)c.width=w;if(c.height!==h)c.height=h;}
function invalidate(){if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;draw();});}
function draw(){
  if(s.page!=='atelier'){paintAtlas();return;}
  const view=viewport(), r=s.room;
  if(s.compare){for(const [i,c] of comparison.entries()){resize(c,view.w,view.h);drawScene(c.getContext('2d'),r,i,view,{grid:s.grid,gates:s.gates});}}
  else{resize(canvas,view.w,view.h);drawScene(ctx,r,s.phase,view,{grid:s.grid,gates:s.gates,interactive:s.mode==='plan'});}
}
function tell(text,err=false){$('hint').textContent=text;$('hint').classList.toggle('alert',err);}
function hint(){
  if(s.compare){tell('Même salle, mêmes meubles, quatre lumières. Clique sur une vue pour l’ouvrir.');return;}
  if(s.mode==='cadre'){const b=s.room.south?.band||0;tell(!b?'Ce seuil atteint déjà le bord de la carte.':(s.before?'Caméra d’origine : '+b+' px sous le seuil.':'Caméra recadrée : '+b+' px de vide hors champ.'));return;}
  if(s.ghost?.bad||s.drag?.position.bad){tell(s.ghost?.bad||s.drag.position.bad,true);return;}
  if(s.tool){tell('Clique sur le plan pour poser : '+assets.get(s.tool).label+'.');return;}
  if(current()){tell('Glisse le meuble ou utilise les flèches. Suppr pour le retirer.');return;}
  tell(dataFor().length?'Clique sur un meuble pour le sélectionner.':'Choisis un objet PMU à droite pour commencer.');
}
function inspector(){
  const panel=$('inspector'),a=s.tool&&assets.get(s.tool),o=current();panel.replaceChildren();panel.hidden=!(a||o);if(panel.hidden)return;
  const caption=make('strong','',a?.label??assets.get(o.meuble).label);panel.append(caption);
  if (a){panel.append(make('span','',a.w+' × '+a.h+' px · sprite natif'));const actions=make('div','inspect-actions');actions.append(button('soft','Poser au centre',()=>center(a),'target'),button('soft','Annuler',()=>{cancel();refresh();}));panel.append(actions);}
  else{
    panel.append(make('span','inspect-coords','X '+o.x+' · Y '+o.y));const actions=make('div','inspect-actions');actions.append(button('soft','Dupliquer',()=>duplicate(o),'copy'),button('soft','Retirer',()=>remove(o),'trash'));panel.append(actions);
  }
}
function updatePalette(){
  const term=normalized($('query').value);const el=$('catalog'),scroll=el.scrollTop;el.replaceChildren();
  const cards=data.catalog.filter(a=>(s.category==='tout'||s.category===a.category)&&(!term||normalized(a.label).includes(term)));
  for(const a of cards){const c=button('asset','',()=>activateTool(a));c.dataset.asset=a.id;c.setAttribute('aria-label',a.label);c.setAttribute('aria-pressed',String(s.tool===a.id));c.title=a.label+' · '+a.w+' × '+a.h+' px';
    const cover=make('span','thumb'),im=make('img');im.alt='';im.src=uri(a.m[0]);im.width=a.w;im.height=a.h;cover.append(im);c.append(cover,make('span','item-label',a.label));el.append(c);}
  if(!cards.length)el.append(make('p','none','Aucun meuble ne correspond.'));el.scrollTop=scroll;
}
function refresh(){
  if (s.selected&&!current())s.selected=null;
  const r=s.room, v=viewport();
  updateAtlas();
  $('room-select').value=r.id;$('room-name').textContent=r.label;$('room-kind').textContent='SALLE '+String(r.n).padStart(2,'0')+' · DESTINY 0.7.7';$('dim').textContent=v.w+' × '+v.h+' px';
  for(const [el,m,b] of roomButtons){el.setAttribute('aria-current',String(r===m));const n=dataFor(m).length;b.textContent=n;b.hidden=!n;}
  for(const [i,b] of phaseButtons.entries())b.setAttribute('aria-pressed',String(i===s.phase&&!s.compare));
  for(const [k,b] of filterButtons)b.setAttribute('aria-pressed',String(s.category===k));
  for(const [id,value] of Object.entries({plan:s.mode==='plan',camera:s.mode==='cadre',before:s.before,gates:s.gates,grid:s.grid,compare:s.compare}))$(id).setAttribute('aria-pressed',String(value));
  $('camera').disabled=!r.south;$('before').hidden=s.mode==='plan'||!r.south?.band;$('before').textContent=s.before?'Avant ✓':'Avant';
  $('compare').querySelector('span').textContent=s.compare?'Vue simple':'Comparer les 4';$('mapwrap').hidden=s.compare;$('compare-view').hidden=!s.compare;$('zoom').disabled=s.compare;
  $('mapwrap').style.setProperty('--pixel-w',v.w+'px');$('mapwrap').classList.toggle('is-one',$('zoom').value==='one');$('mapwrap').classList.toggle('is-zoom',$('zoom').value==='two');
  canvas.classList.toggle('editable',s.mode==='plan');
  $('accesses').replaceChildren(...r.gates.map((g,i)=>{const to=gameMap.get(g.dest);const p=to?button('portal',(i+1)+' · '+to.label,()=>selectRoom(to.id)):make('span','portal-out',(i+1)+' · Falaise');p.title=g.id;return p;}));
  $('undo').disabled=!back.length;$('redo').disabled=!forwards.length;$('download-ground').disabled=s.page!=='atelier';$('download-png').disabled=s.page!=='atelier';
  const count=Object.values(layout).reduce((n,a)=>n+a.length,0);
  $('save-state').textContent=count?`${count} objet${count>1?'s':''} dans le projet · ${saveAvailable?'copie locale':'exporte ton JSON'}`:'Projet local · aucun changement dans le jeu';
  inspector();hint();
  // Keep catalogue keyboard focus and scroll in place between actions.
  for(const b of $('catalog').querySelectorAll('[data-asset]'))b.setAttribute('aria-pressed',String(s.tool===b.dataset.asset));
  invalidate();
}

function cursor(e){
  const v=viewport(),r=canvas.getBoundingClientRect(),scaleW=(r.width-2)/v.w,scaleH=(r.height-2)/v.h;
  return {x:clampInt((e.clientX-r.left-1)/scaleW+v.x),y:clampInt((e.clientY-r.top-1)/scaleH+v.y)};
}
function mouseGhost(e){
  const p=cursor(e);$('coords').textContent='X '+p.x+' · Y '+p.y;
  if(s.mode!=='plan')return;
  if(s.drag){const a=assets.get(s.drag.meuble),v=pos(a,p.x-s.drag.dx,p.y-s.drag.dy);v.bad=why(s.room,a,v.x,v.y);s.drag.position=v;hint();invalidate();}
  else if(s.tool){const a=assets.get(s.tool),q=pos(a,p.x-a.w/2,p.y-a.h/2);q.bad=why(s.room,a,q.x,q.y);s.ghost=q;hint();invalidate();}
}
canvas.addEventListener('pointermove',mouseGhost);
canvas.addEventListener('pointerleave',()=>{if(!s.drag){s.ghost=null;$('coords').textContent='X — · Y —';hint();invalidate();}});
canvas.addEventListener('pointerdown',e=>{
  if(s.mode!=='plan'||s.compare||e.button>0||s.drag)return;e.preventDefault();canvas.focus({preventScroll:true});
  const t=cursor(e);
  if(s.tool){const a=assets.get(s.tool);place(a,pos(a,t.x-a.w/2,t.y-a.h/2));return;}
  const o=[...dataFor()].reverse().find(o=>{const a=assets.get(o.meuble);return t.x>=o.x&&t.y>=o.y&&t.x<o.x+a.w&&t.y<o.y+a.h;});
  s.selected=o?.id??null;
  if(o){s.drag={...o,dx:t.x-o.x,dy:t.y-o.y,position:o,pointer:e.pointerId};canvas.setPointerCapture(e.pointerId);canvas.classList.add('dragging');}
  refresh();
});
canvas.addEventListener('pointerup',e=>{
  const d=s.drag;if(!d||d.pointer!==e.pointerId)return;
  s.drag=null;canvas.classList.remove('dragging');if(canvas.hasPointerCapture(e.pointerId))canvas.releasePointerCapture(e.pointerId);
  const o=current();if(o){const {x,y}=d.position;move(o,{x,y});}else refresh();
});
canvas.addEventListener('pointercancel',()=>{s.drag=null;canvas.classList.remove('dragging');refresh();});
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'&&s.tool){cancel();refresh();return;}
  if(e.target.closest('input,textarea,select,[contenteditable],dialog'))return;
  const k=e.key.toLowerCase();if((e.ctrlKey||e.metaKey)&&k==='z'){e.preventDefault();e.shiftKey?redo():undo();return;}
  if((e.ctrlKey||e.metaKey)&&k==='y'){e.preventDefault();redo();return;}
  const o=current();if(!o||s.mode!=='plan'||s.compare||s.page!=='atelier')return;
  if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();remove(o);return;}
  const v={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[e.key];
  if(v){e.preventDefault();const n=e.shiftKey?1:s.snap?8:1;move(o,{x:o.x+v[0]*n,y:o.y+v[1]*n});}
});

function download(blob,name){
  const ref=URL.createObjectURL(blob),link=make('a');link.href=ref;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(ref),2500);
}
const jsonBlob=(o,pretty)=>new Blob([JSON.stringify(o,null,pretty)+'\n'],{type:'application/json'});
function prepareExport(){
  $('export-note').textContent='Le jeu n’est jamais modifié par le navigateur. Ouvre ce HTML directement si l’aperçu intégré bloque un téléchargement.';
  $('download-ground').querySelector('small').textContent=s.page==='atelier'?'Copie native sans verdure, avec les meubles posés.':'Ouvre une salle pour exporter sa carte.';
  $('download-png').querySelector('small').textContent=s.page==='atelier'?(s.room.label+' · ambiance et cadrage actuels'):'Ouvre une salle pour exporter son image.';
  $('export-box').showModal();
}
async function exportPng(){
  const r=s.room,i=s.phase,v=viewport(),items=[...dataFor()];const bits=[...r.m[i],...items.map(o=>sprite(assets.get(o.meuble),i,r))];
  const ok=await Promise.all(bits.map(b=>picture(b).promise));if(ok.includes(false))throw new Error('Image non disponible.');
  const out=make('canvas');resize(out,v.w,v.h);drawScene(out.getContext('2d'),r,i,v,{items});
  const b=await new Promise(resolve=>out.toBlob(resolve,'image/png'));if(!b)throw new Error('Export PNG non pris en charge.');
  download(b,r.id+'-'+data.phases[i]+(s.mode==='plan'?'':'-sud')+'.png');
}
function appendDecoration(input,addition,existing){
  const fields=[...input.matchAll(/"Decorations"\s*:\s*\[/g)];
  if(fields.length!==1)throw new Error('Calque de décor natif introuvable.');
  const hit=fields[0],begin=hit.index+hit[0].length-1;
  let depth=0,quoted=false,escaped=false;
  for(let i=begin;i<input.length;i++){
    const c=input[i];
    if(quoted){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c==='"')quoted=false;continue;}
    if(c==='"'){quoted=true;continue;}
    if(c==='['){depth++;continue;}
    if(c===']'&&--depth===0){
      let end=i;while(end>begin+1&&/\s/.test(input[end-1]))end--;
      const join=(existing?',':'')+(input.includes('\r\n')?'\r\n':'\n')+'        ';
      return input.slice(0,end)+join+JSON.stringify(addition)+input.slice(end);
    }
  }
  throw new Error('Le tableau de décor natif est incomplet.');
}
async function exportGround(file){
  const r=s.room,items=[...dataFor()];if(s.page!=='atelier')throw new Error('Ouvre une salle pour exporter sa carte.');
  const name=r.id+'.rsground';
  if(file.name!==name||file.size>12*1024*1024)throw new Error('Choisis la carte d’origine : '+name+'.');
  if(!globalThis.crypto?.subtle)throw new Error('Ouvre le HTML directement dans un navigateur récent pour vérifier la carte locale.');
  const raw=await file.arrayBuffer();const a=new Uint8Array(await crypto.subtle.digest('SHA-256',raw));
  if(Array.from(a,b=>b.toString(16).padStart(2,'0')).join('')!==r.sha256)throw new Error('Ce fichier n’est pas la carte Windows 0.7.7 d’origine. Sélectionne ta copie de sauvegarde intacte.');
  const original=new TextDecoder('utf-8',{ignoreBOM:true,fatal:true}).decode(raw);
  const g=JSON.parse(original.replace(/^\uFEFF/,'')),meta=g.Object;
  if(meta?.AssetName!==r.id||g.Version!==r.version||!Array.isArray(meta.Decorations))throw new Error('Carte incompatible.');
  // Disable only the original vegetation layer. Do not reserialize the map or its 64-bit state.
  const foliage=/("Name"\s*:\s*"04 verdure separee"\s*,\s*"Layer"\s*:\s*0\s*,\s*"Visible"\s*:\s*)true/g;
  if(!Array.isArray(meta.Layers)||meta.Layers.filter(t=>t.Name==='04 verdure separee'&&t.Visible===true).length!==1||[...original.matchAll(foliage)].length!==1) throw new Error('Calque de verdure natif introuvable.');
  const clean=original.replace(foliage,'$1false');
  // Native, non-collidable decoration layer. Keep every tile, entity and trigger byte-value intact.
  const Anims=items.map(o=>{const a=assets.get(o.meuble),q=why(r,a,o.x,o.y);if(q)throw new Error(q);return {ObjectAnim:{'$type':'RogueEssence.Content.ObjAnimData, RogueEssence',AnimIndex:a.sheet,FrameTime:60,StartFrame:-1,EndFrame:-1,AnimDir:0,Alpha:255,AnimFlip:0},MapLoc:{X:o.x,Y:o.y}};});
  const output=items.length?appendDecoration(clean,{Name:'AtelierMobilierPMU',Layer:4,Visible:true,Anims},meta.Decorations.length>0):clean;
  // Do not stringify the whole map: the native RNG includes unsigned 64-bit integers.
  download(new Blob([output],{type:'application/json'}),name);
  $('export-note').textContent='Copie sans verdure prête. Sauvegarde ta carte originale et ferme Destiny avant tout remplacement. Si tu veux le cadrage, installe-le avant de changer la carte. Le mobilier reste décoratif et traversable.';
}

/*@GALERIE@*/

try{const old=localStorage.getItem(STORE);if(old)layout=parseLayout(JSON.parse(old));}catch{saveAvailable=false;}
for(const [i,label] of groups.entries()){
  $('rooms').append(make('h3','',label));const opt=make('optgroup');opt.label=label;$('room-select').append(opt);
  for(const r of data.rooms.filter(r=>r.group===i)){
    const b=button('room-button','',()=>selectRoom(r.id));b.dataset.room=r.id;const c=make('span','room-count');b.append(make('span','n',String(r.n).padStart(2,'0')),make('span','room-label',r.label),c);$('rooms').append(b);roomButtons.push([b,r,c]);
    const o=make('option','',r.label);o.value=r.id;opt.append(o);
  }
}
$('room-select').onchange=e=>selectRoom(e.target.value);
for(const [i,p] of phases.entries()){
  const b=button('phase-choice',p.name,()=>setPhase(i),p.icon);b.dataset.phase=String(i);if(p.title)b.title=p.title;b.style.setProperty('--tone',p.tone);b.style.setProperty('--tint',p.tint);$('phases').append(b);phaseButtons.push(b);
  const card=button('comparison','',()=>setPhase(i));card.setAttribute('aria-label','Agrandir : '+p.name);card.style.setProperty('--tone',p.tone);
  const title=make('div','strip');title.append(svg(p.icon),make('span','',p.name),make('span','','Ouvrir ↗'));const c=make('canvas');card.append(title,c);$('compare-view').append(card);comparison.push(c);
}
for(const [id,label] of cats){const b=button('',label,()=>{s.category=id;updatePalette();refresh();});$('filters').append(b);filterButtons.push([id,b]);}
$('query').addEventListener('input',updatePalette);
$('compare').onclick=()=>{s.compare=!s.compare;s.ghost=null;s.drag=null;refresh();};
$('plan').onclick=()=>{s.mode='plan';s.before=false;s.ghost=null;refresh();};
$('camera').onclick=()=>{cancel();s.mode='cadre';s.before=false;s.selected=null;refresh();};
$('before').onclick=()=>{s.before=!s.before;refresh();};
$('gates').onclick=()=>{s.gates=!s.gates;refresh();};
$('grid').onclick=()=>{s.grid=!s.grid;refresh();};
$('zoom').onchange=()=>refresh();$('snap').onchange=e=>{s.snap=e.target.checked;s.ghost=null;refresh();};
$('undo').onclick=undo;$('redo').onclick=redo;
$('help').onclick=()=>$('help-box').showModal();$('export').onclick=prepareExport;
for(const b of document.querySelectorAll('.close-dialog'))b.onclick=()=>b.closest('dialog').close();
$('import').onclick=()=>$('layout-file').click();
$('layout-file').onchange=async e=>{
  const f=e.target.files[0];e.target.value='';if(!f)return;
  try{if(f.size>1024*1024)throw new Error('Fichier trop volumineux (maximum 1 Mo).');const d=parseLayout(JSON.parse(await f.text()));s.selected=null;cancel();remember(d);toast('Plan ouvert. Tu peux annuler l’import.');}
  catch(err){toast(err instanceof SyntaxError?'Le fichier JSON n’a pas pu être lu.':err.message,true);}
};
$('download-plan').onclick=()=>download(jsonBlob(payload(),2),'Mon-plan-PMU-Destiny-077.json');
$('download-png').onclick=()=>exportPng().catch(e=>{ $('export-note').textContent=e.message; });
$('download-ground').onclick=()=>$('ground-file').click();
$('ground-file').onchange=async e=>{
  const f=e.target.files[0];e.target.value='';if(!f)return;
  try{await exportGround(f);}catch(err){$('export-note').textContent=err.message;}
};
setupAtlas();updatePalette();refresh();
})();
