// One shared latch for the existing stairs on both maps. No destination is overwritten.
const grille=data.grille_accueil,grilleHall=gameMap.get(grille.id),grilleNext=gameMap.get(grille.dest),grilleCv=$('grille-plan');
const lift={frame:0,target:0,moving:false};
const lastGrille=grille.positions.length-1;
const grilleOuverte=()=>!lift.moving&&lift.frame===lastGrille;
const isGrilleLink=(r,g)=>grille.liens.some(([room,id])=>room===r.id&&id===g.id);
function suivrePassage(r,g){
  if(isGrilleLink(r,g)&&!grilleOuverte()){toast('Lève complètement la grille pour franchir l’escalier.',true);return;}
  if(gameMap.has(g.dest))selectRoom(g.dest);
}
function portesPour(r){
  return r.gates.map((g,i)=>{
    const to=gameMap.get(g.dest), gated=isGrilleLink(r,g);
    const p=to?button('portal',(i+1)+' · '+to.label,()=>suivrePassage(r,g)):make('span','portal-out',(i+1)+' · Falaise');
    p.title=g.id;
    if(gated){p.disabled=!grilleOuverte();p.dataset.grille='true';}
    return p;
  });
}
function grilleAt(r,p){return r.id===grille.id?grille.calques[p]:null;}
function drawGrille(c,asset,frame){
  if(!asset||frame===lastGrille)return;
  const row=picture(asset),[x,y,w,h]=grille.rect, col=frame%grille.colonnes,line=Math.floor(frame/grille.colonnes);
  if(row.ready)c.drawImage(row.pic,col*w,line*h,w,h,x,y,w,h);
}
function basculerGrille(){
  if(lift.moving)return;
  const start=lift.frame,end=grilleOuverte()?0:lastGrille;
  lift.target=end;
  if(boundedMotion.matches){lift.frame=end;draw();refresh();return;}
  lift.moving=true;refresh();
  const tick0=performance.now(),direction=end>start?1:-1,total=Math.abs(end-start);
  function tick(now){
    const step=Math.max(0,Math.min(total,Math.floor((now-tick0)*grille.ips/1000)));
    const next=start+direction*step;
    if(step===total){
      // Paint the end pose before announcing it or unlocking the passage.
      lift.frame=end;draw();lift.moving=false;refresh();return;
    }
    if(lift.frame!==next){lift.frame=next;invalidate();}
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
function setupGrille(){
  resize(grilleCv,grille.vues.w,grille.vues.h);
  $('grille-ref-fermee').src=grille.reference.fermee;
  $('grille-ref-ouverte').src=grille.reference.ouverte;
  $('grille-sheet').src=grille.calques[0];
  $('grille-lever').onclick=basculerGrille;
  $('grille-editor-lever').onclick=basculerGrille;
  $('grille-passer').onclick=()=>{if(grilleOuverte())openDepuisAtlas(grilleNext);};
  $('grille-voir-plan').onclick=()=>openDepuisAtlas(grilleHall);
}
function updateGrille(){
  $('grille-demo').hidden=s.page!=='atlas';
  const ouvert=grilleOuverte(),goingUp=lift.target===lastGrille;
  const msg=lift.moving?(goingUp?'En train de monter · passage bloqué':'En train de descendre · passage bloqué'):(ouvert?'Ouverte · passage libre':'Fermée · passage bloqué');
  const action=lift.moving?(goingUp?'Ouverture…':'Fermeture…'):(ouvert?'Abaisser la grille':'Lever la grille');
  $('grille-etat').textContent=msg;
  $('grille-editor-status').textContent=msg;
  $('grille-editor-tools').hidden=!s.room.gates.some(g=>isGrilleLink(s.room,g));
  for(const key of ['grille-lever','grille-editor-lever']){const b=$(key);b.disabled=lift.moving;b.querySelector('span').textContent=action;}
  $('grille-passer').disabled=!ouvert;
  grilleCv.parentElement.dataset.ouvert=String(ouvert);
  grilleCv.setAttribute('aria-label','Escalier nord : grille '+msg.toLowerCase());
}
function paintGrille(visibleOnly=false){
  if(visibleOnly&&!inWindow(grilleCv))return;
  drawScene(grilleCv.getContext('2d'),grilleHall,s.phase,grille.vues);
  grilleCv.dataset.grilleImage=String(lift.frame);
}
