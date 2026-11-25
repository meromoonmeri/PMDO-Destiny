#!/usr/bin/env python3
"""Éclipse X → Prisme fendu : une seule sphère, raccord de phase et vraie fracture V2.

Compositing indépendant de PMDO. Conserve les trois propositions initiales.
Python 3 + Pillow, NumPy et FFmpeg. Voir Credits-et-notes.md pour la provenance.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from functools import lru_cache
import math
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from rendre import (
    HERE, W, H, FEET, CORE, FPS, SCALE, NEAR, TAU, Take, BASE, CHARGE, MEGA,
    IDLE_TICKS, MEGA_TICKS, SPIRAL, CRACK, ECLIPSE, RINGS, ICE_STAR, BALL,
    layer, col, stamp, ease, unit, blend, out_cubic, fade, orbit, intaking,
    wave, drift, crest, stage, shadow, soundtrack,
)

# Frames à 30 i/s ; l'apogée du son est recalée à RELEASE.
BIRTH = 30
FULL_DIAMETER = 50
COLOR_IN, COLOR_OUT = 43, 74
MATCH, FRACTURE = 81, 87
SWAP, RELEASE = 62, 100
END = 144
COOL = (121, 230, 238)
PRISM = (218, 183, 249)
COLORS = ((89, 186, 250), (141, 239, 255), (248, 204, 157), (243, 172, 250))
TAKE = Take('04-Eclipse-X-Prisme', 'Éclipse X — Prisme fendu', COOL,
            END, SWAP, RELEASE, 3.52, COLORS)

# Same RGBA geometry in both variants. Local easing makes the inner filaments take
# colour first, then the outer spiral. The underlying phase is never restarted.
_y, _x = np.indices((80, 80), dtype=np.float32)
_r = np.hypot(_x-39.5, _y-39.5)/40
_phi = np.arctan2(_y-39.5, _x-39.5)
_COLOR_DELAY = .165*np.minimum(1, _r) + .085*(.5+.5*np.cos(_phi+3.8*_r-.63))
_ECLIPSE_RGBA = [np.asarray(i, dtype=np.float32) for i in ECLIPSE]
_PRISM_RGBA = [np.asarray(i, dtype=np.float32) for i in SPIRAL]


def rgb(a,b,q):
    return tuple(round(blend(x,y,q)) for x,y in zip(a,b))


def colorize(index, amount):
    """Start/end are the exact same bank cells, not two stacked spheres."""
    if amount <= 0:
        return ECLIPSE[index]
    if amount >= 1:
        return SPIRAL[index]
    a, b = _ECLIPSE_RGBA[index], _PRISM_RGBA[index]
    p = np.clip((amount-_COLOR_DELAY)/(1-_COLOR_DELAY),0,1)
    weight = (p*p*(3-2*p))[...,None]
    o = b.copy()
    o[...,:3] = a[...,:3]*(1-weight) + b[...,:3]*weight
    return Image.fromarray(np.rint(o).astype('uint8'))


def premult_mix(a, b, q):
    if q<=0:return a
    if q>=1:return b
    am,bm = [np.asarray(p,dtype=np.float32)/255 for p in (a,b)]
    alpha = am[...,3:]*(1-q)+bm[...,3:]*q
    color = (am[...,:3]*am[...,3:]*(1-q)+bm[...,:3]*bm[...,3:]*q)/np.maximum(alpha,1/255)
    return Image.fromarray(np.rint(np.clip(np.concatenate((color,alpha),axis=2),0,1)*255).astype('uint8'))


# The colour/contour lookup against the 48 complete spiral cells favours phase 0.
# Align the first fracture cel at (dx,dy) = (0,1) and 92×91 instead of 94×94.
# At the release, the shards gradually regain their V2 scale as they spread.
_prism_end = layer(); stamp(_prism_end, SPIRAL[0], CORE)
_crack_start = layer(); stamp(_crack_start, CRACK[0], (CORE[0], CORE[1]+1), (92,91))


def spiral_at(f):
    return (f-MATCH)%48


@lru_cache(maxsize=END)
def shell(f):
    """Alpha of the actual occluder; tests never count the background or flash."""
    if f < BIRTH: return layer()
    if f < MATCH:
        q=ease((f-BIRTH)/(FULL_DIAMETER-BIRTH))
        p=unit((f-COLOR_IN)/(COLOR_OUT-COLOR_IN))
        diameter=round(blend(26,80,q))
        art=colorize(spiral_at(f),p)
        a=layer()
        stamp(a,art,CORE,(diameter,diameter),ease((f-BIRTH)/17))
        return a
    if f < FRACTURE:
        return premult_mix(_prism_end,_crack_start,ease((f-MATCH)/(FRACTURE-MATCH)))
    if f < RELEASE:
        p=(f-FRACTURE)/(RELEASE-FRACTURE)
        k=round(15*p**1.02)
        a=layer();stamp(a,CRACK[k],(CORE[0],CORE[1]+1),(92,91));return a
    a=layer(); age=(f-RELEASE)/FPS
    k=15+round(age*32)
    if k<43:
        radial=out_cubic(age/.82)
        stamp(a,CRACK[k],(CORE[0],CORE[1]+1-radial),
              (92+15*radial,91+16*radial),1-ease((k-31)/11))
    return a


# Reshaped native Deeshura highlight. The narrow iris appears only while colour
# is forming, recedes before the pristine prism hold, and never turns into a column.
def iris_bank():
    r=[]
    for im in BALL:
        x=np.array(im,dtype=np.float32)
        v=.25*x[...,0]+.50*x[...,1]+.25*x[...,2]
        x[...,0]=np.minimum(255,26+.64*v)
        x[...,1]=np.minimum(255,61+.72*v)
        x[...,2]=np.minimum(255,96+.64*v)
        r.append(Image.fromarray(x.astype('uint8')))
    return r


IRIS=iris_bank()


def render(f, direction=0):
    t=f/FPS; age=(f-RELEASE)/FPS
    p=unit((f-COLOR_IN)/(COLOR_OUT-COLOR_IN)); tintp=ease(p)
    floor, back, front = layer(),layer(),layer()
    cover=shell(f)

    # The same blue/pink orbits continue around the shell; their radius shrinks
    # as the energy enters it, then they peel outward with the released shards.
    a=TAU*(.15+.67*min(t,1.63)+.29*min(t,1.63)**2+1.02*max(0,t-1.63))
    pull=ease((t-1.10)/1.18); recoil=out_cubic(age/.55)
    r=1-.20*pull+.50*recoil
    pre=fade(t,.16,.44,1.9,3.33)
    post=.71*fade(age,-.08,.09,.22,.84)
    power=min(.99,pre+post)
    teal=rgb(COLORS[1],(183,252,238),tintp*.56)
    rose=rgb(COLORS[3],(255,199,204),tintp*.43)
    for fg, plane in ((False,back),(True,front)):
        orbit(plane,(54+3*math.sin(a))*r,17*r,1,-.27,a,2.26,teal,power,fg)
        orbit(plane,49*r,19*r,-1,.32,-a+.44,1.94,rose,power*.9,fg)
        intaking(plane,t,722,COLORS,1.62,fg)

    for start,dur,gain in ((1.07,.64,.37),(1.67,.67,.40)):
        q=(t-start)/dur
        if 0<=q<1:
            stamp(floor,RINGS[min(8,int(q*9))], (FEET[0],FEET[1]+3), (103,36),
                  gain*fade(q,0,.15,.67,1))

    # Rim highlights belong to the dark eclipse only. Fade them down as the
    # rainbow texture takes over. No second orb or artificial fade-to-white.
    rim=layer(); d=ImageDraw.Draw(rim)
    if BIRTH<=f<COLOR_OUT:
        g=ease((f-BIRTH)/(FULL_DIAMETER-BIRTH)); dim=g*(1-ease((p-.15)/.67))
        radius=blend(26,80,g)/2-1
        x,y=CORE; rect=(round(x-radius),round(y-radius),round(x+radius),round(y+radius))
        ang=round(-t*162)
        d.arc(rect,ang,ang+104,fill=col(teal,.79*dim),width=2)
        d.arc(rect,ang+178,ang+256,fill=col((169,141,255),.66*dim),width=1)
        ir=fade(t,1.48,1.74,1.83,2.23)
        if ir:
            iq=ease((t-1.48)/.68)
            stamp(rim,IRIS[min(10,7+int(iq*4))],(x,y+1),(64+7*iq,6+3*ir),.54*ir)

    if 0<=age<.52:
        b=out_cubic(age/.50); star=ICE_STAR[2+min(3,int(age/.087))]
        width=blend(100,166,b)
        stamp(back,star,CORE,(width,width*.34),.9*(1-ease(age/.52)))
    if 0<=age<.1:
        # Very thin sideways release, behind the sprite. Retains the aperture
        # character of Éclipse X without replacing the prism's real fracture.
        stamp(back,IRIS[9], CORE, (122+age*220,9), .57*(1-ease(age/.1)))
    if age>=0:
        for j in range(2):
            q=(age-j*.10)/.68
            if 0<=q<1:
                rad=blend(17,75+j*14,out_cubic(q))
                wave(floor,(FEET[0],FEET[1]+2),rad,rad*.235,(teal,rose)[j],
                     (1-ease(q))*(.79 if j==0 else .44),.54,2 if j==0 and q<.31 else 1,q*3)
        drift(front,age,1121,COLORS,1.02,32)
        crest(front,t,1,RELEASE/FPS+.16,23,1.22,42)

    lamp=rgb(COOL,PRISM,tintp)
    before=(.69*fade(t,.09,.73,2.7,3.37)+.30*fade(t,1.48,2.17,3.2,3.48))
    burst=1.04*(1-ease(age/.82)) if age>=0 else 0
    scene=stage(lamp,.22+max(before,burst))
    scene.alpha_composite(floor)
    evolved=f>=SWAP
    shadow(scene,evolved)
    scene.alpha_composite(back)

    if not (SWAP<f<RELEASE):
        if evolved:
            pose=MEGA[direction][bisect_right(MEGA_TICKS, (2*max(0,f-RELEASE))%MEGA_TICKS[-1])]
            if 0<=age<.57:
                rimlight=Image.new('RGBA',(W,H),(159,229,255))
                alpha=pose.getchannel('A').filter(ImageFilter.MaxFilter(3))
                rimlight.putalpha(alpha.point([round(i*.51*(1-ease(age/.57))) for i in range(256)]))
                scene.alpha_composite(rimlight)
        elif t>.32:
            pose=CHARGE[direction][2]
        else:
            pose=BASE[direction][bisect_right(IDLE_TICKS,(2*f)%IDLE_TICKS[-1])]
        scene.alpha_composite(pose)
    scene.alpha_composite(cover)
    scene.alpha_composite(rim)
    scene.alpha_composite(front)
    return scene.convert('RGB')


def audit():
    checks=0
    for f in (SWAP-1,SWAP):
        a=np.asarray(shell(f).getchannel('A'))
        for group in (BASE,CHARGE,MEGA):
            for seq in group:
                for item in seq:
                    assert np.all(a[np.asarray(item.getchannel('A'))>0]==255), f'changement visible à {f}'
                    checks+=1
    # Identical texture, colour, dimensions and placement to the pristine Prisme
    # bank from the end of the colour transition until the matched fracture cel.
    for f in range(COLOR_OUT,MATCH+1):
        expected=layer(); stamp(expected,SPIRAL[spiral_at(f)],CORE)
        assert np.array_equal(np.asarray(expected),np.asarray(shell(f))),f'prisme non identique à {f}'
    assert not shell(END-1).getchannel('A').getbbox()
    print(f'PASS : {checks} contrôles de masquage (8 directions) ; '
          f'{MATCH+1-COLOR_OUT} images prisme exact, puis vraie coque V2.',flush=True)


def film(out, direction):
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='eclipse-prisme-') as scratch:
        audio=Path(scratch)/'son.wav'
        soundtrack(TAKE,audio)
        cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
             '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(audio),'-map','0:v:0','-map','1:a:0',
             '-vf',f'scale={W*SCALE}:{H*SCALE}:flags=neighbor','-c:v','libx264','-crf','14',
             '-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',
             '-t',f'{TAKE.nsec:.6f}','-metadata',f'title={TAKE.title} — Guilde Treehouse PMD',str(out)]
        with subprocess.Popen(cmd,stdin=subprocess.PIPE) as p:
            for f in range(END):p.stdin.write(render(f,direction).tobytes())
            p.stdin.close()
            if p.wait()!=0:raise RuntimeError('Encodage FFmpeg incomplet')
    print(f'{out.name} : {END} images, {TAKE.nsec:.2f} s, {out.stat().st_size} octets',flush=True)


def control(path,direction):
    samples=((.67,'Orbites'),(1.42,'Éclipse'),(1.70,'Iris'),(1.93,'Premières couleurs'),
             (2.2,'Spirale en couleur'),(2.57,'Prisme exact'),(3.10,'Fissures'),(3.50,'Révélation'))
    board=Image.new('RGB',(W*4,(H+24)*2),'#141b2a');d=ImageDraw.Draw(board)
    font=ImageFont.truetype('DejaVuSans.ttf',12)
    for i,(t,label) in enumerate(samples):
        x,y=i%4*W,i//4*(H+24)
        d.text((x+8,y+6),f'{t:.2f} s · {label}',fill='#d9ebfc',font=font)
        board.paste(render(round(t*FPS),direction),(x,y+24))
    path.parent.mkdir(parents=True,exist_ok=True)
    board.save(path)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=HERE.parent/(TAKE.slug+'.mp4'))
    p.add_argument('--direction',type=int,choices=range(8),default=0)
    p.add_argument('--control',type=Path)
    p.add_argument('--draft',action='store_true')
    a=p.parse_args();audit()
    if a.control:control(a.control,a.direction)
    if not a.draft:film(a.out,a.direction)


if __name__=='__main__':main()
