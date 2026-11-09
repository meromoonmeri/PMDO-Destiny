#!/usr/bin/env python3
"""Les dix cartes conservent le décor complet et onze couches expérimentales."""
from pathlib import Path
import hashlib,ijson
R=Path(__file__).resolve().parents[2];D=R/'game/Data/Ground'
base=(D/'WaterfallVillageCapital.rsground').read_bytes();a=base.index(b'"Layers":')+len(b'"Layers":');b=base.index(b'"AssetName":',a)-1;layers=base[a:b]
for name in ['WaterfallVillageCapital','reverie_centre','reverie_nord','reverie_residentiel','reverie_etang']:
 jeu=(D/(name+'.rsground')).read_bytes();dev=(D/(name+'_Dev.rsground')).read_bytes()
 def parts(raw):
  a=raw.index(b'"Layers":')+len(b'"Layers":');b=raw.index(b'"AssetName":',a)-1
  return raw[:a],raw[a:b],raw[b:]
 p,l,s=parts(jeu);q,k,t=parts(dev)
 assert p==q and k==l==layers and t==s.replace(('"AssetName":"'+name+'"').encode(),('"AssetName":"'+name+'_Dev"').encode(),1),name
 with (D/(name+'_Dev.rsground')).open('rb') as f:
  assert f.read(3)==b'\xef\xbb\xbf';names=[layer['Name'] for layer in ijson.items(f,'Object.Layers.item')]
 assert names==['Base','Cliffs','River','Layer 4','Objects Under','Objects Under Anim','Objects','Objects Anim','Objects Over','Objects Over Anim','Fringe'],name
 print('PASS',name,'11 calques, décor intégral et métadonnées jeu/édition')
