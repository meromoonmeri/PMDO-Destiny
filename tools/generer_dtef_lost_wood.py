#!/usr/bin/env python3
"""Convertit le nouvel art et l'eau existante au VRAI layout DTEF PMDO 0.8.12.

Séparément de l'aperçu : fichiers tileset_*.png en 18x8 cases, métadonnées
et 32 poses de l'extension PMDO, avec masques des 47 configurations.
"""
from pathlib import Path
from PIL import Image
import json,sys,os
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from preview_maps import SheetReader
GAME=ROOT/'game'
DEST=Path(os.environ.get('DESTINY_DTEF_OUT', ROOT/'build/LostWoodDestiny'))
DEST.mkdir(parents=True,exist_ok=True)
MAPPING=[0x89,0x9B,0x13,0x09,0x0A,0x03,0xCD,0xFF,0x37,0x05,0x00,0x06,0x4C,0x6E,0x26,0x0C,0x01,-1,0x3F,0xCF,0x0B,0x08,0x0F,0x02,0x9F,0x6F,0x0E,0x0D,0x04,0x07,0x7F,0xEF,0x4D,0x27,0x1B,0x8B,0xBF,0xDF,0x8D,0x17,0x2E,0x4E,0x8F,0x1F,0x4F,0x2F,0x5F,0xAF]
assert len(MAPPING)==48 and len(set(MAPPING))==48
names=['wall','secondary','floor']
docs={n:json.loads((GAME/'Data/AutoTile'/f'lost_wood_{n}.json').read_text(encoding='utf-8-sig'))['Object']['Tiles'] for n in names}
readers={}
def read(frame):
    sheet=frame['Sheet'];xy=frame['TexLoc']
    if sheet not in readers:
        readers[sheet]=SheetReader(GAME/'Content/Tile'/(sheet+'.tile'))
    result=readers[sheet].get_tile(xy['X'],xy['Y'])
    assert result is not None and result.size==(24,24),(sheet,xy)
    return result

def place(im,part,j,frame):
    x=(part*6+j%6)*24;y=(j//6)*24
    im.paste(read(frame),(x,y))

for vi in range(3):
    atlas=Image.new('RGBA',(18*24,8*24),(0,0,0,0));counts={n:0 for n in names}
    for part,n in enumerate(names):
      for j,code in enumerate(MAPPING):
        if code<0:continue
        variants=docs[n][f'Tilex{code:02X}']
        if vi>=len(variants):continue
        layers=variants[vi];assert layers and len(layers[0]['Frames'])==1
        place(atlas,part,j,layers[0]['Frames'][0]);counts[n]+=1
    atlas.save(DEST/f'tileset_{vi}.png')
    print('variante',vi,counts)

# Extension PMDO : couche 0 = ondulation (25 frames/pose), couche 1 = éclat
# (15 frames/pose). Les zones sol/paroi restent transparentes dans ces planches.
for layer,duration in [(1,25),(2,15)]:
    for frame_index in range(16):
        atlas=Image.new('RGBA',(18*24,8*24),(0,0,0,0));filled=0
        for j,code in enumerate(MAPPING):
            if code<0:continue
            variant=docs['secondary'][f'Tilex{code:02X}'][0]
            if len(variant)<=layer:continue
            lay=variant[layer];assert lay['FrameLength']==duration and len(lay['Frames'])==16
            cell=read(lay['Frames'][frame_index]);assert cell.getchannel('A').getbbox() is not None
            place(atlas,1,j,lay['Frames'][frame_index]);filled+=1
        atlas.save(DEST/f'tileset_0_frame{layer-1}_{frame_index}.{duration}.png')
        assert filled==[47,46][layer-1]
for r in readers.values():r.close()
(DEST/'tileset.dtef.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<DungeonTileset dimensions="24">\n</DungeonTileset>\n',encoding='utf-8')
print('DTEF préparé dans',DEST)
