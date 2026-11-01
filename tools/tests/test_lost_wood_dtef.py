#!/usr/bin/env python3
"""Vérifie les raccords et phases de la forêt aux lucioles importée dans PMDO."""
from pathlib import Path
from collections import Counter
from PIL import Image
import json,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from preview_maps import SheetReader
SRC=ROOT/'art/dtef/LostWoodLucioles';GAME=ROOT/'game'
M=[0x89,0x9B,0x13,0x09,0x0A,0x03,0xCD,0xFF,0x37,0x05,0x00,0x06,0x4C,0x6E,0x26,0x0C,0x01,-1,0x3F,0xCF,0x0B,0x08,0x0F,0x02,0x9F,0x6F,0x0E,0x0D,0x04,0x07,0x7F,0xEF,0x4D,0x27,0x1B,0x8B,0xBF,0xDF,0x8D,0x17,0x2E,0x4E,0x8F,0x1F,0x4F,0x2F,0x5F,0xAF]
cache={}
def image(name):
 if name not in cache:
  cache[name]=Image.open(SRC/name).convert('RGBA');assert cache[name].size==(432,192),name
 return cache[name]
def extract(name,part,j):
 x=(part*6+j%6)*24;y=(j//6)*24
 return image(name).crop((x,y,x+24,y+24))
def same(source,frame,sheet,where):
 assert frame['Sheet']=='LostWoodLucioles',where
 loc=frame['TexLoc'];target=sheet.get_tile(loc['X'],loc['Y']);assert target is not None,where
 # L'importeur PMDO prémultiplie l'alpha ; tolérance d'un entier d'arrondi.
 for a,b in zip(source.convert('RGBA').getdata(),target.convert('RGBA').getdata()):
  assert a[3]==b[3],(where,a,b)
  if a[3]:assert all(abs(round(a[i]*a[3]/255)-b[i])<=1 for i in range(3)),(where,a,b)

def main():
 assert ET.parse(SRC/'tileset.dtef.xml').getroot().attrib['dimensions']=='24'
 assert len(M)==48 and len(set(M))==48 and M.count(-1)==1
 sheet=SheetReader(GAME/'Content/Tile/LostWoodLucioles.tile');counts=Counter()
 try:
  assert sheet.tile_size==24 and len(sheet.positions)==1233
  for part,kind in enumerate(('wall','secondary','floor')):
   defs=json.loads((GAME/'Data/AutoTile'/f'lost_wood_{kind}.json').read_text(encoding='utf-8-sig'))['Object']['Tiles']
   for j,code in enumerate(M):
    if code<0:continue
    variants=defs[f'Tilex{code:02X}']
    expected=[v for v in range(3) if extract(f'tileset_{v}.png',part,j).getchannel('A').getbbox()]
    assert len(variants)==len(expected),(kind,code,len(variants),expected)
    for v,layers in zip(expected,variants):
     assert len(layers[0]['Frames'])==1
     same(extract(f'tileset_{v}.png',part,j),layers[0]['Frames'][0],sheet,(kind,code,v,'base'));counts[kind+'_base']+=1
     for li,dur in enumerate((17,9)):
      files=[f'tileset_{v}_frame{li}_{i}.{dur}.png' for i in range(12)]
      frames=[extract(f,part,j) for f in files] if all((SRC/f).exists() for f in files) else []
      if frames and any(im.getchannel('A').getbbox() for im in frames):
       lay=layers[li+1];assert lay['FrameLength']==dur and len(lay['Frames'])==12,(kind,code,v,li)
       for i,(src,fr) in enumerate(zip(frames,lay['Frames'])):
        same(src,fr,sheet,(kind,code,v,li,i));counts[kind+'_animation']+=1
  assert dict(counts)=={'wall_base':57,'secondary_base':47,'secondary_animation':1080,'floor_base':49},counts
 finally:
  sheet.close()
  for im in cache.values():im.close()
 print('DTEF Treehouse OK : 47 raccords, variantes et 1 080 cellules animées vérifiés contre les sources.')
if __name__=='__main__':main()
