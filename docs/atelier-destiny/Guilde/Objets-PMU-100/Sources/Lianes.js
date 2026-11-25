// Optional artwork, applied without mutating the room blueprint or the existing Grodoudou palettes.
const vineLUTs = new Map();
function lianesAt(r,p,show=s.lianes){
  if(!show)return [];
  const layer=data.lianes[r.id],key=r.id+':'+p;
  if(!vineLUTs.has(key)){
    const matrix=ambiance(r,p)?.lut;
    vineLUTs.set(key,[layer.s,layer.t].map(source=>matrix?{source,lut:matrix,patches:[]}:source));
  }
  return p===3?[...vineLUTs.get(key),layer.l,layer.b]:vineLUTs.get(key);
}
function ordered(items){return [...items].sort((a,b)=>Number(assets.get(b.meuble).category==='tapis')-Number(assets.get(a.meuble).category==='tapis'));}
function updateLianeUI(){
  const b=$('toggle-lianes');b.setAttribute('aria-pressed',String(s.lianes));
  b.querySelector('span').textContent=s.lianes?'Lianes : avec':'Lianes : sans';
  b.classList.toggle('show-glow',s.phase===3&&s.lianes);
  const words=s.lianes ? s.compare ? 'Lianes · halos en Nuit' : s.phase===3 ? `Nuit · ${data.lianes[s.room.id].n} bourgeons lumineux` : 'Lianes de Reverie visibles' : 'Lianes masquées';
  $('foliage-status').textContent=words;
}
$('toggle-lianes').onclick=()=>{s.lianes=!s.lianes;refresh();};
$('collection').onchange=()=>{s.collection=$('collection').value;s.palette='tout';$('palette-pmu').value='tout';$('palette-pmu').disabled=s.collection==='origine';s.category='tout';cancel();updatePalette();refresh();};
$('palette-pmu').onchange=()=>{s.palette=$('palette-pmu').value;cancel();updatePalette();refresh();};
