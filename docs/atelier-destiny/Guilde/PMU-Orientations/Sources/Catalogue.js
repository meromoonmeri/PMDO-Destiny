'use strict';
(()=>{
const $=q=>document.getElementById(q), D=JSON.parse($('banque').textContent), dirs=D.projection.ordre;
const node=(kind,className,content)=>{const n=document.createElement(kind);if(className)n.className=className;if(content!==undefined)n.textContent=content;return n;};
const normalize=t=>t.normalize('NFD').replace(/\p{Diacritic}/gu,'').toLowerCase().replace(/[’_\-]/g,' ');
const objects=D.objets;for(const r of objects)r.find=normalize([r.nom,r.code,r.famille,r.collection,r.id].join(' '));
const featured=objects.filter(o=>o.prov==='new'),other=objects.filter(o=>o.prov!=='new'),all=[...featured,...other];
let cur=featured.find(x=>x.code==='Creation_Pupitre-aux-cartes')||all[0],i=0,page=0,browse=[],ticket=0,spin=null;
const pagesize=10, dirNodes=[];
for(const cat of [...new Set(objects.map(o=>o.collection))].sort((a,b)=>a.localeCompare(b,'fr'))){const o=node('option',null,cat);o.value=cat;$('category').append(o);}
function dim(n){return [n[0],n[1]].join(' × ');}
function choose(j){i=(8+j)%8;showSprite();}
function srcThumb(url,cls){const n=node('img',cls);n.src=url;n.alt='';n.decoding='async';return n;}
for(let j=0;j<8;j++){
  const n=node('button');n.type='button';n.setAttribute('aria-label',dirs[j]+' : '+D.projection.libelles[j]);
  const im=srcThumb(cur.vues[j][0]);const ar=node('span','arrow',D.projection.fleches[j]), p=node('span','dir-pic'), label=node('b',null,dirs[j]);p.append(im);n.append(ar,p,label);
  n.addEventListener('click',()=>{setSpin(false);choose(j);});$('dirs').append(n);dirNodes.push([n,im]);
}
const mode={plan_sol:'À plat : la vue suit le plan du sol, sans incliner tout le sprite.',volume_et_textures:'Volume reconstitué : les faces non visibles dans Down sont interprétées.',ensemble_de_volumes:'Plusieurs éléments dans le sprite source : ils restent groupés, chacun avec son volume et sa position.'};
const tag={pmu:'BANQUE 0.7.7',new:'CRÉATION',ai:'BONUS EXISTANT'};
function setSpin(on){if(spin)clearInterval(spin);spin=on?setInterval(()=>choose(i+1),690):null;$('spin').textContent=on?'Ⅱ Pause':'▷ Tourner';$('spin').setAttribute('aria-pressed',String(on));}
function showSprite(){
  const v=cur.vues[i], q=cur.frame, canvas=$('sprite'), id=++ticket;
  const f=Math.min(3,Math.min(525/q[0],300/q[1]));
  canvas.width=Math.ceil(q[0]*f);canvas.height=Math.ceil(q[1]*f);canvas.setAttribute('aria-label',cur.nom+' — '+dirs[i]);
  const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);ctx.imageSmoothingEnabled=false;
  const im=new Image();im.decoding='async';
  im.onload=()=>{if(id!==ticket)return;const x=Math.round((q[2]-v[3])*f),y=Math.round((q[3]-v[4])*f);ctx.drawImage(im,x,y,Math.round(v[1]*f),Math.round(v[2]*f));$('problem').hidden=true;canvas.dataset.direction=dirs[i];};
  im.onerror=()=>{if(id===ticket)$('problem').hidden=false;};im.src=v[0];
  for(let j=0;j<8;j++)dirNodes[j][0].setAttribute('aria-pressed',String(j===i));
  $('dir-title').textContent=dirs[i];$('dir-scale').textContent=D.projection.libelles[i]+' · '+dim(v.slice(1,3))+' px';
  $('download').href=v[0];$('pivot').textContent='PIVOT '+v[3]+' / '+v[4];
}
function select(o,jump=false){
  cur=o;setSpin(false);
  $('badge').textContent='02 / '+o.collection;$('object-name').textContent=o.nom;$('subname').textContent=o.code+' · '+o.famille;
  $('source-chip').textContent=tag[o.prov];$('method').textContent=mode[o.methode];$('atlas').href=o.atlas;
  for(let j=0;j<8;j++)dirNodes[j][1].src=o.vues[j][0];
  showSprite();list(false);
  if(jump&&matchMedia('(max-width: 650px)').matches){$('object-name').focus({preventScroll:true});$('object-name').scrollIntoView({block:'start'});}
}
function list(pick=false){
  const query=normalize($('search').value.trim()).split(/\s+/).filter(Boolean), family=$('family').value,category=$('category').value;
  browse=all.filter(o=>(family==='*'||o.prov===family)&&(category==='*'||o.collection===category)&&query.every(s=>o.find.includes(s)));
  const max=Math.max(1,Math.ceil(browse.length/pagesize));page=Math.max(0,Math.min(page,max-1));
  $('results').textContent=browse.length+' modèle'+(browse.length===1?'':'s')+(browse.length?' · 8 vues chacun':'');
  const fr=document.createDocumentFragment(), n=browse.slice(page*pagesize,(page+1)*pagesize);
  for(const o of n){const bn=node('button','entry');bn.type='button';bn.setAttribute('aria-pressed',String(cur===o));bn.dataset.code=o.code;
    const pic=node('span','thumb');pic.append(srcThumb(o.vues[0][0]));const tx=node('span');tx.append(node('b',null,o.nom),node('small',null,o.code));bn.append(pic,tx,node('span','arr','›'));bn.onclick=()=>select(o,true);fr.append(bn);}
  if(!n.length)fr.append(node('p','empty','Aucun objet ne correspond. Essaie un autre mot ou choisis « Toutes catégories ».'));
  $('entries').replaceChildren(fr);$('page-n').textContent=(page+1)+' / '+max;$('page-prev').disabled=page<1;$('page-next').disabled=page>=max-1;
  if(pick&&n.length&&!browse.includes(cur))select(n[0]);
}
$('dir-prev').onclick=()=>{setSpin(false);choose(i-1);};$('dir-next').onclick=()=>{setSpin(false);choose(i+1);};$('spin').onclick=()=>setSpin(!spin);
$('page-prev').onclick=()=>{page--;list();};$('page-next').onclick=()=>{page++;list();};
for(const e of ['family','category'])$(e).addEventListener('change',()=>{page=0;list(true);});
$('search').addEventListener('input',()=>{page=0;list(true);});
$('dirs').addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();setSpin(false);choose(i+(e.key==='ArrowRight'?1:-1));dirNodes[i][0].focus();}});
document.addEventListener('visibilitychange',()=>{if(document.hidden)setSpin(false);});
select(cur);
})();
