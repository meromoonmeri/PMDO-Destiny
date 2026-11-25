#!/usr/bin/env python3
"""Generated ivy on native posts; localized emissive and cast-shadow passes for the 15-room atlas."""
from pathlib import Path
from io import BytesIO
import hashlib,json,sys,importlib.util,shutil
import numpy as np
from scipy import ndimage as nd
from PIL import Image,ImageDraw

S=Path(__file__).resolve().parent;O=S.parent;G=O.parent;H=Path.home();W=H/'.cache/guilde-animee';ROOT=G/'Objets-PMU-100/Sources'
BASE=G/'Guilde-Destiny-Drapeaux-et-Lianes.html';STORE=O/'Calques-nuit';P=O/'Lianes-de-poteaux'
sys.path.insert(0,str(ROOT));_spec=importlib.util.spec_from_file_location('atelier_calques',ROOT/'Construire-lianes.py');old=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(old)
from Trajets import ROUTES,H as CORNICHE,V,R,A
from math import pi
LUMA=np.array([.2126,.7152,.0722]); HALO=np.array([251,194,114]); OMBRE=(61,51,65); IVORY=np.array([255,232,168]);
CADENCES=[(11300,1.23),(15300,.38),(12900,4.70),(17200,3.13)]; OMBRE_PERIODE=18100

# Additional posts, checked against the native room elevations. Each list is selective;
# bare passage pillars remain untouched. A mirrored turn follows the opposite face of the timber.
EXTRA_P={
 'accueil':[(22,1,[(86,106),(85,125),(87,152),(90,174)]),(22,0,[(430,108),(429,131),(430,153),(428,175)])],
 'missions':[(23,1,[(145,87),(144,111),(147,139),(146,157)]),(25,0,[(526,113),(527,141),(522,170),(522,210)])],
 'grand_salon':[(27,0,[(154,81),(153,106),(155,134),(155,153)]),(28,1,[(420,80),(420,102),(422,128),(420,151)])],
 'bureau_maitre':[(25,1,[(51,112),(51,138),(47,161),(48,185)])],
 'refectoire':[(24,1,[(145,89),(148,109),(149,134),(148,155)]),(25,0,[(425,81),(428,106),(428,131),(427,151)])],
 'cuisine':[(22,0,[(355,63),(355,81),(357,102),(357,120)])],
 'reserve':[(22,0,[(328,80),(326,104),(330,127),(330,149)])],
 'dortoir_nord_1':[(21,0,[(120,78),(119,99),(120,126),(118,148)])],
 'dortoir_nord_2':[(21,0,[(326,78),(327,98),(325,125),(326,149)])],
 'dortoir_sud_1':[(21,1,[(328,82),(326,102),(329,129),(328,149)])],
 'dortoir_sud_2':[(21,1,[(116,81),(116,106),(119,130),(120,148)])],
 'chambre_heros':[(23,1,[(337,65),(337,82),(339,107),(340,127)])],
}
# One elaborate crown or a pair on the largest room axes; bedrooms use the more open motif.
NOBLE={1:{1,2},2:{1,2},3:{3,4},4:{1},6:{2},7:{1},15:{2}}

def data_base():return json.loads(BASE.read_text(encoding='utf8').split('<script id="donnees" type="application/json">',1)[1].split('</script>',1)[0])
def json_file(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def bytes_sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(a):r,g,b=a.astype(np.int16).transpose(2,0,1);return (r>24)&(r>g+14)&(b>g+6)&(2*b>r)
def clipbox(img):
 y,x=np.where(img[:,:,3]>0);assert len(y);x0,y0,x1,y1=int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1);return x0,y0,img[y0:y1,x0:x1]
def collect_flower(a,noble):
 r,g,b,alpha=a.astype(np.int16).transpose(2,0,1);m=(alpha>0)&(r>(172 if noble else 164))&(g>(125 if noble else 138))&(b>(47 if noble else 75))&(r>=g+11)&(g>=b+10)
 if not noble:m&=(b*2>=g-16)
 lab,_=nd.label(m,np.ones((3,3)));c=np.bincount(lab.ravel());c[0]=0;good=np.where((c>=2)&(c<=max(14,a.shape[1]*2)))[0];lab[~np.isin(lab,good)]=0
 assert 3<=len(good)<=16,(noble,len(good));return lab

def wrap_module(file,size,noble):
 f=W/'bruts'/file;a=np.array(Image.open(f).convert('RGB'));m=~key(a)
 if noble:
  # Isolate the airy crowned helix: the other drafts hide more of the wood shaft.
  m[:,269:]=False
 lab,_=nd.label(m,np.ones((3,3)));num=np.bincount(lab.ravel());num[0]=0;srcmask=(num[lab]>=(95 if noble else 850));assert srcmask.sum()>70000
 a4=np.zeros((*m.shape,4),np.uint8);a4[srcmask,:3]=a[srcmask];a4[srcmask,3]=255;_,_,a4=clipbox(a4)
 a4=np.array(Image.fromarray(a4).resize(size,Image.Resampling.BOX));mask=(a4[:,:,3]>=112)&~key(a4[:,:,:3]);a4[~mask]=0;a4[mask,3]=255
 _,_,a4=clipbox(a4);lab=collect_flower(a4,noble);Image.fromarray(a4).save(P/file,optimize=True)
 return a4,lab,dict(nom=file,dimensions=list(a4.shape[:2][::-1]),sha256_generation=bytes_sha(f),coupe='spire couronnée isolée' if noble else 'liane complète',bourgeons=int(len(np.unique(lab))-1))

def refs():
 source=[]
 for name,dim,premium in [('Enroulement-de-Reverie.png',(30,90),False),('Enroulement-de-ceremonie.png',(31,93),True)]:
  a,b,n=wrap_module(name,dim,premium);source.append(n)
  if premium:ceremony=(a,b)
  else:reverie=(a,b)
 return reverie,ceremony,source

def grow_routes(r):
 key=r['id'].removeprefix('guilde_destiny_');out=[];v=0
 for what,title,width,mirror,knots in ROUTES[key]:
  if what==V:
   v+=1;out.append(((what,title,round(width*1.40),mirror,knots),v in NOBLE.get(r['n'],set())))
  else:out.append(((what,title,width,mirror,knots),False))
 for i,(width,flip,points) in enumerate(EXTRA_P.get(key,[]),1):
  v+=1;out.append(((V,'Enroulement du poteau '+str(v),width,flip,points),v in NOBLE.get(r['n'],set())))
 return out,v

def freeze_support(r,d):
 b=old.decode(r['base']);f=old.decode(r['front']);h,w=b.shape[:2];y,x=np.indices((h,w));support=((b[:,:,:3]!=old.BRUN).any(2)&(b[:,:,3]>0))|(f[:,:,3]>0)
 floor=np.repeat(np.repeat(np.array([list(s) for s in r['floor']])=='1',8,0),8,1)[:h,:w];assert floor.shape==support.shape
 glass=np.zeros_like(support);tone=d['nuits'][r['nuit']]['verre']
 for a,c,bit in r['patches'][3]:
  q=old.decode(bit);hh,ww=q.shape[:2];glass[c:c+hh,a:a+ww]=(q[:,:,:3]==tone).all(2)&(q[:,:,3]==255)
 gates=old.mask_rects(support.shape,[g['rect'] for g in r['gates']]);no_plant=old.mask_rects(support.shape,[g['rect'] for g in r['gates']]+r['mark'],5)
 bottom=r['south']['bottom'] if r['south'] else h
 silhouette=support&~glass&(y<bottom)&~gates
 post=support&~no_plant&~nd.binary_dilation(glass,iterations=1)&(y<bottom)
 penumbra=np.minimum(nd.distance_transform_edt(~gates)/12,1)*np.minimum(nd.distance_transform_edt(~glass)/4,1)*silhouette
 if r['south'] and r['south']['band']:penumbra*=np.minimum(np.maximum((bottom-y)/10,0),1)
 return b,f,x,y,floor,glass,gates,bottom,post,penumbra

def low_shade(point_nodes,visible,leaves,fold,floor,dist,idx,angles,where,shadows):
 """Use the generated leaf silhouette to cast softer shapes against wall and converging floor planes."""
 h,w=floor.shape;nodes=np.asarray(point_nodes);y0,y1=nodes[0,1],nodes[-1,1];cx=int(nodes[-1,0]);leaf=leaves&visible; ys,xs=np.where(leaf)
 if len(ys)<12: return
 u=np.clip((ys-y0)/max(6,y1-y0),0,1)
 lo=idx[:,int(y1),cx];fdy,fdx=map(int,lo);gap=float(dist[int(y1),cx]);
 for i,sign in enumerate(angles):
  wally=np.clip(ys+np.rint(4.0+3*u).astype(int),0,h-1);wallx=np.clip(xs+np.rint(sign*(6.0+4*u)).astype(int),0,w-1)
  ink=np.zeros_like(shadows[i]);np.maximum.at(ink,(wally,wallx),(.25 if fold else .28)*(.8+.2*u))
  # The shadow falls into the near boards, flattened by the top-down perspective.
  floor_x=np.clip(np.rint(fdx+.70*(xs-cx)+sign*(4+18*(1-u))).astype(int),0,w-1);floor_y=np.clip(np.rint(fdy+8+32*(1-u)).astype(int),0,h-1)
  cast=np.zeros_like(ink);np.maximum.at(cast,(floor_y,floor_x),.44*(1-.49*(1-u))*np.exp(-gap/60))
  shadows[i]=np.maximum(shadows[i],(.87*nd.gaussian_filter(ink,1.25)+1.15*nd.gaussian_filter(cast,1.65)*floor)*where)

def rgba(alpha,tone):
 out=np.zeros((*alpha.shape,4),np.uint8);q=alpha>0;out[q,:3]=tone;out[:,:,3]=alpha;return out

def lights_pack(a):x,y,c=clipbox(a);return [x,y,old.pack(c)]

def visual(b,h,k,scene,glows,emit,shadow,stamp,x,y,m):
 bg=Image.fromarray(b);bg.alpha_composite(Image.fromarray(h));image=np.array(bg,dtype=float)
 def lay(a,alpha,mode):
  nonlocal image
  rgba=a.astype(float);weight=rgba[:,:,3:]/255*alpha
  if mode=='screen':image[:,:,:3]+=(255-image[:,:,:3])*(rgba[:,:,:3]/255)*weight
  if mode=='multiply':image[:,:,:3]*=1-weight*(1-rgba[:,:,:3]/255)
  if mode=='normal':image[:,:,:3]=image[:,:,:3]*(1-weight)+rgba[:,:,:3]*weight
 for i,(time,ph) in enumerate(CADENCES):
  omega=2*pi*stamp/time;v=.84+.103*np.sin(omega+ph+.103*m)+.039*np.sin(.61*omega-.8*ph+.013*m)
  lay(glows[i],v,'screen')
 if k is not None:
  f=.50+.42*np.sin(2*pi*stamp/OMBRE_PERIODE+.12*m)
  lay(shadow[0],.90*(1-f),'multiply');lay(shadow[1],.90*f,'multiply')
 if scene is not None:
  for i,(time,ph) in enumerate(CADENCES):
   v=.83+.110*np.sin(2*pi*stamp/time+ph+.103*m)+.038*np.cos(2*pi*stamp/(time*1.6)+ph+.049*m)
   lay(emit[i],v,'normal')
 return np.rint(image).astype(np.uint8)

def make(r,d,oldart,thin,noble):
 b,f,x,y,floor,glass,gates,bottom,location,lightmask=freeze_support(r,d);hh,ww=y.shape;night_r=np.maximum(.0,(b[:,:,:3].astype(float)@LUMA)/255)
 near,idx=nd.distance_transform_edt(~floor,return_indices=True);routes,n_post=grow_routes(r);assert n_post>=2
 fields=[np.zeros(y.shape,np.float32) for _ in range(4)];cores=[np.zeros((*y.shape,4),np.uint8) for _ in fields]
 shade=np.zeros_like(fields[0]);shadows=[np.zeros_like(shade),np.zeros_like(shade)];count=[0,0,0,0];parts=[];flora=Image.new('RGBA',(ww,hh));floor_median=float(np.median(y[floor]));total_post=[]
 for ri,(route,ceremonial) in enumerate(routes):
  kind,desc,width,flip,knots=route;pic,seed=old.warp(*(noble if ceremonial else thin if kind==V else oldart[kind]),route,x,y)
  raw=pic[:,:,3]>0;mask=raw&location;assert mask.sum()>=max(55,raw.sum()*.43),(r['label'],desc,int(mask.sum()),int(raw.sum()))
  pic[~mask]=0;seed[~mask]=0
  # Depth relief: the tips curl away and darken while diagonal foliage crosses the brighter shaft.
  if kind==V:
   p=np.asarray(knots);axis=np.interp(y,p[:,1],p[:,0]);distance=np.clip(abs(x-axis)/(width*.65),0,1)
   project=np.clip(.97-.40*distance**2+.037*np.sin(y/10.),.60,1.0)
   pic[mask,:3]=np.rint(pic[mask,:3]*project[mask,None]*np.array([.97,1.,.91])).astype(np.uint8)
   pxarea=(abs(x-axis)<=min(9,width*.31))& (y>=p[0,1])&(y<=p[-1,1])&location
   ratio=(mask&pxarea).sum()/max(1,pxarea.sum());assert ratio<.75,(r['label'],desc,ratio)
   total_post.append(dict(nom=desc,cadre=knots,branche='cérémonie' if ceremonial else 'Reverie',largeur_px=width,bois_visible_part=round(1-ratio,3)))
   pcol=pic[:,:,:3].astype(np.int16);leaf=(pcol[:,:,1]>=pcol[:,:,0]*.80)&(pcol[:,:,1]>pcol[:,:,2]+18)
   low_shade(knots,mask,leaf,ceremonial,floor,near,idx,(-1,1),lightmask,shadows)
  else:
   tint=np.array([1.00,.96,.91]) if kind!=R else np.array([.89,.93,.85]);pic[mask,:3]=np.clip(np.rint(pic[mask,:3]*tint),0,255).astype(np.uint8)
  flora.alpha_composite(Image.fromarray(pic));cast=np.zeros_like(shade);cast[2:,1:]=mask[:-2,:-1];shade=np.maximum(shade,nd.gaussian_filter(cast,sigma=1.12)*.53)
  xx0=float(np.mean(np.asarray(knots)[:,0]));g=int(xx0>=ww/2)+(2 if kind==R else 0)
  lights=[]
  for label in np.unique(seed[seed>0]):
   m=seed==label;ry,rx=np.where(m);n=len(rx);ux,uy=float(rx.mean()),float(ry.mean());lights.append((ux,uy));count[g]+=1
   q=cores[g];q[m,:3]=np.rint(.33*pic[m,:3]+.67*IVORY).astype(np.uint8);q[m,3]=233 if kind==V else 218
   gain=1.07 if kind==V else .77 if kind==R else .90
   if ceremonial:gain*=.91
   fields[g]+=gain*min(.76+n*.075,1.)*(.207*old.ellipse(ux,uy,x,y,14,16)+.061*old.ellipse(ux,uy+7,x,y,30,27))
  if lights:
   ux,uy=np.mean(lights,axis=0);ix,iy=int(round(ux)),int(round(uy));fy,fx=idx[:,iy,ix];gap=near[iy,ix];fx=.95*fx+.05*ww/2;fy=.82*fy+.18*floor_median
   fields[g]+=(.137 if kind!=R else .107)*min(len(lights)/4,1.21)*np.exp(-gap/137.)*old.ellipse(fx,fy,x,y,37,27)*floor
  parts.append(dict(nom=desc,lueurs=len(lights),zone=g,genre=kind))
 assert min(count)>=2,(r['label'],count)
 canopy=np.array(flora);plant=canopy[:,:,3]>0;contact=np.rint(255*shade*location).astype(np.uint8);spread=Image.fromarray(rgba(contact,(29,20,12)));spread.alpha_composite(flora);vine=np.array(spread);fp=f[:,:,3]>0;s=vine.copy();s[fp]=0;t=vine.copy();t[~fp]=0
 weights=(.65+.35*np.sqrt(night_r))*lightmask
 glows=[rgba(np.clip(2*np.rint(.5*255*np.minimum(.54,(1-np.exp(-.95*fl))*weights)),0,144).astype(np.uint8),HALO) for fl in fields]
 casts=[rgba(np.clip(np.rint(255*np.minimum(.41,1.20*a)*lightmask),0,255).astype(np.uint8),OMBRE) for a in shadows]
 # Geometry checks apply to every frame because all animated effects are opacity-only within these masks.
 guard=gates|glass|(y>=bottom);assert not any(a[guard,3].any() for a in [s,t,*glows,*casts,*cores]);assert all(cores[i][...,3].max()>0 and glows[i][...,3].max()>0 for i in range(4))
 b_n,f_n,lut=old.image_layers(r,d,3);no=Image.fromarray(b_n);no.alpha_composite(Image.fromarray(f_n));bare=np.asarray(no)
 on=Image.fromarray(b_n);s_n=s.copy();t_n=t.copy()
 for ch in range(3):s_n[:,:,ch]=lut[ch,s_n[:,:,ch]];t_n[:,:,ch]=lut[ch,t_n[:,:,ch]]
 on.alpha_composite(Image.fromarray(s_n));on.alpha_composite(Image.fromarray(f_n));on.alpha_composite(Image.fromarray(t_n));wood=np.array(on);empty=np.zeros_like(wood)
 a0=visual(wood,empty,1,1,glows,cores,casts,0,x,y,r['n']);a1=visual(wood,empty,1,1,glows,cores,casts,5800,x,y,r['n']);lightonly=visual(wood,empty,None,1,glows,cores,casts,0,x,y,r['n'])
 bare_floor=floor&~(vine[:,:,3]>0);carbon=((a1[:,:,:3].astype(float)-a0[:,:,:3])@LUMA);strength=((a0[:,:,:3].astype(float)-bare[:,:,:3])@LUMA);casted=((lightonly[:,:,:3].astype(float)-a0[:,:,:3])@LUMA)
 assert np.array_equal(a0[guard],bare[guard]) and np.array_equal(a1[guard],bare[guard]);floorflare=int(((strength>=5)&bare_floor).sum());flooranimated=int(((np.abs(carbon)>=1.8)&bare_floor).sum());shadowed=int(((casted>=2.5)&~plant).sum());assert floorflare>1400 and flooranimated>300 and shadowed>25,(r['label'],floorflare,flooranimated,shadowed)
 stages=STORE/(f'{r["n"]:02}-'+r['id'].removeprefix('guilde_destiny_'));stages.mkdir(parents=True,exist_ok=True)
 Image.fromarray(vine).save(stages/'Lianes-tous-poteaux.png',optimize=True)
 for i,(g,c) in enumerate(zip(glows,cores),1):
  Image.fromarray(g).save(stages/f'{i}-Halo-Ecran.png',optimize=True);Image.fromarray(c).save(stages/f'{i}-Bourgeons-Normal.png',optimize=True)
 for i,c in enumerate(casts,1):Image.fromarray(c).save(stages/f'Ombre-{i}-Produit.png',optimize=True)
 b_d,f_d,lut_d=old.image_layers(r,d,0);day=Image.fromarray(b_d);day.alpha_composite(Image.fromarray(f_d));v=vine.copy()
 for ch in range(3):v[:,:,ch]=lut_d[ch,v[:,:,ch]]
 day.alpha_composite(Image.fromarray(v));meta=dict(s=old.pack(s),t=old.pack(t),n=sum(count),v=n_post,g=[dict(l=lights_pack(g),b=lights_pack(c)) for g,c in zip(glows,cores)],o=[lights_pack(o) for o in casts]);row=dict(n=r['n'],salle=r['id'],nom=r['label'],dimensions=[ww,hh],poteaux=n_post,bourgeons_par_zone=count,sections=parts,poteaux_enroules=total_post,px_plancher_eclaires=floorflare,px_plancher_animes=flooranimated,px_ombre_projetee=shadowed,seuils_et_vitres_intacts=True)
 a0=Image.fromarray(a0);a1=Image.fromarray(a1)
 for name,im in [('jour',day),('nuit',a0),('nuit-5800',a1)]:im.save(W/f'{name}-{r["n"]:02}.png')
 return meta,row

def main():
 W.mkdir(parents=True,exist_ok=True);P.mkdir(parents=True,exist_ok=True);d=data_base();thin,noble,origin=refs();art={k:old.describe_sprite(k) for k in (CORNICHE,R,A)}
 report=[];datas={}
 for r in d['rooms']:
  a,row=make(r,d,art,thin,noble);report.append(row);datas[r['id']]=a;print(f'{r["n"]:02} · {r["label"]}: {row["poteaux"]} enroulements, {a["n"]} bourgeons, {row["px_plancher_animes"]} pixels de plancher qui varient, {row["px_ombre_projetee"]} pixels ombrés',flush=True)
 assert len(datas)==15
 (W/'LianesAnimees.json').write_text(json.dumps(datas,separators=(',',':')),encoding='utf8');json_file(P/'Index-poteaux.json',dict(source='générateur d’image, references Reverie Normal Home / Inn et poteaux natifs Destiny',motifs=origin))
 styles=dict(statut='PASS',atlas_de_reference_sha256=bytes_sha(BASE),rooms=report,nb_salles=15,nb_poteaux=sum(r['poteaux'] for r in report),nb_bourgeons=sum(sum(r['bourgeons_par_zone']) for r in report),zones_par_salle=4,parametres=dict(cadences_ms=[[t,p]for t,p in CADENCES],ombre_periode_ms=OMBRE_PERIODE,phase_par_salle=.103),jeu_modifie=False)
 json_file(OUT:=O/'Index-nuit-et-poteaux.json',styles)
 for p in ('jour','nuit'):
  for j in range(3):
   im=Image.new('RGB',(270*5,220),'#2d2019');dr=ImageDraw.Draw(im)
   for i,r in enumerate(d['rooms'][j*5:j*5+5]):
    img=Image.open(W/f'{p}-{r["n"]:02}.png');img.thumbnail((266,198));im.paste(img,(i*270+(270-img.width)//2,20+(198-img.height)//2));dr.text((i*270+7,5),r['label'],fill='#ffe3b8')
   im.save(W/f'{p}-atlas-{j+1}.jpg',quality=93)
 print(f'PASS · 15 salles · {styles["nb_poteaux"]} poteaux · {styles["nb_bourgeons"]} bourgeons générant des halos et des ombres.',flush=True)
if __name__=='__main__':main()
