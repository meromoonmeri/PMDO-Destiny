#!/usr/bin/env python3
"""Small orthographic voxel renderer. x = east, v = south, z = up. Camera Y = .68 v - z.
Render at 1x, via exact voxel traversal / z buffer, not a rotation of the upright bitmap.
"""
from dataclasses import dataclass
from pathlib import Path
import math
import os
import numpy as np
from scipy import ndimage as ndi
# The jit cache is only scratch, never part of the source kit.
os.environ.setdefault('NUMBA_CACHE_DIR',str(Path.home()/'.cache/pmu-orientations/jit'))
from numba import njit

K=.68
DIRS=('Down','DownRight','Right','UpRight','Up','UpLeft','Left','DownLeft')
TRIG=tuple((round(math.cos(i*math.pi/4),12),round(math.sin(i*math.pi/4),12)) for i in range(8))
MATERIALS=('bois','pierre','tissu','metal','feuille','peau','cuivre','osier','eau')

@njit(cache=True,nogil=True)
def march(G,cs,sn,w,h,x0,y0):
    """Return exact first hit for each pixel: x,v,z coords, v_cam depth and cell label."""
    dz,dv,du=G.shape
    ox=du*.5;ov=dv*.5
    out=np.zeros((h,w,5),np.float32)
    out[:,:,3]=-1e6
    for y in range(h):
        Y=y+.5+y0
        for x in range(w):
            X=x+.5+x0
            b0=X*cs+ox;b1=X*sn+ov
            m0=-sn;m1=cs
            lo=Y/K;hi=(dz+Y)/K
            if abs(m0)>1e-10:
                aa=-b0/m0;bb=(du-b0)/m0
                lo=max(lo,min(aa,bb));hi=min(hi,max(aa,bb))
            elif not 0<=b0<du:continue
            if abs(m1)>1e-10:
                aa=-b1/m1;bb=(dv-b1)/m1
                lo=max(lo,min(aa,bb));hi=min(hi,max(aa,bb))
            elif not 0<=b1<dv:continue
            if hi<=lo:continue
            q=hi-1e-6
            xcell=min(du-1,max(0,int(math.floor(b0+m0*q))))
            vcell=min(dv-1,max(0,int(math.floor(b1+m1*q))))
            zcell=min(dz-1,max(0,int(math.floor(K*q-Y))))
            ux=(xcell+(1 if m0<0 else 0)-b0)/m0 if abs(m0)>1e-10 else -1e10
            uv=(vcell+(1 if m1<0 else 0)-b1)/m1 if abs(m1)>1e-10 else -1e10
            uz=(zcell+Y)/K
            stepx=-1 if m0>0 else 1
            stepv=-1 if m1>0 else 1
            disx=abs(1./m0) if abs(m0)>1e-10 else 0.
            disv=abs(1./m1) if abs(m1)>1e-10 else 0.
            while 0<=xcell<du and 0<=vcell<dv and 0<=zcell<dz and q>lo-1e-8:
                material=G[zcell,vcell,xcell]
                if material:
                    # Sample just INSIDE the voxel even at an exact coplanar edge.
                    q-=.00004
                    out[y,x,0]=min(du-.0001,max(.0001,b0+m0*q))
                    out[y,x,1]=min(dv-.0001,max(.0001,b1+m1*q))
                    out[y,x,2]=min(dz-.0001,max(.0001,K*q-Y))
                    out[y,x,3]=q
                    out[y,x,4]=material
                    break
                if ux>=uv and ux>=uz:
                    q=ux;ux-=disx;xcell+=stepx
                elif uv>=uz:
                    q=uv;uv-=disv;vcell+=stepv
                else:
                    q=uz;uz-=1./K;zcell-=1
    return out

@dataclass
class Model:
    ref: np.ndarray
    geom: np.ndarray
    pivot: tuple
    recipe: str
    pigment: str
    fit: float=0.

    def __post_init__(self):
        h,w=self.ref.shape[:2]
        self.down=march(self.geom,1.,0.,w,h,-w/2.,-self.pivot[1])
        m=self.ref[:,:,3]>127
        self.fit=round(float(np.count_nonzero((self.down[:,:,4]>0)&m)/max(1,m.sum())),4)
        self.edge=np.pad(self.geom!=0,2,mode='constant')
        self.tints=sample_tints(self.ref,self.pigment,self.recipe)
        good=np.where(m)
        self.nearest=ndi.distance_transform_edt(~m,return_distances=False,return_indices=True) if len(good[0]) else None
        yy,vv,uu=np.nonzero(self.geom)
        assert yy.size,(self.ref.shape,self.recipe)
        self.box=(uu.min()-w/2,uu.max()+1-w/2,vv.min()-self.geom.shape[1]/2,vv.max()+1-self.geom.shape[1]/2,yy.min(),yy.max()+1)
        # Ground projection of the real volume, at 1x; z 0 through 4 support toes and plinths.
        base=np.any(self.geom[:min(5,self.geom.shape[0])]!=0,axis=0)
        if not base.any():base=np.any(self.geom,axis=0)
        vy,ux=np.where(base)
        self.foot=(ux+.5-w/2.,vy+.5-self.geom.shape[1]/2.)


def sample_tints(a,primary,recipe):
    h,w=a.shape[:2]; y,x=np.indices((h,w));rgb=a[:,:,:3].astype(float);r,g,b=rgb.transpose(2,0,1)
    l=rgb @ np.array([.24,.64,.12]);solid=a[:,:,3]>127
    p=solid&(l>25)&(l<231)
    edge=(x<w*.16)|(x>w*.84)|(y<max(4,h*.15))|(y>h*.87)
    palette={
        'bois':p&(r>=g+3)&(g>=b+1)&(r>b+12),
        'pierre':p&(np.maximum(r,np.maximum(g,b))-np.minimum(r,np.minimum(g,b))<44),
        'tissu':p&(np.abs(r-g)+np.abs(g-b)>11),
        'metal':p&((np.abs(r-g)+np.abs(g-b)<38)|(b>r+6)),
        'feuille':p&(g>=r+5)&(g>=b+7),
        'peau':p,
        'cuivre':p&(r>g+8)&(g>b+6)&(l>66),
        'osier':p&(r>g+8)&(g>b+10),
        'eau':p&((b>=r+10)&(g>r+5)),
    }
    fallback={'bois':[118,77,51],'pierre':[108,103,108],'tissu':[133,83,77],'metal':[116,124,132],'feuille':[71,103,52],'peau':[128,103,86],'cuivre':[149,99,53],'osier':[160,128,69],'eau':[57,130,149]}
    out=[]
    for mat in MATERIALS:
        take=palette[mat]
        if mat=='bois' and recipe in {'biblio','buffet','commode','armoire','horloge','grainotheque','caisse'} and (p&edge).sum()>16:
            candidate=p&edge
            # The painted frames can be green. Derive the body colours from hue of the frame itself.
            med=np.median(rgb[candidate],axis=0)
            if med[1]>med[0]+3:take=candidate&(g>r)
            elif (take&edge).sum()>14:take=take&edge
        if take.sum()>12:
            v=rgb[take]
            lum=v@[.24,.64,.12];lo,hi=np.percentile(lum,[29,80]);a1=v[(lum>=lo)&(lum<=hi)]
            tone=np.median(a1,axis=0) if len(a1) else np.median(v,axis=0)
        elif mat==primary and p.sum()>6:tone=np.median(rgb[p],axis=0)
        else:tone=np.array(fallback[mat])
        # Keep modest chroma in the reconstructed, unlit surfaces.
        out.append(np.clip(tone,18,220))
    return np.array(out)


def cut(a,depth,x0,y0):
    yy,xx=np.where(a[:,:,3]>0)
    if not xx.size:return (a[:1,:1],depth[:1,:1],x0,y0)
    l,t,r,b=xx.min(),yy.min(),xx.max()+1,yy.max()+1
    return (a[t:b,l:r].copy(),depth[t:b,l:r].copy(),x0+int(l),y0+int(t))


def view(m,i):
    cs,sn=TRIG[i];U0,U1,V0,V1,Z0,Z1=m.box
    fx=[u*cs+v*sn for u in (U0,U1) for v in (V0,V1)];fy=[K*(-u*sn+v*cs)-z for u in (U0,U1) for v in (V0,V1) for z in (Z0,Z1)]
    l,t=math.floor(min(fx))-1,math.floor(min(fy))-1;r,b=math.ceil(max(fx))+1,math.ceil(max(fy))+1
    pix=march(m.geom,cs,sn,r-l,b-t,l,t);hit=pix[:,:,4]>0
    ph,pw=hit.shape;a=np.zeros((ph,pw,4),np.uint8)
    if not hit.any():return a,pix[:,:,3],l,t
    x,v,z,depth,mt=pix[hit].T;mi=mt.astype('intp')-1
    zi=np.minimum(z.astype('intp'),m.geom.shape[0]-1)+2;vi=np.minimum(v.astype('intp'),m.geom.shape[1]-1)+2;xi=np.minimum(x.astype('intp'),m.geom.shape[2]-1)+2
    E=m.edge
    def differ(axis):
        g=np.zeros(len(x),np.float32)
        for d,f in ((1,.72),(2,.28)):
            dz,dv,dx=[d if j==axis else 0 for j in range(3)]
            g+=f*(E[zi-dz,vi-dv,xi-dx].astype(float)-E[zi+dz,vi+dv,xi+dx])
        return g
    nd=np.stack([differ(2),differ(1),differ(0)],axis=1)
    nd/=np.maximum(.08,np.linalg.norm(nd,axis=1)[:,None]);nx,ny,nz=nd.T
    H,W=m.ref.shape[:2];V=m.geom.shape[1];X=x-W/2;Y=v-V/2
    uu=np.clip(np.floor(x).astype('intp'),0,W-1);pr=Y*K-z+m.pivot[1];rr=np.clip(np.floor(pr).astype('intp'),0,H-1)
    s=m.ref[rr,uu,:3].astype(float);registered=m.ref[rr,uu,3]>127;registered&=(pr>=0)&(pr<H)
    dDown=m.down[rr,uu,3]
    # Reproject only the facets that the source's camera could have seen.
    # Tolerate the 1px quantisation of the canonical lookup, not the depth of a panel.
    visible=registered&(dDown>-1e5)&(Y>=dDown-(1.05+np.maximum(nz,0)*.56))&((ny>.10)|(nz>.10)|(np.abs(nx)*.80+ny>.59)&(Y>=V*.08))
    if i in (3,4,5):visible&=(nz>.2)|(ny>.30)
    if i==4 and m.recipe not in ('toile','drapeau'):visible&=(nz>.19)
    if i in (3,4,5) and m.recipe in ('kiosque','mannequin','statue'):
        visible&=(rr>H*.63)|(nz>.60)&(rr<H*.045)
    if m.recipe=='chariot':
        # The pot and cups stay on their own solids, not printed again on the tray beneath them.
        propBand=(rr<H*.42)&(((s[:,0]>148)&(s[:,1]>127)&(s[:,2]>91))|((s[:,0]>s[:,1]*1.54)&(s[:,1]<95)&(s[:,0]>74)))
        visible&=~((mi==0)&(nz>.35)&propBand)
    # No front detail printed on the reverse of a mirror, slate, signs or chest faces.
    if m.recipe in ('toile','drapeau') and i in (3,4,5):
        # Dyed stitching can be read in reverse through a woven hanging, not through wood.
        woven=registered&(ny<-.13)
    else:woven=np.zeros_like(registered)
    orient=np.round((.17*nz+.082*ny-.092*nx)*17)/17
    tone=m.tints[mi];lu=tone@[.24,.64,.12]
    axis=np.where(np.abs(nx)>=np.abs(ny),v,x);top=nz>.58
    line=np.floor(axis).astype(np.intp);tier=np.floor(z).astype(np.intp)
    seed=((line*31+tier*47+np.floor(v).astype(int)*13) % 29)
    raised = np.where((tier<=1)|(tier>=m.box[-1]-1.1),-.21,0.)
    # Simulate drawn planks, stone joints or textile seams with repeatable native pixels.
    rel=np.zeros(len(x),float);wood=(mi==0)|(mi==7);stone=(mi==1)|(mi==3);cloth=(mi==2);leaf=(mi==4);water=(mi==8)
    cadence=12 if m.recipe in {'biblio','buffet','armoire','grainotheque','horloge'} else 9
    uLine=np.where(top,np.floor(v).astype(int),line);zLine=np.where(top,np.floor(x).astype(int),tier)
    seams=(uLine%cadence==0);ribbon=(uLine%cadence==1)
    rel[wood]+=np.where(seams,-.115,np.where(ribbon,.105,0))[wood]
    grain=((uLine*2+zLine//4)%13==3)&(zLine%17>3);rel[wood]+=np.where(grain,-.048,0)[wood]
    # Visible frame and rails are not repeated over a whole slatted back.
    if m.recipe in {'armoire','biblio','buffet','foyer','commode','horloge','grainotheque','caisse','coffre','piano','bloc','kiosque','paroi'}:
        nearRim=(x<3)|(x>W-3)|(v<2.4)|(v>V-2.4)|(z<3)|(z>m.box[-1]-3.1)
        rel[wood]+=np.where(nearRim,.10,0)[wood];rel[wood]+=np.where((tier==4)|(tier==m.box[-1]-4),-.125,0)[wood]
    mortar=(tier%5==0)|((line+5*(tier//5%2))%12==0)
    rel[stone]+=np.where(mortar,-.097,0)[stone] if m.recipe in {'foyer','bloc','paroi','arche','rocher'} else 0
    rel[cloth]+=np.where((line%4==0)&(tier%5>0),.058,np.where(seed<6,-.055,0))[cloth]
    fleck=((np.floor(x).astype(int)//3*13+np.floor(v).astype(int)//3*19+tier//2*7)%23)
    rel[leaf]+=(np.where(fleck<5,.19,np.where(fleck>=16,-.14,0))+np.where(seed<4,.04,0))[leaf]
    rel[water]+=np.where((uLine+((zLine//5)%2)*3)%10==0,.18,0)[water]
    var=(np.where(seed<3,-.056,np.where(seed>25,.06,0)))
    # Keep an authored four-value light ramp instead of smooth plastic lighting.
    k=np.round((.87+orient+raised+rel+var)*33.)/33.
    hidden=tone*k[:,None]
    soft=m.recipe in {'plante','palmier','pot','statue','mannequin','sac','coussin','souche','orbe','rocher','rouleaux','moulin','luminaire','pile','relief','kiosque'}
    if soft:
        # Carry some colour bands and clusters around a shape without putting its eyes or labels on the back.
        aidx=(np.floor(np.abs(X)*.45+np.abs(Y)*.62)+W//4).astype(int)%W
        arow=np.clip(rr+(np.floor(v).astype(int)%5-2),0,H-1)
        sy,sx=m.nearest[:,arow,aidx];band=m.ref[sy,sx,:3].astype(float)
        use=np.where(leaf,.43,np.where(cloth,.25,.20))
        if m.recipe in ('coussin','orbe','souche','luminaire'):use=np.maximum(use,.44)
        hidden=hidden*(1-use[:,None])+band*(k*use)[:,None]
    # A bright cap becomes slightly darker round its side. Pixel palette remains source-derived.
    sk=np.clip(.956+orient-.035*np.abs(nx),.79,1.10)
    color=np.where(visible[:,None],s*sk[:,None],hidden)
    color=np.where(woven[:,None],(.73*s+.14*tone)*np.clip(.99+orient,.83,1.12)[:,None],color)
    a[hit,:3]=np.clip(np.rint(color),0,255).astype(np.uint8);a[hit,3]=255
    # Contours sit on the solid surface. They don't add a halo or a built-in shadow.
    border=hit&~ndi.binary_erosion(hit)
    outlines=a[border,:3].astype(float)
    a[border,:3]=np.clip(np.rint(outlines*.64+np.array([10,7,8])),0,255).astype(np.uint8)
    for off,axis0 in [(1,0),(1,1)]:
        dep=pix[:,:,3];delta=np.roll(dep,off,axis0)-dep
        seam=hit&(delta>4.5)&(delta<15.)&(~border)
        a[seam,:3]=np.rint(a[seam,:3].astype(float)*.85).astype(np.uint8)
    return cut(a,pix[:,:,3],l,t)


def flat(src,i):
    """Nearest inverse planar mapping. Cardinal rotations keep every pixel exactly."""
    h,w=src.shape[:2];c,s=TRIG[i]
    if not i%2:
        b=np.rot90(src,i//2).copy();hh,ww=b.shape[:2]
        # Choose pivots in the centre of their continuous footprints.
        return b,np.zeros((hh,ww),np.float32),-(ww//2),-(hh//2)
    l=math.floor(-abs(c)*w/2-abs(s)*h/2);r=-l;t=math.floor(-abs(s)*w/2-abs(c)*h/2);b=-t
    yy,xx=np.mgrid[t:b,l:r];xx=xx+.5;yy=yy+.5
    sx=np.floor(c*xx-s*yy+w/2).astype(int);sy=np.floor(s*xx+c*yy+h/2).astype(int)
    m=(sx>=0)&(sx<w)&(sy>=0)&(sy<h)
    a=np.zeros((*m.shape,4),np.uint8);a[m]=src[sy[m],sx[m]]
    return cut(a,np.zeros(m.shape,np.float32),l,t)


def composite(pieces,i):
    cs,sn=TRIG[i];all=[]
    for picture,dx,dv in pieces:
        a,d,x,y=picture;xx=dx*cs+dv*sn;vv=-dx*sn+dv*cs
        all.append((a,d+vv,x+round(xx),y+round(vv*K)))
    l=min(x for a,d,x,y in all);t=min(y for a,d,x,y in all)
    r=max(x+a.shape[1] for a,d,x,y in all);b=max(y+a.shape[0] for a,d,x,y in all)
    a=np.zeros((b-t,r-l,4),np.uint8);z=np.full((b-t,r-l),-1e6,np.float32)
    for p,d,x,y in all:
        dest=a[y-t:y-t+p.shape[0],x-l:x-l+p.shape[1]];dep=z[y-t:y-t+p.shape[0],x-l:x-l+p.shape[1]];k=(p[:,:,3]>0)&(d>=dep)
        dest[k]=p[k];dep[k]=d[k]
    return cut(a,z,l,t)
