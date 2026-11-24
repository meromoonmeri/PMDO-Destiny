// This fixture belongs only to the north staircase. It never changes the gates or layout JSON.
const chainSet=data.chaines_accueil,chainRoom=gameMap.get(chainSet.id),chainView=$('chaines-plan');
function chainesAt(r,p){return s.chaines&&r.id===chainSet.id?chainSet.phases[p]:[];}
function setupChaines(){
  resize(chainView,chainSet.vue.w,chainSet.vue.h);
  $('chaines-tilesheet').src=chainSet.planche;$('chaines-source').src=chainSet.reference;
  $('ouvrir-chaines').onclick=()=>openDepuisAtlas(chainRoom);
  $('toggle-chaines').onclick=()=>{s.chaines=!s.chaines;refresh();};
}
function updateChaines(){
  $('chaines-demo').hidden=s.page!=='atlas';
  const b=$('toggle-chaines');b.setAttribute('aria-pressed',String(s.chaines));b.querySelector('span').textContent=s.chaines?'Chaînes : avec':'Chaînes : sans';
  $('chaines-ambiance').textContent=phases[s.phase].name+(s.chaines?'':' · sans chaînes');
  chainView.setAttribute('aria-label',s.chaines?'Deux chaînes montent de part et d’autre de l’escalier nord':'Escalier nord sans chaînes');
}
function paintChaines(visibleOnly=false){
  if(!visibleOnly||inWindow(chainView))drawScene(chainView.getContext('2d'),chainRoom,s.phase,chainSet.vue);
}
