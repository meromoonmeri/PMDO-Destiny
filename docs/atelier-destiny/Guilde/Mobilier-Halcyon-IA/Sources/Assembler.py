#!/usr/bin/env python3
"""Ajoute le rayon IA dans une copie autonome de l'atelier Halcyon, sans écraser l'original."""
from pathlib import Path
import hashlib,base64,json
S=Path(__file__).resolve().parent;O=S.parent;G=O.parent
BASE=G/'Guilde-Destiny-Mobilier-Halcyon.html';OUT=G/'Guilde-Destiny-Mobilier-Halcyon-IA.html'
SHA='a45b4f07580fe23648bc2f0e5a3f77b6a2f552e62c2c9415cfb677db9c871e5a'
OPEN='<script id="donnees" type="application/json">'

def check(b):return hashlib.sha256(b).hexdigest()
def inject(s,old,new):
    assert s.count(old)==1,(s.count(old),old)
    return s.replace(old,new,1)

def pack(p,expected):
    raw=p.read_bytes();assert check(raw)==expected
    return base64.b64encode(raw).decode('ascii')

def main():
    raw=BASE.read_bytes();assert check(raw)==SHA
    html,b=raw.decode().split(OPEN,1);dat,js=b.split('</script>',1);d=json.loads(dat)
    index=json.loads((O/'Index.json').read_text());byid={m['id']:m for m in index['modeles']}
    source={m['id']:m for m in d['halcyon']['modele']}
    assert len(index['variantes'])==30 and len(byid)==3
    d['halcyon']['modele'] += [dict(id=m['id'],nom=m['titre'],famille='Meubles',origine='ia',salle=m['salle'],png=source[m['souche']]['png'],choix=m['palette'],detail=m['note'],source_taille=m['rect_source'][2:4]) for m in index['modeles']]
    d['halcyon']['demo']['pose']=[['banniere',143,50],['nappe-sol',196,194],['ia-banquet',203,197],['ia-bureau',394,142],['ia-coffre',132,218],['tonneau',385,240],['plante-fleurie',410,245]]
    k=max(a.get('n',0) for a in d['catalog']);d['catalog']+= [dict(n=k+i,id=v['id'],label=v['nom']+' · '+v['nom_palette'],category='meubles',wall=False,w=v['w'],h=v['h'],palette=v['palette'],collection='halcyon-ia',previewOnly=True,halcyon=v['modele'],generation=v['traitement'],m=[pack(O/v['png'],v['sha256'])]) for i,v in enumerate(index['variantes'],1)]
    assert len({a['id'] for a in d['catalog']})==len(d['catalog'])==677
    h=[
     ('<title>Destiny · Mobilier de Halcyon</title>','<title>Destiny · Mobilier Halcyon — Série IA</title>'),
     ('ATELIER HALCYON <i></i> TEINTES DESTINY','GÉNÉRATEUR D’IMAGE <i></i> MODÈLES HALCYON'),
     ('Le mobilier de Destiny<span>.</span>','Mobilier Halcyon · Série IA<span>.</span>'),
     ('490 variantes pixel art : 420 de la guilde de Halcyon et 70 de l’auberge de Metano. Essaie-les dans les quinze salles de Destiny, de jour comme de nuit.',
      'Trois meubles passés au générateur d’image à partir des sprites de Halcyon. Les versions choisies sont détourées, adaptées en pixel art et déclinées dans les teintes de Destiny.'),
     ('<div><strong>49</strong><span>MODÈLES</span></div><div><strong>10</strong><span>PALETTES</span></div><div><strong>490</strong><span>VARIANTES</span></div>',
      '<div><strong>3</strong><span>GÉNÉRATIONS</span></div><div><strong>10</strong><span>PALETTES</span></div><div><strong>30</strong><span>SPRITES IA ET DÉRIVÉS</span></div>'),
     ('<span>Mobilier Halcyon</span></button>','<span>Catalogue Halcyon</span></button>'),
     ('Collection 01 · Halcyon','Édition IA · trois sélections'),
     ('Des meubles pour les salles de Destiny','Les trois meubles générés'),
     ('Les silhouettes originales de la guilde de Halcyon, recolorées pour le parquet, les ronces et les nuits bleues de Destiny. L’auberge de Metano a son propre rayon.',
      'La table de banquet en Lierre, le grand coffre en Minuit et le bureau aux parchemins en Ronce. Trois dessins générés, puis neuf autres teintes par dessin.'),
     ('Réfectoire · exemple, rien n’est posé','Réfectoire · essai visuel, aucun placement ajouté'),
     ('Pixels natifs 1×','Sprites à l’échelle 1×'),
     ('<p id="hal-note-tone" aria-live="polite"></p>','<div class="hal-selected-note"><p id="hal-note-tone" aria-live="polite"></p><button id="hal-chosen" type="button" class="hal-outline" aria-pressed="true">Teintes choisies</button></div>'),
     ('ORIGINAUX HALCYON · TEINTES DESTINY','SÉRIE IA À PART DES SPRITES ORIGINAUX'),
     ('          <a id="hal-source"','          <p id="hal-ia-note" class="hal-ia-note" hidden></p>\n          <a id="hal-source"'),
     ('Les meubles de cette collection sont distincts de la banque PMU.','Les trois modèles IA sont des interprétations guidées par ces sprites, pas des découpes d’origine. Les autres rayons gardent les 490 variantes précédentes.'),
     ('<h2 id="editor-bank-name">Mobilier Halcyon</h2></div><span class="pill" id="catalog-count">42</span>',
      '<h2 id="editor-bank-name">Créations IA</h2></div><span class="pill" id="catalog-count">30</span>'),
     ('<option value="halcyon" selected>Guilde Halcyon · 420</option>', '<option value="halcyon-ia" selected>Créations IA · 30</option><option value="halcyon">Guilde Halcyon · 420</option>'),
    ]
    for a,b in h:html=inject(html,a,b)
    css='''
.hal-selected-note{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.hal-selected-note .hal-outline{min-height:30px;font-size:11px}.hal-selected-note [aria-pressed=true]{border-color:#e4c68e;background:#4d4230;color:#ffebc4}
.hal-ia-note{font:11px/1.45 var(--sans);color:#c6bda9;margin:7px 0 0}.hal-card-copy small.made-ia{color:#dfceaf}.hal-shelf:has(.hal-card[data-ia=true]) .hal-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
@media(max-width:770px){.hal-shelf:has(.hal-card[data-ia=true]) .hal-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''
    html=inject(html,'</style>',css+'\n</style>')
    t=[
      ("pmd-destiny:guilde:mobilier-halcyon:077:v1","pmd-destiny:guilde:mobilier-halcyon-ia:077:v1"),
      ("const halState={palette:'lierre',origine:'guilde',family:'',q:'',page:0,model:'banquet',", "halTones.set('selection',{nom:'Teintes choisies',accord:'Table Lierre · coffre Minuit · bureau Ronce'});\nconst halState={palette:'selection',origine:'ia',family:'',q:'',page:0,model:'ia-banquet',"),
      ("const halOrigins=[['guilde','Guilde de Halcyon']", "const halOrigins=[['ia','Créations IA'],['guilde','Guilde de Halcyon']"),
      ("const halAsset=(m,p=halState.palette)=>assets.get('halcyon-'+m.id+'-'+p);", "const halAsset=(m,p=halState.palette)=>assets.get('halcyon-'+m.id+'-'+(p==='selection'?(m.choix??'lierre'):p));"),
      ("const hal=['halcyon','metano'].includes(collection);", "const hal=['halcyon-ia','halcyon','metano'].includes(collection);"),
      ("const source=hal?[...halTones.values()].map(p=>[p.id,p.nom]):oldTones;", "const source=hal?halData.palettes.map(p=>[p.id,p.nom]):oldTones;"),
      ("(collection==='halcyon'?'Mobilier Halcyon':'Auberge de Metano')", "(collection==='halcyon-ia'?'Créations IA':collection==='halcyon'?'Mobilier Halcyon':'Auberge de Metano')"),
      ("  $('hal-scene-tone').textContent=tone.nom;", "  $('hal-scene-tone').textContent=tone.nom;$('hal-chosen').setAttribute('aria-pressed',String(halState.palette==='selection'));"),
      ("  $('hal-count').textContent=`${found.length} modèle${found.length===1?'':'s'} · palette ${tone.nom}`;", "  $('hal-count').textContent=`${found.length} modèle${found.length===1?'':'s'} · ${tone.nom}`;"),
      ("    c.setAttribute('aria-label',m.nom+' · '+tone.nom);\n    const body=make('span','hal-card-copy');body.append(make('b','',m.nom),make('small','',m.origine==='metano'?'Auberge · '+m.famille:m.famille));",
       "    c.setAttribute('aria-label',m.nom+' · '+halTones.get(a.palette).nom);c.dataset.ia=String(m.origine==='ia');\n    const body=make('span','hal-card-copy'),caption=m.origine==='ia'?halTones.get(a.palette).nom+' · '+(a.generation==='generation-detouree'?'Génération retenue':'Teinte dérivée'):m.origine==='metano'?'Auberge · '+m.famille:m.famille;\n    body.append(make('b','',m.nom),make('small',m.origine==='ia'?'made-ia':'',caption));"),
      ("  $('hal-size').textContent=a.w+' × '+a.h+' px';$('hal-detail-name').textContent=m.nom;",
       "  const taille=halState.original&&m.source_taille?m.source_taille:[a.w,a.h];$('hal-size').textContent=taille.join(' × ')+' px';$('hal-detail-name').textContent=m.nom;"),
      ("(m.origine==='metano'?'Auberge':'Guilde');", "(m.origine==='ia'?'Création IA':m.origine==='metano'?'Auberge':'Guilde');\n  const note=$('hal-ia-note');note.hidden=m.origine!=='ia';note.textContent=m.origine==='ia'?(a.generation==='generation-detouree'?'Génération retenue, détourée. ':'Teinte dérivée du dessin généré. ')+m.detail:'';"),
      ("halState.original?'Revenir à la variante':'Voir l’original'", "halState.original?'Revenir à la variante':m.origine==='ia'?'Voir le sprite source':'Voir l’original'"),
      ("!halState.original&&p.id===halState.palette", "!halState.original&&p.id===a.palette"),
      ("  editorBank('halcyon','lierre');halRender();", "  $('hal-chosen').onclick=()=>halPick('selection');editorBank('halcyon-ia','tout');halRender();"),
    ]
    for a,b in t:js=inject(js,a,b)
    data=json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    OUT.write_text(html+OPEN+data+'</script>'+js,encoding='utf-8');assert BASE.read_bytes()==raw
    print('PASS · 30 entrées IA séparées · 490 sprites précédents conservés ·',OUT.stat().st_size,'octets')

if __name__=='__main__':main()
