#!/usr/bin/env python3
"""Intègre la bibliothèque offline dans une copie de la guilde Destiny validée."""
from pathlib import Path
from io import BytesIO
from PIL import Image
import numpy as np
import argparse, base64, hashlib, json, re

S = Path(__file__).resolve().parent
O = S.parent
G = O.parent
BASE = G/'Guilde-Destiny-Bourgeons-PMD.html'
TARGET = G/'Guilde-Destiny-Mobilier-Halcyon.html'
SHA = 'ed187565fec4cfe2a98ec2c342e5112296222ee6a4ab82b8f67a173dc2d2dc13'
OPEN = '<script id="donnees" type="application/json">'
CARTES = {
 'guild_second_floor':'Deuxième étage', 'guild_third_floor_lobby':'Salon du troisième étage', 'guild_guildmasters_room':'Bureau du maître',
 'guild_dining_room':'Réfectoire', 'guild_bedroom_hallway':'Couloir des chambres', 'guild_storage_room':'Réserve',
 'guild_top_left_bedroom':'Chambre nord-ouest','guild_top_right_bedroom':'Chambre nord-est',
 'guild_bottom_left_bedroom':'Chambre sud-ouest','guild_bottom_right_bedroom':'Chambre sud-est',
 'guild_heros_room':'Chambre du héros','metano_inn':'Auberge de Metano',
}


def lire(f):return f.read_text(encoding='utf-8')
def digest(b):return hashlib.sha256(b).hexdigest()
def to64(b):return base64.b64encode(b).decode('ascii')

def mod(s,a,b):
    if s.count(a)!=1: raise ValueError(f'Ancre prévue une fois, trouvée {s.count(a)} : {a[:140]}')
    return s.replace(a,b,1)

def base64_parquet(d):
    r=next(r for r in d['rooms'] if r['id']=='guilde_destiny_refectoire')
    im=Image.open(BytesIO(base64.b64decode(r['base'].split(',')[-1]))).convert('RGB').crop((120,200,440,328))
    lut=np.asarray(d['lumieres'][r['nuit']][0]['lut'],dtype='uint8')
    a=np.asarray(im);out=Image.fromarray(lut[np.arange(3)[None,None,:],a]);b=BytesIO();out.save(b,format='PNG',optimize=True)
    return to64(b.getvalue())


def main():
    arg=argparse.ArgumentParser(description=__doc__);arg.add_argument('--source',type=Path,default=BASE);arg.add_argument('--sortie',type=Path,default=TARGET);opt=arg.parse_args()
    source=opt.source.read_bytes();assert digest(source)==SHA, 'Le socle « Bourgeons PMD » doit rester la version validée.'
    assert opt.source.resolve()!=opt.sortie.resolve()
    html,b=source.decode('utf-8').split(OPEN,1);js,tail=b.split('</script>',1)
    old=json.loads(js);index=json.loads(lire(O/'Index.json'));data=dict(old);models={m['id']:m for m in index['models']}
    var=[]
    for v in index['variantes']:
        m=models[v['modele']];b=(O/v['png']).read_bytes();assert v['sha256']==digest(b)
        var.append({'n':max((t.get('n') or 0) for t in old['catalog'])+len(var)+1,'id':v['id'],'label':v['nom']+' · '+v['nom_palette'],
                    'category':m['categorie'],'wall':m['famille']=='Décor mural','w':v['w'],'h':v['h'],
                    'palette':v['palette'],'collection':'halcyon' if m['origine']=='guilde' else 'metano',
                    'previewOnly':True,'halcyon':m['id'],'m':[to64(b)]})
    assert len(var)==490 and len(old['catalog'])==157
    data['catalog']=old['catalog']+var
    assert len({a['id'] for a in data['catalog']})==len(data['catalog'])
    data['halcyon']={**index['source'],'palettes':index['palettes'],'cartes':CARTES,'bois':base64_parquet(old),
            'modele':[{k:m[k] for k in ('id','nom','famille','origine','salle')}|{'png':to64((O/m['source_png']).read_bytes())} for m in index['models']],
            'demo':{'salle':'guilde_destiny_refectoire','zone':{'x':96,'y':48,'w':368,'h':236},
                    'pose':[['banniere',143,50],['nappe-sol',196,194],['banquet',203,196],['plante-haute',395,149],['coffre-haut',133,203],['tonneau',385,239],['plante-fleurie',411,246]]}}

    a=re.search(r'<title>.*?</title>',html).group(0);html=mod(html,a,'<title>Destiny · Mobilier de Halcyon</title>')
    edits = [
      ('PLANS NATIFS <i></i> LUMIÈRE DES BOURGEONS','ATELIER HALCYON <i></i> TEINTES DESTINY'),
      ('La guilde de Destiny<span>.</span>','Le mobilier de Destiny<span>.</span>'),
      ('Le halo de Grodoudou et le tapis PMU sont posés sur le seuil de l’Accueil. Dans les salles, les bourgeons conservent leur lumière tamisée en mode Nuit.',
       '490 variantes pixel art : 420 de la guilde de Halcyon et 70 de l’auberge de Metano. Essaie-les dans les quinze salles de Destiny, de jour comme de nuit.'),
      ('<div><strong>15</strong><span>SALLES</span></div><div><strong>42</strong><span>POTEAUX HABILLÉS</span></div><div><strong>04</strong><span>AMBIANCES</span></div>',
       '<div><strong>49</strong><span>MODÈLES</span></div><div><strong>10</strong><span>PALETTES</span></div><div><strong>490</strong><span>VARIANTES</span></div>'),
      ('    <button id="tab-all" class="soft" type="button" aria-pressed="true">',
       '    <button id="tab-halcyon" class="soft" type="button" aria-pressed="true"><svg aria-hidden="true"><use href="#i-guilde"/></svg><span>Mobilier Halcyon</span></button>\n    <button id="tab-all" class="soft" type="button" aria-pressed="false">'),
      ('<aside class="panel palette" aria-label="Catalogue de mobilier PMU">','<aside class="panel palette" aria-label="Catalogue de mobilier">'),
      ('<h2>Mobilier PMU</h2></div><span class="pill" id="catalog-count">24</span>', '<h2 id="editor-bank-name">Mobilier Halcyon</h2></div><span class="pill" id="catalog-count">42</span>'),
      ('<option value="drapeaux" selected>Drapeaux et tentures · 24</option>', '<option value="halcyon" selected>Guilde Halcyon · 420</option><option value="metano">Auberge de Metano · 70</option><option value="drapeaux">Drapeaux et tentures · 24</option>'),
      ('aria-label="Rechercher un meuble PMU"','aria-label="Rechercher un meuble"'),
      ('Choisis un objet PMU à droite pour commencer.','Choisis un objet à droite pour commencer.'),
      ('Le fond reste brun.', 'Les fonds sont bleus, d’après les intérieurs de Grodoudou.'),
      ('choisis un objet PMU puis clique', 'choisis une variante Halcyon ou un objet PMU puis clique'),
      ('Les 100 variantes, les nouveaux ornements et les lianes ne sont pas exportés vers Destiny.', 'Les variantes Halcyon et PMU, les nouveaux ornements et les lianes ne sont pas exportés vers le jeu.'),
    ]
    for x,y in edits: html=mod(html,x,y)
    html=mod(html,'  </nav>\n', '  </nav>\n'+lire(S/'Catalogue.html'))
    # Le fichier de base a un bloc CSS principal, qui garde ses variables et règles d’atelier.
    html=mod(html,'</style>','\n'+lire(S/'Catalogue.css')+'\n</style>')
    edits_js=[
      ("pmd-destiny:guilde:nuit-vivante:077:v1", "pmd-destiny:guilde:mobilier-halcyon:077:v1"),
      ("page:'atlas',room:data.rooms[0]", "page:'halcyon',room:data.rooms[0]"),
      ("collection:'drapeaux',palette:'tout'", "collection:'halcyon',palette:'lierre'"),
      ("{atlas:'tab-all',sud:'tab-south',atelier:'tab-work'}", "{halcyon:'tab-halcyon',atlas:'tab-all',sud:'tab-south',atelier:'tab-work'}"),
      ("  $('editor').hidden=!atelier;$('atlas-page').hidden=atelier;updateFilm();updateSeuil();updateGrille();",
       "  const hal=s.page==='halcyon';$('halcyon-page').hidden=!hal;halPhaseButtons();\n  $('editor').hidden=!atelier;$('atlas-page').hidden=atelier||hal;updateFilm();updateSeuil();updateGrille();"),
      ("  if(s.page!=='atelier'){paintAtlas();return;}", "  if(s.page==='halcyon'){halPaint();return;}\n  if(s.page!=='atelier'){paintAtlas();return;}"),
      ("function drawMotion(){\n  if(s.page!=='atelier'){", "function drawMotion(){\n  if(s.page==='halcyon'){if(s.phase===3&&s.lianes&&inWindow($('hal-scene')))halPaint();return;}\n  if(s.page!=='atelier'){"),
      ("s.collection=$('collection').value;s.palette='tout';$('palette-pmu').value='tout';$('palette-pmu').disabled=s.collection==='origine';", "editorBank($('collection').value);"),
      ("    panel.append(make('span','inspect-coords','X '+o.x+' · Y '+o.y));const actions", "    panel.append(make('span','inspect-coords','X '+o.x+' · Y '+o.y));halRecolor(panel,o);const actions"),
      ("Choisis un objet PMU à droite pour commencer.", "Choisis un objet à droite pour commencer."),
      ("Objet PMU inconnu ou identifiant en double.", "Objet inconnu ou identifiant en double."),
      ("Mon-plan-PMU-Destiny-077.json", "Mon-plan-Destiny-077.json"),
      ('setupGrille();setupSeuil();setupAtlas();updatePalette();refresh();setupMotion();', lire(S/'Catalogue.js')+'\nsetupGrille();setupSeuil();setupAtlas();setupHalcyon();updatePalette();refresh();setupMotion();'),
    ]
    for x,y in edits_js:tail=mod(tail,x,y)
    dat=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    opt.sortie.write_text(html+OPEN+dat+'</script>'+tail,encoding='utf-8')
    assert opt.source.read_bytes()==source
    print(f'PASS · {len(old["rooms"])} salles et {len(old["catalog"])} entrées préexistantes intactes · +{len(var)} entrées Halcyon · {opt.sortie.stat().st_size:,} o')

if __name__=='__main__':main()
