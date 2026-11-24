#!/usr/bin/env python3
"""A legible MP4 preview (no external player plugins or web page needed)."""
from Construire import *
from PIL import ImageFont
from functools import lru_cache
import subprocess
from math import ceil

FILE=ROOT/'Refectoire-EoS-Cheminee.mp4'; PRE=ROOT/'Refectoire-EoS-Apercu.png';FPS=30;SIZE=(1280,720)
INK='#f8ead3';GOLD='#eabf83';LOW='#bcafb1';LINE='#514353';MID='#251e2d';BG='#171421';ASH='#1a1726';BLUE='#1a182e';WOOD='#2f262f';COLD='#a0b2d2'
FONTS={'s':'DejaVuSans.ttf','b':'DejaVuSans-Bold.ttf','m':'DejaVuSansMono.ttf','t':'DejaVuSerif.ttf'}

@lru_cache(maxsize=64)
def font(n,q):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/'+FONTS[q],n)
def text(d,q,x,y,n=19,k='s',c=INK,an='lt'):d.text((x,y),q,font=font(n,k),fill=c,anchor=an)
def line(d,pts,c=LINE,w=1):d.line(pts,fill=c,width=w)
def panel(d,box,fill=MID,edge=LINE,rad=12):d.rounded_rectangle(box,rad,fill=fill,outline=edge,width=1)
def strap(d,msg,x,y,cl=GOLD):
    w=ceil(d.textlength(msg,font=font(12,'m')))+23;panel(d,(x,y,x+w,y+26),WOOD,'#735647',10);text(d,msg,x+w//2,y+7,12,'m',cl,'mt')
def header(mark,title,sub):
    z=Image.new('RGB',SIZE,BG);d=ImageDraw.Draw(z)
    for j in range(32):
        q=841+j*17;d.line((q,0,q+306,306),fill='#211a29' if j%4 else '#282032',width=1)
    text(d,'◇  GUILDE DE GRODOUDOU / DESTINY',43,23,14,'m',GOLD);text(d,mark,1237,23,13,'m',LOW,'rt');line(d,(43,47,1237,47))
    text(d,title,42,66,45,'t');text(d,sub,45,128,17,'s',LOW)
    return z,d

def ends(d,left,right):
    line(d,(43,660,1237,660));text(d,left,43,676,13,'m',LOW);text(d,right,1237,676,13,'m',GOLD,'rt')

def fit(z,im,box):
    x,y,r,b=box;s=min((r-x)/im.width,(b-y)/im.height);w,h=round(im.width*s),round(im.height*s);a=im.resize((w,h),Image.Resampling.NEAREST)
    z.paste(a,(x+(r-x-w)//2,y+(b-y-h)//2),a if a.mode=='RGBA' else None)

@lru_cache(maxsize=21)
def image(n):return Image.open(W/(n+'.png')).convert('RGB')

@lru_cache(maxsize=7)
def overview(i):
    z,d=header('01 / LE RÉFECTOIRE','Une cheminée entre les deux fenêtres','Dalles de pierre, manteau en chêne et foyer encastré dans la paroi du fond.')
    panel(d,(43,166,946,643),ASH);panel(d,(963,166,1237,643),MID,'#6d554e')
    fit(z,image(f'Jour-{i}').crop((67,51,504,307)),(45,175,944,636))
    strap(d,'JOUR',980,183)
    text(d,'Plan G01P06',980,231,29,'t',GOLD);text(d,'Explorateurs du Ciel',981,275,16,'s',LOW)
    line(d,(982,314,1218,314))
    for j,(n,col) in enumerate([('Fenêtres rondes',INK),('Table au centre',INK),('Fontaine à droite',INK),('Passage est libre',GOLD)]):
        y=338+j*52;text(d,'0'+str(j+1),982,y+2,12,'m',LOW);text(d,n,1013,y,17,'s',col)
    text(d,'1 CHEMINÉE · FEU ANIMÉ',980,608,12,'m',GOLD)
    ends(d,'RÉFECTOIRE · HABILLAGE BOIS DESTINY','PLAN NATIF 504 × 360 PX');return z

@lru_cache(maxsize=7)
def compare(i):
    z,d=header('02 / LE PLAN CONSERVÉ','Le même plan, habillé de bois','Les fenêtres, la table, la fontaine et l’accès à droite gardent leurs emplacements.')
    for x,im,cap,sub in [(43,refs()[0][i],'EXPLORATEURS DU CIEL','Référence G01P06A'),(648,image('Jour-'+str(i)),'RÉFECTOIRE RÉGÉNÉRÉ','Bois Destiny et foyer central')]:
        panel(d,(x,165,x+589,620),ASH,'#6c534d');text(d,cap,x+17,185,14,'m',GOLD);line(d,(x+17,210,x+572,210))
        fit(z,im.crop((65,47,504,318)),(x+12,218,x+578,580));text(d,sub,x+17,587,14,'s',LOW)
    ends(d,'COMPARAISON À LA MÊME ÉCHELLE · PAS DE SORTIE AJOUTÉE','G01P06A / JOUR');return z

@lru_cache(maxsize=8)
def detail(i):
    on=i>=0;tag=str(i) if on else 'Eteint';z,d=header('03 / LA MAÇONNERIE','Dalles, manteau de chêne et feu','Le conduit rejoint la traverse ; les flammes restent à l’intérieur de l’âtre.')
    panel(d,(43,167,785,641),ASH,'#746054');panel(d,(804,167,1237,641),MID)
    fit(z,image('Jour-'+tag).crop((172,74,331,191)),(52,173,775,635));strap(d,'ALLUMÉE' if on else 'ÉTEINTE',823,188)
    details=[('01','Conduit encastré','Dalles jointées jusqu’à la traverse.'),('02','Manteau en chêne','Une traverse de bois au-dessus de l’arc.'),('03','Âtre maçonné','Foyer animé et reflets sur le parquet.')]
    for j,(n,a,b) in enumerate(details):
        y=251+j*112;text(d,n,824,y,14,'m',GOLD);text(d,a,862,y-2,27,'t');text(d,b,862,y+40,15,'s',LOW)
        if j!=2:line(d,(825,y+82,1217,y+82))
    ends(d,'FLAMMES ET EAU EN QUATRE POSES','CALQUES INDÉPENDANTS');return z

@lru_cache(maxsize=8)
def night(i):
    z,d=header('04 / AMBIANCE NOCTURNE','Le réfectoire à la nuit tombée','Un reflet chaud sur le mur et les lames du parquet, sans masquer les fenêtres.')
    p=image('Nuit-'+str(i))
    panel(d,(43,166,852,643),BLUE);fit(z,p.crop((68,51,504,310)),(48,172,847,637))
    panel(d,(870,166,1237,643),MID,'#6d554e');text(d,'AU PLUS PRÈS DE L’ÂTRE',886,184,14,'m',GOLD)
    fit(z,p.crop((219,111,285,201)),(887,218,1220,593));text(d,'UNE SEULE CHEMINÉE',885,613,13,'m',LOW)
    ends(d,'DEUX AMBIANCES · JOUR ET NUIT','UNE VARIANTE GRAPHIQUE · JEU INCHANGÉ');return z


def poster():
    a=image('Jour-0').crop((67,51,504,309));shot(a.resize((a.width*3,a.height*3),Image.Resampling.NEAREST),PRE)


def film():
    cfg=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(FPS),'-i','-','-an','-c:v','libx264','-crf','16','-preset','fast','-threads','6','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(FILE)]
    p=subprocess.Popen(cfg,stdin=subprocess.PIPE)
    try:
        shots=[(overview,144),(compare,174),(detail,222),(night,198)]
        for f,len0 in shots:
            known={};
            for n in range(len0):
                i=(n//3)%4
                if f is detail and n<51:i=-1
                if i not in known:known[i]=f(i).tobytes()
                p.stdin.write(known[i]);
        p.stdin.close();assert p.wait()==0
    finally:
        if p.poll() is None:p.kill();p.wait()
    print(FILE.name, '24.6 s ·',FILE.stat().st_size,'octets')

if __name__=='__main__':poster();film()
