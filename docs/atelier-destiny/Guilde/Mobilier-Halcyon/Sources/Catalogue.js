// Tables d'atelier et pose : jamais de mutation des cartes Destiny.
const halData=data.halcyon;
const halById=new Map(halData.modele.map(m=>[m.id,m]));
const halTones=new Map(halData.palettes.map(p=>[p.id,p]));
const halState={palette:'lierre',origine:'guilde',family:'',q:'',page:0,model:'banquet',original:false,room:halData.demo.salle};
const halOrigins=[['guilde','Guilde de Halcyon'],['metano','Auberge de Metano'],['toutes','Tout voir']];
const halRoomNames=halData.cartes;
const HAL_LIMIT=12;
const halAsset=(m,p=halState.palette)=>assets.get('halcyon-'+m.id+'-'+p);
const isHalcyon=a=>!!a?.halcyon;

const oldTones=[['miel','Chêne & miel'],['grenat','Noyer & grenat'],['sauge','Châtaigne & sauge'],['ardoise','Bois fumé & ardoise']];
function editorBank(collection,palette){
  const el=$('palette-pmu');
  const hal=['halcyon','metano'].includes(collection);
  const source=hal?[...halTones.values()].map(p=>[p.id,p.nom]):oldTones;
  s.collection=collection;s.palette=palette??(hal?'lierre':'tout');$('collection').value=collection;
  el.replaceChildren(new Option('Toutes les palettes','tout'),...source.map(([id,n])=>new Option(n,id)));
  el.value=s.palette;el.disabled=collection==='origine';
  $('editor-bank-name').textContent=hal?(collection==='halcyon'?'Mobilier Halcyon':'Auberge de Metano'):'Mobilier PMU';
}
function halRecolor(panel,o){
  const a=assets.get(o.meuble);if(!isHalcyon(a))return;
  const wrap=make('label','hal-recolor','Changer la teinte sans déplacer');
  const select=make('select');select.id='hal-recolor';select.setAttribute('aria-label','Teinte du meuble sélectionné');
  select.append(...halData.palettes.map(p=>new Option(p.nom,p.id)));select.value=a.palette;
  select.onchange=()=>{const next=halAsset(halById.get(a.halcyon),select.value);if(next.id===o.meuble)return;
    setRoomItems(dataFor().map(i=>i.id===o.id?{...i,meuble:next.id}:i));$('hal-recolor')?.focus({preventScroll:true});};
  wrap.append(select);panel.append(wrap);
}
function halImg(a,src=a.m[0],scl=2){
  const im=make('img');im.alt='';im.src=uri(src);im.width=a.w*scl;im.height=a.h*scl;return im;
}
function halThumb(a,name){
  const cover=make('span',name);cover.append(halImg(a));return cover;
}
function halPick(p){
  halState.palette=p;halState.original=false;halRender();
}
function halSelect(model){
  halState.model=model;halState.original=false;halMarkCards();halDetail();
  if(matchMedia('(max-width:640px)').matches){$('hal-detail-name').focus({preventScroll:true});$('hal-detail').scrollIntoView({block:'start',behavior:'auto'});}
}
function halMarkCards(){
  for(const b of $('hal-grid').querySelectorAll('[data-model]'))b.setAttribute('aria-pressed',String(b.dataset.model===halState.model));
}
function halFilter(){
  const term=normalized(halState.q);
  return halData.modele.filter(m=>(halState.origine==='toutes'||m.origine===halState.origine)
    &&(!halState.family||halState.family===m.famille)
    &&(!term||term.split(/\s+/).every(t=>normalized(m.nom+' '+m.famille+' '+halRoomNames[m.salle]).includes(t))));
}
function halReset(){
  halState.family='';halState.page=0;halState.q='';halState.origine='toutes';$('hal-family').value='';$('hal-search').value='';halRender();
}
function halRender(){
  const found=halFilter();const pages=Math.max(1,Math.ceil(found.length/HAL_LIMIT));halState.page=Math.min(halState.page,pages-1);
  const list=found.slice(halState.page*HAL_LIMIT,(halState.page+1)*HAL_LIMIT);
  if(!list.some(m=>m.id===halState.model)){halState.model=list[0]?.id;halState.original=false;}
  const tone=halTones.get(halState.palette);$('hal-note-tone').textContent=tone.accord;
  $('hal-scene-tone').textContent=tone.nom;
  $('hal-count').textContent=`${found.length} modèle${found.length===1?'':'s'} · palette ${tone.nom}`;
  $('hal-paging-top').textContent=found.length?`${halState.page*HAL_LIMIT+1}–${halState.page*HAL_LIMIT+list.length} / ${found.length}`:'';
  $('hal-page-number').textContent='Page '+(halState.page+1)+' / '+pages;
  $('hal-prev').disabled=!halState.page;$('hal-next').disabled=halState.page+1>=pages;
  $('hal-paging').hidden=pages<2;
  for(const b of $('hal-swatches').children)b.setAttribute('aria-pressed',String(b.dataset.tone===halState.palette));
  for(const b of $('hal-origins').children)b.setAttribute('aria-pressed',String(b.dataset.origin===halState.origine));
  const grid=$('hal-grid');grid.replaceChildren();
  for(const m of list){
    const a=halAsset(m),c=button('hal-card',null,()=>halSelect(m.id));c.dataset.model=m.id;
    c.setAttribute('aria-label',m.nom+' · '+tone.nom);
    const body=make('span','hal-card-copy');body.append(make('b','',m.nom),make('small','',m.origine==='metano'?'Auberge · '+m.famille:m.famille));
    c.append(halThumb(a,'hal-thumb'),body);grid.append(c);
  }
  if(!list.length){const empty=make('div','hal-empty');empty.append(make('p','','Aucun objet ne correspond à ces filtres.'),button('hal-outline','Effacer les filtres',halReset));grid.append(empty);}
  halMarkCards();halDetail();invalidate();
}
function halDetail(){
  const m=halById.get(halState.model);$('hal-detail').hidden=!m;if(!m)return;
  const a=halAsset(m);const image=$('hal-detail-image');image.src=uri(halState.original?m.png:a.m[0]);image.width=a.w*2;image.height=a.h*2;image.alt=m.nom+' · '+(halState.original?'original Halcyon':halTones.get(a.palette).nom);
  $('hal-size').textContent=a.w+' × '+a.h+' px';$('hal-detail-name').textContent=m.nom;
  $('hal-detail-provenance').textContent=halRoomNames[m.salle]+' · '+(m.origine==='metano'?'Auberge':'Guilde');
  $('hal-detail-palette').textContent=halState.original?'Couleurs originales':halTones.get(a.palette).nom;
  $('hal-original').setAttribute('aria-pressed',String(halState.original));$('hal-original').textContent=halState.original?'Revenir à la variante':'Voir l’original';
  const element=$('hal-choices'),focused=document.activeElement?.dataset?.mini;element.replaceChildren();
  for(const p of halData.palettes){const v=halAsset(m,p.id);
    const b=button('hal-mini',null,()=>halPick(p.id));b.dataset.mini=p.id;b.title=p.nom;b.setAttribute('aria-label','Voir la teinte '+p.nom);
    b.setAttribute('aria-pressed',String(!halState.original&&p.id===halState.palette));b.append(halImg(v,v.m[0],1));element.append(b);
  }
  if(focused)element.querySelector(`[data-mini="${focused}"]`)?.focus({preventScroll:true});
  $('hal-source').href=halData.repo+'/blob/'+halData.commit+'/Data/Ground/'+m.salle+'.rsground';
}
function halDemoItems(){
  return halData.demo.pose.map(([id,x,y])=>({id:'etude-'+id,meuble:halAsset(halById.get(id)).id,x,y}));
}
function halPaint(){
  const r=gameMap.get(halData.demo.salle),cv=$('hal-scene'),v=halData.demo.zone;
  drawScene(cv.getContext('2d'),r,s.phase,v,{items:halDemoItems(),lianes:s.lianes,ms:clock.ms});
}
function halPhaseButtons(){
  $('hal-day').setAttribute('aria-pressed',String(s.phase!==3));$('hal-night').setAttribute('aria-pressed',String(s.phase===3));
}
async function halPNG(){
  const m=halById.get(halState.model);if(!m)return;const a=halAsset(m);
  const bytes=Uint8Array.from(atob(a.m[0].split(',').at(-1)),c=>c.charCodeAt(0));download(new Blob([bytes],{type:'image/png'}),a.id+'.png');
}
function halStartPlacing(){
  const m=halById.get(halState.model);if(!m)return;const a=halAsset(m);
  editorBank(a.collection,a.palette);s.category='tout';$('query').value='';$('catalog').scrollTop=0;updatePalette();
  openDepuisAtlas(gameMap.get(halState.room));activateTool(a);
}
function setupHalcyon(){
  const panel=$('halcyon-page');panel.style.setProperty('--hal-wood',`url("${uri(halData.bois)}")`);
  for(const p of halData.palettes){const b=button('hal-tone',null,()=>halPick(p.id));b.dataset.tone=p.id;b.title=p.usage;
    const sw=make('span','hal-sw');sw.setAttribute('aria-hidden','true');for(const c of [p.bois[2],p.tissu[3],p.metal[3]]){const i=make('i');i.style.setProperty('--sw','#'+c);sw.append(i);}
    b.append(sw,make('b','',p.nom));$('hal-swatches').append(b);}
  for(const [id,nom] of halOrigins){const len=halData.modele.filter(m=>id==='toutes'||m.origine===id).length;
    const b=button('hal-origin',nom+' · '+len,()=>{halState.origine=id;halState.page=0;halRender();});b.dataset.origin=id;$('hal-origins').append(b);}
  $('hal-family').append(new Option('Toutes les familles',''),...[...new Set(halData.modele.map(m=>m.famille))].map(n=>new Option(n,n)));
  $('hal-family').onchange=e=>{halState.family=e.target.value;halState.page=0;halRender();};
  $('hal-search').oninput=e=>{halState.q=e.target.value;halState.page=0;halRender();};
  $('hal-room').append(...data.rooms.map(r=>new Option(r.label,r.id)));$('hal-room').value=halState.room;$('hal-room').onchange=e=>{halState.room=e.target.value;};
  const list=(focus=false)=>{$('hal-rayons').scrollIntoView({behavior:'auto',block:'start'});if(focus)$('hal-browse-title').focus({preventScroll:true});};
  $('hal-prev').onclick=()=>{halState.page--;halRender();list();};$('hal-next').onclick=()=>{halState.page++;halRender();list();};
  $('hal-browse').onclick=() => list(true);$('hal-to-list').onclick=()=>{list();$('hal-grid').querySelector('[aria-pressed=true]')?.focus({preventScroll:true});};
  $('hal-original').onclick=()=>{halState.original=!halState.original;halDetail();};
  $('hal-day').onclick=()=>setPhase(0);$('hal-night').onclick=()=>{s.lianes=true;setPhase(3);};
  $('hal-visit').onclick=()=>{s.phase=3;s.lianes=true;openDepuisAtlas(gameMap.get(visite.depart));};
  $('hal-place').onclick=halStartPlacing;$('hal-png').onclick=halPNG;
  editorBank('halcyon','lierre');halRender();
}
