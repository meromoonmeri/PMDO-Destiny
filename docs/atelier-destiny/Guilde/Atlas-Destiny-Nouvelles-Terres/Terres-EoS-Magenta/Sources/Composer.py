#!/usr/bin/env python3
"""Compose the generated land sprites on the approved Destiny geography, with native DS material swatches."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np
import json,math,hashlib

BASE=Path(__file__).resolve().parents[1]; S=BASE/'Sources'; G=BASE/'Generations'; O=BASE/'Terres-separees';O.mkdir(exist_ok=True)
NN=Image.Resampling.NEAREST; AREA=Image.Resampling.BOX
KEY=(255,0,255)
lay=json.loads((S/'Placement-valide.json').read_text());des=json.loads((S/'Geographie-validee.json').read_text());spec={r['id']:r for r in des['regions']}
INDEX=np.array(Image.open(S/'Index-terres-validees.png')); H,W=INDEX.shape; w,h=W//2,H//2
idx=np.array(Image.fromarray(INDEX).resize((w,h),NN)); land=idx>0
wetfull=(np.array(Image.open(S/'Eaux-validees.png'))>0)&(INDEX>0)
water0=Image.open(S/'Eaux-de-reference.png').convert('RGBA'); wcol=np.array(water0.resize((w,h),NN)); wet=(wcol[:,:,3]>0)&land
Y,X=np.mgrid[:h,:w];rng=np.random.default_rng(817642)
FULL=w,h

def bounds(b):
    y,x=np.where(b);return (int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1)

def rf(p):return np.asarray(Image.open(p).convert('RGB'),dtype=np.float32)

def sav(a,p):
    p.parent.mkdir(parents=True,exist_ok=True);a.save(p,optimize=True)

def cyc(tile,x=X,y=Y):return tile[y%tile.shape[0],x%tile.shape[1]]
def small_np(a,sz,filt=AREA):return np.asarray(Image.fromarray(np.clip(a,0,255).astype('uint8')).resize(sz,filt)).astype(np.float32)

def normal(p):
    a=rf(p);r,g,b=a.transpose(2,0,1)
    pink=(r>147)&(b>135)&(g<.59*np.minimum(r,b))&(abs(r-b)<106)
    ids,n=nd.label(nd.binary_closing(~pink,iterations=1));nums=np.bincount(ids.ravel());nums[0]=0;n0=nums.argmax();m=ids==n0
    # Separate anything disconnected, including the extra Orival variant in the raw output.
    assert m.any() and 0.02<m.mean()<.92,p.name
    q=bounds(m);return a[q[1]:q[3],q[0]:q[2]],m[q[1]:q[3],q[0]:q[2]],int((nums>1000).sum())

def match(a,m,s):
    # At the drawing resolution, mask pink *before* sampling. Fill only gaps at silhouette differences.
    l,t,r,b=bounds(s);sz=r-l,b-t
    _,nn=nd.distance_transform_edt(~m,return_indices=True)
    a=a[nn[0],nn[1]]
    pix=small_np(a,sz)*.42+small_np(a,sz,NN)*.58;k=np.asarray(Image.fromarray(m.astype('uint8')*255).resize(sz,NN))>0
    dd,inv=nd.distance_transform_edt(~k,return_indices=True)
    if (~k).any():
        yy,xx=np.mgrid[:k.shape[0],:k.shape[1]]
        dy=inv[0]-yy;dx=inv[1]-xx
        ay=np.clip(np.rint(inv[0]+dy*.45).astype(int),0,k.shape[0]-1);ax=np.clip(np.rint(inv[1]+dx*.45).astype(int),0,k.shape[1]-1)
        ay,ax=inv[0][ay,ax],inv[1][ay,ax]
        pix[~k]=pix[ay,ax][~k]
    q=np.zeros((h,w,3),np.float32);q[t:b,l:r]=pix
    inside=s[t:b,l:r];ratio=np.count_nonzero(k&inside)/np.count_nonzero(k|inside)
    return q,float(ratio)

DEMO={'orival':'Orival','seracine':'Seracine','estrel':'Estrel','torselune':'Torselune','reve':'Reverie','haltes':'Les-Haltes'}
raw=np.zeros((h,w,3),dtype=np.float32);align={}
for cfg in lay['regions']:
    key=cfg['id'];target=idx==cfg['index']
    if key!='haltes':
        a,m,n=normal(G/(DEMO[key]+'.png'));pat,iou=match(a,m,target);raw[target]=pat[target]
        align[key]={'rapport_aire_apres_cadrage_avant_masque':round(iou,4),'composantes_source':n,'source':DEMO[key]+'.png'}
    else:
        # The generation painted the surrounding gold too. Retain the three interior illustrated motifs only.
        a=rf(G/'Les-Haltes.png'); ah,aw=a.shape[:2];regions,n=nd.label(target,structure=np.ones((3,3)))
        pins=sorted(range(1,n+1),key=lambda i:np.where(regions==i)[0].mean());assert len(pins)==3
        for i,box in zip(pins,[(6,107,92,212),(465,315,625,487),(691,554,941,795)]):
            l,t,r,b=(round(v*k) for v,k in zip(box,(aw/1264,ah/844,aw/1264,ah/844)));cand=a[t:b,l:r];this=regions==i
            pat,_iou=match(cand,np.ones(cand.shape[:2],bool),this);raw[this]=pat[this]
        align[key]={'source':'Les-Haltes.png','traitement':'trois prélèvements intérieurs, clé refaite avec les trois masques'}
# Exact patches of hatching, extracted inside the reference land; no old coast is imported.
GOLD=rf(S/'Trame-EoS-Ocre.png');DUNE=rf(S/'Trame-EoS-Sable.png');SHALE=rf(S/'Trame-EoS-Sombre.png');DARK=rf(S/'Trame-EoS-Colline.png'); DIAMOND=rf(S/'Trame-EoS-Losange.png')
A=cyc(GOLD,X+Y//14*3,Y);B=cyc(DUNE,X+14,Y+2);C=cyc(SHALE,X*1+4,Y+3);E=cyc(DARK,X,Y)
# Satellites have their own approved contours. Material adapted from the drawn land throughout the plate.
for n in np.unique(idx[idx>=101]):
    m=idx==n;i=int(n)-101;biome=des['ilots'][i][4];a=A[m].copy();
    if biome=='rock':a=a*.72+E[m]*.28
    if biome=='pine':a=a*.63+np.array([132,153,77])*.37
    if biome=='sand':a=B[m]
    if biome=='clay':a=a*.75+np.array([183,123,55])*.25
    raw[m]=a

# Refine contrasts in the same small-pixel print used in the Nintendo DS source.
R,Gr,Blu=raw.transpose(2,0,1);lum=.299*R+.587*Gr+.114*Blu
possible_water=(Blu>R+12)&(Gr>R+10)&(Blu+23>Gr)&(Blu>95)&(Gr>86)&land
wet_sources=wet|possible_water
for i in np.unique(idx[land]):
    reg=idx==i;k=reg&~wet_sources
    if (reg&possible_water&~wet).any() and k.any():
        dd,j=nd.distance_transform_edt(~k,return_indices=True);take=reg&possible_water&~wet
        raw[take]=raw[j[0][take],j[1][take]]
R,Gr,Blu=raw.transpose(2,0,1);L=.299*R+.587*Gr+.114*Blu
# Ready-to-print chroma zones : strong ochre paper pigment, shaded lozenges in the relief and
# teal/olive tree crowns, with cold stone kept cold and Estrel's sunny salt flats left pale.
base=A.copy();crust=np.maximum(0,R-Gr);grn=(Gr>R*.90)&(Gr>Blu*1.13)&(Gr>65)&(R<194)&(crust<26)&land
cold=(abs(R-Blu)<49)&(Blu>R-27)&(L>120)&(idx==2)&(X<414)&(Y<110)
pale=(R>205)&(Gr>170)&(Blu>96)&(Blu<R*.74)&np.isin(idx,[3,4]);clay=(R>138)&(R-Gr>43)&(Blu<R*.64)&np.isin(idx,[1,4]);
open_area=(L>159)&(R>185)&(R-Gr<62)&(Gr-Blu>36)&~grn&~cold&~pale&~clay&land
hatch=A-(np.array([224,181,75],dtype='f'))
relief=np.clip((169-L)/76,0,1)[...,None];base=base*(1-relief*.66)+C*(relief*.66)
# Convert the broad neutral ground planes to gold. Preserve generated microfeatures and their shading.
sep=np.clip((L-93)/135,0,1)[...,None];shade=np.array([104,70,34])+sep*np.array([139,126,52]);
base=raw*.75+shade*.25
base[open_area]=raw[open_area]*.64+A[open_area]*.36
base[pale]=raw[pale]*.74+B[pale]*.26
base[clay]=raw[clay]*.84+np.array([201,147,66])*.16
base[grn]=raw[grn]*.86+np.array([107,140,78])*.14
# EoS prints the groves onto a tawny surface, rather than flooding their entire biome green.
meadow=grn&(L>131)&(Gr>139)&(nd.gaussian_filter(L,1)-L<11)
base[meadow]=base[meadow]*.59+(A[meadow]*.78+np.array([160,158,69])*.22)*.41
base[cold]=raw[cold]*.85+np.array([189,201,202])*.15
vol=np.where(open_area,.42,np.where(grn,.10,np.where(cold,.08,.13)));base+=hatch*vol[...,None]

# The picture generator's smaller crowns, rocks and buildings remain. To give the ridges the
# true DS rhythm, add original staggered diamond crowns shaded with the sampled printing grain.
# All brush placement follows the approved ridgelines rather than the reference map.
sitekeep=np.zeros((h,w),bool)
for p in lay['sites']:
    l,t,r,b=p['boite'];sitekeep[t//2:(b+1)//2,l//2:(r+1)//2]=True

def pseq(nodes,step):
    acc=0.;xx,yy=nodes[0];yield xx/2,yy/2
    for nx,ny in nodes[1:]:
        dx,dy=nx-xx,ny-yy;d=math.hypot(dx,dy)
        if d==0:continue
        while acc+step<=d:
            acc+=step;f=acc/d;yield (xx+dx*f)/2,(yy+dy*f)/2
        acc-=d;xx,yy=nx,ny

def ridge_art(w0,h0,theme,seed):
    rv=np.random.default_rng(seed);im=Image.new('L',(w0,h0+4));dr=ImageDraw.Draw(im);cx=w0//2;pt=[(0,h0-1),(cx-3,3),(cx,0),(cx+3,2),(w0-1,h0-2),(cx+3,h0+1),(cx,h0+3),(cx-4,h0+1)];dr.polygon(pt,fill=255)
    v=np.asarray(im)>0;yy,xx=np.mgrid[:im.height,:im.width]; f=(xx+yy*.34<cx+.8);o=np.zeros((*v.shape,4),dtype=np.uint8)
    if theme=='snow': low=np.array([109,137,143]);light=np.array([188,207,203]);mid=np.array([147,175,174]);hi=np.array([225,228,213]);e=np.array([111,128,125]);texture=(cyc(GOLD,xx,yy)[:,:,0]-224)*.43
    elif theme in ('clay','ember'):low=np.array([135,77,35]);light=np.array([224,160,70]);mid=np.array([183,118,54]);hi=np.array([235,183,92]);e=np.array([125,80,42]);texture=(cyc(DARK,xx,yy)[:,:,0]-175)*.60
    else: low=np.array([142,96,40]);light=np.array([219,168,67]);mid=np.array([185,133,52]);hi=np.array([237,190,88]);e=np.array([143,96,43]);texture=(cyc(DARK,xx,yy)[:,:,0]-175)*.68
    d=np.clip(yy/(h0+3),0,1)[...,None];rgb=np.where(f[...,None],mid*(1-d)+light*d,low*(1-d)+mid*d);rgb+=texture[...,None]*[1,.81,.49]
    ds=nd.distance_transform_edt(v);rim=(ds<1.41)&v
    upper=rim&(yy<h0)&(yy<.72*h0+1)
    rgb[upper]=rgb[upper]*.17+e*.83
    if theme not in ('snow','clay','ember'):
        art=small_np(DIAMOND,(w0,h0+4),NN);rgb=rgb*.38+art*.62
    else:rgb[(f)&(yy<=2)&(ds>1.4)]=hi
    o[...,:3]=np.clip(np.rint((rgb-3)/8)*8+7,0,255).astype('uint8');o[...,3]=v*255
    # Broken lower pixel edge disperses into the ground as in printed DS hills.
    end=(yy>=h0)&v;keep=(yy+xx*2+rv.integers(0,3,yy.shape))%5>1;o[end&~keep,3]=0
    return o

for i,r in enumerate(des['regions'],1):
    if r['type'] not in ('continent',):continue
    for j,rr in enumerate(r['ridges']):
        # Dense staggered mountain clusters, some chains left entirely in the generated art.
        if i==3 and j==4:continue
        th=rr['style'];density=14 if th=='snow' else 16 if th in ('clay','ember') else 18
        points=list(pseq(rr['p'],density));
        for k,(x,y) in enumerate(points):
            x,y=round(x+rng.uniform(-2,2)),round(y+rng.uniform(-1,2))
            if not (5<x<w-5 and 6<y<h-3) or idx[y,x]!=i or wet[y,x] or sitekeep[y,x]:continue
            if (k+j)%4==3:continue
            ww=int(rng.integers(10,16))+(2 if th=='snow' else 1);hh=int(ww*.57)
            for dx,dy,sc in [(2,-4,.86),(0,0,1)]:
                ww0=max(6,round(ww*sc));hh0=max(4,round(hh*sc));sprite=ridge_art(ww0,hh0,th,k*17+j*53+i*613+dx)
                yy=y+dy-hh0+2;xx=x+dx-ww0//2;u=xx+ww0;v=yy+hh0+4
                if xx<1 or yy<1 or u>w-1 or v>h-1:continue
                cut=(idx[yy:v,xx:u]==i)&~wet[yy:v,xx:u]&~sitekeep[yy:v,xx:u];al=sprite[...,3]>0
                if np.count_nonzero(cut&al)/np.count_nonzero(al)<.79:continue
                sub=base[yy:v,xx:u,:];ss=cut&al;sub[ss]=sprite[...,:3][ss]*.88+sub[ss]*.12

# Flat pixel shapes for the DS print finish. No forests or large features from the game's map
# are stamped wholesale: crown positions come from the agreed geography and the new generation.
CROWNS={
 'forest':[(65,89,54),(82,113,61),(109,139,67),(150,163,86),(106,84,45)],
 'pine':[(54,80,65),(78,110,84),(104,136,101),(139,164,111),(104,81,47)],
 'tropic':[(64,83,46),(90,121,55),(123,152,62),(161,171,78),(104,82,43)],
 'umber':[(101,82,34),(144,103,35),(179,134,42),(213,156,55),(123,87,39)],
 'petal':[(107,81,45),(156,97,56),(188,127,65),(215,153,72),(123,86,47)],
 'marsh':[(66,84,49),(89,113,57),(115,141,62),(150,156,77),(103,83,43)],
 'meadow':[(105,91,40),(145,130,43),(170,151,49),(195,168,55),(116,87,37)],
}
# Tight ranks and stepped pixel silhouettes are the principal thing missing from a paint-like generation.
TREE_SHAPES=(('..11.','.1231','12321','12221','.121.','..5..'),
             ('..1..','.131.','.232.','12321','12221','.151.'),
             ('..11.','.1331','12321','12221','.121.','..5..'))

def draw_crown(x,y,kind,cur,fruit=False):
    sh=TREE_SHAPES[cur%len(TREE_SHAPES)]; pal=CROWNS[kind]; im=np.zeros((len(sh),5,3),np.float32);a=np.zeros(im.shape[:2],bool)
    for j,row in enumerate(sh):
        for k,c in enumerate(row):
            if c!='.': im[j,k]=pal[int(c)-1];a[j,k]=True
    if fruit:im[2,2]=(213,117,47) if cur%2 else (227,109,45)
    px=x-2;py=y-5
    if px<0 or py<0 or px+5>w or y+1>h:return
    sl=(slice(py,py+len(sh)),slice(px,px+5));hit=(idx[sl]==int(idx[y,x]))&~wet[sl]&~sitekeep[sl]&a
    if (hit.sum()<a.sum()*.90):return
    item=base[sl];item[hit]=im[hit]*.96+item[hit]*.04

for k,r in enumerate(des['regions'],1):
    for i,(x,y,width,theme) in enumerate(r.get('groves',())):
        if theme not in CROWNS or ((i+k)%5==0) or (theme=='meadow' and i%2):continue
        x,y=x*.5,y*.5; rad=max(3.8,width*.25);pts=[]
        for yd in np.arange(-rad*.64,rad*.68,3.3):
            for xd in np.arange(-rad,rad+.25,3.3):
                if (xd/rad)**2+(yd/(rad*.78))**2>1+rng.uniform(-.16,.1):continue
                xx,yy=round(x+xd+rng.uniform(-.9,.9)),round(y+yd+rng.uniform(-.7,.8));
                if 2<xx<w-3 and 5<yy<h-1 and idx[yy,xx]==k and not wet[yy,xx]:pts.append((xx,yy))
        for j,(xx,yy) in enumerate(sorted(pts,key=lambda p:p[1])):draw_crown(xx,yy,theme,j+i,theme in ('umber','petal') and (i+j)%4==0)

# Small honey-colour masonry lumps on chalk and salt, like the tiny groups visible in the reference.
def blocks(x,y,k,kind):
    t=Image.new('RGBA',(14,11));d=ImageDraw.Draw(t)
    pal={'salt':('#9e8550','#d8c385','#efda9f','#b19a5c'),'scarp':('#907037','#c5a054','#e0be73','#aa874b'),'floe':('#718b8c','#a6c3be','#c9dfd2','#8eacaa')}
    e,m,hi,sh=pal[kind]
    for a,b,ww in [(4,0,5),(8,4,5),(0,5,6)]:
        d.polygon([(a,b+1),(a+2,b),(a+ww-1,b),(a+ww,b+1),(a+ww,b+4),(a+1,b+4),(a,b+3)],fill=m,outline=e)
        d.line((a+1,b+1,a+ww-1,b+1),fill=hi);d.point((a+ww-2,b+3),fill=sh)
    q=np.array(t);x-=6;y-=9
    if x<0 or y<0 or x+14>=w or y+11>=h:return
    sl=(slice(y,y+11),slice(x,x+14));cut=idx[sl]==k;mask=q[...,3]>0;both=cut&mask&~sitekeep[sl]&~wet[sl]
    if (both.sum()<mask.sum()*.80):return
    item=base[sl];item[both]=q[...,:3][both]*.95+item[both]*.05

for k,r in enumerate(des['regions'],1):
    for i,(kind,x,y,width,_th) in enumerate(r.get('reliefs',())):
        if kind in ('scarp','salt','floe') and (i+k)%3!=2:
            blocks(round(x/2),round(y/2),k,kind)

# Keep the existing water paths, not the substitute rivers proposed in any generated crop.
water=wcol[...,:3].astype('f');Lw=water[:,:,1];deep=np.clip((Lw-89)/104,0,1)
sw0=np.array([47,101,118]);sw1=np.array([107,185,196]);wc=sw0+deep[...,None]*(sw1-sw0)
shine=(wcol[:,:,0]>156)&(wcol[:,:,1]>171);wc[shine]=np.where(((X+Y)%6==0)[shine,None],np.array([221,232,207]),np.array([158,202,191]));
wy=wet&(wcol[:,:,1]>120)&(wcol[:,:,0]<110)&((X+2*Y)%11<3);wc[wy]+=np.array([4,12,9]);base[wet]=wc[wet]
# Return the generated village-tree to the validated village anchor (instead of accepting
# the slight position change in the generation). Its natural shadow is inside its cut-out.
a=Image.open(S/'Reverie-village-genere-decoupe.png').convert('RGBA').resize((28,24),NN)
p=next(p for p in lay['sites'] if p['id']=='reverie');x,y=[round(v/2) for v in p['position']];xx=x-14;yy=y-22
v=np.asarray(a);sl=(slice(yy,yy+24),slice(xx,xx+28));ss=(v[:,:,3]>0)&(idx[sl]==5)
base[sl][ss]=v[:,:,:3][ss]*.91+base[sl][ss]*.09
# Native 5-bit paint values. No soft alpha or interpolation is left in the sprite layer.
base=np.clip(np.rint((base-3)/8)*8+7,0,255).astype('uint8')
full=np.asarray(Image.fromarray(base).resize((W,H),NN)).copy()
# Ensure even the subpixel outline from the validated map remains exact, at the 1112px work size.
isea=(INDEX==0); idx2=np.asarray(Image.fromarray(idx).resize((W,H),NN));missing=(~isea)&(idx2!=INDEX)
for i in np.unique(INDEX[missing]):
    ok=(idx2==i)&(INDEX==i);want=missing&(INDEX==i)
    if not ok.any():full[want]=[207,167,71];continue
    near=nd.distance_transform_edt(~ok,return_indices=True,return_distances=False);full[want]=full[near[0][want],near[1][want]]
# Exact wet-pixel coverage too, including the narrow springs and mouths.
w2=np.asarray(Image.fromarray(wet.astype('uint8')*255).resize((W,H),NN))>0
bad=w2&~wetfull&~isea
if bad.any():
    seed=(~isea)&~w2&~wetfull;nn=nd.distance_transform_edt(~seed,return_indices=True,return_distances=False);full[bad]=full[nn[0][bad],nn[1][bad]]
k=wetfull&~w2
if k.any():
    a=np.asarray(water0).astype('int16');c=np.clip((a[:,:,1]-89)/104,0,1);pat=sw0+c[...,None]*(sw1-sw0);full[k]=np.clip(np.rint((pat[k]-3)/8)*8+7,0,255).astype('uint8')
distance=nd.distance_transform_edt(~isea);yy,xx=np.mgrid[:H,:W]
ed=(distance<1.48)&~isea&~wetfull
full[ed]=np.clip(full[ed].astype('f')*.24+np.array([151,101,46])*.76,0,255).astype('uint8')
engrave=(distance>=1.5)&(distance<2.5)&~wetfull&((xx+yy*2)%9<3)
full[engrave]=np.clip(full[engrave].astype('f')*.66+np.array([182,126,60])*.34,0,255).astype('uint8')
rgba=np.dstack((full,~isea*255)).astype('uint8');rgba[isea]=0
mag=full.copy();mag[isea]=KEY
sprite=Image.fromarray(rgba);plate=Image.fromarray(mag);assert np.array_equal(np.all(np.array(plate)==KEY,axis=2),isea)
sav(plate,BASE/f'Terres-EoS-Magenta-{W}x{H}.png');sav(sprite,BASE/f'Terres-EoS-Transparent-{W}x{H}.png')
sav(plate.resize((W*5,H*5),NN),BASE/f'Planche-Terres-EoS-Magenta-{W*5}x{H*5}.png')
placements=[]
for p in lay['regions']:
    s=INDEX==p['index'];b=bounds(s);x,y,u,v=b;a=image=np.array(sprite.crop(b));o=~s[y:v,x:u];a[o]=0
    c=a[...,:3].copy();c[o]=KEY
    label=DEMO[p['id']]; sav(Image.fromarray(a),O/f'{label}-Transparent.png');sav(Image.fromarray(c),O/f'{label}-Magenta.png')
    placements.append({'nom':p['nom'],'masque':p['index'],'ancre_coin_haut_gauche':[x,y],'boite':list(b),'png_alpha':f'Terres-separees/{label}-Transparent.png','png_magenta':f'Terres-separees/{label}-Magenta.png'})
islets=INDEX>=101;u=np.array(sprite);u[~islets]=0;save=Image.fromarray(u);sav(save,O/'Ilots-satellites-Transparent.png');v=u[...,:3].copy();v[~islets]=KEY;sav(Image.fromarray(v),O/'Ilots-satellites-Magenta.png');placements.append({'nom':'18 îlots satellites','ancre_coin_haut_gauche':[0,0],'boite':[0,0,W,H],'png_alpha':'Terres-separees/Ilots-satellites-Transparent.png','png_magenta':'Terres-separees/Ilots-satellites-Magenta.png'})
routes={'size':[W,H],'fond_magenta':list(KEY),'ordre':placements,'sites_valides':lay['sites'],'empreinte_geographie':lay['empreinte_geographie']}
(BASE/'Replacer-les-terres.json').write_text(json.dumps(routes,ensure_ascii=False,indent=2)+'\n')
assert np.array_equal(np.asarray(sprite.getchannel('A'))>0,INDEX>0)
cc=Image.new('RGBA',(W,H))
for p in placements:cc.alpha_composite(Image.open(BASE/p['png_alpha']).convert('RGBA'),tuple(p['ancre_coin_haut_gauche']))
assert np.array_equal(np.array(cc),np.array(sprite))
rep={'statut':'PASS','generation_raster':6,'enregistrement_des_entrees':align,'geographie_et_cles':{'alpha_identique_au_masque_valide':True,'fond_magenta_sans_variation':True,'pixel_magenta_a_l_interieur':False,'calques_recomposables_a_l_identique':True,'regions':len(lay['regions']),'ilots':len(des['ilots']),'sites_conserves_dans_index':len(lay['sites']),'empreinte_geographie':lay['empreinte_geographie']},'trames_eos':5,'taille_sprite':[W,H],'export_magenta':[W*5,H*5]}
(BASE/'Verification.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n')
print('PASS : Géographie verrouillée (26 masses), 6 illustrations générées, 5 échantillons de grain natif, magenta pur et recomposition pixel-identique.')
