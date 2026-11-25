#!/usr/bin/env python3
"""Checks the animated shoreline patch and cutscene guards in ten variants."""
from pathlib import Path
import gzip,struct,io,hashlib
import ijson
from PIL import Image
R=Path(__file__).resolve().parents[2];bank='Reverie_Berges_053';raw=(R/'game/Content/Tile'/f'{bank}.tile').read_bytes();size,n=struct.unpack_from('<ii',raw);assert size==8 and n==43
index={}
for i in range(n):
 x,y,o=struct.unpack_from('<iiq',raw,8+16*i);length=struct.unpack_from('<q',raw,o)[0];im=Image.open(io.BytesIO(raw[o+8:o+8+length])).convert('RGBA');assert im.size==(8,8);index[(x,y)]=im
names=['WaterfallVillageCapital','WaterfallVillageCapital_Dev','reverie_centre','reverie_centre_Dev','reverie_nord','reverie_nord_Dev','reverie_residentiel','reverie_residentiel_Dev','reverie_etang','reverie_etang_Dev'];layer_hashes=[]
for name in names:
 file=R/'payload'/f'{name}.rsground.gz';data=gzip.decompress(file.read_bytes());a=data.index(b'"Layers":')+len(b'"Layers":');b=data.index(b'"AssetName":',a)-1;layer_hashes.append(hashlib.sha256(data[a:b]).hexdigest());del data
 with gzip.open(file,'rb') as f:
  if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
  layer=next(x for x in ijson.items(f,'Object.Layers.item') if x['Name']=='Objects Under')
 seqs=[]
 for x,col in enumerate(layer['Tiles']):
  for y,cell in enumerate(col):
   for seq in cell.get('Layers',[]):
    if seq.get('Frames') and seq['Frames'][0]['Sheet']==bank:
     assert y==113 and (83<=x<=93 or 126<=x<=148) and seq['FrameLength']==10 and len(seq['Frames'])==4
     for fr in seq['Frames']:
      assert fr['Sheet']==bank;pos=fr['TexLoc'];assert (pos['X'],pos['Y']) in index
     seqs.append((x,y))
 assert len(seqs)==30 and len(set(seqs))==30,(name,len(seqs));del layer
assert len(set(layer_hashes))==1
s=(R/'game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text();dev=(R/'game/Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_text();assert s==dev
scene=s[s.index('function ville.Visite(map)'):s.index('local function position_partenaire_retour')]
assert 'A Successful Rescue.ogg' not in scene
assert "SOUND:FadeOutBGM(45)" in scene and "SOUND:FadeOutBGM(90)" in scene
assert scene.count("SOUND:PlayBGM('Threat.ogg', false)")==1
assert "SV.Destiny.AlerteShinx = 'a_secourir'" in scene and "SV.Destiny.LuxrayAttente = 'place'" in scene
print('PASS 10 cartes synchronisées, 30 raccords animés, banques et garde-fous cinématique')
