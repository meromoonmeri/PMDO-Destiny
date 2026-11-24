#!/usr/bin/env python3
"""Short MP4 demo from screenshots exported from the actual local positioning tool."""
from pathlib import Path
from functools import cache
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json
ROOT=Path(__file__).resolve().parents[1];W=Path.home()/'.cache/atelier-destiny-8-sens/Film';OUT=ROOT/'Immobilier-Destiny-Pose-8-Sens.mp4';FPS=30;P=(1280,720);N=Image.Resampling.NEAREST
BG='#19221e';GOLD='#edc78a';INK='#f4e8cf';LINE='#48534a';SUB='#bfcbbb';TUNE='#a5c2a5'
ORDER=['Down','DownRight','Right','UpRight','Up','UpLeft','Left','DownLeft'];ARROWS=['↓','↘','→','↗','↑','↖','←','↙']
FONTS={'s':'DejaVuSans.ttf','t':'DejaVuSerif.ttf','m':'DejaVuSansMono.ttf'}
@cache
def f(n,k):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/'+FONTS[k],n)
def t(d,txt,x,y,n=19,k='s',c=INK,an='lt'):d.text((x,y),txt,font=f(n,k),fill=c,anchor=an)
def l(d,x,y,r,b,c=LINE):d.line((x,y,r,b),fill=c,width=1)
def box(d,rect,c='#30392f',outline=LINE,r=11):d.rounded_rectangle(rect,r,fill=c,outline=outline)
@cache
def pic(n):return Image.open(W/(n+'.png')).convert('RGB')
def fit(b,p,x,y,w,h):
    s=min(w/p.width,h/p.height);z=p.resize((int(p.width*s),int(p.height*s)),N);b.paste(z,(x+(w-z.width)//2,y+(h-z.height)//2))
def base(i,title,sub):
    z=Image.new('RGB',P,BG);d=ImageDraw.Draw(z)
    t(d,'✦  ATELIER DE LA GUILDE / DESTINY',40,22,14,'m',GOLD);t(d,i,1240,22,14,'m',SUB,'rt');l(d,40,46,1240,46)
    t(d,title,39,63,44,'t');t(d,sub,41,120,17,'s',SUB);l(d,40,664,1240,664);t(d,'1 TUILE = 8 PX   /   PIVOT CONSERVÉ',40,684,12,'m',SUB);t(d,'1 108 ENTRÉES · 8 864 VUES',1240,684,12,'m',GOLD,'rt')
    return z,d

@cache
def spin(i):
    z,d=base('01 / HUIT SENS','Tourner un meuble déjà posé','Le bureau change d’angle. Sa croix d’ancrage reste sur la même case.')
    box(d,(40,155,914,646));fit(z,pic(f'Bibliotheque-{i}'),48,165,852,474)
    box(d,(931,155,1240,646));t(d,'BIBLIOTHÈQUE',951,175,14,'m',GOLD);t(d,'Bureau aux parchemins',951,211,22,'t');fit(z,pic(f'Sprite-{i}'),944,237,280,183)
    t(d,ORDER[i],1084,434,26,'m',GOLD,'mt');l(d,952,475,1219,475)
    for j,(x,y) in enumerate([(1086,587),(1141,587),(1141,548),(1141,510),(1086,510),(1031,510),(1031,548),(1031,587)]):
        box(d,(x-22,y-16,x+22,y+16),'#635039' if j==i else '#3a473b',GOLD if j==i else LINE,5);t(d,ARROWS[j],x,y-9,19,'s',GOLD if j==i else SUB,'mt')
    return z

@cache
def mirror(i):
    z,d=base('02 / LE MIROIR','Retourner gauche-droite','Même dessin retourné autour de la croix, sans sauter d’une case.')
    for slot,(x,n,label) in enumerate([(40,'Bibliotheque-1','DOWNRIGHT'),(648,'Bibliotheque-Miroir','DOWNRIGHT · MIROIR')]):
        box(d,(x,160,x+592,641),outline=GOLD if slot==i else LINE);fit(z,pic(n).crop((95,125,331,277)),x+17,183,558,409);t(d,label,x+19,609,16,'m',GOLD if slot==i else SUB)
    return z

@cache
def examples(i):
    z,d=base('03 / EN SALLE','De la banque au plan','Choisis un objet, clique sur Poser, puis oriente-le sur la grille.')
    for x,scene,label,direction in [(40,'Refectoire-Nuit','RÉFECTOIRE','Comptoir natif · DownLeft'),(648,'Etendard-Accueil','ACCUEIL','Étendard · UpRight')]:
        box(d,(x,160,x+592,640));t(d,label,x+18,179,14,'m',GOLD);fit(z,pic(scene),x+11,211,568,382);t(d,direction,x+19,607,16,'s',SUB)
    return z

SHOTS=[(240,lambda n:spin((n//30)%8)),(150,lambda n:mirror((n//48)%2)),(150,lambda n:examples(0))]

def video():
    out=W/OUT.name;cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','16','-threads','6','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n,s in SHOTS:
            b=None;dat=None
            for k in range(n):
                v=s(k)
                if v is not b:b=v;dat=b.tobytes()
                p.stdin.write(dat)
        p.stdin.close();assert p.wait()==0;out.replace(OUT)
    finally:
        if p.poll() is None:p.kill();p.wait()
    spin(1).save(ROOT/'Pose-DownRight.png',optimize=True)
    print('Vidéo de pose 18 s :',OUT.stat().st_size,'octets')
if __name__=='__main__':video()
