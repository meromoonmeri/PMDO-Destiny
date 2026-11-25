// A floor-only fixture: no item, collision, or native map entry is created.
const seuil = data.seuil_accueil;
const hall = gameMap.get(seuil.id);
const seuilControls = [];
const seuilRows = [[$('seuil-salle'),planVue(hall)],[$('seuil-detail'),seuil.detail]];
function seuilAt(r,p){return s.seuil && r.id===seuil.id ? seuil.phases[p] : [];}
function setupSeuil(){
  for(const [cv,view] of seuilRows)resize(cv,view.w,view.h);
  $('seuil-source').src=seuil.reference;
  for(const [i,p] of phases.entries()){
    const b=button('phase-choice',p.name,()=>setPhase(i),p.icon);
    b.dataset.seuilPhase=String(i);b.style.setProperty('--tone',p.tone);b.style.setProperty('--tint',p.tint);
    $('seuil-phases').append(b);seuilControls.push(b);
  }
  $('seuil-toggle').onclick=()=>{s.seuil=!s.seuil;refresh();};
  $('ouvrir-accueil').onclick=()=>openDepuisAtlas(hall);
}
function updateSeuil(){
  $('seuil-demo').hidden=s.page!=='atlas';
  for(const [i,b] of seuilControls.entries())b.setAttribute('aria-pressed',String(s.phase===i));
  $('seuil-indication').textContent=phases[s.phase].name+' · seuil sud';
  $('seuil-legende').textContent=s.seuil?'Après':'Avant';
  $('seuil-detail').setAttribute('aria-label',s.seuil?'Gros plan : le halo et le tapis sur le seuil de Destiny':'Gros plan : le seuil de Destiny sans habillage');
  const b=$('seuil-toggle');b.setAttribute('aria-pressed',String(s.seuil));b.querySelector('span').textContent=s.seuil?'Halo et tapis : avec':'Halo et tapis : sans';
  const badge=document.querySelector('.badges-seuil');if(badge)badge.hidden=!s.seuil;
}
function paintSeuil(visibleOnly=false){
  for(const [cv,view] of seuilRows)if(!visibleOnly||inWindow(cv))drawScene(cv.getContext('2d'),hall,s.phase,view);
}
