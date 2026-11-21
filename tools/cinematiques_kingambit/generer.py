#!/usr/bin/env python3
"""Sources d'effets Kingambit : éclairage à 1× et serrurerie assortie aux 18 trappes.

Les cartes restent inchangées. Les BG sont prémultipliés pour FNA ; les deux
plans de trappe réutilisent les pixels Sol/Rebord d'origine après ouverture.
"""
import argparse
import hashlib
import io
import json
import math
import re
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BOSS_FRAMES, BOSS_TICK = 16, 6
TRAP_FRAMES, TRAP_TICK = 24, 4
BW, BH = 384, 288
X, Y = np.meshgrid(np.arange(BW) - 12, np.arange(BH) - 12)
POINTS = ((180, 92), (132, 116), (228, 116))

def hex_rgb(text):
    return tuple(bytes.fromhex(text.removeprefix('#')))

def ease(x):
    x = max(0, min(1, x))
    return x*x*(3-2*x)

def ellipse(d, x, y, rx, ry, color, width=1):
    d.ellipse((x-rx,y-ry,x+rx,y+ry), outline=color, width=width)

def poly_points(x,y,n,rx,ry,phase=0):
    return [(round(x+rx*math.cos(phase+i*math.tau/n)),round(y+ry*math.sin(phase+i*math.tau/n))) for i in range(n)]

def etoile(d,x,y,r,c):
    d.polygon([(x-r,y),(x-1,y-1),(x,y-r),(x+1,y-1),(x+r,y),(x+1,y+1),(x,y+r),(x-1,y+1)],fill=c)

def signe(im, x, y, style, f, strength, col, side):
    """Chiffres de lumière spécifiques : mouvement dessiné, pas simple recoloration."""
    a = int(203*strength)
    if a < 4: return
    x += 12; y += 12
    d = ImageDraw.Draw(im)
    hi = (*col,a); lo = (*col,a//2); coeur=(*(min(255,c+48) for c in col),a)
    t = f*.51+side*.8
    p = min(9, f)
    if style == 'echo':
        for i in range(3):
            r=4+((p*2+i*7)%20);ellipse(d,x,y,r,max(2,r//3),(*col,a*(23-r)//26))
    elif style == 'braise':
        for i in range(5):
            u=x+(i-2)*5+int(math.sin(t+i)*3);v=y-(f*3+i*7)%20
            d.polygon([(u-2,v),(u,v-5),(u+3,v+1),(u,v+4)],fill=hi if i%2 else coeur)
        d.line([(x-15,y+5),(x+15,y+5)],fill=lo,width=2)
    elif style == 'onde':
        for i in range(3):
            r=6+((p*3+i*8)%25);ellipse(d,x,y,r,r//4+1,(*col,a*(31-r)//32))
        d.line([(x+i,y-5+round(math.sin(i*.23+t)*3)) for i in range(-20,21)],fill=hi)
    elif style == 'vrille':
        pts=[(x+i,y+round(math.sin(i*.22+t)*6)) for i in range(-20,max(-18,min(22,-16+f*6)))]
        if len(pts)>1: d.line(pts,fill=hi,width=2)
        for i,(u,v) in enumerate(pts[4::8]):d.line([(u,v),(u+3,v+(-6 if i%2 else 5))],fill=coeur)
    elif style == 'arc':
        d.line([(x-20,y+7),(x-8,y-5),(x-3,y+2),(x+7,y-12),(x+11,y-3),(x+20,y-10)],fill=hi,width=2)
        for u,v in ((-20,7),(8,-12),(20,-10)):etoile(d,x+u,y+v,2+f%3,coeur)
    elif style == 'cristal':
        for i in range(6):
            u,v=poly_points(x,y,6,12+f,8+f//2)[i];d.line([(x,y),(u,v)],fill=hi)
            d.line([(u,v),(round((u+x)*.5)-2,round((v+y)*.5)-4)],fill=lo)
        d.point((x,y),fill=coeur)
    elif style == 'impact':
        q=min(21,5+2*f); pts=poly_points(x,y,8,q,max(3,q//3),math.pi/8)
        d.line(pts+pts[:1],fill=hi,width=2)
        for u in (-8,0,8):d.line([(x+u,y-4),(x+u+int(u/2),y-9)],fill=lo)
    elif style == 'spore':
        for i in range(7):
            u=x+((i*11+int(4*math.sin(t+i)))%36)-18;v=y-(i*5+f*2)%22
            ellipse(d,u,v,2+i%3,2+i%3,hi if i%2 else lo)
    elif style == 'sable':
        for i in range(12):
            u=x+(((i*13+5*f)%43)-21);v=y+((i*7+2*f)%13)-6
            d.line((u,v,u+2+i%3,v),fill=(hi if i%3 else lo))
        d.line((x-18,y+5,x+18,y+5),fill=lo)
    elif style == 'plume':
        for i in range(3):
            v=y-5-i*5+round(math.sin(t+i)*3)
            d.line([(x+b,v+round((b*b)/96)+round(math.sin(b*.18+t)*2)) for b in range(-22,21)],fill=hi if i==1 else lo,width=1)
    elif style == 'prisme':
        for i in (-1,1):
            u=x+i*(4+f);q=9+side%3; pts=[(u,y-q),(u+6,y),(u,y+q),(u-6,y)]
            d.line(pts+pts[:1],fill=hi,width=2);d.line((u,y-q,u,y+q),fill=lo)
    elif style == 'alveole':
        for i,(u,v) in enumerate(((0,0),(-12,5),(12,5),(0,-12))):
            if f+1>=i:
                pts=poly_points(x+u,y+v,6,7,5,math.pi/6);d.line(pts+pts[:1],fill=hi if i==f%4 else lo)
    elif style == 'faille':
        d.line([(x-20,y-5),(x-11,y-3),(x-5,y+4),(x+4,y-2),(x+10,y+4),(x+21,y)],fill=hi,width=2)
        d.line([(x-5,y+4),(x-3,y+10),(x+5,y+12)],fill=lo)
        for i in range(4):d.point((x-10+i*7,y-f-i),fill=coeur)
    elif style == 'lanterne':
        for i in (-1,1):
            u=x+i*8;v=y-7+round(math.sin(t+i)*3)
            d.polygon([(u,v-6),(u+4,v+1),(u,v+6),(u-4,v+1)],fill=lo)
            d.line((u,v-2,u,v+5),fill=coeur,width=2);ellipse(d,u,y+5,6,2,lo)
    elif style == 'spirale':
        pts=[(x+round(j*.55*math.cos(t+j*.26)),y+round(j*.23*math.sin(t+j*.26))) for j in range(1,34)]
        d.line(pts,fill=hi,width=2); etoile(d, *pts[-1], 3, coeur)
    elif style == 'paupiere':
        for i in (-1,1):
            u=x+i*10;r=3+f%5
            d.line([(u-6,y),(u,y-r),(u+6,y),(u,y+r),(u-6,y)],fill=hi)
            d.line((u,y-r+1,u,y+r-1),fill=coeur)
    elif style == 'pignon':
        pts=poly_points(x,y,12,14,8,t/4);d.line(pts+pts[:1],fill=hi,width=2)
        for i,(u,v) in enumerate(pts):
            if i%2==0:d.line((u,v,u+round((u-x)/4),v+round((v-y)/4)),fill=coeur,width=2)
        ellipse(d,x,y,4,3,lo)
    elif style == 'etoile':
        for i,(u,v) in enumerate(poly_points(x,y,5,19,8,t/2)):
            etoile(d,u,v,2+(i+f)%4,coeur if i%2 else hi)


def faisceaux(plan):
    col=hex_rgb(plan['teinte']); col_ref=tuple((i*3+13)//4 for i in col)
    # La caméra reste dans les bornes de la salle 15×11 ; le voile couvre tous ses cadrages.
    mask=np.clip(19*((X-180)**2/185**2+(Y-128)**2/135**2),0,40)
    hero=np.exp(-(((X-180)/42)**2+((Y-195)/36)**2))
    for f in range(BOSS_FRAMES):
        release=ease((f-11)/4)
        alpha= (235 + mask - hero * (28+min(4,f)*10))*(1-release)
        light=Image.new('RGBA',(BW,BH))
        for j,spot in enumerate(plan['ordre']):
            k=f-(3+3*j)
            if k<0:continue
            x,y=POINTS[spot-1]; p=ease((k+1)/3); falloff=np.exp(-(((X-x)/(17+min(12,k)))**2+((Y-y)/(14+min(7,k)))**2))
            alpha-=falloff*195*p*(1-release)
            signe(light,x,y,plan['signe'],k,p*(1-release),col,spot)
            if k<4:
                dl=ImageDraw.Draw(light);dl.point((x+12,y+12+k),fill=(*col_ref,int(155*p*(1-release))))
        layer=np.zeros((BH,BW,4),dtype=np.uint8);layer[:,:,:3]=[9,8,17];layer[:,:,3]=np.clip(alpha,0,255).astype(np.uint8)
        yield Image.alpha_composite(Image.fromarray(layer,'RGBA'),light)


def melange(a,b,t): return tuple(round(u*(1-t)+v*t) for u,v in zip(a[:3],b[:3]))+(255,)

def trappe(base,rebord,plan,rupture):
    old,lip=rupture(base,rebord)
    colours=sorted((c for _,c in rebord.getcolors(96*80) if c[3]),key=lambda c:sum(c[:3]))
    accent=hex_rgb(plan['teinte']); mid=colours[len(colours)//2]; top=melange(mid,accent,.58); outline=melange(mid,(15,17,23),.73)
    shade=melange(mid,(19,18,32),.48); gleam=melange(mid,accent,.84); rivet=melange(mid,accent,.35)
    left,_,right,_=base.getbbox(); left+=5;right-=6
    for f in range(TRAP_FRAMES):
        index=min(9,max(0,f-7))
        a=old[index].copy() if f>=8 else Image.new('RGBA',(96,80))
        b=lip[index].copy() if f>=8 else Image.new('RGBA',(96,80))
        racks=ImageDraw.Draw(a); handle=ImageDraw.Draw(b)
        # Courses de denture : deux pênes en sens opposés, puis retrait des feuilles.
        for k,(x,sgn) in enumerate(((left,1),(right,-1))):
            t= max(0,min(1,(f-(3+k*2))/4)); u=round(x+(15-11*ease(t))*sgn)
            if f<=20:
                racks.rounded_rectangle((x-5,30,x+5,49),radius=2,fill=shade,outline=outline)
                racks.line((x-2,32,x-2,46),fill=top)
                for y in range(34,46,4):racks.line((x-4,y,x+4,y),fill=rivet)
                racks.line((x,40,u,40),fill=outline,width=5)
                racks.line((x,39,u,39),fill=top,width=2)
                handle.rectangle((x-3,49,x+3,53),fill=shade,outline=outline)
                handle.point((x,50),fill=gleam if f>=1+2*k else rivet)
            if f<13:
                shift=round(ease((f-4)/8)*23)*sgn
                inner=48-shift; outer=48-sgn*23-shift
                pts=[(outer,35),(outer+3*sgn,30),(inner-sgn,30),(inner-sgn,49),(outer+3*sgn,49),(outer,46)]
                racks.polygon(pts,fill=shade,outline=outline)
                racks.line([(outer+3*sgn,31),(inner-2*sgn,31)],fill=top)
                for y in (34,46):
                    racks.line((outer+4*sgn,y,inner-3*sgn,y),fill=rivet)
                # Rappel de la matière du biome sur la feuille, sans resampler le pixel.
                for h in range(5):
                    xx=outer+(6+((h*7+k*5)%12))*sgn;yy=35+(h*5)%9
                    racks.point((xx,yy),fill=top if h==f%5 else rivet)
            if f in (4+k*2,5+k*2,9+k):
                for i in range(4):
                    xx=u+sgn*(i*3-3); yy=36-(i%3)*3
                    handle.line((xx,yy,xx+sgn,yy-2),fill=gleam if i%2 else top)
        if f==12:
            for u in (23,73): handle.point((u,53),fill=gleam)
        yield a,b


def sheet(dst,frames,cols):
    frames=list(frames); w,h=frames[0].size;n=len(frames)
    atlas=Image.new('RGBA',(cols*w,math.ceil(n/cols)*h))
    for i,im in enumerate(frames):
        assert im.size==(w,h)
        # BG semi-transparents en alpha prémultiplié ; aucun redimensionnement.
        pixel=Image.frombytes('RGBA',im.size,im.convert('RGBa').tobytes())
        atlas.paste(pixel,(i%cols*w,i//cols*h))
    png=io.BytesIO();atlas.save(png,format='PNG',optimize=True);b=png.getvalue()
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_bytes(struct.pack('<q',len(b))+b+struct.pack('<iiii',w,h,0,n))
    return dict(path=dst.name,width=w,height=h,frames=n,sha256=hashlib.sha256(dst.read_bytes()).hexdigest())


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base',type=Path,required=True,help='Racine source Destiny, illustrations originales')
    ap.add_argument('--out',type=Path,required=True,help='Racine isolée du lot')
    a=ap.parse_args();sys.path.insert(0,str(a.base/'tools'))
    from dessiner_trappe_kingambit import rupture
    p=json.loads((HERE/'Plans.json').read_text(encoding='utf-8')); assert len(p)==18
    types=re.findall(r'\{"(\w+)",', (a.base/'game/Data/Script/destiny/dojo_kingambit_types.lua').read_text());assert list(p)==types
    art=a.base/'art/dojo_dedales_trappes'; banks=[]; lua=['-- Généré par tools/cinematiques_kingambit/generer.py.', 'return {'];
    for k,plan in p.items():
        assert sorted(plan['ordre'])==[1,2,3] and len(plan['sons'])==3
        root=a.out/'game/Content';banks.append(sheet(root/'BG'/f'Kingambit_Signaux_{k}.dir',faisceaux(plan),4))
        base=Image.open(art/f'{k}_sol.png').convert('RGBA'); lip=Image.open(art/f'{k}_rebord.png').convert('RGBA')
        plans=list(trappe(base,lip,plan,rupture))
        for f,name in enumerate(('Sol','Rebord')):
            banks.append(sheet(root/'Particle'/f'Kingambit_Mecanisme_{k}_{name}.dir',[r[f] for r in plans],6))
        def q(s):return json.dumps(s,ensure_ascii=False)
        lua += [f"  {k} = {{", f"    chef={q(plan['chef'])}, titre={q(plan['titre'])}, noir={q(plan['noir'])}, replique={q(plan['replique'])},",
                '    ordre={'+','.join(map(str,plan['ordre']))+'}, sons={'+','.join(map(q,plan['sons']))+'},','  },']
    lua+=['}','']
    out=a.out/'game/Data/Script/destiny/dojo_kingambit_plans.lua';out.parent.mkdir(parents=True,exist_ok=True);out.write_text('\n'.join(lua),encoding='utf-8')
    doc=a.out/'tools/cinematiques_kingambit/Banques.json';doc.parent.mkdir(parents=True,exist_ok=True);doc.write_text(json.dumps(banks,indent=2)+'\n',encoding='utf-8')
    print(f'{len(banks)} banques à 1× : 18 lumières distinctes, 36 plans de trappe. 18 fiches Lua.')

if __name__=='__main__': main()
