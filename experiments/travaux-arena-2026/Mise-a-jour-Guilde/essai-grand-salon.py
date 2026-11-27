#!/usr/bin/env python3
"""Prototype isolé, non installé : verdure jour validée pour le Grand Salon.
Les reflets, les ambiances, les portes et le test réel ne sont pas traités.
"""
import base64,copy,io,json,struct,hashlib
from pathlib import Path
from PIL import Image
import numpy as np

P=Path(__file__).resolve().parent;S=P/'sources';out=P/'essai-natif-NE-PAS-INSTALLER';out.mkdir(exist_ok=True)
html=(S/'docs/atelier-destiny/Guilde/Guilde-Destiny-Bourgeons-PMD.html').read_text();data=json.loads(html.split('<script id="donnees" type="application/json">')[1].split('</script>')[0]);rid='guilde_destiny_grand_salon';room=next(r for r in data['rooms'] if r['id']==rid);q=data['balade_nuit'].get('ronces',{}).get(rid,data['lianes'][rid]);w,h=room['w'],room['h'];assert w%8==h%8==0

def decode(uri):return Image.open(io.BytesIO(base64.b64decode(uri.split(',')[1]))).convert('RGBA')
imgs=[decode(q[k]) for k in ('s','t')];assert all(im.size==(w,h) for im in imgs)
# PMDO .tile sheets use per-cell premultiplied RGBA PNGs.
canvas=Image.new('RGBA',(2*w,h));canvas.paste(imgs[0],(0,0));canvas.paste(imgs[1],(w,0));a=np.asarray(canvas).copy();c=a[:,:,:3].astype(np.uint16);alpha=a[:,:,3].astype(np.uint16);a[:,:,:3]=((c*alpha[:,:,None])//255).astype('uint8');premul=Image.fromarray(a)
tiles=[]
for y in range(h//8):
 for x in range(2*w//8):
  tile=premul.crop((x*8,y*8,x*8+8,y*8+8))
  if tile.getchannel('A').getbbox():
   b=io.BytesIO();tile.save(b,format='PNG',optimize=True);tiles.append((x,y,b.getvalue()))
head=bytearray(struct.pack('<ii',8,len(tiles)));body=bytearray();off=8+16*len(tiles)
for x,y,png in tiles:
 head+=struct.pack('<iiq',x,y,off);body+=struct.pack('<q',len(png))+png;off+=8+len(png)
blob=bytes(head+body);(out/'Destiny_Guilde_Salon_Verdure_ESSAI.tile').write_bytes(blob)
# Independently decode all tiles and compare exact premultiplied pixels.
size,count=struct.unpack_from('<ii',blob);assert size==8 and count==len(tiles);rebuilt=Image.new('RGBA',canvas.size)
for i in range(count):
 x,y,offset=struct.unpack_from('<iiq',blob,8+i*16);length=struct.unpack_from('<q',blob,offset)[0];rebuilt.paste(Image.open(io.BytesIO(blob[offset+8:offset+8+length])).convert('RGBA'),(x*8,y*8))
assert rebuilt.tobytes()==premul.tobytes()
src=S/'game/Data/Ground'/f'{rid}.rsground';j=json.loads(src.read_text());original=copy.deepcopy(j);o=j['Object'];layers=o['Layers'];assert (len(layers[0]['Tiles'])*8,len(layers[0]['Tiles'][0])*8)==(w,h);assert layers[4]['Name']=='04 verdure separee'
name='Destiny_Guilde_Salon_Verdure_ESSAI';blank={'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1};coords={(x,y) for x,y,_ in tiles}
def grid(part):
 out=[]
 for x in range(w//8):
  col=[]
  for y in range(h//8):
   xx=x+part*(w//8)
   if (xx,y) in coords:col.append({'AutoTileset':'','Associates':[],'Layers':[{'Frames':[{'Sheet':name,'TexLoc':{'X':xx,'Y':y}}],'FrameLength':60}],'NeighborCode':0})
   else:col.append(copy.deepcopy(blank))
  out.append(col)
 return out
layers[4]['Tiles']=grid(0);layers.append({'Name':'ESSAI verdure avant-plan validee','Layer':4,'Visible':True,'Tiles':grid(1)})
# All original map fields, objects, markers, obstacles and other layers remain identical.
old=original['Object'];assert all(o[k]==old[k] for k in o if k!='Layers');assert layers[:4]==old['Layers'][:4] and layers[5:len(old['Layers'])]==old['Layers'][5:];assert {k:v for k,v in layers[4].items() if k!='Tiles'}=={k:v for k,v in old['Layers'][4].items() if k!='Tiles'}
(out/(rid+'.rsground')).write_text(json.dumps(j,ensure_ascii=False,separators=(',',':')),encoding='utf8')
for k,im in zip(('sol','avant-plan'),imgs):im.save(out/f'verdure-{k}-source.png')
report={'etat':'PROTOTYPE NON TESTÉ DANS LE JEU — NE PAS INSTALLER','source':'7bd2dc104706571c91a2ea4a3c45282b94eabbb6','salle':rid,'dimensions':[w,h],'pixels_par_tuile':8,'tuiles':count,'format_tuiles':'RGBA prémultiplié','sortie':'copie séparée, pas de modification du dépôt ni du jeu','invariants':['collision, entités, passages, scripts, et couches hors verdure inchangés','aucun pixel source altéré hormis prémultiplication pour l’encodage'],'manques':['vérification dans PMDO et index des tiles','salles restantes','lueurs animées des 32 bourgeons','ambiances jour/aube/crépuscule/nuit','falaise et braseros','vérification visuelle des objets et des portes','parcours complet, build et release']}
(out/'CONTROLE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Prototype isolé vérifié :',count,'tuiles ; copie Grand Salon, verdure jour uniquement. Non testé dans PMDO.')
