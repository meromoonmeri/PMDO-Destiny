#!/usr/bin/env python3
"""18 chorégraphies pixel art à 1×, deux plans sol/air, animées en DirSheets PMDO.

Les motifs sakura, prisme et ombre sont détourés depuis les trois originaux
sur fond magenta. Tous les mouvements et les autres tracés sont peints sur la
grille finale : aucune interpolation de particule ni emprunt à un autre dojo.
"""
import argparse
import io
import math as m
from pathlib import Path
import struct
from PIL import Image, ImageDraw, ImageOps
from dojo_kingambit_troupes import POSES, TROUPES

W,H=112,112
OX,OY=W//2,H//2
ROOT=Path(__file__).resolve().parents[1]
PAL={
    'normal':   ('#4e3e39','#a39177','#ddcda5','#fff0d0'),
    'fire':     ('#63332e','#ce4b32','#ff944f','#ffe9ae'),
    'water':    ('#243951','#347ca4','#71c8dc','#d8fcff'),
    'grass':    ('#263b32','#457747','#89b768','#e0eea0'),
    'electric': ('#664526','#d89d37','#ffe06b','#fff6c8'),
    'ice':      ('#2b506f','#59899f','#9cdef2','#e6fbff'),
    'fighting': ('#583734','#b55a44','#ed916a','#ffdfb6'),
    'poison':   ('#372943','#80557e','#b981c1','#dce3a0'),
    'ground':   ('#574133','#a57146','#dcb170','#f4d99a'),
    'flying':   ('#3b536e','#728fa5','#b7d6e7','#edf7ef'),
    'psychic':  ('#432963','#815498','#c997dd','#ffe5fc'),
    'bug':      ('#384631','#65724b','#a2be69','#e5edab'),
    'rock':     ('#4e4041','#82605b','#b38872','#efd0a0'),
    'ghost':    ('#161322','#272139','#513f65','#a38cbe'),
    'dragon':   ('#332846','#755182','#b789ca','#f7d8f6'),
    'dark':     ('#1e1d2b','#443149','#966594','#f4c9d4'),
    'steel':    ('#2c3946','#5c7182','#a3c7cf','#ecf5ea'),
    'fairy':    ('#8c3f62','#d96e91','#f7b5bf','#fff0dd'),
}


def pt(x,y): return round(OX+x),round(OY+y)


class Plan:
    def __init__(self,pal):
        self.im=Image.new('RGBA',(W,H)); self.d=ImageDraw.Draw(self.im); self.pal=pal
    def poly(self,p,c,b=None):
        self.d.polygon([pt(*x) for x in p],fill=self.pal[c],outline=self.pal[b] if b is not None else None)
    def line(self,p,c,w=1): self.d.line([pt(*x) for x in p],fill=self.pal[c],width=w)
    def ov(self,x,y,rx,ry,c,fill=False):
        if min(rx,ry)>0:
            self.d.ellipse((*pt(x-rx,y-ry),*pt(x+rx,y+ry)),fill=self.pal[c] if fill else None,outline=self.pal[c])
    def arc(self,x,y,rx,ry,a,b,c,w=1):
        if min(rx,ry)>0:
            self.d.arc((*pt(x-rx,y-ry),*pt(x+rx,y+ry)),a,b,fill=self.pal[c],width=w)
    def grain(self,x,y,c=2): self.line(((x,y),(x+1,y)),c)
    def los(self,x,y,w,h,c,b=None): self.poly(((x-w,y),(x,y-h),(x+w,y),(x,y+h)),c,b)
    def etoile(self,x,y,r,c=3):
        self.poly(((x-r,y),(x-1,y-1),(x,y-r),(x+1,y-1),(x+r,y),(x+1,y+1),(x,y+r),(x-1,y+1)),c)
    def motif(self,im,x,y): self.im.alpha_composite(im,(round(OX+x-im.width/2),round(OY+y-im.height/2)))


def etale(f): return min(f,15-f)


def normal(s,a,f,_):
    for i in range(3):
        p=f-i*2
        if 0<p<11:
            s.arc(0,4,4+2*p,2+p,12+28*i,205+28*i,1+(i==0),1)
            s.arc(0,4,5+2*p,2+p,225-10*i,340-10*i,1,1)
    for i in range(5):
        t=f-i
        if 1<=t<=8:
            x=(-1)**i*(4+t*2+i);y=4+(i%3)*2-t
            a.line(((x+(-1)**i*5,y-2),(x,y),(x-2,y)),2 if t<6 else 1)
            if t<5: a.grain(x+2,y-3,3)


def fire(s,a,f,_):
    r=6+min(f,10)*2
    if 0<f<14:
        for i in range(9):
            phi=i*2.39996
            x,y=r*m.cos(phi),5+.44*r*m.sin(phi)
            s.los(x,y,3 if f<9 else 2,2,(1,2,0)[i%3],0)
    for i,dx in enumerate((0,-12,11,18,-19)):
        p=f-i%2
        if not 1<=p<=13: continue
        h=3+etale(p)*(4 if i==0 else 2); y=3+p//5
        w=3+min(3,h//4)
        if i==0 and p>=7: x=dx+int((p-6)*2.8)
        else: x=dx
        a.poly(((x-w,y),(x-w-1,y-h//2),(x+1,y-h),(x+1,y-h//2-2),(x+w,y-h//2),(x+w,y-3),(x+2,y+1)),1,0)
        a.poly(((x-2,y-1),(x-3,y-h//3),(x+1,y-h//2-2),(x+3,y-2)),3 if p<=8 else 2)


def water(s,a,f,_):
    if 0<f<15:
        for i in range(2): s.arc(1,4,5+f*1.7+i*3,2+f*.54+i,12+i*75,325-i*12,2-i)
    for i in range(3):
        t=f-i*2
        if not 1<=t<=10: continue
        x=-22+t*3+i*4; y=5-i*4; r=3+etale(t+1)
        a.poly(((x-9,y+2),(x-5,y-r),(x+2,y-2*r),(x+9,y-2*r),(x+12,y-r),(x+7,y-r-2),(x+2,y-r),(x+3,y-1),(x+11,y+2)),1,0)
        a.arc(x+3,y-r+1,7,r,187,320,3,2)
        if t>4: a.ov(x+14,y-2*t,2+i%2,2,2)


def grass(s,a,f,_):
    for i in range(7):
        t=f-i%3
        if 0<t<15:
            phi=i*2.39996;dx=m.cos(phi);dy=m.sin(phi)*.55;r=min(t,9)*2.5
            s.line(((0,5),(dx*r*.48,5+dy*r*.6),(dx*r,5+dy*r)),1,2)
            s.los(dx*r,5+dy*r,2,1,2)
    for j,side in enumerate((-1,1,-1,1)):
        t=f-j//2*2
        if not 2<=t<=12: continue
        x=side*(5+min(7,t)+j*2+(max(0,t-7)*2));h=min(t,8)*3-j
        a.poly(((x,4),(x-side*4,-h*.48),(x+side*3,-h),(x+side*11,-h-1),(x+side*7,-h*.45)),2,0)
        a.line(((x,4),(x+side*2,-h*.43),(x+side*8,-h+2)),3)


def electric(s,a,f,_):
    if 0<f<13:
        r=8+f*1.4
        for i in range(5):
            phi=i*2*m.pi/5; x=m.cos(phi)*r; y=4+m.sin(phi)*r*.40
            s.line(((x*.4,4+(y-4)*.5),(x*.65+4,y+1),(x,y)),2 if f in (5,6,8) else 1)
    if 2<=f<=10:
        for i in range(3):
            d=(i-1)*(8+2*abs(f-6));x=d+(f+i)%3
            path=((x+4,-41+i*7),(x-5,-29+i*4),(x+2,-24+i*4),(x-7,-9),(x+2,1))
            a.line(path,0,3);a.line(path,3 if 5<=f<=7 else 2,1)
            a.line((path[1],(x-14,-25),(x-9,-22)),2)
    if 5<=f<=13:
        for i in range(4): a.etoile((-1)**i*(7+(f-4)*2+i*3),-3-(i%3)*7+(f-8),2,3 if f<10 else 2)


def ice(s,a,f,_):
    if 0<f<15:
        p=min(f,10);r=3+p*2
        s.poly(((-r,4),(-r*.40,-3),(r*.58,-4),(r,3),(r*.52,10),(-r*.55,9)),0,1)
        s.line(((-r,4),(-r*.2,7),(r*.52,10)),2 if f<12 else 1)
    for j,x in enumerate((-17,-9,0,10,18)):
        t=f-j%3
        if not 1<=t<=12: continue
        h=5+min(t,7)*(3 if x==0 else 2);u=max(0,t-7)
        x+=(-1 if x<0 else 1)*u*2; y=3-u*2;h*=1-u*.12
        a.poly(((x-4,y),(x-3,y-h*.65),(x+1,y-h),(x+5,y-h*.52),(x+5,y+3),(x,y+4)),1,0)
        a.poly(((x+1,y-h),(x+2,y),(x+5,y+3),(x+5,y-h*.52)),2)
        if t<8: a.line(((x+1,y-h+2),(x-2,y-h*.57),(x-2,y-2)),3)
    if 7<=f<14:
        for i in range(4): a.los((-1)**i*(10+i+f*1.4),-8-f+i*6,2,3,3 if i%2 else 2,1)


def fighting(s,a,f,_):
    for delay in (6,9):
        t=f-delay
        if 0<=t<=6:
            r=7+3*t;s.arc(0,3,r,3+t,0,359,1,2);s.arc(0,3,r-2,2+t,30,210,2)
    for i in range(8):
        if 3<=f<=12:
            theta=i*m.pi/4; t=f-3; x=m.cos(theta);y=m.sin(theta)*.62
            l=2+3*t
            a.line(((x*l,y*l-4),(x*(l+8),y*(l+8)-4)),0,3 if f<9 else 1)
            a.line(((x*(l+2),y*(l+2)-4),(x*(l+7),y*(l+7)-4)),2)
    if 5<=f<=8: a.etoile(0,3,5+etale(f)//2)


def poison(s,a,f,_):
    if 0<f<15:
        for i in range(4): s.ov((i-1.5)*min(f,8)*1.3,4+i%2*3,4+etale(f),2+etale(f)//2,i%2,True)
    for i in range(8):
        t=f-i%4
        if not 1<=t<=11: continue
        x=(i-3.5)*7+m.sin(t*.75+i)*4;y=5-t*(2+i%3*.6)
        r=min(t,4)+i%2
        if t<8 or i%2: a.ov(x,y,r,r,1 if t>=7 else 0,True)
        a.arc(x,y,r,r,165,300,2)
        if t==7 or t==8: a.etoile(x,y,3,3)


def ground(s,a,f,_):
    if 0<f<=14:
        t=min(f,10)
        for d in (-1,1):
            s.line(((0,0),(8*d,-2),(15*d,2),(19*d,1),(d*(19+t),5)),0,2)
            s.line(((7*d,2),(11*d,5),(15*d,4),(20*d,8)),1)
            s.arc(d*3,5,7+t*2,4+t*.35,15 if d==1 else 195,167 if d==1 else 345,2)
    for i in range(5):
        t=f-i%3
        if not 1<=t<=12: continue
        d=(-1)**i;x=d*(t*1.9+i*2);y=7-t*2+i%2*4
        a.poly(((x-d*7,y+1),(x-d*2,y-4),(x+d*2,y-5),(x+d*7,y-1),(x+d*4,y+3)),1,0)
        a.line(((x-d*3,y),(x,y-2),(x+d*4,y-2)),3 if t<7 else 2)
        a.grain(x+d*7,y-3,2)


def flying(s,a,f,_):
    if 1<=f<=12:
        r=4+f*2;s.arc(0,5,r,3+f*.48,34,324,2,1);s.arc(0,5,r-2,2+f*.5,90,270,1)
    for i in range(6):
        t=f-i%3
        if not 1<=t<=11: continue
        d=(-1)**i;x=d*(6+t*2+i);y=-36+t*3-i*2
        a.line(((x-d*12,y-9),(x-d*4,y-4),(x,y)),1,2)
        a.poly(((x-d*4,y-2),(x+d*3,y-6),(x+d*9,y-6),(x+d*6,y-2),(x,y+1)),3 if i%2 else 2,1)
        a.line(((x-d*4,y),(x+d*7,y-5)),2)


def psychic(s,a,f,mot):
    if 1<=f<=14:
        t=min(f,15-f); r=4+t*2.8
        for j in range(6):
            pts=[(m.cos((j+k)*m.pi/3)*r,4+m.sin((j+k)*m.pi/3)*r*.5) for k in (0,1)]
            s.line(pts,3 if f in (6,7) else 1+j%2,1)
    if 1<=f<=10:
        h=6+min(f,6)*4; r=3+3*abs(f-6)
        for d in (-1,1):
            a.poly(((0,6),(d*r,1),(d*r,-h*.67),(0,-h)),1 if f<6 else 2,0)
            a.line(((0,-h),(d*(r-2),-h*.61),(d*(r-2),-5)),3 if 5<=f<=7 else 2)
        if f in (5,6,7): a.etoile(0,-10,5,3)
    for i in range(3):
        t=f-i
        if 2<=t<12:
            x=(-1)**i*(10+abs(6-t)*3+i*3);y=-8-t*1.9+i*4
            a.motif(mot['prisme_petit' if i else 'prisme'],x,y)


def bug(s,a,f,_):
    if 0<f<14:
        x=min(f*2,21)
        s.poly(((-x,6),(-x*.48,-2),(x*.48,-2),(x,6),(x*.49,12),(-x*.48,12)),1,0)
        s.line(((-x,6),(-x*.4,7),(x*.49,12)),2)
    if 1<=f<=12:
        for side in (-1,1):
            d=max(0,f-6)*3*side;r=min(14,5+f);h=min(30,6+f*4); y=-max(0,f-8)*2
            a.poly(((d,y+4),(d+side*r,y-5),(d+side*r,y-h*.66),(d+side*r*.45,y-h),(d,y-h+3)),2,0)
            a.line(((d+side,y-h+4),(d+side*3,y-h*.45),(d+side,y-2)),3)
            a.line(((d+side*4,y-h*.5),(d+side*9,y-h*.67),(d+side*r,y-h*.66)),1)
    if 6<=f<=13:
        for i in range(4): a.los((-1)**i*(11+2*(f-6)+2*i),-10+(f-7)*2+i%2*4,2,3,3,1)


def rock(s,a,f,_):
    if 1<=f<=13:
        for d in (-1,1):
            r=min(24,4+2*f)
            s.line(((0,2),(d*r*.32,3),(d*r*.62,9),(d*r,10),(d*(r+4),6)),0,2)
            s.line(((0,3),(d*r*.32,4),(d*r*.62,10),(d*r,11)),2)
    for i,d in enumerate((-1,1)):
        t=f-i
        if not 1<=t<=13: continue
        x=d*(5+max(0,t-7)*4);h=min(t*5,32);y=5-(max(0,t-7)*2)
        a.poly(((x,y),(x-d*3,y-h*.40),(x+d*6,y-h),(x+d*16,y-h*.85),(x+d*19,y-4),(x+d*9,y+2)),1,0)
        a.poly(((x+d*6,y-h),(x+d*10,y-h*.40),(x+d*19,y-4),(x+d*16,y-h*.85)),2)
        a.line(((x+d*6,y-h+1),(x+d*16,y-h*.85)),3)
    if 7<=f<15:
        for i in range(4): a.los((-1)**i*(9+f+i*3),-6+i*5-(f-8)**2*.3,3,2,1+i%2,0)


def ghost(s,a,f,mot):
    if 0<f<15:
        r=3+etale(f)*3.7
        s.poly(((-r,4),(-r*.8,-6),(-r*.35,-9),(r*.3,-8),(r*.62,-4),(r,2),(r*.77,9),(r*.25,12),(-r*.55,10)),0)
        s.arc(0,3,r*.89,r*.36,46,165,2,2)
        s.arc(0,-4,r*.64,r*.28,200,345,1)
    for i in range(5):
        t=f-i%3
        if i==0 and 2<=t<=9: a.motif(mot['ombre'],0,-t*2)
        if 1<=t<=12 and i>0:
            x=(-1)**i*(i*3+t*1.65);y=7-t*2.8+i%2*6
            a.motif(mot['ombre_petitemir' if i%2 else 'ombre_petite'],x,y)
            if 3<=t<=9: a.grain(x+2,y-5,2)
    if 4<=f<=11:
        a.arc(0,5,12+max(0,f-6)*3,5,21,157,0,3)
        a.arc(0,6,14+max(0,f-6)*2,5,26,151,2)


def dragon(s,a,f,_):
    if 0<f<15:
        for i in range(8):
            p=i*m.pi/4+f*.3;r=4+etale(f)*3
            s.los(m.cos(p)*r,5+m.sin(p)*r*.45,3,2,1+i%2,0)
    for i in range(12):
        t=f-i*.38
        if not 1<t<11: continue
        phi=t*.72+i*.36;x=m.sin(phi)*(10+t*1.5);y=5-t*3+i%2
        a.los(x,y,4 if i<3 else 3,3 if i<3 else 2,2 if i%2 else 1,0)
        if i%3==0: a.grain(x,y-1,3)
    if 4<=f<=9:
        x=m.sin(f*.72)*(10+f*1.5);y=5-f*3
        a.poly(((x-6,y),(x-2,y-6),(x+2,y-4),(x+4,y-8),(x+7,y-2),(x+8,y+2),(x+1,y+4)),2,0)
        a.grain(x+3,y-1,3)


def dark(s,a,f,_):
    if 1<=f<=13:
        for d in (-1,1):
            w=4+2*etale(f);s.poly(((d*w*1.6,4),(0,-5),(-d*w,1),(d*w,11)),0)
            s.line(((d*w*1.5,4),(d*w,8),(0,9)),1)
    for i,d in enumerate((-1,1)):
        t=f-i
        if not 1<=t<=11: continue
        x=d*(-6+t*3.2); y=-17+(t-5)*2; r=15+etale(t)
        a.poly(((x-d*r,y+2),(x-d*4,y-7),(x+d*9,y-10),(x+d*r,y-10),(x+d*6,y-3),(x-d*5,y+4),(x-d*r,y+7)),0)
        a.line(((x-d*r,y+7),(x-d*3,y+4),(x+d*7,y-3),(x+d*r,y-10)),2 if 5<=t<=8 else 1)
        if 5<=t<=8: a.grain(x+d*6,y-3,3)


def steel(s,a,f,_):
    if 0<f<=14:
        x=5+min(f,10)*2;s.poly(((-x,1),(-x+8,-6),(x-9,-6),(x,1),(x-7,10),(-x+6,10)),0,1)
        for j in range(4): s.line((((j-1.5)*x/3-3,8),((j-1.5)*x/3,4)),2)
    for i,d in enumerate((-1,1)):
        t=f-i
        if not 1<=t<=12: continue
        x=d*(17-min(t,7)*2+max(0,t-7)*3);h=min(25,6+t*3);w=9
        a.poly(((x,-h),(x+d*w,-h-4),(x+d*w,0),(x,6),(x-d*2,3),(x-d*2,-h+3)),1,0)
        a.line(((x,-h+1),(x+d*w,-h-3)),3);a.line(((x,5),(x+d*w,-1)),2,2)
        for yy in (-h//2,-h//2+4,-h//2+8): a.line(((x+d*2,yy),(x+d*7,yy-2)),0)
    if 7<=f<14:
        for i in range(6): a.etoile((-1)**i*(6+i*2+(f-7)*3),-6+i%3*6-(f-8)*1.6,2+i%2,3 if f<10 else 2)


def fairy(s,a,f,mot):
    for i in range(8):
        t=f-i//2
        if 0<t<14:
            theta=i*2.39996; r=min(t,10)*2.15
            s.etoile(r*m.cos(theta),6+r*.5*m.sin(theta),2 if t>=6 else 1,2 if i%2 else 1)
    for i in range(12):
        t=f-(i%5)*1.2
        if not -.6<=t<10.8: continue
        x=(i%6-2.5)*8 + m.sin(i*.9+t*.57)*6 + (t-4)*.7
        y=-38+(i//6)*9+t*(3.6+(i%3)*.2)
        use=('petale_petit','petale-mir','petale-cerisier')[(i+int(t)//3)%3]
        a.motif(mot[use],x,y)
    if 9<=f<=13:
        for i in range(4): a.etoile((-1)**i*(12+(f-9)*3+i*2),-12+i*4+f,2,3)


FX=dict(normal=normal,fire=fire,water=water,grass=grass,electric=electric,ice=ice,fighting=fighting,
        poison=poison,ground=ground,flying=flying,psychic=psychic,bug=bug,rock=rock,ghost=ghost,
        dragon=dragon,dark=dark,steel=steel,fairy=fairy)


def depart(f,im):
    a=Plan(PAL['psychic'])
    if f!=5:
        r=3+f*3; h=9+f*4
        a.line(((-r,-5),(-r*.48,-h),(r*.48,-h),(r,-5),(0,7),(-r,-5)),1 if f>2 else 3,1)
        a.line(((0,7),(0,-h-2)),2,2 if f==2 else 1)
        if f<3: a.motif(im,0,-8-f*3)
    return a.im


def motifs(folder):
    im={n:Image.open(folder/f'{n}.png').convert('RGBA') for n in ('ombre','prisme','petale-cerisier')}
    im.update(petale_petit=im['petale-cerisier'].resize((6,6),Image.Resampling.NEAREST),
              prisme_petit=im['prisme'].resize((7,10),Image.Resampling.NEAREST),
              ombre_petite=im['ombre'].resize((10,15),Image.Resampling.NEAREST))
    im['petale-mir']=ImageOps.mirror(im['petale-cerisier']).resize((9,9),Image.Resampling.NEAREST)
    im['ombre_petitemir']=ImageOps.mirror(im['ombre_petite'])
    return im


def frames(typ,im):
    sol,air=[],[]
    for f in range(POSES):
        plans=s,a=Plan(PAL[typ]),Plan(PAL[typ])
        if f<POSES-1: FX[typ](s,a,f,im)
        for p,out in zip(plans,(sol,air)):
            assert set(p.im.getchannel('A').tobytes()) <= {0,255}
            bbox=p.im.getbbox()
            assert not bbox or (0<bbox[0]<bbox[2]<W and 0<bbox[1]<bbox[3]<H), (typ,f,bbox)
            out.append(p.im)
    return sol,air


def dirsheet(p,poses):
    n=len(poses);cols=4 if n>=8 else 3
    a=Image.new('RGBA',(W*cols,H*((n+cols-1)//cols)))
    for i,im in enumerate(poses): a.paste(im,(i%cols*W,i//cols*H))
    f=io.BytesIO();a.save(f,format='PNG',optimize=True);png=f.getvalue()
    with p.open('xb') as w:
        w.write(struct.pack('<q',len(png))+png+struct.pack('<iiii',W,H,0,n))
    return a


def run(out,art,export=None):
    out.mkdir(exist_ok=True,parents=True)
    if export: export.mkdir(exist_ok=True,parents=True)
    im=motifs(art)
    for typ in TROUPES:
        for name,poses in zip(('Sol','Air'),frames(typ,im)):
            a=dirsheet(out/f'Kingambit_Entree_{typ}_{name}.dir',poses)
            if export: a.save(export/f'{typ}_{name}.png',optimize=True)
    a=dirsheet(out/'Kingambit_Entree_psychic_Depart.dir',[depart(f,im['prisme']) for f in range(6)])
    if export: a.save(export/'psychic_Depart.png',optimize=True)
    print('18 apparitions sol/air + le départ visible Psy, 37 DirSheets, 582 poses natives.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('out',type=Path)
    p.add_argument('--art',type=Path,default=ROOT/'art/dojo_kingambit_troupes')
    p.add_argument('--export',type=Path)
    a=p.parse_args();run(a.out,a.art,a.export)
