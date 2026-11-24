#!/usr/bin/env python3
"""Read the actual Grodoudou APNG, then relight Destiny from selected visible buds.

No Grodoudou prop or geometry is transferred. The generated light matte is
projected at low opacity onto the nearby wood, preserving local occlusion.
"""
from pathlib import Path
from io import BytesIO
import base64,hashlib,importlib.util,json,re
import numpy as np
from PIL import Image
from scipy import ndimage as nd

import Lueur

S=Path(__file__).resolve().parent; O=S.parent; G=O.parent; W=Path.home()/'.cache/lumiere-braseros'; P=G/'Animations-Destiny'; STOCK=G/'Guilde-Destiny-Nuit-Vivante.html'
_REF=G.parent/'Reference-Guildhouse/Project-Pokemon/Guilde-de-Grodoudou.html'; MARK='<script id="donnees" type="application/json">'; APREF='https://projectpokemon.org/home/gallery/image/77578-g01p05cpng/'
loader=importlib.util.spec_from_file_location('relief',P/'Sources/Enrouler-et-eclairer.py'); fx=importlib.util.module_from_spec(loader);loader.loader.exec_module(fx)
old=fx.old; LUMA=fx.LUMA
# Low or mid-low buds on the posts on either side of the room, not a string of overhead spotlights.
ANCHORS={1:(0,1),2:(2,1),3:(2,3),4:(0,1),5:(0,1),6:(2,3),7:(0,2),8:(0,1),9:(0,1),10:(1,0),11:(2,1),12:(0,1),13:(0,1),14:(1,0),15:(0,2)}

def jd(path,o):path.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def data():return json.loads(STOCK.read_text(encoding='utf-8').split(MARK,1)[1].split('</script>',1)[0])
def sha(b):return hashlib.sha256(b).hexdigest()

def lire_braseros():
 h=_REF.read_text(encoding='utf-8'); raw=base64.b64decode(json.loads(re.search(r'<script type="application/json" id="loops">(.*?)</script>',h,re.S)[1])['77578'].rsplit(',',1)[1]);im=Image.open(BytesIO(raw));frames=[];durations=[]
 for i in range(im.n_frames):
  im.seek(i);frame=np.array(im.convert('RGBA'));frames.append(frame);durations.append(im.info['duration'])
 values=np.array(frames);change=np.any(values!=values[0],axis=(0,3));labels,n=nd.label(change,np.ones((3,3)));rect=[]
 for k in range(1,n+1):
  y,x=np.where(labels==k);rect.append(dict(rectangle=[int(x.min()),int(y.min()),int(x.max()-x.min()+1),int(y.max()-y.min()+1)],pixels=int(len(x))))
 assert durations==[100]*4 and [q['rectangle'] for q in rect]==[[128,154,32,38],[248,154,32,38]] and int(change.sum())==1718
 # Read the bright and dark stills, and check the same grass colour at different distances from the two fires.
 pics={}
 for fig in re.findall(r'<figure\b[^>]*>.*?</figure>',h,re.S):
  m=re.search(r'<figcaption><b>(G01P05[AC])\.png</b>',fig);p=re.search(r'<img src="data:image/[^;]+;base64,([^"]+)',fig)
  if not m or not p:continue
  q=np.asarray(Image.open(BytesIO(base64.b64decode(p[1]))).convert('RGB'))
  if q.shape!=(384,408,3):continue
  if m[1] not in pics:pics[m[1]]=q
 light,dark=pics['G01P05A'],pics['G01P05C'];notice=[]
 for label,(x,y,w,hh) in [('près du brasero ouest',(130,204,28,36)),('près du brasero est',(268,205,23,42)),('loin des deux braseros',(129,250,30,39))]:
  a=light[y:y+hh,x:x+w];b=dark[y:y+hh,x:x+w];m=(a==[183,199,23]).all(2);assert m.sum()>100;z=(b[m]==[159,175,0]).all(1);notice.append(dict(zone=label,jour=[183,199,23],nuit=[159,175,0],echantillons=int(m.sum()),identiques=int(z.sum())))
 (W/'Grodoudou-original.apng').write_bytes(raw)
 return dict(fiche=APREF,image='G01P05C',sha256_apng=sha(raw),dimensions=list(im.size),durees_ms=durations,pixels_changes=int(change.sum()),zones_animees=rect,bois_et_sol_hors_zones_fixes=True,gazon_compare=notice,interpretation='Contraste entre une base nocturne stable et deux foyers chauds bien lisibles ; pas de mouvement de lumière sur le sol dans cet APNG.')

def flowers(arrays):
 out=[];labs=[]
 for zones in arrays:
  lab,n=nd.label(zones[:,:,3]>0,np.ones((3,3)));labs.append(lab)
  for j in range(1,n+1):
   pixels=lab==j;ys,xs=np.where(pixels);x,y=float(xs.mean()),float(ys.mean());out.append((x,y,len(xs),len(labs)-1,j))
 return out,labs

def identify(r,geom,buds,vine,xx,yy):
 routes=geom['poteaux_enroules'];out=[];r0,g0,b0,alpha=vine.astype(np.int16).transpose(2,0,1)
 for target,ri in enumerate(ANCHORS[r['n']]):
  col=routes[ri];a=np.array(col['cadre']);lo,hi=a[:,1][[0,-1]];span=hi-lo;breadth=col['largeur_px'];want_y=lo+span*(.70 if target==0 else .77)
  pot=[]
  for bud in buds:
   x,y,n,kind,j=bud;dx=abs(x-np.interp(y,a[:,1],a[:,0]));if_inside=(lo+.50*span<=y<=lo+.92*span)&(dx<breadth*.55)
   if if_inside and kind<2 and n>=1:pot.append((bud, (y-want_y)**2+(dx*.8)**2-3*min(n,8)))
  if pot:
   bud=min(pot,key=lambda q:q[1])[0];out.append((bud,col,None));continue
  # The airy Reverie spiral has subdued tips near its foot. Pick a real warm node in that silhouette.
  axis=np.interp(yy,a[:,1],a[:,0]);belt=(abs(xx-axis)<breadth*.48)&(yy>lo+.52*span)&(yy<lo+.91*span)&(alpha==255)
  warm=belt&(r0>=g0-4)&(r0>=b0+19)&(g0>=b0+10)
  if warm.sum()<5:warm=belt&(r0>=48)&(g0>=b0+10)
  assert warm.sum()>=5,(r['label'],target,col['nom'])
  score=.72*r0+.28*g0+.22*np.maximum(r0-g0,0)-.17*(yy-want_y)**2-.055*(xx-axis)**2
  j=int(np.argmax(np.where(warm,score,-np.inf)));y,x=np.unravel_index(j,yy.shape)
  around=belt&((xx-x)**2+(yy-y)**2<=3.2)&((r0>=g0-12)|(yy==y))
  near=np.flatnonzero(around);near=near[np.argsort(((xx-x)**2+(yy-y)**2-.004*score).ravel()[near])[:5]];m=np.zeros_like(warm);m.ravel()[near]=True
  assert m.any();out.append(((float(x),float(y),int(m.sum()),-1,-1),col,m))
 assert out[0][0]!=out[1][0];return out

def screen(dst,layer,value):
 weight=layer[:,:,3:].astype(float)/255*value
 return dst+(255-dst)*(layer[:,:,:3].astype(float)/255)*weight

def paint_towards(r,d,geom,v,matte):
 b,f,x,y,floor,glass,gates,bottom,vegetal,support=fx.freeze_support(r,d);room=r['id'];postset=P/'Calques-nuit'/(f'{r["n"]:02}-'+room.removeprefix('guilde_destiny_'))
 core=[np.array(Image.open(postset/f'{i}-Bourgeons-Normal.png').convert('RGBA')) for i in range(1,5)];vine=np.array(Image.open(postset/'Lianes-tous-poteaux.png').convert('RGBA'));buds,labs=flowers(core);lights=identify(r,geom,buds,vine,x,y);bud_mask=vine[:,:,3]>0;inside=bud_mask&(vine[:,:,1].astype(int)>=vine[:,:,0].astype(int)*.79)&(vine[:,:,1]>vine[:,:,2].astype(int)+17)
 faint=Image.new('RGBA',(r['w'],r['h']));lit=[];report=[];layers=[];index=nd.distance_transform_edt(~floor,return_distances=False,return_indices=True)
 guard=gates|glass|(y>=bottom);mat=.48+.52*np.sqrt((b[:,:,:3].astype(float)@LUMA)/255.)
 pick=[(bud[3],bud[4]) for bud,_,_ in lights if bud[3]>=0]
 for i,c in enumerate(core):
  q=c.copy()
  for u,j in pick:
   if i==u:q[labs[u]==j]=0
  # The remaining pinpoints read as buds, not as additional lamps that fill the room.
  q[:,:,3]=np.rint(q[:,:,3].astype(float)*Lueur.TIP_ALPHA).astype(np.uint8);q[q[:,:,3]==0]=0;faint.alpha_composite(Image.fromarray(q))
 soft_a=np.array(faint);soft_a[:,:,3]=np.minimum(soft_a[:,:,3],round(255*Lueur.TIP_ALPHA))
 night_b,night_f,lut=old.image_layers(r,d,3);base=Image.fromarray(night_b);base.alpha_composite(Image.fromarray(night_f));bare=np.array(base)
 vv=vine.copy()
 for u in range(3):vv[:,:,u]=lut[u,vv[:,:,u]]
 base.alpha_composite(Image.fromarray(vv));scene=np.array(base);current=scene[:,:,:3].astype(float)
 for i,((sx,sy,n,k,j),post,node) in enumerate(lights):
  si=np.asarray(post['cadre']);foot_x,foot_y=map(int,si[-1]);fx0,fy0=map(int,index[:,foot_y,foot_x][::-1]);fx0,fy0=float(fx0),float(fy0)
  hemi=1 if foot_x<r['w']/2 else -1
  small=(r['w']<=480 and r['n']!=15);shrink=.86 if small else 1.
  # The same generated painting is warped onto the lower foliage, then onto the floor.
  # Keep the strongest light close to its bud and turn the floor reflection towards the room.
  hotspot=.103*matte.project(x,y,sx,sy+1,24*shrink,30*shrink,hemi,.17)
  gap=max(0,fy0-sy);castx=fx0*.73+sx*.27+4.5*hemi;casty=fy0+5+.09*gap
  stem=.031*matte.project(x,y,sx*.64+castx*.36,(sy+casty)*.5,28*shrink,33*shrink,hemi,.25)
  pool=(.091 if not small else .084)*np.exp(-gap/140.)*matte.project(x,y,castx,casty,48*shrink,28*shrink,hemi,.20)*floor
  bound=np.clip((71-np.abs(x-sx))/12,0,1)*np.clip((83-np.abs(y-sy))/13,0,1)
  fluence=np.minimum(Lueur.REFLECTION_ALPHA/255,(hotspot+stem+pool)*support*mat*bound)
  # Project actual nearby leaf silhouettes away from this source; occlusion only removes its own contribution.
  sample=inside&(abs(x-sx)<post['largeur_px']*.65)&(abs(y-sy)<31)&(((x-sx)**2+(y-sy)**2)>12)
  ly,lx=np.where(sample);assert len(lx)>30,(r['label'],i)
  shadow=np.zeros_like(fluence);dr=np.sign(lx-sx);wx=np.rint(sx+1.28*(lx-sx)+2*(dr-hemi*.24)).astype(int);wy=np.rint(sy+1.17*(ly-sy)-1.8).astype(int)
  ok=(wx>=0)&(wx<r['w'])&(wy>=0)&(wy<r['h']);np.maximum.at(shadow,(wy[ok],wx[ok]),.54)
  wall=nd.gaussian_filter(shadow,1.23)*(~floor)*~bud_mask
  sample=(ly>=sy+3.0);lx,ly=lx[sample],ly[sample];splay=np.clip((gap+6)/(ly-sy+4),1.18,2.75);ax=np.clip(np.rint(castx+(lx-sx)*splay).astype(int),0,r['w']-1)
  ay=np.clip(np.rint(casty-7+(foot_y-ly)*.57+.10*abs(ax-fx0)).astype(int),0,r['h']-1)
  projection=np.zeros_like(fluence);np.maximum.at(projection,(ay,ax),.79)
  shadow_strength=np.clip(wall+nd.gaussian_filter(projection,1.38)*floor,0,.68)
  transmitted=fluence*(1-shadow_strength)
  la=np.rint(255*transmitted).clip(0,Lueur.REFLECTION_ALPHA).astype(np.uint8);la[la<2]=0
  grel=fx.rgba(la,Lueur.AMBER)
  em=np.zeros_like(vine);m=labs[k]==j if node is None else node;assert m.sum()==n and (m&bud_mask).any()
  # A warm tint, never an opaque replacement for a bud or its outline.
  bud_gain=(.71+.29*np.exp(-((x[m]-sx)**2+(y[m]-sy)**2)/3.8))
  em[m,:3]=Lueur.CORE;em[m,3]=np.rint(Lueur.CORE_ALPHA*bud_gain).astype(np.uint8)
  assert not grel[guard,3].any() and not em[guard,3].any()
  proof=((fluence-transmitted)>.0035)&floor&~bud_mask;assert proof.sum()>=9,(r['label'],i,int(proof.sum()))
  px=abs(sx-x);py=abs(sy-y);assert la[(px>71)|(py>83)].max(initial=0)==0
  packet=dict(l=fx.lights_pack(grel),b=fx.lights_pack(em),x=round(sx,2),y=round(sy,2),p=round(.48+r['n']*.319+i*2.45,5));lit.append(packet)
  value=Lueur.level(0,packet);current=screen(current,grel,value)
  report.append(dict(poteau=post['nom'],source=[round(sx,2),round(sy,2)],pied=[int(foot_x),int(foot_y)],reflet=[round(castx,2),round(casty,2)],periode_ms=Lueur.CYCLE['ms'],texels_bourgeon=n,plancher_ombre=int(proof.sum()),alpha_reflet_max_255=int(la.max()),alpha_coeur_max_255=int(em[:,:,3].max()),portee_max_px=int(np.ceil(np.sqrt((px[la>0]**2+py[la>0]**2).max())))))
  layers.append((grel,em))
 delta=(current-scene[:,:,:3].astype(float))@LUMA;bare_floor=floor&~bud_mask
 reflection=(delta>=1.5)&bare_floor;assert reflection.sum()>180,(r['label'],int(reflection.sum()))
 # No general veil: the unlit boards, passage bands and glass remain byte-for-byte intact.
 hit=(np.maximum(layers[0][0][:,:,3],layers[1][0][:,:,3])>0);distant=int((floor&~hit).sum());assert distant>=int(floor.sum())*.73,(r['label'],distant,int(floor.sum()))
 assert np.array_equal(np.rint(current[guard]).astype(np.uint8),bare[guard,:3]);assert not soft_a[guard,3].any()
 t=soft_a[:,:,3:].astype(float)/255;current=current*(1-t)+soft_a[:,:,:3]*t
 for (_,em),lamp in zip(layers,lit,strict=True):current=screen(current,em,Lueur.level(0,lamp))
 composite=scene.copy();composite[:,:,:3]=np.rint(current).astype(np.uint8)
 Image.fromarray(composite).save(W/f'Destiny-source-{r["n"]:02}.png',optimize=False)
 return dict(s=v['s'],t=v['t'],n=v['n'],v=v['v'],points=lit,reflets=fx.lights_pack(soft_a)),dict(salle=room,nom=r['label'],sources=report,plancher_lit=int(reflection.sum()),plancher_hors_halos=distant,plancher_total=int(floor.sum()),gain_luma_max_plancher=round(float(delta[bare_floor].max()),2),seuils_et_vitrage_intacts=True)

def main():
 W.mkdir(parents=True,exist_ok=True);r=lire_braseros();d=data();matte=Lueur.Matte();oldidx=json.loads((P/'Index-nuit-et-poteaux.json').read_bytes());report=[];payload={}
 for g,q in zip(oldidx['rooms'],d['rooms'],strict=True):
  assert g['salle']==q['id'];packet,article=paint_towards(q,d,g,d['lianes'][q['id']],matte);payload[q['id']]=packet;report.append(article);print(q['label'],':',article['plancher_lit'],'pixels de plancher éclairés ; hors portée',round(100*article['plancher_hors_halos']/article['plancher_total']),'%',flush=True)
 assert len(report)==15
 (W/'Ancrages.json').write_text(json.dumps(payload,separators=(',',':')),encoding='utf8');jd(O/'Releve-Grodoudou.json',r);jd(O/'Index-lumiere-ancree.json',dict(statut='PASS',source=r['image'],adaptation='Texture de lumière générée projetée à faible opacité au pied des lianes ; occlusion calculée dans le rayon de chaque source.',texture=matte.info,cadence=Lueur.CYCLE,plafond_alpha_reflet_255=Lueur.REFLECTION_ALPHA,plafond_alpha_coeur_255=Lueur.CORE_ALPHA,sha_atelier_precedent=sha(STOCK.read_bytes()),sources=30,plans=report))
 print('PASS · texture générée projetée sur 30 sources à faible opacité · 15 salles.',flush=True)
if __name__=='__main__':main()
