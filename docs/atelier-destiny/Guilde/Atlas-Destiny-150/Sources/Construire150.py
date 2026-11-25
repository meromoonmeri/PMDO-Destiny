#!/usr/bin/env python3
"""150 illustrated sites on the accepted Destiny atlas. Map stays free of lettering."""
from pathlib import Path
from hashlib import sha256
from functools import lru_cache
from collections import Counter
import json,re,unicodedata,math,random
import numpy as np
from scipy import ndimage as nd
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'Atlas-du-Monde-Destiny';C=OLD/'Calques';PUBLIC=ROOT/'Apercu';O=PUBLIC/'assets';W=Path.home()/'.cache/atlas-destiny-150';TRAITS=ROOT/'Sources'/'Traits'
O.mkdir(parents=True,exist_ok=True);W.mkdir(parents=True,exist_ok=True)
A=json.loads((OLD/'Reperes-separes.json').read_text());DEST=A['lieux_destiny'];REF=A['positions_eddy_reference_non_affichees'];SZ=tuple(A['carte_px']);NN=Image.Resampling.NEAREST;BX=Image.Resampling.BOX
START_BOX=tuple(A['cadre_depart'])
MASK=np.asarray(Image.open(TRAITS/'Masque-terres.png')).astype(bool);assert MASK.shape==tuple(SZ[::-1])
ASSETS=json.loads((TRAITS/'Rectangles-des-miniatures.json').read_text());SHEET=Image.open(TRAITS/'Miniatures-de-reference.png').convert('RGBA')
CROQUIS=json.loads((TRAITS/'Provenance-croquis.json').read_text())
TYPES={
 'bourg':['Bourgs','Village, passerelles ou petites toitures sur le parchemin.'],'foret':['Forêts','Bosquets et clairières autour d’un sentier.'],'grotte':['Grottes','Une entrée creusée dans la roche.'],'sommet':['Reliefs','Crêtes, cols et escarpements.'],'ruine':['Ruines et tours','Des pierres taillées, des marches ou un monument.'],'eau':['Lacs et cascades','Une rive, un bassin ou un courant d’eau.'],'mer':['Mers et îles','Un passage au large, un récif ou une île.'],'glace':['Glaces','Des roches froides et des pointes enneigées.'],'volcan':['Volcans','Un cratère, des strates chaudes et un filet de lave.'],'sable':['Sables','Des dunes ou des falaises dans les tons d’ocre.'],'plaine':['Plaines','Une petite étendue ouverte et ses détails de terrain.']}
REG={'destiny':'Côte de Réverie','eau':'Continent de l’Eau','air':'Continent de l’Air','herbe':'Continent de l’Herbe','brume':'Continent de la Brume','sable':'Continent du Sable','mer':'Mer des Merveilles','mystere':'Continent Mystère'}
POOLS={
 'eau':(24,[i for i in range(33) if i not in (28,29,30)], [0,1,7,13,32]),
 'air':(30,list(range(33,52))+[i for i in range(120,164) if i not in (123,132,141,149,150,151,157)], [33,39,41,120,126,144,158,159,163]),
 'herbe':(32,[i for i in range(52,77) if i not in (53,56,63,68,73)]+[i for i in range(164,227) if i not in (168,169,170,171,172,173,174,185,186,187,188,189,190,191,192,193,196,198,206,207,219)], [52,54,55,62,64,164,175,204,209,217]),
 'brume':(28,list(range(77,92))+list(range(227,265)), [77,79,85,86,89,91,227,230,231,251]),
 'sable':(14,list(range(92,109)),[92,95,98,99,100,101]),
 'mer':(14,list(range(109,117))+[48,53,56,63,68,73,123,132,141,149,150,151,157,172,174,185,186,187,188,189,191,193,196,206,219], [110,111,113,116,172,185,187,188,191,193]),
 'mystere':(3,[117,118,119],[117,118,119]),
}
ORIG={
 'MarkerSmd':'Super Donjon Mystère','MarkerExp':'Explorateurs','MarkerRt':'Équipe de Secours','MarkerGti':'Les Portes de l’Infini','MarkerEtc':'Autre',
}
TITLES={164:'Bourg-Trésor',120:'Place Pokémon',54:'Jungle Mystère',187:'Terre Cachée',188:'Tour du Temps',191:'Volcan Géant',185:'Cratère Obscur',204:'Grotte Cristal',117:'Tour du Destin',39:'Arbre du Monde',110:'Volcan de l’île de Feu',55:'Lac Cœur',230:'Grand Glacier',231:'Palais de Glace',53:'Tourbillon Spiral',62:'Triangle Temple'}
SL={'guilde':'ruine','fosse':'eau','bois':'foret','reverie':'bourg','passage':'grotte'}
PALETTES={'roche':('#96734b','#ba8e57','#e3b579'),'nuages':('#a09878','#e7d9b0','#f5e2b9')}


def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def dig(x):return sha256(x).hexdigest()
def sh(p):return dig(p.read_bytes())
def paste(dst,src,x,y):dst.alpha_composite(src,(round(x-src.width/2),round(y-src.height)))
def resize(a,w):return a.resize((w,max(2,round(a.height*w/a.width))),NN)
@lru_cache(maxsize=128)
def cut(r):
    a=SHEET.crop(ASSETS[r[0]][r[1]]);return a.crop(a.getbbox())

@lru_cache(maxsize=8)
def study(k):
    p=TRAITS/CROQUIS[k]['fichier_detoure'];a=Image.open(p).convert('RGBA');assert a.width==30 and a.getbbox();return a


def kind(i,nom):
    t=nom.lower();c=lambda x:bool(re.search(x,t))
    if i in (187,):return 'ruine'
    if i in (201,211):return 'grotte'
    if i in (172,196):return 'mer'
    if c(r'town|village|pokémon square|marine resort'):return 'bourg'
    if c(r'lava|volcan|magma|blaze|dark crater|blazing|smoking mountain|inferno|fiery field'):return 'volcan'
    if c(r'waterfall|cascade|pol[yi]wrath river|river|heart lake|lake|headwater|hot springs|enlightenment|pond|spring|waterfall basin'):return 'eau'
    if c(r'frozen|frost|ice\b|icy\b|glacier|snow|avalanche|tundra|freeze|blizzard|freezing'):return 'glace'
    if c(r'relic|ruin|tower|temple|hall of magic|gate|geoglyph|historic|bridge'):return 'ruine'
    if c(r'vortex|strait|ocean|\bsea\b|tempest|archipelago|trench|island|\bisle\b|reef|coast|shoreline'):return 'mer'
    if c(r'dune|sand|desert|savannah'):return 'sable'
    if c(r'cave|grotto|tunnel|cavern|burrow|mine|maze|quarry|barrow|crevice'):return 'grotte'
    if c(r'forest|jungle|woods|grove|tree of|world tree|tree steps|fallen leaves|leafy|woodland'):return 'foret'
    if c(r"mount|mt\.|mountain|range|peak|cliff|hill|ridge|canyon|gorge|highland|stairway|chasm"):return 'sommet'
    if c(r'pass|field|plain|meadow|prairie|path|garden|bog|hollow|wasteland|valley'):return 'plaine'
    return 'ruine' if i in (118,119,124,184) else 'sommet'


def view(i,typ,title,big=False):
    # Every location gets its own graphic. These are newly composed sprites on a small DS grid,
    # not text markers, randomised coordinates or individually claimed AI paintings.
    seed=int(dig((str(i)+title).encode())[:8],16);r=random.Random(seed);n=title.lower();S=Image.new('RGBA',(48,44));d=ImageDraw.Draw(S)
    def mot(f,j,w,x,y,mirror=False):
        q=resize(cut((f,j%len(ASSETS[f]))),w);paste(S,ImageOps.mirror(q) if mirror else q,x,y)
    def ai(k,w,x=24,y=34,m=False):
        q=resize(study(k),w);paste(S,ImageOps.mirror(q) if m else q,x,y)
    def bed(x,y,w,h,colors):
        lc,hi,lo=colors
        d.polygon([(x-w//2,y-2),(x-w//2+3,y-h+4),(x-6,y-h),(x+w//2-4,y-h+1),(x+w//2,y-h+5),(x+w//2+1,y-3),(x+w//2-4,y),(x-w//2+5,y+1)],fill=hi,outline=lc)
        d.line((x-w//2+5,y-1,x+w//2-4,y-2),fill=lo)
    def path(x,y,k):d.line([(x,y),(x-2,y+2),(x+1,y+3),(x-4,y+5)][:k],fill='#e0b671',width=1)
    def water(x,y,w,h,col='#54a3a0'):
        pts=[(x-w//2,y-2),(x-w//2+2,y-h+1),(x-3,y-h),(x+w//2-2,y-h+1),(x+w//2,y-h+3),(x+w//2-1,y-2),(x+w//2-5,y),(x-w//2+4,y)]
        d.polygon(pts,fill=col,outline='#706b51');d.line((x-w//2+3,y-h+3,x-1,y-h+2),fill='#a0cbad');d.line((x,y-2,x+w//4+2,y-2),fill='#78c6bc')
    def color(s):return ['#986a48','#bb9051','#dfaa64'][s%3]
    def hut(x,y,w=8,h=9,roof='#827548'):
        d.rectangle((x+1,y-h//2,x+w-1,y),fill='#ba8d56',outline='#69482f');d.polygon([(x,y-h//2),(x+2,y-h+1),(x+w-3,y-h),(x+w+1,y-h//2)],fill=roof,outline='#745539');d.line((x+2,y-h+2,x+w-3,y-h+1),fill='#c2a875');d.point((x+w//2,y-2),fill='#704627');d.point((x+w//2+2,y-3),fill='#ddac61')
    b=r.randrange(4);s=r.randint(-2,2)
    if i in (158,218):  # Sky landmarks, intentionally offshore on the survey.
        mot('nuage',0,32,24,38)
        if i==158:
            mot('tour',1,20,24,34);d.line((21,18,21,28),fill='#efcc91');d.line((27,15,27,25),fill='#bea16d')
        else:
            for a,bp in [(14,33),(19,29),(24,24),(29,19)]:
                d.polygon([(a-3,bp),(a+1,bp-2),(a+6,bp-1),(a+3,bp+2),(a-3,bp+2)],fill='#d9bc82',outline='#91795b')
            mot('nuage',0,12,32,17);d.point((33,13),fill='#f6e4ab')
    elif i==111:  # The undersea ruins are under the water, not an unsupported brown gate.
        water(24,36,34,15,'#68a3a0');water(24,34,25,10,'#548e92')
        d.rectangle((16,27,32,32),fill='#718477',outline='#536a64');d.polygon([(17,28),(17,23),(20,21),(28,21),(32,25),(32,29),(27,28),(27,24),(21,25),(21,29)],fill='#829a81',outline='#4d6e6a')
        d.line((12,31,17,31,21,30),fill='#97b8a5');d.line((25,33,32,32,35,30),fill='#90bfb0');d.point((31,25),fill='#c1d2ad')
    elif i in (187,188): # A plateau and a separate tower, visually belonging to one island chain.
        bed(24,37,34,13,PALETTES['roche']);d.line((12,37,20,38,32,37,39,36),fill='#91b3a4')
        if i==187:
            mot('buttes',3,28,23,36);mot('site',0,13,25,29);mot('arbres',0,8,33,35);d.line((20,35,25,32,28,32),fill='#dfb976')
        else:
            mot('tour',1,18,24,35);d.rectangle((22,19,25,23),fill='#bcad7e',outline='#775844');d.point((24,21),fill='#ecd1a0');d.line((23,31,28,30),fill='#d6ae73')
    elif i in (201,211):
        bed(24,36,34,14,('#91744a','#b69653','#d2ab67'))
        mot('desert' if i==201 else 'buttes',1,23,25,30)
        d.polygon([(11,30),(15,26),(28,25),(36,29),(33,33),(25,36),(16,34)],fill='#876341',outline='#725434')
        d.polygon([(16,30),(22,28),(29,28),(31,30),(27,33),(20,33)],fill='#55483d');d.line((12,32,19,35,29,34,33,32),fill='#d4a25d')
        d.line((18,30,24,29,29,29),fill='#a58a56')
    elif typ=='bourg':
        bed(24,36,34,14,('#977449','#bd9856','#e0bb7a'))
        mot('arbres',b,8,12,27);mot('arbres',b+2,7,35,33)
        if i in (164,120,33,92,52,77) or b%2==0:ai('bourg',r.randint(24,30),24+s,35,bool(b&1));hut(31+s,30,7,9,['#a56b48','#847347','#a88a4e','#87614a'][b]);
        else:
            hut(12,29,9,13,'#a1744c');hut(22+s,27,8,11,'#8d8b48');hut(28,32,12,15,'#a8804b');hut(16+s,37,8,11);d.line((15,35,28,33),fill='#ddaf6b')
        if 'serene' in n or i==164:
            d.line([(14,31),(19,33),(19,35),(23,36),(22,38)],fill='#679c9b',width=2);d.line((17,34,21,34),fill='#a77b4e')
        if 'post town' in n:
            hut(24,35,9,14,'#9f6a49');d.line((22,35,22,23),fill='#795a3b');d.polygon([(22,23),(28,24),(22,26)],fill='#d8af69')
        elif 'shaymin' in n:
            d.line((14,36,33,36),fill='#909455');d.point((16,35),fill='#dd9a7d');d.point((26,36),fill='#ead496');d.point((33,34),fill='#d58a79')
    elif typ=='foret':
        bed(24,36,31,13,('#878250','#a6a054','#c6b36e'));mot('arbres',r.choice([0,4,6]),r.randint(15,20),18,33);mot('arbres',2,6,34,32)
        if 'tree of' in n or 'world tree' in n:
            d.rectangle((22,22,27,36),fill='#986339',outline='#775637');mot('arbres',0,23,24,29);mot('arbres',6,13,29,29);path(24,36,4)
        else:
            mot('arbres',r.choice([0,4,6]),r.randrange(10,17),27+s,31,r.random()<.5)
            mot('arbres',r.choice([1,3,5,7]),r.randrange(8,12),30+s,36);path(19+s,32,4)
        if re.search('apple|berry|bounty|oran|fair|pumpka',n):
            for j in range(4):d.rectangle((14+j*5,24+(j%3)*2,15+j*5,25+(j%3)*2),fill=['#d68443','#bc6946','#e1b55f'][j%3])
        if re.search('fog|myst|whisper|moonlit|sinister',n):d.line((17,33,24,33,27,32),fill='#c6c8a4');d.point((29,31),fill='#f0d6a1')
    elif typ=='grotte':
        bed(24,36,33,11,('#977347','#c3a060','#dfba7b'))
        if i in (204,205,225) or re.search('crystal|star|lapis|gleam',n):
            mot('buttes',1,20,24,35);d.polygon([(10,30),(9,23),(11,18),(15,22),(16,28)],fill='#6794a5',outline='#536873');d.line((11,20,12,27),fill='#acc7ca');d.polygon([(29,31),(30,22),(35,18),(37,23),(35,32)],fill='#74978b',outline='#586f69');d.line((35,21,33,27),fill='#cee2c2')
        else:
            if b==1 or b==3:ai('ruines',r.randint(19,26),24+s,34,bool(b&1))
            else:mot('buttes',r.choice([0,1,2,3,4]),r.randint(21,26),24+s,34,bool(b&1))
            mx=24+s;d.polygon([(mx-5,34),(mx-5,29),(mx-3,26),(mx+2,26),(mx+5,30),(mx+5,34)],fill='#624a3c',outline='#815a37');d.polygon([(mx-3,34),(mx-3,29),(mx,27),(mx+3,29),(mx+3,34)],fill='#3e372d');path(mx,34,r.choice([3,4]));mot('arbres',r.randrange(8),6,34,35)
    elif typ=='sommet':
        bed(24,36,33,13,('#98714a','#ba9657','#dab171'))
        if re.search('gorge|chasm|canyon|valley|bluff',n):
            mot('mont',r.randrange(3),15,17,34);mot('buttes',0,16,29,36,True);d.line([(26,22),(23,27),(23,30),(20,33),(19,37)],fill='#8d603b',width=2);d.line([(27,22),(24,28),(25,30),(21,33)],fill='#e3b570');path(18,35,3)
        else:
            mot('mont',r.randrange(3),r.randint(15,25),24+s,33,bool(b&1));mot('mont',r.randrange(3),r.randint(10,16),14,36);mot('buttes',r.randrange(5),r.randint(7,13),32,36);path(26,34,r.choice([3,4]))
        if re.search('moon|sun|glitter|sky|revelation',n):d.point((24,17),fill='#f5dfa3');d.line((24,17,25,18),fill='#d9af70')
    elif typ=='ruine':
        bed(24,36,32,12,('#987753','#bd9c64','#d9b578'));mot('plaine',2,11,15,36)
        if re.search(r'tower|tour|stair|palace',n):mot('tour',0 if b in (0,2) else 1,r.randrange(15,21),24+s,34,bool(b&1));mot('buttes',1,8,31,36)
        elif re.search('geoglyph|bridge',n):
            mot('site',2,17,23+s,33);d.line([(12,34),(19,29),(26,29),(34,35)],fill='#8e6b49',width=2);d.line([(12,35),(19,30),(26,30),(34,36)],fill='#e6ba72',width=1)
        else:
            ai('ruines',r.randint(23,28),24+s,35,bool(b&1));mot('plaine',b%3,8,35,36);path(24,34,r.choice([3,4]))
    elif typ=='eau':
        bed(24,36,34,14,('#968355','#bc9e66','#dabd85'))
        if 'fall' in n or 'waterfall' in n:
            a=Image.open(C/'Lieu-fosse.png').convert('RGBA');paste(S,resize(ImageOps.mirror(a) if b&1 else a,r.randint(19,24)),25+s,32);water(24,36,19,6);mot('arbres',b,8,13,30)
        elif 'heart' in n:
            pts=[(24,26),(17,22),(13,25),(14,30),(24,36),(33,30),(35,25),(30,22)];d.polygon(pts,fill='#54a9ac',outline='#796d56');d.line((15,26,18,24,22,25),fill='#a3c6ac');mot('arbres',b,7,33,32)
        elif 'river' in n or 'headwater' in n:
            d.line([(13,28),(18,28),(23,23),(29,23),(28,28),(24,32),(29,36),(33,35)],fill='#94744f',width=5);d.line([(13,28),(18,28),(23,23),(29,23),(28,28),(24,32),(29,36),(33,35)],fill='#589fa1',width=3);d.line((21,30,29,30),fill='#d3a36a',width=2);mot('arbres',b,9,15,33)
        else:
            water(23+s,35,r.randint(19,28),r.randint(8,11),['#4e9fa3','#66a7a2','#6096a0','#79b5b1'][b]);mot('plaine',2,r.randint(7,10),14,29);mot('arbres',b,8,33,32)
            if re.search('hot|mysteri|luminous|light',n):d.line([(20,27),(19,24),(21,22),(21,19)],fill='#d9cfb1');d.line([(26,25),(28,22),(28,20)],fill='#ece0bf')
    elif typ=='mer':
        if re.search('vortex|abyss|tempest|devil|maelstrom|trench|bottomless|far.off|storm',n):
            water(24,36,32,12,'#7aa7a0');d.line([(13,34),(11,29),(16,25),(31,24),(36,28),(35,33),(27,35),(19,34),(16,31),(19,28),(27,27),(31,29),(28,31),(24,31)],fill='#4e8790',width=2);d.line((14,33,16,35,22,36),fill='#a6caba');d.point((24,31),fill='#c0d5b3')
        elif re.search('island|isle|hidden land',n):
            icy='blizzard' in n;bed(24,36,33,15,('#90774c','#c8baa1' if icy else '#ba9959','#d7b271'))
            mot('pic' if icy else 'mont',b,14,25,31);mot('arbres',b+1,9,17,35);d.line((11,36,15,37,24,37),fill='#92b6ab');d.line((27,37,35,36),fill='#85a7a4')
            if 'islands' in n:
                bed(34,31,9,6,('#937849','#c2a46a','#d4b984'));d.line((30,32,35,32),fill='#9bbcb2')
        else:
            water(24,36,31,10,'#6da8a8');mot('buttes',r.randrange(5),r.randint(12,17),24+s,32);mot('plaine',2,7,14,34);d.line((29,32,34,32),fill='#afd3bc')
    elif typ=='glace':
        bed(24,36,31,14,('#879e9c','#c4d0bb','#d9d7bc'))
        if 'cave' in n or b%2==1 or i in (230,231,254):ai('glace',r.randint(22,30),24+s,35,bool(b&1))
        else:mot('pic',b,21,25+s,34);mot('pic',2,13,16,36,True)
        d.point((16,35),fill='#e7e6c7');d.line((27,35,33,34),fill='#a2b8b4')
        if 'fall' in n:d.line((24,24,24,30,22,33,24,34),fill='#b0d9d3',width=2)
        if 'palace' in n:
            for u,v in [(17,28),(23,24),(29,28)]:
                d.polygon([(u-2,32),(u-2,v),(u,v-4),(u+3,v),(u+3,33)],fill='#8fbab9',outline='#526e74');d.line((u,v-2,u,31),fill='#cadbd0')
            d.line((18,33,29,33),fill='#b7cbb9')
    elif typ=='volcan':
        bed(24,36,32,13,('#906448','#ab7748','#d09b58'))
        if b in (0,1,3) or i in (185,191,110,163):ai('volcan',r.randint(22,28),24+s,35,bool(b&1))
        else:mot('volcan',0,24,24+s,35,bool(b&1))
        d.line((22+s,28,23+s,30,23+s,32,20+s,34),fill='#d05431',width=1);d.point((24+s,29),fill='#faa94d');d.point((19+s,35),fill='#ef8c42')
    elif typ=='sable':
        bed(24,36,35,14,('#ab793f','#d9ad5a','#e6c980'));mot('desert',b,18,26+s,32,bool(b&1));mot('desert',0,15,17,34);d.line((15,35,21,34,25,35,33,33),fill='#a97443');d.line((15,36,21,35,25,36,33,34),fill='#e9bd6a')
        if re.search('thirst|mirage|spirit|jewel',n):d.point((29,30),fill='#84a5a2');d.line((16,28,18,27),fill='#f5ce7a')
    else:
        bed(24,36,32,14,('#93844f','#aca65c','#cbbc76'));mot('plaine',r.randrange(3),r.randrange(10,15),23,35)
        if 'electric' in n or 'amp' in n:
            d.polygon([(22,21),(19,28),(23,27),(21,32),(28,25),(24,26),(26,21)],fill='#e3b955',outline='#a78247')
        elif re.search('nectar|garden|meadow|sun',n):
            for j in range(4):
                x=15+j*5;y=27+r.randrange(5);d.point((x,y+1),fill='#77764c');d.rectangle((x-1,y-1,x,y),fill=['#de9b77','#b39262','#e0c37c','#dfb476'][j])
        else:mot('arbres',b,7,14,33);mot('buttes',r.randrange(5),8,31,31);path(24,31,4)
    a=S.crop(S.getbbox());tw=r.randrange(19,24)+(3 if big or typ=='bourg' else 0)+(1 if typ in ('eau','volcan','mer') else 0)
    a=resize(a,min(30,tw));a=a.crop(a.getbbox());return a


@lru_cache(maxsize=2048)
def offset(radius):
    return sorted([(x,y) for y in range(-radius,radius+1,2) for x in range(-radius,radius+1,2) if x*x+y*y<=radius*radius],key=lambda k:(k[0]*k[0]+k[1]*k[1],abs(k[1])))

def slot(a,x0,y0,allowed,boxes,radius,near=False):
    # Make tiny cartographic label-style adjustments only when two emblems would overlap.
    for dx,dy in offset(radius):
        x,y=x0+dx,y0+dy;w,h=a.size;l=x-w//2;t=y-h;b=(l,t,l+w,y)
        if l<9 or t<9 or l+w>=SZ[0]-9 or y>=SZ[1]-8:continue
        if not near and ((x-1170)/82)**2+((y-844)/66)**2<1:continue
        if not allowed and (not MASK[y-1,x] or np.mean(MASK[y-5:y+1,x-3:x+4])<.62):continue
        if any(not(b[2]+3<=e[0] or e[2]+3<=b[0] or b[3]+3<=e[1] or e[3]+3<=b[1]) for e in boxes):continue
        return (x,y),b
    return None


def record(key,group,typ,name,a,b,p,**kw):return {'id':key,'nom':name,'region':group,'type':typ,'ancre':list(p),'rect':list(b),'info':TYPES[typ][1],**kw},a


def make_places():
    out=[];boxes=[];grp=[];uniq=set()
    for k in ('reverie','fosse','passage','bois','guilde'):
        row=DEST[k];im=Image.open(OLD/row['fichier']).convert('RGBA');b=tuple(row['rectangle']);assert im.size==(b[2]-b[0],b[3]-b[1]);boxes.append(b)
        note={'reverie':'Le point de départ. Trois premiers donjons sont joignables par de courts sentiers.','fosse':'Une chute d’eau cache l’entrée du donjon, à deux pas de Réverie.','passage':'Un tunnel d’eau s’ouvre sur la petite crique au sud-ouest du village.','bois':'Une clairière et son chemin à l’ouest de Réverie.','guilde':'Le grand chêne de la guilde sur son promontoire, au nord de Réverie.'}[k]
        out.append(record(k,'destiny',SL[k],row['nom'],im,b,row['ancre'],jeu='Destiny',premiere_zone=True,note=note))
    for group,(quota,pool,priority) in POOLS.items():
        placed=[];done=[];order=list(dict.fromkeys(priority+pool));nr=0
        while len(placed)<quota and order:
            if order[0] in priority:
                i=order.pop(0);fixed=True
            else:
                def score(idx):
                    u,v=REF[idx]['ancre'];near=min((math.hypot(u-x,v-y) for x,y in done),default=40);k=kind(idx,REF[idx]['nom']);return min(270,near)+4*(4-sum(out[i][0]['type']==k for i in placed))+(idx%11)*.16
                i=max(order,key=score);order.remove(i);fixed=False
            row=REF[i];name=TITLES.get(i,row['nom']);raw=row['nom'];norm=re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',raw).casefold());
            if norm in uniq and raw!='Destiny Tower':continue
            if i==212 and norm in uniq:name='Tour du Destin (Explorateurs)'
            typ=kind(i,raw);img=view(i,typ,raw,fixed);x,y=row['ancre'];floating=group=='mer' or typ=='mer' or i in (158,184,218);
            res=slot(img,x,y,floating,boxes,38 if fixed else 26)
            if not res and fixed:res=slot(img,x,y,floating,boxes,65)
            if not res and fixed and i in (52,164):res=slot(img,x,y,floating,boxes,73)
            if not res:continue
            pivot,b=res;boxes.append(b);done.append(pivot);uniq.add(norm);nr+=1
            r0=row['serie'].split('.')[0].rstrip('L');decl=ORIG.get(r0,'Donjon Mystère')
            out.append(record(f'monde-{i+1:03}',group,typ,name,img,b,pivot,jeu=decl,original=raw,ancre_reference=[x,y],lien=row['lien']));placed.append(len(out)-1)
        grp.append((group,nr,quota));print(group,nr,'/',quota,flush=True)
    assert len(out)==150,(len(out),grp)
    return out


def decor(rows):
    # Backdrop kept at exactly the same scale. Quiet the forest stamps behind each new emblem.
    b=Image.open(C/'Parchemin-relief.png').convert('RGBA');r=Image.open(C/'Reliefs-et-forets.png').convert('RGBA');rel=np.array(r)
    mask=Image.new('L',SZ);d=ImageDraw.Draw(mask)
    for p,im in rows:
        if p.get('premiere_zone'):continue
        x,y,w,h=p['rect'];aa=nd.binary_dilation(np.array(im)[...,3]>0,iterations=2);mask.paste(Image.fromarray(aa.astype(np.uint8)*255),(x,y),Image.fromarray(aa.astype(np.uint8)*255))
    # Suppress the 12 unindexed historical trial emblems of the accepted atlas; their geographic
    # scenery and the five approved Destiny sprites remain untouched.
    for x,y,w in ((1339,176,21),(322,265,24),(1294,60,15),(596,144,17),(987,714,23),(988,875,20),(669,431,18),(830,422,20),(1080,344,16),(239,936,22),(1358,344,19),(954,679,19)):
        d.rectangle((x-w//2-1,y-32,x+(w+1)//2+1,y+1),fill=255)
    rel[np.asarray(mask)>0]=0;r=Image.fromarray(rel);b.alpha_composite(r);b.alpha_composite(Image.open(C/'Sentiers-et-ruisseau.png').convert('RGBA'))
    return b


def spin(a,k,typ):
    q=np.array(a);r,g,b=q[...,:3].astype(np.int16).transpose(2,0,1);m=(g>82)&(g-r>13)&(b-r>19)&(q[...,3]>0)
    if typ=='volcan':m=(r>148)&(r-g>35)&(g-b>20)&(q[...,3]>0)
    if typ not in ('eau','mer','volcan'):return a
    y,x=np.indices(m.shape);amt=((((x*.65+y-k*2.7)%17)<1.75)*24 + (((x+2*y-k*2)%23)<1)*11)*m
    if typ=='volcan':amt=amt[...,None]*[.55,1,.35]
    else:amt=amt[...,None]*[.69,.93,1.]
    q[...,:3]=np.clip(q[...,:3].astype(float)+amt,0,255).astype(np.uint8);return Image.fromarray(q)


def sprites(rows):
    cols=15;pitch=42;atlas=Image.new('RGBA',(cols*pitch,math.ceil(len(rows)/cols)*pitch));cells=[]
    animated=[]
    for i,(p,im) in enumerate(rows):
        w,h=im.size;assert max(w,h)<=pitch-2
        l=i%cols*pitch+1;t=i//cols*pitch+1;atlas.paste(im,(l,t));p['sprite']=[l,t,w,h]
        old=C/f"Eau-{p['id']}-8-poses.png"
        frames=[]
        if p.get('premiere_zone') and old.is_file():
            q=Image.open(old).convert('RGBA');frames=[q.crop((k%4*w,k//4*h,k%4*w+w,k//4*h+h)) for k in range(8)]
            assert frames[0].tobytes()==im.tobytes()
        elif p['type'] in ('eau','mer','volcan'):
            cand=[im]+[spin(im,k,p['type']) for k in range(1,8)]
            if len({f.tobytes() for f in cand})>=5:frames=cand
        if frames:
            p['animation']=len(animated);animated.append((p,frames))
    atlas.save(O/'Lieux-150.png',optimize=True)
    anim=Image.new('RGBA',(8*pitch,len(animated)*pitch))
    for i,(v,fr) in enumerate(animated):
        for k,a in enumerate(fr):anim.paste(a,(k*pitch+1,i*pitch+1))
    anim.save(O/'Animations.png',optimize=True);return len(animated)


def main():
    source={k:sh(OLD/k) for k in ('Monde-Destiny-Sans-Texte-6144x4608.png','Reverie-Et-Ses-Donjons.png','Reperes-separes.json')}
    rows=make_places();b=decor(rows);b.convert('RGB').save(O/'Terrain.png',optimize=True);n=sprites(rows)
    for p,a in sorted(rows,key=lambda k:k[0]['ancre'][1]):b.alpha_composite(a,tuple(p['rect'][:2]))
    b=b.convert('RGB');b.save(O/'Monde-150.png',optimize=True);b.resize((SZ[0]*4,SZ[1]*4),NN).save(ROOT/'Monde-Destiny-150-Lieux-6144x4608.png',compress_level=6)
    Image.open(C/'Carte-non-devoilee.png').convert('RGB').save(O/'Nuages.png',optimize=True)
    # Light contact sheet for internal QA, not an atlas delivered with printed names.
    b.resize((1152,864),BX).save(W/'Vue-ensemble.png',optimize=True);b.crop(START_BOX).resize((1152,864),NN).save(W/'Depart.png',optimize=True)
    m=[k[0] for k in rows];uids=[r['id'] for r in m];assert len(m)==len(set(uids))==150
    assert all(sh(OLD/k)==v for k,v in source.items())
    assert len({a.tobytes() for _,a in rows})==150
    for i,p in enumerate(m):
        x,y,w,h=p['rect']
        for q in m[:i]:
            l,t,r,s=q['rect'];assert w<=l or r<=x or h<=t or s<=y,(p['id'],q['id'])
    stats=Counter(r['region'] for r in m);tp=Counter(r['type']for r in m);assert n>=16
    j={'version':3,'taille':list(SZ),'nb':150,'regions':REG,'types':{k:v[0] for k,v in TYPES.items()},'par_region':stats,'par_type':tp,'grille_atlas':42,'animations':n,'depart':{'centre':DEST['reverie']['ancre'],'cadre':list(START_BOX),'chemins':A['chemins']},'lieux':m,'references':A['references'],'edition_validee_sha256':source,'croquis':{k:{**v,'sha256_detoure':sh(TRAITS/v['fichier_detoure'])} for k,v in CROQUIS.items()}}
    write(O/'Lieux.json',j);print(f"150 motifs distincts · {n} animations · {dict(stats)}",flush=True)

if __name__=='__main__':main()
