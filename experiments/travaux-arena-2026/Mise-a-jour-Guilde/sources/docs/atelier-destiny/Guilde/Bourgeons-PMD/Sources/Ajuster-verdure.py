#!/usr/bin/env python3
"""Fit selected vine spirals to the native timber, and follow moved buds with PMD light."""
from pathlib import Path
import hashlib,importlib.util
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from scipy.interpolate import PchipInterpolator

O=Path(__file__).resolve().parents[1];G=O.parent;CACHE=Path.home()/'.cache/verdure-ajustee'
ASSET=O/'Verdure/Ronce-de-poteau.png';RAW=CACHE/'Rameau-ronce-genere.png'

def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);return a
fx=load('enroulements',G/'Animations-Destiny/Sources/Enrouler-et-eclairer.py');old=fx.old
# Room/detail IDs follow Index-nuit-et-poteaux.json. Knots: verified shaft centre at
# crown, mouldings, body and foot. Width is varied through the tapered timber.
FIX={
 (1,2):('Accueil · côté est',[(335,79),(336,94),(336,116),(336,132),(337,140)],21,[(77,90),(133,144)]),
 (2,4):('Missions · montant droit',[(527,121),(525,147),(525,172),(524,194),(523,209)],21,[(146,165)]),
 (3,1):('Grand Salon · poteau ouest',[(63,124),(63,141),(62,160),(62,180),(62,191)],23,[(141,154),(181,194)]),
 (3,2):('Grand Salon · poteau est',[(515,124),(514,142),(513,160),(513,180),(513,191)],23,[(141,154),(181,194)]),
 (3,3):('Grand Salon · baie ouest',[(154,81),(157,97),(158,116),(158,136),(157,152)],24,[(88,102),(146,158)]),
 (3,4):('Grand Salon · baie est',[(420,81),(421,97),(421,118),(421,137),(420,152)],24,[(88,103),(145,158)]),
 (4,1):('Bureau · montant de baie',[(211,53),(209,69),(210,90),(210,108),(209,119)],21,[(56,72),(111,123)]),
 (6,1):('Réfectoire · poteau central',[(284,65),(286,81),(286,102),(285,122),(286,136)],23,[(68,84),(125,140)]),
 (6,2):('Réfectoire · côté service',[(513,126),(513,148),(513,169),(513,195),(513,212)],24,[(147,165),(205,219)]),
 (7,3):('Cuisine · baie est',[(355,61),(356,77),(356,93),(357,108),(357,118)],19,[(65,77),(110,121)]),
 (9,1):('Couloir ouest · colonne intérieure',[(143,66),(142,79),(142,94),(142,106),(143,114)],20,[(70,84),(105,117)]),
 (10,1):('Couloir est · colonne intérieure',[(337,66),(337,79),(337,94),(337,107),(337,115)],20,[(70,84),(106,118)]),
 (11,2):('Dortoir nord I · poteau est',[(328,80),(329,100),(329,118),(329,137),(328,147)],22,[(95,108),(137,151)]),
 (12,1):('Dortoir nord II · poteau ouest',[(120,80),(120,99),(120,116),(120,138),(121,147)],22,[(97,109),(138,151)]),
 (15,2):('Chambre du héros · poteau extérieur',[(386,112),(385,129),(385,149),(385,167),(384,185),(384,193)],23,[(123,134),(142,156),(188,196)]),
}
# Short offshoots along lower moulding, away from exits; never new light sources.
RONCES={(3,1):(-1,22,7),(3,2):(1,22,7),(6,1):(1,24,8),(9,1):(-1,19,7),(10,1):(1,19,7),(15,2):(-1,21,7)}
ANCHORS={1:(0,1),2:(2,1),3:(2,3),4:(0,1),5:(0,1),6:(2,3),7:(0,2),8:(0,1),9:(0,1),10:(1,0),11:(2,1),12:(0,1),13:(0,1),14:(1,0),15:(0,2)}

def bramble():
 if not ASSET.exists():
  with Image.open(RAW) as im:a=np.array(im.convert('RGB'))
  r,g,b=a.astype(int).transpose(2,0,1);m=~((r>=80)&(b>=75)&(r-g>=35)&(b-g>=29)&(b>=r*.52));labs,n=nd.label(m,np.ones((3,3)));c=np.bincount(labs.ravel());c[0]=0;m=labs==c.argmax();assert m.sum()>20000
  a=np.dstack((a,(m*255).astype(np.uint8)));a[~m]=0;im=Image.fromarray(a);im=im.crop(im.getbbox()).resize((61,18),Image.Resampling.BOX);a=np.array(im);m=a[...,3]>=128;a[~m]=0;a[m,3]=255
  ASSET.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(a).save(ASSET,optimize=True)
 with Image.open(ASSET) as im:return np.array(im.convert('RGBA'))

def modules():
 v={k:old.describe_sprite(k) for k in (fx.CORNICHE,fx.R,fx.A)};u=[]
 for i,name in enumerate(('Reverie','ceremonie')):
  with Image.open(G/'Animations-Destiny/Lianes-de-poteaux'/f'Enroulement-de-{name}.png') as im:a=np.array(im.convert('RGBA'))
  u.append((a,fx.collect_flower(a,bool(i))))
 return v,u

def axis_at(nodes,y):
 p=np.asarray(nodes);return PchipInterpolator(p[:,1],p[:,0])(np.clip(y,p[0,1],p[-1,1]))

def winding(source,x,y,entry,flip,allowed):
 _,nodes,width,rims=entry;p=np.asarray(nodes);ax=axis_at(nodes,y);dx=x-ax
 start,end=p[0,1],p[-1,1];height=end-start+1;t=np.clip((y-start)/(height-1),0,1)
 # Keep more spread in the torso, taper at the cap and when the stem meets the plinth.
 span=width*(.83+.17*np.sin(np.pi*t))
 tex,labels=source;h,w=labels.shape
 u=np.rint((dx/(span-1)+.5)*(w-1)).astype(int);v=np.rint(t*(h-1)).astype(int)
 m=(y>=start)&(y<=end)&(u>=0)&(u<w)&allowed
 occl=np.zeros_like(m)
 for lo,hi in rims:
  stripe=(y>=lo)&(y<=hi);fade=np.sin(np.pi*np.clip((y-lo+.4)/(hi-lo+.8),0,1))
  # The stem disappears behind the face of the gilded collar, peeking out at the rim.
  # Preserve a little green on the edges, and never a square cap on the carving.
  occl|=stripe&(np.abs(dx)<(width*.29+2.2)*(.35+.65*np.sqrt(fade)))
 m&=~occl
 if flip:u=w-1-u
 a=np.zeros((*x.shape,4),np.uint8);seed=np.zeros(x.shape,np.int16)
 a[m]=tex[v[m],u[m]];seed[m]=labels[v[m],u[m]]
 body=a[...,3]>0
 gain=.99-.27*np.minimum(1.,np.abs(dx)/(width*.48))**1.65
 a[body,:3]=np.rint(a[body,:3]*gain[body,None]*[.97,1.,.92]).astype(np.uint8)
 return a,seed,occl

def foot(tex,x,y,entry,style,allowed):
 _,nodes,width,_=entry;direction,w,h=style;xc,yend=nodes[-1];cy=yend-7
 dx=x-(xc+direction*3.);dy=y-cy;centre=.12*direction*dx+.012*dx**2
 u=np.rint((dx/(w-1)+.5)*(tex.shape[1]-1)).astype(int);v=np.rint(((dy-centre)/(h-1)+.5)*(tex.shape[0]-1)).astype(int)
 live=(u>=0)&(u<tex.shape[1])&(v>=0)&(v<tex.shape[0])&(y<=yend-1)&allowed
 if direction<0:u=tex.shape[1]-1-u
 a=np.zeros((*x.shape,4),np.uint8);a[live]=tex[v[live],u[live]];m=a[...,3]>0
 a[m,:3]=np.rint(a[m,:3]*[.86,.91,.83]).astype(np.uint8)
 return a

def combine(parts,where,fore):
 hh,ww=where.shape;flora=Image.new('RGBA',(ww,hh));shade=np.zeros_like(where,dtype=float)
 for a in parts:
  flora.alpha_composite(Image.fromarray(a));m=a[...,3]>0;cast=np.zeros_like(shade);cast[2:,1:]=m[:-2,:-1];shade=np.maximum(shade,nd.gaussian_filter(cast,1.12)*.53)
 s=Image.fromarray(fx.rgba(np.rint(255*shade*where).astype(np.uint8),(29,20,12)));s.alpha_composite(flora);all=np.array(s);A=all.copy();B=all.copy();A[fore]=0;B[~fore]=0
 return A,B,np.array(flora)

def lamp_pixels(ref,L):
 x,y,bit=ref;v=L.decode(bit);yy,xx=np.where(v[...,3]>0);return x+xx,y+yy,v

def projected_shadow(sx,sy,flora,x,y,room_width):
 a=flora.astype(int);leaves=(a[...,3]>0)&(a[...,1]>=a[...,0]*.78)&(a[...,1]>=a[...,2]+16)
 chosen=leaves&(abs(x-sx)<17)&(abs(y-sy)<25)&((x-sx)**2+(y-sy)**2>18)
 hh,ww=x.shape;yy,xx=np.where(chosen);hand=1 if sx<room_width/2 else -1
 u=np.rint(sx+1.24*(xx-sx)+hand*1.4).astype(int);v=np.rint(sy+1.20*(yy-sy)+2).astype(int)
 m=(u>=0)&(v>=0)&(u<ww)&(v<hh);a=np.zeros_like(x,dtype=float);np.maximum.at(a,(v[m],u[m]),1.)
 return nd.gaussian_filter(a,1.15)

def fitted_lamp(p,L,r,n,idx,info,flora,forbid,lightmask,floor,x,y):
 sx,sy=float(p['x']),float(p['y']);rx,ry=np.rint([sx,sy]).astype(int)
 a,b,_=lamp_pixels(p['images'][0][1],L)
 if idx not in info and (flora[b,a,3]>0).all():return p,False
 route,entry,pic,lab,br=info[idx]
 _,_,_,_,nodes=route;_,new,width,_=entry
 cy=np.interp(sy,[nodes[0][1],nodes[-1][1]],[new[0][1],new[-1][1]]);cx=float(axis_at(new,cy))+(sx-float(axis_at(nodes,sy)))*.74
 visible=(pic[...,3]>0)&(flora[...,3]>0)&~forbid&~br
 spots=[]
 for k in np.unique(lab[visible]):
  if not k:continue
  m=(lab==k)&visible;yy,xx=np.where(m);z=np.hypot(xx.mean()-cx,yy.mean()-cy)
  if z<=11.:spots.append((z-.10*min(len(xx),6),m))
 if spots:
  best=min(spots,key=lambda q:q[0])[1]
 else:
  rr,gg,bb,alpha=pic.astype(int).transpose(2,0,1);near=((x-cx)**2+(y-cy)**2<=105)&visible
  warm=near&(rr>=gg-6)&(rr>=bb+19)&(gg>=bb+10)
  if warm.sum()<3:warm=near&(rr>=44)&(gg>=bb+11)
  assert warm.sum()>=3,(r['label'],idx,cx,cy,int(warm.sum()))
  z=.52*rr+.39*gg-.21*bb-.74*((x-cx)**2+(y-cy)**2);l=np.argmax(np.where(warm,z,-np.inf));v,u=np.unravel_index(l,x.shape)
  best=warm&((x-u)**2+(y-v)**2<=3.)
 # Stamp only the selected vein/bud pixels, never the bramble or bare wood.
 yy,xx=np.where(best);sx1,sy1=float(xx.mean()),float(yy.mean());assert np.hypot(sx1-sx,sy1-sy)<19
 dx=sx1-sx;dy=sy1-sy;hb=fx.clipbox(fx.rgba(best.astype(np.uint8),[0,0,0]));bx,by,m=hb;bw,bh=m.shape[1],m.shape[0];m=m[...,3]>0
 shade=projected_shadow(sx1,sy1,flora,x,y,r['w'])
 frames=[]
 for a0,b0 in p['images']:
  ox,oy,bit=a0;q=L.decode(bit);h,w=q.shape[:2];arr=L.decode(b0[2]);rgb=np.array(arr[arr[...,3]>0][0,:3]);peak=int(arr[...,3].max());core=fx.rgba(m.astype(np.uint8)*peak,rgb)
  # Shift the existing reflected-light footprint from the new point. Near the floor,
  # keep the original projection plane. Additional leaf occlusion is local.
  u=np.rint(x-ox-dx).astype(int);v=np.rint(y-oy-dy*np.where(floor,.42,1.)).astype(int)
  valid=(u>=0)&(u<w)&(v>=0)&(v<h)&~forbid&(lightmask>0)&(abs(x-sx1)<74)&(abs(y-sy1)<87)
  f=np.zeros((*x.shape,4),np.uint8);f[valid]=q[v[valid],u[valid]];shifted=np.rint(f[...,3]*np.minimum(1,lightmask*1.2)*(1-.36*np.minimum(1,shade))).astype(np.uint8);f[...,3]=shifted;f[shifted==0]=0
  frames.append([fx.lights_pack(f),[bx,by,L.pack(core)]]);assert f[...,3].max()<=25
 return dict(x=round(sx1,2),y=round(sy1,2),images=frames),True

def run(d,L):
 asset=bramble();art,reverie=modules();report=[]
 for r in d['rooms']:
  n=r['n'];plans={j:spec for (k,j),spec in FIX.items() if k==n}
  if not plans:continue
  q=d['lianes'][r['id']];b,f,x,y,floor,glass,gates,bottom,allowed,lightmask=fx.freeze_support(r,d);forbid=L.extract_alpha(d,r)
  source=[],[];before,after=source;info={};cnt=0;rp=0
  for route,noble in fx.grow_routes(r)[0]:
   k,nom,w,flip,p=route;tex=reverie[noble] if k==fx.V else art[k]
   a,lab=old.warp(*tex,route,x,y);m=(a[...,3]>0)&allowed;a[~m]=0;lab[~m]=0
   if k==fx.V:
    rp+=1;axis=np.interp(y,np.asarray(p)[:,1],np.asarray(p)[:,0]);distance=np.clip(abs(x-axis)/(w*.65),0,1);gain=np.clip(.97-.40*distance**2+.037*np.sin(y/10.),.60,1.0)
    a[m,:3]=np.rint(a[m,:3]*gain[m,None]*[.97,1.,.91]).astype(np.uint8)
   else:
    tint=np.array([1.00,.96,.91]) if k!=fx.R else np.array([.89,.93,.85]);a[m,:3]=np.clip(np.rint(a[m,:3]*tint),0,255).astype(np.uint8)
   before.append(a)
   if k==fx.V and rp in plans:
    var=plans[rp];loc=allowed&~nd.binary_dilation(glass,iterations=2)
    c,lab,hide=winding(tex,x,y,var,flip,loc);visible=c[...,3]>0
    assert visible.sum()>=77 and (hide&m).sum()>6,(n,rp,int(visible.sum()))
    if (n,rp) in RONCES:
     g=foot(asset,x,y,var,RONCES[n,rp],loc&~forbid);assert (g[...,3]>0).sum()>21,(n,rp)
     canvas=Image.fromarray(g);canvas.alpha_composite(Image.fromarray(c));after.append(np.array(canvas));br=(g[...,3]>0)&~visible
    else:after.append(c);br=np.zeros_like(visible)
    info[rp]=(route,var,c,lab,br)
    report.append(dict(salle=r['label'],poteau=rp,nom=var[0],axe_avant=p,axe_ajuste=var[1],largeur_avant=w,largeur_ajustee=var[2],anneaux_proteges=var[3],rameau=(n,rp) in RONCES))
   else:after.append(a)
   cnt+=len(np.unique(lab[lab>0]))
  A,B,_=combine(before,allowed,f[...,3]>0)
  assert np.array_equal(A,L.decode(q['s'])) and np.array_equal(B,L.decode(q['t'])),('reconstruction source',n)
  A,B,flora=combine(after,allowed,f[...,3]>0)
  assert not (A[...,3][forbid].any() or B[...,3][forbid].any()),('masques protégés',n)
  lamps=[]
  for j,p in enumerate(q['points']):lamps.append(fitted_lamp(p,L,r,n,ANCHORS[n][j]+1,info,flora,forbid,lightmask,floor,x,y)[0])
  for s in lamps:
   for _,t in s['images']:
    xx,yy,_=lamp_pixels(t,L);assert (flora[yy,xx,3]>0).all() and not forbid[yy,xx].any()
  q.update(s=L.pack(A),t=L.pack(B),n=cnt,points=lamps)
  print(f'{r["label"]} : {len(plans)} enroulement(s) corrigé(s)',flush=True)
 return dict(statut='PASS',poteaux_total=42,poteaux_repris=len(report),rameaux_courts=len(RONCES),poteaux=report,source_ronce=hashlib.sha256(ASSET.read_bytes()).hexdigest())
