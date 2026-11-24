#!/usr/bin/env python3
"""Progressive DS-style reveal: inked parchment clouds, small water cycles, no lettering."""
from pathlib import Path
from functools import lru_cache
import subprocess, json, math
import numpy as np
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parents[1];C=ROOT/'Calques';W=Path.home()/'.cache/atlas-monde-destiny';W.mkdir(exist_ok=True)
M=json.loads((ROOT/'Reperes-separes.json').read_text());SIZE=tuple(M['carte_px']);COL=M['lieux_destiny'];XC,YC=COL['reverie']['ancre'];SX,SY=SIZE
V=(1440,1080);F=24;DUR=27;NN=Image.Resampling.NEAREST
OUT=ROOT/'Monde-Destiny-Devoilement.mp4'
Y,X=np.indices(SIZE[::-1],dtype=np.float32)
Y0=Y-YC;X0=X-XC
RAD=np.hypot(X0*.84,Y0)+9*np.sin(X*.061+Y*.035)+5*np.sin(X*.13-Y*.111)+3*np.sin(Y*.21+X*.17)
PAPER=Image.open(C/'Carte-non-devoilee.png').convert('RGB');WORLD=Image.open(C/'Monde-1x.png').convert('RGB');PURE=Image.open(C/'Monde-sans-lieux.png').convert('RGB');CLOUD=Image.open(C/'Nuages-graves.png').convert('RGBA')


def s(a,b,x):u=np.clip((x-a)/(b-a),0.,1.);return u*u*(3.-2*u)

def lerp(a,b,t):return a+(b-a)*t

def anchors(u):
    if u<6.5:return lerp(29,109,s(.65,5.7,u)),lerp(162,286,s(.7,6.5,u)),XC+5,YC-13
    if u<11.25:return 109,286,XC+5,YC-13
    if u<21.5:
        t=s(11.25,21.5,u);z=286*(SX/286)**t
        return lerp(109,1520,t**1.04),z,lerp(XC+5,SX/2,t),lerp(YC-13,SY/2,t)
    return 1520,SX,SX/2,SY/2


def bounds(w,x,y):
    w=min(SX,max(100,round(w)));h=round(w*.75);l=int(np.clip(round(x-w/2),0,SX-w));t=int(np.clip(round(y-h/2),0,SY-h));return l,t,l+w,t+h

@lru_cache(maxsize=96)
def sprite(kind,k):
    a=Image.open(ROOT/COL[kind]['fichier']).convert('RGBA');q=np.array(a)
    if kind not in ('reverie','fosse','passage') or k==0:return a
    r,g,b=q[...,:3].astype('int16').transpose(2,0,1);m=(b-r>25)&(g-r>25)&(g>77)&(q[...,3]>0)
    yy,xx=np.indices(m.shape);h=q.shape[0];phase=k%8
    if kind=='fosse':
        var=(((yy+xx*.19-phase*2.4)%15)<1.65)*41+(((yy-phase*1.7)%13)<2)*12;var=var*s(2,h*.34,yy)
    else:var=(((xx*.63+yy-phase*2)%13)<1.55)*23+(((xx+yy-phase)%9)<1)*8
    q[...,:3]=np.clip(q[...,:3].astype(float)+(var*m)[...,None]*[.53,.80,.84],0,255).astype(np.uint8)
    return Image.fromarray(q)


def pose_sprites():
    for k in ('reverie','fosse','passage'):
        b=sprite(k,0);src=Image.new('RGBA',(b.width*4,b.height*2))
        for i in range(8):src.paste(sprite(k,i),(i%4*b.width,i//4*b.height))
        src.save(C/f'Eau-{k}-8-poses.png',optimize=True)


def overlap(a,b):return a[2]>b[0] and a[3]>b[1] and b[2]>a[0] and b[3]>a[1]


def sea_sparks(z,box,i):
    d=ImageDraw.Draw(z,'RGBA');l,t,_,_=box
    # Tiny copper sea pulses and moving foam, anchored to the map itself.
    for j,(x,y) in enumerate([(1110,883),(1151,909),(1155,912),(1171,906),(1079,930),(1121,919),(1251,925),(870,780),(862,802),(639,986),(426,633),(867,149),(744,154),(853,688),(343,687),(511,400),(511,516),(239,780),(1474,421),(1412,774),(1418,947)]):
        if not (box[0]+6<x<box[2]-6 and box[1]<y<box[3]):continue
        p=(i+j*3)%13
        if p in (0,1,11) and z.getpixel((x-l,y-t))[0]>208:
            ox=x-l+(p%2);oy=y-t+(j%2)
            d.line((ox-1,oy,ox+4+(j%4),oy),fill=(255,231,174,120+(p!=0)*47),width=1)


def fogged(z,box,radius,t):
    y0,y1=box[1],box[3];x0,x1=box[0],box[2]
    if radius>1510:return z
    r=RAD[y0:y1,x0:x1];fade=s(radius-6,radius+14,r)
    # Paper cloud band is scalloped. Offset slowly over the parchment, without deforming coast.
    a=(fade*255+.5).astype(np.uint8);ink=PAPER.crop(box)
    # Upper-right daylight on the reveal edge gives it the small cream rim of a moving cloud.
    br=(1-np.abs(np.clip((r-radius-1)/7.5,-1,1)))**2
    if br.max()>.1:
        g=Image.new('RGB',ink.size,(255,230,178));ink=Image.composite(g,ink,Image.fromarray((br*72).astype(np.uint8)))
    return Image.composite(ink,z,Image.fromarray(a))


def view(i):
    t=i/F;radius,w,cx,cy=anchors(t);q=bounds(w,cx,cy);l,u,*_=q;im=PURE.crop(q);phase=i//3
    for k,v in COL.items():
        b=v['rectangle'];
        if not overlap(q,b):continue
        p=sprite(k,phase%8);im.paste(p,(b[0]-l,b[1]-u),p.getchannel('A'))
    sea_sparks(im,q,phase)
    if t>2.3 and t<18.3:
        d=ImageDraw.Draw(im,'RGBA')
        for j,k in enumerate(('reverie','fosse','passage','bois')):
            x,y=COL[k]['ancre'];x-=l;y=COL[k]['rectangle'][1]-u-3
            # A tiny gold location glint, never text or a modern pin. The fog covers unopened spots.
            v=(phase+j*2)%12
            if v<6:
                c=(250,210,91,120+int(122*math.sin((v+1)*math.pi/7)));d.polygon([(x,y-2),(x+2,y),(x,y+2),(x-2,y)],fill=c);d.point((x,y),fill=(255,246,172,220))
    im=fogged(im,q,radius,t)
    return im.resize(V,NN)


def film():
    pose_sprites();dest=W/OUT.name
    args=['ffmpeg','-hide_banner','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{V[0]}x{V[1]}','-r',str(F),'-i','-','-an','-c:v','libx264','-threads','6','-crf','17','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE)
    try:
        pts=[12,102,217,369,525,632]
        for i in range(F*DUR):
            a=view(i);proc.stdin.write(a.tobytes())
            if i in pts:a.resize((720,540),NN).save(W/f'Film-{i}.png',optimize=True)
        proc.stdin.close();assert proc.wait()==0;dest.replace(OUT)
    finally:
        if proc.poll() is None:proc.kill();proc.wait()
    print(OUT.name, DUR,'s',OUT.stat().st_size,'octets',flush=True)

if __name__=='__main__':film()
