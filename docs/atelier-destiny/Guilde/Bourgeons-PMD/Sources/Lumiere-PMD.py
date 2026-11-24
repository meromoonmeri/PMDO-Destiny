#!/usr/bin/env python3
"""Transfer real G01P01C colour steps and timing, not scenery or flame pixels."""
import json, hashlib, base64
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parents[1]
G=OUT.parent
BASE=G/'Guilde-Destiny-Lumiere-Ancree.html'
AP=OUT/'Reference/G01P01C-Falaise-Nuit.png'
SOURCE='https://projectpokemon.org/home/gallery/image/77577-g01p01cpng/'
MARK='<script id="donnees" type="application/json">'
LUMA=np.array([.2126,.7152,.0722]); MAX_ALPHA=25; MAX_BUD=67


def page(path=BASE):
 h,rest=path.read_text(encoding='utf8').split(MARK,1);s,tail=rest.split('</script>',1)
 return h,json.loads(s),tail


def decode(uri):
 with Image.open(BytesIO(base64.b64decode(uri.rsplit(',',1)[-1]))) as im:
  return np.array(im.convert('RGBA'))


def uri(raw, kind='image/png'):
 return f'data:{kind};base64,'+base64.b64encode(raw).decode('ascii')


def pack(im,lossless=True):
 if isinstance(im,np.ndarray):im=Image.fromarray(im)
 b=BytesIO();im.save(b,'WEBP',lossless=lossless,method=4,quality=90,exact=True)
 return uri(b.getvalue(),'image/webp')


def jsonout(path,data):
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def ref_frames():
 with Image.open(AP) as im:
  frames=[];delays=[]
  for i in range(im.n_frames):
   im.seek(i);frames.append(np.array(im.convert('RGB')));delays.append(im.info['duration'])
 a=np.asarray(frames)
 assert a.shape==(4,408,480,3) and all(abs(v-1000/6)<.0001 for v in delays)
 return a,delays


def read_reference():
 a,delays=ref_frames();digest=hashlib.sha256(AP.read_bytes()).hexdigest()
 assert digest=='a62e368a20edfde44d170977361f286add36f71c85127804ec5df49360f7f635'
 diff=np.any(a!=a[0],axis=(0,3));assert diff.sum()==6283
 # Read the four colour tracks exclusively on stone, away from the flame sprites.
 xy=[(151,160),(167,145),(180,156),(151,164)]
 paint=np.stack([a[:,y,x] for x,y in xy],axis=1)
 hit=[];notes={}
 zones={'pierres_ouest':(143,145,192,174),'pierres_est':(288,145,337,174),'facade':(194,106,286,141),'chemin_central':(223,215,251,289),'ciel':(110,15,360,55)}
 for k,(x,y,X,Y) in zones.items():
  rgb=a[:,y:Y,x:X];raw=rgb@LUMA;extent=np.ptp(raw,axis=0);changed=extent>.1
  notes[k]=dict(zone=[x,y,X,Y],pixels_variables=int(changed.sum()),pic_luma=round(float(extent.max()),2))
  if k.startswith('pierres'):
   quiet=(extent>3)&(extent<35)&(rgb[...,0].min(0)>160)&(rgb[...,2].min(0)>30)
   assert changed.sum()>140 and quiet.sum()>50
   levels=raw[:,quiet].mean(1);notes[k]['luminosite_4_images']=np.round(levels,3).tolist()
   # Match the reference temporal curve, but use a short, low-alpha response indoors.
   gain=.70+.30*(levels-levels.min())/np.ptp(levels);hit.append(gain)
 assert notes['chemin_central']['pixels_variables']==notes['ciel']['pixels_variables']==0
 report=dict(source=SOURCE,extraction='MegaMinerd · archive Project Pokémon publiée par evandixon',carte='G01P01C',lieu='Extérieur, entrée de la guilde de Grodoudou au sommet de la falaise',sha256=digest,dimensions=[480,408],durees_ms=delays,pixels_variables=int(diff.sum()),releves=notes,teintes=[dict(coordonnees=list(xy[j]),rgb=paint[:,j].tolist()) for j in range(4)],notes=['Les deux braseros supérieurs éclairent notamment les pierres et la façade ; le sol éloigné contrôlé et le ciel échantillonné restent fixes.','Les teintes chaudes et les quatre phases sont reportées dans Destiny. Aucun pixel de flamme ni de décor de la falaise n’est reporté à l’intérieur.'])
 return a,paint,hit,report


def extract_alpha(d,r):
 glass=np.zeros((r['h'],r['w']),bool);tone=d['nuits'][r['nuit']]['verre']
 for x,y,bit in r['patches'][3]:
  p=decode(bit);h,w=p.shape[:2];glass[y:y+h,x:x+w]=(p[:,:,:3]==tone).all(2)&(p[:,:,3]==255)
 guard=glass.copy()
 for x,y,w,h in [g['rect'] for g in r['gates']]+r['mark']: guard[y:y+h,x:x+w]=True
 if r['south']:guard[r['south']['bottom']:]=True
 return guard


def recolour(d,tones,response):
 # Geometry and occlusion from the existing generated matte. Allow colour cycling
 # on its existing footprint only, and pin the emitted light to actual bud texels.
 proof=[]
 for r in d['rooms']:
  q=d['lianes'][r['id']];guard=extract_alpha(d,r);fibres=np.zeros(guard.shape,np.uint8)
  for k in ('s','t'):fibres=np.maximum(fibres,decode(q[k])[...,3]);
  updated=[]
  for s in q['points']:
   x,y,body=s['l'];u,v,bud=s['b'];a0=decode(body)[...,3];b0=decode(bud)[...,3]
   h,w=a0.shape;j,k=b0.shape
   assert b0.max()>0 and a0.max()>0 and (fibres[v:v+j,u:u+k][b0>0]>0).all()
   bands=np.digitize(a0,[6,11,17]);centers=np.asarray([3.5,8,13.5,21.])[bands]
   # The carved leaf occlusion is retained in the alpha. Native texel-scale bands
   # echo the palette changes of the stone without outlining the whole room.
   support=(.72*a0+.28*centers);support[a0==0]=0
   strength=response[int(float(s['x'])>=r['w']/2)];frames=[];steps=[]
   bscale=b0.astype(float)/46.;y1=y+h;x1=x+w;v1=v+j;u1=u+k
   for i,z in enumerate(strength):
    A=np.rint(np.minimum(MAX_ALPHA,support*z)).astype(np.uint8)
    B=np.rint(np.minimum(MAX_BUD,bscale*(49+18*(z-.70)/.30))).astype(np.uint8)
    A[guard[y:y1,x:x1]]=0;B[guard[v:v1,u:u1]]=0
    aa=np.dstack((tones[i][bands],A));aa[A==0]=0
    bb=np.empty((j,k,4),dtype=np.uint8);bb[:,:,:3]=tones[i,-1];bb[:,:,3]=B;bb[B==0]=0
    frames.append([[x,y,pack(aa)],[u,v,pack(bb)]]);steps.append([int(A.max()),int(B.max())]);
   assert len({p[0][2] for p in frames})==4 and max(e[0] for e in steps)<=25
   updated.append(dict(x=s['x'],y=s['y'],images=frames));proof.append(dict(salle=r['id'],bourgeon=[s['x'],s['y']],pixels_source=int((b0>0).sum()),alpha_par_image=steps))
  q.pop('reflets');q['points']=updated
 assert len(proof)==30
 return proof


def night_base(r,d):
 lut=np.array(d['nuits'][r['nuit']]['lut'], dtype=np.uint8)
 def shade(s):
  a=decode(s)
  for i in range(3):a[...,i]=lut[i,a[...,i]]
  return Image.fromarray(a)
 bg=shade(r['base']);layer=d['lianes'][r['id']]
 for x,y,bit in r['patches'][3]:bg.paste(Image.fromarray(decode(bit)),(x,y))
 for a in (shade(layer['s']),shade(r['front']),shade(layer['t'])):bg.alpha_composite(a)
 return np.array(bg.convert('RGB'),dtype=float)


def night_frames(r,d):
 a0=night_base(r,d);frames=[];guard=extract_alpha(d,r)
 for i in range(4):
  acc=a0.copy()
  for s in d['lianes'][r['id']]['points']:
   for x,y,bit in s['images'][i]:
    q=decode(bit);h,w=q.shape[:2];p=acc[y:y+h,x:x+w];p+=(255-p)*(q[:,:,:3]/255.)*(q[:,:,3:]/255.)
  frames.append(np.rint(acc).astype(np.uint8));assert np.array_equal(frames[-1][guard],a0[guard].astype(np.uint8))
 return frames
