#!/usr/bin/env python3
"""Eight true camera projections of a hand-built counter with an AI concept texture.
Each projected column has its own depth, walnut carcass, backed shelves and stone lip.
The 1x PNGs are never rotated. Floor samples are projected from that same model.
"""
from pathlib import Path
from math import cos,sin,pi
from hashlib import sha256
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation

ROOT=Path(__file__).resolve().parents[1]; DEST=ROOT/'PNG-1x'; W=Path.home()/'.cache/comptoirs-et-falaise'
SRC=ROOT/'Reference/Comptoir-etude-IA.png'; HAL=ROOT.parent/'Mobilier-Halcyon/Originaux-1x/comptoir-cloche.png'; PRI=(80,80); SIZE=(160,152); CY=.57
DIRS=[('Down','Face','↓'),('DownRight','Avant droit','↘'),('Right','Profil droit','→'),('UpRight','Arrière droit','↗'),('Up','Dos','↑'),('UpLeft','Arrière gauche','↖'),('Left','Profil gauche','←'),('DownLeft','Avant gauche','↙')]
# Clockwise outer boundary. The service opening, with shelves, is at v < 0.
U=np.array([(-37,-19),(-25,-19),(-25,0),(-20,5),(20,5),(25,0),(25,-19),(37,-19),(41,-15),(41,7),(38,13),(31,18),(24,20),(-24,20),(-31,18),(-38,13),(-41,7),(-41,-15)],dtype=float)
Y,X=np.indices((SIZE[1],SIZE[0]),dtype=float); X+=.5-PRI[0];Y+=.5-PRI[1]

def pal(z):return np.array(tuple(bytes.fromhex(z)),dtype=float)

# The threshold and quantisation select the real little brass bell in the IA study.
def concept():
    im=Image.open(SRC).convert('RGB');assert im.size==(1504,704)
    grain=np.asarray(im.crop((485,272,1013,370)).resize((38,8),Image.Resampling.BOX)).astype(float)
    st=np.mean(grain,axis=(0,1));grain-=st
    a=np.asarray(im.crop((1208,137,1308,259)).resize((8,10),Image.Resampling.NEAREST)).astype(int)
    r,g,b=a.transpose(2,0,1);m=((r>g+12)&(r>b+29))|((r<91)&(g<87)&(b<73))
    colors=np.asarray([pal(z) for z in ['24190e','46301e','71502e','9b6c37','c29347','e2b869','f0d393','fbe8ad']]);inds=((a[:,:,None,:]-colors)**2).sum(3).argmin(2)
    out=np.dstack((colors[inds].astype('uint8'),m.astype('uint8')*255));out[~m]=0;return grain,st,Image.fromarray(out)


def inside(p,x,y):
    isin=np.zeros_like(x,dtype=bool)
    for j,a in enumerate(p):
        b=p[(j+1)%len(p)]
        if a[1]!=b[1]:isin^=((a[1]>y)!=(b[1]>y))&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])
    return isin


def draw(i):
    theta=i*pi/4;cs=round(cos(theta),12);sn=round(sin(theta),12)
    def R(u,v):return u*cs+v*sn,-u*sn+v*cs
    def inv(x,y):return x*cs-y*sn,x*sn+y*cs
    u,v=R(U[:,0],U[:,1]);poly=np.stack((u,v),axis=1)
    pix=np.zeros((SIZE[1],SIZE[0],4),dtype='uint8');dep=np.full(X.shape,-1e8)
    grain,st,bell=concept()
    def coat(valid,depth,color):
        take=valid&(depth>dep)
        dep[take]=np.broadcast_to(depth,dep.shape)[take]
        pix[take,:3] = np.clip(np.rint(np.broadcast_to(color,(*dep.shape,3))[take]),0,255).astype('uint8');pix[take,3]=255
    # levels: those upper edges catch real light; the dark joint under the stone is 1 px.
    for j,a in enumerate(poly):
        b=poly[(j+1)%len(poly)];f=b-a;L=np.linalg.norm(U[(j+1)%len(U)]-U[j]);norm=np.array([f[1],-f[0]])/L
        if norm[1]<1e-7:continue
        side=norm[0]; face=norm[1]; S=(face-.62)*13-side*9
        back=j in {1,2,3,4,5};front=j==12;vertical_long=j in {8,16};wood=pal('814e32' if not back else '653c2c')
        # Three darker wood shelves on the inner long wall; panels on ends and frontage.
        for lo,hi,sca,mat in [(0,1,.965,'foot'),(1,4,.965,'plinth'),(4,5,.970,'base-highlight'),(5,17,.974,'wood'),(17,18,.974,'rail'),(18,19,1,'joint'),(19,22,1,'stone')]:
            ax,ay=a*sca;bx,by=b*sca;t=(X-ax)/(bx-ax);yp=ay+(by-ay)*t;Z=yp*CY-Y;z=np.floor(Z);D=yp+CY*Z
            valid=(t>=0)&(t<1)&(Z>=lo)&(Z<hi);u=np.floor(t*L);rng=(u*37+z*11+j*61)%29
            if mat=='wood':
                v=u+2*j;start=(v%10<=.1);end=(u<=.1)|(u>=L-1.7);rail=(z==5)|(z==16)
                # Grain on upright planks, not random single-pixel noise.
                stripe=((v+((z+2*j)//3))%11==2)&(z>=7)&(z<=15)
                grainv=np.where(stripe,9,0)+np.where((v%7==3)&((z+j)%11>3),-6,0)+np.where(rng==5,4,0)
                vals=grainv+np.where(start|end,-18,0)+np.where(rail,-13,0)
                if front:
                    # Five inset panels, each framed along the upper and lower rails.
                    panel=(u%9.4);recess=(panel>1)&(panel<8)&(z>=8)&(z<=14);vals+=np.where(recess,4,0)+np.where((panel>8.1)&(z>=7)&(z<=15),-19,0)
                if back and j==3:
                    # The actual rear: separate darker cavities with an exposed shelf.
                    cell=u%13.4;opening=(cell>1.8)&(cell<11.7)&(z>=7)&(z<16);
                    vals=np.where(opening,-23+(z-8)*.85,vals)
                    vals+=np.where(opening&(z==10),25,0)+np.where(opening&(z==9),9,0)
                if vertical_long:vals+=np.where((z==11)&(u>4)&(u<L-4),7,0)
                color=wood+(S+vals)[...,None]*np.array([1,.80,.65])
            elif mat=='stone':
                stone=st*np.array([.95,.97,.96])+np.array([1,0,-2]);light=np.where(z==21,24,np.where(z==19,-33,-13))+S*.8
                color=stone+light[...,None]+np.where((rng==5)[...,None],-3,0)
                if L>42 and not back:
                    rivet=(np.abs(u-(L/2))<1.05)|(np.abs(u-(L*.19))<.8)|(np.abs(u-(L*.81))<.8)
                    color=np.where((rivet&(z==20))[...,None],pal('ba985f')+S*.3,color)
            else:
                base={'foot':'322119','plinth':'5e3e2a','base-highlight':'99734b','rail':'603b29','joint':'36271e'}[mat]
                color=pal(base)+S*np.array([.82,.65,.52])
            coat(valid,D,color)
    # Horizontal stone cap. Its little seams meet the sides of the same model.
    yv=(Y+22)/CY;xw,yw=inv(X,yv);valid=inside(U,xw,yw);d=yv+CY*22+.01
    # Native pixel bevel: a distance field in world units, computed only for the cap.
    signed=[]
    for j,a in enumerate(U):
        b=U[(j+1)%len(U)];f=b-a;t=np.clip(((xw-a[0])*f[0]+(yw-a[1])*f[1])/np.dot(f,f),0,1);dist=np.hypot(xw-(a[0]+t*f[0]),yw-(a[1]+t*f[1]));signed.append(dist)
    dist=np.stack(signed);mi=dist.argmin(axis=0);md=dist.min(axis=0);gs=grain[(np.floor(yw).astype(int)+8)%8,(np.floor(xw).astype(int)+38)%38]
    stone=st*np.array([1.03,1.01,.94])+np.array([4,3,3]);seam=(np.abs(np.abs(xw)-25)<.57)&(yw>6)
    # Light ribbon on exposed edges, quiet pitting/colour in the top stone.
    bits=(np.floor(xw).astype(int)*13+np.floor(yw).astype(int)*7)%37
    dcol=np.where(md<.95,-40,np.where(md<2.5,20,np.where(md<3.7,5,0)))+np.where(seam,-21,0)+np.where(bits<3,3,np.where(bits>34,-3,0))
    mottled=gs*1.65+dcol[...,None];coat(valid,d,stone+mottled)
    # Export a 1px deliberate silhouette, then emboss the bell, copied from the study.
    solid=pix[...,3]>0;edge=binary_dilation(solid)&~solid;pix[edge]=[48,32,24,255]
    im=Image.fromarray(pix);u,v=R(32,-11);xx=round(PRI[0]+u);yy=round(PRI[1]+v*CY-22);im.alpha_composite(bell,(xx-4,yy-8))
    bb=im.getbbox();out=im.crop(bb);p=[PRI[0]-bb[0],PRI[1]-bb[1]]
    # Work in room-plan pixels rather than over the entire upright picture. Include
    # near vertices/edges and keep a customer aisle along the long public-facing side.
    fp=set(); aisle=set()
    for u in range(-41,42,3):
        for v in range(-19,21,3):
            if inside(U,np.array(float(u)),np.array(float(v))):
                a,b=R(u,v);fp.add((p[0]+round(a),p[1]+round(b*CY)))
    for u in range(-29,30,4):
        for v in [23,29,35,42]:
            a,b=R(u,v);aisle.add((p[0]+round(a),p[1]+round(b*CY)))
    # Where to sample the actual weight of this counter, not the height of the top.
    return out,p,sorted(fp),sorted(aisle)


def main():
    DEST.mkdir(exist_ok=True);W.mkdir(exist_ok=True); rows=[];images=[]
    for i,(label,fr,sign) in enumerate(DIRS):
        im,p,fp,aisle=draw(i);images.append(im);file=DEST/(label+'.png');im.save(file,optimize=True)
        assert len(fp)>=160 and im.getpixel((0,0))[3]==0,(len(fp),im.getpixel((0,0)))
        rows.append({'id':'comptoir-'+label.lower(),'direction':label,'nom':fr,'flèche':sign,'w':im.width,'h':im.height,'pivot':p,'empreinte':fp,'allée':aisle,'png':str(file.relative_to(ROOT)),'sha256':sha256(file.read_bytes()).hexdigest()})
    (ROOT/'Index-Comptoirs.json').write_text(json.dumps({'source_modele_halcyon':{'fichier':HAL.name,'sha256':sha256(HAL.read_bytes()).hexdigest()},'source_etude_ia':{'fichier':str(SRC.relative_to(ROOT)),'sha256':sha256(SRC.read_bytes()).hexdigest()},'projection':'orthographique et dessinee par faces ; 1 PNG par axe, sans rotation d’image','orientations':rows},ensure_ascii=False,separators=(',',':'))+'\n')
    pre=Image.new('RGB',(950,605),'#27232c');d=ImageDraw.Draw(pre)
    for i,im in enumerate(images):
        x=i%4*234+8;y=i//4*294+8;d.rounded_rectangle((x,y,x+222,y+279),radius=10,fill='#38323c',outline='#5b4e44');d.text((x+9,y+15),DIRS[i][0]+' / '+DIRS[i][1],fill='#efd7ad');n=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST); pre.paste(n,(x+(222-n.width)//2,y+151-n.height//2),n)
    pre.save(W/'Huit-vues-test.png');print([(v['direction'],v['w'],v['h'],len(v['empreinte'])) for v in rows]);assert len({v['sha256'] for v in rows})==8

if __name__=='__main__':main()
