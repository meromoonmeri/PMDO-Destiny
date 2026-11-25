#!/usr/bin/env python3
"""Trois propositions hors moteur. Compositing natif au pixel, puis agrandissement entier.
Python 3, Pillow, NumPy et FFmpeg. Voir Credits-et-notes.md pour les sources épinglées.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
import json
import math as m
from pathlib import Path
import random
import subprocess
import tempfile
from dataclasses import dataclass
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent
MAT = HERE / 'Matieres'
W, H = 224, 144
FEET = (112, 100)
CORE = (112, 86)
FPS, SCALE = 30, 4
NEAR = Image.Resampling.NEAREST
TAU = m.tau


@dataclass(frozen=True)
class Take:
    slug: str
    title: str
    accent: tuple[int, int, int]
    frames: int
    swap: int
    release: int
    gallery: float
    palette: tuple[tuple[int, int, int], ...]

    @property
    def nsec(self):
        return self.frames / FPS


TAKES = [
    Take('01-Resonance', 'Résonance violette', (192, 144, 254), 105, 51, 54, 1.94,
         ((148, 96, 230), (210, 154, 255), (253, 218, 255), (188, 149, 250))),
    Take('02-Prisme-fendu', 'Prisme fendu', (248, 185, 127), 132, 58, 79, 2.83,
         ((148, 142, 250), (248, 188, 255), (255, 217, 152), (156, 238, 242))),
    Take('03-Eclipse-X', 'Éclipse X', (121, 230, 238), 117, 61, 65, 1.88,
         ((57, 179, 245), (130, 238, 252), (167, 136, 251), (242, 169, 249))),
]


def unit(z):
    return min(1., max(0., z))


def ease(z):
    z = unit(z)
    return z * z * (3 - 2 * z)


def out_cubic(z):
    return 1 - (1 - unit(z)) ** 3


def fade(t, a, b, c, d):
    return ease((t-a)/(b-a)) * (1-ease((t-c)/(d-c)))


def blend(a, b, z):
    return a + (b-a)*z


def layer():
    return Image.new('RGBA', (W, H))


def tint(im, lut):
    return Image.merge('RGBA', tuple(im.getchannel(b).point(list(table))
                                     for b, table in zip('RGB', lut)) + (im.getchannel('A'),))


def col(c, opacity=1.):
    return (*c, int(255 * unit(opacity)))


def mul_alpha(im, a):
    if a >= .999:
        return im
    return Image.merge('RGBA', (im.getchannel('R'), im.getchannel('G'), im.getchannel('B'),
                                 im.getchannel('A').point([round(i*unit(a)) for i in range(256)])))


def stamp(dst, im, position, size=None, strength=1.):
    if strength <= 0:
        return
    if size:
        im = im.resize((max(1, round(size[0])), max(1, round(size[1]))), NEAR)
    x, y = position
    dst.alpha_composite(mul_alpha(im, strength), (round(x-im.width/2), round(y-im.height/2)))


def raw_bank(name):
    im = Image.open(MAT / 'Mega-Stones' / f'{name}.None.png').convert('RGBA')
    return [im.crop((i, 0, i + im.height, im.height)) for i in range(0, im.width, im.height)]


def gh_cycle(name, n, region):
    im = Image.open(MAT / 'Guildhouse' / f'MEGAGEN_V2_{name}.png').convert('RGBA')
    return [im.crop(tuple(v + (i % 8 if j % 2 == 0 else i // 8) * 160
                          for j, v in enumerate(region))) for i in range(n)]


def poses(p, name):
    node = next(a for a in ET.parse(p/'AnimData.xml').findall('.//Anim') if a.findtext('Name') == name)
    w, h = [int(node.findtext(i)) for i in ('FrameWidth', 'FrameHeight')]
    im, sha = (Image.open(p/f'{name}-{a}.png').convert('RGBA') for a in ('Anim','Shadow'))
    times = [int(q.text) for q in node.findall('./Durations/Duration')]
    assert im.size == sha.size == (w*len(times), 8*h)
    dirs = []
    for d in range(8):
        row = []
        for i in range(len(times)):
            box = (i*w, d*h, (i+1)*w, (d+1)*h)
            marks = np.asarray(sha.crop(box))
            y, x = np.where((marks[..., :3] == 255).all(axis=2) & (marks[..., 3] != 0))
            assert len(x) == 1, f'Ancre de sol {p.name} {name} {i}/{d}'
            c = layer()
            c.alpha_composite(im.crop(box), (FEET[0]-x.item(), FEET[1]-y.item()))
            row.append(c)
        dirs.append(row)
    return dirs, list(np.cumsum(times))


BASE, IDLE_TICKS = poses(MAT/'charizard', 'Idle')
MEGA, MEGA_TICKS = poses(MAT/'mega_charizard_x', 'Idle')
CHARGE, _ = poses(MAT/'charizard', 'Charge')
RINGS = raw_bank('Circle_Small_Purple_In')
BALL = raw_bank('Light_Ball_Purple')
SPIRAL = gh_cycle('sphere', 48, (40, 40, 120, 120))
CRACK = gh_cycle('break', 43, (33, 33, 127, 127))
CREST = gh_cycle('emblem', 48, (64, 56, 96, 104))

# Conserver le flash radial de Mega Stones, mais retirer les deux grandes pointes
# verticales et aplatir les autres lors du compositing. Aucun atlas de colonne chargé.
def short_star(im):
    a = np.array(im)
    y, x = np.indices(a.shape[:2])
    vertical_spikes = (abs(y-60) > 22) & (abs(x-60)*3 < abs(y-60)-15)
    a[vertical_spikes] = 0
    return Image.fromarray(a)


STAR = [short_star(p) for p in raw_bank('Mega_Background_White')]
ICE_STAR = [short_star(p) for p in raw_bank('Mega_Background_Light_Blue')]
ECLIPSE = []
for im in SPIRAL:
    # Same drawn texture, recast as a muted blue eclipse (faint spiral centre).
    a = np.array(im, dtype=np.float32)
    yy, xx = np.indices(a.shape[:2]); rad = np.hypot(xx-39.5, yy-39.5)/40
    luminance = (.24*a[..., 0]+.54*a[..., 1]+.22*a[..., 2])/255
    nm = np.clip((rad-.72)/.28, 0, 1)**1.32
    for ch, a0, a1, a2 in [(0, 11, 26, 102), (1, 17, 36, 182), (2, 40, 57, 218)]:
        a[..., ch] = a0+a1*luminance+a2*nm*luminance
    ECLIPSE.append(Image.fromarray(np.clip(a, 0, 255).astype('uint8')))


def arena():
    """Neutral orthogonal PMD-style stone; not an in-game capture."""
    rng = random.Random(12536)
    base = Image.new('RGB', (W,H), '#172331')
    d = ImageDraw.Draw(base)
    for yy in range(-9,H,24):
        shift = 0 if (yy//24)%2 else 12
        for xx in range(-16+shift,W,24):
            c = rng.randint(-4,4)
            d.rectangle((xx+1,yy+1,xx+23,yy+23),fill=(40+c,50+c,64+c))
            d.line((xx+2,yy+2,xx+21,yy+2),fill=(51+c,61+c,74+c))
            d.line((xx+2,yy+3,xx+2,yy+20),fill=(49+c,59+c,71+c))
            d.line((xx+4,yy+22,xx+21,yy+22),fill=(31+c,41+c,55+c))
            for _ in range(14):
                dx,dy=rng.randrange(3,20),rng.randrange(4,21)
                k=rng.randint(-5,5)
                d.line((xx+dx,yy+dy,xx+dx+rng.randrange(0,4),yy+dy),fill=(40+c+k,50+c+k,64+c+k))
            if rng.random()<.35:
                d.line((xx+23,yy+12,xx+19,yy+12,xx+17,yy+15,xx+14,yy+15),fill=(33+c,43+c,57+c))
    a = np.array(base, dtype=np.float32)
    y,x = np.indices((H,W)); v = np.clip(1-np.hypot((x-FEET[0])/138,(y-92)/116),.0,1.)
    a = a*(.53+.43*v[...,None])+v[...,None]*np.array([2.,6.,9.])
    return a.astype('float32')


FLOOR = arena()
YY,XX = np.indices((H,W))
GLOW = np.exp(-((XX-FEET[0])/40)**2-((YY-(FEET[1]+3))/18)**2)


def stage(color, gain):
    a = np.clip(FLOOR + GLOW[...,None]*(np.asarray(color)*.22)*min(1.35,gain),0,255).astype('uint8')
    return Image.fromarray(a).convert('RGBA')


def shadow(dst, evolved):
    im=layer();d=ImageDraw.Draw(im)
    x,y=FEET;w=16 if evolved else 13
    d.ellipse((x-w-2,y-4,x+w+2,y+6),fill=(12,18,28,123))
    d.ellipse((x-w,y-3,x+w,y+4),fill=(9,12,20,171))
    dst.alpha_composite(im)


def rhombus(d, x, y, n, c, a):
    x,y=round(x),round(y)
    if n<=1:
        d.point((x,y),fill=col(c,a))
    else:
        d.polygon([(x,y-n),(x+n-1,y),(x,y+n),(x-n+1,y)],fill=col(c,a*.9))
        if n>=3: d.point((x,y),fill=col((255,249,255),a))


def wave(dst, pos, rx, ry, c, gain, alpha_back=.48, width=1, phase=0.):
    if gain<=0 or rx<=1 or ry<=1:
        return
    x,y=pos; bounds=(round(x-rx), round(y-ry), round(x+rx), round(y+ry))
    d=ImageDraw.Draw(dst)
    d.arc(bounds, 180, 359, fill=col(c,gain*alpha_back), width=width)
    d.arc(bounds, 0, 180, fill=col(c,gain), width=width)
    if width>1:
        st=int(phase*180/m.pi)%120
        d.arc(bounds, st, st+28, fill=col((240,238,255),gain), width=1)


def orbit(dst, rx, ry, phi, tilt, head, length, color, strength, front):
    if strength<=0:return
    x,y=CORE;d=ImageDraw.Draw(dst);p=None
    for u in range(15,-1,-1):
        p0=head-phi*length*(u/15)
        dx=rx*m.cos(p0);dy=ry*m.sin(p0)
        a=dx*m.cos(tilt)-dy*m.sin(tilt)+x
        b=dx*m.sin(tilt)+dy*m.cos(tilt)+y
        visible=(m.sin(p0)>=0) == front
        alpha=strength*(1-u/16)**1.4*(1 if front else .63)
        if visible and p: d.line((p,(round(a),round(b))),fill=col(color,alpha),width=1 if u>7 else 2)
        p=(round(a),round(b)) if visible else None
        if visible and u==0: rhombus(d, a, b, 3, color, alpha)


def intaking(dst, t, seed, colors, close, front):
    rng=random.Random(seed);d=ImageDraw.Draw(dst)
    for i in range(26):
        a0=rng.uniform(-m.pi,m.pi);rad=rng.uniform(38,87);s=rng.uniform(.17,close-.31);duration=rng.uniform(.24,.69)
        height=rng.uniform(.36,.64); v=rng.choice([-1.,1.]); n=rng.choice((1,1,2,2,3))
        z=(t-s)/duration
        if z<0 or z>=1 or t>=close or (m.sin(a0+v*z*1.40)>=0)!=front: continue
        gain=fade(z,0,.20,.62,1)*ease((close-t)/.15)
        if gain<=0: continue
        def xy(p):
            r=blend(rad,5,p**1.30);a=a0+v*p*1.40
            return (CORE[0]+r*m.cos(a),CORE[1]+r*height*m.sin(a))
        x,y=xy(z); x0,y0=xy(max(0,z-.075))
        c=colors[(i+1)%len(colors)]; d.line((round(x0),round(y0),round(x),round(y)),fill=col(c,gain*.46))
        rhombus(d,x,y,n,c,gain)


def drift(dst, age, seed, colors, duration, bits):
    if age<0 or age>duration: return
    rng=random.Random(seed);d=ImageDraw.Draw(dst)
    for i in range(bits):
        a=i*TAU/bits+rng.uniform(-.25,.25);r=rng.uniform(45,87); lift=rng.uniform(2,24)
        z=(age-rng.uniform(0,.125))/(duration*rng.uniform(.58,1.02));
        if not 0<=z<1:continue
        n=rng.choice((1,1,1,2,2,3))
        x=CORE[0]+(12+r*out_cubic(z))*m.cos(a)
        y=CORE[1]+(6+r*out_cubic(z))*m.sin(a)*.44-lift*m.sin(m.pi*z)
        p=1-ease(z)
        rhombus(d,x,y,n if p>.39 else 1,colors[i%len(colors)],p*.88)


def crest(dst, t, take, launch, width, duration, high):
    q=t-launch
    if q<0 or q>=duration:return
    alpha=fade(q,0,.16,duration*.61,duration)
    im=CREST[int(q*30)%48]
    if take==2:
        im=tint(im, ([round(i*.72) for i in range(256)],
                     [round(i*.83+25) for i in range(256)],[min(255,round(i*.82+55)) for i in range(256)]))
    stamp(dst, im,(CORE[0],high-6*out_cubic(q/duration)),(width,width*1.5),alpha)


def frame(take_i, f, direction=0, audit=False):
    t=f/FPS; v=TAKES[take_i]; age=(f-v.release)/FPS; s=v.release/FPS
    after=f>=v.swap
    c=v.palette
    ground, behind, ahead, cover = (layer() for _ in range(4))
    if take_i==0:
        # Nested, slightly inclined pulses, then the growth of Deeshura's white orb.
        charge=fade(t,.13,.56,1.52,1.85)
        for i,start in enumerate((.17,.52,.87,1.19)):
            q=(t-start)/(.57 if i<2 else .53)
            if 0<=q<1:
                fa=fade(q,0,.18,.65,1)
                ring=RINGS[min(8,int(q*9))]
                stamp(ground,ring,FEET,(99,40),fa*.87)
                stamp(ahead,ring,(CORE[0],CORE[1]-3),(56,56),fa*.50)
        intaking(behind,t,231,c,1.65,False);intaking(ahead,t,231,c,1.65,True)
        if .77<=t<s:
            p=unit((t-.77)/(.92)); b=min(10,int(p*11)); size=blend(61,82,ease(p))
            stamp(cover,BALL[b],CORE,(size,size),1.)
            if f>=v.swap-3:
                # Small chromatic fringe drawn from the rainbow spiral.
                fringe=SPIRAL[(f*2)%48]; width=82+round(5*m.sin(p*m.pi))
                stamp(behind,fringe,CORE,(width,width),.78)
        if 0<=age<.44:
            k=2+min(3,int(age/.073)); w=blend(103,145,out_cubic(age/.37))
            stamp(behind,STAR[k],(CORE[0],CORE[1]+2),(w,w*.54),(1-ease(age/.44))*.94)
            if age<.11:
                q=age/.11;stamp(cover,BALL[9-int(q*5)],CORE,(76,76),(1-q)**2*.72)
        crest(ahead,t,0,s+.17,21,1.08,48)
        intensity=charge*.65+(1-ease(age/.65))*.83 if age>=0 else charge*.75
    elif take_i==1:
        # Guildhouse spiral, held, then the actual Guildhouse shell fracture.
        charge=fade(t,.1,.69,1.88,2.34)
        intaking(behind,t,119,c,1.65,False);intaking(ahead,t,119,c,1.65,True)
        for i,start in enumerate((.28,.79,1.22)):
            q=(t-start)/.78
            if 0<=q<1:
                stamp(ground,RINGS[min(8,int(q*9))],(FEET[0], FEET[1]+3),
                      (100,38),fade(q,0,.16,.60,1)*.71)
        if .65<=t<2.19:
            q=ease((t-.65)/.91); k=int((t-.65)*32)%48
            size=blend(23,80,q)
            stamp(cover,SPIRAL[k],CORE,(size,size),ease((t-.65)/.57))
            if t>=2.02:
                # Match colour and shape into the first held fracture key.
                stamp(cover,CRACK[0],CORE,(94,94),ease((t-2.02)/.15))
        elif 2.19<=t<s:
            k=round(blend(0,14,ease((t-2.19)/(s-2.19))))
            stamp(cover,CRACK[k],CORE)
            if k>=7 and f%10 in (2,3,4):
                gl=1-abs(3-f%10)/2
                stamp(ahead,STAR[1],(CORE[0]+(8 if f%20<10 else -13),CORE[1]-17),(53,36),.6*gl)
        if age>=0:
            k=15+round(age*33)
            if k<43:
                size=94+12*out_cubic(age/.74)
                stamp(cover,CRACK[k],CORE,(size,size),1-ease((k-32)/10))
            if age<.49:
                k=2+min(3,int(age/.089));w=blend(115,146,out_cubic(age/.48))
                stamp(behind,ICE_STAR[k],CORE,(w,w*.58),(1-ease(age/.49))*.84)
            crest(ahead,t,1,s+.12,24,1.31,43)
        intensity=charge*.56+(.54 if 1.50<t<s else 0)
        if age>=0:intensity=(1-ease(age/.83))*1.1
    else:
        # Two streaked orbits with real back/front crossings; no vertical emitter.
        charge=fade(t,.10,.43,1.72,2.17)
        orbit_amp=fade(t,.16,.44,2.24,2.91)
        tr=t if t<1.63 else 1.63+(t-1.63)*.66
        a=TAU*(.15+.67*tr+.29*tr**2)
        p=1-ease((t-1.36)/.59)*.11+.42*out_cubic(age/.49)
        for fg, plane in ((False,behind),(True,ahead)):
            orbit(plane, (54+3*m.sin(a))*p, 17*p, 1, -.27, a, 2.26, c[1], orbit_amp, fg)
            orbit(plane, 49*p, 19*p, -1, .32, -a+.44, 1.94, c[3], orbit_amp*.96, fg)
        intaking(behind,t,722,c,1.58,False);intaking(ahead,t,722,c,1.58,True)
        if 1.05<=t<s:
            q=ease((t-1.05)/.60); size=blend(26,75,q)
            stamp(cover,ECLIPSE[(f*2)%48],CORE,(size,size),q)
            if q>.45:
                # Broken, moving highlights on a dark rim; do not brighten the whole sphere.
                rim=layer();d=ImageDraw.Draw(rim);x,y=CORE;r=size/2-1
                bbox=(round(x-r),round(y-r),round(x+r),round(y+r));theta=round(-t*162)
                d.arc(bbox,theta,theta+100,fill=col(c[1],q*.81),width=2)
                d.arc(bbox,theta+176,theta+250,fill=col(c[2],q*.7),width=1)
                cover.alpha_composite(rim)
            if t>=1.67:
                # The native Deeshura light ball becomes a cold horizontal iris instead
                # of a second giant white sphere. The opaque shell stays underneath.
                a0=ease((t-1.67)/.40)
                stamp(cover,BALL[min(10,int(6+a0*4))],CORE,(78,5+8*a0),.87*a0)
        if 0<=age<.48:
            w=blend(96,172,out_cubic(age/.46)); k=2+min(3,int(age/.087))
            stamp(behind,ICE_STAR[k],CORE,(w,w*.265),1-ease(age/.48))
            if age<.27:
                iris=ECLIPSE[((v.release-1)*2)%48].resize((75,75),NEAR)
                q=out_cubic(age/.27); a1=(1-ease(age/.27))*.77
                for side in (-1,1):
                    piece=iris.crop((0,0,36,75) if side<0 else (39,0,75,75))
                    stamp(behind,piece,(CORE[0]+side*(22+34*q),CORE[1]),(36,75-33*q),a1)
                if age<.085: stamp(ahead,BALL[9],CORE,(122,19),.72*(1-ease(age/.085)))
        crest(ahead,t,2,s+.24,20,1.16,45)
        intensity=charge*.80+(1-ease(age/.67))*.97 if age>=0 else charge*.82

    if age>=0:
        for j in range(2):
            q=(age-j*.095)/(.64 if take_i==1 else .60)
            if 0<=q<1:
                r=blend(16,78+12*j,out_cubic(q)); g=(1-ease(q))*(.79 if j==0 else .46)
                wave(ground,(FEET[0],FEET[1]+2),r,r*.235,c[j+1],g,.57,2 if q<.38 and j==0 else 1,q*4)
        drift(ahead,age,180+take_i,c,[.82,.95,.87][take_i], [24,36,29][take_i])

    scene=stage(v.accent,.22+intensity)
    scene.alpha_composite(ground)
    shadow(scene,after)
    scene.alpha_composite(behind)
    # Base Charge pose is held only during energy intake (original file, centered at native white floor marker).
    if after:
        pose = MEGA[direction][bisect_right(MEGA_TICKS, (max(0,f-v.release)*2)%MEGA_TICKS[-1])]
    elif .32<t<s:
        pose = CHARGE[direction][2]
    else:
        pose = BASE[direction][bisect_right(IDLE_TICKS,(f*2)%IDLE_TICKS[-1])]
    # The Prisme reveal is held until the aperture in its shell is visible.
    if take_i!=1 or not (v.swap+1<=f<v.release):
        if after and 0<=age<=.55:
            # A separate underlit soft 1 px edge: never edits the official sprite.
            aura=Image.new('RGBA',(W,H),c[1]);a=pose.getchannel('A').filter(ImageFilter.MaxFilter(3))
            aura.putalpha(a.point([round(p*.54*(1-ease(age/.55))) for p in range(256)]))
            scene.alpha_composite(aura)
        scene.alpha_composite(pose)
    scene.alpha_composite(cover)
    scene.alpha_composite(ahead)
    if audit: return scene,cover
    return scene.convert('RGB')


def audit_swap():
    result=[]
    for i,v in enumerate(TAKES):
        # Validate the exact switch pose against all eight native orientations and all Idle cels,
        # plus Charge on the outgoing side. Only the actual opaque covering layer may count.
        runs=0
        for f in (v.swap-1,v.swap):
            _,cover=frame(i,f,audit=True)
            mask=np.asarray(cover.getchannel('A'))
            for group in (BASE,MEGA,CHARGE):
                for row in group:
                    for sprite in row:
                        alpha=np.asarray(sprite.getchannel('A'))
                        assert (mask[alpha>0] == 255).all(), (v.slug,f,'forme non masquée')
                        runs+=1
        # All complete previews end cleanly without an opaque sphere or remaining shell.
        _,last=frame(i,v.frames-1,audit=True)
        assert not last.getchannel('A').getbbox()
        result.append({'version':v.title,'images':v.frames,'duration_s':v.nsec,
                       'frame_forme':v.swap,'frame_revelation':v.release,
                       'tests_masquage_complet':runs,'orientations_test_masque':8})
    return result


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def soundtrack(take, path):
    """Retiming only: original climax starts just before 3.70 s in the source.
    Keep the impact/tail at original pitch and speed, sync it to the visual release.
    """
    source = MAT/'Mega-Stones/Mega_Evolution.ogg'
    mark=3.70; start=.15; trigger=take.release/FPS
    # Compress attack using atempo, with two stages if needed to stay within [0.5,2].
    before=trigger-start
    speed=mark/before
    factors=[2,speed/2] if speed>2 else [speed]
    tempo=','.join('atempo=%.7f'%i for i in factors)
    graph=(f'[0:a]asplit=2[up][hit];[up]atrim=0:{mark},asetpts=PTS-STARTPTS,{tempo},'
           f'apad,atrim=0:{before:.6f},afade=in:d=0.04,afade=out:st={before-.028:.6f}:d=0.028,'
           f'adelay={round(start*1000)}:all=1[a];'
           f'[hit]atrim=start={mark},asetpts=PTS-STARTPTS,adelay={round(trigger*1000)}:all=1[b];'
           f'[a][b]amix=inputs=2:normalize=0,volume=1.50,alimiter=limit=0.85:latency=1,'
           f'apad,atrim=duration={take.nsec:.6f},afade=out:st={take.nsec-.18:.6f}:d=0.18[out]')
    run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(source),'-filter_complex',graph,
         '-map','[out]','-ac','2','-ar','48000',str(path)])


def export(take_i, out, direction):
    v=TAKES[take_i]; target=out/(v.slug+'.mp4')
    with tempfile.TemporaryDirectory(prefix='guildhouse-') as scratch:
        wav=Path(scratch)/'son.wav';soundtrack(v,wav)
        cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
             '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(wav),'-map','0:v:0','-map','1:a:0',
             '-vf',f'scale={W*SCALE}:{H*SCALE}:flags=neighbor', '-c:v','libx264','-crf','14','-preset','fast',
             '-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart','-t',f'{v.nsec:.6f}',
             '-metadata',f'title={v.title} — Guilde Treehouse PMD',str(target)]
        with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
            for f in range(v.frames):
                proc.stdin.write(frame(take_i,f,direction).tobytes())
            proc.stdin.close()
            if proc.wait()!=0: raise RuntimeError(f'encodage impossible : {v.slug}')
    print(f'{v.title} : {v.frames} images, {v.nsec:.2f} s, {target.stat().st_size:,} o', flush=True)


def review(out, direction):
    samples=[(.00,.73,1.24,1.70,1.87,2.16,2.63,3.25),
             (.00,.87,1.39,1.93,2.50,2.76,3.14,4.14),
             (.00,.58,1.19,1.50,1.97,2.20,2.56,3.65)]
    for i, v in enumerate(TAKES):
        board=Image.new('RGB',(W*4,H*2+46),(15,21,33));d=ImageDraw.Draw(board)
        font=ImageFont.truetype('DejaVuSans.ttf', 11)
        for k,t in enumerate(samples[i]):
            f=min(v.frames-1,round(t*FPS));x=W*(k%4);y=(H+23)*(k//4)
            d.text((x+8,y+5),f'{v.title}   •   {f/FPS:.2f} s', font=font,fill=v.accent)
            board.paste(frame(i,f,direction),(x,y+23))
        board.save(out/(v.slug+'-controle.png'))
        frame(i,round(v.gallery*FPS),direction).resize((W*2,H*2),NEAR).save(out/(v.slug+'-visuel.png'))
    print('Planches de contrôle prêtes.',flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE.parent)
    p.add_argument('--direction',type=int,choices=range(8),default=0)
    p.add_argument('--draft',type=Path,help='Destination des planches, pas de MP4')
    a=p.parse_args(); stats=audit_swap(); print(json.dumps(stats,ensure_ascii=False),flush=True)
    if a.draft:
        a.draft.mkdir(parents=True,exist_ok=True);review(a.draft,a.direction);return
    a.out.mkdir(parents=True,exist_ok=True)
    for i in range(3):export(i,a.out,a.direction)


if __name__=='__main__':main()
