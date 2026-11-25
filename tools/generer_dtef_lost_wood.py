#!/usr/bin/env python3
"""Reconstruit le DTEF de Lost Wood depuis les tuiles PMDO actives."""
from pathlib import Path
from PIL import Image
import json,sys,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from preview_maps import SheetReader
GAME=ROOT/'game';DEST=Path(os.environ.get('DESTINY_DTEF_OUT',ROOT/'build/LostWoodLucioles'));DEST.mkdir(parents=True,exist_ok=True)
M=[0x89,0x9B,0x13,0x09,0x0A,0x03,0xCD,0xFF,0x37,0x05,0x00,0x06,0x4C,0x6E,0x26,0x0C,0x01,-1,0x3F,0xCF,0x0B,0x08,0x0F,0x02,0x9F,0x6F,0x0E,0x0D,0x04,0x07,0x7F,0xEF,0x4D,0x27,0x1B,0x8B,0xBF,0xDF,0x8D,0x17,0x2E,0x4E,0x8F,0x1F,0x4F,0x2F,0x5F,0xAF]
names=('wall','secondary','floor');docs={n:json.loads((GAME/'Data/AutoTile'/f'lost_wood_{n}.json').read_text(encoding='utf-8-sig'))['Object']['Tiles'] for n in names};readers={}
def tile(frame):
 sheet=frame['Sheet'];xy=frame['TexLoc']
 if sheet not in readers:readers[sheet]=SheetReader(GAME/'Content/Tile'/(sheet+'.tile'))
 result=readers[sheet].get_tile(xy['X'],xy['Y']);assert result is not None and result.size==(24,24),(sheet,xy)
 return result

def place(im,part,j,frame):
 x=(part*6+j%6)*24;y=(j//6)*24;im.paste(tile(frame),(x,y))
try:
 for vi in range(3):
  atlas=Image.new('RGBA',(432,192));counts={n:0 for n in names}
  for part,n in enumerate(names):
   for j,code in enumerate(M):
    if code<0:continue
    variants=docs[n][f'Tilex{code:02X}']
    if vi>=len(variants):continue
    layers=variants[vi];assert layers and len(layers[0]['Frames'])==1
    place(atlas,part,j,layers[0]['Frames'][0]);counts[n]+=1
  atlas.save(DEST/f'tileset_{vi}.png');print('Variante',vi,counts)
 # Les deux couches d'eau actives ont chacune douze phases cohérentes.
 sample=next(v[0] for v in docs['secondary'].values() if v and len(v[0])>2)
 for li,expected_duration in ((1,17),(2,9)):
  duration=sample[li]['FrameLength'];count=len(sample[li]['Frames']);assert duration==expected_duration and count==12
  for fi in range(count):
   atlas=Image.new('RGBA',(432,192))
   for j,code in enumerate(M):
    if code<0:continue
    variant=docs['secondary'][f'Tilex{code:02X}'][0]
    if len(variant)<=li:continue
    layer=variant[li];assert layer['FrameLength']==duration and len(layer['Frames'])==count
    place(atlas,1,j,layer['Frames'][fi])
   atlas.save(DEST/f'tileset_0_frame{li-1}_{fi}.{duration}.png')
 (DEST/'tileset.dtef.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<DungeonTileset dimensions="24">\n</DungeonTileset>\n',encoding='utf8')
 print('DTEF actif reconstruit dans',DEST)
finally:
 for reader in readers.values():reader.close()
