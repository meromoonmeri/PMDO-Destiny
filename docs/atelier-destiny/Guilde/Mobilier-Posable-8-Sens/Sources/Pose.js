'use strict';
(() => {
const B=window.DESTINY_POSE,$=id=>document.getElementById(id), cv=$('map'), ctx=cv.getContext('2d'), S=$('sprite'),sx=S.getContext('2d');
const KEY='destiny:atelier-pose-8:v1', U='guilde_destiny_', FIRST=U+'cuisine', ARENA='table-vide', NB=12;
const by=new Map(B.ob.map(a=>[a.id,a])),alias=new Map(B.ob.flatMap(a=>a.alias.map(x=>[x,a.id]))), rooms=new Map(B.rooms.map(r=>[r.id,r]));
rooms.set(ARENA,{id:ARENA,nom:'Plateau d’essai',w:648,h:488,sol:Array(61).fill('1'.repeat(81)),seuils:[],images:[]});
const saved=(()=>{try{return JSON.parse(localStorage.getItem(KEY)||'null')}catch{return null}})();
let sel='comptoir-u',rid=FIRST,pp=0,direction=0,mirror=false,items={},focus=null,placing=false,grid=false,page=0,mouse=null,drag=null,serial=0,dirty=true;
const glyph=['↓','↘','→','↗','↑','↖','←','↙'];const names=['Face','Avant droit','Profil droit','Arrière droit','Dos','Arrière gauche','Profil gauche','Avant gauche'];
const tilt=[['3','2'],['3','3'],['2','3'],['1','3'],['1','2'],['1','1'],['2','1'],['3','1']];let dirs=[];
const safeText=(e,t)=>{e.textContent=t;};const norm=s=>String(s).toLowerCase().normalize('NFD').replace(/\p{Mark}/gu,'');
const mk=(tag,t,cl)=>{const e=document.createElement(tag);if(t)e.textContent=t;if(cl)e.className=cl;return e;};
const pages=new Map(),imgs=new Map(),pending=new Map();
const still=matchMedia('(prefers-reduced-motion: reduce)').matches;
function iid(){return `p${Date.now().toString(36)}${(serial++).toString(36)}`;}
function keep(){try{localStorage.setItem(KEY,JSON.stringify({v:1,rid,pp,items,sel}))}catch{}}
function fresh(){return items[rid]??(items[rid]=[]);}
function one(){return fresh().find(a=>a.uid===focus)||null;}
function selected(){return by.get(one()?.id||sel)||B.ob[0];}
function active(){return rooms.get(rid);}
function error(o,r=active()){
  const ob=by.get(o.id);if(!ob)return 'Objet inconnu';const f=ob.v[o.d];if(!f)return 'Orientation inconnue';
  const x=o.x-(o.m?(f[3]-f[5]):f[5]),y=o.y-f[6];
  if(x<0||y<0||x+f[3]>r.w||y+f[4]>r.h)return 'Trop près du bord.';
  for(const g of r.seuils){const [l,t,w,h]=g.rect;if(o.x>=l-11&&o.x<=l+w+11&&o.y>=t-10&&o.y<=t+h+10)return 'Ce seuil doit rester libre.';}
  const cell=r.sol[Math.floor(o.y/8)]?.[Math.floor(o.x/8)];if(cell!=='1'&&!(ob.mur&&cell==='2'))return 'Place le pivot sur le sol ou le mur autorisé.';
  return '';
}
function filestring(file,body){const q=document.createElement('script');q.src=body;q.onerror=()=>status('Impossible de lire '+file+'. Décompresse le ZIP en entier.');document.head.append(q);}
function picture(src){
  if(!src)return null;if(imgs.has(src))return imgs.get(src);
  const im=new Image();imgs.set(src,im);im.addEventListener('load',()=>{dirty=true;catalogWait();},{once:true});im.src=src;return im;
}
window.bankPage=(n,src)=>{const im=picture(src);pages.set(n,im);pending.delete(n);dirty=true;};
function pageImage(n){if(!pages.has(n)&&!pending.has(n)){pending.set(n,1);filestring('la page '+n,B.pages[n].file)}return pages.get(n);}
function ready(im){return !!(im&&im.complete&&im.naturalWidth);}
function pose(ob,ii,time=0){const a=ob.anim?.[ii];return a&&!still&&time>0?a[1][Math.floor(time/a[0])%a[1].length]:ob.v[ii];}
function drawTo(c,f,x,y,m,scale=1){const [pg,l,t,w,h,px,py]=f,img=pageImage(pg);if(!ready(img))return false;c.save();c.translate(Math.round(x),Math.round(y));c.scale(m?-scale:scale,scale);c.imageSmoothingEnabled=false;c.drawImage(img,l,t,w,h,-px,-py,w,h);c.restore();return true;}
function face(f,m){return f[3]+'×'+f[4]+' · pivot '+(m?(f[3]-f[5]):f[5])+', '+f[6];}
function pstar(ct,x,y,c){ct.save();ct.lineWidth=1;ct.strokeStyle=c;ct.beginPath();ct.moveTo(x-8,y+.5);ct.lineTo(x+8,y+.5);ct.moveTo(x+.5,y-7);ct.lineTo(x+.5,y+7);ct.stroke();ct.fillStyle=c;ct.fillRect(x-2,y-2,4,4);ct.restore();}
function indicator(c,v,chosen=false){const f=by.get(v.id).v[v.d],x=v.x-(v.m?(f[3]-f[5]):f[5]),y=v.y-f[6];c.save();c.strokeStyle=chosen?'#f5d092':'#acf1b9';c.setLineDash([2,3]);c.lineWidth=.9;c.strokeRect(x+.5,y+.5,f[3],f[4]);c.restore();pstar(c,v.x,v.y,chosen?'#fcda9e':'#d3f5b0');}
function resize(){const r=active();if(cv.width!==r.w||cv.height!==r.h){cv.width=r.w;cv.height=r.h;}cv.style.aspectRatio=`${r.w} / ${r.h}`;cv.style.maxWidth=Math.min(975,r.w*2.0,Math.floor(650*r.w/r.h))+'px';ctx.imageSmoothingEnabled=false;cv.dataset.salle=rid;}
function platform(c,r){c.fillStyle='#262821';c.fillRect(0,0,r.w,r.h);for(let y=0;y<r.h;y+=8)for(let x=0;x<r.w;x+=48){c.fillStyle=(Math.floor(x/48)+Math.floor(y/8))%2?'#9a6c45':'#906441';c.fillRect(x+1,y+1,47,7);c.fillStyle='#b08250';c.fillRect(x+1,y+1,43,1);}}
function architecture(c,r,time){
  const f=r.foyers;if(!f)return;const t=Math.floor(Math.max(0,time)/100)%4;
  let q=[f.ombre,f.reflets[t]];q.forEach(([x,y,b],i)=>{const im=picture(b);if(!ready(im))return;c.save();if(i){c.globalCompositeOperation='screen';c.globalAlpha=pp?1:.62;}c.drawImage(im,x,y);c.restore();});
  for(const [i,v] of f.modules.entries()){const [x,y,w,h,j,n]=v,im=picture(pp?n:j);if(ready(im))c.drawImage(im,((t+i*2)%4)*w,0,w,h,x,y,w,h);}
}
function scene(c,time,r=active(),decor=false){
  c.clearRect(0,0,r.w,r.h);c.imageSmoothingEnabled=false;
  if(r.id===ARENA)platform(c,r);else{let img=picture(r.images[pp]);if(ready(img))c.drawImage(img,0,0);}
  architecture(c,r,time);
  for(const o of fresh().slice().sort((a,b)=>Number(by.get(b.id).plan)-Number(by.get(a.id).plan)||a.y-b.y))drawTo(c,pose(by.get(o.id),o.d,time),o.x,o.y,o.m);
  const f=picture(r.front);if(ready(f))c.drawImage(f,0,0);
  if(!decor)return;
  if(grid){c.fillStyle='#dcf1d125';for(let y=0;y<r.h;y+=8)c.fillRect(0,y,r.w,1);for(let x=0;x<r.w;x+=8)c.fillRect(x,0,1,r.h);}
  if(one())indicator(c,one(),true);
  if(mouse&&placing){const o={id:sel,d:direction,m:mirror,...mouse};c.save();c.globalAlpha=.63;drawTo(c,pose(by.get(sel),direction,0),o.x,o.y,o.m);c.restore();pstar(c,o.x,o.y,error(o)?'#ffc1ab':'#c8ffb6');}
}
function preview(time=0){const o=one(),a=selected(),i=o?.d??direction,m=o?.m??mirror;const f=pose(a,i,time);sx.clearRect(0,0,S.width,S.height);const n=Math.min(3,Math.max(.43,Math.floor(Math.min(166/f[3],101/f[4]))||.65));const x=(S.width-f[3]*n)/2+(m?f[3]-f[5]:f[5])*n;const y=(S.height-f[4]*n)/2+f[6]*n;drawTo(sx,f,x,y,m,n);pstar(sx,Math.round(x),Math.round(y),'#ecc386');}
function status(s){safeText($('status'),s);}
function update(){
  const o=one(),a=selected(),i=o?.d??direction,m=o?.m??mirror;safeText($('assetfamily'),a.famille);safeText($('assetname'),a.nom);safeText($('anchor'),face(a.v[i],m));
  safeText($('facing'),B.dirs[i]+' · '+names[i]+(m?' · miroir':''));$('mirror').setAttribute('aria-pressed',m?'true':'false');$('remove').disabled=!o;
  $('place').textContent=placing?'Cliquer dans la salle…':'Poser sur le plan';$('place').classList.toggle('awaiting',placing);
  for(const [n,b] of dirs.entries())b.setAttribute('aria-pressed',i===n?'true':'false');
  cv.dataset.items=String(fresh().length);cv.dataset.pivot=o?`${o.x},${o.y}`:'';cv.dataset.direction=B.dirs[i];cv.dataset.miroir=String(m);cv.dataset.asset=a.id;dirty=true;
}
function curr(id){sel=id;focus=null;placing=false;mouse=null;direction=0;mirror=false;update();catalogMarks();keep();}
function rotate(i){const o=one();if(o){const next={...o,d:i},e=error(next);if(e){status(e+' Déplace d’abord le pivot.');return false;}o.d=i;status(`${selected().nom} · ${B.dirs[i]} · même pivot [${o.x}, ${o.y}]`);}else{direction=i;status(`${B.dirs[i]} : pose prête.`);}update();keep();return true;}
function mir(){const o=one();if(o){const next={...o,m:!o.m},e=error(next);if(e){status(e);return false;}o.m=!o.m;status(o.m?'Miroir horizontal, pivot conservé.':'Miroir désactivé.');}else mirror=!mirror;update();keep();return true;}
function room(id){if(!rooms.has(id))return;rid=id;$('salle').value=id;safeText($('room-title'),active().nom);focus=null;placing=false;mouse=null;resize();update();keep();status('Choisis ou sélectionne un meuble.');}
function setPhase(p){pp=p;$('night').setAttribute('aria-pressed',p?'true':'false');dirty=true;keep();}
function currentFilters(){const q=norm($('query').value.trim()),fam=$('famille').value;return B.ob.filter(s=>(!fam||s.famille===fam)&&(!q||norm([s.nom,s.code,s.famille,...s.alias].join(' ')).includes(q)));}
function catalogMarks(){for(const b of $('catalog').querySelectorAll('button[data-id]'))b.setAttribute('aria-selected',b.dataset.id===sel?'true':'false');}
let reqCat=false;
function catalogWait(){if(reqCat)return;reqCat=true;requestAnimationFrame(()=>{reqCat=false;for(const c of $('catalog').querySelectorAll('canvas[data-id]')){
  const a=by.get(c.dataset.id),f=a.v[0],k=Math.min(2,60/f[3],40/f[4]),g=c.getContext('2d');g.clearRect(0,0,c.width,c.height);drawTo(g,f,(64-f[3]*k)/2+f[5]*k,(45-f[4]*k)/2+f[6]*k,false,k);
}});}
function list(){let a=currentFilters(),max=Math.max(1,Math.ceil(a.length/NB));page=Math.min(max-1,page);const b=$('catalog');b.replaceChildren();for(const o of a.slice(page*NB,(page+1)*NB)){
  const c=mk('button',null,'asset');c.type='button';c.dataset.id=o.id;c.title=o.nom+' · '+o.code;c.setAttribute('aria-label',o.nom);c.setAttribute('aria-selected',o.id===sel?'true':'false');const k=mk('canvas');k.width=64;k.height=45;k.dataset.id=o.id;c.append(k,mk('span',o.nom));c.onclick=()=>{curr(o.id);status('Prêt à poser : '+o.nom);};b.append(c);
}safeText($('page'),`${page+1} / ${max}`);safeText($('count'),`${a.length.toLocaleString('fr')} éléments`);$('prev').disabled=page===0;$('next').disabled=page>=max-1;catalogWait();}
function snap(x,y){return {x:Math.floor(x/8)*8+4,y:Math.floor(y/8)*8+4};}
function coords(e){const rect=cv.getBoundingClientRect();return {x:(e.clientX-rect.left)*cv.width/rect.width,y:(e.clientY-rect.top)*cv.height/rect.height};}
function selection(x,y){const f=fresh().slice().sort((a,b)=>Number(by.get(a.id).plan)-Number(by.get(b.id).plan)||b.y-a.y);for(const v of f){const a=by.get(v.id).v[v.d],l=v.x-(v.m?(a[3]-a[5]):a[5]),t=v.y-a[6];if(x>=l&&x<l+a[3]&&y>=t&&y<t+a[4])return v;}return null;}
function insert(x,y){const o={uid:iid(),id:sel,...snap(x,y),d:direction,m:mirror},e=error(o);if(e){status(e);return false;}if(fresh().length>=256){status('256 placements maximum par plan.');return false;}fresh().push(o);focus=o.uid;placing=false;mouse=null;status(`Posé · pivot [${o.x}, ${o.y}]. Tourne-le sans le déplacer.`);update();keep();return true;}
cv.addEventListener('pointerdown',e=>{if(e.button!==0)return;const {x,y}=coords(e);if(placing){insert(x,y);return;}const o=selection(x,y);focus=o?.uid??null;if(o){sel=o.id;direction=o.d;mirror=o.m;cv.setPointerCapture(e.pointerId);drag={uid:o.uid,dx:x-o.x,dy:y-o.y};status(`Sélection · ${selected().nom}. Déplace ou tourne.`);}update();catalogMarks();});
cv.addEventListener('pointermove',e=>{const {x,y}=coords(e);if(placing){mouse=snap(x,y);dirty=true;}if(drag){const o=fresh().find(o=>o.uid===drag.uid);if(!o)return;const z=snap(x-drag.dx,y-drag.dy);if(!error({...o,...z})){Object.assign(o,z);update();}}});
for(const key of ['pointerup','lostpointercapture','pointercancel'])cv.addEventListener(key,()=>{if(drag)keep();drag=null;});
cv.addEventListener('pointerleave',()=>{mouse=null;dirty=true;});
function remove(){const o=one();if(!o)return;items[rid]=fresh().filter(v=>v.uid!==o.uid);focus=null;status('Objet retiré du plan.');update();keep();}
function saveBlob(blob,name){if(!blob)return;const a=mk('a');a.download=name;const u=URL.createObjectURL(blob);a.href=u;a.click();setTimeout(()=>URL.revokeObjectURL(u),5000);}
async function savePNG(){const o=one(),a=selected(),i=o?.d??direction,m=o?.m??mirror,f=a.v[i];const c=mk('canvas');c.width=f[3];c.height=f[4];const pg=pageImage(f[0]);if(!ready(pg)){status('Chargement du sprite…');return;}drawTo(c.getContext('2d'),f,m?f[3]-f[5]:f[5],f[6],m);c.toBlob(b=>saveBlob(b,`${a.code}-${B.dirs[i]}${m?'-miroir':''}.png`),'image/png');}
function savePlan(){const o={v:1,rid,pp,items,sel};saveBlob(new Blob([JSON.stringify(o,null,2)],{type:'application/json'}),'Destiny-plan-de-pose.json');}
function importObj(o){
  if(!o||o.v!==1||!o.items||Array.isArray(o.items)||!rooms.has(o.rid))throw Error('Plan incorrect ou version non reconnue.');
  const M={};for(const [r,v] of Object.entries(o.items)){const mm=rooms.get(r);if(!mm||!Array.isArray(v)||v.length>256)throw Error('Salle inconnue ou trop de meubles.');M[r]=[];for(const e of v){const z={uid:iid(),id:by.has(e.id)?e.id:alias.get(e.id),d:e.d,m:!!e.m,x:e.x,y:e.y};if(!Number.isInteger(z.d)||z.d<0||z.d>7||![z.x,z.y].every(Number.isInteger)||error(z,mm))throw Error('Pose invalide dans '+mm.nom);M[r].push(z);}}
  items=M;sel=by.has(o.sel)?o.sel:'comptoir-u';room(o.rid);setPhase(o.pp===1?1:0);status('Plan restauré. Les pivots et les sens ont été conservés.');catalogMarks();
}
for(const [i,c] of glyph.entries()){const a=mk('button',c);a.type='button';a.dataset.dir=B.dirs[i];a.title=B.dirs[i]+' · '+names[i];a.setAttribute('aria-label',a.title);a.style.gridRow=tilt[i][0];a.style.gridColumn=tilt[i][1];a.onclick=()=>rotate(i);dirs.push(a);$('directions').append(a);}
$('query').oninput=$('famille').onchange=()=>{page=0;list();};$('prev').onclick=()=>{page--;list()};$('next').onclick=()=>{page++;list()};
$('salle').onchange=e=>room(e.target.value);$('night').onclick=()=>setPhase(1-pp);$('grid').onclick=()=>{grid=!grid;$('grid').setAttribute('aria-pressed',grid?'true':'false');dirty=true;};
$('rot').onclick=()=>rotate(((one()?.d??direction)+1)%8);$('mirror').onclick=mir;$('remove').onclick=remove;
$('place').onclick=()=>{if(one()){const o=one();sel=o.id;direction=o.d;mirror=o.m;focus=null;}placing=!placing;update();status(placing?'Clique sur une zone libre du plan.':'Pose annulée.');if(placing)cv.focus({preventScroll:true});};
$('png').onclick=savePNG;$('save').onclick=savePlan;$('planpng').onclick=()=>{const c=mk('canvas');c.width=cv.width;c.height=cv.height;scene(c.getContext('2d'),0);c.toBlob(b=>saveBlob(b,'Destiny-'+rid+'.png'),'image/png');};
$('load').onchange=async e=>{const f=e.target.files[0];if(!f)return;try{if(f.size>1e6)throw Error('Fichier trop grand.');importObj(JSON.parse(await f.text()));}catch(err){status(err.message);}e.target.value='';};
window.addEventListener('keydown',e=>{if(e.ctrlKey||e.altKey||e.metaKey||/INPUT|SELECT|TEXTAREA/.test(e.target.tagName))return;const k=e.key.toLowerCase();if(k==='r'||k==='m'){e.preventDefault();if(k==='r')$('rot').click();else mir();}else if(k==='escape'){placing=false;focus=null;mouse=null;update();status('Pose annulée.');}else if(k==='delete'&&one()){remove();e.preventDefault();}else if(k.startsWith('arrow')&&one()&&document.activeElement===cv){const o=one(),p={...o};p.x+=k==='arrowleft'?-8:k==='arrowright'?8:0;p.y+=k==='arrowup'?-8:k==='arrowdown'?8:0;if(!error(p)){Object.assign(o,p);update();keep();}e.preventDefault();}});
safeText($('total'),`${B.chiffres.ids.toLocaleString('fr')} éléments · 8 sens`);$('famille').append(new Option('Toutes les collections',''));for(const n of Object.keys(B.chiffres.familles).sort((a,b)=>a.localeCompare(b,'fr')))$('famille').append(new Option(n,n));for(const r of rooms.values())$('salle').append(new Option(r.nom,r.id));
room(FIRST);if(saved)try{importObj(saved);}catch{}list();update();
let last=0;function loop(time){if(dirty||(!still&&time-last>87)){last=time;dirty=false;scene(ctx,still?0:time,active(),true);preview(still?0:time);}requestAnimationFrame(loop);}requestAnimationFrame(loop);
// The local reproduction test reads the exact same canvas transforms as the controls.
window.poseTest={list:()=>B.chiffres,pose:()=>one()?{...one()}:null,exists:id=>by.has(id),scene:()=>JSON.parse(JSON.stringify({v:1,rid,pp,items,sel})),wanted:id=>{curr(by.has(id)?id:alias.get(id));},error,importObj,assets:()=>B.ob.map(a=>[a.id,a.v.length]),room:()=>({id:rid,w:cv.width,h:cv.height}),view:i=>selected().v[i],ready:()=>!pending.size};
})();
