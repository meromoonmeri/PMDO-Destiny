#!/usr/bin/env python3
"""Validation de 47 cas et de raccords voisins, indépendante de la capture."""
from pathlib import Path
from PIL import Image
from itertools import product
import json, struct, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from preview_maps import SheetReader
G=ROOT/'game/Data/AutoTile'
T=ROOT/'game/Content/Tile'
sheets={}
def render(kind,code,var):
    key=(kind,code,var)
    if key in sheets:return sheets[key]
    doc=json.loads((G/f'lost_wood_{kind}.json').read_text(encoding='utf-8-sig'))['Object']['Tiles']
    variants=doc[f'Tilex{code:02X}'];var=min(var,len(variants)-1)
    frame=variants[var][0]['Frames'][0];loc=frame['TexLoc']
    reader=SheetReader(T/(frame['Sheet']+'.tile'));im=reader.get_tile(loc['X'],loc['Y']).convert('RGB');reader.close();sheets[key]=im
    return im
DIRECTIONS=[(0,1),(-1,0),(0,-1),(1,0)]
DIAGS=[(-1,1),(-1,-1),(1,-1),(1,1)]
def code(values,x,y):
    b=[bool(values.get((x+dx,y+dy),0)) for dx,dy in DIRECTIONS]
    n=sum(1<<i for i,v in enumerate(b) if v)
    for i,(dx,dy) in enumerate(DIAGS):
        if b[i] and b[(i+1)%4] and values.get((x+dx,y+dy),0):n|=1<<(i+4)
    return n

def test_headers():
    for name in ['LostWoodFloor','LostWoodWall','LostWoodLucioles']:
        data=(T/(name+'.tile')).read_bytes()
        ts,count=struct.unpack_from('<ii',data)
        expected={'LostWoodFloor':49,'LostWoodWall':57,'LostWoodLucioles':1233}[name]
        assert ts==24 and count==expected
        reader=SheetReader(T/(name+'.tile'))
        assert len(reader.positions)==count
        for xy in reader.positions:
            assert reader.get_tile(*xy) is not None, (name,xy)
        reader.close()

def test_raccords():
    # Toutes les configurations d'un voisinage 4x3 (puis 3x4), les deux
    # cases centrales et toutes leurs variantes. Compare les pixels de bord.
    tested=0;seen=set(); exact=0; difference=0; compared=0; max_difference=0
    for horizontal in [True,False]:
      W,H=(4,3) if horizontal else (3,4); a=(1,1);b=(2,1) if horizontal else (1,2)
      cells=list(product(range(W),range(H)))
      for bits in range(1<<len(cells)):
        values={p:(bits>>i)&1 for i,p in enumerate(cells)}
        ca=code(values,*a) if values[a] else 0xFF
        cb=code(values,*b) if values[b] else 0xFF
        ka='wall' if values[a] else 'floor';kb='wall' if values[b] else 'floor'
        for va in range(3):
          for vb in range(3):
            ia=render(ka,ca,va);ib=render(kb,cb,vb)
            edge_a=[ia.getpixel((23,i) if horizontal else (i,23)) for i in range(24)]
            edge_b=[ib.getpixel((0,i) if horizontal else (i,0)) for i in range(24)]
            for left,right in zip(edge_a,edge_b):
                delta=sum(abs(x-y) for x,y in zip(left,right))
                exact+=int(delta==0);difference+=delta;compared+=1;max_difference=max(max_difference,delta)
            tested+=1;seen.add((ka,ca));seen.add((kb,cb))
    mean=difference/(compared*3)
    print('Paires adjacentes:',tested,'; codes de murs:',sum(k=='wall' for k,c in seen),'/47')
    print(f'Pixels de bord identiques : {100*exact/compared:.2f} % ; écart RGB moyen {mean:.2f}/255 ; écart maximal par canal cumulé {max_difference}/765')
    # La texture Treehouse validée est plus nuancée que l'ancienne : sa
    # moyenne observée est 9,38/255. La borne 10,5 détecte une régression
    # importante mais ne démontre pas un raccord artistique parfait.
    # La fidélité exacte au DTEF est contrôlée par test_lost_wood_dtef.py.
    assert sum(k=='wall' for k,c in seen)==47 and mean<10.5 and max_difference<200

if __name__=='__main__':test_headers();test_raccords();print('OK: feuilles natives et couverture des cas')
