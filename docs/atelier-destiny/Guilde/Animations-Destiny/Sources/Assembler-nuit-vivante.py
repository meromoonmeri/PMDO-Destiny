#!/usr/bin/env python3
"""Add an independent animated edition; do not touch any previous workshop or game file."""
from pathlib import Path
import hashlib,json,re
S=Path(__file__).resolve().parent;O=S.parent;G=O.parent;W=Path.home()/'.cache/guilde-animee'
BASE=G/'Guilde-Destiny-Drapeaux-et-Lianes.html';DEST=G/'Guilde-Destiny-Nuit-Vivante.html';MARK='<script id="donnees" type="application/json">'

def read(p):return p.read_text(encoding='utf8')
def edit(t,pairs):
 for a,b in pairs:
  assert t.count(a)==1,(t.count(a),a)
  t=t.replace(a,b,1)
 return t

def main():
 base=BASE.read_bytes();head,rest=base.decode('utf-8').split(MARK,1);data,tail=rest.split('</script>',1);d=json.loads(data);stock=dict(d)
 d['lianes']=json.loads(read(W/'LianesAnimees.json'));d['etoffes']=json.loads(read(W/'Etoffes.json'));index=json.loads(read(O/'Index-nuit-et-poteaux.json'));d['cadence']=index['parametres']
 assert len(d['lianes'])==15 and len(d['etoffes'])==12 and set(d['etoffes'])<={a['id'] for a in d['catalog']}
 assert all(d[s]==stock[s] for s in ('rooms','nuits','lumieres','catalog','game','phases'))
 head=edit(head,[
  ('<title>Destiny · Drapeaux, étendards et lianes</title>','<title>Destiny · Nuit vivante</title>'),
  ('</style>',read(S/'Motion.css')+'\n</style>'),
  ('  <symbol id="i-leaf"','''  <symbol id="i-pause-motion" viewBox="0 0 24 24"><path d="M9 5v14m6-14v14" stroke-width="3"/></symbol>
  <symbol id="i-play-motion" viewBox="0 0 24 24"><path d="M8 5l11 7-11 7z"/></symbol>
  <symbol id="i-leaf"'''),
  ('PLANS NATIFS <i></i> LIANES INSPIRÉES DE REVERIE','PLANS NATIFS <i></i> ÉDITION NUIT VIVANTE'),
  ('Drapeaux, gonfanons, fanions et tentures inspirés de l’emblème de la guilde. Les lianes de Reverie éclairent toujours les boiseries en Nuit. À toi de placer les ornements.', 'Les lianes s’enroulent autour des poteaux. À la nuit, leurs bourgeons respirent en douceur et les ombres de feuillage glissent sur le bois. Essaie les étoffes animées dans Aménager.'),
  ('<strong>24</strong><span>ORNEMENTS</span>',f'<strong>{index["nb_poteaux"]}</strong><span>POTEAUX HABILLÉS</span>'),
  ('    <span class="atlas-nav-note">Lumières de Grodoudou · 7 sorties sud corrigées</span>','''    <button id="motion-toggle" class="soft motion-button" aria-pressed="true" type="button"><svg aria-hidden="true"><use href="#i-pause-motion"/></svg><span>Animations : actives</span></button>
    <span class="atlas-nav-note">4 ambiances · 7 sorties sud corrigées</span>'''),
  ('Décor · ambiance et lianes sélectionnées','Instant de l’animation et ambiance choisie'),
  ('<p><b>Lianes.</b> Bascule « Lianes : avec / sans » pour retrouver les salles sans végétation. En Nuit, les bourgeons projettent une lumière chaude sur le bois.</p>', '<p><b>Nuit vivante.</b> Les enroulements laissent le bois des poteaux apparent. En Nuit, les halos et les ombres varient lentement, sans flash. Tu peux figer la scène avec « Animations : en pause » ou revenir aux plans nus avec « Lianes : sans ».</p><p><b>Étoffes.</b> Les drapeaux sur hampe, les gonfanons de cérémonie et les guirlandes de fanions portent le badge « Animé » dans le catalogue. Choisis un emplacement pour les voir sur le plan. Les supports ne bougent pas.</p>'),
 ])
 tail=edit(tail,[
  ('pmd-destiny:guilde:drapeaux-lianes:077:v1','pmd-destiny:guilde:nuit-vivante:077:v1'),
  ("room:data.rooms[0],phase:0,mode:'plan'", "room:data.rooms[0],phase:3,mode:'plan'"),
  ('''  const {grid=false,gates=false,interactive=false,items=dataFor(r),lianes=s.lianes}=opts;''','''  const {grid=false,gates=false,interactive=false,items=dataFor(r),lianes=s.lianes,ms=clock.ms}=opts;'''),
  ('''c.globalAlpha=q.bad?.42:1;drawPicture(c,sprite(a,p,r),q.x,q.y);c.globalAlpha=1;''','''c.globalAlpha=q.bad?.42:1;drawObjet(c,a,p,r,q.x,q.y,ms);c.globalAlpha=1;'''),
  ('''c.globalAlpha=q.bad?.42:.76;drawPicture(c,sprite(a,p,r),q.x,q.y);c.globalAlpha=1;''','''c.globalAlpha=q.bad?.42:.76;drawObjet(c,a,p,r,q.x,q.y,ms);c.globalAlpha=1;'''),
  ('''  if(vines.length===4){c.save();c.globalCompositeOperation='screen';drawPicture(c,vines[2],0,0);c.restore();drawPicture(c,vines[3],0,0);}''', '''  if(vines.length&&p===3)illuminate(c,r,ms);'''),
  ('''  c.canvas.dataset.scene=[...r.m[p],...vines,...items.map(o=>sprite(assets.get(o.meuble),p,r))].every(b=>picture(b).ready)?`${r.id}:${p}:${view.y}:${items.length}`:'';''', '''  const scene=[...r.m[p],...vines,...nightBits(r,p,lianes),...items.map(o=>spriteForScene(assets.get(o.meuble),p,r))].every(b=>picture(b).ready)?`${r.id}:${p}:${view.y}:${items.length}`:'';
  if(c.canvas.dataset.scene!==scene)c.canvas.dataset.scene=scene;'''),
  ('''  const view=viewport(), r=s.room;
  if(s.compare)''','''  const view=viewport(), r=s.room;
  showCloth();
  if(s.compare)'''),
  ('''el.replaceChildren();
  const cards=data.catalog.filter''','''el.replaceChildren();clothPreviews=[];
  const cards=data.catalog.filter'''),
  ('''cover.append(im);c.append(cover,make('span','item-label',a.label));el.append(c);''','''cover.append(im);if(data.etoffes[a.id]){buildClothThumb(a,cover,im);c.title+=' · animé';c.dataset.anime='true';}c.append(cover,make('span','item-label',a.label));el.append(c);'''),
  ('''  if(!cards.length)el.append(make('p','none','Aucun objet ne correspond à ces filtres.'));el.scrollTop=scroll;''','''  if(!cards.length)el.append(make('p','none','Aucun objet ne correspond à ces filtres.'));el.scrollTop=scroll;showCloth();'''),
  ('''(a.previewOnly?'variante d’atelier':'sprite natif')''','''(data.etoffes[a.id]?'étoffe animée':a.previewOnly?'variante d’atelier':'sprite natif')'''),
  ('''const r=s.room,i=s.phase,v=viewport(),items=[...dataFor()],lianes=s.lianes;const bits=[...r.m[i],...lianesAt(r,i,lianes),...items.map(o=>sprite(assets.get(o.meuble),i,r))];''','''const r=s.room,i=s.phase,v=viewport(),items=[...dataFor()],lianes=s.lianes,ms=clock.ms,mode=s.mode;const bits=[...r.m[i],...lianesAt(r,i,lianes),...nightBits(r,i,lianes),...items.map(o=>spriteForScene(assets.get(o.meuble),i,r))];'''),
  ('''drawScene(out.getContext('2d'),r,i,v,{items,lianes});''','''drawScene(out.getContext('2d'),r,i,v,{items,lianes,ms});'''),
  ('''(s.mode==='plan'?'':'-sud')+(lianes?'-lianes':'')''','''(mode==='plan'?'':'-sud')+(lianes?'-lianes':'')'''),
  ('''// Optional artwork, applied without mutating the room blueprint or the existing Grodoudou palettes.''',read(S/'Motion.js')+'\n// Optional artwork, applied without mutating the room blueprint or the existing Grodoudou palettes.'),
  ('''  return p===3?[...vineLUTs.get(key),layer.l,layer.b]:vineLUTs.get(key);''','''  return vineLUTs.get(key);'''),
  ("'Lianes de Reverie visibles'",'`${data.lianes[s.room.id].v} poteaux enroulés`'),
  ('Les lianes suivent les poutres et les rives des 15 salles. Choisis Nuit pour allumer les bourgeons.','Poutres, poteaux et rives habillés de lianes. En Nuit, regarde le jeu de lumière sur les planches.'),
  ('''setupAtlas();updatePalette();refresh();''','''setupAtlas();updatePalette();refresh();setupMotion();'''),
 ])
 DEST.write_text(head+MARK+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>'+tail,encoding='utf-8')
 m=re.search(r'\s*<script>(.*)</script>\s*</body>',tail,re.S);assert m;(W/'Nuit-vivante.js').write_text(m.group(1),encoding='utf8');assert BASE.read_bytes()==base
 print('PASS · Nuit vivante, HTML autonome ·',f'{DEST.stat().st_size:,} octets','· référence inchangée',flush=True)
if __name__=='__main__':main()
