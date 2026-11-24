#!/usr/bin/env python3
"""Seat the existing L03 twigs on the actual carved lower rims of the preview."""
from pathlib import Path
import importlib.util
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import PchipInterpolator

P=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

V=load('poteaux',P/'Ajuster-verdure.py');F,T=V.fx,V.old
L=load('lumiere_rives',P/'Lumiere-PMD.py')
# L'Accueil montre déjà les tiges sur la face du bois, non sur le parquet.
# Au Réfectoire, la rive E. est déjà continue sur la lèvre et ses rainures.
ALREADY_SEATED={(1,0),(1,1),(6,1)}
# Centre de la tige dans le module original (96 × 25), hors rameaux et feuilles.
STEM=PchipInterpolator([0,10,22,34,47,56,68,78,87,95],[9,10,14.5,16,11.5,11.5,15.6,13.8,10.4,7.7])


def trace_rail(route,img):
    """Follow the fall from the gold lip to the carved, more violet facing."""
    _,_,_,_,pts=route
    p=np.asarray(pts);xs=np.arange(p[0,0],p[-1,0]+1)
    old=PchipInterpolator(*p.T)(xs)
    rr,gg,bb=img[:,:,:3].astype(float).transpose(2,0,1)
    ochre=np.clip((gg-bb+10)*.013,0,1);dark=np.clip(.92-rr/160,0,1)
    # Horizontal cracks in the parquet are too short in y to match both bands.
    roll=lambda n: np.roll(ochre,n,axis=0)
    edge=(np.mean([roll(i) for i in range(2,8)],axis=0)
          -np.mean([roll(-i) for i in range(3,14)],axis=0)+.13*dark)
    dy=np.arange(-17,28);ys=np.rint(old).astype(int)[None,:]+dy[:,None]
    ev=edge[ys,xs[None,:]]-.00044*(dy[:,None]-10)**2
    delta=np.abs(dy[:,None]-dy[None,:]);step=-.080*delta-.14*np.maximum(delta-2,0)**1.25
    back=np.zeros_like(ev,dtype=int);score=ev[:,0]
    for j in range(1,len(xs)):
        t=step+score[None,:];which=t.argmax(1);back[:,j]=which;score=t[np.arange(len(dy)),which]+ev[:,j]
    which=int(score.argmax());contour=np.empty(len(xs),float)
    for j in reversed(range(len(xs))):
        contour[j]=ys[which,j];which=back[which,j]
    contour=gaussian_filter1d(contour,2.3)
    return xs,old,contour


def fit_tex(tex,route,n,slot,img,x,y):
    _,name,width,mirror,_=route
    xs,old,edge=trace_rail(route,img)
    # Move the stem onto the lip, not onto the dark lower face. Sample at 1×
    # and leave a little of the sprite's natural undulation around the guide.
    grade=np.clip(abs(np.gradient(edge)),0,1.60)
    lip=edge-(1.8+1.75*grade)
    if (n,slot)==(12,1):
        lip-=np.interp(xs,[xs[0],xs[0]+10,xs[-1]-12,xs[-1]],[3.,1.0,1.0,5.])
    if (n,slot) in ((8,0),(13,0),(14,0)):
        lip-=np.interp(xs,[xs[0],xs[-1]-16,xs[-1]],[0.6,0.6,2.4])
    u=np.clip((x-xs[0])*(tex.shape[1]-1)/(xs[-1]-xs[0]),0,tex.shape[1]-1)
    if mirror:u=tex.shape[1]-1-u
    # Width is projected onto the vertical pixel grid, not interpolated over RGB.
    t=(tex.shape[0]-1)/(width-1)
    anchor=STEM(u);axis=np.interp(x,xs,lip)
    v=np.rint((y-axis)*t+(anchor*.70+(tex.shape[0]-1)*.15)).astype(int)
    uu=np.rint(u).astype(int);valid=(x>=xs[0])&(x<=xs[-1])&(v>=0)&(v<tex.shape[0]);a=np.zeros_like(img)
    a[valid]=tex[v[valid],uu[valid]]
    return a,(xs,old,edge,lip)


def foliage_part(tex,route,allowed,x,y):
    kind,_,w,_,p=route
    a,lab=T.warp(*tex,route,x,y);m=(a[...,3]>0)&allowed;a[~m]=0;lab[~m]=0
    if kind==F.V:
        p=np.asarray(p);axis=np.interp(y,p[:,1],p[:,0]);dist=np.clip(abs(x-axis)/(w*.65),0,1)
        gain=np.clip(.97-.40*dist**2+.037*np.sin(y/10.),.60,1.)
        a[m,:3]=np.rint(a[m,:3]*gain[m,None]*[.97,1.,.91]).astype(np.uint8)
    else:
        tone=[.89,.93,.85] if kind==F.R else [1.,.96,.91]
        a[m,:3]=np.rint(a[m,:3]*tone).astype(np.uint8)
    return a


def reposer(r,d,art,reverie,bramble):
    n=r['n'];q=d['lianes'][r['id']]
    b,f,x,y,_,glass,_,_,allowed,_=F.freeze_support(r,d)
    guard=L.extract_alpha(d,r);deny=guard|~allowed
    if n==1:
        sx,sy,sw,sh=224,313,64,39;deny[sy:sy+sh,sx:sx+sw]=True
    img=np.array(Image.alpha_composite(Image.fromarray(b),Image.fromarray(f)))
    ret,base,notes,axes=[],[],[],[];post=0;slot=0
    for route,noble in F.grow_routes(r)[0]:
        k,name,width,flip,pts=route;tex=reverie[noble] if k==F.V else art[k]
        pic=foliage_part(tex,route,allowed,x,y)
        new=pic
        if k==F.V:
            post+=1
            if (n,post) in V.FIX:
                loc=allowed&~F.nd.binary_dilation(glass,iterations=2)
                pic,_,_=V.winding(tex,x,y,V.FIX[n,post],flip,loc)
                if (n,post) in V.RONCES:
                    foot=V.foot(bramble,x,y,V.FIX[n,post],V.RONCES[n,post],loc&~guard)
                    pic=np.array(Image.alpha_composite(Image.fromarray(foot),Image.fromarray(pic)))
                new=pic
        if k==F.R:
            keep=(n,slot) in ALREADY_SEATED
            scan=None
            if not keep:
                new,scan=fit_tex(tex[0],route,n,slot,img,x,y)
                m=(new[...,3]>0)&~deny;new[~m]=0
                new[m,:3]=np.rint(new[m,:3]*[.89,.93,.85]).astype(np.uint8)
                assert .79<m.sum()/(pic[...,3]>0).sum()<1.24,(r['label'],name)
                assert not new[...,3][deny].any()
                xx,old,edge,lip=scan;shift=lip-old;before,after=[stem_distance(p,xx,lip) for p in (pic,new)]
                assert after[0]<1.6 and after[0]<before[0] and after[1]<7.,(n,slot,before,after)
                notes.append(dict(nom=name,pose='recalée sur la lèvre',x_depart=int(xx[0]),x_arrivee=int(xx[-1]),
                                  decalage_y_px=[round(float(shift.min()),1),round(float(shift.max()),1)],
                                  axe_echantillons=[[int(xx[j]),round(float(lip[j]),1)] for j in sorted(set(range(0,len(xx),8))|{len(xx)-1})],
                                  distance_tige_axe_px=dict(mediane_avant=before[0],mediane_apres=after[0],p90_avant=before[1],p90_apres=after[1]),
                                  feuillage_pixels=int(m.sum())))
            else:notes.append(dict(nom=name,pose='en contact, conservée'))
            axes.append((route,pic,new,scan));slot+=1
        base.append(pic);ret.append(new)
    seen=F.grow_routes(r)[1];assert post==seen==q['v'] and slot==2
    s0,t0,flora0=V.combine(base,allowed,f[...,3]>0)
    original=[L.decode(q[k]) for k in ('s','t')]
    assert np.array_equal(s0,original[0]) and np.array_equal(t0,original[1]),('rendu source non reproduit',n)
    # Same contact shadows, front occlusion and unchanged top- and post-parts.
    s,t,flora=V.combine(ret,~deny,f[...,3]>0)
    diff=np.any((s!=s0)|(t!=t0),axis=2);sprite_diff=np.any(flora!=flora0,axis=2)
    contact_zone=np.zeros_like(deny)
    for route,pic,new,scan in axes:
        if scan is None:continue
        mask=(pic[...,3]>0)|(new[...,3]>0);cast=np.zeros_like(mask);cast[2:,1:]=mask[:-2,:-1]
        contact_zone|=mask|F.nd.maximum_filter(cast,size=9)
    assert not diff[deny].any() and not diff[~contact_zone].any()
    assert (diff.sum()>0)==any(a[3] is not None for a in axes)
    for i in range(4):
        for pt in q['points']:
            cx,cy,core=pt['images'][i][1];m=L.decode(core)[...,3]>0;ph,pw=m.shape
            assert not sprite_diff[cy:cy+ph,cx:cx+pw][m].any() and (flora[cy:cy+ph,cx:cx+pw,3][m]>0).all()
    crop=maskbox(diff)
    return (s,t),diff,axes,dict(salle=r['id'],nom=r['label'],no=n,bordures=notes,pixels_modifies=int(diff.sum()),emprise=crop)


def maskbox(m):
    yy,xx=np.where(m)
    if len(xx):return [int(xx.min()),int(yy.min()),int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1)]
    return None


def stem_distance(pic,xs,axis):
    # Brown, matte twigs, excluding bright buds and leaves.
    r,g,b,a=pic.astype(int).transpose(2,0,1)
    branch=(a>0)&(r>=g+10)&(g>b+9)&(r<137)
    cy,cx=np.where(branch);z=np.abs(cy-np.interp(cx,xs,axis))
    assert len(z)>28
    return np.round(np.percentile(z,[50,90]),2).tolist()
