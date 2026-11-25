#!/usr/bin/env python3
"""Independent offline edition. Keeps the atlas geometry and existing saved plans."""
from pathlib import Path
import importlib.util,json
import Ornements,Video

S=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lumiere_pmd',S/'Lumiere-PMD.py');L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)
FINAL=L.G/'Guilde-Destiny-Bourgeons-PMD.html'


def swap(s,a,b):
 assert s.count(a)==1,(s.count(a),a)
 return s.replace(a,b,1)


JS='''const muralCache=new Map();
function muralLayer(r,p){
  const bit=data.ornements[r.id];if(!s.ornements||!bit)return null;
  const key=r.id+':'+p;
  if(!muralCache.has(key)){
    const [x,y,source]=bit; const n=ambiance(r,p);
    muralCache.set(key,[x,y,n?{source,lut:n.lut,patches:[]}:source]);
  }
  return muralCache.get(key);
}
function frameLueur(ms){return Math.floor(ms*data.canon.ips/1000+1e-7)%data.canon.images;}
function nightBits(r,p,active){
  if(p!==3||!active)return [];
  return data.lianes[r.id].points.flatMap(s=>s.images.flatMap(pair=>pair.map(bit=>bit[2])));
}
function illuminate(c,r,ms){
  const i=frameLueur(ms);c.save();c.globalCompositeOperation='screen';
  for(const p of data.lianes[r.id].points){
    for(const [x,y,b] of p.images[i])drawPicture(c,b,x,y);
  }
  c.restore();
}
'''


def assemble(h,d,t):
 for a,b in [
  ('<title>Destiny · Lueur tamisée</title>','<title>Destiny · Bourgeons — lumière PMD</title>'),
  ('PLANS NATIFS <i></i> LUEUR TAMISÉE','PLANS NATIFS <i></i> LUMIÈRE DES BOURGEONS'),
  ('En mode Nuit, deux bourgeons par salle diffusent une lueur ambrée très légère. Le reflet s’efface sur les planches proches sans masquer les veines du bois.', 'En mode Nuit, la lueur part des bourgeons. Les teintes et le rythme viennent de la falaise nocturne de Grodoudou, avec des reflets tamisés sur les feuilles et le bois proche.'),
  ('Les deux foyers en mouvement','De la falaise aux bourgeons'),
  ('<b>À gauche</b>, la boucle originale des braseros de Grodoudou. <b>À droite</b>, la nouvelle lueur tamisée de Destiny. Regarde le bois au pied des lianes, près des fenêtres.', '<b>À gauche</b>, l’entrée de Grodoudou sur la falaise, de nuit. <b>À droite</b>, les bourgeons de Destiny reprennent les quatre phases de cette lumière, sans braseros dans la salle.'),
  ('<span class="film-note">Sans son · en boucle</span></div>','<span class="film-note">Sans son · détail à 4 s</span></div>\n      <button class="soft" type="button" id="show-salon">Voir les bourgeons dans le Grand Salon</button>'),
  ('Chambre de Grodoudou <span aria-hidden="true">↔</span> Grand Salon de Destiny · mode Nuit, détail agrandi.','Falaise de Grodoudou <span aria-hidden="true">↔</span> Grand Salon de Destiny · teintes et cadence d’origine.'),
  ('RÉFÉRENCE · G01P05C','RÉFÉRENCE · G01P01C'),
  ('<h2 id="braseros-title">Des foyers, pas un voile lumineux</h2>','<h2 id="braseros-title">La falaise de Grodoudou, de nuit</h2>'),
  ('width="408" height="384" alt="Chambre de Grodoudou à la nuit, deux braseros allumés de part et d’autre du tapis"','width="480" height="408" alt="La falaise de la guilde de Grodoudou, deux braseros autour de l’entrée, la nuit"'),
  ('<b>Chambre de Grodoudou</b>Les deux flammes bougent. Le sol et les murs restent fixes.', '<b>Grodoudou · entrée sur la falaise</b>La lumière change sur la pierre près des braseros. Au loin, le chemin testé et le ciel restent fixes.'),
  ('Deux bourgeons de Destiny émettent une lueur très douce. Le bois reste visible à travers le reflet.', 'Les pétales prennent une teinte chaude. Les feuilles coupent la lueur et le bois reste lisible.'),
  ('Dans l’APNG d’origine, les quatre images ne diffèrent qu’autour des deux braseros. Le calque de lueur généré pour Destiny est appliqué à faible opacité sur le bois proche. Aucun brasero ni morceau de salle n’a été recopié.', 'La source G01P01C fournit quatre images et les couleurs observées sur les pierres. Destiny adapte cette lumière aux bourgeons, avec des reflets sous 10 % d’opacité. Les seuls pixels repris à l’intérieur sont des valeurs de couleur, pas les flammes ni le décor.'),
  ('https://projectpokemon.org/home/gallery/image/77578-g01p05cpng/',L.SOURCE),
  ('    <span class="atlas-nav-note">4 ambiances · 7 sorties sud corrigées</span>', '    <button class="soft" type="button" id="toggle-ornements" aria-pressed="false" title="Afficher ou masquer les frises et écussons non lumineux"><svg aria-hidden="true"><use href="#i-grid"/></svg><span>Ornements : sans</span></button>\n    <span class="atlas-nav-note">4 ambiances · 7 sorties sud corrigées</span>'),
 ]:h=swap(h,a,b)
 h=swap(h,'</style>','#show-salon{margin-top:9px;font-size:11px;color:#decfae;border-color:#635c4f;min-height:29px;padding:4px 8px}\n#toggle-ornements[aria-pressed="true"]{border-color:#d4ac73;color:#fff0cf;background:#473925}\n</style>')
 a=t.index('function nightBits(');b=t.index('function spriteForScene(',a);t=t[:a]+JS+t[b:]
 t=swap(t,'lianes:true,tool:null','lianes:true,ornements:false,tool:null')
 t=swap(t,'  if(vines.length&&p===3)illuminate(c,r,ms);','  const mural=muralLayer(r,p);if(mural)drawPicture(c,mural[2],mural[0],mural[1]);\n  if(vines.length&&p===3)illuminate(c,r,ms);')
 t=swap(t,'...r.m[p],...vines,...nightBits','...r.m[p],...vines,...(mural?[mural[2]]:[]),...nightBits')
 t=swap(t,"'Lianes · halos en Nuit'","'Lianes · bourgeons en Nuit'")
 t=swap(t,' foyers sur les poteaux',' bourgeons lumineux')
 t=swap(t,'En mode Nuit, regarde la base des lianes et les premières planches au pied des poteaux.', 'En Nuit, regarde la base des lianes et les premières planches. Les ornements muraux facultatifs n’émettent pas de lumière.')
 t=swap(t,'setupAtlas();updatePalette();refresh();setupMotion();', '''$('show-salon').onclick=()=>{s.phase=3;s.lianes=true;openDepuisAtlas(data.rooms[2]);};
$('toggle-ornements').onclick=()=>{
  s.ornements=!s.ornements;
  const b=$('toggle-ornements');b.setAttribute('aria-pressed',String(s.ornements));
  b.querySelector('span').textContent=s.ornements?'Ornements : avec':'Ornements : sans';
  refresh();
};
setupAtlas();updatePalette();refresh();setupMotion();''')
 return h+L.MARK+json.dumps(d,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')+'</script>'+t


def main():
 h,d,t=L.page();src,tones,gain,report=L.read_reference();L.jsonout(L.OUT/'Releve-Falaise.json',report)
 stats=L.recolour(d,tones,gain)
 d['canon']=dict(image='G01P01C',ips=6,images=4,opacite_reflet_max=25)
 del d['lueur'];d['ornements']=Ornements.decals(d,L.decode,L.pack)
 for r in d['rooms']:
  nf=L.night_frames(r,d)
  assert len({x.tobytes() for x in nf})==4,r['label']
  if r['n']==3:intro=nf
 d['reference']=dict(apng=L.uri(L.AP.read_bytes()),fixe=L.pack(src[0]),salon=L.pack(intro[2]))
 L.jsonout(L.OUT/'Bourgeons-et-reflets.json',dict(statut='PASS',source='G01P01C',salles=15,emetteurs=30,source_unique='texels existants des bourgeons',images=4,cadence_ips=6,reflets_alpha_max_255=max(x[0] for q in stats for x in q['alpha_par_image']),sources=stats))
 print('PASS · 30 sources sur les lianes, sans brasero · 15 salles · plafonds et masques contrôlés.',flush=True)
 Video.build(src,intro)
 d['film']=dict(webm=L.uri(Video.VIDEO.read_bytes(),'video/webm'),mp4=L.uri(Video.MP4.read_bytes(),'video/mp4'),poster=L.uri(Video.POSTER.read_bytes(),'image/webp'))
 FINAL.with_suffix('.tmp').write_text(assemble(h,d,t),encoding='utf8');FINAL.with_suffix('.tmp').replace(FINAL)
 print(f'PASS · HTML autonome : {FINAL.name} · {FINAL.stat().st_size:,} o',flush=True)

if __name__=='__main__':main()
