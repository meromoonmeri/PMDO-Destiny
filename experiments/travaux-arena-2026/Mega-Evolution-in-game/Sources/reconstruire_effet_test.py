"""Reconstitution V2 de 04 pour le banc PMDO, d'après la vidéo de référence.
Les cycles sphere/coque/emblème V2 sont d'origine ; les orbites, l'iris et
les étincelles sont redessinés. Les scripts originaux de 04 restent absents.
La banque ne contient pas les sprites Pokémon : le moteur les affiche lui-même.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import math, io, struct
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'Banc-test'; OUT.mkdir(exist_ok=True)
S=128; N=144
atlas=Image.new('RGBA',(S*12,S*12))
cycles={}
for name in ('sphere','break','emblem'):
    im=Image.open(HERE/f'MEGAGEN_V2_{name}.png').convert('RGBA')
    cycles[name]=[im.crop(((i%8)*160,(i//8)*160,(i%8+1)*160,(i//8+1)*160)) for i in range(48)]

def opacity(im, factor):
    a=np.array(im); a[:,:,3]=(a[:,:,3].astype(np.float32)*max(0,min(1,factor))).astype(np.uint8)
    return Image.fromarray(a)

def orbit(draw,f,phase,color,visibility):
    # Orbites elliptiques croisées. Rotation lente, constellations en mouvement.
    angle=phase+.018*f; ca,sa=math.cos(angle),math.sin(angle)
    coords=[]
    for j in range(105):
        v=2*math.pi*j/104
        x=43*math.cos(v); y=13*math.sin(v)
        coords.append((round(64+x*ca-y*sa),round(64+(x*sa+y*ca)*.60)))
    r,g,b=color
    # Segments pour conserver les interruptions visibles dans l'original.
    for j in range(104):
        if ((j+f//3+round(phase*8))%104)<83:
            light=.42+.58*(.5+.5*math.sin(j/11+f*.16+phase))
            draw.line([coords[j],coords[j+1]],fill=(r,g,b,int(190*light*visibility)),width=1)
    idx=int((f*2+phase*11)%104); x,y=coords[idx]
    star=(r,g,b,int(235*visibility));draw.line((x-2,y,x+2,y),fill=star);draw.line((x,y-2,x,y+2),fill=star)

def sparkle(draw,x,y,color,scale=2):
    r,g,b,a=color
    draw.line((x-scale,y,x+scale,y),fill=(r,g,b,a),width=1)
    draw.line((x,y-scale,x,y+scale),fill=(r,g,b,a),width=1)
    draw.point((x,y),fill=(255,255,255,a))

for f in range(N):
    layer=Image.new('RGBA',(S,S))
    if 30 <= f < 88:
        sphere=cycles['sphere'][(f-30)%48].resize((112,112),Image.Resampling.NEAREST)
        a=np.array(sphere).astype(np.float32)
        yy,xx=np.ogrid[:112,:112]; radius=np.sqrt((xx-56)**2+(yy-56)**2)/32
        progress=max(0,min(1,(f-43)/(74-43)))
        r=np.clip((progress*1.55-radius+.22)*3,0,1)[:,:,None]
        blue=a[:,:,:3]*np.array([.16,.22,.40],dtype=np.float32)+np.array([6,11,30],dtype=np.float32)
        a[:,:,:3]=blue*(1-r)+a[:,:,:3]*r
        a[:,:,3]*=min(1,(f-30)/8)
        layer.alpha_composite(Image.fromarray(np.uint8(np.clip(a,0,255))),(8,8))
    if 88 <= f < 131:
        shell=cycles['break'][min(42,f-88)].resize((112,112),Image.Resampling.NEAREST)
        layer.alpha_composite(shell,(8,8))
    if 106 <= f < 143:
        em=cycles['emblem'][(f-106)%48].resize((112,112),Image.Resampling.NEAREST)
        em=opacity(em,min(1,(f-106)/5)*min(1,(143-f)/10))
        layer.alpha_composite(em,(8,-14))
    front=Image.new('RGBA',(S,S)); d=ImageDraw.Draw(front)
    if f<53:
        fade=min(1,f/8)*min(1,(53-f)/7)
        orbit(d,f,.48,(111,215,255),fade);orbit(d,f,2.20,(195,139,236),fade)
    if 37<=f<=51:
        # Iris horizontal pale pendant la phase d'éclipse ; pas de grand éclair vertical.
        envelope=max(0,1-abs(f-44)/8)
        width=round(20*envelope)
        if width:
            d.ellipse((64-width,63,64+width,65),fill=(165,229,255,round(200*envelope)))
            d.line((64-width-6,64,64+width+6,64),fill=(173,232,255,round(130*envelope)))
    if 98<=f<128:
        fade=min(1,(f-98)/4)*max(0,(128-f)/30)
        # Anneaux au sol pendant l'ouverture et éclats latéraux courts.
        for r in (29,37,44):
            d.ellipse((64-r,70-r*.18,64+r,70+r*.18),outline=(123,211,255,int(110*fade)),width=1)
        t=f-98
        for i in range(12):
            side=-1 if i%2==0 else 1
            x=64+side*(12+((i*7+t*1.1)%39));y=66-((i*13+t*.7)%32)
            sparkle(d,round(x),round(y),(138+((i%3)*35),209,255,int(200*fade)),1+i%2)
        if f<107:
            a=int(220*(1-abs(f-102)/6))
            if a>0:
                d.line((30,64,53,64),fill=(191,240,255,a),width=2)
                d.line((75,64,98,64),fill=(191,240,255,a),width=2)
    layer.alpha_composite(front)
    atlas.alpha_composite(layer,((f%12)*S,(f//12)*S))

png=OUT/'Eclipse-Prisme-reconstitution-V2.png'; atlas.save(png)
a=np.array(atlas); alpha=a[:,:,3].astype(np.uint16)
a[:,:,:3]=((a[:,:,:3].astype(np.uint16)*alpha[:,:,None]+127)//255).astype(np.uint8)
buf=io.BytesIO();Image.fromarray(a).save(buf,format='PNG');p=buf.getvalue()
(OUT/'Eclipse_Prism_Test_V2.dir').write_bytes(struct.pack('<q',len(p))+p+struct.pack('<iiii',S,S,0,N))
print('Generated',png, 'and V2 PMDO particle bank:',len(p))
