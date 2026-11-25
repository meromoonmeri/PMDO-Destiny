#!/usr/bin/env python3
"""Dix-huit wooshes Kingambit. Dessin au pixel + synthèse originale, sans copie de Dazzling.
Dépendances : Pillow, NumPy, SciPy, FFmpeg/libvorbis. Sortie Content/BG et Content/Sound/Battle.
Le PNG de revue est alpha droit ; la banque RogueEssence est RGBA prémultiplié.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import io
import json
import math as m
from pathlib import Path
import random
import struct
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.signal import butter, sosfilt

W,H=320,240
POSES,TICKS=28,3
DURATION=POSES*TICKS/60
COLS=7
NATIVE='Kingambit_Prebataille_'
TAU=m.tau
NEAR=Image.Resampling.NEAREST


@dataclass(frozen=True)
class Costume:
    id:str
    type:str
    boss:str
    titre:str
    motif:str
    core:str
    light:str
    trim:str
    low:str
    ys:tuple
    sides:tuple
    pose:int
    f0:int
    f1:int
    pulse:tuple


COSTUMES=(
    Costume('normal','Normal','Lockpin','Double écho','Bandes crème à rebonds et cercles d’écho','#b99365','#ffe8bc','#eac385','#4d4041',(38,81,121,162,204),(1,-1,1,-1,1),14,330,588,(1,1.25,1.5)),
    Costume('fire','Feu','Braségali','Braises en éventail','Rubans de flamme et gerbes de braises ascendantes','#ea4d39','#fff0a5','#ffab4c','#682d37',(42,91,139,187),(1,-1,1,-1),13,205,585,(.5,1,1.33)),
    Costume('water','Eau','Tortank','Roulis des marées','Vagues roulantes et écume dans le sillage','#257ecb','#d4fff8','#63dfe7','#244b7d',(39,91,145,193),(1,1,-1,1),15,230,416,(1,.79,1.22)),
    Costume('grass','Plante','Jungko','Entrelacs de feuilles','Tiges sinueuses et feuilles qui se décrochent','#4caa60','#eeffc3','#b7df75','#2a5a46',(37,80,118,159,207),(1,-1,1,-1,1),15,410,650,(1,1.3,1.67)),
    Costume('electric','Électrik','Élecsprint','Circuit foudroyant','Trajets brisés, impulsions et filaments jaunes','#e9a739','#fff7c5','#ffe080','#78463b',(35,77,122,163,204),(-1,1,1,-1,1),12,400,1430,(1,1.54,1.12)),
    Costume('ice','Glace','Oniglali','Fracture polaire','Lames effilées, cristaux et éclats givrés','#5da7db','#e5fff9','#a4e8ef','#3d5785',(34,75,119,165,207),(-1,-1,1,1,-1),15,610,965,(1,1.51,2.02)),
    Costume('fighting','Combat','Lucario','Frappes croisées','Deux frappes latérales et un impact en chevrons','#da643e','#ffe8ae','#f9ab70','#5c3945',(52,108,158,202),(1,-1,1,-1),13,152,283,(.62,1,1.18)),
    Costume('poison','Poison','Ectoplasma','Miasme à bulles','Bourrelets violets et bulles légères qui remontent','#9c55b9','#ffe8fb','#dba2f4','#603c79',(47,97,144,192),(1,-1,1,1),15,186,369,(1,.71,1.26)),
    Costume('ground','Sol','Laggron','Lignes de faille','Strates basses, cassure et grains de sable','#c28049','#ffebba','#e4b375','#755344',(64,104,152,194),(1,-1,-1,1),15,110,240,(.77,1,.61)),
    Costume('flying','Vol','Dracaufeu','Plumes d’alizé','Courbes rapides, plumes en piqué et sillages de vent','#518abd','#e7fff7','#99e7e5','#365579',(33,75,120,166,206),(-1,1,-1,-1,1),14,350,805,(1,1.29,1.65)),
    Costume('psychic','Psy','Alakazam','Réfraction mentale','Plans prismatiques en miroir et doubles échos de l’œil','#ab62c8','#ffe9f7','#efa6d9','#544685',(37,78,120,162,202),(1,-1,1,-1,1),14,285,632,(1,1.43,1.9)),
    Costume('bug','Insecte','Dardargnan','Ruée de l’essaim','Alvéoles découpées et petites ailes en cadence','#91a848','#fbffbd','#d3e583','#495842',(32,77,121,166,208),(1,-1,1,1,-1),13,550,884,(1,1.12,1.42)),
    Costume('rock','Roche','Tyranocif','Éclats de carrière','Plaques cassantes, roche taillée et chute de fragments','#a78263','#fce1b6','#dab58e','#625360',(44,94,145,193),(-1,1,-1,1),16,115,293,(1,.81,1.36)),
    Costume('ghost','Spectre','Branette','Feux-follets','Veilleuses translucides et ombres en contre-courant','#7770be','#e8e5ff','#a9acf2','#414064',(39,81,119,161,204),(-1,1,-1,1,-1),16,190,315,(1,1.41,.74)),
    Costume('dragon','Dragon','Altaria','Sillage des écailles','Longues courbes en S, écailles et signe draconique','#7860cb','#f4e7ff','#c4a2ff','#493d79',(32,77,120,165,207),(1,-1,1,-1,1),15,171,478,(1,1.5,1.89)),
    Costume('dark','Ténèbres','Démolosse','Croissants nocturnes','Fentes d’ombre, croissants et étincelles rouges','#765481','#f2cddd','#cd819b','#3a304d',(41,83,118,160,205),(-1,1,1,-1,1),15,151,306,(1,.75,.52)),
    Costume('steel','Acier','Métalosse','Verrou magnétique','Rails à rivets qui coulissent, s’emboîtent et se libèrent','#7d9eae','#f2fbf6','#afe0eb','#475b73',(34,76,122,163,205),(1,-1,-1,1,-1),14,430,710,(1,1.486,2.34)),
    Costume('fairy','Fée','Gardevoir','Étoiles de soie','Bandes or et rose, étoiles et pétales en cascade','#db7bc0','#fff2cf','#f3b7d9','#784968',(31,75,119,164,208),(1,-1,1,-1,1),15,525,925,(1,1.34,1.68)),
)


def u(x):return max(0.,min(1.,x))
def s(x):x=u(x);return x*x*(3-2*x)
def lerp(a,b,q):return a+(b-a)*q
def win(t,a,b,c,d):return s((t-a)/(b-a))*(1-s((t-c)/(d-c)))
def color(value):return tuple(bytes.fromhex(value.lstrip('#')))
def mix(a,b,q):return tuple(round(lerp(a[i],b[i],q)) for i in range(3))
def rgba(t,alpha=1):return (*t, round(255*u(alpha)))
def blank():return Image.new('RGBA',(W,H))
def points(*p):return list(zip(p[::2],p[1::2]))


def seal(k):
    """Une silhouette originale distincte à 48 px, et non un pictogramme recoloré."""
    a=Image.new('RGBA',(48,48));d=ImageDraw.Draw(a)
    c,l,h,b=[color(getattr(k,x)) for x in ('core','light','trim','low')]
    def poly(p,f,o=None):d.polygon(points(*p),fill=f,outline=o)
    def line(p,f,w=1):d.line(points(*p),fill=f,width=w)
    def ellipse(box,f,o=None,w=1):d.ellipse(box,fill=f,outline=o,width=w)
    def star(x,y,r,f,o=None,rot=-m.pi/2):
        q=[(round(x+m.cos(rot+i*m.pi/5)*(r if i%2==0 else .44*r)),
            round(y+m.sin(rot+i*m.pi/5)*(r if i%2==0 else .44*r))) for i in range(10)]
        d.polygon(q,fill=f,outline=o)
    key=k.id
    if key=='normal':
        for r in (19,13):
            box=(24-r,24-r,24+r,24+r)
            for start in (20,200):
                d.arc(box,start,start+140,fill=b,width=4);d.arc(box,start+5,start+128,fill=h,width=2)
        poly((24,14,32,25,24,34,16,25),h,b);poly((24,16,30,24,24,28,18,24),l)
        d.point((24,10),fill=l);d.point((24,39),fill=l)
    elif key=='fire':
        poly((24,4,31,12,29,19,35,17,41,24,40,35,33,42,18,43,9,36,7,28,12,21,15,24,17,15),c,b)
        poly((23,11,26,22,23,29,29,26,33,20,37,29,35,37,29,42,19,41,13,34,15,29,18,31,20,22),h)
        poly((24,25,27,34,31,32,29,39,24,42,19,38,20,33),l)
        line((10,25,8,31,12,36),h);line((25,7,27,13),h)
    elif key=='water':
        poly((5,31,9,21,15,17,21,18,22,24,19,27,16,27,18,22,13,24,12,30,17,33,22,31,25,24,31,13,36,9,40,10,45,16,44,23,41,26,37,25,38,21,41,21,40,16,36,16,31,27,28,37,21,41,12,40,7,37),c,b)
        line((6,31,10,22,15,18,20,19,22,22),l,2);line((24,29,28,20,33,12,37,10,41,12,44,16),h,3)
        line((13,32,20,36,26,33,29,28,32,21),h,2);ellipse((33,30,37,35),l);ellipse((12,11,15,14),h)
    elif key=='grass':
        poly((23,39,19,28,10,25,6,17,6,10,17,13,23,18,24,26,27,28,30,20,38,15,43,15,41,23,36,31,28,35,26,41),c,b)
        poly((7,11,17,14,22,19,24,28,18,23,12,20),h);poly((42,17,38,24,31,30,27,30,31,23),h)
        line((10,13,20,22,23,32,25,40),l,2);line((27,34,32,28,40,19),l,2)
        poly((26,23,22,16,25,9,31,5,31,15,28,22),c,b);line((26,20,27,14,29,8),h)
    elif key=='electric':
        poly((29,4,10,25,21,25,15,43,40,17,29,18,35,6),h,b)
        poly((28,7,14,23,24,23,19,35,36,19,27,20),l)
        line((34,30,40,25,42,20),h,1);line((7,20,11,14,15,12),c,2)
    elif key=='ice':
        for i in range(6):
            a0=TAU*i/6-m.pi/2;x,y=m.cos(a0),m.sin(a0);xb,yb=-y,x
            q=[(round(24+x*r+xb*w),round(24+y*r+yb*w)) for r,w in ((4,-2),(14,-3),(20,0),(14,3),(4,2))]
            d.polygon(q,fill=h,outline=b);line((24,24,round(24+x*16),round(24+y*16)),l,2)
        poly((24,14,32,20,32,28,24,34,16,28,16,20),c,b)
        poly((24,17,29,24,24,31,19,24),l)
    elif key=='fighting':
        poly((8,17,13,11,17,11,20,8,25,9,28,7,35,9,40,14,41,23,36,31,36,40,21,43,13,36,12,30,7,24),c,b)
        poly((8,17,14,14,21,19,21,26,15,28,10,24),h,b);poly((22,22,38,19,38,25,33,33,29,35,22,33),h)
        line((15,13,19,12,24,14,28,11,35,12,38,16),l,2);line((23,10,25,17,25,20),b)
        line((31,10,32,15,31,20),b);line((15,33,21,36,34,35),b,2)
    elif key=='poison':
        for x,y,r in [(13,30,9),(32,30,12),(24,13,11)]:
            ellipse((x-r,y-r,x+r,y+r),b);ellipse((x-r+2,y-r+2,x+r-1,y+r-1),c)
            d.arc((x-r+3,y-r+3,x+r-3,y+r-3),310,140,fill=h,width=2)
            ellipse((x-r/2-1,y-r/2,x-r/2+2,y-r/2+2),l)
        poly((4,16,7,12,9,16,7,19),h);d.point((37,9),fill=l)
    elif key=='ground':
        poly((5,16,16,13,25,15,34,12,43,15,42,36,34,40,24,37,17,40,7,36),c,b)
        poly((6,17,16,13,25,16,34,13,42,15,34,22,25,21,18,24,7,22),h)
        line((6,28,16,31,25,29,35,30,42,27),b,3);line((7,25,17,27,25,25,33,26,41,24),h,2)
        poly((24,14,21,22,25,25,23,30,28,35,26,41,28,40,31,35,28,29,31,25,26,21,28,14),b)
        line((8,17,16,15,21,16),l,2);line((32,15,35,14,39,15),l)
    elif key=='flying':
        poly((6,39,13,32,14,23,20,16,26,13,26,17,31,9,40,6,44,7,41,15,37,19,40,20,35,27,27,32,18,34,8,42),h,b)
        poly((17,23,21,17,24,16,22,20,29,17,36,11,41,8,38,15,31,22,28,25,21,27),l)
        line((8,39,17,30,28,22,37,12),b,2);line((16,32,22,33,30,30),c,2)
    elif key=='psychic':
        poly((24,4,45,24,24,44,3,24),h,b);poly((24,9,39,24,24,39,9,24),c,b)
        poly((9,24,15,19,24,17,33,19,39,24,33,29,24,31,15,29),l,b)
        ellipse((20,19,29,29),b);ellipse((22,21,27,27),c);ellipse((23,21,25,23),l)
        line((5,24,24,6,43,24),l)
    elif key=='bug':
        poly((24,4,42,14,42,34,24,44,6,34,6,14),b);line((6,14,24,4,42,14,42,34,24,44,6,34,6,14),c,2)
        poly((23,27,16,25,8,17,10,13,16,13,23,21),l,b);poly((25,27,32,25,40,17,38,13,32,13,25,21),l,b)
        ellipse((19,15,29,24),h,b);poly((20,22,28,22,30,30,24,39,18,30),h,b)
        line((20,28,28,28),b,2);line((23,17,20,11,17,10),h);line((25,17,28,11,31,10),h)
    elif key=='rock':
        poly((4,33,10,19,18,15,22,9,33,12,42,19,44,33,33,41,14,40),c,b)
        poly((22,10,32,13,38,20,28,21,18,17),l,b);poly((11,20,18,17,28,22,25,30,16,35,6,33),h,b)
        poly((29,23,41,20,44,33,34,39,25,31),c,b);poly((6,34,16,36,25,32,33,40,14,40),b)
        line((22,12,28,14,34,16),l,2);line((11,22,16,19,22,22),l)
    elif key=='ghost':
        poly((27,5,35,11,35,18,42,22,42,31,37,37,28,42,15,41,8,37,6,32,13,34,16,28,12,23,15,18,21,19,24,14,24,8),c,b)
        poly((30,8,33,13,31,19,36,21,39,26,36,33,29,37,20,38,16,35,20,30,19,24,26,22,29,14),h)
        ellipse((23,25,27,29),b);ellipse((32,24,35,28),b);d.point((24,25),fill=l);d.point((33,24),fill=l)
        line((12,35,19,39,29,39,37,35),l,1)
    elif key=='dragon':
        poly((9,34,13,23,11,18,16,20,16,10,23,16,29,6,31,16,37,20,42,25,42,30,35,31,36,34,29,35,25,43,16,40),c,b)
        poly((15,24,19,15,22,20,28,15,33,19,40,24,35,26,30,24,24,28,21,36,16,38,12,34),h)
        poly((36,26,41,26,40,29,33,30,34,33,30,34,29,29),l,b)
        poly((25,22,30,20,32,22,29,24),l);line((14,30,20,26,20,29,17,32,19,34,16,37),b)
    elif key=='dark':
        ellipse((5,5,41,41),b);ellipse((6,6,40,40),c);ellipse((11,6,43,34),(0,0,0,0))
        d.arc((6,6,40,40),45,220,fill=h,width=2)
        poly((31,11,34,17,40,20,34,21,30,27,30,21,24,19,30,16),l,b)
        d.point((39,11),fill=h);d.point((42,19),fill=c)
    elif key=='steel':
        q=[]
        for i in range(40):
            a0=TAU*i/40;r=20 if i%5 in (1,2,3) else 16
            q.append((round(24+r*m.cos(a0)),round(24+r*m.sin(a0))))
        d.polygon(q,fill=c,outline=b)
        d.arc((8,8,40,40),180,310,fill=l,width=2);d.arc((8,8,40,40),25,140,fill=b,width=2)
        ellipse((13,13,35,35),h,b,2);poly((24,16,32,24,24,32,16,24),b);poly((24,19,29,24,24,29,19,24),l)
    elif key=='fairy':
        star(22,24,20,c,b);star(22,23,16,l,h);star(22,24,10,h)
        star(37,12,8,h,b,-1.25);star(37,12,5,l);star(12,38,6,l,b,-1.)
        poly((36,31,42,33,40,38,36,38,33,35),h,b);d.point((23,23),fill=(255,252,245))
    else:raise ValueError(key)
    mask=a.getchannel('A');border=Image.new('RGBA',a.size,(23,24,38));border.putalpha(mask.filter(ImageFilter.MaxFilter(3)))
    border.alpha_composite(a)
    return border


def alpha(im,gain):
    if gain>=.999:return im
    d=im.copy();d.putalpha(d.getchannel('A').point([round(i*u(gain)) for i in range(256)]));return d


def pin(dst,im,x,y,size,gain=1,rotate=0):
    if size<1 or gain<=0:return
    im=im.resize((max(1,round(size)),max(1,round(size))),NEAR)
    if rotate:im=im.rotate(rotate,resample=NEAR,expand=True)
    dst.alpha_composite(alpha(im,gain),(round(x-im.width/2),round(y-im.height/2)))


def form(k,x,t,i):
    """Découpe et déplacement : trajectoires propres aux 18 types."""
    z=x/W; a=TAU*z
    tri=lambda f: 2*abs((f%1)*2-1)-1
    return {
        'normal':2.5*m.sin(a*1.5-t*5+i*.8),
        'fire':-8*z+4*tri(z*5.2+t*2.1+i*.2),
        'water':8*m.sin(a*1.36-t*10+i*.78)+2*m.sin(a*2.9-t*12),
        'grass':8*m.sin(a*.86+t*6+i*.84)+3*m.sin(a*1.93-t*6),
        'electric':6*tri(z*4.1-t*4.1+i*.31)+(3 if i%2 else -3),
        'ice':((i%3-1)*9)*(z-.35)+3*tri(z*2.7+i*.25),
        'fighting':19*(z-.5)*(1 if i%2 else -1)+2*tri(z*2),
        'poison':6*m.sin(a*.78+i*1.2-t*3.5)-14*t+3*m.sin(a*2.0),
        'ground':(6 if z>.56+i*.02 else -2)+2.8*tri(z*3.3-i*.20),
        'flying':-13*m.sin(a*.60+i*.41)+13*(z-.43),
        'psychic':(8+15*abs(z-.51))*(z-.5)*(1 if i%2 else -1)+3*tri(z*2+i/3),
        'bug':5*tri(z*3.7+i/4)+4*m.sin(t*23+i),
        'rock':6*tri(z*3.1+i*.13)+5*tri(z*1.65-i*.21),
        'ghost':12*m.sin(a*.55+i*.89+t*5.3)-7*(t-.4),
        'dragon':13*m.sin(a*.92-t*6+i*.73)+4*m.sin(a*1.9+i*.2),
        'dark':(6 if i%2 else -6)+13*(z-.5)*(1 if i%2 else -1)+4*m.sin(a*.8+i),
        'steel':4*round(1.7*tri(z*1.65+i*.35)),
        'fairy':3.4*m.sin(a*.68+i*.51-t*2.7),
    }[k]


def band(dst,k,t,y,sign,i,icon):
    begin=.045+i*.045 if k.id not in ('electric','fighting','psychic','steel') else .067+abs(i-1.7)*.038
    end=.43 if k.id in ('electric','fighting','flying') else (.56 if k.id in ('rock','ghost','water') else .49)
    p=(t-begin)/end
    gain=win(t,begin,begin+.085,.74+(.016*(i%3)),.96)
    if gain<=0 or p<0:return
    c,l,hi,b=[color(getattr(k,x)) for x in ('core','light','trim','low')]
    head=-36+400*(.63*s(p)+.37*p)+405*max(0,p-1)
    length=288+18*(i%3)+(29 if k.id in ('water','dragon','steel') else 0)
    # Taper at both ends, with a longer lit tail and separate foil trim.
    wide=(7,10,12,8,10)[i]*(1.15 if k.id in ('fire','poison','rock') else 1.)
    wide*=1-.35*s((t-.72)/.23)
    controls=[]
    for gx in range(max(-28,int(head-length)),min(W+28,int(head))+1,5):
        q=u((int(head)-gx)/length);x=gx if sign>0 else W-gx
        yy=y+form(k.id,gx,t,i)
        wid=wide*(.39+.61*s((1-q)/.38))*(.35+.65*s(q/.16))
        if k.id in ('ice','electric','rock','steel'):wid*=.73+.27*((int(gx)//12+i)%3!=0)
        if k.id in ('water','ghost','dragon'):wid*=.89+.23*m.sin(gx/31-t*5+i)
        controls.append((round(x),round(yy),wid))
    if len(controls)<2:return
    d=ImageDraw.Draw(dst)
    def contour(f0,f1,ink):
        a=[(x,round(y+r*f0)) for x,y,r in controls];b1=[(x,round(y+r*f1)) for x,y,r in reversed(controls)]
        d.polygon(a+b1,fill=ink)
    # Different opacities preserve silhouettes beyond the central crest.
    contour(-1.19,1.15,rgba(b,gain*.72))
    contour(-.95,.92,rgba(c,gain*(.67 if k.id in ('ghost','dark') else .86)))
    contour(-.78,-.45,rgba(hi,gain*.92))
    contour(-.30,.02,rgba(mix(c,hi,.32),gain*.91))
    contour(.42,.66,rgba(hi,gain*.76))
    for level in (-.95,.81):
        cpts=[(x,round(yy+wid*level)) for x,yy,wid in controls]
        d.line(cpts,fill=rgba(l,gain*.62),width=1)
    for j in range(2,len(controls)-2,3 if k.id in ('steel','bug','electric') else 5):
        if (j+i)%4==0 and k.id not in ('steel','bug'):continue
        x0,y0,wid=controls[j];x1,y1,_=controls[j+2]
        if k.id in ('steel','bug','ground'):
            d.line((x0,y0+2,x0+3*sign,y0-2,x0+6*sign,y0-2),fill=rgba(b,gain*.84),width=2)
            d.point((x0+4*sign,y0-2),fill=rgba(l,gain*.97))
        elif k.id in ('fire','ice','psychic','fighting','rock'):
            d.polygon([(x0,round(y0+wid*.42)),(x0+4*sign,y0-2),(x1+5*sign,y1-3)],fill=rgba(l,gain*.81))
        else:
            d.line((x0,y0-1,x1,y1-1),fill=rgba(l,gain*.69),width=1)
    hx=head if sign>0 else W-head;hy=y+form(k.id,head,t,i)
    if -22<hx<W+22:
        if k.id=='electric':d.line((round(hx-sign*23),round(hy+4),round(hx-sign*12),round(hy-6),round(hx),round(hy)),fill=rgba(l,gain),width=2)
        pin(dst,icon,hx,hy,20+(i%3)*2,gain*.93,rotate=(3 if sign==1 else -3))
        d=ImageDraw.Draw(dst);u0=(round(hx+5*sign),round(hy));d.point(u0,fill=rgba(l,gain))


def particles(dst,k,t,seed,front):
    rng=random.Random(seed);d=ImageDraw.Draw(dst)
    c,l,h,b=[color(getattr(k,x)) for x in ('core','light','trim','low')]
    peak=k.pose/(POSES-1)
    for j in range(79):
        phase=rng.uniform(.12,.48);life=rng.uniform(.21,.56);x0=rng.uniform(-14,W+14);lane=rng.randrange(len(k.ys))
        ang=rng.uniform(0,TAU);jitter=rng.uniform(-10,10);r=rng.uniform(30,133);z=(t-phase)/life
        attack=j%3==0
        if front!=(j%4>1):continue
        if attack:
            phase=peak-.09+rng.uniform(0,.21);z=(t-phase)/life
        if not 0<=z<1:continue
        gain=win(z,0,.18,.49,1)*(1-s((t-.81)/.18));mag=rng.choice((1,1,2,2,3,4));colr=(h,l,c)[j%3]
        if attack:
            q=(1-(1-z)**2);x=160+m.cos(ang)*(19+q*r);y=118+m.sin(ang)*(13+q*r*.67)
        else:
            x=x0+k.sides[lane]*(42+36*r/133)*z
            y=k.ys[lane]+form(k.id,x,t,lane)+jitter+z*m.sin(ang)*17
        if k.id in ('fire','poison','ghost'):y-=39*z
        if k.id in ('rock','ground','ice'):y+=19*z*z
        if k.id in ('water','flying','dragon'):y+=11*m.sin(ang+t*10)*z
        if k.id=='electric':x+=6*m.sin(z*24);y+=6*m.cos(z*20)
        if mag<2:
            d.point((round(x),round(y)),fill=rgba(colr,gain*.92));continue
        x,y=round(x),round(y); ink=rgba(colr,gain*(.65 if k.id=='ghost' else .94));spark=rgba(l,gain*.95)
        if k.id in ('ice','rock','ground','dark','dragon'):
            d.polygon([(x-mag,y+1),(x,y-mag),(x+mag+1,y-mag//2),(x+1,y+mag+1)],fill=ink)
            d.line((x-mag,y+1,x,y-mag,x+mag+1,y-mag//2),fill=spark,width=1)
        elif k.id in ('grass','flying','bug'):
            ix=(1 if j%2 else -1)*mag
            d.polygon([(x-ix,y+mag),(x-ix//2,y-mag),(x+ix,y-mag),(x+ix//2,y+1)],fill=ink)
            d.line((x-ix,y+mag,x+ix-1,y-mag+1),fill=spark)
        elif k.id in ('fairy','psychic','electric'):
            d.line((x-mag*2,y,x+mag*2,y),fill=ink);d.line((x,y-mag,x,y+mag),fill=ink);d.point((x,y),fill=spark)
        elif k.id in ('poison','water','normal','ghost'):
            d.ellipse((x-mag,y-mag,x+mag,y+mag),outline=ink,width=1)
            if mag>=3:d.point((x-1,y-mag+1),fill=spark)
        else:
            d.polygon([(x,y-mag),(x+mag,y),(x+1,y+mag),(x-1,y+mag),(x-mag,y)],fill=ink)
            d.point((x,y),fill=spark)


def symbol(dst,k,icon,t):
    q=k.pose/(POSES-1); g=win(t,q-.20,q-.034,q+.13,.97)
    if not g:return
    c,l,h,b=[color(getattr(k,x)) for x in ('core','light','trim','low')]
    # Signature stamp moves slightly differently with each gesture.
    j=next(i for i,x in enumerate(COSTUMES) if x.id==k.id)
    age=t-q; lock=s((age+.19)/.17); r0=lerp(20,30,lock)+7*s(age/.20)
    r0+=2.2*m.sin(age*17+j*.37)*(1-s(age/.28))
    cx=160+lerp((j%3-1)*19,0,lock);cy=117+lerp((j%4-1.5)*9,0,lock)
    if k.id in ('fighting','electric','steel'):r0-=2*m.sin(16*max(0,age))
    if k.id in ('ghost','flying','fairy'):cy-=7*s(age/.24)
    d=ImageDraw.Draw(dst);a0=j*.27+t*.71
    if k.id in ('fighting','electric','psychic','steel','rock'):sides=4 if k.id in ('psychic','fighting','electric') else 8
    elif k.id in ('bug','dragon','ice'):sides=6
    else:sides=12
    polys=[(round(cx+m.cos(a0+i*TAU/sides)*r0),round(cy+m.sin(a0+i*TAU/sides)*r0)) for i in range(sides)]
    d.polygon(polys,fill=rgba(mix(b,(20,23,31),.65),g*.59),outline=rgba(h,g*.79),width=1)
    for i in range(sides):
        if i%3==(j%3):continue
        a=a0+(i+.06)*TAU/sides;rr=r0+5+6*s(age/.27)
        x,y=cx+rr*m.cos(a),cy+rr*m.sin(a);n=4 if i%2 else 2
        d.line((round(x-m.cos(a)*n),round(y-m.sin(a)*n),round(x+m.cos(a)*2),round(y+m.sin(a)*2)),fill=rgba(l,g*.90),width=1)
    size=lerp(21,45,lock)+3*m.sin(s(age/.24)*m.pi); size*=1-.22*s((t-.74)/.23)
    pin(dst,icon,cx,cy,size,g)


def signature(dst,k,icon,t):
    """Le coup de ponctuation n'a pas la même silhouette ni le même geste par type."""
    hit=k.pose/(POSES-1); p=(t-hit+.073)/.36
    if not 0<p<1:return
    amp=win(p,0,.14,.36,1); z=1-(1-p)**3; cx,cy=160,117
    c,l,h,b=[color(getattr(k,x)) for x in ('core','light','trim','low')]
    d=ImageDraw.Draw(dst); ink=rgba(h,.70*amp); pale=rgba(l,.88*amp); shade=rgba(c,.42*amp)
    def path(seq,fill=ink,w=1):d.line([(round(x),round(y)) for x,y in seq],fill=fill,width=w)
    def poly(seq,fill=shade,stroke=ink):d.polygon([(round(x),round(y)) for x,y in seq],fill=fill,outline=stroke)
    def arc(x,y,rx,ry,a,bb,fill=ink,w=1):d.arc(tuple(round(v) for v in (x-rx,y-ry,x+rx,y+ry)),a,bb,fill=fill,width=w)
    def polar(a,r,ry=1.):return cx+m.cos(a)*r,cy+m.sin(a)*r*ry
    key=k.id
    if key=='normal':
        for i in range(2):
            r=25+z*56-i*9
            arc(cx,cy,r,r*.62,12,155,pale if i==0 else ink)
            arc(cx,cy,r,r*.62,192,335,ink)
    elif key=='fire':
        for i in range(6):
            a=1 if i%2 else -1;x=cx+a*(21+(10+i%3*14)*z);y=cy-12-37*z-i%3*8
            poly([(x-4,y+9),(x-5,y+4),(x+2*a,y-9),(x+3,y),(x+4,y+5)],shade,ink)
            path([(x-2,y+6),(x+2*a,y-2)],pale)
    elif key=='water':
        r=29+z*74
        arc(cx,cy+17,r,15+12*z,2,176,pale,2);arc(cx,cy+21,r*.77,13,7,161,ink)
        arc(cx,cy-14,r*.81,18,188,345,ink);arc(cx,cy-16,r*.73,15,208,336,shade)
    elif key=='grass':
        for side in (-1,1):
            seq=[(cx+side*(16+i*z*6),cy+(12+6*p)*m.sin(i*.57+p*2.7)*side) for i in range(13)]
            path(seq,ink,2)
            for j in (6,9,12):
                x,y=seq[j];poly([(x,y),(x+side*3,y-6),(x+side*12,y-9),(x+side*9,y-3)],shade,ink)
    elif key=='electric':
        for side in (-1,1):
            r=21+44*z; y=cy+side*5
            seq=[(cx+side*(20+j*r/5),y+(18 if j%2 else -10)*(-side if j%3==0 else side)) for j in range(5)]
            path(seq,shade,3);path(seq,pale if int(p*25)%3 else ink)
    elif key=='ice':
        for i in range(6):
            a=i*TAU/6+.19;r=22+50*z
            q=[polar(a+ang,r+rr) for ang,rr in ((0,-7),(-.13,2),(0,19),(.13,3))]
            poly(q,shade,ink);path([q[0],q[2]],pale)
    elif key=='fighting':
        for side in (-1,1):
            j=42-18*s(p/.25)+42*s((p-.34)/.66); x=cx+side*j
            poly([(x+side*25,cy-18),(x,cy),(x+side*25,cy+18),(x+side*15,cy),(x+side*28,cy-10)],shade,pale)
    elif key=='poison':
        for i in range(8):
            a=i*TAU/8+.4;x,y=polar(a,17+z*(31+5*(i%3)),.8);y-=24*z
            r=3+i%3*2+2*p;arc(x,y,r,r,0,359,ink,1);arc(x,y,r-1,r-1,200,300,pale)
    elif key=='ground':
        r=17+75*z;yo=cy+23
        pts=[(cx-r+i*r/5,yo+([4,-5,2,-3,6][i%5])) for i in range(11)]
        path(pts,shade,5);path([(x,y-2) for x,y in pts],pale)
        path([(x,y+5) for x,y in pts],ink)
    elif key=='flying':
        r=31+77*z
        arc(cx,cy-7,r,22+9*z,190,335,pale,1);arc(cx,cy+5,r*.84,17,9,160,ink)
        pin(dst,icon,cx+r*.72,cy-21*z,15,.94*amp,-18);pin(dst,icon,cx-r*.70,cy+16*z,12,.77*amp,29)
    elif key=='psychic':
        for i in range(3):
            r=31+z*37+i*7
            q=[(cx+i*2-r,cy),(cx,cy-r*.70+i*2),(cx+r-i*2,cy),(cx,cy+r*.70-i*2)]
            poly(q,(0,0,0,0),pale if i==1 else ink)
    elif key=='bug':
        for i in range(6):
            x,y=polar(TAU*i/6,28+z*32,.88);r=7+(i%2)
            poly([(x+m.cos(a*TAU/6)*r,y+m.sin(a*TAU/6)*r) for a in range(6)],shade,ink)
            path([(x-4,y),(x,y-3),(x+4,y)],pale)
    elif key=='rock':
        for side in (-1,1):
            for j in range(3):
                x=cx+side*(28+(45+8*j)*z);y=cy-15+j*13-11*m.sin(p*m.pi)+12*p*p
                pin(dst,icon,x,y,19-j*4,amp*.82,-side*(4+j*16)*p)
    elif key=='ghost':
        for i in range(4):
            a=TAU*i/4+z*.45;x,y=polar(a,32+37*z,.76)
            pin(dst,icon,x,y-16*z,17-.4*i,amp*.57,10-19*i)
    elif key=='dragon':
        r=33+z*45
        arc(cx-3,cy-2,r,r*.58,184,338,pale,2);arc(cx+7,cy+3,r*.90,r*.61,14,164,ink,2)
        for j in range(4):
            x,y=polar(TAU*j/4+.53+t,r-2,.59)
            poly([(x,y-5),(x+7,y),(x+2,y+4),(x-5,y)],shade,ink)
    elif key=='dark':
        for side in (-1,1):
            x=cx+side*(23+37*z);y=cy+side*7
            arc(x,y,13+9*z,17+9*z,65 if side>0 else 245,215 if side>0 else 399,shade,4)
            arc(x,y,14+9*z,18+9*z,65 if side>0 else 245,215 if side>0 else 399,ink)
    elif key=='steel':
        q=40-19*s(p/.34)+28*s((p-.58)/.42)
        for side in (-1,1):
            x=cx+side*q
            poly([(x+side*21,cy-18),(x,cy-18),(x,cy-10),(x+side*8,cy-10),(x+side*8,cy+10),
                  (x,cy+10),(x,cy+18),(x+side*21,cy+18)],shade,pale)
            path([(x+side*12,cy-13),(x+side*14,cy-13)],pale,2)
            path([(x+side*12,cy+13),(x+side*14,cy+13)],pale,2)
    elif key=='fairy':
        for i in range(13):
            a=TAU*i/13+p*.52;x,y=polar(a,22+z*(42+(i%4)*9),.76);x0,y0=round(x),round(y);r=3+(i%3)
            star=[(x0+m.cos(j*m.pi/5-1.57)*(r if j%2==0 else r*.42),
                   y0+m.sin(j*m.pi/5-1.57)*(r if j%2==0 else r*.42)) for j in range(10)]
            poly(star,pale if i%3==0 else ink,shade)


def animation(k):
    icon=seal(k);result=[];j=next(i for i,x in enumerate(COSTUMES) if x.id==k.id)
    for f in range(POSES):
        t=f/(POSES-1)
        if f in (0,POSES-1):result.append(blank());continue
        dark=mix(color(k.low),(12,18,30),.78)
        cover=Image.new('RGBA',(W,H),rgba(dark,.33*win(t,.04,.34,.70,.98)))
        straps=blank()
        for i,(y,side) in enumerate(zip(k.ys,k.sides)):band(straps,k,t,y,side,i,icon)
        cover.alpha_composite(straps)
        p=blank();particles(p,k,t,4135+j*131,False);cover.alpha_composite(p)
        p=blank();signature(p,k,icon,t);cover.alpha_composite(p)
        p=blank();symbol(p,k,icon,t);cover.alpha_composite(p)
        p=blank();particles(p,k,t,4135+j*131,True);cover.alpha_composite(p)
        result.append(cover)
    return result


def bank(frames,p):
    grid_h=m.ceil(len(frames)/COLS)
    sheet=Image.new('RGBA',(COLS*W,grid_h*H))
    for i,f in enumerate(frames):sheet.paste(f,(i%COLS*W,i//COLS*H))
    a=np.array(sheet);a[...,:3]=((a[...,:3].astype('uint16')*a[...,3:4]+127)//255).astype('uint8')
    dst=io.BytesIO();Image.fromarray(a).save(dst,format='PNG',compress_level=5)
    b=dst.getvalue()
    p.write_bytes(struct.pack('<q',len(b))+b+struct.pack('<4i',W,H,0,len(frames)))
    return sheet


def score(k,path):
    """SFX par type : bruit filtré et partiels accordés, deux accents stéréo."""
    n=COSTUMES.index(k); sr=44100; t=np.arange(round(sr*DURATION))/sr
    rng=np.random.default_rng(5238+n*193); noise=rng.normal(0,1,len(t))
    def bp(a,b):
        q=sosfilt(butter(2,(a,b),fs=sr,btype='bandpass',output='sos'),noise)
        return q/max(1e-7,np.std(q))
    def env(at,up,down):
        v=t-at; return np.where(v>=0,(1-np.exp(-np.maximum(v,0)/up))*np.exp(-np.maximum(v,0)/down),0)
    h=bp(490+17*n,2800+90*n); l=bp(78+16*n,400+24*n)
    q=np.clip((t-.13)/.8,0,1)
    pitch=k.f0*(k.f1/k.f0)**(q+.058*np.sin(TAU*t*(1.35+n*.13)))
    ph=TAU*np.cumsum(pitch)/sr
    t_hit=k.pose*TICKS/60
    airy=.25*h*np.sin(np.pi*np.clip(t/.96,0,1))**2
    low=l*.17*env(.10,.08,.4)
    sig=airy+low+(np.sin(ph)+.19*np.sin(ph*1.504+n))*.113*env(.11,.16,.36)
    if k.id in ('fire','electric','rock','ground','fighting','steel'):
        sig+=l*.44*env(t_hit,.007,.092)
        for i in range(9 if k.id=='electric' else 5):sig+=h*.12*env(.32+i*.068,.002,.034+(.015 if k.id=='fire' else 0))
    elif k.id in ('poison','water','ghost','dark'):
        sig+=.21*np.sin(ph*.48+1.1*np.sin(TAU*(5+n*.3)*t))*env(.22,.1,.44)
        sig+=l*.12*env(t_hit,.025,.17)
    else:
        sig+=airy*.24+np.sin(ph*2)*(env(.44,.04,.20))*.10
    for i,r in enumerate(k.pulse):
        start=t_hit+.062*i; delta=np.maximum(t-start,0)
        tone=np.sin(TAU*(k.f1*r*delta-.027*k.f1*delta**2)+.76*np.sin(TAU*k.f1*.57*delta)*np.exp(-delta/.18))
        sig+=tone*env(start,.005,.12 if k.id in ('electric','fighting','rock') else .18)*(.36/(1+i*.35))
    fadeout=np.clip((DURATION-.006-t)/.14,0,1)**1.6
    fadein=np.clip(t/.043,0,1)**1.4
    pan=np.sin(TAU*(.69+.033*n)*t+(.6*n))*.24
    stereo=np.column_stack((sig*(1+pan),sig*(1-pan)))*(fadeout*fadein)[:,None]
    stereo*=.54/max(.001,np.max(np.abs(stereo)))
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','s16le','-ar',str(sr),'-ac','2','-i','-',
                    '-c:a','libvorbis','-q:a','5','-metadata',f'title=Kingambit : {k.titre}',str(path)],
                   input=np.rint(stereo*32767).astype('<i2').tobytes(),check=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--reviews',action='store_true');ap.add_argument('--type',choices=[x.id for x in COSTUMES],nargs='+');a=ap.parse_args()
    root=a.out; b=root/'Content/BG'; v=root/'Content/Sound/Battle';r=root/'Planches'
    for p in (b,v,r):p.mkdir(parents=True,exist_ok=True)
    index=[]
    for k in COSTUMES:
        if a.type and k.id not in a.type:continue
        frames=animation(k); assert len(frames)==POSES and not frames[0].getbbox() and not frames[-1].getbbox()
        bg=b/(NATIVE+k.id+'.dir');snd=v/(NATIVE+k.id+'.ogg');sheet=bank(frames,bg);score(k,snd)
        if a.reviews:sheet.save(r/(k.id+'.png'),compress_level=5)
        index.append(dict(id=k.id,type=k.type,boss=k.boss,signature=k.titre,motif=k.motif,accent=k.trim,
                          pic=k.pose,largeur=W,hauteur=H,poses=POSES,ticks_pose=TICKS,atlas=bg.name,
                          son=snd.name,sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in (bg,snd)}))
        print(k.type, k.titre, bg.stat().st_size, 'o +', snd.stat().st_size, 'o', flush=True)
    (root/'Index-Prebatailles.json').write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n')


if __name__=='__main__':main()
