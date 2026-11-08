from pathlib import Path
from PIL import Image,ImageChops
import json,struct,io,collections,hashlib
R=Path('/home/user/chantier-grand-cap-nuit');p=R/'candidat/Data/Ground/grand_cap_panoramique_nuit.rsground';d=json.loads(p.read_text());o=d['Object'];bg=o['Layers'];assert len(bg)==5
terrain=Image.open(R/'apercu/terrain-grand-cap-nuit.png').convert('RGBA');base=Image.open(R/'L01_herbe_native.png').convert('RGBA');rim=Image.open(R/'L03_bordure_nord_native.png').convert('RGBA');assert base.size==rim.size==terrain.size==(1200,880)
# Couverture de la bordure conservée dans le fond historique : uniquement
# les pixels natifs du plateau non déjà présents dans les calques maintenus.
under=base.copy();under.putalpha(ImageChops.subtract(base.getchannel('A'),terrain.getchannel('A')))
# Les deux couches sont extraites des PNG 1x déjà publiés, sans recoloration.
assets=[('GrandCap_Couverture_Bord_Nuit',under),('GrandCap_Bordure_Nord_Nuit',rim)]
def encode(name,img):
 unique={};blobs=[];refs={}
 for x in range(150):
  for y in range(110):
   tile=img.crop((x*8,y*8,x*8+8,y*8+8))
   if tile.getchannel('A').getbbox() is None:continue
   b=tile.tobytes()
   if b not in unique:unique[b]=len(unique);blobs.append(tile)
   refs[(x,y)]=unique[b]
 head=8+16*len(blobs);body=bytearray();rows=[]
 for i,tile in enumerate(blobs):
  out=io.BytesIO();tile.save(out,format='PNG');png=out.getvalue();rows.append((i%32,i//32,head+len(body)));body+=struct.pack('<q',len(png))+png
 path=R/'candidat/Content/Tile'/f'{name}.tile';path.write_bytes(struct.pack('<ii',8,len(blobs))+b''.join(struct.pack('<iiq',*rec) for rec in rows)+body)
 # Copie d'un calque existant pour conserver la structure PMDO des cases.
 layer=json.loads(json.dumps(o['Layers'][0]));layer['Name']=name;layer['Layer']=0
 for x,col in enumerate(layer['Tiles']):
  for y,t in enumerate(col):
   t['AutoTileset']='';t['Associates']=[];t['NeighborCode']=-1;t['Layers']=[]
   if (x,y) in refs:
    i=refs[(x,y)];t['Layers']=[{'Frames':[{'Sheet':name,'TexLoc':{'X':i%32,'Y':i//32}}],'FrameLength':60}]
 return layer,{'nom':name,'positions':len(refs),'unique':len(blobs),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
a,aa=encode(*assets[0]);b,bb=encode(*assets[1]);o['Layers'].insert(0,a);o['Layers'].insert(3,b);p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
# Preuve : 5 calques du terrain et toutes les autres données restent identiques.
orig=json.loads((R/'grand-cap-nuit-original.rsground').read_text(encoding='utf-8-sig')); old=orig['Object']; assert o['Layers'][1:3]+o['Layers'][4:]==old['Layers'][1:];assert o['obstacles']==old['obstacles'] and o['Entities']==old['Entities']
# Reconstruction du relief par superposition, identique aux données du candidat.
composite=Image.new('RGBA',(1200,880));composite.alpha_composite(under);composite.alpha_composite(terrain);composite.alpha_composite(rim);composite.save(R/'apercu/terrain-bordure-candidate.png')
# Recomposer les aperçus avec les 12 frames de fond .dir.
raw=(R/'candidat/Content/BG/GrandCap_V24P01A_Nuit.dir').read_bytes();n=struct.unpack_from('<q',raw)[0];atlas=Image.open(io.BytesIO(raw[8:8+n])).convert('RGBA');views=[]
for i in range(12):
 frame=atlas.crop((i*312,0,(i+1)*312,880));im=Image.new('RGBA',(1200,880));
 for x in range(0,1200,312):im.paste(frame,(x,0))
 im.alpha_composite(composite);views.append(im.convert('RGB'))
views[0].save(R/'apercu/grand-cap-nuit-phase-01.png',optimize=True)
views[0].save(R/'apercu/grand-cap-nuit-anime.png',format='PNG',save_all=True,append_images=views[1:],duration=[133.333]*12,loop=0,disposal=0,blend=0,optimize=True)
views[0].resize((960,704),Image.Resampling.NEAREST).save(R/'apercu/grand-cap-nuit-anime.gif',save_all=True,append_images=[f.resize((960,704),Image.Resampling.NEAREST) for f in views[1:]],duration=130,loop=0,optimize=True,disposal=2)
proof=json.loads((R/'preuves.json').read_text());proof['bordure_retrouvee']={'source_commit':'9bac5c1','calques_source':['L01_herbe_native.png','L03_bordure_nord_native.png'],'banques':[aa,bb],'reconstruit_sans_recoloration':True};proof['geometry_collisions_entities_remaining_layers_unchanged']=True;(R/'preuves.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2));print('Bordure restaurée:',aa,bb)
