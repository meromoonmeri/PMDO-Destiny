#!/usr/bin/env python3
"""Optional non-emitting generated reliefs with fitted wall-tangent projection."""
from pathlib import Path
import base64,hashlib,json
from io import BytesIO
from PIL import Image
from scipy import ndimage as nd
import numpy as np

O=Path(__file__).resolve().parents[1]/'Ornements'
IA=Path.home()/'.cache/braseros-falaise/ia'
S={'frise':('Frise.png',(88,16),'Frise-laurier.png'),'ecusson':('Ecusson.png',(38,60),'Ecusson-aile.png')}
# Anchor in the face of the real panelling. dx and dx² terms follow the curve, with a
# smaller cross-slope on the relief to preserve a vertical impression on the wall.
PLACEMENTS={
 2:[('frise',198,111,47,7,-.12,.0018),('frise',378,111,47,7,.12,.0018)],
 3:[('frise',201,111,42,7,-.12,.0026),('frise',375,111,42,7,.12,.0026)],
 4:[('ecusson',172,73,16,27,-.17,.0016),('ecusson',344,73,16,27,.17,.0016)],
 5:[('frise',178,67,38,7,-.34,.002),('frise',302,67,38,7,.34,.002)],
 6:[('frise',94,125,41,7,-.55,.003),('frise',483,125,41,7,.55,.003)],
 7:[('ecusson',240,71,14,22,0,.002)],
 9:[('frise',180,66,37,7,-.31,.002),('frise',298,66,37,7,.31,.002)],
 10:[('frise',180,66,37,7,-.31,.002),('frise',298,66,37,7,.31,.002)],
 15:[('ecusson',181,71,15,24,-.15,.0016),('ecusson',310,71,15,24,.15,.0016)],
}


def acquire(k):
 f,sz,dst=S[k];photo=IA/f;out=O/dst
 if not out.exists():
  with Image.open(photo) as im:a=np.array(im.convert('RGB'))
  r,g,b=a.astype(np.int16).transpose(2,0,1);mask=~((r>=85)&(b>=80)&(r-g>=47)&(b-g>=28)&(b>=r*.56))
  labs,n=nd.label(mask,np.ones((3,3)));cs=np.bincount(labs.ravel());cs[0]=0;mask=labs==np.argmax(cs)
  assert mask.sum()>40000
  rgba=np.dstack((a,255*mask.astype(np.uint8)));rgba[~mask]=0
  im=Image.fromarray(rgba);im=im.crop(im.getbbox()).resize(sz,Image.Resampling.BOX)
  q=np.array(im);m=q[:,:,3]>=137;q[~m]=0;q[m,3]=255
  Image.fromarray(q).save(out,optimize=True)
 return Image.open(out).convert('RGBA')


def decals(d,decode,pack):
 src={k:acquire(k) for k in S};out={};fittings=[]
 for r in d['rooms']:
  parts=PLACEMENTS.get(r['n'],[])
  if not parts:continue
  b=decode(r['base']);f=decode(r['front']);q=d['lianes'][r['id']];yy,xx=np.indices(b.shape[:2]);h,w=yy.shape
  vines=np.maximum(decode(q['s'])[...,3],decode(q['t'])[...,3])
  # Attach only to wooden wall pixels, never to glass, architecture rims, or paths.
  rgb=np.where(f[...,3:]>0,f[:,:,:3],b[:,:,:3]).astype(int);red,green,blue=rgb.transpose(2,0,1)
  wall=(red>=103)&(red-green>=23)&(green-blue>=18)&(vines<90)&((b[:,:,:3]!=[104,72,47]).any(2)|(f[...,3]>0))
  for x,y,j,k in [g['rect'] for g in r['gates']]+r['mark']:wall[max(0,y-3):y+k+3,max(0,x-3):x+j+3]=False
  lay=Image.new('RGBA',(w,h))
  for key,cx,cy,aw,ah,slope,bend in parts:
   dx=xx-cx;u=np.rint((dx/(aw-1)+.5)*(src[key].width-1)).astype(int);v=np.rint(((yy-cy-slope*dx-bend*dx**2)/(ah-1)+.5)*(src[key].height-1)).astype(int)
   pick=(u>=0)&(u<src[key].width)&(v>=0)&(v<src[key].height)
   a=np.zeros((*yy.shape,4),np.uint8);tex=np.asarray(src[key]);a[pick]=tex[v[pick],u[pick]];active=a[...,3]>0
   fraction=float(wall[active].mean());a[~wall]=0
   # Reject a doubtful siting instead of hanging a cropped sprite on a post or window.
   if fraction<.955:
    print('Ornement écarté',r['label'],key,(cx,cy),round(fraction,3),flush=True);continue
   a[active&wall,:3]=np.rint(a[active&wall,:3].astype(float)*[.92,.91,.90]).astype(np.uint8)
   contact=np.roll(np.roll(a[...,3],1,axis=0),1 if slope>=0 else -1,axis=1)>0
   ss=np.zeros_like(a);ss[contact&wall]=[37,23,13,59];lay.alpha_composite(Image.fromarray(ss));lay.alpha_composite(Image.fromarray(a))
   fittings.append(dict(salle=r['id'],modele=key,centre=[cx,cy],pente=slope,courbure=bend,part_sur_bois=round(fraction,3)))
  crop=lay.getbbox()
  if crop:out[r['id']]=[crop[0],crop[1],pack(lay.crop(crop))]
 json_data=dict(models=[dict(type=k,fichier=S[k][2],sha256=hashlib.sha256((O/S[k][2]).read_bytes()).hexdigest(),provenance='générateur d’images') for k in S],poses=fittings,option='facultatif, non lumineux, pas de préplacement exporté')
 (O/'Index-ornements.json').write_text(json.dumps(json_data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 assert len(out)>=4 and len({s['modele'] for s in fittings})==2, (list(out),fittings)
 return out
