// New atelier views. Counter assets are radial projections, not canvas rotations.
const counterData=data.comptoirs, cliffData=data.cliff;
const cfById=new Map(counterData.orientations.map(v=>[v.id,v]));
const cfDemo={asset:counterData.orientations[0].id,room:Object.keys(counterData.exemples)[0],access:false};
const clipped={layers:true};
const cfOrientButtons=[],cfPhaseButtons=[];
const cfPlan=$('cf-plan'),cliffMap=$('cliff-map');
const cfAsset=()=>assets.get(cfDemo.asset);
const anchored=(a,p)=>[p[0]+a.pivot[0],p[1]+a.pivot[1]];
const atRect=(x,y,b,pad=0)=>x>=b[0]-pad&&y>=b[1]-pad&&x<b[0]+b[2]+pad&&y<b[1]+b[3]+pad;
const tileNum=(x,y,r)=>Math.floor(y/8)*r.floor[0].length+Math.floor(x/8);
const tilesFor=(a,k,x,y,r)=>new Set(a[k].map(([u,v])=>tileNum(x+u,y+v,r)));
const share=(a,b)=>[...a].some(n=>b.has(n));
function feetOf(o,r){
  const a=assets.get(o.meuble),v=cfById.get(o.meuble);if(!a||a.wall||a.category==='tapis')return new Set();
  if(v)return tilesFor(v,'empreinte',o.x,o.y,r);
  const q=new Set(),row=o.y+a.h-5;
  for(let x=Math.round(a.w*.25);x<=Math.ceil(a.w*.75);x+=5)q.add(tileNum(o.x+x,row,r));
  q.add(tileNum(o.x+a.w*.5,row,r));return q;
}
function routesCourtes(r,blocked){
  const groups=counterData.routes[r.id];if(!groups.length)return true;
  const rowN=r.floor.length,line=r.floor[0].length,length=rowN*line,mask=new Uint8Array(length),queue=new Int32Array(length);
  for(let y=0;y<rowN;y++)for(let x=0;x<line;x++)if(r.floor[y][x]==='1')mask[y*line+x]=1;
  for(const k of blocked){const x=k%line,y=(k-x)/line;for(const [dx,dy] of [[0,0],[1,0],[-1,0],[0,1],[0,-1]])if(x+dx>=0&&x+dx<line&&y+dy>=0&&y+dy<rowN)mask[k+dx+line*dy]=0;}
  for(const group of groups){
    const id=group.map(([x,y])=>x+y*line);if(id.some(k=>mask[k]===0))return false;
    const visited=new Uint8Array(length);let first=0,last=1,rest=new Set(id.slice(1));queue[0]=id[0];visited[id[0]]=1;
    while(first<last&&rest.size){
      const k=queue[first++],x=k%line;
      for(const n of [x>0?k-1:-1,x<line-1?k+1:-1,k-line,k+line])if(n>=0&&n<length&&mask[n]&&!visited[n]){
        queue[last++]=n;visited[n]=1;rest.delete(n);
      }
    }
    if(rest.size)return false;
  }
  return true;
}
function whyCounters(r,a,x,y,ignore,items){
  const current=cfById.get(a.id),other=items.filter(o=>o.id!==ignore),others=other.filter(o=>cfById.has(o.meuble));
  if(!current){
    if(!others.length||a.category==='tapis'||a.wall)return '';
    const foot=feetOf({meuble:a.id,x,y},r);
    if(others.some(o=>{const v=cfById.get(o.meuble);return ['empreinte','allée'].some(k=>share(foot,tilesFor(v,k,o.x,o.y,r)));}))return 'Garde le comptoir et son allée libres.';
    return '';
  }
  const routes=counterData.axes[r.id]||[],entry=[...r.gates.map(q=>q.rect),...r.mark];
  for(const k of ['empreinte','allée']){
    for(const [u,v] of current[k]){
      const X=x+u,Y=y+v;
      if(r.floor[Math.floor(Y/8)]?.[Math.floor(X/8)]!=='1')return k==='empreinte'?'Tout le pied du comptoir doit tenir sur le sol.':'Laisse une allée libre sur la longueur du comptoir.';
      if(routes.some(b=>atRect(X,Y,b))||(k==='empreinte'&&entry.some(b=>atRect(X,Y,b,8))))return 'Laisse libre l’allée des passages et des arrivées.';
    }
  }
  const inner=tilesFor(current,'empreinte',x,y,r), aisle=tilesFor(current,'allée',x,y,r), blocked=new Set(inner);
  for(const o of other){
    const old=feetOf(o,r),v=cfById.get(o.meuble);
    if(share(inner,old)||share(aisle,old)||(v&&share(inner,tilesFor(v,'allée',o.x,o.y,r))))return 'Ce meuble empiète sur l’empreinte ou l’allée d’un comptoir.';
    if(v)for(const n of old)blocked.add(n);
  }
  return routesCourtes(r,blocked)?'':'Ce comptoir coupe un chemin entre deux passages.';
}
function cfUpdate(){
  $('cf-page').hidden=s.page!=='comptoirs';$('cliff-page').hidden=s.page!=='cliff';
  for(const [i,b] of cfPhaseButtons)b.setAttribute('aria-pressed',String(i===s.phase));
  if(s.page==='comptoirs'){
    const v=cfById.get(cfDemo.asset),r=gameMap.get(cfDemo.room);
    for(const [key,b] of cfOrientButtons)b.setAttribute('aria-pressed',String(key===v.id));
    $('cf-pose-caption').textContent=v.nom+' / '+v.direction;
    $('cf-size').textContent=`${v.w} × ${v.h} PX · NOYER / PIERRE`;
    $('cf-room-label').textContent=r.label;
    $('cf-show-access').setAttribute('aria-pressed',String(cfDemo.access));
    $('cf-show-access').lastChild.textContent=cfDemo.access?' Masquer les seuils':' Montrer les seuils';
    cfPlan.setAttribute('aria-label',`${v.nom} : exemple de pose dans la salle ${r.label}, ambiance ${phases[s.phase].name}`);
  }
  if(s.page==='cliff'){
    $('cliff-light').textContent=phases[s.phase].name;
    $('cliff-state').textContent=!clipped.layers?'Falaise sans ajout':s.phase===3?'Deux braseros allumés':'Deux braseros éteints';
    $('cliff-toggle').setAttribute('aria-pressed',String(clipped.layers));
    $('cliff-toggle').textContent=clipped.layers?'Avec braseros':'Sans braseros';
    cliffMap.setAttribute('aria-label',`Falaise de Destiny. ${$('cliff-light').textContent} · ${$('cliff-state').textContent}.`);
  }
}
function showCounter(){
  const r=gameMap.get(cfDemo.room),q=counterData.exemples[r.id][cfDemo.asset];resize(cfPlan,r.w,r.h);
  drawScene(cfPlan.getContext('2d'),r,s.phase,planVue(r),{items:[{id:'cf-demonstration',meuble:cfDemo.asset,x:q[0],y:q[1]}],gates:cfDemo.access});
}
function cfSelectForEditor(){
  const a=cfAsset();editorBank('comptoirs','tout');s.category='tout';$('query').value='';updatePalette();
  openDepuisAtlas(gameMap.get(cfDemo.room));activateTool(a);
}
function cfChooseOrientation(panel,o,a){
  const own=cfById.get(a.id);if(!own)return;
  const wrap=make('label','cf-orientation','Orientation du comptoir');const control=make('select');control.id='cf-orientation';
  control.append(...counterData.orientations.map(v=>new Option(`${v.flèche} ${v.nom} · ${v.direction}`,v.id)));control.value=a.id;
  control.onchange=()=>{
    if(!o){s.tool=control.value;s.ghost=null;refresh();$('cf-orientation')?.focus();return;}
    const next=cfById.get(control.value),[px,py]=anchored(own,[o.x,o.y]);
    const x=px-next.pivot[0],y=py-next.pivot[1],issue=why(s.room,assets.get(next.id),x,y,o.id);
    if(issue){control.value=o.meuble;toast(issue,true);return;}
    setRoomItems(dataFor().map(t=>t.id===o.id?{...o,meuble:next.id,x,y}:t));$('cf-orientation')?.focus();
  };
  wrap.append(control);panel.append(wrap);
  if(!o){const q=counterData.exemples[s.room.id]?.[a.id];if(q)panel.append(button('soft','Poser comme dans l’exemple',()=>place(a,{x:q[0],y:q[1]}),'target'));}
}
function openCliff(night=false){
  if(night)s.phase=3;s.compare=false;changePage('cliff');window.scrollTo({top:0,behavior:'auto'});$('cliff-title').focus({preventScroll:true});
}
function fromCliff(){openDepuisAtlas(gameMap.get(cliffData.accueil));}
function cliffFrame(p,withL=clipped.layers,ms=clock.ms){
  const f=p===3?Math.floor(ms*cliffData.fps/1000)%4:0;
  const sea=p===3?Math.floor(ms*cliffData.mer.fps/1000)%cliffData.mer.frames:0;
  return {p,f,sea,overlay:withL?cliffData.calques[p][f]:null,code:`cliff:${p}:${sea}:${withL?f:'nu'}`};
}
function cliffBits(q){return [cliffData.bases[q.p],...(q.p===3?[cliffData.mer.png]:[]),...(q.overlay?[q.overlay[2]]:[])];}
function drawCliff(c,q){
  c.imageSmoothingEnabled=false;c.clearRect(0,0,480,520);c.fillStyle='#151934';c.fillRect(0,0,480,520);drawPicture(c,cliffData.bases[q.p],0,0);
  if(q.p===3&&q.sea){const b=picture(cliffData.mer.png),[x,y,w,h]=cliffData.mer.rect;if(b.ready)c.drawImage(b.pic,(q.sea%2)*w,Math.floor(q.sea/2)*h,w,h,x,y,w,h);}
  if(q.overlay){const [x,y,z]=q.overlay;drawPicture(c,z,x,y);}
  c.canvas.dataset.scene=cliffBits(q).every(s=>picture(s).ready)?q.code:'';
  c.canvas.dataset.flamme=q.p===3&&q.overlay?String(q.f):'éteinte';
}
function paintCliff(){drawCliff(cliffMap.getContext('2d'),cliffFrame(s.phase));}
async function cliffReference(){
  if($('destiny-foyers').src)return;
  const q=cliffFrame(3,true,0),c=make('canvas');resize(c,480,520);
  const ok=await Promise.all(cliffBits(q).map(b=>picture(b).promise));if(ok.includes(false))throw new Error('L’image de comparaison est indisponible.');
  drawCliff(c.getContext('2d'),q);$('destiny-foyers').src=c.toDataURL('image/png');
}
async function cliffPNG(){
  const q=cliffFrame(s.phase);const ok=await Promise.all(cliffBits(q).map(b=>picture(b).promise));if(ok.includes(false))throw new Error('L’image de la falaise est indisponible.');
  const c=make('canvas');resize(c,480,520);drawCliff(c.getContext('2d'),q);
  const b=await new Promise(resolve=>c.toBlob(resolve,'image/png'));if(!b)throw new Error('Export PNG non pris en charge.');
  download(b,`Cliff-Destiny-${data.phases[q.p]}${q.overlay?'-braseros':''}.png`);
}
function setupCF(){
  for(const v of counterData.orientations){
    const a=assets.get(v.id),b=button('cf-direction',null,()=>{cfDemo.asset=v.id;refresh();});
    b.dataset.dir=v.direction;b.title=v.nom+' · '+v.direction;b.setAttribute('aria-label',b.title);
    const sign=make('span','cf-track',v.flèche);sign.setAttribute('aria-hidden','true');const im=make('img');im.src=uri(a.m[0]);im.alt='';
    const thumb=make('span','cf-thumb');thumb.append(im);b.append(sign,thumb,make('strong','',v.direction));$('cf-directions').append(b);cfOrientButtons.push([v.id,b]);
  }
  const room=$('cf-room');room.append(...Object.keys(counterData.exemples).map(n=>new Option(gameMap.get(n).label,n)));room.value=cfDemo.room;
  room.onchange=()=>{cfDemo.room=room.value;refresh();};
  for(const id of ['cf-phases','cliff-phases'])for(const [i,p] of phases.entries()){
    const b=button('cf-button',p.name,()=>setPhase(i),i===3?'moon':null);b.dataset.cfPhase=String(i);cfPhaseButtons.push([i,b]);$(id).append(b);
  }
  $('cf-png').onclick=()=>{const a=cfAsset(),v=cfById.get(a.id);const bytes=Uint8Array.from(atob(a.m[0].split(',').at(-1)),c=>c.charCodeAt(0));download(new Blob([bytes],{type:'image/png'}),`Comptoir-Destiny-${v.direction}.png`);};
  $('cf-try').onclick=cfSelectForEditor;$('cf-show-access').onclick=()=>{cfDemo.access=!cfDemo.access;refresh();};
  $('cf-go-night').onclick=()=>openCliff(true);$('tab-cliff').onclick=()=>openCliff();$('cliff-return').onclick=fromCliff;$('cliff-door').onclick=fromCliff;
  $('cliff-toggle').onclick=()=>{clipped.layers=!clipped.layers;refresh();};$('cliff-save').onclick=()=>cliffPNG().catch(e=>toast(e.message,true));
  $('cliff-west').src=uri(cliffData.details[0]);$('cliff-east').src=uri(cliffData.details[1]);
  const exit=cliffData.porte; // Real collider centres the interactive doorway hit area.
  $('cliff-door').style.left=`${100*(exit[0]-15)/480}%`;
  $('cliff-door').style.width=`${100*(exit[2]+30)/480}%`;
}
