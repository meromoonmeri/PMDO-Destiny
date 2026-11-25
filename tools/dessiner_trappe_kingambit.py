#!/usr/bin/env python3
"""Anime à 1× les ouvertures de biome préparées par preparer_trappes_magenta.py."""
import argparse
import io
import json
from pathlib import Path
import struct

from PIL import Image, ImageDraw
from dojo_reverie_types import TYPES
from lib_tiles import write_tilesheet

FRAMES,TICKS=10,5
W,H,CX,CY=96,80,48,40
HERE=Path(__file__).resolve().parents[1]


def passage(im,dx,dy):
    """Retire des colonnes/lignes du centre, sans changer l'échelle du dessin."""
    out=Image.new('RGBA',im.size)
    for x,sx in ((0,0),(CX,CX+dx)):
        for y,sy in ((0,0),(CY,CY+dy)):
            r=CX-dx if x==0 else W
            b=CY-dy if y==0 else H
            out.paste(im.crop((sx,sy,r,b)),(dx if x==0 else CX,dy if y==0 else CY))
    return out


def rupture(base,rebord):
    assert base.size==rebord.size==(W,H)
    assert all(set(im.getchannel('A').tobytes())<={0,255} for im in (base,rebord))
    colors=[(c,n) for n,c in rebord.getcolors(W*H) if c[-1]==255]
    colors.sort(key=lambda t: sum(t[0][:3]));dark=colors[max(0,len(colors)//7)][0]
    light=colors[min(len(colors)-1,3*len(colors)//4)][0]
    sol=[];front=[]
    for f in range(FRAMES):
        if f<=1:
            a,b=Image.new('RGBA',(W,H)),Image.new('RGBA',(W,H))
            d=ImageDraw.Draw(a);l=18+f*11
            d.line((CX-l,CY+2,CX-12,CY+1,CX-5,CY-2,CX+2,CY,CX+9,CY-1,CX+l,CY+2),fill=dark,width=1+f)
            if f:
                d.line((CX-11,CY+1,CX-8,CY+5,CX-4,CY+7),fill=dark)
                d.line((CX+9,CY-1,CX+12,CY-5,CX+17,CY-7),fill=light)
        elif f<=5:
            dx,dy=((11,10),(7,7),(4,4),(1,1))[f-2]
            a=passage(base,dx,dy);b=passage(rebord,dx,dy)
        else:
            a,b=base.copy(),rebord.copy()
        if 2<=f<=6:
            dr=ImageDraw.Draw(b);n=f-2
            for i,(x,y) in enumerate(((-18,-8),(16,-3),(25,3),(-24,8))):
                x=CX+x+(1 if x>0 else -1)*3*n;y=CY+y-2*n+i%2
                dr.line((x,y,x+(i%2),y),fill=(light if i in (0,3) else dark))
        sol.append(a);front.append(b)
    return sol,front


def dirsheet(p,frames):
    atlas=Image.new('RGBA',(W*5,H*2))
    for i,im in enumerate(frames): atlas.paste(im,(i%5*W,i//5*H))
    png=io.BytesIO();atlas.save(png,format='PNG',optimize=True);raw=png.getvalue()
    with p.open('xb') as f:
        f.write(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',W,H,0,len(frames)))


def generer(out,art,export=None):
    out.mkdir(parents=True,exist_ok=True)
    entries=[];w,h=4*24,4*24
    if export:
        export.mkdir(parents=True,exist_ok=True)
        maps=[Image.new('RGBA',(FRAMES*w,len(TYPES)*h)) for _ in range(2)]
    for row,(typ,label,_,biome,*_) in enumerate(TYPES):
        b=Image.open(art/f'{typ}_sol.png').convert('RGBA');r=Image.open(art/f'{typ}_rebord.png').convert('RGBA')
        for p,(nom,poses) in enumerate(zip(('Sol','Rebord'),rupture(b,r))):
            dirsheet(out/f'Kingambit_Trappe_{typ}_{nom}.dir',poses)
            if export:
                for i,im in enumerate(poses): maps[p].paste(im,(i*w,row*h+(h-H)//2))
        entries.append(dict(ligne=row,id=typ,type=label,biome=biome))
    if export:
        cells={}
        for p,(nom,atlas) in enumerate(zip(('Sol','Rebord'),maps)):
            atlas.save(export/f'Trous_{nom}_24.png',optimize=True)
            for y in range(0,atlas.height,24):
                for x in range(0,atlas.width,24):
                    im=atlas.crop((x,y,x+24,y+24))
                    if im.getbbox(): cells[x//24,y//24+p*(atlas.height//24)]=im
        count=write_tilesheet(export/'Kingambit_Trous_24.tile',cells,tile_size=24)
        (export/'Trous_index.json').write_text(json.dumps(dict(taille_tuile=24,sprite=[W,H],cellule=[w,h],
           decalage=[0,(h-H)//2],poses=FRAMES,ticks=TICKS,origine_sol=[0,0],origine_rebord=[0,maps[0].height//24],
           tuiles=count,lignes=entries),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('36 DirSheets animées à 1× ; deux plans × 18 biomes.')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('destination',type=Path)
    ap.add_argument('--art',type=Path,default=HERE/'art/dojo_dedales_trappes')
    ap.add_argument('--export',type=Path)
    a=ap.parse_args();generer(a.destination,a.art,a.export)
