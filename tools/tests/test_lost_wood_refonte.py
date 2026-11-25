#!/usr/bin/env python3
"""Contrôle statique des nouvelles ruines et chemins de Lost Wood."""
from pathlib import Path
from PIL import Image
import json,struct,sys
ROOT=Path(__file__).resolve().parents[2];G=ROOT/'game';ART=ROOT/'art/lost_wood_ruines';T=G/'Content/Tile'
sys.path.insert(0,str(ROOT/'tools'))
from preview_maps import SheetReader

SPECS={'ruins':('DestinyRuinesMousse_Arche',4,3),'pillar':('DestinyRuinesMousse_Pilier',1,3),'broken_pillar':('DestinyRuinesMousse_PilierBrise',1,2),'fallen_left':('DestinyRuinesMousse_TombeGauche',2,2),'fallen_right':('DestinyRuinesMousse_TombeDroite',2,2),'rubble':('DestinyRuinesMousse_Debris',1,1)}
EXTRA={sheet for sheet,_,_ in SPECS.values()}|{'LostWoodLucioles','LostWoodPierresV3','LostWoodSentiers'}

def compare_sheet_png(name):
 image=Image.open(ART/(name+'.png')).convert('RGBA');sheet=SheetReader(T/(name+'.tile'))
 try:
  assert sheet.tile_size==24
  assert len(sheet.positions)==(image.width//24)*(image.height//24)
  for (x,y) in sheet.positions:
   src=image.crop((x*24,y*24,(x+1)*24,(y+1)*24));dst=sheet.get_tile(x,y);assert dst is not None,(name,x,y)
   for a,b in zip(src.getdata(),dst.convert('RGBA').getdata()):
    expected=tuple((a[i]*a[3]+127)//255 for i in range(3))+(a[3],)
    assert expected==b,(name,x,y,a,b)
 finally:sheet.close();image.close()

def tile_index():
 data=(T/'index.idx').read_bytes();n,=struct.unpack_from('<i',data);off=4;found={}
 for _ in range(n):
  v=0;shift=0
  while True:
   b=data[off];off+=1;v|=(b&127)<<shift
   if b<128:break
   shift+=7
  name=data[off:off+v].decode('utf8');off+=v
  begin=off;_,count=struct.unpack_from('<ii',data,off);off+=8+count*16
  assert name not in found,name;found[name]=data[begin:off]
 assert off==len(data)
 assert EXTRA.issubset(found)
 assert not any(name.startswith('Relic_Forest_Blob_') or name in ('LostWoodPierresV2','LostWoodSteppingStones') for name in found)
 for name in EXTRA:
  raw=(T/(name+'.tile')).read_bytes();_,count=struct.unpack_from('<ii',raw)
  assert found[name]==raw[:8+count*16],name

def main():
 floor_data=json.loads((G/'Data/Zone/lost_wood.json').read_text(encoding='utf-8-sig'))['Object']['Segments'][0]['Floors'];assert len(floor_data)==7
 for floor in floor_data:
  steps=floor['GenSteps']
  assert sum('GridPathTwoSides' in s['Value'].get('$type','') for s in steps)==1
  assert sum('LoadBlobStep' in s['Value'].get('$type','') for s in steps)==1
  assert sum(s['Value'].get('Script')=='DestinyLostWoodRiviereEtLucioles' for s in steps)==1
  blob=next(s['Value'] for s in steps if 'LoadBlobStep' in s['Value'].get('$type',''))
  assert {m['Spawn'] for m in blob['Maps']}=={'destiny_lost_wood_ruine_'+s for s in SPECS}
  assert 'NoChokepointStencil' in json.dumps(blob['TerrainStencil'])
 for suffix,(sheet,w,h) in SPECS.items():
  obj=json.loads((G/'Data/Map'/f'destiny_lost_wood_ruine_{suffix}.rsmap').read_text(encoding='utf-8-sig'))
  assert obj['Version']=='0.8.12.0';m=obj['Object'];assert len(m['Tiles'])==w and all(len(col)==h for col in m['Tiles'])
  assert all(t['Data']['ID']=='unbreakable' for col in m['Tiles'] for t in col)
  for x in range(w):
   for y in range(h):
    f=m['Layers'][0]['Tiles'][x][y]['Layers'][0]['Frames'][0]
    assert f['Sheet']==sheet and f['TexLoc']=={'X':x,'Y':y}
  compare_sheet_png(sheet)
 for sheet in ('LostWoodPierresV3','LostWoodSentiers'):compare_sheet_png(sheet)
 # Les raccords opposés doivent avoir la même ouverture alpha au bord.
 path=SheetReader(T/'LostWoodSentiers.tile')
 try:
  assert len(path.positions)==16
  for mask in range(16):
   a=path.get_tile(mask,0).getchannel('A')
   for other in range(16):
    b=path.get_tile(other,0).getchannel('A')
    if mask&1 and other&4:assert [a.getpixel((x,0))>0 for x in range(24)]==[b.getpixel((x,23))>0 for x in range(24)]
    if mask&2 and other&8:assert [a.getpixel((23,y))>0 for y in range(24)]==[b.getpixel((0,y))>0 for y in range(24)]
 finally:path.close()
 d=(G/'Content/Object/LostWoodLucioles.dir').read_bytes();size,=struct.unpack_from('<q',d);assert d[8:16]==b'\x89PNG\r\n\x1a\n';assert struct.unpack_from('<iiii',d,8+size)==(24,24,0,24)
 script=(G/'Data/Script/destiny/mapgen_lost_wood.lua').read_text(encoding='utf-8');assert 'QA_' not in script and 'LostWoodSentiers' in script and 'LostWoodPierresV3' in script
 tile_index()
 print('Lost Wood : 7 étages, 6 fragments, 8 feuilles éditables, raccords et index vérifiés.')
if __name__=='__main__':main()
