#!/usr/bin/env python3
"""Composite des vrais calques Cliff 0.7.7, en lecture seule."""
from pathlib import Path
from functools import cache
import io,struct,json,hashlib,sys
import numpy as np
from PIL import Image
H=Path.home(); W=H/'.cache/comptoirs-et-falaise'; A=W/'natif'; O=Path(__file__).resolve().parents[1]; A0=W/'Cliff-natif'
P=('jour','aube','crepuscule','nuit'); SZ=(480,520)

@cache
def asset(s):
    b=(A/s).read_bytes(); return b

def unprem(b):
    a=np.array(Image.open(io.BytesIO(b)).convert('RGBA'));al=a[...,3];partial=(al>0)&(al<255)
    if partial.any() and not np.any(a[partial,:3]>al[partial,None]):
        a[partial,:3]=np.minimum(255,np.rint(a[partial,:3].astype(float)*255/al[partial,None])).astype('uint8')
    a[al==0]=0
    return Image.fromarray(a)

@cache
def shard(sheet):
    b=asset(f'Content/Tile/{sheet}.tile');size,n=struct.unpack_from('<ii',b);assert size==8
    table={(x,y):k for x,y,k in struct.iter_unpack('<iiq',b[8:8+n*16])};assert len(table)==n
    return b,table

@cache
def tile(sheet,x,y):
    b,t=shard(sheet)
    if (x,y) not in t:return Image.new('RGBA',(8,8))
    k=t[x,y];n=struct.unpack_from('<q',b,k)[0];im=unprem(b[k+8:k+8+n]);assert im.size==(8,8)
    return im

@cache
def obj(folder,name):
    b=asset(f'Content/{folder}/{name}.dir');n=struct.unpack_from('<q',b)[0];im=unprem(b[8:8+n]); w,h,dr,frames=struct.unpack_from('<iiii',b,8+n)
    assert w*h>0 and frames>0 and im.width%w==0 and im.height%h==0
    return [im.crop((i% (im.width//w)*w,i//(im.width//w)*h,(i%(im.width//w)+1)*w,(i//(im.width//w)+1)*h)) for i in range(frames)]

@cache
def carte(p):
    x=json.loads((A/f'Data/Ground/guilde_cliff_{p}.rsground').read_text(encoding='utf-8-sig'))['Object'];assert x['TexSize']==1 and x['AssetName'].endswith('_'+p)
    return x

def out_layer(p,k,idx=0):
    l=carte(p)['Layers'][k];im=Image.new('RGBA',SZ)
    for x,col in enumerate(l['Tiles']):
        for y,cell in enumerate(col):
            for fr in cell['Layers']:
                ar=fr['Frames'];f=ar[idx%len(ar)] if ar else None
                if f and f['Sheet']:
                    im.alpha_composite(tile(f['Sheet'],f['TexLoc']['X'],f['TexLoc']['Y']),(x*8,y*8))
    return im

def decal(page,orig,anim,i=0):
    lx,ly=orig['X'],orig['Y'];im=anim[max(0,i)%len(anim)];page.alpha_composite(im,(lx,ly))

def sky(p):
    b=Image.new('RGBA',SZ,(12,13,34,255))
    for row in carte(p)['Background']['Layers']:
        bg=row['BG'];q=bg['BGAnim'];i=obj('BG',q['AnimIndex'])[0];x,y=map(bg['MapLoc'].get,['X','Y'])
        X=range(x%i.width-i.width,SZ[0],i.width) if bg['RepeatX'] else [x]
        Y=range(y%i.height-i.height,SZ[1],i.height) if bg['RepeatY'] else [y]
        for xx in X:
            for yy in Y:b.alpha_composite(i,(xx,yy))
    return b

def decor(p,opening=False):
    doc=carte(p);base=Image.new('RGBA',SZ);top=Image.new('RGBA',SZ);tex=doc['Layers'];assert tex[0]['Name']=='00_Mer_Animee_12Phases'
    for k,row in enumerate(tex[1:],1):
        if row['Visible']:(top if row['Layer']==4 else base).alpha_composite(out_layer(p,k))
    for l in doc['Decorations']:
        visible=l['Visible'] if not opening else l['Name']!='BatimentGuilde'
        if not visible:continue
        can=base if l['Layer']==0 else top
        for row in l['Anims']:
            a=row['ObjectAnim'];v=obj('Object',a['AnimIndex'])[max(0,a['StartFrame'])].copy()
            if a['Alpha']!=255:v.putalpha(v.getchannel('A').point(lambda x:x*a['Alpha']//255))
            can.alpha_composite(v,tuple(row['MapLoc'][j] for j in ('X','Y')))
    base.alpha_composite(top);return base

def render(p,n=0,opening=False):
    b=sky(p);b.alpha_composite(out_layer(p,0,n));b.alpha_composite(decor(p,opening));return b

def foundation():
    A0.mkdir(exist_ok=True)
    for p in P:
        ks=12 if p=='nuit' else 1
        # Static foreground and sky unchanged during the twelve native sea phases.
        d=decor(p);bg=sky(p)
        for k in range(ks):
            v=bg.copy();v.alpha_composite(out_layer(p,0,k));v.alpha_composite(d);v.save(A0/f'{p}-{k:02}.png',optimize=True)
        d.save(A0/f'{p}-decor.png',optimize=True)
        print(p,ks,'images')

if __name__=='__main__':foundation()
