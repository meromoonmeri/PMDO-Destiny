from pathlib import Path
import shutil, json, copy, struct, io, math, hashlib
from PIL import Image, ImageDraw
import numpy as np
import sys
sys.path.insert(0,'/home/user/destiny-reference/tools')
from preview_maps import DirReader, SheetReader
R=Path('/home/user/chantier-cap-escalier-nuages'); P=Path('/home/user/chantier-grand-cap-nuit'); C=R/'candidat'; G=Path('/home/user/.cache/lostwood-moteur/PMDO-Destiny')
assert not C.exists(), 'éviter écrasement accidentel'
shutil.copytree(P/'candidat',C)
for n in ['CLIFF_PICHU_NUIT_NUAGES_HAUT_RECALE','CLIFF_PICHU_NUIT_NUAGES_MILIEU_RECALE']:
 src=G/'Content/BG'/f'{n}.dir';dst=C/'Content/BG'/src.name;shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes()
p=C/'Data/Ground/grand_cap_panoramique_nuit.rsground';d=json.loads(p.read_text());o=d['Object'];old=copy.deepcopy(o)
# L'aplat géographique de Réverie est utilisé uniquement comme donneur 1×.
source=Image.open('/home/user/apercu-global-reverie/reverie-etang-candidat-global.png').convert('RGBA')
stair=source.crop((680,0,864,160)); arr=np.array(stair);arr[:,:,:3]=(arr[:,:,:3].astype(float)*[.30,.40,.58]).astype('uint8');stair=Image.fromarray(arr)
mask=Image.new('L',stair.size,255);draw=ImageDraw.Draw(mask);draw.polygon([(0,0),(184,0),(184,24),(160,16),(152,10),(144,5),(136,2),(128,0),(56,0),(48,2),(40,5),(32,10),(24,16),(0,24)],fill=0);stair.putalpha(mask)
# Origine de la ville (680,0) -> Cap (512,720), translation x=-168 ;
# il y a donc un raccord centré, sans redimensionnement, à l'échelle 8 px.
stair.save(R/'escalier-nuit-recolore.png');name='GrandCap_EscalierNord_Nuit';unique={};blobs=[];refs={}
for dx in range(23):
 for dy in range(20):
  tile=stair.crop((dx*8,dy*8,dx*8+8,dy*8+8))
  if tile.getchannel('A').getbbox() is None:continue
  key=tile.tobytes()
  if key not in unique:unique[key]=len(blobs);blobs.append(tile)
  refs[(64+dx,90+dy)]=unique[key]
header=8+16*len(blobs);body=bytearray();rows=[]
for i,t in enumerate(blobs):
 b=io.BytesIO();t.save(b,format='PNG');png=b.getvalue();rows.append((i%32,i//32,header+len(body)));body+=struct.pack('<q',len(png))+png
(C/'Content/Tile'/f'{name}.tile').write_bytes(struct.pack('<ii',8,len(blobs))+b''.join(struct.pack('<iiq',*r) for r in rows)+body)
layer=copy.deepcopy(o['Layers'][0]);layer['Name']=name;layer['Layer']=0
for x,col in enumerate(layer['Tiles']):
 for y,t in enumerate(col):
  t['AutoTileset']='';t['Associates']=[];t['NeighborCode']=-1;t['Layers']=[]
  if (x,y) in refs:
   n=refs[(x,y)];t['Layers']=[{'Frames':[{'Sheet':name,'TexLoc':{'X':n%32,'Y':n//32}}],'FrameLength':60}]
o['Layers'].append(layer)
# Parois visibles uniquement. Le couloir libre fait 56 px de large.
changed=[]
for x in list(range(64,72))+list(range(79,87)):
 for y in range(90,110):
  piece=mask.crop(((x-64)*8,(y-90)*8,(x-63)*8,(y-89)*8));
  if sum(1 for v in piece.getdata() if v)>48 and o['obstacles'][x][y]['Tags']==0:
   o['obstacles'][x][y]['Tags']=1;changed.append((x,y))
base=copy.deepcopy(o['Background']);clouds=[]
for name2,y,v in [('CLIFF_PICHU_NUIT_NUAGES_HAUT_RECALE',175,-9),('CLIFF_PICHU_NUIT_NUAGES_MILIEU_RECALE',205,-5)]:
 cloud=copy.deepcopy(base);cloud['BGAnim'].update(AnimIndex=name2,FrameTime=1,StartFrame=-1,EndFrame=-1);cloud['MapLoc']={'X':0,'Y':y};cloud['BGMovement']={'X':v,'Y':0};cloud['RepeatX']=True;clouds.append(cloud)
o['Background']={'$type':'RogueEssence.Dungeon.LayeredBG, RogueEssence','Layers':[{'BG':x} for x in [base]+clouds]}
o['Comment']='Candidat nocturne : escalier nord, mer 12 phases, nuages défilants ; à tester.'
p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
script=C/'Data/Script/destiny/ground/grand_cap_panoramique_nuit/init.lua';s=script.read_text();assert 'RogueElements.Rect(552, 864, 96, 8)' in s;s=s.replace('RogueElements.Rect(552, 864, 96, 8)','RogueElements.Rect(576, 864, 56, 8)');script.write_text(s)
# Reconstruction statique des données de terrain déjà rendues, plus la nouvelle couche.
terrain=Image.open(P/'apercu/terrain-bordure-candidate.png').convert('RGBA');terrain.alpha_composite(stair,(512,720))
raw=(C/'Content/BG/GrandCap_V24P01A_Nuit.dir').read_bytes();l=struct.unpack_from('<q',raw)[0];atlas=Image.open(io.BytesIO(raw[8:8+l])).convert('RGBA');cloud_imgs=[DirReader.frame0(C/'Content/BG'/f"{c['BGAnim']['AnimIndex']}.dir") for c in clouds]
def render(t):
 frame=int(t*60//8)%12;f=atlas.crop((312*frame,0,312*(frame+1),880));img=Image.new('RGBA',(1200,880));
 for x in range(0,1200,312):img.paste(f,(x,0))
 for c,cl in zip(clouds,cloud_imgs):
  offset=int(c['BGMovement']['X']*t);w=cl.width;x=offset%w-w
  while x<1200:img.alpha_composite(cl,(x,c['MapLoc']['Y']));x+=w
 img.alpha_composite(terrain);return img.convert('RGB')
im=render(0);im.save(R/'apercu-complet-hors-moteur.png',optimize=True)
# 96 images à 133 ms : nuages visibles et 12 phases mer conservées.
frames=[render(i*8/60).resize((900,660),Image.Resampling.NEAREST) for i in range(72)]
frames[0].save(R/'apercu-nuages-et-mer-hors-moteur.gif',save_all=True,append_images=frames[1:],duration=130,loop=0,optimize=True,disposal=2)
# Contrôles de conservation et passage de deux acteurs de 16x16.
assert o['Layers'][:-1]==old['Layers'] and o['Entities']==old['Entities'];assert o['Background']['Layers'][0]['BG']==old['Background']
for x,y in [(592,800),(616,800),(592,720),(592,688),(592,848)]:
 assert all(o['obstacles'][cx][cy]['Tags']==0 for cx in range(x//8,(x+15)//8+1) for cy in range(y//8,(y+15)//8+1)),(x,y)
assert all(o['obstacles'][x][y]['Tags']==old['obstacles'][x][y]['Tags'] or (x,y) in changed for x in range(150) for y in range(110))
proof={'reference_T00P04A_sha256':hashlib.sha256((R/'T00P04A-source.gif').read_bytes()).hexdigest(),'nuages_source':['CLIFF_PICHU_NUIT_NUAGES_HAUT_RECALE','CLIFF_PICHU_NUIT_NUAGES_MILIEU_RECALE'],'vitesses_px_sec':[-9,-5],'mer_source_12_phases_conservee':True,'escalier_donneur_zone':[680,0,864,160],'escalier_position':[512,720],'translation_x':-168,'escalier_recoloration':[.30,.40,.58],'cases_tuiles':len(refs),'tuiles_uniques':len(blobs),'obstacles_ajoutes':len(changed),'ground_layers_preexistants_et_entites_egaux':True,'moteur_valide':False}
(R/'preuves.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False));print(json.dumps(proof,indent=2,ensure_ascii=False))
