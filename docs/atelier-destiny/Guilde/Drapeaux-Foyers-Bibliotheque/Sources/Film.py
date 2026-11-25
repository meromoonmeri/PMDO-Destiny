#!/usr/bin/env python3
"""HD MP4: synchronized before/after on Cliff, 8 cloth projections and actual room planes."""
from Commun import *
import importlib.util,subprocess
from PIL import ImageDraw
from functools import lru_cache
sys.path.insert(0,str(OLD/'Sources'))
spec=importlib.util.spec_from_file_location('videostyle',OLD/'Sources/Film-mp4.py');style=importlib.util.module_from_spec(spec);spec.loader.exec_module(style)
head,txt,card,fit,foot,checker,label=style.head,style.txt,style.card,style.fit,style.foot,style.checker,style.label
GOLD,CREAM,M=style.G,style.C,style.M
FPS=30;SIZE=(1280,720);VIDEO=ROOT/'Destiny-Drapeaux-Foyers-Bibliotheque.mp4'
D=json.loads((ROOT/'Drapeaux/Index-Drapeaux.json').read_text())['variantes'];CL=json.loads((ROOT/'Cliff-lumiere/Releve-Lumiere.json').read_text());cliffs=[(q['x'],q['y'],Image.open(ROOT/q['png']).convert('RGBA')) for q in CL['poses']]
DS=[Image.open(ROOT/a['atlas']).convert('RGBA') for a in D]
BOOK_NAMES={'archives':'Archives miel','herbiers':'Herbiers mousse','atlas':'Atlas bleu'}

@lru_cache(maxsize=20)
def im(n):return Image.open(W/f'Video-{n}.png').convert('RGB')

@lru_cache(maxsize=32)
def cliff(k,f,new):
    if not new:return style.night(k,f)
    z=style.NIGHT.copy()
    if k:z.alpha_composite(style.SEA[k],(style.OX,style.OY))
    x,y,a=cliffs[f];z.alpha_composite(a,(x,y));return z.convert('RGB')

def pl(n):return (n//4)%12,(n//5)%4

@lru_cache(maxsize=1)
def cliff_card():
    z,d=head('01 / CLIFF','La lumière des braseros','Les flammes éclairent maintenant le sol, les racines, les marches et le bas de la façade.',True)
    card(d,'#151b2d',(42,150,630,640),'#556782');card(d,'#1b2337',(650,150,1238,640),'#aa8757')
    txt(d,'AVANT · HALO AU SOL',55,164,20,'mono','#cbd4ec');txt(d,'APRÈS · FAÇADE ET SOL',664,164,20,'mono',GOLD)
    foot(d,'MÊMES FLAMMES ET MÊME AMBIANCE','PAS DE LUEUR SUR LE CIEL NI LA MER');return z

def clip_compare(n):
    z=cliff_card().copy();k,f=pl(n)
    for j,x in enumerate((58,666)):
        u=cliff(k,f,bool(j)).crop((95,151,386,352));fit(z,u,(x,202,x+556,626),1.90)
    return z

@lru_cache(maxsize=1)
def night_card():
    z,d=head('01 / CLIFF','La falaise de nuit',None,True)
    card(d,'#17243b',(43,113,590,653),'#566984');card(d,'#1f2533',(612,113,1237,653),'#615b4f')
    txt(d,'LES DEUX BRASEROS',634,147,23,'mono',GOLD);txt(d,'À la porte de Destiny',630,196,42,'title')
    txt(d,'Les fenêtres basses, les marches',636,292,23,'sans',M)
    txt(d,'et les racines prennent des reflets chauds.',636,331,23,'sans',M)
    txt(d,'La cime reste dans la nuit.',636,404,23,'bold',CREAM)
    foot(d,'GRODOUDOU · 4 POSES ORIGINALES','CLIFF DESTINY 0.7.7');return z

def clip_full(n):
    z=night_card().copy();fit(z,cliff(*pl(n),True),(53,118,580,648),1);return z


def flag(i,k):
    a=D[i];w,h=a['w'],a['h'];x=k%3*w;y=k//3*h
    return DS[i].crop((x,y,x+w,y+h))

@lru_cache(maxsize=8)
def flagboard(i):
    z,d=head('02 / DRAPEAUX','L’étendard au gland','Huit orientations, du recto doré aux plis vus de profil ou de dos.')
    for n,a in enumerate(D):
        x=44+n%4*172;y=151+n//4*246;on=n==i
        card(d,'#443927' if on else '#233027',(x,y,x+160,y+229),'#d6b376' if on else '#526554',9)
        txt(d,a['flèche'],x+10,y+9,28,'sans',GOLD if on else M)
        fit(z,flag(n,0),(x+10,y+39,x+150,y+171),1.49)
        txt(d,a['direction'],x+80,y+181,17,'bold',anchor='ma');txt(d,a['nom'],x+80,y+207,16,'sans',GOLD if on else M,anchor='ma')
    card(d,'#242d26',(743,151,1235,626),'#647153');txt(d,'ORIENTATION AGRANDIE',762,167,19,'mono',GOLD)
    checker(d,(760,204,1218,536),'#2d362e','#333e33',12)
    txt(d,D[i]['direction'],761,551,32,'bold');txt(d,D[i]['nom'],763,595,18,'sans',M)
    foot(d,'HAMPE FIXE · TISSU ANIMÉ','8 ORIENTATIONS');return z

@lru_cache(maxsize=12)
def flagshot(i,f):
    z=flagboard(i).copy();fit(z,flag(i,f),(767,210,1208,529),3.5);return z

def clip_flags(n):return flagshot(n//24,(n*8//30)%6)

@lru_cache(maxsize=6)
def flags_in_room(k):
    z,d=head('02 / DRAPEAUX','En place dans l’Accueil','Deux essais en diagonale. Le trajet central entre les passages reste libre.')
    card(d,'#202441',(44,151,726,646),'#636c7d');card(d,'#242d27',(743,151,1236,646),'#536752')
    p=im('flag-'+str(k));fit(z,p,(53,165,715,633))
    txt(d,'DÉTAIL · AVANT DROIT',760,172,19,'mono',GOLD);q=p.crop((113,106,193,237));fit(z,q,(756,209,1221,631),3)
    foot(d,'EXEMPLES SUR LE PLAN NATIF','ACCUEIL DESTINY');return z

def clip_flagroom(n):return flags_in_room((n*8//30)%6)

@lru_cache(maxsize=5)
def foyer_card(k):
    p=im('foyer-off' if k<0 else 'foyer-'+str(k));z,d=head('03 / RÉFECTOIRE','Deux cheminées animées','Les deux foyers épousent les murs latéraux et laissent libre le passage est.',True)
    card(d,'#171c36',(44,148,726,645),'#586582');card(d,'#23252d',(743,148,1235,645),'#766043')
    fit(z,p,(55,160,715,632))
    txt(d,'FOYER OUEST',758,162,18,'mono',GOLD);txt(d,'FOYER EST',758,396,18,'mono',GOLD)
    fit(z,p.crop((62,79,155,178)),(758,191,1221,377),1.85)
    fit(z,p.crop((424,78,517,178)),(758,424,1221,624),1.95)
    label(d,'ÉTEINTES' if k<0 else 'ALLUMÉES',1062,50,True)
    foot(d,'GRÈS MIEL + PIERRE FUMÉE','4 POSES PAR FOYER · 10 I/S');return z

def clip_foyer(n):return foyer_card(-1 if n<27 else (n//3)%4)

@lru_cache(maxsize=3)
def bib_card(k):
    name=['bib-sans','bib','bib-alt'][k];p=im(name);z,d=head('04 / BIBLIOTHÈQUE','De Cuisine à Bibliothèque','Même salle, mêmes accès. Les rayonnages s’encastrent sur un calque à part.')
    card(d,'#202540',(44,148,728,646),'#596175');card(d,'#252c25',(746,148,1236,646),'#66785a')
    fit(z,p,(55,165,717,632));txt(d,'LES TROIS NICHES MURALES',761,165,19,'mono',GOLD)
    fit(z,p.crop((54,19,426,131)),(760,202,1222,386),1.20)
    d.line((759,374,1220,374),fill='#576550');txt(d,'MODÈLES DE RAYONNAGES',762,392,18,'mono',GOLD)
    for off,name in enumerate(('archives','herbiers','atlas')):
        x=761+153*off;checker(d,(x,424,x+145,568),'#2d372e','#344133',10)
        pic=Image.open(ROOT/'Rayonnages'/f'centre-{name}.png').convert('RGBA');fit(z,pic,(x+3,427,x+143,565),1.77);txt(d,BOOK_NAMES[name],x+72,580,15,'bold',anchor='ma')
    label(d,['CALQUE MASQUÉ','CALQUE VISIBLE','AUTRE ASSORTIMENT'][k],957,51)
    foot(d,'1 CALQUE RGBA TRANSPARENT · 480 × 360','FENÊTRES ET SOL CONSERVÉS');return z

def clip_bib(n):return bib_card(0 if n<39 else 1 if n<172 else 2)

PARTS=[(162,clip_compare),(90,clip_full),(192,clip_flags),(90,clip_flagroom),(216,clip_foyer),(252,clip_bib)]

def main():
    tmp=VIDEO.with_suffix('.tmp.mp4');cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(FPS),'-i','pipe:0','-an','-vf','scale=iw:ih:out_color_matrix=bt709:out_range=tv,format=yuv420p','-c:v','libx264','-profile:v','high','-level','4.0','-threads','4','-preset','fast','-crf','18','-g','60','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart','-metadata','title=Destiny — Drapeaux, foyers et bibliothèque',str(tmp)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for j,(n,q) in enumerate(PARTS):
            for t in range(n):
                f=q(t)
                if t in [0,72]:png(f,W/f'MP4-check-{j}-{t}.png')
                proc.stdin.write(f.tobytes())
    finally:
        proc.stdin.close()
        if proc.wait():raise SystemExit('FFmpeg: erreur d’encodage')
    tmp.replace(VIDEO);print(VIDEO.name, sum(a for a,q in PARTS)/FPS, 'secondes,',VIDEO.stat().st_size,'octets')

if __name__=='__main__':main()
