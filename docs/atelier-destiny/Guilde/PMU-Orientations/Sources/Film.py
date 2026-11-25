#!/usr/bin/env python3
"""Film and printable proof plate. Every sprite comes from the delivered PNG folders."""
from functools import lru_cache
from math import ceil, floor, pi, cos, sin
from pathlib import Path
import json
import subprocess
import os
import argparse
from PIL import Image, ImageDraw, ImageFont
from Produire import ROOT,W

K=W/'Kit';DX=json.loads((K/'Index-PMU-8.json').read_text());BY={o['repere']:o for o in DX['objets']}
DIR=DX['projection']['ordre'];FRE=DX['projection']['libelles'];ARR=DX['projection']['fleches']
FILE=ROOT/'Destiny-PMU-Les-huit-orientations.mp4';PLANCHE=ROOT/'Planche-PMU-Huit-orientations.png'
A='Creation_Pupitre-aux-cartes';B='Creation_Chariot-a-the';C='Creation_Grainotheque';D='Creation_Horloge-lunaire'
NEW=(A,B,C,D)
WIDE,HIGH=1280,720;FPS=30
BG='#191824';BG2='#251f2c'; PANEL='#262333';PANE2='#2e2839';GOLD='#e8bc7a'; EDGE='#594855';MUTED='#c1b3ab';INK='#f4e9d6';OLIVE='#acbd93';BRONZE='#896449';LINE='#403546';CREAM='#fae0b5'
STYLES={
 's':'DejaVuSans.ttf','b':'DejaVuSans-Bold.ttf','m':'DejaVuSansMono.ttf','title':'DejaVuSerif.ttf','em':'DejaVuSerif-Italic.ttf'}

@lru_cache(maxsize=70)
def font(n,k):
    name=STYLES[k];p=Path('/usr/share/fonts/truetype/dejavu')/name
    if not p.exists():p=p.with_name('DejaVuSerif.ttf') if k=='em' else p
    return ImageFont.truetype(str(p),n)

def txt(d,x,y,st,n=20,k='s',color=INK,anc='lt'):
    d.text((x,y),st,font=font(n,k),fill=color,anchor=anc)

def paragraph(d,x,y,text,width,n=17,step=26,cl=MUTED):
    parts=[];line=''
    for word in text.split():
        test=f'{line} {word}'.strip()
        if line and d.textlength(test,font=font(n,'s'))>width:parts.append(line);line=word
        else:line=test
    if line:parts.append(line)
    for j,ln in enumerate(parts):txt(d,x,y+j*step,ln,n,'s',cl)
    return y+step*len(parts)

def panel(d,r,fill=PANEL,edge=EDGE,rad=13):d.rounded_rectangle(r,rad,fill=fill,outline=edge,width=1)

def rule(d,x0,y0,x1,y1,col=LINE):d.line((x0,y0,x1,y1),fill=col,width=1)

def pill(d,x,y,st,col=CREAM,fill='#3b2f3a'):
    w=ceil(d.textlength(st,font=font(12,'m')))+24;panel(d,(x,y,x+w,y+26),fill,BRONZE,11);txt(d,x+w//2,y+7,st,12,'m',col,'mt');return w

def checker(d,r,s=15,light=False):
    l,t,ri,b=r;d.rectangle(r,fill='#342c3c' if light else '#2b2635')
    for y in range(t,b,s):
        for x in range(l,ri,s):
            if ((x-l)//s+(y-t)//s)%2:
                d.rectangle((x,y,min(ri,x+s-1),min(b,y+s-1)),fill='#3a3243' if light else '#302a3b')

def bg(sz=(WIDE,HIGH)):
    z=Image.new('RGB',sz,BG);d=ImageDraw.Draw(z);w,h=sz
    for k in range(26):
        v=BG2 if k%4==0 else '#211d2a';x=w-340+k*21;rule(d,x,6,x+375,381,v)
    return z,d

def top(d,chapter):
    txt(d,45,25,'◈  DESTINY',14,'m',GOLD);txt(d,160,25,'/  ARCHIVES DE LA GUILDE',13,'m',MUTED);txt(d,1235,25,chapter,13,'m',GOLD,'rt');rule(d,44,48,1236,48,EDGE)

def foot(d,left,right):
    rule(d,44,665,1236,665,EDGE);txt(d,45,680,left,13,'m',MUTED);txt(d,1234,680,right,13,'m',GOLD,'rt')

def header(chapter,title,sub):
    z,d=bg();top(d,chapter);txt(d,44,65,title,42,'title',INK);txt(d,46,124,sub,18,'s',MUTED);return z,d

@lru_cache(maxsize=350)
def sprite(key,i):return Image.open(K/BY[key]['vues'][i]['fichier']).convert('RGBA')

@lru_cache(maxsize=45)
def room(key):return Image.open(W/'Scenes'/(key+'.png')).convert('RGB')

def put(z,key,i,bounds,max_scale=4,mark=False):
    l,t,r,b=bounds;ob=BY[key];a=ob['atlas'];rw,rh=a['cellule'];px,py=a['pivot_case'];ss=ob['vues'][i];q=sprite(key,i)
    fac=min((r-l)/rw,(b-t)/rh,max_scale)
    hx,hy=(l+r)/2-rw*fac/2+px*fac,(t+b)/2-rh*fac/2+py*fac
    if mark:
        d=ImageDraw.Draw(z);rule(d,l+6,round(hy),r-6,round(hy),'#5a4451')
        d.polygon([(hx-3,hy),(hx,hy-3),(hx+3,hy),(hx,hy+3)],fill=GOLD)
    im=q.resize((max(1,round(q.width*fac)),max(1,round(q.height*fac))),Image.Resampling.NEAREST)
    x=round(hx-ss['pivot'][0]*fac);y=round(hy-ss['pivot'][1]*fac);z.paste(im,(x,y),im)


def fit(z,q,box,f=4):
    x,y,r,b=box;g=min((r-x)/q.width,(b-y)/q.height,f);n=q.resize((int(q.width*g),int(q.height*g)),Image.Resampling.NEAREST);z.paste(n,(x+(r-x-n.width)//2,y+(b-y-n.height)//2),n if n.mode=='RGBA' else None)


def draw_metrics(d,y=544):
    labels=[('346','OBJETS PMU'),('4','CRÉATIONS INÉDITES'),('10','ANCIENS MODÈLES BONUS'),('2 880','PNG TRANSPARENTS')]
    for j,(n,label) in enumerate(labels):
        x=45+j*300;panel(d,(x,y,x+288,y+89),PANE2,EDGE,10);txt(d,x+17,y+11,n,39,'title',GOLD);txt(d,x+20,y+66,label,12,'m',MUTED)

@lru_cache(maxsize=12)
def intro(i):
    z,d=bg();top(d,'01 / LA BANQUE COMPLÈTE');txt(d,47,91,'COFFRET GRAPHIQUE · 0.7.7',14,'m',GOLD)
    txt(d,43,125,'Objets PMU',69,'title');txt(d,44,206,'dans les huit sens',62,'em',GOLD)
    rule(d,47,318,594,318,EDGE);txt(d,47,348,'Face, profils, diagonales et dos.',23,'s',INK)
    txt(d,47,387,'Un PNG à taille native pour chaque orientation.',18,'s',MUTED)
    panel(d,(693,79,1234,515),'#282234',EDGE);checker(d,(708,114,1221,460),20)
    txt(d,715,89,'DEUX NOUVEAUTÉS · PIVOTS FIXES',12,'m',GOLD)
    rule(d,965,130,965,442,EDGE)
    put(z,A,i,(725,153,955,425),3.6,True);put(z,D,(i+1)%8,(973,133,1205,438),3.8,True)
    txt(d,772,477,'PUPITRE',15,'m',CREAM);txt(d,1046,477,'HORLOGE',15,'m',CREAM)
    draw_metrics(d);foot(d,'BANK PMU · DESTINY 0.7.7'.replace('BANK','BANQUE'),'8 ORIENTATIONS · APERÇU D’UNE SÉLECTION');return z

@lru_cache(maxsize=10)
def spotlight(i):
    z,d=header('02 / LE TOUR COMPLET','Une bibliothèque, huit directions','La texture des livres reste sur la face ; le dos et les côtés sont reconstruits.')
    panel(d,(44,171,587,642));checker(d,(59,209,572,554),16,True)
    txt(d,61,184,'MOB_017  /  BOIS DE NOYER',13,'m',GOLD)
    put(z,'Mob_017',i,(99,214,529,546),3.75,True)
    txt(d,63,573,ARR[i]+'  '+DIR[i],31,'b',INK);txt(d,65,613,FRE[i].upper()+(' · SPRITE SOURCE' if not i else ' · VUE RECONSTITUÉE'),13,'m',GOLD)
    for j in range(8):
        x=607+156*(j%4);y=171+239*(j//4)
        panel(d,(x,y,x+146,y+230),'#463438' if j==i else PANEL,GOLD if j==i else EDGE,9)
        txt(d,x+11,y+11,ARR[j],23,'s',GOLD);txt(d,x+134,y+15,f'{j+1:02d}',12,'m',MUTED,'rt')
        put(z,'Mob_017',j,(x+10,y+45,x+136,y+173),1.5)
        txt(d,x+73,y+185,DIR[j],14,'b',INK,'mt');txt(d,x+73,y+209,FRE[j],11,'s',MUTED,'mt')
    foot(d,'PIVOT COMMUN · NOUVELLES VUES À TAILLE NATIVE','DU SUD AU NORD-OUEST');return z


def rotation_strip(z,d,i,y=602,l=44,r=1236):
    cw=(r-l)/8
    for j in range(8):
        x=round(l+j*cw);xp=round(l+(j+1)*cw)-4
        panel(d,(x,y,xp,y+42),'#473536' if i==j else '#2a2634',GOLD if i==j else EDGE,7)
        txt(d,x+12,y+8,ARR[j],19,'s',GOLD if j==i else MUTED);txt(d,(x+xp)//2+8,y+14,DIR[j],14,'m',CREAM if j==i else MUTED,'mt')

@lru_cache(maxsize=24)
def category(k,i):
    if k==0:
        z,d=header('03 / LA BANQUE PMU','Du mobilier et des rangements','Les bancs, les plateaux et les coffres changent de perspective sans basculer.')
        keys=('Mob_030','Mob_038','coffre_bois_bleu');titles=('Banc à socles de pierre','Grande table de bois','Coffre bleu');labels=('MOBILIER · MOB_030','MOBILIER · MOB_038','GUILDE · COFFRE')
    else:
        z,d=header('04 / LA BANQUE PMU','Tapis, étendards et décors','Un motif plat tourne sur le sol. Les objets debout gardent leur volume.')
        keys=('tapis_bleu','DecA_177','Mob_035');titles=('Tapis bleu','Étendard orange','Palmier en pot');labels=('GUILDE · SURFACE PLANE','DÉCOR · DECA_177','MOBILIER · MOB_035')
    for j,(key,t,s) in enumerate(zip(keys,titles,labels)):
        x=44+j*400
        panel(d,(x,168,x+388,590));txt(d,x+15,182,s,12,'m',GOLD)
        checker(d,(x+14,207,x+373,521),15)
        put(z,key,i,(x+21,227,x+368,502),3.4,mark=key!='tapis_bleu')
        txt(d,x+16,545,t,23,'title')
    rotation_strip(z,d,i)
    foot(d,'UNE SÉLECTION DE LA BANQUE · 346 SOURCES DANS LE COFFRET','VUE ACTIVE : '+DIR[i].upper());return z

@lru_cache(maxsize=10)
def creations(i):
    z,d=header('05 / COLLECTION INÉDITE','Quatre nouvelles créations','Études générées et reprises au pixel, puis déclinées dans les huit sens.')
    for j,(key,line) in enumerate(zip(NEW,['Carte, boussole et noyer','Théière et plateau bas','Six tiroirs et graines','Laiton et croissant de lune'])):
        x=44+300*j
        panel(d,(x,169,x+288,590),PANEL,BRONZE,13);txt(d,x+14,185,'0'+str(j+1)+' / CRÉATION',12,'m',GOLD)
        checker(d,(x+11,213,x+277,494),17,True)
        put(z,key,i,(x+20,224,x+268,484),3.25,True)
        txt(d,x+14,519,BY[key]['nom'],24,'title');txt(d,x+15,556,line,14,'s',MUTED)
    rotation_strip(z,d,i)
    foot(d,'4 NOUVEAUX MODÈLES · 32 PNG','LE PIVOT RESTE AU MÊME ENDROIT');return z

@lru_cache(maxsize=26)
def space(scene,i,night=False):
    isbib=scene=='Bibliotheque';lab='Bibliothèque' if isbib else 'Réfectoire'
    lead='Le pupitre tourne sur le tapis ; l’horloge reste près des rayonnages.' if isbib else 'Le chariot à thé et la grainothèque prennent place près des tables.'
    z,d=header('06 / MISE EN PLACE','Dans la '+lab if isbib else 'Au '+lab,lead)
    panel(d,(44,166,803,647),'#1d1b30',EDGE);pic=room(f'{scene}-{"Nuit-" if night else ""}{i}')
    fit(z,pic,(51,172,796,641))
    panel(d,(824,166,1236,647),PANEL,BRONZE);txt(d,843,183,'DÉTAIL / '+('PUPITRE' if isbib else 'CHARIOT'),13,'m',GOLD)
    txt(d,1217,183,'NUIT' if night else 'JOUR',13,'m',OLIVE if night else CREAM,'rt')
    if isbib:cut=pic.crop((92,118,208,250));bound=(841,207,1218,502)
    else:cut=pic.crop((278,188,400,306));bound=(841,207,1218,502)
    panel(d,bound,'#28243a',EDGE);fit(z,cut,(850,214,1209,495))
    j=1 if night else i;txt(d,844,526,ARR[j]+'  '+DIR[j],27,'b');txt(d,845,565,FRE[j].upper(),13,'m',GOLD)
    txt(d,845,602,'Exemple de placement',16,'s',MUTED)
    foot(d,'MOTEUR D’APERÇU DESTINY · PASSAGES CONSERVÉS','LE JEU N’A PAS ÉTÉ MODIFIÉ');return z

@lru_cache(maxsize=2)
def ending():
    z,d=header('07 / À EMPORTER','Le coffret des huit orientations','Les PNG à taille native, les pivots et un catalogue à ouvrir hors ligne.')
    panel(d,(44,164,1236,531),PANEL,BRONZE,15);rule(d,831,187,831,510,EDGE)
    txt(d,67,187,'EXEMPLE D’ATLAS / PUPITRE AUX CARTES',15,'m',GOLD)
    for i in range(8):
        x=65+(i%4)*191;y=221+(i//4)*148
        panel(d,(x,y,x+177,y+136),PANE2,EDGE,8);txt(d,x+12,y+10,ARR[i]+'  '+DIR[i],14,'m',MUTED)
        put(z,A,i,(x+9,y+31,x+167,y+129),1.55,True)
    for j,(big,small) in enumerate([('2 880 PNG','Un fichier par angle'),('360 atlas','Huit cases calées par objet'),('Catalogue','Recherche, profils et dos')]):
        y=205+j*100;txt(d,860,y,big,35,'title',GOLD);txt(d,861,y+52,small,17,'s',MUTED)
    txt(d,45,574,'Décompresse le ZIP et ouvre Catalogue.html.',27,'title',INK)
    txt(d,47,619,'Aucune installation dans le jeu. Les PNG sont prêts à être utilisés dans ton propre projet.',16,'s',MUTED)
    foot(d,'COFFRET GRAPHIQUE DESTINY','PNG · ATLAS · INDEX CSV ET JSON');return z


def planche():
    order=[A,B,C,D,'Mob_017','coffre_bois_bleu'];baseX=290;cw=152;ch=131
    z,d=bg((1545,1110));txt(d,43,32,'◈  DESTINY / ARCHIVES DE LA GUILDE',15,'m',GOLD);txt(d,1502,32,'PLANCHE Nº 08 · 0.7.7',14,'m',GOLD,'rt')
    rule(d,43,57,1502,57,EDGE)
    txt(d,41,77,'Les objets dans les huit sens',53,'title');txt(d,44,149,'Une sélection : quatre créations inédites et deux références de la banque PMU.',21,'s',MUTED)
    pill(d,1181,121,'360 MODÈLES DANS LE COFFRET');pill(d,1181,155,'8 PNG PAR MODÈLE')
    rule(d,43,187,1502,187,EDGE)
    for i,di in enumerate(DIR):
        x=baseX+i*cw+71;txt(d,x,199,ARR[i],25,'s',GOLD,'mt');txt(d,x,231,di,16,'b',INK,'mt')
        txt(d,x,254,'Vue source' if i==0 else FRE[i],12,'s',MUTED,'mt')
    for j,key in enumerate(order):
        yy=280+j*ch;panel(d,(44,yy,1503,yy+ch-7),'#282331',EDGE,10)
        numer=f'{j+1:02d} / '+('CRÉATION' if j<4 else 'BANQUE PMU');txt(d,59,yy+16,numer,12,'m',GOLD)
        title={'Mob_017':'Bibliothèque en noyer','coffre_bois_bleu':'Coffre bleu'}.get(key,BY[key]['nom']);f=23
        while d.textlength(title,font=font(f,'title'))>219:f-=1
        txt(d,57,yy+40,title,f,'title')
        txt(d,58,yy+84,('MODÈLE INÉDIT' if j<4 else BY[key]['repere'].upper()),12,'m',MUTED)
        for i in range(8):
            x=baseX+cw*i;panel(d,(x,yy+7,x+cw-10,yy+ch-13),'#332b3d' if i==0 else '#2b2736',BRONZE if i==0 else '#423b49',6)
            put(z,key,i,(x+7,yy+11,x+cw-17,yy+ch-17),1.75,True)
    rule(d,44,1077,1501,1077,EDGE);txt(d,44,1086,'PNG TRANSPARENTS À 1×  /  PIVOTS DANS L’INDEX',13,'m',MUTED);txt(d,1502,1086,'UNE SÉLECTION · PAS LA BANQUE ENTIÈRE',13,'m',GOLD,'rt')
    z.save(PLANCHE,optimize=True);return z

SECTIONS=[(126,'Intro'),(240,'Bibliothèque en noyer : les huit angles'),(168,'Mobilier et rangements'),(168,'Tapis et décors'),(240,'Créations inédites'),(216,'En place dans la Bibliothèque'),(168,'En place au Réfectoire'),(126,'Contenu du coffret')]

def frame(j,n):
    if j==0:return intro(n//32)
    if j==1:return spotlight(n//30)
    if j==2:return category(0,n//21)
    if j==3:return category(1,n//21)
    if j==4:return creations(n//30)
    if j==5:return space('Bibliotheque',n//27)
    if j==6:return space('Refectoire',n//12) if n<96 else space('Refectoire',(n//3)%4,True)
    return ending()


def film():
    options=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{WIDE}x{HIGH}','-r',str(FPS),'-i','-','-an','-vcodec','libx264','-preset','fast','-threads','7','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(FILE)]
    proc=subprocess.Popen(options,stdin=subprocess.PIPE)
    try:
        for j,(frames,title) in enumerate(SECTIONS):
            current=None;bb=None
            for n in range(frames):
                im=frame(j,n)
                if im is not current:bb=im.tobytes();current=im
                proc.stdin.write(bb)
            print(f'{j+1:02d} · {title}',flush=True)
        proc.stdin.close();res=proc.wait();assert res==0,res
    finally:
        if proc.poll() is None:proc.kill();proc.wait()
    duration=sum(fr for fr,l in SECTIONS)/FPS
    print(f'{FILE.name} · {duration:.1f} s, {FILE.stat().st_size:,} octets',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--planche-seule',action='store_true');args=parser.parse_args();planche()
    if not args.planche_seule:film()
