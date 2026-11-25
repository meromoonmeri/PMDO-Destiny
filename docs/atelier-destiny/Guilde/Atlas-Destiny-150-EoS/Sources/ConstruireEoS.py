#!/usr/bin/env python3
"""Extract the exact eight EoS plates and put the existing Destiny atlas on a separate layer."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json,math
import numpy as np
from scipy import ndimage as nd
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'Sources'/'Reference-EoS.png';PREV=ROOT.parent/'Atlas-Destiny-150'/'Apercu'/'assets';A=ROOT/'Apercu'/'assets';A.mkdir(exist_ok=True,parents=True)
CACHE=Path.home()/'.cache/atlas-destiny-eos';CACHE.mkdir(exist_ok=True)
W,H=504,336;S=3;WIDE=(W*S,H*S);PITCH=42;NN=Image.Resampling.NEAREST
DEP={'reverie':(215,180),'fosse':(256,166),'passage':(199,201),'bois':(225,191),'guilde':(231,157)}
START_BOX=(145,105,321,237)
PATHS={'guilde':[(215,180),(222,175),(226,169),(228,163),(231,157)],'fosse':[(215,180),(222,175),(231,177),(241,177),(250,172),(256,166)],'passage':[(215,180),(213,185),(211,191),(207,196),(199,201)],'bois':[(215,180),(220,184),(225,191)]}
REGIONS={'destiny':'Côte de Réverie','ouest':'Baies de l’Ouest','nord':'Hautes terres du Nord','centre':'Vallées du Centre','est':'Forêts de l’Est','sud':'Péninsule du Sud','archipel':'Îles et haute mer','neiges':'Île des Neiges','volcans':'Île volcanique'}
# A few itinerary landmarks are purposefully assigned to a feature of the new atlas; the
# remaining names are clustered on EoS terrain, not plotted as official EoS coordinates.
HERO={
 'monde-001':('ouest',174,113),'monde-165':('ouest',185,153),'monde-118':('nord',315,56),
 'monde-189':('nord',400,48),'monde-040':('est',415,99),'monde-188':('archipel',83,201),
 'monde-056':('sud',234,248),'monde-205':('nord',317,85),'monde-231':('neiges',99,278),
 'monde-186':('volcans',81,88),'monde-192':('volcans',119,52),'monde-159':('archipel',455,162),
 'monde-219':('archipel',173,51),'monde-112':('archipel',149,202),
}
SECTOR={'eau':['ouest','centre','sud'],'air':['nord','est','ouest'],'herbe':['centre','sud','est','ouest'],'brume':['est','centre','nord'],'sable':['ouest','nord','sud'],'mer':['archipel','sud'],'mystere':['nord','est']}
QUOTAS={'ouest':20,'nord':24,'centre':29,'est':24,'sud':19}
VARS={'neiges':1,'volcans':2,'archipel':3,'nord':4,'ouest':5,'est':6,'centre':7,'sud':8}


def hashfile(p):return sha256(p.read_bytes()).hexdigest()
def output(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def frame_boxes():return [(k%2*507,k//2*339,k%2*507+W,k//2*339+H) for k in range(8)]
def rect(x,y,w,h):return(x-w//2,y-h,x-w//2+w,y)
def grow(r):return [int(v*S) for v in r]

def extract():
    src=Image.open(SRC);assert src.size==(1011,2031) and src.mode=='P'
    plate=[src.crop(r) for r in frame_boxes()];a=Image.new('P',(4*W,2*H));a.putpalette(src.getpalette())
    for k,p in enumerate(plate):a.paste(p,(k%4*W,k//4*H))
    a.save(A/'Feuillets-EoS.png',optimize=True)
    plate[-1].save(ROOT/'Fond-EoS-Original-504x336.png',optimize=True)
    # Native pixels are repeated, never interpolated, recolored, or retextured.
    plate[-1].resize(WIDE,NN).save(A/'Terrain.png',optimize=True)
    return plate


def grounds(plate):
    q=np.asarray(plate[-1]);rgb=np.asarray(plate[-1].convert('RGB')).astype(np.float32);r,g,b=rgb.transpose(2,0,1);yy,xx=np.indices((H,W))
    # Terrain measurement only: these masks constrain the separate symbols, not the original pixels.
    ocean_indices=[0,1,2,4,5,54,55,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95]
    ocean=nd.gaussian_filter(np.isin(q,ocean_indices).astype(np.float32),1.05)>.57
    l,n=nd.label(nd.binary_closing(~ocean,np.ones((3,3))));counts=np.bincount(l.ravel());counts[0]=0
    big=nd.binary_fill_holes(l==int(np.argmax(counts)));assert big.mean()>.24 and big.mean()<.64
    volc=nd.binary_fill_holes((~ocean)&(xx>=23)&(xx<135)&(yy>=31)&(yy<=111))
    ice=nd.binary_fill_holes((~ocean)&(xx>=27)&(xx<178)&(yy>=240)&(yy<=308))
    island=nd.binary_fill_holes((~ocean)&(xx>=50)&(xx<=111)&(yy>=176)&(yy<=231))
    island2=nd.binary_fill_holes((~ocean)&(xx>=216)&(xx<=259)&(yy>=228)&(yy<=260))
    land=big|volc|ice|island|island2
    interior=nd.distance_transform_edt(land)
    rough=nd.gaussian_filter(np.abs((r*.32+g*.56+b*.12)-nd.gaussian_filter(r*.32+g*.56+b*.12,1.6)),2.4)
    # Keep icons adjacent to rather than over major original art; very dark/high-contrast bases
    # receive a placement penalty. Ground and its printed cloud borders always remain unmodified.
    richness=nd.uniform_filter(((g-r>8)|(b-r>8)|(r<126)).astype('f'),size=9)
    forest=nd.gaussian_filter(((g-r>0)&(g-b>12)).astype('f'),4)
    water=nd.gaussian_filter(((b-r>12)&(g-r>5)).astype('f'),5)
    e=(xx>=389)&(yy<=229);north=(yy<111)&(xx>=214);south=yy>=214;west=xx<220
    zones={
       'volcans':volc,'neiges':ice,'archipel':((~land)&(xx<220)&(yy>43)&(yy<310))|island,
       'ouest':big&west&~south,'nord':big&north,'centre':big&~(e|north|south|west),
       'est':big&e&~north,'sud':(big&south&~e)|island2,
    }
    # Save a small independent grid to audit positions, never served in the viewer.
    Image.fromarray(land).save(CACHE/'Masqueterres.png'); print('Terres EoS',round(big.mean(),3), {k:int(z.sum()) for k,z in zones.items()},flush=True)
    return land,interior,rough,richness,forest,water,zones


def sample_sprite(i,old,im,for_map=True):
    o=im.crop((old[0],old[1],old[0]+old[2],old[1]+old[3]));typ=i['type']
    if i.get('premiere_zone'):w=max(6,round(o.width/2.65))
    else:w=max(6,min(9,round((o.width+(2 if typ=='bourg' else 0))/2.9)))
    h=max(3,round(o.height*w/o.width));return o.resize((w,h),NN)


def placer(plate,rows,sourcearts):
    land,margin,rough,rich,foret,eau,zones=grounds(plate);faces=np.stack([np.asarray(p) for p in plate]);npins=np.full((H,W),1000.,np.float32);taken=np.zeros((H,W),bool);y,x=np.indices((H,W));regional=Counter();out={}
    safe=((x-225)/48)**2+((y-172)/37)**2>1
    border=(x>=12)&(x<W-13)&(y>=22)&(y<H-22)
    # Foot placements are integral at the real DS scale. No new terraforming under any icon.
    def reserve(row,sprite,x0,y0,area):
        b=rect(x0,y0,*sprite.size);l,t,r,s=b
        assert not np.any(taken[t:s,l:r]),(row['id'],b);taken[max(t-2,0):s+2,max(l-2,0):r+2]=True
        np.minimum(npins,((x-x0)**2+(y-y0)**2)**.5,out=npins)
        exposure=np.mean(faces[:,max(0,t-1):s+1,max(l-1,0):r+1]==faces[-1,max(0,t-1):s+1,max(l-1,0):r+1],axis=(1,2));steps=[k for k in range(8) if np.all(exposure[k:]>=.89)]
        first=0 if area=='destiny' else max(1,min(steps));assert area!='destiny' or exposure[0]>.9,(row['id'],exposure[0])
        z={**row,'region_ancien_atlas':row['region'],'region':area,'ancre':grow((x0,y0)),'rect':grow(b),'ancre_eos_native':[x0,y0],'apparition':first}
        out[row['id']]=(z,sprite);regional[area]+=1
    by={r['id']:r for r in rows}
    for i,(x0,y0) in DEP.items():reserve(by[i],sourcearts[i],x0,y0,'destiny')
    # Big eponymous sites get first choice of nearby pixels. Details should have space between them.
    order=[by[i] for i in HERO if i in by]+[r for r in rows if r['id'] not in DEP and r['id'] not in HERO]
    for ix,row in enumerate(order):
        i=row['id'];s=sourcearts[i];w,h=s.size;k=row['type'];preferred=HERO.get(i);old=row['region']
        if preferred:groups=[preferred[0]]
        elif k=='glace':groups=['neiges']
        elif k=='volcan':groups=['volcans']
        elif k=='mer':groups=['archipel']
        else:groups=SECTOR[old][:]
        picks=np.full((H,W),-1e7,np.float32);chosen=np.int8(np.zeros((H,W)))
        # The rectangle is checked exactly by a summed-area table, including negative overhang.
        l=(x-w//2).clip(0,W);r=(x-w//2+w).clip(0,W);t=(y-h).clip(0,H);b=y
        sat=np.pad(taken.astype(np.int32),((1,0),(1,0))).cumsum(0).cumsum(1)
        valid=(sat[b,r]-sat[t,r]-sat[b,l]+sat[t,l]==0)&safe&border
        proximity=np.minimum(npins,26 if preferred else 43)
        variety=((15*x+31*y+(ix+1)*(9*x+6*y+37))%43)/42.
        quality=-.56*rough-7*rich+(8*foret if k=='foret' else 0)+(11*eau if k=='eau' else 0)+(1*np.minimum(margin,6))
        for rank,area in enumerate(groups+[a for a in QUOTAS if a not in groups]):
            # A hero can also be offshore (cloud stairs or the white tower on the printed map).
            zone=zones[area]
            if preferred and area==preferred[0]:
                u,v=preferred[1:];dist=np.hypot(x-u,y-v)
                if i in ('monde-159','monde-219','monde-189'):
                    zone=zone|(dist<12)
                local=np.clip(90-1.8*dist,-15,90)
            else:local=0
            limit=QUOTAS.get(area,100);excess=regional[area]-limit
            rate=(-12.5*max(0,excess) if limit<100 else 0)+(-3.5*rank)
            if area in ('neiges','volcans'):rate+=43
            elif area=='archipel' and (k=='mer' or old=='mer'):rate+=21
            elif area=='archipel':rate-=18
            legality=zone&valid&(npins>=8)
            fit=np.where(legality,quality+.86*proximity+variety*2+local+rate,-1e7)
            best=fit>picks;picks[best]=fit[best];chosen[best]=VARS[area]
        u=int(np.argmax(picks));ay,ax=divmod(u,W);assert picks[ay,ax]>-999999,(i,groups)
        region=next(rn for rn,num in VARS.items() if num==chosen[ay,ax]);reserve(row,s,ax,ay,region)
    assert len(out)==150 and all(k in regional for k in REGIONS);print('150 décors replacés',dict(regional),flush=True)
    for q in out.values():yield q


def paths_layer():
    p=Image.new('RGBA',(W,H));d=ImageDraw.Draw(p)
    for pts in PATHS.values():
        d.line(pts,fill=(107,77,42,133),width=1)
        for a,b in zip(pts,pts[1:]):
            n=max(abs(b[0]-a[0]),abs(b[1]-a[1]));u=range(0,n,2)
            for k in u:d.point((round(a[0]+k*(b[0]-a[0])/n),round(a[1]+k*(b[1]-a[1])/n)),fill=(249,220,153,225))
    p.resize(WIDE,NN).save(A/'Chemins.png',optimize=True)
    return p


def main():
    plate=extract();prior=json.loads((PREV/'Lieux.json').read_text());rows=prior['lieux'];base=plate[-1].convert('RGB');assert len(rows)==150
    raw=Image.open(PREV/'Lieux-150.png').convert('RGBA');rawanim=Image.open(PREV/'Animations.png').convert('RGBA');art={p['id']:sample_sprite(p,p['sprite'],raw) for p in rows}
    # Original illustrated miniatures, byte for byte, for the index and detail cards.
    (A/'Lieux-150.png').write_bytes((PREV/'Lieux-150.png').read_bytes())
    loc=list(placer(plate,rows,art));loc.sort(key=lambda k:next(i for i,p in enumerate(rows) if p['id']==k[0]['id']))
    atlas=Image.new('RGBA',(PITCH*15,PITCH*10));anim=Image.new('RGBA',(8*PITCH,prior['animations']*PITCH));ani_count=0
    for k,(p,sp) in enumerate(loc):
        w,h=sp.size;xy=(k%15*PITCH+1,k//15*PITCH+1);scaled=sp.resize((w*S,h*S),NN);atlas.paste(scaled,xy);p['carte']=[*xy,*scaled.size]
        if 'animation' in p:
            i=p.pop('animation');uw,uh=p['sprite'][2:];frames=[]
            for zz in range(8):
                x,y=zz*PITCH+1,i*PITCH+1;frames.append(rawanim.crop((x,y,x+uw,y+uh)).resize(sp.size,NN).resize(scaled.size,NN))
            assert frames[0].tobytes()==scaled.tobytes()
            if len({fr.tobytes() for fr in frames})>1:
                for j,fr in enumerate(frames):anim.paste(fr,(j*PITCH+1,ani_count*PITCH+1))
                p['animation']=ani_count;ani_count+=1
    assert ani_count>20
    atlas.save(A/'Vignettes-carte.png',optimize=True);anim.crop((0,0,8*PITCH,ani_count*PITCH)).save(A/'Animations.png',optimize=True)
    comp=base.convert('RGBA');decl=[p for p,_ in loc];assert len(set(p['nom']for p in decl))==150
    for p,sp in sorted(loc,key=lambda q:q[0]['ancre'][1]):comp.alpha_composite(sp,tuple(v//S for v in p['rect'][:2]))
    comp=comp.convert('RGB');comp.resize(WIDE,NN).save(A/'Monde-150.png',optimize=True);comp.resize((W*12,H*12),NN).save(ROOT/'Monde-Destiny-EoS-6048x4032.png',optimize=True)
    routes=paths_layer();seen=plate[0].convert('RGBA');seen.alpha_composite(routes)
    for p,sp in loc[:5]:seen.alpha_composite(sp,tuple(v//S for v in p['rect'][:2]))
    seen.crop(START_BOX).resize((864,648),NN).save(CACHE/'Reverie-EoS.png',optimize=True)
    comp.resize((1008,672),NN).save(CACHE/'Monde-EoS-avec-lieux.png',optimize=True)
    j={**prior,'version':4,'taille':list(WIDE),'regions':REGIONS,'par_region':dict(Counter(p['region']for p in decl)), 'animations':ani_count,'depart':{'centre':grow(DEP['reverie']),'cadre':grow(START_BOX),'chemins':{s:[grow(u)for u in pts] for s,pts in PATHS.items()}},'lieux':decl,'eos':{'cadrages_source':[list(x) for x in frame_boxes()],'taille_native':[W,H],'echelle':S,'colonnes':4,'nb_feuillets':8,'source_sha256':hashfile(SRC),'source':'Planche Explorateurs du Ciel fournie par l’utilisateur','temps_ms':[0,3600,5100,6650,8200,9900,11800,14500],'fondu_ms':600,'duree_ms':15750}}
    output(A/'Lieux.json',j);print('Phases de découverte',dict(sorted(Counter(p['apparition'] for p in decl).items())),'· animations',ani_count,flush=True)

if __name__=='__main__':main()
