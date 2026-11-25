#!/usr/bin/env python3
"""Prototype isolé d'un Ground de guilde. Ne modifie aucun jeu ou index existant."""
from pathlib import Path
from PIL import Image,ImageDraw
from collections import deque
import numpy as np, json, copy, io, struct, zipfile, sys
R=Path(__file__).resolve().parent
C=R/'candidat-isole';ground=C/'Data/Ground';tiles=C/'Content/Tile';ground.mkdir(parents=True,exist_ok=True);tiles.mkdir(parents=True,exist_ok=True)
if (ground/'guilde_cliff_essai_jour.rsground').exists():raise SystemExit('Candidat déjà présent : préserver la version existante.')
with zipfile.ZipFile('/home/user/chantier-grand-cap-nuit/sauvegardes-originales.zip') as z:doc=json.loads(z.read('grand-cap-nuit-original.rsground'))
o=doc['Object'];old=copy.deepcopy(o);W,H=480,520;tw,th=W//8,H//8
scene=Image.open('/home/user/chantier-cliff-raccords-qg/cliff-jour-phase00.png').convert('RGBA');assert scene.size==(W,H)
qg=Image.open(R/'qg-fond-porte-ouverte-transparent.png').convert('RGBA');door=Image.open(R/'porte-00.png').convert('RGBA');assert qg.size==(224,224) and door.size==(48,48)
objects=Image.new('RGBA',(W,H));objects.alpha_composite(qg,(128,120))
doors=Image.new('RGBA',(W,H));doors.alpha_composite(door,(216,271))
# Un tileset autonome à cellules 8×8 : seules les cellules entièrement
# transparentes sont omises ; aucune interpolation au découpage.
name='Destiny_GuildeCliff_Essai_Jour_059';uniques=[];lookup={}
def refs_for(img):
 refs={}
 for x in range(tw):
  for y in range(th):
   t=img.crop((x*8,y*8,x*8+8,y*8+8))
   if t.getchannel('A').getbbox() is None:continue
   b=t.tobytes()
   if b not in lookup:lookup[b]=len(uniques);uniques.append(t)
   refs[(x,y)]=lookup[b]
 return refs
references=[refs_for(im) for im in (scene,objects,doors)]
header=8+16*len(uniques);body=bytearray();rows=[]
for i,t in enumerate(uniques):
 b=io.BytesIO();t.save(b,format='PNG');p=b.getvalue();rows.append((i%32,i//32,header+len(body)));body+=struct.pack('<q',len(p))+p
(tiles/(name+'.tile')).write_bytes(struct.pack('<ii',8,len(uniques))+b''.join(struct.pack('<iiq',*r) for r in rows)+body)
# Préserver les autres attributs de Ground du gabarit, mais construire trois
# couches autonomes de dimensions appropriées et sans références à l'ancien décor.
layer_template=old['Layers'][0]; blank=copy.deepcopy(layer_template['Tiles'][0][0]);blank['AutoTileset']='';blank['Associates']=[];blank['NeighborCode']=-1;blank['Layers']=[]
layers=[]
for lname,refs in zip(('00_Scene_Jour_Fixe','01_QG_Porte_Ouverte','02_Porte_Fermee'),references):
 layer={k:copy.deepcopy(v) for k,v in layer_template.items() if k!='Tiles'};layer.update(Name=lname,Layer=0,Visible=True)
 columns=[]
 for x in range(tw):
  col=[]
  for y in range(th):
   cell=copy.deepcopy(blank)
   if (x,y) in refs:
    i=refs[(x,y)];cell['Layers']=[{'Frames':[{'Sheet':name,'TexLoc':{'X':i%32,'Y':i//32}}],'FrameLength':60}]
   col.append(cell)
  columns.append(col)
 layer['Tiles']=columns;layers.append(layer)
o['Layers']=layers
# Marge intérieure et marche : entrée sous la porte, couloir d'escalier en bas.
# Le bâtiment et le vide ne sont pas traversables. Masque conservateur qui doit
# être vérifié au moteur : il n'a pas été dessiné à la main en mode dev.
# L'herbe appartient aux couleurs claires vert-jaune, et l'objet opaque n'est
# pas traversable. Les marches dégagent un couloir central jusqu'au seuil.
scene_rgb=np.asarray(scene)[:,:,:3].astype('int16')
grass=(scene_rgb[:,:,0]>130)&(scene_rgb[:,:,1]>scene_rgb[:,:,0]+5)&(scene_rgb[:,:,2]<120)
object_alpha=np.asarray(objects.getchannel('A'))
obstacles=[]
for x in range(tw):
 col=[]
 for y in range(th):
  pixels=grass[y*8:y*8+8,x*8:x*8+8]
  occupied=object_alpha[y*8:y*8+8,x*8:x*8+8]
  free=bool(pixels.sum()>=56 and (occupied>0).sum()<=4)
  if 27<=x<=32 and y>=43:free=True
  col.append({'Bounds':{'X':x*8,'Y':y*8,'Width':8,'Height':8},'Tags':0 if free else 1})
 obstacles.append(col)
o['obstacles']=obstacles;o['AssetName']='guilde_cliff_essai_jour';o['Name']={'DefaultText':'Guilde Cliff — essai jour','LocalTexts':{'fr':'Guilde Cliff — essai jour'}}
o['Comment']='Essai isolé : guilde fermée, ciel fixe, non raccordé, aucune validation en jeu.'
o['Background']=copy.deepcopy(old['Background']);o['Decorations']=[{'Name':'New Deco','Layer':0,'Visible':True,'Anims':[]}]
ents=copy.deepcopy(old['Entities']); assert len(ents)==1
for ent in ents[0]['Spawners']:
 if ent['EntName']=='PLAYER':ent['Collider'].update(X=224,Y=472)
 elif ent['EntName']=='TEAMMATE_1':ent['Collider'].update(X=248,Y=472)
for ent in ents[0]['Markers']:
 if ent['EntName']=='Entrance':ent['Collider'].update(X=224,Y=472)
o['Entities']=ents
p=ground/'guilde_cliff_essai_jour.rsground';p.write_text(json.dumps(doc,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
# Lecteur de production : vérifier quelques cellules par couche et les références.
sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
reader=SheetReader(tiles/(name+'.tile'))
for refs,img in zip(references,(scene,objects,doors)):
 for (x,y),i in list(refs.items())[::max(1,len(refs)//100)]:
  actual=reader.get_tile(i%32,i//32);assert actual is not None and actual.convert('RGBA').tobytes()==img.crop((x*8,y*8,x*8+8,y*8+8)).tobytes()
reader.close()
# BFS à pas d'une tuile avec deux empreintes indépendantes 16×16. Ceci ne
# remplace pas les collisions, le partenaire ou le fonctionnement en jeu.
def free(x,y):return 0<=x<tw-1 and 0<=y<th-1 and all(obstacles[x+a][y+b]['Tags']==0 for a in (0,1) for b in (0,1))
q=deque([(28,59)]);seen={(28,59)}
while q:
 x,y=q.popleft()
 for n in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
  if n not in seen and free(*n):seen.add(n);q.append(n)
assert free(28,59) and free(31,59) and (28,43) in seen and (31,59) in seen
report={'carte':o['AssetName'],'dimensions_pixels':[W,H],'dimensions_cases':[tw,th],'calques':[l['Name'] for l in layers],'tileset':name,'tuiles_uniques':len(uniques),'cellules_par_couche':[len(x) for x in references],'spawn_heros':[224,472],'spawn_partenaire':[248,472],'seuil_porte':[224,344],'bfs_pas_8_px_cases':len(seen),'bfs_porte_atteignable':True,'validation_jeu':False,'sprite_door_declenchement':False,'eau_etoiles_nuages_animes':False,'raccord_reverie':False,'reproducible_art_pixels_sans_interpolation_au_decoupage':True,'statut':'candidat isole incomplet, non installable tel quel'}
(R/'rapports/candidat-carte-essai.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(report,indent=2,ensure_ascii=False))
