#!/usr/bin/env python3
"""Create a distinct, self-contained live workshop; the reference atlas stays byte-identical."""
from pathlib import Path
import hashlib,json,re,sys

S=Path(__file__).resolve().parent; O=S.parent; G=O.parent; W=Path.home()/'.cache/guilde-objets'; A=G/'Atlas-Sorties-Sud/Sources'
ORIGINAL=G/'Guilde-Destiny-Toutes-les-Salles.html'; TARGET=G/'Guilde-Destiny-Lianes-et-PMU-100.html'

def read(f):return f.read_text(encoding='utf-8')
def edit(t,pairs):
 for old,new in pairs:
  assert t.count(old)==1,old
  t=t.replace(old,new,1)
 return t

def main():
 base_bytes=ORIGINAL.read_bytes();d=json.loads(read(ORIGINAL).split('<script id="donnees" type="application/json">',1)[1].split('</script>',1)[0]);data={**d}
 extras=json.loads(read(W/'Catalogue.json'));data['lianes']=json.loads(read(W/'Calques.json'));assert len(extras)==100 and len(data['lianes'])==15
 data['catalog']=d['catalog']+extras
 assert data['rooms']==d['rooms'] and data['nuits']==d['nuits'] and data['lumieres']==d['lumieres']
 assert len({a['id'] for a in data['catalog']})==len(data['catalog'])==133
 chapter=read(A/'Galerie.js');chapter=edit(chapter,[
  ('''  $('atlas-note').textContent=sud?'La caméra remonte juste au-dessus de la bande sous le passage. Les chemins ne bougent pas.':'Les plans entiers de Destiny 0.7.7, sans verdure. Ouvre une salle pour voir ses passages ou l’aménager.';''',
   '''  $('atlas-note').textContent=sud?'La caméra remonte juste au-dessus de la bande sous le passage. Les chemins ne bougent pas.':(s.lianes?'Les lianes suivent les poutres et les rives des 15 salles. Choisis Nuit pour allumer les bourgeons.':'Les salles natives, sans aucun calque de verdure.');'''),
  ('''  $('atlas-gates').setAttribute('aria-pressed',String(s.gates));''',
   '''  $('atlas-gates').setAttribute('aria-pressed',String(s.gates));updateLianeUI();'''),
 ])
 js=edit(read(A/'Atelier.js'),[
  ("const STORE='pmd-destiny:guilde:atelier:077:v1'", "const STORE='pmd-destiny:guilde:lianes-pmu100:077:v1'"),
  ("snap:true,category:'tout',tool:null", "snap:true,category:'tout',collection:'pmu100',palette:'tout',lianes:true,tool:null"),
  ("if(!n)return a.m[p];", "if(!n)return a.m[p]??a.m[0];"),
  ('''function drawScene(c,r,p,view,opts={}){
  const {grid=false,gates=false,interactive=false,items=dataFor(r)}=opts;''',
   '''function drawScene(c,r,p,view,opts={}){
  const {grid=false,gates=false,interactive=false,items=dataFor(r),lianes=s.lianes}=opts;
  const vines=lianesAt(r,p,lianes);'''),
  ('''  drawPicture(c,r.m[p][0],0,0);
  for(const o of items){''',
   '''  drawPicture(c,r.m[p][0],0,0);
  if(vines.length)drawPicture(c,vines[0],0,0);
  for(const o of ordered(items)){'''),
  ('''  drawPicture(c,r.m[p][1],0,0);
  if(grid)''',
   '''  drawPicture(c,r.m[p][1],0,0);
  if(vines.length)drawPicture(c,vines[1],0,0);
  if(vines.length===4){c.save();c.globalCompositeOperation='screen';drawPicture(c,vines[2],0,0);c.restore();drawPicture(c,vines[3],0,0);}
  if(grid)'''),
  ('[...r.m[p],...items.map(o=>sprite(assets.get(o.meuble),p,r))]', '[...r.m[p],...vines,...items.map(o=>sprite(assets.get(o.meuble),p,r))]'),
  ('''a.w+' × '+a.h+' px · sprite natif' ''','''a.w+' × '+a.h+' px · '+(a.previewOnly?'variante d’atelier':'sprite natif') ''') if "a.w+' × '+a.h+' px · sprite natif' " in read(A/'Atelier.js') else
  ("a.w+' × '+a.h+' px · sprite natif'","a.w+' × '+a.h+' px · '+(a.previewOnly?'variante d’atelier':'sprite natif')"),
  ('''  const cards=data.catalog.filter(a=>(s.category==='tout'||s.category===a.category)&&(!term||normalized(a.label).includes(term)));''',
   '''  const cards=data.catalog.filter(a=>(a.collection??'origine')===s.collection&&(s.palette==='tout'||s.palette===a.palette)&&(s.category==='tout'||s.category===a.category)&&(!term||normalized(a.label).includes(term)));
  $('catalog-count').textContent=cards.length;$('catalog-count').setAttribute('aria-label',cards.length+' résultats');'''),
  ('''c.dataset.asset=a.id;c.setAttribute''','''c.dataset.asset=a.id;c.dataset.famille=a.collection??'origine';if(a.palette)c.dataset.palette=a.palette;c.setAttribute'''),
  ("'Aucun meuble ne correspond.'", "'Aucun objet ne correspond à ces filtres.'"),
  ("$('download-ground').disabled=s.page!=='atelier';", "$('download-ground').disabled=s.page!=='atelier'||dataFor().some(o=>assets.get(o.meuble).previewOnly);"),
  ('''const o=[...dataFor()].reverse().find''', '''const o=ordered(dataFor()).reverse().find'''),
  ('''  $('export-note').textContent='Le jeu n’est jamais modifié par le navigateur. Ouvre ce HTML directement si l’aperçu intégré bloque un téléchargement.';
  $('download-ground').querySelector('small').textContent=s.page==='atelier'?'Copie native sans verdure, avec les meubles posés.':'Ouvre une salle pour exporter sa carte.';''',
   '''  const virt=dataFor().some(o=>assets.get(o.meuble).previewOnly);
  $('export-note').textContent=virt&&s.page==='atelier'?'Les nouvelles variantes et les lianes sont des éléments d’aperçu. Choisis PNG ou JSON pour les conserver.':'Le jeu n’est jamais modifié par le navigateur. Ouvre ce HTML directement si l’aperçu intégré bloque un téléchargement.';
  $('download-ground').querySelector('small').textContent=s.page!=='atelier'?'Ouvre une salle pour exporter sa carte.':virt?'Indisponible avec les 100 variantes d’atelier.':'Objets d’origine seulement · n’inclut pas les lianes ni la lumière.';'''),
  ('''const r=s.room,i=s.phase,v=viewport(),items=[...dataFor()];const bits=[...r.m[i],...items.map(o=>sprite(assets.get(o.meuble),i,r))];''',
   '''const r=s.room,i=s.phase,v=viewport(),items=[...dataFor()],lianes=s.lianes;const bits=[...r.m[i],...lianesAt(r,i,lianes),...items.map(o=>sprite(assets.get(o.meuble),i,r))];'''),
  ('''drawScene(out.getContext('2d'),r,i,v,{items});''', '''drawScene(out.getContext('2d'),r,i,v,{items,lianes});'''),
  ("(s.mode==='plan'?'':'-sud')+'.png'", "(s.mode==='plan'?'':'-sud')+(lianes?'-lianes':'')+'.png'"),
  ('''  const name=r.id+'.rsground';''',
   '''  if(items.some(o=>assets.get(o.meuble).previewOnly))throw new Error('Les nouvelles variantes ne sont pas installées dans Destiny. Exporte un PNG ou un JSON.');
  const name=r.id+'.rsground';'''),
  ('''/*@GALERIE@*/''', read(S/'Lianes.js')+'\n'+chapter),
 ])
 html=edit(read(A/'Atelier.gabarit.html'),[
  ('<title>La guilde de Destiny · Atlas des 15 salles</title>', '<title>Destiny · Lianes de Reverie &amp; mobilier PMU</title>') if '<title>La guilde de Destiny · Atlas des 15 salles</title>' in read(A/'Atelier.gabarit.html') else
  (re.search(r'<title>.*?</title>',read(A/'Atelier.gabarit.html')).group(0),'<title>Destiny · Lianes de Reverie &amp; mobilier PMU</title>'),
  ('''  <symbol id="i-trash"''','''  <symbol id="i-leaf" viewBox="0 0 24 24"><path d="M4 20c2-5 5-7 10-10m-7 6C1 8 12 4 20 4c0 9-3 17-13 12Z"/></symbol>
  <symbol id="i-trash"'''),
  ('id="import" class="top-action" type="button"', 'id="import" class="top-action" type="button" aria-label="Ouvrir un plan" title="Ouvrir un plan"'),
  ('id="export" class="top-action filled" type="button"', 'id="export" class="top-action filled" type="button" aria-label="Exporter" title="Exporter"'),
  ('PLANS NATIFS <i></i> SANS VERDURE','PLANS NATIFS <i></i> LIANES INSPIRÉES DE REVERIE'),
  ('Explore les quinze salles et retrouve les chemins d’origine, avec le cadrage des sorties sud corrigé.', 'Des lianes inspirées de Reverie suivent les boiseries. À la nuit, leurs bourgeons éclairent murs et planchers. À toi de placer le mobilier.'),
  ('<div><strong>07</strong><span>SORTIES SUD</span></div>', '<div><strong>100</strong><span>VARIANTES</span></div>'),
  ('    <span class="atlas-nav-note">Lumières de Grodoudou · Cadrage sans rallonge</span>',
   '''    <button id="toggle-lianes" class="soft foliage-toggle" type="button" aria-pressed="true" title="Afficher ou masquer toutes les lianes et leur lumière"><svg><use href="#i-leaf"/></svg><span>Lianes : avec</span></button>
    <span class="atlas-nav-note">Lumières de Grodoudou · 7 sorties sud corrigées</span>'''),
  ('<span id="dim" class="dim">512 × 384 px</span>', '<div class="room-stage-meta"><span id="dim" class="dim">512 × 384 px</span><span id="foliage-status" class="foliage-status"></span></div>'),
  ('<span class="pill">33</span>', '<span class="pill" id="catalog-count">100</span>'),
  ('''      <div class="palette-controls">
''','''      <div class="palette-controls">
        <div class="catalog-selects">
          <label>Collection<select id="collection"><option value="pmu100">100 variantes</option><option value="origine">Banque d’origine · 33</option></select></label>
          <label>Palette<select id="palette-pmu"><option value="tout">Toutes les palettes</option><option value="miel">Chêne &amp; miel</option><option value="grenat">Noyer &amp; grenat</option><option value="sauge">Châtaigne &amp; sauge</option><option value="ardoise">Bois fumé &amp; ardoise</option></select></label>
        </div>
'''),
  ('Décor sans verdure · ambiance actuelle','Décor · ambiance et lianes sélectionnées'),
  ('<p><b>En jeu.</b> L’aperçu n’installe rien. La copie de carte masque la verdure et ajoute ton mobilier. Installe le correctif de cadrage avant de remplacer une carte et garde les fichiers d’origine.</p>',
   '<p><b>Lianes.</b> Bascule « Lianes : avec / sans » pour retrouver les salles sans végétation. En Nuit, les bourgeons projettent une lumière chaude sur le bois.</p><p><b>En jeu.</b> L’aperçu n’installe rien. Les 100 variantes et les lianes ne sont pas exportées vers Destiny. La copie native reste disponible uniquement avec les 33 objets d’origine et sans verdure.</p>'),
  ('Destiny 0.7.7 · Plans natifs · Aperçu hors ligne', 'Destiny 0.7.7 · Plans natifs, calques d’atelier · Aperçu hors ligne'),
 ])
 for token,body in {'CSS':read(A/'Atelier.css')+'\n'+read(A/'Galerie.css')+'\n'+read(S/'Lianes.css'), 'JS':js,'DONNEES':json.dumps(data,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')}.items():
  html=edit(html,[(f'/*@{token}@*/',body)])
 TARGET.write_text(html,encoding='utf-8');(W/'Apercu.js').write_text(js,encoding='utf-8')
 assert ORIGINAL.read_bytes()==base_bytes
 print('PASS · aperçu autonome ·',TARGET.name,TARGET.stat().st_size,'octets · atlas de référence intact.',flush=True)

if __name__=='__main__':main()
