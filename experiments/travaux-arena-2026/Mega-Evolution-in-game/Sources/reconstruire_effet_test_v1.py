"""Reconstitution expérimentale de la variante 04 pour un banc PMDO.
Ne prétend pas reproduire pixel pour pixel le script source perdu.
Sort une banque `.dir` et un PNG d'édition, sans sprites Pokémon incrustés.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import math, io, struct
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'Banc-test'
OUT.mkdir(exist_ok=True)
S=128; N=144
atlas=Image.new('RGBA',(S*12,S*12))
cycles={}
for name in ('sphere','break','emblem'):
    im=Image.open(HERE/f'MEGAGEN_V2_{name}.png').convert('RGBA')
    cycles[name]=[im.crop(((i%8)*160,(i//8)*160,(i%8+1)*160,(i//8+1)*160)) for i in range(48)]

def dim_alpha(im, factor):
    a=np.array(im); a[:,:,3]=(a[:,:,3].astype(np.float32)*max(0,min(1,factor))).astype(np.uint8)
    return Image.fromarray(a)

def ring(draw, t, phase, col):
    # Points d'une orbite inclinée, avec interruption progressive et petites étoiles.
    ang=phase + t*.115
    pts=[]
    for j in range(75):
        v=2*math.pi*j/74
        x=31*math.cos(v); y=10*math.sin(v)
        ca=math.cos(ang); sa=math.sin(ang)
        pts.append((round(64+x*ca-y*sa),round(64+x*sa*.45+y*ca)))
    draw.line(pts, fill=col, width=1)
    p=pts[int((t*2+phase*11)%74)]; x,y=p
    draw.line((x-2,y,x+2,y),fill=col,width=1);draw.line((x,y-2,x,y+2),fill=col,width=1)

for f in range(N):
    layer=Image.new('RGBA',(S,S)); d=ImageDraw.Draw(layer)
    # Croisement de deux trajectoires, allégées pendant la sphère.
    if f < 53 or 97 <= f < 130:
        fade=min(1,f/8) if f<53 else max(0,1-(f-97)/33)
        ring(d,f,.6,(106,209,255,int(185*fade)))
        ring(d,f,2.4,(192,132,255,int(160*fade)))
    if 30 <= f < 100:
        k=(f-30)%48; sphere=cycles['sphere'][k].resize((112,112),Image.Resampling.NEAREST)
        a=np.array(sphere).astype(np.float32)
        # Révélation de la spirale du centre vers les bords, suivant les timings de 04.
        yy,xx=np.ogrid[:112,:112]; radius=np.sqrt((xx-56)**2+(yy-56)**2)/32
        progress=max(0,min(1,(f-43)/(74-43)))
        r=np.clip((progress*1.55-radius+0.22)*3,0,1)[:,:,None]
        blue=a[:,:,:3]*np.array([.20,.29,.52],dtype=np.float32)+np.array([5,10,26],dtype=np.float32)
        a[:,:,:3]=blue*(1-r)+a[:,:,:3]*r
        a[:,:,3]*=min(1,(f-30)/8)
        sphere=Image.fromarray(np.uint8(np.clip(a,0,255)))
        layer.alpha_composite(sphere,(8,8))
    if 100 <= f < 143:
        shell=cycles['break'][min(42,f-100)].resize((112,112),Image.Resampling.NEAREST)
        layer.alpha_composite(shell,(8,8))
    if 100 <= f < 139:
        em=cycles['emblem'][(f-100)%48].resize((112,112),Image.Resampling.NEAREST)
        # The emblem rises above the breaking shell.
        em=dim_alpha(em,min(1,(f-100)/5)*min(1,(139-f)/12))
        layer.alpha_composite(em,(8,-14))
    atlas.alpha_composite(layer,((f%12)*S,(f//12)*S))

png=OUT/'Eclipse-Prisme-reconstitution.png'; atlas.save(png)
# PMDO's .dir stores PNG premultiplied alpha, followed by tile dimensions and count.
a=np.array(atlas); alpha=a[:,:,3].astype(np.uint16)
a[:,:,:3]=((a[:,:,:3].astype(np.uint16)*alpha[:,:,None]+127)//255).astype(np.uint8)
buf=io.BytesIO(); Image.fromarray(a).save(buf,format='PNG')
p=buf.getvalue(); (OUT/'Eclipse_Prism_Test.dir').write_bytes(struct.pack('<q',len(p))+p+struct.pack('<iiii',S,S,0,N))
print('Generated',png, 'and experimental PMDO particle bank:', len(p))
