#!/usr/bin/env python3
"""Vérification du layout DTEF et des 32 phases conservées, cellule par cellule."""
from pathlib import Path
from PIL import Image
import json,re,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from preview_maps import SheetReader
# Reproduit ici la table exacte de DtefImportHelper.FieldDtefMapping 0.8.12.
M=[0x89,0x9B,0x13,0x09,0x0A,0x03,0xCD,0xFF,0x37,0x05,0x00,0x06,0x4C,0x6E,0x26,0x0C,0x01,-1,0x3F,0xCF,0x0B,0x08,0x0F,0x02,0x9F,0x6F,0x0E,0x0D,0x04,0x07,0x7F,0xEF,0x4D,0x27,0x1B,0x8B,0xBF,0xDF,0x8D,0x17,0x2E,0x4E,0x8F,0x1F,0x4F,0x2F,0x5F,0xAF]
P=ROOT/'art/dtef/LostWoodDestiny';G=ROOT/'game'
names=['wall','secondary','floor'];docs={n:json.loads((G/'Data/AutoTile'/f'lost_wood_{n}.json').read_text(encoding='utf-8-sig'))['Object']['Tiles'] for n in names};readers={}
def ref(frame):
 name=frame['Sheet'];q=frame['TexLoc']
 if name not in readers:
  readers[name]=SheetReader(G/'Content/Tile'/(name+'.tile'))
 return readers[name].get_tile(q['X'],q['Y']).convert('RGBA')
def extract(im,section,j):
 x=(section*6+j%6)*24;y=(j//6)*24
 return im.crop((x,y,x+24,y+24))
def check_equal(a,b,desc):
 assert a.tobytes()==b.tobytes(),desc

def validate():
 assert ET.parse(P/'tileset.dtef.xml').getroot().attrib['dimensions']=='24'
 assert len(M)==48 and len(set(M))==48 and M.count(-1)==1
 counts=[]
 for var in range(3):
  im=Image.open(P/f'tileset_{var}.png').convert('RGBA');assert im.size==(432,192)
  per=0
  for k,name in enumerate(names):
   for j,code in enumerate(M):
    tile=extract(im,k,j)
    if code<0:
     assert tile.getchannel('A').getbbox() is None;continue
    variations=docs[name][f'Tilex{code:02X}']
    if var>=len(variations):
     assert tile.getchannel('A').getbbox() is None;continue
    source=ref(variations[var][0]['Frames'][0]);check_equal(tile,source,(var,name,code));per+=1
  counts.append(per)
 assert counts==[141,6,6],counts
 frames=0
 for layer,duration in [(1,25),(2,15)]:
  for i in range(16):
   im=Image.open(P/f'tileset_0_frame{layer-1}_{i}.{duration}.png').convert('RGBA');assert im.size==(432,192)
   for part in (0,2):
    assert im.crop((part*144,0,part*144+144,192)).getchannel('A').getbbox() is None
   for j,code in enumerate(M):
    tile=extract(im,1,j)
    if code<0:assert tile.getchannel('A').getbbox() is None;continue
    variant=docs['secondary'][f'Tilex{code:02X}'][0]
    if len(variant)<=layer:assert tile.getchannel('A').getbbox() is None;continue
    lay=variant[layer];assert lay['FrameLength']==duration and len(lay['Frames'])==16
    check_equal(tile,ref(lay['Frames'][i]),('eau',layer,i,code));frames+=1
 assert frames==16*(47+46)
 for r in readers.values():r.close()
 print('DTEF OK : 47 raccords × 3 matières ; 3 variantes ;',frames,'cellules d’eau animées identiques aux ressources existantes ; 32 planches de phases.')

if __name__=='__main__':validate()
