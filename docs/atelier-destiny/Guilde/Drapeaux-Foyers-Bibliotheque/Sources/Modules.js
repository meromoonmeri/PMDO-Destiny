// Independent architectural layers. Room IDs, obstacles and passages do not change.
const ext=data.extensions, shelves=ext.biblio, fireplaces=ext.foyers;
const flagSpecs=new Map(ext.drapeaux.map(a=>[a.id,a]));
const extModels=new Map(shelves.modeles.map(a=>[a.id,a.nom]));
const extState={flag:ext.drapeaux[0].id,room:fireplaces.salle,shelves:true,slots:Object.fromEntries(shelves.slots.map(a=>[a.id,a.defaut])),fire:'allumees'};
const extStore='pmd-destiny:guilde:archi:077:v1';
const fireStyles=[['allumees','Cheminées allumées'],['eteintes','Cheminées éteintes'],['masquees','Cheminées masquées']];
const extPlan=$('ext-room'), extFlag=$('ext-flag'), extButtons=[];
const rackTint=new Map(),extFrontCache=new Map(), extForms=new Map();
const fireOffset=[0,2],flameAlpha=[.62,.82,.94,1];
function extSave(){try{localStorage.setItem(extStore,JSON.stringify({shelves:extState.shelves,slots:extState.slots,fire:extState.fire}));}catch{}}
function extLoad(){try{const st=JSON.parse(localStorage.getItem(extStore)||'null');if(!st)return;
  if(typeof st.shelves==='boolean')extState.shelves=st.shelves;
  if(fireStyles.some(([id])=>id===st.fire))extState.fire=st.fire;
  for(const slot of shelves.slots){const v=st.slots?.[slot.id];if(v==='vide'||Object.hasOwn(slot.choix,v))extState.slots[slot.id]=v;}
}catch{}}
function extPhaseRack(r,p,m,key){
  const n=ambiance(r,p);if(!n)return m.png;
  const tag=key+'|'+p;
  if(!rackTint.has(tag))rackTint.set(tag,{source:m.png,lut:n.lut,patches:[]});return rackTint.get(tag);
}
function fpsFoyer(ms){return Math.floor(Math.max(0,ms)*fireplaces.fps/1000)%4;}
function areFoyersMoving(r){return r.id===fireplaces.salle&&extState.fire==='allumees';}
function planArchitecture(r,p,ms,active=true){
  if(active&&r.id===shelves.salle&&extState.shelves){
    const racks=shelves.slots.flatMap(s=>{const v=extState.slots[s.id],m=s.choix[v];return m?[[s.xy[0],s.xy[1],extPhaseRack(r,p,m,s.id+':'+v)]]:[];});
    const key='rayons:'+shelves.slots.map(s=>extState.slots[s.id]).join('/')+':'+p;
    return {racks,key,bits:racks.map(q=>q[2])};
  }
  if(active&&r.id===fireplaces.salle&&extState.fire!=='masquees'){
    const lit=extState.fire==='allumees',frame=lit?fpsFoyer(ms):0;
    const modules=fireplaces.modules.map((q,k)=>({x:q.xy[0],y:q.xy[1],w:q.size[0],h:q.size[1],png:lit?q.anime[p]:q.arret[p],frame:lit?(frame+fireOffset[k])%4:0}));
    const heat=lit?fireplaces.reflets[frame]:null;
    return {modules,heat,shadow:fireplaces.ombre,level:flameAlpha[p],key:'foyers:'+extState.fire+':'+frame,bits:[fireplaces.ombre[2],...(heat?[heat[2]]:[]),...modules.map(q=>q.png)]};
  }
  return {bits:[],key:''};
}
function drawArchitecture(c,arc){
  if(arc.racks)for(const [x,y,b] of arc.racks)drawPicture(c,b,x,y);
  if(!arc.modules)return;
  const [x,y,b]=arc.shadow;drawPicture(c,b,x,y);
  if(arc.heat){const [hx,hy,hb]=arc.heat;c.save();c.globalCompositeOperation='screen';c.globalAlpha=arc.level;drawPicture(c,hb,hx,hy);c.restore();}
  for(const q of arc.modules){
    const f=picture(q.png);if(f.ready)c.drawImage(f.pic,q.frame*q.w,0,q.w,q.h,q.x,q.y,q.w,q.h);
  }
}
function architectureFront(c,r,p,arc){
  if(!arc.racks?.length){drawPicture(c,r.m[p][1],0,0);return;}
  if(extFrontCache.has(arc.key)){c.drawImage(extFrontCache.get(arc.key),0,0);return;}
  const fr=picture(r.m[p][1]);const masks=arc.racks.map(([x,y,b])=>[x,y,picture(b)]);
  if(!fr.ready||masks.some(q=>!q[2].ready)){drawPicture(c,r.m[p][1],0,0);return;}
  // The central niche crosses the native back-wall fringe. Knock out only its
  // footprint, leaving vines above, books behind movable props, and the rest intact.
  const layer=make('canvas');resize(layer,r.w,r.h);const cx=layer.getContext('2d');cx.imageSmoothingEnabled=false;cx.drawImage(fr.pic,0,0);
  cx.globalCompositeOperation='destination-out';for(const [x,y,m] of masks)cx.drawImage(m.pic,x,y);
  if(extFrontCache.size>=12)extFrontCache.delete(extFrontCache.keys().next().value);
  extFrontCache.set(arc.key,layer);c.drawImage(layer,0,0);
}
function activeArchitecture(r){return r.id===fireplaces.salle&&extState.fire!=='masquees'||r.id===shelves.salle&&extState.shelves&&shelves.slots.some(a=>extState.slots[a.id]!=='vide');}
function extPaint(onlyVisible=false){
  if(!onlyVisible||inWindow(extFlag)){
    const a=assets.get(extState.flag);resize(extFlag,76,108);const c=extFlag.getContext('2d');c.clearRect(0,0,76,108);c.imageSmoothingEnabled=false;
    const x=38-flagSpecs.get(a.id).pivot[0],y=(100-a.h);
    stand(c,a,data.etoffes[a.id].s,x,y,clock.ms);
    extFlag.dataset.flag=a.id;extFlag.dataset.trame=String(Math.floor(clock.ms/data.etoffes[a.id].dt)%data.etoffes[a.id].n);
  }
  if(!onlyVisible||inWindow(extPlan)){
    const r=gameMap.get(extState.room);resize(extPlan,r.w,r.h);drawScene(extPlan.getContext('2d'),r,s.phase,planVue(r),{items:[]});
  }
}
function extUpdate(){
  $('ext-page').hidden=s.page!=='extensions';
  const match=extState.room===shelves.salle;
  for(const [key,b] of extButtons)b.setAttribute('aria-pressed',String(extState.flag===key));
  const f=flagSpecs.get(extState.flag);
  $('ext-flag-label').textContent=`${f.flèche}  ${f.nom} / ${f.direction}`;extFlag.setAttribute('aria-label',`Étendard animé · ${f.nom}`);
  $('ext-ref').setAttribute('aria-pressed',String(!match));$('ext-bib').setAttribute('aria-pressed',String(match));
  $('ext-jour').setAttribute('aria-pressed',String(s.phase===0));$('ext-nuit').setAttribute('aria-pressed',String(s.phase===3));
  $('ext-plan-title').textContent=gameMap.get(extState.room).label;
  $('ext-plan-summary').textContent=match?'Trois niches à garnir':'Deux cheminées encastrées';
  $('ext-plan-copy').textContent=match?'Les rayons sont sur leur propre calque ; les fenêtres et le sol restent libres.':'Feux animés dans les murs latéraux, hors du passage est.';
  $('ext-plan-note').textContent=match?'Calque indépendant de la pièce':'Éclairage limité aux cheminées et au sol proche';
  extPlan.setAttribute('aria-label',match?'Bibliothèque · rayonnages dans trois niches murales':'Réfectoire · deux cheminées, dans les murs latéraux');
  syncExtForm($('ext-preview-tools'),extState.room);
  const ed=$('ext-editor');ed.hidden=s.page!=='atelier'||![shelves.salle,fireplaces.salle].includes(s.room.id);syncExtForm(ed,ed.hidden?'':s.room.id);
}
function setWall(f){f();extSave();refresh();}
function syncExtForm(w,rid){
  if(!extForms.has(w)||extForms.get(w).rid!==rid){
    w.replaceChildren();const st={rid,slots:[]};extForms.set(w,st);
    if(rid===fireplaces.salle){
      const row=make('div','ext-field-row'),l=make('label','','Calque des foyers'),sel=make('select');sel.setAttribute('aria-label','État des cheminées');sel.dataset.foyer='true';
      sel.append(...fireStyles.map(([v,n])=>new Option(n,v)));sel.onchange=()=>setWall(()=>extState.fire=sel.value);l.append(sel);row.append(l);w.append(row);st.fire=sel;
    }else if(rid===shelves.salle){
      const row=make('div','ext-field-row');
      for(const slot of shelves.slots){const l=make('label','ext-slot',slot.nom),sel=make('select');sel.dataset.niche=slot.id;
        sel.append(new Option('Vide','vide'),...shelves.modeles.map(v=>new Option(v.nom,v.id)));sel.onchange=()=>setWall(()=>extState.slots[slot.id]=sel.value);l.append(sel);row.append(l);st.slots.push([slot.id,sel]);}
      const tog=button('ext-button','Rayonnages : visibles',()=>setWall(()=>extState.shelves=!extState.shelves),'grid');
      tog.dataset.rayonnages='toggle';const dl=button('ext-button','Calque PNG',()=>exportRacks().catch(e=>toast(e.message,true)),'download');dl.dataset.rayonnages='export';row.append(tog,dl);st.toggle=tog;st.download=dl;w.append(row);
    }
  }
  const c=extForms.get(w);
  if(c.fire)c.fire.value=extState.fire;
  if(c.toggle){c.toggle.setAttribute('aria-pressed',String(extState.shelves));c.toggle.querySelector('span').textContent=extState.shelves?'Rayonnages : visibles':'Rayonnages : masqués';}
  if(c.download)c.download.disabled=c.slots.every(([id])=>extState.slots[id]==='vide');
  for(const [k,q] of c.slots){q.value=extState.slots[k];q.disabled=!extState.shelves;}
}
async function exportRacks(){
  const cols=shelves.slots.flatMap(a=>{const m=a.choix[extState.slots[a.id]];return m?[[...a.xy,picture(m.png)]]:[];});
  const c=make('canvas');resize(c,...shelves.canvas);const ct=c.getContext('2d');ct.imageSmoothingEnabled=false;
  const ok=await Promise.all(cols.map(q=>q[2].promise));if(ok.includes(false))throw new Error('Rayonnage indisponible.');
  for(const [x,y,p] of cols)ct.drawImage(p.pic,x,y);
  const blob=await new Promise(resolve=>c.toBlob(resolve,'image/png'));if(!blob)throw new Error('Export PNG indisponible.');download(blob,'Bibliotheque-Rayonnages-480x360.png');
}
function flagPng(){const a=assets.get(extState.flag),v=flagSpecs.get(a.id);const ar=Uint8Array.from(atob(a.m[0].split(',').at(-1)),x=>x.charCodeAt(0));download(new Blob([ar],{type:'image/png'}),`Etendard-Destiny-${v.direction}.png`);}
function extFlagControl(panel,o,a){
  const old=flagSpecs.get(a.id);if(!old)return;
  const l=make('label','ext-flag-choose','Orientation de l’étendard'),sel=make('select');sel.id='ext-turn-flag';
  sel.append(...ext.drapeaux.map(v=>new Option(v.flèche+' '+v.nom+' · '+v.direction,v.id)));sel.value=a.id;
  sel.onchange=()=>{
    if(!o){s.tool=sel.value;s.ghost=null;refresh();$('ext-turn-flag')?.focus();return;}
    const v=flagSpecs.get(sel.value),x=o.x+old.pivot[0]-v.pivot[0],y=o.y+old.pivot[1]-v.pivot[1],bad=why(s.room,assets.get(v.id),x,y,o.id);
    if(bad){sel.value=o.meuble;toast(bad,true);return;}
    setRoomItems(dataFor().map(q=>q.id===o.id?{...q,meuble:v.id,x,y}:q));$('ext-turn-flag')?.focus();
  };l.append(sel);panel.append(l);
  if(!o&&s.room.id===ext.accueil){const x=158-old.pivot[0],y=209-old.pivot[1];if(!why(s.room,a,x,y))panel.append(button('soft','Poser dans l’exemple',()=>place(a,{x,y}),'target'));}
}
function setupExt(){
  extLoad();
  for(const f of ext.drapeaux){const b=button('ext-dir',null,()=>{extState.flag=f.id;refresh();});b.dataset.flagDir=f.direction;
    const a=make('b','',f.flèche);a.setAttribute('aria-hidden','true');b.append(a,make('strong','',f.direction));b.title=f.nom+' · '+f.direction;b.setAttribute('aria-label',b.title);$('ext-directions').append(b);extButtons.push([f.id,b]);}
  $('ext-ref').onclick=()=>{extState.room=fireplaces.salle;refresh();};$('ext-bib').onclick=()=>{extState.room=shelves.salle;refresh();};
  $('ext-jour').onclick=()=>setPhase(0);$('ext-nuit').onclick=()=>setPhase(3);$('ext-open-room').onclick=()=>openDepuisAtlas(gameMap.get(extState.room));
  $('ext-flag-png').onclick=flagPng;$('ext-flag-use').onclick=()=>{const a=assets.get(extState.flag);editorBank('etendards','tout');s.category='tout';$('query').value='';updatePalette();openDepuisAtlas(gameMap.get(ext.accueil));activateTool(a);};
  $('ext-cliff').onclick=()=>openCliff(true);
}
