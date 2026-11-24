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
from Miniatures import mountain,tree,dune,rock,site,cloud,nautic,canopy,scarp,dune_long,NN

ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'Sources'; C=ROOT/'Calques'; C.mkdir(exist_ok=True)
DES=json.loads((SRC/'Geographie.json').read_text()); W,H=SIZE=tuple(DES['taille']); Z=DES['zoom_export']
YY,XX=np.mgrid[:H,:W]; X=XX.astype(np.float32);Y=YY.astype(np.float32);RNG=np.random.default_rng(DES['graine'])
P=lambda c:np.array(tuple(bytes.fromhex(c.lstrip('#'))),dtype=np.float32)
RGB=lambda c:tuple(bytes.fromhex(c.lstrip('#')))
sha=lambda p:sha256(p.read_bytes()).hexdigest()
DUMP=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
BARE=SRC/'Fond-nu-original.png';BARE_SHA='67e1bf2020a11b1d0dcdb4ea9400eb4cd75e2ada19b48f80c8420f5ea798c1d3'

BASE={'verd':'c9ae62','givre':'d2ded2','cendre':'b2926b','palus':'b0a16a','metano':'c9b772','ambre':'e6b063','vesp':'c5aa70','flor':'cfb675','reve':'c9b06a'}
LAND={k:P(v) for k,v in {'forest':'899753','pine':'9da672','rock':'c79154','meadow':'d6c078','sand':'ebbe72','snow':'e2e7d6','ice':'b8d5d0','ash':'957a63','ember':'cf905d','clay':'d2955a','marsh':'8d955c','petal':'c8a176','tropic':'9fa65b'}.items()}
MAP_THEME={'verd':'forest','givre':'snow','cendre':'ash','palus':'marsh','metano':'pine','ambre':'clay','vesp':'rock','flor':'petal','reve':'forest'}
WAT={'lake':('4b6470','538794','73b5b5','97cebf','def0d3'),'marais':('56644a','62866b','82a87d','a8c58a','dfdaa9'),'thermale':('69624f','6a9382','83b8a1','add2ae','e9e3c0'),'oasis':('6c694e','5a9695','78b6a4','a0cabe','e8e6b1'),'lave':('82573b','ad593b','d77746','f4a35c','ffde88')}


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
    main=[only_big(mask_from_poly(reg['cote'])) for reg in DES['regions']]
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
        base=np.zeros((H,W,3),np.float32)+P(BASE[r['id']]); strongest=np.zeros((H,W),np.float32)+.38
        default={'givre':'snow','cendre':'ash','ambre':'sand','palus':'marsh','flor':'meadow','reve':'meadow'}.get(r['id'],'meadow')
        dominant[m]=default
        for k,f in ph.items():
            sel=m & (f>strongest);dominant[sel]=k;strongest[sel]=f[sel]
            sel=m
            w=f[sel,None]*.84;base[sel]=base[sel]*(1-w)+LAND[k]*w
        # Broad slopes toward authored ridge lines, never a height map sampled from another game.
        ridge=Image.new('L',SIZE); rd=ImageDraw.Draw(ridge)
        for nodes in r['ridges']:rd.line(path_pts(nodes),fill=255,width=3)
        proximity=nd.distance_transform_edt(np.asarray(ridge)==0)
        T=np.exp(-np.square(proximity/22)).astype(np.float32)
        elev[m]=T[m]
        base[m]+=T[m,None]*np.array([-3.5,-4.3,-4],np.float32)
        terrain[m]=base[m]
    for j,(x,y,rx,ry,k) in enumerate(DES['ilots'],101):
        small=Image.new('L',SIZE);ImageDraw.Draw(small).polygon([(round(xx),round(yy))for xx,yy in spline(jagged(x,y,rx,ry,(j*13)%86-40,j,11),True,2)],fill=255)
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
    sand=m&(di>2.3)&(di<6.2+n2*1.2)&~((sections==2)|(sections==3))
    terrain[sand]=terrain[sand]*.75+P('edc17c')*.25
    darkedge=np.maximum(0,4.1-di)[:,:,None]/4.1
    terrain[m]-=darkedge[m]*np.array([11,10,7]);
    terrain[light]+=np.array([13,12,7])
    forefront=m&~np.roll(m,-4,axis=0)&(sections<10)
    cliff=forefront & (n1+.35*n2 > -.13) & (sections!=4) & (sections!=6)
    face=cliff&~rim
    terrain[face]=terrain[face]*.53+P('a87b4a')*.47
    face2=face&(sections==2);terrain[face2]=terrain[face2]*.50+P('939b8c')*.50
    cuts=face&(np.mod(XX+(n3*2).astype(int),6)<1)&(di<3.1)
    terrain[cuts]-=[10,14,12]
    ink=.64+.065*(n2>0)+.055*forefront
    terrain[rim]=terrain[rim]*(1-ink[rim,None])+P('795333')*ink[rim,None]
    ice_rim=rim&(sections==2);terrain[ice_rim]=terrain[ice_rim]*.57+P('6b7271')*.43
    a=np.where(m,255,0).astype(np.uint8)
    aswash=(do>0)&(do<=5.3)
    terrain[aswash]=P('f2c986')+GRAIN[aswash,None]*[.5,.6,.4]
    a[aswash]=np.clip(np.rint(91*(1-do[aswash]/5.6)),8,91).astype(np.uint8)
    shelf=(do>=1.4)&(do<=3.1)&(np.roll(m,2,axis=0)|np.roll(m,3,axis=1))
    terrain[shelf]=P('a67340');a[shelf]=np.maximum(a[shelf],112)
    surf=(do>3.4)&(do<=4.47)&(n1+.42*n2>.03)&(np.mod(XX+2*YY,9)!=0)
    terrain[surf]=P('fbd598');a[surf]=101
    return main,sections,m,di,do,dominant,probs,elev,rgba(terrain,a)

def lake_pts(L,i):return [(round(x),round(y))for x,y in spline(jagged(L['x'],L['y'],L['rx'],L['ry'],L.get('rot',0),1000+i,16),True,1.5)]

def water(raster,regions):
    hydro=Image.new('RGBA',SIZE);d=ImageDraw.Draw(hydro);wet=Image.new('L',SIZE);wd=ImageDraw.Draw(wet)
    for j,r in enumerate(regions):
      for i,river in enumerate(r['rivers']):
        typ=river.get('eau','lake') if isinstance(river,dict) else 'lake';nodes=river['p'] if isinstance(river,dict) else river
        pt=path_pts(nodes,1.7);e,b,c,l,hi=[('#'+v)for v in WAT[typ]]
        lengths=[0.]
        for u,v in zip(pt,pt[1:]):lengths.append(lengths[-1]+math.dist(u,v))
        vari=[round(1+(2 if j in (4,8) else 1.6)*(s/max(lengths[-1],1))**1.1) for s in lengths]
        if typ=='lave':vari=[1+(i%2==0 and k>len(pt)*.22) for k in range(len(pt))]
        # Ink the cut banks, then the water. Smaller headwaters, broader mouths.
        for k,(x,y) in enumerate(pt):
            brush=vari[k];d.rectangle((x-brush,y-brush,x+brush,y+brush),fill=e);wd.rectangle((x-brush,y-brush,x+brush,y+brush),fill=255)
        for k,(x,y) in enumerate(pt):
            brush=vari[k]-1;d.rectangle((x-brush,y-brush,x+brush,y+brush),fill=b)
        d.line([(x-1 if r>1 else x,y) for (x,y),r in zip(pt[1:-1],vari[1:-1])],fill=(l if typ=='lave' else c),width=1)
        for k in range(3,len(pt)-2,6):
            x,y=pt[k];d.point((x-(vari[k]>1),y),fill=(hi if typ=='lave' else l))
      for i,L in enumerate(r['lakes']):
        pt=lake_pts(L,j*23+i);x,y=L['x'],L['y'];e,b,c,l,hi=[('#'+v)for v in WAT[L.get('eau','lake')]]
        d.polygon(pt,fill=b,outline=e);wd.polygon(pt,fill=255)
        n=math.ceil(L['rx']*L['ry']*.042)
        d.polygon([(round(x+(a-x)*.86-1),round(y+(q-y)*.80-1))for a,q in pt],fill=c)
        # A second depth face on the lower half follows the pixels of the banks.
        bot=[(round(x+(a-x)*.87),round(y+(q-y)*.81))for a,q in pt if q>y+L['ry']*.23]
        if len(bot)>3:d.line(sorted(bot),fill=b,width=1)
        top=sorted((p for p in pt if p[1]<y-2),key=lambda o:o[0]);
        if len(top)>2:
            d.line([(a,q-1)for a,q in top[len(top)//6:len(top)*3//4]],fill='#d8c087',width=1)
        # interrupted light bands across the water like on the original DS charts
        local=Image.new('L',SIZE);ImageDraw.Draw(local).polygon(pt,fill=255); lm=np.asarray(local)>0
        rng=np.random.default_rng(j*8345+i+331)
        for _ in range(n):
            xx=int(x+rng.integers(-L['rx']+1,L['rx']));yy=int(y+rng.integers(-L['ry']-1,L['ry']+2));sz=int(rng.integers(2,7))
            if all(lm[yy,k] for k in range(xx-1,xx+sz+1)):d.line((xx,yy,xx+sz-1,yy),fill=l if _%3 else hi,width=1)
    a=np.array(hydro);a[~raster]=0
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
    out=Image.new('RGBA',SIZE);g=ImageDraw.Draw(out);items=[];blk=wet.copy();ridge_dots=np.zeros((H,W),bool)
    for r in DES['regions']:
        for s in r['sites']:
            x,y,a,b=crop_for_site(s);blk[max(0,y-3):b+3,max(0,x-3):a+3]=True
    wetd=nd.distance_transform_edt(~wet)
    def add(a,x,y,rid,check=.58,ground=1):
        x=int(x);y=int(y);xl=x-a.width//2;xr=xl+a.width;yt=y-a.height+2;yb=y+2
        if not(0<=xl<xr<=W and 0<=yt<yb<=H) or sections[y,x]!=rid or dist[y,x]<ground:return False
        cut=sections[yt:yb,xl:xr]==rid
        if cut.mean()<check or blk[max(0,y-7):y+3,max(0,x-4):x+5].mean()>.36 or wetd[y,x]<2.:return False
        items.append((y,x,a));return True
    GROVES={
        'verd':[(180,151,30,'forest'),(198,160,33,'forest'),(213,144,30,'forest'),(204,179,26,'forest'),(184,185,24,'forest'),(182,223,28,'forest'),(201,237,21,'forest'),(265,183,23,'forest')],
        'givre':[(467,139,19,'pine'),(500,147,22,'pine'),(514,151,16,'pine'),(593,196,19,'pine'),(566,159,15,'snow')],
        'palus':[(349,362,22,'marsh'),(357,369,24,'marsh'),(379,338,23,'marsh'),(424,418,25,'marsh'),(415,445,27,'marsh'),(466,423,23,'marsh'),(488,433,20,'marsh'),(478,341,21,'marsh')],
        'metano':[(746,383,26,'pine'),(760,402,25,'pine'),(768,414,24,'pine'),(916,453,21,'forest'),(902,470,28,'forest'),(874,481,27,'forest'),(862,494,24,'forest')],
        'vesp':[(447,608,20,'pine'),(454,618,22,'pine'),(477,614,19,'pine'),(488,602,18,'pine')],
        'flor':[(825,587,22,'tropic'),(832,616,26,'tropic'),(932,557,21,'petal'),(955,577,27,'petal'),(900,603,24,'petal'),(993,605,25,'tropic'),(1006,646,24,'tropic'),(982,662,22,'tropic'),(934,655,24,'petal')],
        'reve':[(565,318,16,'forest'),(564,326,18,'forest'),(586,281,17,'forest'),(682,313,13,'pine'),(644,354,15,'meadow')],
    }
    DUNES=[[(132,518),(154,508),(193,507),(220,492)],[(152,551),(185,558),(217,547),(252,550)],[(219,580),(246,575),(276,568),(294,561)],[(178,628),(212,639),(243,621),(270,620)]]
    for k,r in enumerate(DES['regions'],1):
        g0=MAP_THEME[r['id']]; rng=np.random.default_rng(922+791*k)
        for i,rd in enumerate(r['ridges']):
            step=(14 if g0=='snow' else 16 if r['id'] not in ('reve','palus') else 19)
            pos=list(along(rd,step))
            for j,(x0,y0) in enumerate(pos):
                x=round(x0+rng.uniform(-5.5,5.5));y=round(y0+rng.uniform(-2,5))
                if sections[y,x]!=k:continue
                theme=g0
                if g0=='petal':theme='forest' if j%3 else 'petal'
                if g0=='ash' and i>0:theme='ember' if j%3 else 'ash'
                w=int(rng.integers(16,31)) if g0!='marsh' else int(rng.integers(13,24))
                if g0=='snow':w+=4
                if r['id']=='reve':w=round(w*.66)
                h=round(w*(rng.uniform(.72,1.04) if g0 in ('snow','ash') else rng.uniform(.63,.85)))
                a=mountain(theme,int(rng.integers(0,4)),w,h)
                if add(a,x,y,k,.61,3):
                    ridge_dots[max(0,y-10):y+7,max(0,x-w//2):x+w//2]=True
                    if j%3!=2:
                        a=rock(j,round(w*.52),theme);add(a,x+round(rng.uniform(-13,13)),y+round(rng.uniform(4,9)),k,.7,4)
        for j,(x,y,w,b) in enumerate(GROVES.get(r['id'],[])):
            if add(canopy(b,j+k,w),x,y,k,.63,3):
                ridge_dots[max(0,y-6):y+3,max(0,x-w//2):x+w//2]=True
        if r['id']=='ambre':
            for i,lines in enumerate(DUNES):
                for j,(x,y) in enumerate(lines):
                    w=int(rng.integers(25,36));add(dune_long(i+j,w),x,y,k,.74,4)
                    ridge_dots[max(0,y-8):y+3,max(0,x-w//2):x+w//2]=True
        if r['id'] in ('cendre','vesp','ambre'):
            for j,rd in enumerate(r['ridges']):
                for k0,(xx,yy) in enumerate(along(rd,24.6)):
                    x=round(xx+rng.uniform(-6,6));y=round(yy+rng.uniform(12,23))
                    if 0<y<H and 0<x<W and not ridge_dots[y,x]:
                        if rng.random()<.69:add(scarp(j+k0,int(rng.integers(17,30)),g0),x,y,k,.62,4)
        xa,ya,xb,yb=bounds(sections==k)
        for cy in range(ya+6,yb,9):
            for cx in range(xa+5,xb,10):
                x=int(np.clip(cx+rng.integers(-5,6),2,W-3));y=int(np.clip(cy+rng.integers(-4,5),4,H-2))
                if sections[y,x]!=k or dist[y,x]<3 or wetd[y,x]<2 or blk[y,x] or ridge_dots[y,x]:continue
                b=dom[y,x];p=rng.random();q=float(np.clip(.8+.48*n1[y,x]+.31*n2[y,x],.5,1.1))
                if b=='sand' and g0 in ('clay','ember','ash'):
                    if p<.48:
                        z=int(rng.integers(9,18));add(dune(cy+cx,z),x,y,k,.72,4)
                    if p>.88:add(rock(cy+cx,int(rng.integers(5,11)),'clay'),x,y,k,.72)
                elif b in ('snow','ice'):
                    if p<.30 and q>=.68:add(tree('snow',cy,int(rng.integers(5,13))),x,y,k,.75)
                    elif p>.84:add(rock(cx,int(rng.integers(7,12)),'snow'),x,y,k,.68)
                elif b in ('ash','ember','clay','rock') and g0 not in ('forest','pine'):
                    if p<.44:add(rock(cx+cy,int(rng.integers(5,14)),b),x,y,k,.68)
                    elif p>.94 and b!='ash':add(tree('meadow',cy,int(rng.integers(5,11))),x,y,k)
                elif b in ('forest','marsh','pine','petal','tropic'):
                    strength=probs[r['id']].get(b)
                    v=.7 if strength is None else strength[y,x]
                    if p<(.29+.49*v)*q:
                        w=int(rng.integers(6,14) if b!='petal' else rng.integers(7,13));add(tree(b,int(p*100),w),x,y,k,.63)
                        if p<.15 and wetd[y,x]>4.:add(tree(b,cx,max(5,w-3)),x+int(rng.choice([-5,5])),y+2,k,.65)
                    elif p>.94:add(rock(cy,int(rng.integers(5,9)),g0),x,y,k)
                else:
                    # Quiet grasslands are intentionally less crowded, with sprigs, tiny stones and hatches.
                    if p<.12:add(tree('meadow',cy+cx,int(rng.integers(5,11))),x,y,k,.69)
                    elif p>.91:add(rock(cx,int(rng.integers(5,12)),g0),x,y,k,.71)
        # Tiny grouped strokes, not a global overspray of noise.
        for _ in range(round((xb-xa)*(yb-ya)/58)):
            x=int(rng.integers(xa+1,xb-2));y=int(rng.integers(ya+1,yb-2))
            if sections[y,x]!=k or dist[y,x]<2.6 or blk[y,x] or wetd[y,x]<1.:continue
            b=dom[y,x]
            tone={'snow':('#a3b1ab','#e2dec7'),'ice':('#99b2aa','#d4dfc9'),'ash':('#8c7459','#caa47b'),'ember':('#9e6c49','#e4b276'),'clay':('#a7794e','#e7bb76'),'sand':('#b98a4b','#f1d285'),'marsh':('#777d53','#c4b879'),'tropic':('#879353','#c4b772'),'petal':('#a68769','#e3bd94')}.get(b,('#a18f56','#debc72'))
            if rng.random()<.6:
                dx=int(rng.integers(1,4));g.line((x,y,x+dx,y-1),fill=tone[0]);g.point((x,y-1),fill=tone[1])
            else:g.point((x,y),fill=tone[0]);g.point((x+1,y),fill=tone[1])
    for j,(x,y,rx,ry,b) in enumerate(DES['ilots'],101):
        if b in ('snow','ash','ice','rock','ember','clay') or j%4 in (0,1):
            theme={'ice':'snow','meadow':'forest','tropic':'forest','sand':'sand'}.get(b,b);add(rock(j,round(min(rx*1.1,20)),theme),x,y+2,j,.58)
        else:add(tree(b,j,round(min(rx,12))),x,y+1,j,.56)
        if rx>=20:add(tree(b,j+1,9),x+8,y+4,j,.6)
    for y,x,a in sorted(items,key=lambda o:(o[0],o[1])):on(out,a,x,y)
    return out,len(items)


def orn(m,sea_dist):
    v=Image.new('RGBA',SIZE);w=Image.new('RGBA',SIZE)
    for i,(x,y,side) in enumerate(DES['courants']):
        a=nautic((i+1)%2);a=ImageOps.mirror(a) if side<0 else a
        if sea_dist[y,x]>7 and not m[y-a.height:y,x-a.width//2:x+(a.width+1)//2].any():on(v,a,x,y)
    for x,y in [(377,500),(749,475),(271,371),(1025,503),(384,113)]:
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


def render(cache):
    assert sha(BARE)==BARE_SHA and Image.open(BARE).size==(556,366)
    frame=Image.open(BARE).convert('RGB').resize(SIZE,NN).convert('RGBA')
    a,sect,land,dist,od,dom,probs,elev,earth=compose_shapes();regions=DES['regions']
    hydro,wet=water(land,regions);detail,count=decor(sect,land,dist,dom,probs,elev,wet);o,brume=orn(land,od)
    highlights=Image.new('RGBA',SIZE);places=[]
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
    }
    flat_export=ROOT/f'Carte-des-Continents-Destiny-{W*Z}x{H*Z}.png';flat.resize((W*Z,H*Z),NN).save(flat_export,optimize=True)
    # Draw the island vignette from its own land and its six places, on the same temperate sheet.
    island=frame.copy(); shy=regions[-1]['id']; island_ink=nd.distance_transform_edt(sect!=9)<=6
    for layer in (terrain,detail):
        ar=np.array(layer);ar[~island_ink]=0;island.alpha_composite(Image.fromarray(ar))
    local=path_local();ar=np.array(local);ar[sect!=9]=0;island.alpha_composite(Image.fromarray(ar))
    for a0 in sorted((p for p in places if p['region']==shy),key=lambda p:p['position'][1]):on(island,site(a0['type']),*a0['position'])
    cropped=island.convert('RGB').crop(tuple(DES['cote_vue_reverie']));cropped.resize((cropped.width*Z,cropped.height*Z),NN).save(ROOT/'Ile-de-Reverie.png',optimize=True)
    ready=[]
    for j,r in enumerate(regions,1):
        x,y,u,v=bounds(sect==j); mx=(x+u)/2;my=(y+v)/2
        crop=(max(0,x-14),max(0,y-15),min(W,u+14),min(H,v+18))
        sample=ImageOps.fit(flat.crop(crop),(142,83),Image.Resampling.NEAREST,centering=(.5,.52))
        ready.append({**{k:r[k] for k in ('id','num','nom','biome','couleur','texte','label')},'bounds':[x,y,u,v],'focus':[round(mx),round(my)],'surface':int(a[j-1].sum()),'image':file(sample,f'Miniatures/Region-{r["id"]}.png')})
    pins={p['id']:p for p in places}; lens=lambda p,q:math.hypot(*[i-j for i,j in zip(pins[p]['position'],pins[q]['position'])])
    assert all(lens('reverie',k)<60 for k in ('fosse','passage','guilde','bois','source'))
    components,n=nd.label(land);area=np.bincount(components.ravel())[1:];majeurs=int(sum(area>=2000));assert majeurs==9,(majeurs,sorted(area)[-12:]);assert n==9+len(DES['ilots']),(n,len(DES['ilots']))
    meta={'nom':'Atlas des continents de Destiny','version':1,'size':[W,H],'export':[W*Z,H*Z],
      'couche_originale':{'sha256':BARE_SHA,'fichier':str(BARE.relative_to(ROOT))},'layers':layers,'regions':ready,'sites':places,
      'continents':8,'ilots':len(DES['ilots']),'reverie_box':DES['cote_vue_reverie'],
      'convention':'Coordonnées d’illustration. Les continents, la position mondiale des lieux et leurs noms nouveaux sont une proposition pour Destiny, pas une donnée du jeu.',
      'natif':native,'ordre':['parchemin','terrain','gravures','reliefs','lieux','nuages'],
      'calques_optionnels': {'sentiers': 'Dans le cadrage de l’île, entre reliefs et lieux.'}}
    DUMP(ROOT/'Calques'/'Atlas.json',meta)
    DUMP(ROOT/'Verification-carte.json',{'statut':'PASS','taille_logique':[W,H],'export':[W*Z,H*Z],'continents':8,'ile_reverie':True,
        'ilots':len(DES['ilots']),'continents_et_ile_9_silhouettes_disjointes':majeurs==9,'ensembles_de_terre':int(n),
        'reliefs_et_arbres':count,'reperes':len(places),'reperes_noms_du_projet':sum(p['existe_dans_le_projet']for p in places),
        'fond_nu_sha256':sha(BARE),'source_geographie': 'Geographie.json (géométrie originale)',
        'taux_de_terre':round(float(land.mean()),4),'distances_depuis_reverie_px':{k:round(lens('reverie',k),2)for k in ('fosse','passage','guilde','bois','source')},
        'plan_sha256':sha(flat_export),'export_sans_texte':True})
    print(f'{majeurs-1} continents + Réverie + {n-9} îlots, {len(places)} lieux, {count} reliefs, terre {land.mean():.1%}, {flat_export.stat().st_size:,} octets')

if __name__=='__main__':
    ap=ArgumentParser(description=__doc__);ap.add_argument('--cache',type=Path);ns=ap.parse_args();render(ns.cache)
