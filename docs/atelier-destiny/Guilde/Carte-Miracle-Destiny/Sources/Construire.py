#!/usr/bin/env python3
"""Compose generated inks on the approved background and bake continuous travel paths."""
from pathlib import Path
from hashlib import sha256
from math import hypot, sqrt
from heapq import heappush, heappop
from PIL import Image
from scipy import ndimage as nd
from scipy.optimize import linear_sum_assignment
import json, shutil
import numpy as np
from Archipels import place as placer_archipels

D=Path(__file__).resolve().parents[1];G=D/'Generations';C=D/'Calques';C.mkdir(exist_ok=True);V=D.parent;home=Path.home()
FN=V/'Fond-Nu-EoS'; EO=V/'Carte-Miracle-EoS'; NT=V/'Atlas-Destiny-Nouvelles-Terres'; AP=home/'Destiny-World-Map-EoS-Generee.png'
N=Image.Resampling.NEAREST; W,H=1112,732; step=4; gw,gh=W//step,H//step
S3=np.ones((3,3),np.uint8)

def js(p):return json.loads(p.read_text())
def save(im,p):im.save(p,optimize=True)
def png(a,p):save(Image.fromarray(a),p)
def hashp(p):return sha256(p.read_bytes()).hexdigest()
def writej(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def box(m):y,x=np.where(m);return tuple(int(n) for n in (x.min(),y.min(),x.max()+1,y.max()+1))
def rgb(p):return np.array(Image.open(p).convert('RGB').resize((W,H),N))
def chroma(a):
 r,g,b=np.moveaxis(a.astype('int16'),-1,0); return (r>136)&(b>130)&(g<.67*np.minimum(r,b))&(np.abs(r-b)<114)
def azure(a):
 r,g,b=np.moveaxis(a.astype('int16'),-1,0); return (g-r>28)&(b-r>28)&(b>=g-12)&(b>98)

aa=hashp(AP); base=rgb(AP); gen=rgb(G/'Destiny-Terrain-enrichi.png'); land=~chroma(base); new=~chroma(gen)
labels,num=nd.label(land,structure=S3); assert num==26
# Direct pixel composition, not re-illustration: retain the approved silhouettes and water
# and admit only generated art that fits inland. This discards an extra offshore piece of the edit.
dist=nd.distance_transform_edt(land);inner=dist>2.0
warm=labels==19
r,g,b=np.moveaxis(gen.astype(np.int16),-1,0)
new_pond=warm&(g-r>26)&(b-r>15)&~nd.binary_dilation(azure(base),iterations=4)
keep_water=nd.binary_dilation((azure(base)|azure(gen))&land,iterations=2)|nd.binary_dilation(new_pond,iterations=6)
take=land&new&inner&~keep_water
terrain=base.copy(); terrain[take]=gen[take]
# Remove only pink matte contamination left in the resampled generated edge. The alpha and
# original approved shoreline remain unchanged; all colors come from source image pixels.
r,g,b=np.moveaxis(terrain.astype(np.int16),-1,0)
spill=land&(dist<=3.05)&(r-g>22)&(b-g>1)
near=nd.distance_transform_edt(~(land&~spill),return_indices=True,return_distances=False)
terrain[spill]=terrain[near[0][spill],near[1][spill]]
rgba=np.dstack((terrain,land.astype('uint8')*255)); rgba[~land]=0
# Land art and overlays are generated images. No contours, mountains or wave marks are drawn here.
save(Image.fromarray(rgba),C/'01-Terres.png')
shutil.copyfile(FN/'Fond-nu-EoS-556x366.png',C/'00-Parchemin.png')
assert hashp(C/'00-Parchemin.png')=='67e1bf2020a11b1d0dcdb4ea9400eb4cd75e2ada19b48f80c8420f5ea798c1d3'

def glyph(n,name,sz,center,inside=None):
 a=np.array(Image.open(G/n).convert('RGB'));m=~chroma(a);l,t,r,b=box(m)
 rr,gg,bb=np.moveaxis(a.astype(np.int16),-1,0);spill=m&(rr-gg>22)&(bb-gg>2)
 if spill.any():
  ii=nd.distance_transform_edt(~(m&~spill),return_indices=True,return_distances=False);a[spill]=a[ii[0][spill],ii[1][spill]]
 z=np.dstack((a,m.astype('uint8')*255));z[~m]=0
 im=Image.fromarray(z).crop((l,t,r,b));s=float(sz)/im.width; im=im.resize((sz,max(1,round(im.height*s))),N)
 x,y=center[0]-im.width//2,center[1]-im.height//2
 if inside is not None:
  dx=im.width;dy=im.height;out=np.array(im); m2=np.asarray(im.getchannel('A'))>0
  loc=inside[y:y+dy,x:x+dx];assert (loc&m2).sum()>.98*m2.sum(),(n,(loc&m2).sum(),m2.sum());out[~loc]=0;im=Image.fromarray(out)
 dest=C/name;save(im,dest);return {'file':dest.name,'x':int(x),'y':int(y),'w':im.width,'h':im.height,'cx':int(center[0]),'cy':int(center[1])}

gly={
 'fosse':glyph('Fosse-Cascade.png','02-Fosse-Cascade.png',30,(216,491),labels==18),
 'spirale':glyph('Spirale-du-Jusant.png','03-Spirale-du-Jusant.png',54,(604,323)),
 'houle':glyph('Mer-Houleuse.png','04-Mer-Houleuse.png',77,(315,444))}
for k in ['spirale','houle']:
 q=gly[k]; mx=12; margin=land[q['y']-mx:q['y']+q['h']+mx,q['x']-mx:q['x']+q['w']+mx];assert not margin.any(),k
full=Image.open(C/'00-Parchemin.png').convert('RGBA').resize((W,H),N);full.alpha_composite(Image.fromarray(rgba));
for q in gly.values():full.alpha_composite(Image.open(C/q['file']).convert('RGBA'),(q['x'],q['y']))
before=np.array(full)
arch,all_labels,avoid,arch_meta=placer_archipels(labels,gly,G,C)
full.alpha_composite(arch)
arch_area=all_labels>=101
assert np.array_equal(before[~arch_area],np.asarray(full)[~arch_area])
assert nd.label(all_labels>0,structure=S3)[1]==num+sum(len(x['components']) for x in arch_meta)
save(full.convert('RGB'),D/'Carte-Complete-Destiny.png')

# Register the previous atlas's proposed landmark coordinates to the selected generation, by
# matching each island's bounding box. Independently illustrated entrances use their image positions.
oldidx=np.array(Image.open(NT/'Terres-EoS-Magenta/Sources/Index-terres-validees.png')); old,n=nd.label(oldidx>0,structure=S3);assert n==num
ob=[box(old==i) for i in range(1,n+1)]; nb=[box(labels==i) for i in range(1,num+1)]
def unit(b,m):x,y,u,v=m;return (np.array(b)-[x,y,x,y])/np.array([u-x,v-y,u-x,v-y])
O=np.array([unit(b,box(old>0)) for b in ob]);P=np.array([unit(b,box(land)) for b in nb]); pp,qq=linear_sum_assignment(((O[:,None]-P[None,:])**2).sum(axis=2)); onto={int(i+1):int(j+1) for i,j in zip(pp,qq)}
regs={'reve':'Réverie','orival':'Orival','seracine':'Séracine','estrel':'Estrel','torselune':'Torselune','haltes':'Les Haltes','mer':'Les Traversées','volcans':'Archipel volcanique','coraux':'Atoll des Coraux','amethystes':'Île des Améthystes','petales':'Bois des Pétales'}
Geo=js(NT/'Sources/Geographie.json'); inf={}; sites={}
for ri,r in enumerate(Geo['regions'],1):
 for ident,name,kind,x,y,detail,*ex in r['sites']:
  oi=int(old[y,x]); mask=oldidx==ri
  if oi==0 or not mask[y,x]:
   yd,xd=np.nonzero(mask);best=int(np.argmin((xd-x)**2+(yd-y)**2));x,y=int(xd[best]),int(yd[best]);oi=int(old[y,x])
  u,v,X,Y=ob[oi-1];l,t,L,T=nb[onto[oi]-1]
  gx=int(round(l+(x-u)/(X-u)*(L-l)));gy=int(round(t+(y-v)/(Y-v)*(T-t)));sites[ident]={'id':ident,'name':name,'area':r['id'],'kind':kind,'lore':bool(ex and ex[0]),'text':detail,'loc':[gx,gy],'island':onto[oi]}

def choose(ident,name,area,kind,at,text,island):
 sites[ident]={'id':ident,'name':name,'area':area,'kind':kind,'loc':list(at),'text':text,'island':island,'lore':False}
choose('grotte-ramures','Grotte des Ramures','orival','grotte',(200,347),'Une arche de pierre s’ouvre au pied des reliefs d’Orival, au bord des bois.',4)
choose('grotte-givre','Grotte du Givre','seracine','grotte',(599,140),'Sous les crêtes gelées de Séracine, la pierre bleuit au-dessus de l’entrée.',1)
choose('grotte-ocre','Grotte d’Ocre','torselune','grotte',(333,548),'Une entrée sombre et basse s’abrite dans le grès, près de la première vasque.',19)
choose('houle','Mer Houleuse','mer','mer',(315,444),'Des crêtes d’écume se lèvent au large de Réverie. L’équipe franchit la houle en bateau.',0)
choose('spirale','Spirale du Jusant','mer','mer',(604,323),'Le courant tourne à l’est des Haltes. L’étape se fait en lisière du tourbillon.',0)
sites['reverie']['loc']=[144,539];sites['fosse']['loc']=[214,503];sites['passage']['loc']=[219,544]
arch_by={z['id']:z for z in arch_meta}

def append_island_site(id,name,area,category,compass,approach,text,eos=None):
 z=arch_by[area]
 def locate(x,y):return [round(z['x']+x*z['w']),round(z['y']+y*z['h'])]
 choose(id,name,area,'archipel',locate(*compass),text,z['main'])
 x,y=sites[id]['loc'];assert all_labels[y,x]==z['main'],(id,x,y)
 sites[id]['arrival_hint']=locate(*approach);sites[id]['category']=category;sites[id]['new']=True
 if eos:sites[id]['origine']='eos';sites[id]['source_eos']=eos

def donjon_url(s):return 'https://www.pokepedia.fr/'+s
append_island_site('volcan-geant','Volcan Géant','volcans','Volcan',(.61,.64),(.69,.33),
 'Un cône de basalte s’élève au-dessus des coulées rouges. Le donjon d’EoS est redessiné et placé dans les eaux de Destiny.',donjon_url('Volcan_G%C3%A9ant'))
append_island_site('cratere-obscur','Cratère Obscur','volcans','Cratère',(.33,.24),(.047,.43),
 'Au nord du massif, une caldeira sombre perce les cendres. Le repère d’EoS est adapté à cette carte.',donjon_url('Crat%C3%A8re_Obscur'))
append_island_site('atoll-coraux','Atoll des Coraux','coraux','Récif',(.18,.41),(.33,.12),
 'Le lagon turquoise est ceint de sable et de petits bancs de corail. Le sentier suit la rive, jamais le fond du lagon.')
append_island_site('grotte-amethystes','Grotte des Améthystes','amethystes','Cristaux',(.54,.46),(.40,.16),
 'Des pointes mauves signalent une petite grotte au pied des collines. On débarque côté roche et on gagne l’entrée à pied.')
append_island_site('bois-petales','Bois des Pétales','petales','Bosquet',(.37,.46),(.71,.53),
 'Une arche de pierre dort entre les houppiers roses et les arbres verts. Le bois s’étend derrière deux basses terrasses.')
order=['reverie','fosse','guilde','passage','bois','source','houle','spirale','grotte-ocre','vrille','balise-nacre','signal-voiles','abri-jusant','grotte-ramures','miroir','grotte-givre','deux-mers','bourg-ecume','cotes-metano','salines','volcan-geant','cratere-obscur','atoll-coraux','grotte-amethystes','bois-petales']
sites={k:sites[k] for k in order}
for k,s in sites.items():
 s.setdefault('category','Mer' if s['area']=='mer' else 'Grotte' if s['kind']=='grotte' or k in ('fosse','passage') else 'Vigie' if s['area']=='haltes' or k=='deux-mers' else 'Site')
 s['region']=regs[s['area']]
# Canvas coordinates at grid centres. Land cost steers routes away from drawn waterways; if a
# valley polygon only crosses a very thin river, that line is a proposed ford, not a sea leg.
xg=step//2+step*np.arange(gw); yg=step//2+step*np.arange(gh)
lgr=all_labels[np.ix_(yg,xg)];wet=azure(base)[np.ix_(yg,xg)];block=avoid[np.ix_(yg,xg)];sea=lgr==0
def dry(isl):return (lgr==isl)&~block
# Avoid seas outside the parchment design border.
sea[:6]=False;sea[-5:]=False;sea[:,:5]=False;sea[:,-4:]=False
Dsea=nd.distance_transform_edt(sea); coast_pen=.65*np.clip(1-Dsea/7,0,1)

def xy(pt):x,y=pt;return [int(xg[x]),int(yg[y])]
def nearest(mask,at,extra=None):
 y,x=np.nonzero(mask); a=(xg[x]-at[0])**2+(yg[y]-at[1])**2
 if extra is not None:a=a+extra[y,x]
 q=int(np.argmin(a));return int(x[q]),int(y[q])

Yg,Xg=np.meshgrid(yg,xg,indexing='ij')
# Keep the (32×38 px) standing team clear of the coloured centres of the fixed markers at the new stops.
# The arrival is a nearby place to stand, not the landmark icon itself.
readable=Yg>=42
for site in sites.values():
 px,py=site['loc']
 readable&=~((Xg-22<=px+6)&(Xg+23>=px-6)&(Yg-37<=py+6)&(Yg+8>=py-6))
for p in sites.values():
 allow=dry(p['island']) if p['island'] else sea
 # Explorers land on the rim of the spiral and at the lee side of the waves, not in their core.
 hint={'spirale':(627,340),'houle':(313,453),'fosse':(194,514)}.get(p['id'],p.get('arrival_hint',p['loc']))
 if p.get('new'):allow=allow&readable
 p['node']=list(nearest(allow,hint,wet*75 if p['island'] else None));p['point']=xy(p['node'])

haz=np.zeros((gh,gw),bool);Y,X=np.meshgrid(yg,xg,indexing='ij')
haz|=(X-gly['spirale']['cx'])**2+(Y-gly['spirale']['cy'])**2<18**2
sea&=~haz
world={k:{'node':v['node'],'island':v['island']} for k,v in sites.items()}
# Site-to-site sections are never straight cross-water shortcuts: travel to a real coast cell,
# board an adjacent exterior route cell, continue by sea, and disembark on the next coast.
sides={18:(223,529),4:(399,348),1:(749,221),13:(684,539),19:(332,503),9:(472,271),14:(505,348),16:(568,421)}
sides.update({z['main']:z['port_souhaite'] for z in arch_meta})
ports={}
for isl,at in sides.items():
 p=[]
 for gy,gx in zip(*np.nonzero(dry(isl))):
  for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
   bx,by=int(gx)+dx,int(gy)+dy
   if 0<=bx<gw and 0<=by<gh and sea[by,bx]:
    x,y=xy((gx,gy));p.append(((x-at[0])**2+(y-at[1])**2+float(wet[gy,gx])*180,(int(gx),int(gy)),(bx,by)))
 assert p,isl
 _,lp,sp=min(p);a,b='port-'+str(isl),'nav-'+str(isl);ports[isl]=(a,b)
 world[a]={'node':list(lp),'island':isl};world[b]={'node':list(sp),'island':0}

for z in arch_meta:
 a,b=ports[z['main']];z['port']={'terre':xy(world[a]['node']),'mer':xy(world[b]['node'])}

moves=((1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,sqrt(2)),(-1,1,sqrt(2)),(1,-1,sqrt(2)),(-1,-1,sqrt(2)))

def continuous(mask):
 # A sea/land cell is sampled at its centre. Also check pixels BETWEEN centres to keep
 # the actual interpolated movement off rocks, land and lagoon/lava edges.
 inter=np.ones((len(moves),gh,gw),dtype=bool)
 for i,(dx,dy,_) in enumerate(moves):
  for t in range(1,step):
   inter[i]&=mask[np.ix_(np.clip(yg+dy*t,0,H-1),np.clip(xg+dx*t,0,W-1))]
 return inter

def shortest(allowed, penalty, start, end, between=None):
 start=tuple(start);end=tuple(end)
 if start==end:return [start]
 sx,sy=start;ex,ey=end; spanW=allowed.shape[1]
 assert allowed[sy,sx] and allowed[ey,ex]
 idx0=sy*spanW+sx;idx1=ey*spanW+ex
 best=np.full(allowed.size,np.inf);back=np.full(allowed.size,-1,np.int32);best[idx0]=0
 hq=[(hypot(ex-sx,ey-sy),0.,idx0)]
 while hq:
  f,g,u=heappop(hq)
  if g>best[u]+1e-8:continue
  if u==idx1:break
  y,x=divmod(u,spanW)
  for i,(dx,dy,c) in enumerate(moves):
   if between is not None and not between[i,y,x]:continue
   X=x+dx;Y=y+dy
   if not (0<=X<allowed.shape[1] and 0<=Y<allowed.shape[0] and allowed[Y,X]):continue
   if dx and dy and not(allowed[Y,x] and allowed[y,X]):continue
   v=Y*spanW+X;ng=g+c*(1+float(penalty[Y,X]));
   if ng+1e-8<best[v]:
    best[v]=ng;back[v]=u;heappush(hq,(ng+hypot(ex-X,ey-Y),ng,v))
 assert idx0==idx1 or back[idx1]>=0,(start,end,'route inaccessible')
 s=[];u=idx1
 while u!=idx0:
  Y,X=divmod(u,spanW);s.append((X,Y));u=int(back[u])
 s.append(start);return s[::-1]

def compact(points):
 if len(points)<3:return [xy(v) for v in points]
 def diff(p,q):return(q[0]-p[0],q[1]-p[1])
 return [xy(points[0])]+[xy(points[i]) for i in range(1,len(points)-1) if diff(points[i-1],points[i])!=diff(points[i],points[i+1])]+[xy(points[-1])]

edges=[];pairs=0; crossings=0
fy,fx=np.ogrid[:H,:W]
sail=(all_labels==0)&((fx-gly['spirale']['cx'])**2+(fy-gly['spirale']['cy'])**2>=18**2)
for isl in [*sides,0]:
 ids=[k for k,v in world.items() if v['island']==isl];allowed=sea if isl==0 else dry(isl)
 fine=sail if not isl else ((all_labels==isl)&~avoid if isl>=101 else None)
 between=continuous(fine) if fine is not None else None
 penalty=coast_pen if not isl else 3.65*wet+.30*np.clip(1-nd.distance_transform_edt(allowed)/4,0,1)
 for i,k in enumerate(ids):
  for j in ids[i+1:]:
   points=shortest(allowed,penalty,world[k]['node'],world[j]['node'],between); assert all(allowed[y,x] for x,y in points)
   if not isl: assert not any(lgr[y,x] for x,y in points)
   else: crossings+=sum(int(wet[y,x]) for x,y in points)
   pp=compact(points);lng=sum(hypot(y[1]-x[1],y[0]-x[0]) for x,y in zip(pp,pp[1:]));edges.append({'a':k,'b':j,'mode':'mer' if not isl else 'terre','p':pp,'distance':round(lng,4)});pairs+=1
for k,j in ports.values():
 p=[xy(world[k]['node']),xy(world[j]['node'])];edges.append({'a':k,'b':j,'mode':'port','p':p,'distance':float(step)})

reachable={'reverie'}
while True:
 previous=len(reachable)
 for e in edges:
  if e['a'] in reachable or e['b'] in reachable:reachable.update((e['a'],e['b']))
 if len(reachable)==previous:break
assert set(sites)<=reachable

anim=js(EO/'Calques/Animation.json');art={}
glyph('Barque.png','05-Barque.png',40,(0,0))
for name,f in [('fond','00-Parchemin.png'),('terrain','01-Terres.png'),('fosse','02-Fosse-Cascade.png'),('spirale','03-Spirale-du-Jusant.png'),('houle','04-Mer-Houleuse.png'),('barque','05-Barque.png'),('archipels','06-Archipels.png')]:art[name]=f
for key,k in [('yellow','Repère-jaune.png'),('red','Repère-rouge.png'),('blue','Repère-bleu.png'),('dim','Repère-jaune-atténué.png'),('arrowA','Flèche-01.png'),('arrowB','Flèche-02.png')]:
 name='Repere-'+key+'.png';shutil.copyfile(EO/'Calques'/'Repères'/k,C/name);art[key]=name
for id in [0,1,13,15,16]:
 name=f'Nuage-{id:02}.png';shutil.copyfile(FN/'Calques'/'Sprites-mobiles'/f'Pose-{id:02}.png',C/name);art[f'cloud{id}']=name
poses={}
for k,v in anim['pikachu']['poses'].items():
 name=f'Marche-{int(k):02}.png';shutil.copyfile(EO/v['fichier'],C/name);art[f'p{k}']=name;poses[k]={'size':v['taille'],'offset':v['coin_relatif']}
shutil.copyfile(EO/'Calques/Audio/Jingle-ME-06.mp3',C/'Signal-Decouverte.mp3')
writej(D/'Atlas.json',{'version':1,'width':W,'height':H,'sites':list(sites.values()),'regions':regs,'glyphs':gly,'archipels':arch_meta,'edges':edges,'art':art,'poses':poses,'walk':anim['pikachu']['sequences'],'audio':'Signal-Decouverte.mp3','circuits':{'rive':['fosse','passage'],'marees':['houle','balise-nacre','spirale','grotte-ocre'],'archipels':['volcan-geant','cratere-obscur','bois-petales','atoll-coraux','grotte-amethystes']}})
assert hashp(AP)==aa
assert np.array_equal(np.asarray(Image.open(C/'01-Terres.png'))[...,3]>0,land)
writej(D/'Verification-geographie.json',{'statut':'PASS','routes_evitent_lagon_lave_et_source':True,'trajets_maritimes_et_nouvelles_marches_controles_au_pixel':True,'masque_terrain_identique_a_la_decoupe_de_la_generation_approuvee':True,'source_approuvee_sha256':aa,
 'fond_sha256':hashp(C/'00-Parchemin.png'),'silhouettes_base':int(num),
 'composantes_ajoutees':sum(len(z['components']) for z in arch_meta),'archipels':arch_meta,'sans_repeindre_la_carte_existante':True,
 'donjons_originaires_d_eos':sum(p.get('origine')=='eos' for p in sites.values()),'concordance_brut_avec_edit':round(float((land&new).sum()/(land|new).sum()),6),
 'art_image_generee':['terrain enrichi','cascade et grotte de Réverie','spirale','houle','barque'],'sites_simules':len(sites),'huit_noms_connus':sum(bool(s['lore']) for s in sites.values()),
 'troncons_dans_masque_de_transport':pairs,'raccords_port':len(ports),'echelle_grille':step,'franchissements_de_rivieres_valides_pour_la_simulation':crossings})
print('PASS:',num,'côtes d’origine exactes,',len(arch_meta),'nouveaux archipels,',len(sites),'sites,',pairs,'tronçons,',len(ports),'raccords en bateau.')
