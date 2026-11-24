#!/usr/bin/env python3
"""Project a fixed walnut stand + deforming textured cloth in the eight DM directions."""
from Commun import *
from PIL import ImageDraw
from math import cos,sin,pi
from scipy.ndimage import binary_dilation
D=ROOT/'Drapeaux'; PIVOT=np.array([52.,88.]); SIZE=(108,102); PBL=.58
N=6;DT=125


def weave():
    im=Image.open(REF/'Drapeau-etude-IA.png').convert('RGB');assert im.size==(1408,768)
    im=im.crop((577,156,831,603)).resize((35,49),Image.Resampling.NEAREST)
    a=np.array(im.quantize(colors=22,dither=Image.Dither.NONE).convert('RGB'));y,x=np.indices(a.shape[:2]);
    end=48-14*(1-np.abs((x-17)/17));m=(y<=end)&~((a[...,0]>175)&(a[...,2]>133)&(a[...,1]<70));
    a[~m]=0; return a,m


class Stage:
    def __init__(self,i):
        t=i*pi/4;self.cs=round(cos(t),12);self.sn=round(sin(t),12);self.d=np.full(SIZE[::-1],-1e7);self.a=np.zeros((*SIZE[::-1],4),dtype='uint8')
    def project(self,q):
        p=np.asarray(q,dtype=float);u,v,z=p.T;s=u*self.cs+v*self.sn;d=-u*self.sn+v*self.cs
        return np.stack([s+PIVOT[0],PBL*d-z+PIVOT[1],d+PBL*z],axis=1)
    def triangle(self,q,color,depthoff=0):
        p=self.project(q);x,y=p[:,:2].T;l=max(0,int(np.floor(x.min())));t=max(0,int(np.floor(y.min())));r=min(SIZE[0],int(np.ceil(x.max())));b=min(SIZE[1],int(np.ceil(y.max())));a0=p[1]-p[0];a1=p[2]-p[0]
        if min(r-l,b-t)<=0: return
        denom=a0[0]*a1[1]-a0[1]*a1[0]
        if abs(denom)<=1e-7:return
        ii,jj=np.ogrid[t:b,l:r];xx=jj+.5-x[0];yy=ii+.5-y[0]
        u=(xx*a1[1]-yy*a1[0])/denom;v=(a0[0]*yy-a0[1]*xx)/denom
        zz=p[0,2]+u*a0[2]+v*a1[2]+depthoff;a=self.a[t:b,l:r];d=self.d[t:b,l:r]
        mask=(u>=-1e-6)&(v>=-1e-6)&(u+v<=1.000001)&(zz>d)
        if mask.any():d[mask]=zz[mask];a[mask,:3]=color;a[mask,3]=255
    def quad(self,q,color):
        self.triangle([q[j] for j in (0,1,2)],color);self.triangle([q[j] for j in (0,2,3)],color)
    def ring(self,z,r):return [(cos(j*pi/4)*r,sin(j*pi/4)*r,z) for j in range(8)]
    def beam(self,a,b,c,pla=False):
        # broad warm walnut or brass planes: viewer's upper left is the key light.
        for k in range(len(a)):
            j=(k+1)%len(a);q=[a[k],a[j],b[j],b[k]];p=self.project(q)
            normal=(p[1]-p[0]);v=normal[2]/(np.linalg.norm(normal)+1e-9)
            shade=np.clip(.95+v*.22,.72,1.2);self.quad(q,np.clip(np.rint(np.array(c)*shade),0,255))
        for k in range(1,len(b)-1):self.triangle([b[0],b[k],b[k+1]],np.minimum(255,np.array(c)+[23,17,10]))
    def base(self):
        for z0,z1,r0,r1,c in [(0,2,7.1,7.7,(64,44,31)),(2,4,7.7,6.7,(123,78,48)),(4,7,6.7,3.3,(103,63,41)),(7,9,3.3,3.1,(157,105,51)),(9,72,2.05,2.05,(114,72,45)),(70,73,2.4,2.4,(149,99,48)),(73,77,2.6,1.9,(186,138,65)),(77,78,1.9,1.1,(220,176,93))]:
            self.beam(self.ring(z0,r0),self.ring(z1,r1),c)
        def along(u,r,z=69):return [(u,cos(j*pi/4)*r,sin(j*pi/4)*r+z) for j in range(8)]
        self.beam(along(-18.5,1.6),along(18.5,1.6),(126,82,50))
        for u in (-19.4,19.4):self.beam(along(u-1.45,2.35),along(u+1.45,2.35),(181,132,62))
        for u in [-13.5,13.5]:
            self.beam(along(u-.8,2.04),along(u+.8,2.04),(92,131,89))
            self.quad([(u-.9,1.54,70.2),(u+.9,1.54,70.2),(u+.9,5.0,66.0),(u-.9,5.0,66.0)],(115,142,93))
    def cloth(self,a,m,k):
        w,h=a.shape[1],a.shape[0];t=np.arange(h+1)[:,None]/h;v=np.arange(w+1)[None,:]/w;u=-15.9+31.8*v;wave=k*2*pi/N
        dep=4.0+2.15*np.sin(v*6.+.47+1.67*t)+t**1.3*(2.0*np.sin(.9+v*5.+wave)+1.9*np.cos(wave+.5)*v)
        dep=np.maximum(dep,2.7+1.0*np.exp(-((v-.5)/.19)**2))
        z=67.9-48*t+t*1.15*np.sin(v*4.5+wave);coords=np.stack(np.broadcast_arrays(u,dep,z),axis=-1)
        for yi,xi in zip(*np.nonzero(m)):
            q=[coords[yi,xi],coords[yi,xi+1],coords[yi+1,xi+1],coords[yi+1,xi]]
            norm=np.cross(q[1]-q[0],q[3]-q[0]);side=(-self.sn*norm[0]+self.cs*norm[1]+PBL*norm[2])/(np.linalg.norm(norm)+1e-9)
            color=a[yi,xi].astype(float)*((.88+.12*abs(side)) if side>=0 else (.73+.15*abs(side)))
            self.quad(q,np.clip(np.rint(color),0,255))
    def canvas(self):
        m=self.a[...,3]>0;self.a[binary_dilation(m)&~m]=[37,29,23,255];return Image.fromarray(self.a)


def make(i,tex,mat):
    photos=[]
    for k in range(N):
        s=Stage(i);s.base();s.cloth(tex,mat,k);photos.append(s.canvas())
    xy=tuple(fn(im.getbbox()[j] for im in photos) for j,fn in enumerate([min,min,max,max]));return [im.crop(xy) for im in photos],[int(PIVOT[0])-xy[0],int(PIVOT[1])-xy[1]]

def main():
    t,m=weave();rows=[];demo=[]
    for i,(direc,n,sign) in enumerate(DIRS):
        f,p=make(i,t,m);im=f[0];w,h=im.size;assert (16<=w<=53 and 70<=h<=100),(direc,im.size)
        f0=f'Drapeaux/PNG-1x/{direc}.png';png(im,ROOT/f0);name=f'Drapeaux/Animation/{direc}-6-poses.png';a=Image.new('RGBA',(w*3,h*2));
        for k,g in enumerate(f):a.alpha_composite(g,((k%3)*w,(k//3)*h))
        png(a,ROOT/name);demo.append(im)
        rows.append({'id':'etendard-'+direc.lower(),'direction':direc,'nom':n,'flèche':sign,'pivot':p,'w':w,'h':h,'png':f0,'atlas':name,'poses':N,'colonnes':3,'duree_ms':DT,'sha256':filehash(ROOT/f0)})
        assert len({g.tobytes() for g in f})==N
    assert len({v['sha256'] for v in rows})==8
    data={'nom':'Étendard au gland','variantes':rows,'source':{'fichier':'Reference/Drapeau-etude-IA.png','sha256':filehash(REF/'Drapeau-etude-IA.png')},'projection':'maillage tissu recto/verso avec hampe, barre et pied en volumes'}
    write_json(D/'Index-Drapeaux.json',data)
    out=Image.new('RGB',(808,530),'#24302b');d=ImageDraw.Draw(out)
    for i,im in enumerate(demo):
        lx=(i%4)*202;ly=(i//4)*265;lab=rows[i]['direction'];d.rounded_rectangle((lx+8,ly+6,lx+195,ly+258),radius=7,fill='#2a3533',outline='#635a42');d.text((lx+16,ly+18),lab,fill='#e9c591');q=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST);out.paste(q,(lx+101-q.width//2,ly+149-q.height//2),q)
    png(out,W/'Essai-Etendards.png');print([(v['direction'],v['w'],v['h']) for v in rows]);print('8 projections différentes · 6 poses chacune')

if __name__=='__main__':main()
