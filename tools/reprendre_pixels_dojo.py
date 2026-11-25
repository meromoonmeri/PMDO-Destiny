#!/usr/bin/env python3
"""Reprise à 1× des trois intérieurs de Kingambit ; aucune interpolation ni redimensionnement.

python tools/reprendre_pixels_dojo.py --source /checkout-avant --out /copie/vide
La source contient game/Data/Ground et game/Content/Tile. Le programme ne touche
qu'au dessin des calques et ajoute le repère de retour dans l'accueil Kingambit.
"""
import argparse
from copy import deepcopy
import json
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageColor

import render_ground_moteur as render
from lib_tiles import write_tilesheet

ROOMS = {
    'dojo_kingambit': 'Kingambit_Accueil_Natif',
    'dojo_kingambit_arene': 'Kingambit_Arene_Natif',
    'dojo_kingambit_reliques': 'Kingambit_Reliques_Natif',
}


def rampe(*tones):
    return np.array([ImageColor.getrgb(x) for x in tones],dtype=np.uint8)


GRES = rampe('#25222e','#3b3039','#4e3e40','#634c43','#7b624c','#937959',
             '#a78d62','#b59a6b','#c7af7e','#d9c296','#f2d9a5')
CUIVRE = rampe('#322a32','#573738','#73413e','#934f40','#ad6143','#c6794b',
               '#db8a4f','#e99b58','#f1b473','#f8cd86','#ffe9a8')
VERT = rampe('#19262e','#263239','#305058','#3c6362','#4c766d','#5a8b79',
             '#79a593','#98bdaa','#adcdb4','#c7dec4','#e0f2d0')
CRISTAL = rampe('#23313e','#264657','#286274','#327d90','#429aab','#57c2c9',
               '#7edcda','#90e9dc','#a4f4e8','#c0f9ea','#d8fff3')


def nettoyer(im, stylise):
    a = np.asarray(im).copy()
    alpha = a[:,:,3]
    # Rives : clusters binaires sur les bords de roche. Les ombres au sol
    # restent des aplats à quelques densités, pas une frange interpolée.
    if stylise:
        a[:,:,3] = np.where(alpha>=126,255,np.where(alpha>=46,95,0))
    else:
        a[:,:,3] = np.select([alpha>=208,alpha>=105,alpha>=50], [255,144,72], 0)
    rgb = a[:,:,:3].astype(np.int16)
    med = np.asarray(im.convert('RGB').filter(ImageFilter.MedianFilter(3)),dtype=np.int16)
    y = (3*rgb[:,:,0] + 6*rgb[:,:,1] + rgb[:,:,2])//10
    ym = (3*med[:,:,0] + 6*med[:,:,1] + med[:,:,2])//10
    # Un trait franc (joint, flamme, bord de cristal) n'est pas moyenné.
    doux = (abs(y-ym)<=13) & (alpha>=126)
    if not stylise:
        arr = np.where(doux[:,:,None], (rgb+med*2)//3, rgb)
        a[:,:,:3] = np.minimum((arr+3)//7*7,255).astype(np.uint8)
        # Les flammes et enseignes DS qui étaient déjà nettes gardent leur dessin.
        r,g,b = rgb.transpose(2,0,1)
        accent = (r-g>45)&(r>180)|(g-r>30)|(b-r>40)
        a[accent,:3] = rgb[accent].astype(np.uint8)
    else:
        r,g,b = rgb.transpose(2,0,1)
        n = np.where(doux,(2*y+ym*3)//5,y)
        ix = np.digitize(n,[38,53,69,88,105,124,145,167,186,207])
        work = GRES[ix]
        metal=(g>=r+4)&(g>=b-5)&(r<152)
        rubis=(r>g+34)&(r>b+48)
        cyan=(b>=r+32)&(g>=r+30)
        work[metal] = VERT[ix[metal]]
        work[rubis] = CUIVRE[np.clip(ix[rubis]+1,0,10)]
        work[cyan] = CRISTAL[ix[cyan]]
        a[:,:,:3] = work
    a[a[:,:,3]==0] = 0
    return Image.fromarray(a)


def grain_sable(im):
    """Quelques grains à 1×, sur le sable seulement ; même contact sur 00/01."""
    a = np.asarray(im).copy()
    y0,y1 = 157,im.height
    rng = random.Random(45013)
    for _ in range(1950):
        x,y = rng.randrange(27,im.width-28),rng.randrange(y0,y1-4)
        ink = rng.choice(((4,5,2),(-6,-5,-4),(5,4,3),(-7,-5,-5)))
        forme = rng.choice((((0,0),(1,0)),((0,0),(1,0),(1,1)),((0,0),),((0,0),)))
        for dx,dy in forme:
            c = a[y+dy,x+dx]
            if c[3]==255 and (tuple(c[:3])==tuple(GRES[6]) or tuple(c[:3])==tuple(GRES[7])):
                a[y+dy,x+dx,:3] = np.asarray(c[:3],dtype=int)+ink
    return Image.fromarray(a)


def polygone(x,y,rx,ry):
    return [(x-rx,y-ry//2),(x-rx//2,y-ry),(x+rx//2,y-ry),(x+rx,y-ry//2),
            (x+rx,y+ry//2),(x+rx//2,y+ry),(x-rx//2,y+ry),(x-rx,y+ry//2)]


def sceau(w,h,arene,phase):
    im = Image.new('RGBA',(w,h)); d = ImageDraw.Draw(im)
    cx,cy = (384,279) if arene else (384,270)
    size = (118,98) if arene else (52,47)
    flash = ('#d98950','#e09753','#e8a55d','#f0b368','#f1bc70','#f6c47c',
             '#f1bc70','#ecb166','#e8a55d','#e09753','#d98950','#d4824c')[phase]
    def cercle(dx,dy,shade):
        rx,ry=size[0]-dx,size[1]-dy
        d.polygon(polygone(cx,cy,rx,ry),fill=shade)
    if arene:
        cercle(0,0,'#513d37'); cercle(1,3,'#bca273'); cercle(4,6,'#765a45')
        cercle(7,10,'#443d3c'); cercle(10,13,'#a38b65')
        cercle(24,23,'#574641'); cercle(27,26,'#c2a67a'); cercle(30,28,'#846d53')
        cercle(32,30,'#a48b61')
        steps=[(-85,-63),(-57,-83),(-35,-85),(-12,-85),(11,-85),(35,-85),(56,-83),(85,-63),
               (-100,-38),(-100,-18),(-100,4),(-100,26),(100,-38),(100,-18),(100,4),(100,26),
               (-85,62),(-57,82),(-35,84),(-12,84),(11,84),(35,84),(56,82),(85,62)]
        d.line(polygone(cx,cy,90,73)+[polygone(cx,cy,90,73)[0]],fill='#9c704f')
        d.line(polygone(cx,cy,94,77)+[polygone(cx,cy,94,77)[0]],fill='#d08c56')
        for i,(x,y) in enumerate(steps):
            dx,dy=cx+x,cy+y
            if i%3==0:
                d.polygon([(dx,dy-4),(dx+4,dy),(dx,dy+4),(dx-4,dy)],fill='#795547')
                d.line((dx-2,dy,dx,dy-2,dx+2,dy), fill=flash)
            elif i%3==1:
                d.line((dx-3,dy+3,dx-3,dy-2,dx,dy-2,dx,dy+2,dx+3,dy+2), fill=flash,width=1)
            else:
                d.line((dx-3,dy+2,dx,dy-2,dx+3,dy+2), fill=flash,width=1)
                d.point((dx,dy+3),fill='#be8057')
    else:
        cercle(0,0,'#51413b'); cercle(1,2,'#cfb380'); cercle(3,4,'#867557')
        cercle(5,6,'#4d5650'); cercle(7,8,'#84a18c'); cercle(9,11,'#52716b')
        cercle(12,13,'#374b4c'); cercle(14,15,'#ad855c'); cercle(16,17,'#735445')
        for dx,dy in [(-40,-20),(-24,-36),(0,-39),(24,-36),(40,-20),(-40,20),(-24,36),(0,39),(24,36),(40,20),(-43,0),(43,0)]:
            x,y=cx+dx,cy+dy
            d.line((x-2,y,x,y-2,x+2,y,x,y+2,x-2,y),fill='#d3ae78')
        # Lame centrale et ailettes de la crête de Kingambit, incrustées dans la pierre.
        pts=[(-24,11),(-11,0),(-21,-9),(-12,-10),(-4,-5),(-2,-18),(2,-18),(4,-5),
             (12,-10),(21,-9),(11,0),(24,11),(17,14),(6,10),(0,20),(-6,10),(-17,14)]
        d.polygon([(cx+x,cy+y+2) for x,y in pts],fill='#4d3737')
        d.polygon([(cx+x,cy+y) for x,y in pts],fill='#b7744b',outline=flash,width=1)
        d.line((cx,cy-16,cx,cy+12), fill=flash)
    return im


class Bank:
    def __init__(self,name,size):
        self.name,self.size = name,size
        self.cells,self.seen = {},{}

    def frame(self,im):
        x=y=0; name=''
        if im.getbbox():
            key=im.tobytes()
            xy=self.seen.get(key)
            if xy is None:
                j=len(self.cells);xy=j%64,j//64
                self.seen[key]=xy;self.cells[xy]=im
            x,y=xy;name=self.name
        return {'Sheet':name,'TexLoc':{'X':x,'Y':y}}

    def encode(self,ims,tick):
        s = self.size
        n,m = ims[0].width//s, ims[0].height//s
        cols = []
        for x in range(n):
            col = []
            for y in range(m):
                bb=(x*s,y*s,x*s+s,y*s+s)
                frames=[self.frame(i.crop(bb)) for i in ims]
                if all(f==frames[0] for f in frames): frames=frames[:1]
                col.append({'AutoTileset':'','Associates':[],'Layers':
                            [{'Frames':frames,'FrameLength':tick if len(frames)>1 else 60}]
                            if any(f['Sheet'] for f in frames) else [],'NeighborCode':-1})
            cols.append(col)
        return cols


def reprendre(nom, out):
    p = render.ROOT/f'game/Data/Ground/{nom}.rsground'
    doc = json.loads(p.read_text(encoding='utf-8-sig')); o=doc['Object']
    king=nom.startswith('dojo_kingambit'); isarena=nom.endswith('_arene')
    px = 8*o['TexSize']; w=len(o['Layers'][0]['Tiles'])*px;h=len(o['Layers'][0]['Tiles'][0])*px
    bank=Bank(ROOMS[nom],px)
    l = o['Layers']
    for i,a in enumerate(l):
        tracks=[t for col in a['Tiles'] for c in col for t in c['Layers'] if len(t['Frames'])>1]
        if tracks:
            counts={(len(t['Frames']),t['FrameLength']) for t in tracks}
            assert len(counts)==1,(nom,a['Name'],counts)
            phases,tick=next(iter(counts))
        else: phases,tick=1,60
        if king and i==7:
            phases,tick=12,6
            frames=[sceau(w,h,isarena,j) for j in range(phases)]
        else:
            frames=[]
            for j in range(phases):
                im=render._calque(o,a,px,w,h,j)
                if king and 1<=i<=3:
                    # La couche 00 fournit le sable sous les nouveaux sceaux.
                    # Ne pas garder l'ancien disque à la fois sous et autour du nouveau.
                    if isarena: bb=(252,176,516,397)
                    else: bb=(334,206,433,348)
                    d=ImageDraw.Draw(im); d.rectangle(bb,fill=(0,0,0,0))
                if king and i==5:
                    # Le coeur de la flamme EoS est déjà pixel-perfect, pas ses halos.
                    alpha=im.getchannel('A').point(lambda x: 255 if x>=126 else 0)
                    im.putalpha(alpha)
                else:
                    im=nettoyer(im,king)
                    if king and i in (0,1):
                        im=grain_sable(im)
                frames.append(im)
        a['Tiles']=bank.encode(frames,tick)
    if nom=='dojo_kingambit':
        markers=o['Entities'][0]['Markers']
        assert len(markers)==3
        mark=deepcopy(markers[-1]); mark.update(EntName='RetourDedalesMarker',Direction=4)
        mark['Collider'].update(X=376,Y=336); markers.append(mark)
    assert all(not (s and im is None) for (s,x,y),im in render.Planches._tiles.items())
    dest=out/f'game/Data/Ground/{nom}.rsground';dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(doc,f,ensure_ascii=False,separators=(',',':'));f.write('\n')
    tab=out/f'game/Content/Tile/{bank.name}.tile';tab.parent.mkdir(parents=True,exist_ok=True)
    with tab.open('xb'): pass
    print(nom,w,h,px,write_tilesheet(tab,bank.cells,tile_size=px),flush=True)


def produire(source,out):
    render.ROOT=source; render.Planches._slots.clear(); render.Planches._tiles.clear()
    for n in ROOMS: reprendre(n,out)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();produire(a.source,a.out)
