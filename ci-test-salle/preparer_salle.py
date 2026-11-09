"""Test CI jetable : transforme l'image plate en Ground technique, jamais une intégration."""
from pathlib import Path
from PIL import Image
import io, json, copy, struct, os
root=Path('.')
name='CI_SallePrincipaleSpacieuse'
# La réduction 572x464 est une hypothèse, pas la taille finale du projet.
im=Image.open('ci-test-salle/salle-jour-572x464.png').convert('RGBA')
assert im.size==(572,464)
canvas=Image.new('RGBA',(576,464));canvas.alpha_composite(im,(2,0))
w,h=canvas.size;tw,th=w//8,h//8
unique=[];lookup={};refs={}
for x in range(tw):
 for y in range(th):
  tile=canvas.crop((8*x,8*y,8*x+8,8*y+8))
  if tile.getchannel('A').getbbox() is None: continue
  raw=tile.tobytes()
  if raw not in lookup:lookup[raw]=len(unique);unique.append(tile)
  refs[x,y]=lookup[raw]
header=8+16*len(unique);body=bytearray();entries=[]
for i,t in enumerate(unique):
 b=io.BytesIO();t.save(b,format='PNG');data=b.getvalue();entries.append((i%32,i//32,header+len(body)));body+=struct.pack('<q',len(data))+data
p=root/'game/Content/Tile'/f'{name}.tile';p.parent.mkdir(parents=True,exist_ok=True)
p.write_bytes(struct.pack('<ii',8,len(unique))+b''.join(struct.pack('<iiq',*e) for e in entries)+body)
p=root/'game/Data/Ground/destiny_hub.rsground';doc=json.loads(p.read_text(encoding='utf8'));o=doc['Object'];old=o['Layers'][0];blank=copy.deepcopy(old['Tiles'][0][0]);blank.update(AutoTileset='',Associates=[],Layers=[],NeighborCode=-1)
cols=[]
for x in range(tw):
 col=[]
 for y in range(th):
  cell=copy.deepcopy(blank);i=refs.get((x,y))
  if i is not None:cell['Layers']=[{'Frames':[{'Sheet':name,'TexLoc':{'X':i%32,'Y':i//32}}],'FrameLength':60}]
  col.append(cell)
 cols.append(col)
o['Layers']=[{'Name':'CI-image-plate-test-echelle','Layer':0,'Visible':True,'Tiles':cols}]
# Ouvert pour le test visuel uniquement : ne représente pas les collisions définitives.
o['obstacles']=[[{'Bounds':{'X':x*8,'Y':y*8,'Width':8,'Height':8},'Tags':0} for y in range(th)] for x in range(tw)]
o['Comment']='CI seul: photographie candidate convertie en tuiles ; collisions non valides.'
o['Decorations']=[{'Name':'New Deco','Layer':0,'Visible':True,'Anims':[]}]
e=o['Entities'][0];e['GroundObjects']=[];e['MapChars']=[];e['Spawners']=[]
e['Markers'][0]['Collider'].update(X=280,Y=280,Width=16,Height=16)
p.write_text(json.dumps(doc,ensure_ascii=False,separators=(',',':')),encoding='utf8')
p=root/'game/Data/Script/destiny/ground/destiny_hub/init.lua'
p.write_text("require 'origin.common'\nlocal destiny_hub = {}\nfunction destiny_hub.Init(map) end\nfunction destiny_hub.Enter(map) GAME:FadeIn(20) end\nfunction destiny_hub.GameLoad(map) GAME:FadeIn(20) end\nfunction destiny_hub.Update(map,time) end\nreturn destiny_hub\n",encoding='utf8')
print('Salle CI:',canvas.size,'tiles',len(unique),'spawn (280,280)')
