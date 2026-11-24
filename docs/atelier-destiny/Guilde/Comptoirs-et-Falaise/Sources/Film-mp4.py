#!/usr/bin/env python3
"""Short offline MP4 from the workshop's lossless sprites and maps."""
from pathlib import Path
from functools import lru_cache
import json,subprocess
from PIL import Image,ImageDraw,ImageFont
from Implantation import ROOT,base
from Planche import frame as plan_frame

NW,NH,FPS=1280,720,30
W=Path.home()/'.cache/comptoirs-et-falaise'
F=ROOT/'Falaise'; CL=F/'Calques'; OUT=ROOT/'Destiny-Comptoirs-et-Falaise.mp4'
I=json.loads((ROOT/'Index-Comptoirs.json').read_text())['orientations']
EX=json.loads((ROOT/'Implantations.json').read_text());R=json.loads((ROOT/'Releve-Cliff.json').read_text())
SPR=[Image.open(ROOT/q['png']).convert('RGBA') for q in I]
BR=[(x,y,Image.open(CL/n).convert('RGBA')) for x,y,n in R['calques']['nuit']]
OX,OY,OW,OH,path=R['atlas_mer']; atlas=Image.open(CL/path).convert('RGBA'); SEA=[atlas.crop((k%2*OW,k//2*OH,k%2*OW+OW,k//2*OH+OH)) for k in range(12)]
NIGHT=Image.open(F/'Cliff-nuit-sans.png').convert('RGBA');DAY=Image.open(F/'Cliff-jour.png').convert('RGB')
C='#fff0d1';G='#dfb475';M='#c9c6b7';B='#e0e3ff';N='#869a8f'; SAGE='#294238'; GOLD='#604b34'
DIRFONT='/usr/share/fonts/truetype/dejavu/'

@lru_cache(maxsize=None)
def font(style,size):
    return ImageFont.truetype(DIRFONT+{'title':'DejaVuSerif.ttf','sans':'DejaVuSans.ttf','bold':'DejaVuSans-Bold.ttf','mono':'DejaVuSansMono.ttf'}[style],size)
def txt(d,text,x,y,size=23,style='sans',color=C,anchor=None):d.text((x,y),text,font=font(style,size),fill=color,anchor=anchor)
def card(d,bg,r,edge='#4b5c50',rad=11):d.rounded_rectangle(r,radius=rad,fill=bg,outline=edge,width=2)
def tint(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))

@lru_cache(maxsize=3)
def back(cold=False):
    z=Image.new('RGB',(NW,NH));g=ImageDraw.Draw(z)
    lo,hi=((26,32,55),(15,19,30)) if cold else ((27,39,35),(14,22,21))
    for y in range(NH):g.line((0,y,NW,y),fill=tint(lo,hi,y/(NH-1)))
    return z

def label(d,text,x,y,cold=False):
    w=round(d.textlength(text,font=font('mono',18)))+28
    card(d,'#25304b' if cold else '#2a382f',(x,y,x+w,y+34),'#576587' if cold else '#66785e',8);txt(d,text,x+14,y+7,18,'mono',B if cold else '#dfefdf')
    return w

def head(number,title,caption,cold=False):
    z=back(cold).copy();d=ImageDraw.Draw(z);txt(d,'DESTINY 0.7.7  /  '+number,45,22,18,'mono',G);txt(d,title,42,49,45,'title',C)
    if caption:txt(d,caption,45,108,20,'sans',M)
    return z,d

def foot(d,text,right):
    d.line((44,671,1235,671),fill='#476354',width=1)
    txt(d,text,45,684,17,'mono','#d0d6cd');txt(d,right,1233,684,17,'mono',G,anchor='ra')

def fit(dst,im,rect,factor=None):
    l,t,r,b=rect;s=factor or min((r-l)/im.width,(b-t)/im.height)
    n=im.resize((round(s*im.width),round(s*im.height)),Image.Resampling.NEAREST);st=int((l+r-n.width)/2),int((t+b-n.height)/2)
    dst.paste(n,st,n if n.mode=='RGBA' else None)

def checker(d,rect,base,alt,step=10):
    l,t,r,b=rect;d.rectangle((l,t,r-1,b-1),fill=base)
    for y in range(t,b,step):
        for x in range(l,r,step):
            if ((x-l)//step+(y-t)//step)%2:d.rectangle((x,y,min(x+step-1,r-1),min(y+step-1,b-1)),fill=alt)

@lru_cache(maxsize=32)
def night(mer,pose,lit=True):
    p=NIGHT.copy()
    if mer:p.alpha_composite(SEA[mer],(OX,OY))
    if lit:
        x,y,a=BR[pose];p.alpha_composite(a,(x,y))
    return p.convert('RGB')

def phase(n):return (n//4)%12,(n//5)%4

@lru_cache(maxsize=1)
def intro_layout():
    z=back(True).copy();d=ImageDraw.Draw(z)
    card(d,'#12192c',(45,46,595,652),'#50638b')
    txt(d,'CLIFF · EXTÉRIEUR',63,60,19,'mono',B)
    txt(d,'GUILDE DESTINY  /  0.7.7',643,170,22,'mono',G)
    txt(d,'Comptoirs',636,209,72,'title');txt(d,'& falaise',636,290,72,'title')
    d.line((642,391,1203,391),fill='#53617c',width=2)
    txt(d,'Huit orientations de comptoir',643,420,25,'bold','#f1dfb7')
    txt(d,'Deux braseros de Grodoudou à la porte',643,464,22,'sans',M)
    foot(d,'APERÇU VIDÉO · PLANS DESTINY','MOBILIER + EXTÉRIEUR');return z

def intro(n):
    z=intro_layout().copy();fit(z,night(*phase(n)),(64,98,576,635),1);return z

@lru_cache(maxsize=8)
def directions(selected):
    z,d=head('01 / COMPTOIRS','Huit orientations','Le même comptoir à cloche, vu de face, de dos, de profil et en diagonale.')
    for j,v in enumerate(I):
        x,y=44+174*(j%4),153+242*(j//4);active=j==selected
        card(d,'#443628' if active else '#263026',(x,y,x+163,y+227),'#ecbd81' if active else '#506450',9)
        txt(d,v['flèche'],x+12,y+9,28,'sans',G if active else M)
        f=fit(z,SPR[j],(x+7,y+45,x+158,y+174),1.62)
        txt(d,v['direction'],x+81,y+179,18,'bold',anchor='ma');txt(d,v['nom'],x+81,y+205,15,'sans',G if active else M,anchor='ma')
    card(d,'#26241e',(753,153,1235,622),'#745b39');txt(d,'SPRITE AGRANDI',772,170,19,'mono',G)
    checker(d,(773,210,1216,523),'#302b23','#373126',12);fit(z,SPR[selected],(780,214,1208,519),3)
    v=I[selected];txt(d,v['direction'],774,541,28,'bold');txt(d,f"{v['nom']} · {v['w']} × {v['h']} px",776,583,19,'sans',M)
    foot(d,'NOYER · PIERRE MATE · CLOCHE EN LAITON','8 SPRITES PNG');return z

def load_room(n,room,v,coords):
    f=W/f'Video-{n}.png'
    if f.is_file():return Image.open(f).convert('RGB')
    q=base();r=next(x for x in q['rooms'] if x['label']==room)
    return plan_frame(r,q,SPR[v],coords).convert('RGB')

@lru_cache(maxsize=3)
def roomshot(i):
    n,room,idx=[('accueil','Accueil',0),('refectoire','Réfectoire',5),('cuisine','Cuisine',1)][i];v=I[idx];name=v['direction']
    place=next(x['haut_gauche'] for x in EX if x['salle']==room and x['direction']==name);p=load_room(n,room,idx,place)
    z,d=head('02 / MISE EN SITUATION',room,f'Exemple de pose · {name} ({v["nom"].lower()})')
    card(d,'#1e2240',(44,148,725,648),'#5e616f');card(d,'#26251d',(741,148,1235,648),'#745b39')
    fit(z,p,(57,163,712,632))
    txt(d,'DÉTAIL DU COMPTOIR',757,164,19,'mono',G)
    cx=place[0]+v['w']//2;cy=place[1]+v['h']//2;crop=p.crop((cx-93,cy-76,cx+93,cy+72));fit(z,crop,(754,208,1221,631),2.5)
    foot(d,'SUR LE PARQUET D’ORIGINE',f'{i+1} / 3 SALLES');return z

@lru_cache(maxsize=1)
def compare_layout():
    z,d=head('03 / FALAISE','De jour, de nuit','La même falaise de Destiny. Seuls les braseros s’allument à la nuit tombée.',True)
    card(d,'#253448',(44,147,628,649),'#587790');card(d,'#171c34',(652,147,1235,649),'#52668c')
    txt(d,'JOUR · BRASEROS ÉTEINTS',61,159,18,'mono','#e7edf2');txt(d,'NUIT · BRASEROS ALLUMÉS',671,159,18,'mono','#e5dcfe')
    fit(z,DAY,(57,184,615,642));foot(d,'EXTÉRIEUR · CLIFF', 'ACCUEIL → PASSAGES → FALAISE');return z

def compare(n):
    z=compare_layout().copy();fit(z,night(*phase(n)),(665,184,1222,642));return z

@lru_cache(maxsize=2)
def close_layout(lit=True):
    z,d=head('04 / GROS PLAN','Les braseros de Grodoudou',None,True)
    card(d,'#17192b',(44,120,1235,648),'#53607e')
    tag='NUIT · AVEC BRASEROS' if lit else 'NUIT · SANS BRASEROS';label(d,tag,925 if lit else 924,51,True)
    foot(d,'DEVANT LA PORTE · DEHORS UNIQUEMENT','4 POSES · 6 IMAGES/S');return z

def closeup(n):
    lit=n>=36;z=close_layout(lit).copy();s=night(*phase(n),lit).crop((104,199,376,324));fit(z,s,(58,123,1222,645),4);return z

PARTS=[(84,intro),(168,lambda n:directions(n//21)),(84,lambda n:roomshot(0)),(84,lambda n:roomshot(1)),(84,lambda n:roomshot(2)),(144,compare),(204,closeup)]

def main():
    tmp=OUT.with_suffix('.tmp.mp4');W.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{NW}x{NH}','-r',str(FPS),'-i','pipe:0','-an','-vf','scale=iw:ih:out_color_matrix=bt709:out_range=tv,format=yuv420p','-c:v','libx264','-profile:v','high','-level','4.0','-threads','4','-preset','fast','-crf','18','-g','60','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart','-metadata','title=Destiny — Comptoirs & falaise',str(tmp)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for j,(total,draw) in enumerate(PARTS):
            prev=None;last=None
            for n in range(total):
                image=draw(n)
                if n==0 or (j==6 and n==75):image.save(W/f'Film-verif-{j}-{n}.png')
                if image is not prev:last=image.tobytes();prev=image
                p.stdin.write(last)
    finally:
        p.stdin.close()
        if p.wait():raise SystemExit('FFmpeg : échec de l’encodage')
    tmp.replace(OUT);print(f'{OUT.name} · {sum(length for length,_ in PARTS)/FPS:g} s · {OUT.stat().st_size:,} octets')

if __name__=='__main__':main()
