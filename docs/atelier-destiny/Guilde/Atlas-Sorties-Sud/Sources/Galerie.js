// Shared renderer: the overview never substitutes thumbnails for the native maps.
const atlasCards=[], southPairs=[], atlasPhases=[];
const atlasTabs={atlas:'tab-all',sud:'tab-south',atelier:'tab-work'};
const countText=(n,label)=>n+' '+label+(n===1?'':'s');
const tags=(r)=>[String(r.n).padStart(2,'0'),countText(r.gates.length,'passage')];
function planVue(r){return {x:0,y:0,w:r.w,h:r.h};}
function sudVue(r,avant=false){return {x:within(r.south.x-160,0,r.w-320),y:(avant?r.h:r.south.bottom)-240,w:320,h:240};}
function changePage(page){
  if(!(page in atlasTabs))return;
  cancel();s.selected=null;s.page=page;
  if(page==='atelier'){s.mode='plan';s.compare=false;s.before=false;}
  refresh();
}
function openDepuisAtlas(r,mode='plan'){
  s.page='atelier';s.mode=mode;s.compare=false;selectRoom(r.id);
  window.scrollTo({top:0,behavior:'auto'});
  $('room-name').focus({preventScroll:true});
}
function getSouthGate(r){return r.gates.find(g=>g.id==='SortieGuilde'||g.id.endsWith('Sud'));}
function setupAtlas(){
  for(const [page,id] of Object.entries(atlasTabs))$(id).onclick=()=>changePage(page);
  $('atlas-gates').onclick=()=>{s.gates=!s.gates;refresh();};
  for(const [i,p] of phases.entries()){
    const b=button('phase-choice',p.name,()=>setPhase(i),p.icon);b.dataset.atlasPhase=String(i);if(p.title)b.title=p.title;
    b.style.setProperty('--tone',p.tone);b.style.setProperty('--tint',p.tint);
    $('atlas-phases').append(b);atlasPhases.push(b);
  }
  for(const r of data.rooms){
    const panel=make('article','atlas-card');panel.dataset.plan=r.id;
    const open=button('atlas-open','',()=>openDepuisAtlas(r));open.setAttribute('aria-label','Ouvrir : '+r.label);
    const scene=make('canvas','atlas-map');scene.setAttribute('aria-hidden','true');resize(scene,r.w,r.h);
    const label=make('div','atlas-card-label');
    label.append(make('span','atlas-num',tags(r)[0]),make('h3','',r.label));
    const meta=make('div','atlas-card-meta');meta.append(make('span','',tags(r)[1]),make('span','','·'),make('span','',r.w+' × '+r.h+' px'));
    open.append(scene,label,meta);panel.append(open);
    if(r.south?.band){
      const b=button('atlas-pin','Sud corrigé',()=>openDepuisAtlas(r,'cadre'),'cadre');
      b.title='Voir la caméra au seuil : '+r.label;b.setAttribute('aria-label','Voir le cadre sud corrigé : '+r.label);panel.append(b);
    }
    $('overview-grid').append(panel);atlasCards.push([r,scene,planVue(r)]);
    if(!r.south?.band)continue;
    const c=make('article','atlas-pair');c.dataset.south=r.id;
    const header=make('div','atlas-pair-head'), title=make('div');
    title.append(make('span','atlas-num','SALLE '+tags(r)[0]),make('h3','',r.label));
    const to=getSouthGate(r)?.dest; title.append(make('span','atlas-route','Vers : '+(gameMap.get(to)?.label||'Falaise')));
    header.append(title,button('atlas-pin','Voir dans l’atelier',()=>openDepuisAtlas(r,'cadre'),'cadre'));c.append(header);
    const two=make('div','atlas-duo');
    for(const avant of [true,false]){
      const figure=make('figure',avant?'atlas-avant':'atlas-apres');
      const caption=make('figcaption','',avant?'Avant':'Corrigé');
      caption.append(make('span','',avant?'Caméra d’origine':'−'+r.south.band+' px sous le passage'));
      const cv=make('canvas','atlas-crop');resize(cv,320,240);cv.setAttribute('aria-label',r.label+(avant?' : cadre avant correctif':' : cadre corrigé'));
      figure.append(caption,cv);two.append(figure);southPairs.push([r,cv,sudVue(r,avant)]);
    }
    c.append(two);$('south-grid').append(c);
  }
}
function updateAtlas(){
  const atelier=s.page==='atelier', sud=s.page==='sud';
  $('editor').hidden=!atelier;$('atlas-page').hidden=atelier;
  $('overview-grid').hidden=sud;$('south-grid').hidden=!sud;
  for(const [page,id] of Object.entries(atlasTabs))$(id).setAttribute('aria-pressed',String(page===s.page));
  $('atlas-title').textContent=sud?'Les 7 sorties sud corrigées':'Les 15 salles de la guilde';
  $('atlas-note').textContent=sud?'La caméra remonte juste au-dessus de la bande sous le passage. Les chemins ne bougent pas.':'Les plans entiers de Destiny 0.7.7, sans verdure. Ouvre une salle pour voir ses passages ou l’aménager.';
  $('atlas-guide').textContent=(sud?'Même taille de vue (320 × 240 px), mêmes accès. Les fonds sur les côtés restent visibles.':'Les cartes « Sud corrigé » ouvrent directement le cadrage approuvé.')+' '+['Jour : lumière claire des intérieurs de Grodoudou.','Aube : déclinaison douce, aux vitres pêche.','Crépuscule : lumière orangée de la façade de Grodoudou.','Nuit : vitres bleu profond et dortoirs tamisés.'][s.phase];
  for(const [i,b] of atlasPhases.entries())b.setAttribute('aria-pressed',String(i===s.phase));
  $('atlas-gates').setAttribute('aria-pressed',String(s.gates));
}
function paintAtlas(){
  const rows=s.page==='sud'?southPairs:atlasCards;
  for(const [r,cv,view] of rows)drawScene(cv.getContext('2d'),r,s.phase,view,{gates:s.gates});
}
