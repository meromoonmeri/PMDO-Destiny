#!/usr/bin/env python3
"""Fit the four generated sprites to 15 native plans; make a separate Night light pass."""
import base64,hashlib,json,sys
from io import BytesIO
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as nd
from scipy.interpolate import PchipInterpolator
from Trajets import ROUTES,H,V,R,A

S=Path(__file__).resolve().parent; O=S.parent; G=O.parent; W=Path.home()/'.cache/guilde-objets'
ORIGINAL=G/'Guilde-Destiny-Toutes-les-Salles.html'; BRUN=np.array([104,72,47])
LUMA=np.array([.2126,.7152,.0722]); FLEUR=np.array([255,235,169]); HALO=np.array([248,189,108]);

def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()
def decode(s):return np.array(Image.open(BytesIO(base64.b64decode(s.rsplit(',',1)[-1]))).convert('RGBA'))
def rgba(a):return Image.fromarray(a).convert('RGBA')
def pack(a):
 bio=BytesIO();rgba(a).save(bio,'WEBP',lossless=True,method=5,exact=True);res='data:image/webp;base64,'+base64.b64encode(bio.getvalue()).decode('ascii');assert np.array_equal(decode(res),a);return res

def describe_sprite(name):
 tex=np.array(Image.open(O/'Modeles-generes'/f'{name}.png').convert('RGBA'));rr,gg,bb,alpha=tex.astype(np.int16).transpose(2,0,1)
 assert not ((rr>gg+14)&(bb>gg+6)&(2*bb>rr)&(alpha>0)).any(), name
 light=(alpha==255)&(rr>155)&(gg>130)&(bb>82)&(2*bb>gg)&(rr+30>=gg)&(rr-gg<103)
 labels,m=nd.label(light,np.ones((3,3)));sizes=np.bincount(labels.ravel());labels[sizes[labels]<2]=0
 assert 3<=len(np.unique(labels))-1<=10
 return tex,labels

def warp(tex,labels,route,xx,yy):
 kind,_,depth,flip,nodes=route;nodes=np.array(nodes);vertical=kind==V
 along,across=(yy,xx) if vertical else (xx,yy);q=1 if vertical else 0
 start,end=nodes[:,q][[0,-1]];sx,sy=tex.shape[1],tex.shape[0];length=sx if not vertical else sy;thick=sy if not vertical else sx
 mid=PchipInterpolator(nodes[:,q],nodes[:,1-q],extrapolate=False)(np.clip(along,start,end))
 u=np.rint((along-start)*(length-1)/(end-start)).astype(int)
 v=np.rint((across-mid)*(thick-1)/(depth-1)+(thick-1)*.5).astype(int)
 valid=(u>=0)&(u<length)&(v>=0)&(v<thick)
 if flip:
  if vertical:v=thick-1-v
  else:u=length-1-u
 x,y=(v,u) if vertical else (u,v);q=np.zeros((*xx.shape,4),np.uint8);q[valid]=tex[y[valid],x[valid]]
 seed=np.zeros(xx.shape,np.int16);seed[valid]=labels[y[valid],x[valid]];return q,seed

def image_layers(r,d,p):
 a=d['nuits'][r['nuit']] if p==3 else d['lumieres'][r['nuit']][p];base=decode(r['base']);front=decode(r['front']);lut=np.array(a['lut'],dtype=np.uint8)
 for t in (base,front):
  for c in range(3):t[:,:,c]=lut[c,t[:,:,c]]
 for x,y,b in r['patches'][p]:
  bit=decode(b);h,w=bit.shape[:2];base[y:y+h,x:x+w]=bit
 return base,front,lut

def ellipse(x,y,xx,yy,sx,sy):return np.exp(-.5*(((xx-x)/sx)**2+((yy-y)/sy)**2))

def mask_rects(shape,rects,pad=0):
 m=np.zeros(shape,dtype=bool);h,w=shape
 for x,y,a,b in rects:m[max(0,y-pad):min(h,y+b+pad),max(0,x-pad):min(w,x+a+pad)]=True
 return m

def make_room(r,d,modules):
 ident=r['id'];key=ident.removeprefix('guilde_destiny_');name=r['label'];w,h=r['w'],r['h'];yy,xx=np.indices((h,w));shape=yy.shape
 base=decode(r['base']);fore=decode(r['front']);support=((base[:,:,:3]!=BRUN).any(2)&(base[:,:,3]>0))|(fore[:,:,3]>0)
 floor=np.repeat(np.repeat(np.array([list(t) for t in r['floor']])=='1',8,axis=0),8,axis=1)[:h,:w];assert floor.shape==shape
 near_floor,indices=nd.distance_transform_edt(~floor,return_indices=True)
 gates=mask_rects(shape,[g['rect'] for g in r['gates']]);arrival=mask_rects(shape,r['mark']);reserved=mask_rects(shape,[g['rect'] for g in r['gates']]+r['mark'],6)
 rim=r['south']['bottom'] if r['south'] else h
 glass=np.zeros(shape,dtype=bool);tone=d['nuits'][r['nuit']]['verre']
 for x,y,p in r['patches'][3]:
  patch=decode(p);hh,ww=patch.shape[:2];glass[y:y+hh,x:x+ww]=(patch[:,:,:3]==tone).all(2)&(patch[:,:,3]==255)
 location=support&~reserved&~nd.binary_dilation(glass,iterations=2)&(yy<rim)
 lightfield=np.zeros(shape,dtype=float);foliage=Image.new('RGBA',(w,h));flowers=np.zeros((h,w,4),np.uint8);buds=[];segments=[]
 for route in ROUTES[key]:
  kind,title,_,_,_=route
  q,seed=warp(*modules[kind],route,xx,yy);raw=q[:,:,3]>0
  mask=raw&location;n=int(raw.sum());hidden=int((raw&~location).sum());assert n>0
  q[~mask]=0;seed[~mask]=0;assert mask.sum()>=max(72,n*.49),(name,title,int(mask.sum()),n)
  # Small warm-vs-cool variation by material, independently of the room's time-of-day LUT.
  material={'L01-Corniche':(1.02,.96,.91),'L02-Poutre':(.93,.93,.86),'L03-Rive':(.88,.91,.83),'L04-Arche':(1.00,.97,.91)}[kind]
  q[mask,:3]=np.clip(np.rint(q[mask,:3]*material),0,255).astype(np.uint8)
  foliage.alpha_composite(rgba(q));seg=[]
  for label in sorted(np.unique(seed[seed>0])):
   m=seed==label;ys,xs=np.where(m);x=float(xs.mean());y=float(ys.mean());ix=int(round(x));iy=int(round(y));noyau=len(ys)
   if not noyau:continue
   flowers[m,:3]=np.rint(.27*q[m,:3]+.73*FLEUR).astype(np.uint8);flowers[m,3]=np.maximum(211,flowers[m,3]);
   item=dict(x=round(x,1),y=round(y,1),module=kind,plage=title);seg.append(item);buds.append(item)
   # Warm light actually changes non-sprite pixels. Each bud throws a tight and a broad lobe.
   gain=(1.11 if r['nuit']=='sud' else 1.0)*(1.04 if r['n'] in (2,3,6) else 1.)
   gain*=.70 if kind==R else (.82 if kind==A else 1.)
   gain*=min(1.,.70+.08*noyau)
   lightfield+=gain*(.275*ellipse(x,y,xx,yy,15,17)+.104*ellipse(x,y+6,xx,yy,37,35))
  # Diffuse reflected pool on the boards. Its centre is on the floor nearest the branch.
  if seg:
   x=np.mean([p['x'] for p in seg]);y=np.mean([p['y'] for p in seg]);ix=int(round(x));iy=int(round(y));fy,fx=indices[:,iy,ix];gap=near_floor[iy,ix];
   centre_x=w*.5;centre_y=float(np.median(np.where(floor)[0]));fx=.92*fx+.08*centre_x;fy=.76*fy+.24*centre_y
   lightfield+=(.23 if kind!=A else .19)*min(len(seg)/4,1.35)*np.exp(-gap/145)*ellipse(fx,fy,xx,yy,43,29)*floor
  segments.append(dict(section=title,module=kind,largeur=route[2],miroir=bool(route[3]),reperes=route[4],pixels=int(mask.sum()),masques=int(hidden),bourgeons=len(seg)))
 plant=np.array(foliage);actual=plant[:,:,3]>0
 # 1× contact shadow, never extruded into the map background, window glass or a threshold.
 shadow=np.zeros((h,w,4),np.uint8);soft=np.zeros(shape);soft[2:,1:]=actual[:-2,:-1];soft=nd.gaussian_filter(soft,sigma=1.2)
 shadow[location,:3]=(41,29,19);shadow[:,:,3]=(np.rint(soft*120)*location).astype(np.uint8);shadow[shadow[:,:,3]==0]=0
 day=rgba(shadow);day.alpha_composite(foliage);day=np.array(day);decor=day[:,:,3]>0
 mat=(base[:,:,:3].astype(float)@LUMA)/255
 envelope=(support|(fore[:,:,3]>0)) &~glass &(yy<rim)
 # Tone smooths over threshold margins instead of outlining them with a bright rectangle.
 falloff=np.minimum(nd.distance_transform_edt(~gates)/12,1)*np.minimum(nd.distance_transform_edt(~glass)/4,1)
 falloff*=np.minimum(np.maximum(rim-yy,0)/8,1) if r['south'] and r['south']['band'] else 1
 # Fine 3/255 steps retain the painted pixel texture beneath the warm screen blend.
 alpha=3*np.rint(np.minimum(.67,1-np.exp(-lightfield))*(.63+.37*np.sqrt(mat))*255/3)
 alpha=np.clip(3*np.rint(alpha*falloff/3),0,180).astype(np.uint8);alpha[~envelope]=0
 glow=np.zeros((h,w,4),np.uint8);glow[alpha>0,:3]=HALO;glow[:,:,3]=alpha
 assert len(segments)>=5 and len(buds)>=14,(name,len(buds));assert not (decor&(gates|arrival|~support|glass|(yy>=rim))).any()
 assert not (alpha[~envelope]>0).any() and not alpha[gates].any();assert np.all((flowers[:,:,3]>0)<=actual)
 # Quantify the change in illumination on bare boards, not on the foliage.
 base_n,front_n,nightlut=image_layers(r,d,3);bg=rgba(base_n);bg.alpha_composite(rgba(front_n));rgb=np.asarray(bg)[:,:,:3].astype(float)
 delta=(255-rgb)*(HALO/255.)*(alpha[:,:,None]/255.);light=(delta@LUMA>=7)&~decor&~glass
 result=int(light.sum());fl=int((light&floor).sum());assert result>2400 and fl>1000,(name,result,fl)
 report=dict(salle=ident,nom=name,taille=[w,h],segments=segments,bourgeons=buds,pixels_lianes=int(decor.sum()),pixels_eclaires_hors_lianes=result,pixels_plancher_eclaires=fl,passages_libres=len(r['gates']),bord_sud_inchange=True,vitrage_inchange=True)
 return day,glow,flowers,report

def compose(r,d,p,day,glow,flowers,active):
 base,fore,lut=image_layers(r,d,p);out=rgba(base);out.alpha_composite(rgba(fore))
 if active:
  q=day.copy()
  for c in range(3):q[:,:,c]=lut[c,q[:,:,c]]
  out.alpha_composite(rgba(q))
 if active and p==3:
  q=np.array(out);rgb=q[:,:,:3].astype(float);factor=glow[:,:,:3]/255.*(glow[:,:,3:] /255.)
  q[:,:,:3]=np.rint(rgb+(255-rgb)*factor).astype(np.uint8);out=rgba(q);out.alpha_composite(rgba(flowers))
 return out

def main():
 raw=ORIGINAL.read_text(encoding='utf-8');d=json.loads(raw.split('<script id="donnees" type="application/json">',1)[1].split('</script>',1)[0]);
 modules={n:describe_sprite(n) for n in (H,V,R,A)};report=[];sets={};montages={}
 assert len(d['rooms'])==len(ROUTES)==15
 P=O/'Lianes-par-salle'; P.mkdir(exist_ok=True)
 for r in d['rooms']:
  day,glow,flowers,row=make_room(r,d,modules);ident=r['id'];loc=P/(f'{r["n"]:02}-'+ident.removeprefix('guilde_destiny_'));loc.mkdir(exist_ok=True)
  for name,a in [('Lianes',day),('Lumiere-Nuit-Ecran',glow),('Bourgeons-Nuit',flowers)]:rgba(a).save(loc/(name+'.png'),optimize=True)
  below=day.copy();above=day.copy();foreground=decode(r['front'])[:,:,3]>0;below[foreground]=0;above[~foreground]=0
  sets[ident]=dict(s=pack(below),t=pack(above),l=pack(glow),b=pack(flowers),n=len(row['bourgeons']))
  report.append(row); print(f'{r["n"]:02} {r["label"]}: {len(row["bourgeons"])} bourgeons, {row["pixels_plancher_eclaires"]} pixels du plancher éclairés',flush=True)
  for k,p,active in [('jour',0,True),('nuit',3,True),('sans',3,False)]:
   montages.setdefault(k,[]).append((compose(r,d,p,day,glow,flowers,active),r['label']))
 for k,frames in montages.items():
  for j in range(3):
   out=Image.new('RGB',(276*5,228),'#2c2119');draw=ImageDraw.Draw(out)
   for i,(image,label) in enumerate(frames[j*5:j*5+5]):
    image.thumbnail((272,201),Image.Resampling.LANCZOS);x=i*276+(276-image.width)//2;y=23+(201-image.height)//2
    out.paste(image,(x,y));draw.text((8+i*276,5),label,fill='#f9d7a7')
   out.save(W/f'{k}-controle-{j+1}.jpg',quality=92)
 for n in (1,3,6,8,11,15):
  canv=Image.new('RGB',(montages['jour'][n-1][0].width*3+6,montages['jour'][n-1][0].height+20),'#402e22');draw=ImageDraw.Draw(canv)
  for j,(k,title) in enumerate([('jour','JOUR · LIANES'),('sans','NUIT · SANS LIANES'),('nuit','NUIT · LIANES ET LUMIÈRES')]):
   im=montages[k][n-1][0];x=j*(im.width+3);canv.paste(im,(x,20));draw.text((x+9,3),title,fill='#f9d7a7')
  canv.save(W/f'match-{n:02}.png')
 (O/'Lianes-par-salle'/'Index-lianes.json').write_text(json.dumps(dict(statut='PASS',version='0.7.7',original_sha256=sha(ORIGINAL),luminosite_min_RVB=(HALO.tolist()),seuil_luminance=7,plans=report,jeu_modifie=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (W/'Calques.json').write_text(json.dumps(sets,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 assert sum(s['passages_libres'] for s in report)==29
 print('PASS · 15 plans, 29 passages, 7 cadrages et chaque vitrage protégés ; éclairage chaud visible sur les planchers.',flush=True)

if __name__=='__main__':main()
