#!/usr/bin/env python3
"""Build the local-lighting edition with an inspectable, embedded Grodoudou reference."""
from pathlib import Path
from PIL import Image
from io import BytesIO
import json,base64,os,re

import Lueur

S=Path(__file__).resolve().parent;O=S.parent;G=O.parent;W=Path.home()/'.cache/lumiere-braseros'
SRC=G/'Guilde-Destiny-Nuit-Vivante.html';OUT=Path(os.environ.get('DESTINY_ATLAS_STAGE',W/'Lueur-Tamisee-sans-video.html'));MARK='<script id="donnees" type="application/json">'

def pack(b,fmt):return f'data:image/{fmt};base64,'+base64.b64encode(b).decode('ascii')
def still(file):
 im=Image.open(file).convert('RGB');b=BytesIO();im.save(b,'WEBP',lossless=True,method=4);return pack(b.getvalue(),'webp')
def patch(s,a,b):assert s.count(a)==1,(s.count(a),a);return s.replace(a,b,1)

STYLE='''
.atlas-nav .braseros{color:#dcc9a8;border-color:#7c674a;white-space:nowrap}
.atlas-nav .braseros:hover{background:#3e3326;border-color:#c29e67;color:#ffeed2}
#braseros-box{width:min(100% - 22px,920px);max-width:920px;max-height:calc(100dvh - 22px);overflow-y:auto}
.foyers-cols{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:0 0 12px}
.foyers-cols figure{min-width:0;margin:0;border:1px solid var(--line);border-radius:9px;background:#151c19;padding:7px}
.foyers-cols img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:contain;image-rendering:pixelated;border-radius:5px;background:#131925}
.foyers-cols figure:nth-child(2) img{background:#4d3321}
.foyers-cols figcaption{padding:7px 3px 4px;font-size:12px;color:var(--sub)}
.foyers-cols figcaption b{display:block;color:var(--ink);font-size:14px;padding-bottom:3px}
.foyers-cols button{min-height:26px;padding:3px 6px;margin-top:7px;font-size:11px}
.foyers-source{color:var(--jade)}
.foyers-treat{font-size:12px;color:var(--sub);line-height:1.5;margin:0 3px}
@media(max-width:595px){.foyers-cols{grid-template-columns:1fr;gap:8px}.foyers-cols img{max-height:254px}.foyers-cols figcaption b{font-size:12px}}
'''
DIALOG='''<dialog id="braseros-box" aria-labelledby="braseros-title">
  <div class="dialog-head"><div><div class="micro">RÉFÉRENCE · G01P05C</div><h2 id="braseros-title">Des foyers, pas un voile lumineux</h2></div><button class="icon-button close-dialog" aria-label="Fermer"><svg><use href="#i-cross"/></svg></button></div>
  <div class="dialog-body">
    <div class="foyers-cols">
      <figure><img id="grodoudou-fires" width="408" height="384" alt="Chambre de Grodoudou à la nuit, deux braseros allumés de part et d’autre du tapis"><figcaption><b>Chambre de Grodoudou</b>Les deux flammes bougent. Le sol et les murs restent fixes.<br><button class="soft" id="grodoudou-play" aria-pressed="false" type="button">Lire la boucle d’origine</button></figcaption></figure>
      <figure><img id="destiny-foyers" width="576" height="432" alt="Grand Salon de Destiny : deux lueurs discrètes sur les lianes et le bois proche"><figcaption><b>Destiny · Grand Salon</b>Deux bourgeons de Destiny émettent une lueur très douce. Le bois reste visible à travers le reflet.</figcaption></figure>
    </div>
    <p class="foyers-treat">Dans l’APNG d’origine, les quatre images ne diffèrent qu’autour des deux braseros. Le calque de lueur généré pour Destiny est appliqué à faible opacité sur le bois proche. Aucun brasero ni morceau de salle n’a été recopié. <a class="foyers-source" href="https://projectpokemon.org/home/gallery/image/77578-g01p05cpng/" target="_blank" rel="noopener">Fiche de la référence ↗</a></p>
  </div>
</dialog>
'''
JS='''function nightBits(r,p,active){
  if(p!==3||!active)return [];
  const q=data.lianes[r.id];return [q.reflets[2],...q.points.flatMap(l=>[l.l[2],l.b[2]])];
}
const lightSpot=(c,[x,y,image],alpha)=>{c.globalAlpha=alpha;drawPicture(c,image,x,y);};
function lightLevel(ms,source){
  const loop=data.lueur;
  const w=TAU*(ms%loop.ms)/loop.ms;
  return loop.milieu+loop.amplitude*Math.sin(w+source.p)+loop.harmonique*Math.sin(2*w-source.p+loop.decalage);
}
function illuminate(c,r,ms){
  const q=data.lianes[r.id];c.save();
  const values=q.points.map(s=>lightLevel(ms,s));
  c.globalCompositeOperation='screen';
  q.points.forEach((s,i)=>lightSpot(c,s.l,values[i]));
  c.globalCompositeOperation='source-over';lightSpot(c,q.reflets,1);
  c.globalCompositeOperation='screen';
  q.points.forEach((s,i)=>lightSpot(c,s.b,values[i]));
  c.restore();
}
'''
REF_INIT='''
const refBox=$('braseros-box'),refButton=$('grodoudou-play'),fire=$('grodoudou-fires');
function showFlames(active){
  fire.src=active?data.reference.apng:data.reference.fixe;
  refButton.setAttribute('aria-pressed',String(active));
  refButton.textContent=active?'Figer la boucle':'Lire la boucle d’origine';
}
$('braseros-reference').onclick=()=>{
  $('destiny-foyers').src=data.reference.salon;showFlames(false);refBox.showModal();
};
refButton.onclick=()=>showFlames(refButton.getAttribute('aria-pressed')!=='true');
refBox.addEventListener('close',()=>showFlames(false));
'''

def main():
 initial=SRC.read_bytes();head,rest=initial.decode('utf-8').split(MARK,1);body,tail=rest.split('</script>',1);original=json.loads(body);d=dict(original)
 d['lianes']=json.loads((W/'Ancrages.json').read_bytes());d['reference']=dict(apng=pack((W/'Grodoudou-original.apng').read_bytes(),'png'),fixe=still(W/'Grodoudou-original.apng'),salon=still(W/'Destiny-source-03.png'))
 del d['cadence'];d['lueur']=Lueur.CYCLE
 for r in d['rooms']:
  f=d['lianes'][r['id']];base=original['lianes'][r['id']];assert f['s']==base['s'] and f['t']==base['t'] and f['v']==base['v'] and len(f['points'])==2
 head=patch(head,'<title>Destiny · Nuit vivante</title>','<title>Destiny · Lueur tamisée</title>')
 head=patch(head,'</style>',STYLE+'\n</style>')
 head=patch(head,'PLANS NATIFS <i></i> ÉDITION NUIT VIVANTE','PLANS NATIFS <i></i> LUEUR TAMISÉE')
 head=patch(head,'Les lianes s’enroulent autour des poteaux. À la nuit, leurs bourgeons respirent en douceur et les ombres de feuillage glissent sur le bois. Essaie les étoffes animées dans Aménager.', 'En mode Nuit, deux bourgeons par salle diffusent une lueur ambrée très légère. Le reflet s’efface sur les planches proches sans masquer les veines du bois.')
 head=patch(head,'    <span class="atlas-nav-note">4 ambiances · 7 sorties sud corrigées</span>','    <button class="soft braseros" id="braseros-reference" type="button"><svg><use href="#i-help"/></svg><span>Référence Grodoudou</span></button>\n    <span class="atlas-nav-note">4 ambiances · 7 sorties sud corrigées</span>')
 head=patch(head,'<div class="toast" id="toast"',DIALOG+'<div class="toast" id="toast"')
 head=patch(head,'Les enroulements laissent le bois des poteaux apparent. En Nuit, les halos et les ombres varient lentement, sans flash.', 'Les enroulements laissent le bois des poteaux apparent. En mode Nuit, les lueurs à faible opacité varient doucement sans que la salle s’éclaircisse dans son ensemble.')
 a=tail.index('function nightBits(');b=tail.index('function spriteForScene(',a);tail=tail[:a]+JS+tail[b:]
 tail=patch(tail,'''`Nuit · ${data.lianes[s.room.id].n} bourgeons lumineux`''','''`Nuit · ${data.lianes[s.room.id].points.length} foyers sur les poteaux`''')
 tail=patch(tail,'Poutres, poteaux et rives habillés de lianes. En Nuit, regarde le jeu de lumière sur les planches.', 'En mode Nuit, regarde la base des lianes et les premières planches au pied des poteaux.')
 tail=patch(tail,'setupAtlas();updatePalette();refresh();setupMotion();',REF_INIT+'\nsetupAtlas();updatePalette();refresh();setupMotion();')
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(head+MARK+json.dumps(d,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')+'</script>'+tail,encoding='utf-8');assert SRC.read_bytes()==initial
 m=re.search(r'<script>(.*)</script>\s*</body>',tail,re.S);assert m;(W/'Lumiere.js').write_text(m[1],encoding='utf-8')
 print('PASS · nouvel atlas indépendant',OUT.name,OUT.stat().st_size,'octets · masques, poteaux, cartes et étoffes conservés',flush=True)
if __name__=='__main__':main()
