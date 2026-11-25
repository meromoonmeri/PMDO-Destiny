#!/usr/bin/env python3
"""Trace an original Destiny world, from Geographie.json and original pixel drawings.
The sole borrowed raster is the exact user-approved bare parchment. No ROM or game asset required.
"""
from __future__ import annotations
from pathlib import Path
from argparse import ArgumentParser
from hashlib import sha256
from PIL import Image,ImageDraw,ImageOps
from scipy import ndimage as nd
import json,math
import numpy as np
from Miniatures import mountain,tree,dune,rock,cloud,nautic,canopy,scarp,dune_long,NN
from Reperes import site,formation

ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'Sources'; C=ROOT/'Calques'; C.mkdir(exist_ok=True)
DES=json.loads((SRC/'Geographie.json').read_text()); W,H=SIZE=tuple(DES['taille']); Z=DES['zoom_export']
YY,XX=np.mgrid[:H,:W]; X=XX.astype(np.float32);Y=YY.astype(np.float32);RNG=np.random.default_rng(DES['graine'])
P=lambda c:np.array(tuple(bytes.fromhex(c.lstrip('#'))),dtype=np.float32)
RGB=lambda c:tuple(bytes.fromhex(c.lstrip('#')))
sha=lambda p:sha256(p.read_bytes()).hexdigest()
DUMP=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
BARE=SRC/'Fond-nu-original.png';BARE_SHA='67e1bf2020a11b1d0dcdb4ea9400eb4cd75e2ada19b48f80c8420f5ea798c1d3'

REGS=DES['regions']; REVE=next(i for i,r in enumerate(REGS,1) if r['id']=='reve')
NC=sum(r['type']=='continent' for r in REGS)
SILHOUETTES=sum(1+len(r.get('aires',[])) for r in REGS)
LAND={k:P(v) for k,v in {'forest':'899953','pine':'93a275','rock':'c89e67','meadow':'d7c17b','sand':'e8bd76','snow':'dfe6d4','ice':'bfdbd4','ember':'bf8255','clay':'d49661','marsh':'899b67','petal':'c5a17b','tropic':'a4ae62','umber':'c09b62','salt':'e1c893'}.items()}
WAT={'lac':('406171','508897','72b4b3','9bcbb9','dcead2'),'glace':('596c73','6897a8','92c4c9','b4dcd4','e4efe1'),
 'marais':('58694d','638b71','87af87','a5c48d','e1e0ab'),'source':('4c6c68','558f96','7ebdb3','aed4c0','e8efd5'),
 'saline':('766955','8d9e83','b4c7aa','ccd3ad','f0e8cb'),'combe':('805a3b','9e805e','91b49c','c0d3a3','e1e4b2')}


def noise(a,b):
    ar=RNG.integers(3,251,(b,a),dtype=np.uint8)
    return (np.asarray(Image.fromarray(ar).resize(SIZE,Image.Resampling.BILINEAR),np.float32)-127)/127
n1=noise(24,16);n2=noise(83,55);n3=noise(200,136);n4=noise(348,230)
SHORE=n1*2.5+n2*3.7+n3*1.44+np.sin(.41*X+.33*Y)*.56
GRAIN=(n1*8+n2*6+n3*3.1+n4*2.3)

def spline(nodes,close=False,gap=3):
    b=np.asarray(nodes,np.float64)
    q=np.vstack([b[-1:],b,b[:2]]) if close else np.vstack([b[:1],b,b[-1:]])
    parts=[]
    for i in range(len(b) if close else len(b)-1):
        u,v,w,z=q[i:i+4]; length=np.hypot(*(v-w));t=np.linspace(0.,1.,max(3,math.ceil(length/gap)+1),endpoint=False)[:,None]
        ar=.5*((2*v)+(-u+w)*t+(2*u-5*v+4*w-z)*t*t+(-u+3*v-3*w+z)*t*t*t);parts.extend(tuple(map(float,row)) for row in ar)
    if not close:parts.append(tuple(map(float,b[-1])))
    return parts

def path_pts(nodes,gap=3): return [(round(x),round(y)) for x,y in spline(nodes,False,gap)]

def mask_from_poly(ns):
    im=Image.new('L',SIZE);ImageDraw.Draw(im).polygon([(round(x),round(y)) for x,y in spline(ns,True,2)],fill=255)
    m=np.asarray(im)>0;inside=nd.distance_transform_edt(m);outside=nd.distance_transform_edt(~m)
    return nd.binary_closing(inside-outside+SHORE>0,structure=np.ones((3,3)),iterations=1)

def jagged(x,y,rx,ry,rot=0,seed=1,n=16):
    rnd=np.random.default_rng(seed);rot=math.radians(rot)
    out=[]
    for i in range(n):
        a=i*math.tau/n;sc=.8+rnd.random()*.32
        s=math.cos(a)*rx*sc;k=math.sin(a)*ry*sc
        out.append((x+s*math.cos(rot)-k*math.sin(rot),y+s*math.sin(rot)+k*math.cos(rot)))
    return out

def only_big(mask):
    labs,n=nd.label(mask);valid=np.bincount(labs.ravel());valid[0]=0
    return labs==valid.argmax()

def rgba(rgb,a):
    r=np.empty((H,W,4),np.uint8);r[...,:3]=np.clip(np.rint(rgb),0,255).astype(np.uint8);r[...,3]=a;r[a==0]=0;return Image.fromarray(r)

def on(img,sp,x,y):img.alpha_composite(sp,(round(x-sp.width/2),round(y-sp.height+2)))
def file(img,name,sub=C):
    p=sub/name;p.parent.mkdir(parents=True,exist_ok=True);img.save(p,optimize=True);return str(p.relative_to(ROOT).as_posix())

def bounds(m):
    y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1]


def compose_shapes():
    main=[]
    for reg in REGS:
        m=np.zeros((H,W),bool)
        for path in [reg['cote'],*reg.get('aires',[])]:
            a=only_big(mask_from_poly(path))
            assert not (a&m).any(),reg['id']
            m|=a
        main.append(m)
    sections=np.zeros((H,W),np.uint16); probs={};dominant=np.empty((H,W),object);dominant[:]='sand'
    terrain=np.zeros((H,W,3),np.float32);elev=np.zeros((H,W),np.float32)
    for i,(r,m) in enumerate(zip(DES['regions'],main),1):
        assert not np.any((sections>0)&m),r['id'];sections[m]=i
        ph={}
        for cx,cy,rx,ry,k in r['fields']:
            d=((X-cx)/rx)**2+((Y-cy)/ry)**2
            f=np.clip((1.09+.17*n1+.11*n2-d)*1.25,0,1).astype(np.float32)
            ph[k]=np.maximum(ph.get(k,0),f)
        probs[r['id']]=ph
        base=np.zeros((H,W,3),np.float32)+P(r['sol']); strongest=np.zeros((H,W),np.float32)+.38
        default=r['defaut']
        dominant[m]=default
        for k,f in ph.items():
            sel=m & (f>strongest);dominant[sel]=k;strongest[sel]=f[sel]
            sel=m
            w=f[sel,None]*.84;base[sel]=base[sel]*(1-w)+LAND[k]*w
        # Broad slopes toward authored ridge lines, never a height map sampled from another game.
        ridge=Image.new('L',SIZE); rd=ImageDraw.Draw(ridge)
        for ridge_info in r['ridges']:rd.line(path_pts(ridge_info['p']),fill=255,width=3)
        proximity=nd.distance_transform_edt(np.asarray(ridge)==0)
        T=np.exp(-np.square(proximity/22)).astype(np.float32)
        elev[m]=T[m]
        base[m]+=T[m,None]*np.array([-3.5,-4.3,-4],np.float32)
        terrain[m]=base[m]
    for j,(x,y,rx,ry,k,rotation) in enumerate(DES['ilots'],101):
        small=Image.new('L',SIZE);ImageDraw.Draw(small).polygon([(round(xx),round(yy))for xx,yy in spline(jagged(x,y,rx,ry,rotation,j*5+429,12),True,2)],fill=255)
        m=(np.asarray(small)>0)
        assert not np.any((sections>0)&m),('islet',j,x,y)
        sections[m]=j;terrain[m]=LAND[k];dominant[m]=k
    m=sections>0;di=nd.distance_transform_edt(m).astype(np.float32);do=nd.distance_transform_edt(~m).astype(np.float32)
    # Squared-off engraved hatching. All fills stay in a controlled, two-unit texture grid.
    hatch=(np.mod(XX+YY*2+(n2*3).astype(int),8)==0)&(np.mod(YY+(n1*5).astype(int),9)<4)
    small=(np.mod(XX+YY+(n3*7).astype(int),17)==0)&(np.mod(YY,5)<3)
    # Preserve slight echoes of the known graph paper without a new sea texture.
    shade=np.rint((GRAIN*1.18 - (3.6+3.8*(n1>0))*hatch - 6.2*small)/2)*2
    terrain[m]+=shade[m,None]*[1.0,.85,.69]
    # Amber dry beaches and short, vertical facets on the foreground cliffs.
    rim=m&(di<=1.42)
    light=m&(di>1.4)&(di<=3.1)
    sand=m&(di>2.3)&(di<6.2+n2*1.2)
    terrain[sand]=terrain[sand]*.75+P('edc17c')*.25
    darkedge=np.maximum(0,4.1-di)[:,:,None]/4.1
    terrain[m]-=darkedge[m]*np.array([11,10,7]);
    terrain[light]+=np.array([13,12,7])
    forefront=m&~np.roll(m,-4,axis=0)&(sections<101)
    cliff=forefront & (n1+.35*n2 > -.13)
    face=cliff&~rim
    terrain[face]=terrain[face]*.53+P('a87b4a')*.47
    face2=face&((dominant=='ice')|(dominant=='snow'));terrain[face2]=terrain[face2]*.50+P('939b8c')*.50
    cuts=face&(np.mod(XX+(n3*2).astype(int),6)<1)&(di<3.1)
    terrain[cuts]-=[10,14,12]
    ink=.64+.065*(n2>0)+.055*forefront
    terrain[rim]=terrain[rim]*(1-ink[rim,None])+P('795333')*ink[rim,None]
    ice_rim=rim&((dominant=='ice')|(dominant=='snow'));terrain[ice_rim]=terrain[ice_rim]*.57+P('6b7271')*.43
    a=np.where(m,255,0).astype(np.uint8)
    aswash=(do>0)&(do<=5.3)
    terrain[aswash]=P('f2c986')+GRAIN[aswash,None]*[.5,.6,.4]
    a[aswash]=np.clip(np.rint(91*(1-do[aswash]/5.6)),8,91).astype(np.uint8)
    shelf=(do>=1.4)&(do<=3.1)&(np.roll(m,2,axis=0)|np.roll(m,3,axis=1))
    terrain[shelf]=P('a67340');a[shelf]=np.maximum(a[shelf],112)
    surf=(do>3.4)&(do<=4.47)&(n1+.42*n2>.03)&(np.mod(XX+2*YY,9)!=0)
    terrain[surf]=P('fbd598');a[surf]=101
    return main,sections,m,di,do,dominant,probs,elev,rgba(terrain,a)

def lake_pts(L,i):
    ns=L.get('cote') or jagged(L['x'],L['y'],L['rx'],L['ry'],L.get('rot',0),1258+i,16)
    return [(round(x),round(y)) for x,y in spline(ns,True,1.5)]


def water(raster,regions):
    hydro=Image.new('RGBA',SIZE);d=ImageDraw.Draw(hydro);wet=Image.new('L',SIZE);wd=ImageDraw.Draw(wet)
    for j,r in enumerate(regions):
        for i,river in enumerate(r['rivers']):
            pt=path_pts(river['p'],1.40);e,b,c,l,hi=[('#'+v)for v in WAT[river['eau']]]
            vari=[max(1,round(1+(river['largeur']/2-1)*(k/max(len(pt)-1,1))**.73)) for k in range(len(pt))]
            for k,(x,y) in enumerate(pt):
                a=vari[k];d.rectangle((x-a,y-a,x+a,y+a),fill=e);wd.rectangle((x-a,y-a,x+a,y+a),fill=255)
            for k,(x,y) in enumerate(pt):
                a=vari[k]-1;d.rectangle((x-a,y-a,x+a,y+a),fill=b)
            d.line([(x-1 if a>1 else x,y) for (x,y),a in zip(pt[1:-1],vari[1:-1])],fill=c,width=2 if river['largeur']>6 else 1)
            for k in range(4,len(pt)-2,6):
                x,y=pt[k];d.point((x-(vari[k]>1),y),fill=l)
        for i,L in enumerate(r['lakes']):
            pt=lake_pts(L,j*37+i);x,y=L['x'],L['y'];er,br,cr,lr,hr=WAT[L['eau']];e,b,c,l,hi=('#'+o for o in (er,br,cr,lr,hr))
            wd.polygon(pt,fill=255);d.polygon(pt,fill=b,outline=e)
            xa=max(0,min(u for u,v in pt)-2);xb=min(W,max(u for u,v in pt)+3);ya=max(0,min(v for u,v in pt)-2);yb=min(H,max(v for u,v in pt)+3)
            lm=Image.new('L',(xb-xa,yb-ya));ImageDraw.Draw(lm).polygon([(u-xa,v-ya) for u,v in pt],fill=255)
            la=np.asarray(lm)>0;dd=nd.distance_transform_edt(la);ly,lx=np.mgrid[ya:yb,xa:xb]; arr=np.zeros((*la.shape,4),np.uint8)
            arr[la]=(*RGB(er),255)
            arr[dd>1.35]=(*RGB(br),255)
            sh=dd>2.45
            if L.get('cote'):
                sh=dd>4+n2[ya:yb,xa:xb]*1.4
                mid=(lx>871+0.67*(ly-462)+n2[ya:yb,xa:xb]*6) & (dd>8)
                arr[mid]=(*RGB('609fa6'),255)
                sh&=~mid
            arr[sh]=(*RGB(cr),255)
            lit=(dd>=2)&(dd<4)&(ly<y-3)&(np.mod(lx+ly,17)<11)
            arr[lit]=(*RGB(lr),255)
            hydro.alpha_composite(Image.fromarray(arr),(xa,ya))
            rng=np.random.default_rng(8888+j*3403+i)
            n=round((xb-xa)*(yb-ya)*(.009 if L.get('cote') else .025))
            for k in range(n):
                xx=int(rng.integers(xa+2,xb-1));yy=int(rng.integers(ya+1,yb-1));sz=int(rng.integers(2,10 if L.get('cote') else 5));edge=xx+sz-xa
                if edge<la.shape[1] and (dd[yy-ya,xx-xa:edge]>2.7).all():d.line((xx,yy,xx+sz-1,yy),fill=l if k%4 else hi,width=1)
    a=np.asarray(hydro).copy();a[~raster]=0
    return Image.fromarray(a),((np.asarray(wet)>0)&raster)

def along(points,step):
    x=y=None; leftover=step
    for xx,yy in spline(points,gap=2):
        if x is not None:
            leftover+=math.hypot(xx-x,yy-y)
            if leftover>=step:
                leftover-=step;yield xx,yy
        else:yield xx,yy;leftover=0
        x,y=xx,yy

def crop_for_site(s):
    sp=site(s[2]);x,y=s[3:5];left=round(x-sp.width/2);return [left,y-sp.height+2,left+sp.width,y+2]


def decor(sections,raster,dist,dom,probs,elev,wet):
    out=Image.new('RGBA',SIZE);g=ImageDraw.Draw(out);items=[];blk=wet.copy();stamped=np.zeros((H,W),bool)
    for r in REGS:
        for s in r['sites']:
            x,y,a,b=crop_for_site(s);blk[max(0,y-2):b+1,max(0,x-2):a+2]=True
    wetd=nd.distance_transform_edt(~wet)
    def add(a,x,y,rid,check=.58,ground=1,where=True,mark=False):
        x=int(x);y=int(y);xl=round(x-a.width/2);xr=xl+a.width;yt=y-a.height+2;yb=y+2
        if not(0<=xl<xr<=W and 0<=yt<yb<=H) or sections[y,x]!=rid or dist[y,x]<ground:return False
        cut=sections[yt:yb,xl:xr]==rid;opa=np.asarray(a.getchannel('A'))>64
        if not opa.any() or (cut&opa).sum()/opa.sum()<check:return False
        if where and (blk[max(0,y-6):y+2,max(0,x-4):x+5].mean()>.40 or wetd[y,x]<2.):return False
        items.append((y,x,a));
        if mark:stamped[max(0,y-7):y+3,max(0,x-a.width//2):x+a.width//2]=True
        return True
    for k,r in enumerate(REGS,1):
        rng=np.random.default_rng(299+791*k)
        for i,rd in enumerate(r['ridges']):
            for j,(x0,y0) in enumerate(along(rd['p'],rd['step'])):
                x=round(x0+rng.uniform(-4.5,4.5));y=round(y0+rng.uniform(-1,4));theme=rd['style']
                if sections[y,x]!=k:continue
                w=int(rng.integers(*rd['width']));h=round(w*rng.uniform(.70,.90 if theme!='snow' else 1.04))
                if add(mountain(theme,int(rng.integers(0,4)),w,h),x,y,k,.62,2.0,mark=True):
                    if j%3==0:
                        xx=x+round(rng.uniform(-11,11));yy=y+round(rng.uniform(6,10))
                        add(rock(j,round(w*.50),theme),xx,yy,k,.69,3)
        for j,(x,y,w,b) in enumerate(r.get('groves',[])):
            add(canopy(b,j+k,w),x,y,k,.68,2.7,mark=True)
        for j,(kind,x,y,w,t) in enumerate(r.get('reliefs',[])):
            add(formation(kind,j,w,t),x,y,k,.76,2.3,mark=True)
        xa,ya,xb,yb=bounds(sections==k)
        for cy in range(ya+6,yb,9):
            for cx in range(xa+5,xb,10):
                x=int(np.clip(cx+rng.integers(-5,6),2,W-3));y=int(np.clip(cy+rng.integers(-4,5),4,H-2))
                if sections[y,x]!=k or dist[y,x]<3.2 or wetd[y,x]<2.5 or blk[y,x] or stamped[y,x]:continue
                b=dom[y,x];p=rng.random();q=float(np.clip(.84+.62*n1[y,x]+.33*n2[y,x],.40,1.18))
                if b=='salt':
                    if p<.32:add(formation('salt',int(p*20),int(rng.integers(9,20)),'chalk'),x,y,k,.72)
                elif b=='sand' or b in ('clay','ember') and r['id']=='torselune':
                    if p<.39:
                        w=int(rng.integers(9,19));add(dune(cy+cx,w) if b=='sand' else rock(cx, w//2+2,'clay'),x,y,k,.72,3)
                    elif p>.89:add(rock(cy+cx,int(rng.integers(4,11)),'clay'),x,y,k,.72)
                elif b in ('snow','ice'):
                    if p<.18 and q>.6:add(tree('snow',cy,int(rng.integers(6,12))),x,y,k,.76)
                    elif p>.82:add(rock(cx,int(rng.integers(6,13)),'snow'),x,y,k,.66)
                elif b in ('ash','ember','clay','rock'):
                    if p<.36:add(rock(cx+cy,int(rng.integers(5,13)),b),x,y,k,.66)
                    elif p>.89:add(tree('meadow',cy,int(rng.integers(5,11))),x,y,k)
                elif b in ('forest','marsh','pine','petal','tropic','umber'):
                    a=probs[r['id']].get(b);v=.7 if a is None else a[y,x]
                    if p<(.29+.49*v)*q:
                        w=int(rng.integers(6,14));add(tree(b,int(p*100),w),x,y,k,.64)
                        if p<.14 and wetd[y,x]>4:add(tree(b,cx,max(5,w-3)),x+int(rng.choice([-5,5])),y+2,k,.66)
                    elif p>.94:add(rock(cy,int(rng.integers(5,9)),'chalk'),x,y,k)
                else:
                    if p<.14:add(tree('meadow',cy+cx,int(rng.integers(5,11))),x,y,k,.69)
                    elif p>.94:add(rock(cx,int(rng.integers(5,10)),'rock'),x,y,k,.71)
        for _ in range(round((xb-xa)*(yb-ya)/64)):
            x=int(rng.integers(xa+1,xb-2));y=int(rng.integers(ya+1,yb-2))
            if sections[y,x]!=k or dist[y,x]<2.6 or blk[y,x] or wetd[y,x]<1.2:continue
            b=dom[y,x]
            tone={'snow':('#a6b5ac','#e9ebd9'),'ice':('#91b3ae','#d7e9d3'),'ember':('#aa724e','#e4b078'),'clay':('#af8051','#e7b57a'),'salt':('#bda982','#f3dda5'),'sand':('#bd8a50','#f2cf83'),'marsh':('#7a8c59','#b6b76d'),'tropic':('#8d9656','#d0c37a'),'petal':('#ab8766','#e4b893')}.get(b,('#a08d56','#dbba72'))
            if rng.random()<.6:
                dx=int(rng.integers(1,4));g.line((x,y,x+dx,y-1),fill=tone[0]);g.point((x,y-1),fill=tone[1])
            else:g.point((x,y),fill=tone[0]);g.point((x+1,y),fill=tone[1])
    for j,(x,y,rx,ry,b,_rot) in enumerate(DES['ilots'],101):
        if ry<7 or b in ('snow','ash','ice','rock','ember','clay'):
            theme={'ice':'snow','meadow':'forest','tropic':'forest','sand':'sand'}.get(b,b);add(rock(j,round(min(rx*1.1,18)),theme),x,y+1,j,.58,1)
        else:add(tree(b,j,round(min(rx,11))),x,y+1,j,.56,1)
    for y,x,a in sorted(items,key=lambda o:(o[0],o[1])):on(out,a,x,y)
    return out,len(items)

def orn(m,sea_dist):
    v=Image.new('RGBA',SIZE);w=Image.new('RGBA',SIZE)
    for i,(x,y,side) in enumerate(DES['courants']):
        a=nautic((i+1)%2);a=ImageOps.mirror(a) if side<0 else a
        if sea_dist[y,x]>7 and not m[y-a.height:y,x-a.width//2:x+(a.width+1)//2].any():on(v,a,x,y)
    for x,y in DES['voiles']:
        a=nautic(2)
        if sea_dist[y,x]>8 and not m[y-a.height:y,x-a.width//2:x+(a.width+1)//2].any():on(v,a,x,y)
    for i,(x,y,s) in enumerate(DES['nuages']):
        a=cloud(s,i)
        if sea_dist[y,x]>5 and not m[y-a.height:y,x-a.width//2:x+(a.width+1)//2].any():on(w,a,x,y)
    return v,w


def path_local():
    d=Image.new('RGBA',SIZE);c=ImageDraw.Draw(d)
    for ns in DES['sentiers_reverie']:
        for x,y in along(ns,4.5):
            x,y=round(x),round(y)
            c.line((x,y,x+1,y),fill='#805934');c.point((x,y+1),fill='#edc682')
    return d


def routes_maritimes(od):
    a=Image.new('RGBA',SIZE);d=ImageDraw.Draw(a)
    for j,r in enumerate(DES['traversees']):
        for i,(x,y) in enumerate(along(r['p'],7.5)):
            x,y=round(x),round(y)
            if od[y,x]<5.0:continue
            if i%4==0:d.polygon([(x-2,y),(x,y-2),(x+2,y),(x,y+2)],fill='#efd6a1',outline='#724e2e')
            else:d.line((x,y,x+1,y),fill=(100,64,37,205))
    return a


def render(cache):
    assert sha(BARE)==BARE_SHA and Image.open(BARE).size==(556,366)
    frame=Image.open(BARE).convert('RGB').resize(SIZE,NN).convert('RGBA')
    a,sect,land,dist,od,dom,probs,elev,earth=compose_shapes();regions=DES['regions']
    hydro,wet=water(land,regions);detail,count=decor(sect,land,dist,dom,probs,elev,wet);o,brume=orn(land,od)
    highlights=Image.new('RGBA',SIZE);places=[];routes=routes_maritimes(od)
    for rid,r in enumerate(regions,1):
        for s in r['sites']:
            ident,label,k,x,y,desc,*tag=s
            assert sect[y,x]==rid,(ident,x,y,sect[y,x]);im=site(k)
            box=crop_for_site(s);assert min(box)>=0 and box[2]<=W and box[3]<=H
            sp=file(im,f'Miniatures/{ident}.png')
            places.append({'id':ident,'nom':label,'type':k,'region':r['id'],'position':[x,y],'description':desc,
                           'existe_dans_le_projet':bool(tag and tag[0]),'image':sp,'taille':list(im.size),'boite':box})
    for r in sorted(places,key=lambda p:p['position'][1]):
        x,y=r['position'];on(highlights,site(r['type']),x,y)
    # Terrain and water combined for easy compositing; waterways are also included in a readable design source.
    terrain=earth.copy();terrain.alpha_composite(hydro)
    world=frame.copy()
    for layer in [terrain,o,detail,highlights,brume]:world.alpha_composite(layer)
    flat=world.convert('RGB');native=file(flat,'Carte-Destiny-1112x732.png')
    if cache:
        cache.mkdir(parents=True,exist_ok=True);flat.save(cache/'Premiere-carte.png');
        silhouette=Image.new('RGB',SIZE,'#edd299');ds=Image.fromarray(np.where(land,255,0).astype('uint8'));silhouette.paste((84,109,81),(0,0),ds);silhouette.save(cache/'Plan-des-cotes.png')
    layers={
      'parchemin':file(frame.convert('RGB'),'00-Parchemin-1112x732.png'),
      'terrain':file(terrain,'01-Continents-et-eaux.png'),
      'gravures':file(o,'02-Courants-et-voiles.png'),
      'reliefs':file(detail,'03-Reliefs-et-forets.png'),
      'lieux':file(highlights,'04-Lieux.png'),
      'nuages':file(brume,'05-Nuages.png'),
      'sentiers':file(path_local(),'06-Sentiers-Reverie.png'),
      'traversees':file(routes,'07-Traversees-proposees.png'),
    }
    flat_export=ROOT/f'Nouvelles-Terres-Destiny-{W*Z}x{H*Z}.png';flat.resize((W*Z,H*Z),NN).save(flat_export,optimize=True)
    # Draw the island vignette from its own land and its six places, on the same temperate sheet.
    island=frame.copy(); shy='reve'; island_ink=nd.distance_transform_edt(sect!=REVE)<=6
    for layer in (terrain,detail):
        ar=np.array(layer);ar[~island_ink]=0;island.alpha_composite(Image.fromarray(ar))
    local=path_local();ar=np.array(local);ar[sect!=REVE]=0;island.alpha_composite(Image.fromarray(ar))
    for a0 in sorted((p for p in places if p['region']==shy),key=lambda p:p['position'][1]):on(island,site(a0['type']),*a0['position'])
    cropped=island.convert('RGB').crop(tuple(DES['cote_vue_reverie']));cropped.resize((cropped.width*Z,cropped.height*Z),NN).save(ROOT/'Ile-de-Reverie.png',optimize=True)
    ready=[]
    for j,r in enumerate(regions,1):
        x,y,u,v=bounds(sect==j); mx=(x+u)/2;my=(y+v)/2
        crop=(max(0,x-14),max(0,y-15),min(W,u+14),min(H,v+18))
        sample=ImageOps.fit(flat.crop(crop),(142,83),Image.Resampling.NEAREST,centering=(.5,.52))
        ready.append({**{k:r[k] for k in ('id','num','nom','biome','couleur','texte','label','type')},'bounds':[x,y,u,v],'focus':[round(mx),round(my)],'surface':int(a[j-1].sum()),'image':file(sample,f'Miniatures/Region-{r["id"]}.png')})
    pins={p['id']:p for p in places}; lens=lambda p,q:math.hypot(*[i-j for i,j in zip(pins[p]['position'],pins[q]['position'])])
    assert all(lens('reverie',k)<75 for k in ('fosse','passage','guilde','bois','source'))
    components,n=nd.label(land,structure=np.ones((3,3)));areas=np.bincount(components.ravel())[1:]
    assert n==SILHOUETTES+len(DES['ilots']),(n,SILHOUETTES,len(DES['ilots']))
    main_surfaces=[x['surface'] for x in ready if x['type']=='continent']
    assert len(main_surfaces)==NC and min(main_surfaces)>18000
    meta={'nom':DES['nom'],'version':2,'size':[W,H],'export':[W*Z,H*Z],
      'couche_originale':{'sha256':BARE_SHA,'fichier':str(BARE.relative_to(ROOT))},'layers':layers,'regions':ready,'sites':places,
      'continents':NC,'ilots':len(DES['ilots']),'reverie_box':DES['cote_vue_reverie'],
      'convention':'Les côtes et les lieux sont placés à neuf pour cette proposition. Seuls les noms des lieux attestés sont repris du projet. Style EoS, aucune géographie EoS.',
      'natif':native,'planche':flat_export.name,'ordre':['parchemin','terrain','gravures','reliefs','lieux','nuages'],
      'calques_optionnels': {'sentiers':'Entre reliefs et lieux sur Réverie.','traversees':'Au-dessus du parchemin, facultatif.'},
      'routes':[{"nom":r['nom'],'p':r['p']} for r in DES['traversees']]}
    DUMP(C/'Atlas.json',meta)
    DUMP(ROOT/'Verification-carte.json',{'statut':'PASS','taille_logique':[W,H],'export':[W*Z,H*Z],'continents':NC,'ile_reverie':True,
        'iles_des_haltes':1+len(REGS[-1]['aires']),'ilots_satellites':len(DES['ilots']),'ensembles_de_terre':int(n),
        'surfaces_terres_majeures_px2':dict((x['id'],x['surface']) for x in ready if x['type']!='archipel'),
        'fond_nu_sha256':sha(BARE),'source_geographie':'Geographie.json (côtes et coordonnées réécrites à partir d’un canevas vide)',
        'sources_raster':[str(BARE.relative_to(ROOT))],'reliefs_et_arbres':count,'reperes':len(places),
        'reperes_noms_du_projet':sum(p['existe_dans_le_projet']for p in places),'taux_de_terre':round(float(land.mean()),4),
        'distances_depuis_reverie_px':{k:round(lens('reverie',k),2)for k in ('fosse','passage','guilde','bois','source')},
        'plan_sha256':sha(flat_export),'export_sans_texte':True})
    print(f'{NC} continents + Réverie + les Haltes + {len(DES["ilots"])} îlots, {len(places)} lieux, {count} reliefs, terre {land.mean():.1%}, {flat_export.stat().st_size:,} octets')

if __name__=='__main__':
    ap=ArgumentParser(description=__doc__);ap.add_argument('--cache',type=Path);ns=ap.parse_args();render(ns.cache)
