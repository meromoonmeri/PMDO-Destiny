#!/usr/bin/env python3
"""Export the independent PNG layers as a standard downloadable H.264 preview."""
from pathlib import Path
from functools import lru_cache
import json,subprocess
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
TMP=Path.home()/'.cache/ombre-ciel-cliff';TMP.mkdir(exist_ok=True)
REP=json.loads((ROOT/'Releve-Cliff-R2.json').read_text());LAY=REP['couches'];PAD=-REP['nuages_origine_px'][0]
OUT=ROOT/'Falaise-Destiny-Ombre-et-Lune.mp4';POSTER=ROOT/'Falaise-Destiny-Jour-Nuit.png'
SIZE=(1920,1080);FPS=30;NN=Image.Resampling.NEAREST
BASE='#101a21';PAPER='#f1e8d5';GOLD='#f0c482';MIST='#adc1bc';LINE='#344c52';DAY='#c9d888';NIGHT='#a7c0e8'
FONTS={'t':'DejaVuSerif.ttf','s':'DejaVuSans.ttf','b':'DejaVuSans-Bold.ttf','m':'DejaVuSansMono.ttf'}

@lru_cache(maxsize=40)
def font(s,k):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/'+FONTS[k],s)
def text(d,s,x,y,n,k='s',fill=PAPER,anchor='lt'):d.text((x,y),s,font=font(n,k),fill=fill,anchor=anchor)
def rule(d,x,y,x1,y1,c=LINE,w=1):d.line((x,y,x1,y1),fill=c,width=w)
def panel(d,box,c=LINE,w=2):d.rectangle(box,outline=c,width=w)

@lru_cache(maxsize=96)
def im(p):return Image.open(ROOT/p).convert('RGBA')


def frame(phase,sea=0,fire=0,high=0,low=0):
    meta=LAY[phase];layers=meta['calques'];z=im(meta['nu']).copy();x,y,w,h=meta['mer']['rect']
    sw=(sea%2)*w;sh=(sea//2)*h
    if sea:z.alpha_composite(im(meta['mer']['png']).crop((sw,sh,sw+w,sh+h)),(x,y))
    if high or low:
        bg=im(layers['ciel_fixe']).copy()
        if 'lune' in layers:bg.alpha_composite(im(layers['lune']))
        for key,dx in [('nuages_cime',high),('nuages_horizon',low)]:
            p=im(layers[key]);l=PAD+dx
            assert 0<=l<=PAD*2
            bg.alpha_composite(p.crop((l,0,l+480,152)))
        bg.alpha_composite(im(layers['cime_occlusion']));z.paste(bg,(0,0))
    z.alpha_composite(im(meta['feux'][fire if phase=='nuit' else 0]));return z.convert('RGB')


def pose(n):return (n//4%12,n//5%4,n//10,n*14//300)


def scale(p,z):return p.resize((p.width*z,p.height*z),NN)

@lru_cache(maxsize=8)
def plate(theme):
    # Restrained background, so the bright sky, grass and fire are the focus.
    a=Image.new('RGB',SIZE);r=ImageDraw.Draw(a)
    top=(19,29,38) if theme=='nuit' else (23,34,33)
    for y in range(SIZE[1]):
        v=(1-y/SIZE[1])**2;r.line((0,y,SIZE[0],y),fill=tuple(round(t+v*d) for t,d in zip(top,(7,11,17))))
    return a


def eyebrow(d,n,phase):
    rule(d,68,94,867,94)
    d.polygon([(68,59),(74,53),(80,59),(74,65)],fill=GOLD)
    text(d,'DESTINY  /  EXTÉRIEUR DE LA GUILDE',96,50,20,'m',GOLD)
    text(d,n+'  /  '+phase,866,50,20,'m',MIST,'rt')


def lead(d,phase,day):
    text(d,('Le plateau de jour' if day else 'Ombre, nuages et lune'),70,524,31,'s',DAY if day else NIGHT)
    rule(d,70,584,764,584)
    rows= [('Ombre prolongée sous les marches','Les petites marques vertes ont été nettoyées.'),('Nuages en deux plans','Au niveau de la cime et près de l’horizon marin.')] if day else [('Lune au repère rouge','À droite de la cime, au-dessus de la mer.'),('La mer et les braseros restent animés','Lumière recalculée sur le sol et la façade.')]
    for i,(h,s) in enumerate(rows):
        y=618+i*123
        text(d,f'0{i+1}',72,y+3,18,'m',GOLD);text(d,h,124,y,25,'b');text(d,s,124,y+44,22,'s',MIST)
        if i==0:rule(d,124,y+91,762,y+91)

@lru_cache(maxsize=2)
def overview_card(p):
    day=p=='jour';z=plate(p).copy();d=ImageDraw.Draw(z);eyebrow(d,'03' if day else '01','JOUR' if day else 'NUIT')
    text(d,'La falaise',65,274,99,'t');text(d,'de Destiny',65,382,100,'t')
    lead(d,p,day)
    rule(d,68,971,866,971)
    text(d,'PLAN ENTIER  /  480 × 520 PX',69,996,19,'m',MIST);text(d,'CLIFF 0.7.7',867,996,19,'m',GOLD,'rt')
    panel(d,(926,18,1890,1061));return z


def overview(p,n):
    z=overview_card(p).copy();z.paste(scale(frame(p,*pose(n)),2),(928,20));return z


CROP=(95,179,385,346);CMP_Y=291;CMP_X=(70,980);CMP_W=(CROP[2]-CROP[0])*3;CMP_H=(CROP[3]-CROP[1])*3
@lru_cache(maxsize=1)
def comparison_card():
    z=plate('nuit').copy();d=ImageDraw.Draw(z);eyebrow(d,'02','LE SEUIL')
    text(d,'L’ombre ne s’arrête plus sous les marches',67,139,59,'t')
    text(d,'Même vue, mêmes braseros. Seuls l’ombre et les points dans l’herbe changent dans ce détail.',70,221,25,'s',MIST)
    for i,x in enumerate(CMP_X):
        col='#91a8a5' if i==0 else GOLD
        panel(d,(x-2,CMP_Y-2,x+CMP_W+1,CMP_Y+CMP_H+1),LINE if i==0 else '#8b7754')
        text(d,['AVANT','CORRIGÉ'][i],x,CMP_Y+CMP_H+34,25,'m',col)
        text(d,['Ombre coupée net, herbe mouchetée','Contact sous les marches, pénombre progressive'][i],x,CMP_Y+CMP_H+79,22,'s',PAPER)
    rule(d,70,971,1850,971);text(d,'DÉTAIL DU SEUIL  /  MÊME ÉCHELLE',70,994,18,'m',MIST)
    text(d,'OMBRE RECONSTRUITE, PAS DE RECADRAGE DE LA CARTE',1849,994,18,'m',GOLD,'rt')
    return z

@lru_cache(maxsize=4)
def avant(k):return Image.open(TMP/f'Avant-nuit-{k}.png').convert('RGB')

def comparison(n):
    sea,f,a,b=pose(n);z=comparison_card().copy()
    for j,p in enumerate((avant(f),frame('nuit',sea,f,a,b))):z.paste(scale(p.crop(CROP),3),(CMP_X[j],CMP_Y))
    return z


SKYCROP=(0,0,480,350);SKY_X=439;SKY_Y=254
@lru_cache(maxsize=1)
def sky_card():
    z=plate('nuit').copy();d=ImageDraw.Draw(z);eyebrow(d,'04','LE CIEL')
    text(d,'La lune au-dessus de la mer',66,128,62,'t')
    text(d,'L’ancienne lune a été retirée. La nouvelle reste dégagée, à droite de l’arbre.',70,210,25,'s',MIST)
    panel(d,(SKY_X-2,SKY_Y-2,SKY_X+961,SKY_Y+701))
    x=1445;y=SKY_Y+234
    rule(d,SKY_X+962,y,x-11,y,GOLD);text(d,'EMPLACEMENT',x,y-10,19,'m',GOLD);text(d,'Repère de la capture',x,y+28,22,'s',PAPER)
    text(d,'1 / Nuages près de la cime',70,373,25,'s',NIGHT);text(d,'Derrière le feuillage.',70,416,22,'s',MIST)
    text(d,'2 / Bancs à l’horizon',70,521,25,'s',NIGHT);text(d,'Au ras de l’eau.',70,563,22,'s',MIST)
    rule(d,70,985,1850,985);text(d,'LUNE FIXE  /  NUAGES À DEUX VITESSES',70,1008,19,'m',MIST)
    return z


def sky_close(n):
    z=sky_card().copy();z.paste(scale(frame('nuit',*pose(n)).crop(SKYCROP),2),(SKY_X,SKY_Y));return z


SHOT=[('Falaise de nuit',156,lambda n:overview('nuit',n)),('Ombre avant / après',165,comparison),('Falaise de jour',138,lambda n:overview('jour',n)),('Lune et nuages',177,sky_close)]

def poster():
    z=Image.new('RGB',(1116,704),BASE);d=ImageDraw.Draw(z);text(d,'DESTINY  /  CLIFF',47,26,14,'m',GOLD)
    text(d,'La falaise, de jour et de nuit',46,59,36,'t');rule(d,47,111,1068,111)
    for x,p,c in [(47,'jour',DAY),(589,'nuit',NIGHT)]:
        text(d,p.upper(),x,127,15,'m',c);panel(d,(x-1,154,x+480,675),LINE,1);z.paste(frame(p),(x,155))
    z.save(POSTER,optimize=True)


def film():
    tmp=TMP/OUT.name;tags=['-f','rawvideo','-pix_fmt','rgb24','-s',f'{SIZE[0]}x{SIZE[1]}','-r',str(FPS),'-i','-']
    encoder=['-an','-c:v','libx264','-preset','fast','-threads','6','-crf','16','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart','-metadata','title=La falaise de Destiny — Ombre et lune']
    proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y',*tags,*encoder,str(tmp)],stdin=subprocess.PIPE)
    try:
        for i,(n,length,f) in enumerate(SHOT):
            previous=None;data=None
            for j in range(length):
                cur=pose(j)
                if cur!=previous:data=f(j).tobytes();previous=cur
                proc.stdin.write(data)
            print(f'Plan {i+1} : {n}, {length/FPS:.1f} s',flush=True)
        proc.stdin.close();code=proc.wait();assert code==0,code;tmp.replace(OUT)
    finally:
        if proc.poll() is None:proc.kill();proc.wait()
    print(OUT.name, sum(a[1] for a in SHOT)/FPS,'s,',OUT.stat().st_size,'octets')

if __name__=='__main__':poster();film()
