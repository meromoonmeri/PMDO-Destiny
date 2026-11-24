#!/usr/bin/env python3
"""Assemble the image-guided DS terrain, locking the approved geometry and export coordinates."""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from scipy.optimize import linear_sum_assignment
import json, numpy as np

D=Path(__file__).resolve().parents[1]; S=D/'Sources'; U=D.parent
M=U/'Terres-EoS-Magenta'/'Sources'; A=D/'Terres-separees'; C=D/'Calques'; A.mkdir(exist_ok=True);C.mkdir(exist_ok=True)
key=np.array([255,0,255],np.uint8); N=Image.Resampling.NEAREST; BOX=Image.Resampling.BOX
idx=np.asarray(Image.open(M/'Index-terres-validees.png')); H,W=idx.shape; land=idx>0
wet=np.asarray(Image.open(M/'Eaux-validees.png'))>0; water=np.asarray(Image.open(M/'Eaux-de-reference.png').convert('RGBA'))[...,:3]
assert not (wet&~land).any()
place=json.loads((M/'Placement-valide.json').read_text())
geography=(U/'Sources'/'Geographie.json').read_bytes()
shape3=np.ones((3,3),np.uint8)

def count(a):return int(np.count_nonzero(a))
def bounds(a):
 y,x=np.nonzero(a);return tuple(int(k) for k in [x.min(),y.min(),x.max()+1,y.max()+1])
def part(a,b):x,y,u,v=b;return a[y:v,x:u]
def save(a,p):
 p.parent.mkdir(exist_ok=True,parents=True); (a if isinstance(a,Image.Image) else Image.fromarray(a)).save(p,optimize=True)
def jsonout(obj,name): (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def resize(a,size,mode=N):return np.array(Image.fromarray(a).resize(size,mode))
def iou(a,b):return count(a&b)/count(a|b)
def is_pink(a):
 r,g,b=np.moveaxis(a.astype(np.int16),-1,0);return (r>140)&(b>130)&(g<.64*np.minimum(r,b))&(abs(r-b)<110)
def closest(mask): return nd.distance_transform_edt(~mask,return_distances=False,return_indices=True)
def quant5(s):
 q=((np.rint(np.clip(s,0,255)*31/255)).astype(np.uint8));return (q<<3)|(q>>2)

raw=Image.open(S/'Destiny-DS-genere.png').convert('RGB'); ra=np.array(raw)
SL,n=nd.label(~is_pink(ra),structure=shape3); TL,m=nd.label(land,structure=shape3)
tb=[bounds(TL==i) for i in range(1,m+1)];sb=[bounds(SL==i) for i in range(1,n+1)]
tg=bounds(land);sg=bounds(SL>0)
def norm(box,co):
 x,y,u,v=co;return (np.array(box)-[x,y,x,y])/np.array([u-x,v-y,u-x,v-y])
# Pair full regional boxes, not individual hues or landmark motifs. One little pair touched in the raw.
cost=(((np.stack([norm(c,tg) for c in tb])[:,None]-np.stack([norm(c,sg) for c in sb])[None,:])**2)*np.array([2,1,2,1])).sum(axis=2)
i,j=linear_sum_assignment(cost); paired={int(x+1):int(y+1) for x,y in zip(i,j)}
assert m==26 and n>=24, (m,n)
# Atlas has one 26th approved islet whose generated drawing contacts its neighbor. Give it a new
# bounded crop from the right side of that neighbor; untouched global coast will separate both.
replacement={}
for k in set(range(1,m+1))-paired.keys():
 u=tb[k-1]; src=paired[min(paired,key=lambda v:cost[k-1,paired[v]-1])]; bb=sb[src-1];x,y,r,b=bb
 ref=norm(u,tg); whole=norm(bb,sg)
 # If the merged pair covers the missing object's approximate x, use a narrow in-situ slice.
 if r-x>=45 and whole[0]-.015<=ref[0]<=whole[2]+.015:
  left=max(x,min(r-8,int(round(x+(r-x)*.70))));top=max(y,int(y+(b-y)*.03));end=min(b,int(y+(b-y)*.78));bb=(left,top,r,end)
 replacement[k]=(src,bb)


def mount(t, chosen, box):
 """Resample a generated piece without pulling magenta into its antialiased edges."""
 r=part(ra,box); omsk=part(SL==chosen,box)&~is_pink(r);assert omsk.any()
 near=closest(omsk); orig=r[near[0],near[1]]
 h,w=t.shape; col=resize(orig,(w,h)); mask=resize(omsk.astype(np.uint8),(w,h))>0
 # Only the contour pixels omitted by the generator use nearest neighboring terrain.
 # To avoid repeating the old sprite's coastline in the middle, sample its own adjacent interior.
 d=nd.distance_transform_edt(omsk); inmask=d>2 if count(d>2)>4 else omsk; nei=closest(inmask)
 core=r[nei[0],nei[1]]; inds=closest(mask)
 col[t&~mask]=resize(core,(w,h))[inds[0][t&~mask],inds[1][t&~mask]]
 return col, {'recouvrement_apres_cadrage_avant_ecretage':round(iou(t,mask),4),'pixel_generes_et_recadres':count(t&mask),'raccords_de_contour':count(t&~mask)}


def tree_town(col, t, wetlands):
 """Put a miniature generated tree landmark on dry ground at the approved anchor."""
 out=col.copy();h,w=t.shape; assert (w,h)==(176,176)
 # Remove the oversized, misplaced tree from the world pass. The boundary of its silhouette
 # is measured at the fourfold working view, not guessed from the blue threshold of the water.
 approx=[(81,228),(84,211),(99,191),(106,178),(118,166),(131,158),(143,154),(161,156),(176,165),(190,176),(194,186),(200,198),(207,215),(207,233),(200,248),(185,257),(170,265),(162,282),(162,300),(167,321),(175,334),(185,341),(174,352),(152,357),(133,354),(114,346),(120,329),(125,306),(120,275),(107,270),(94,259),(85,247)]
 piece=Image.new('L',(w,h)); ImageDraw.Draw(piece).polygon([(round(x/4),round(y/4)) for x,y in approx],fill=255)
 shell=nd.binary_dilation(np.asarray(piece)>0,iterations=3)&t&~wetlands
 # The close-up generation has a clean hatching patch and the small tree-entrance sprite. Use
 # those two pieces only; the rest of that experiment (including its coast and water) is discarded.
 detail=Image.open(S/'Reverie-DS-generee.png').convert('RGB')
 field=np.asarray(detail.crop((440,461,542,515)).resize((49,27),BOX)).astype(float)
 field=field-field.mean((0,1),keepdims=True)
 yy,xx=np.mgrid[:h,:w]; solid=col.astype(float); r,g,b=np.moveaxis(solid,-1,0)
 good=t&~wetlands&~shell&(r>153)&(r-g>11)&(r-g<67)&(g>b+27)
 band=nd.gaussian_filter(good.astype(float),8); wash=np.stack([nd.gaussian_filter(good*solid[...,i],8)/(band+1e-6) for i in range(3)],axis=-1)
 glow=np.array([196,166,75]); lev=np.clip((band-.10)*1.8,0,.60)[...,None]
 patch=(glow*(1-lev)+wash*lev)+.55*field[yy%field.shape[0],(xx+yy//17)%field.shape[1]]
 out[shell]=np.clip(patch[shell],0,255).astype(np.uint8)
 # Paint a second small group of semi-dry brush in the reclaimed clearing, clipped to its
 # actual art from the global generator so the hatch outlines don't look mechanically tiled.
 forest=np.asarray(detail.crop((267,445,326,504)).resize((19,20),BOX)); fr=forest.astype(int)
 q=(fr[...,1]>fr[...,0]-9)&(fr[...,1]>fr[...,2]+20)&(fr[...,0]<141)
 p=out[57:77,20:39]; p[q&shell[57:77,20:39]]=forest[q&shell[57:77,20:39]]
 # Manually isolate the hue-cluster belonging to the generated guild-tree emblem, rather than
 # moving the land around it. The traced polygon includes the dark arcade and the two little roofs.
 pxy=[(40,127),(63,126),(64,102),(87,102),(87,79),(109,78),(109,55),(174,55),(199,55),(198,30),(269,30),(269,54),(316,54),(337,54),(337,74),(408,74),(408,101),(428,102),(428,125),(453,126),(453,261),(431,261),(431,284),(390,284),(385,308),(345,309),(345,332),(368,332),(368,355),(389,355),(389,397),(369,397),(369,445),(349,445),(349,470),(315,470),(311,446),(178,446),(175,466),(129,465),(128,395),(107,395),(107,353),(130,353),(130,327),(146,327),(146,306),(105,306),(105,281),(64,281),(64,263),(41,263)]
 mark=Image.new('L',(129,129)); ImageDraw.Draw(mark).polygon([(round(x/4),round(y/4)) for x,y in pxy],fill=255)
 ext=mark.getbbox(); sprite=detail.crop((615,333,744,462)).crop(ext); cut=mark.crop(ext)
 tile=(28,30); rgb=np.asarray(sprite.resize(tile,N),dtype=np.float32)*.93+[18,13,6]; fg=np.asarray(cut.resize(tile,N))>0
 sy,sx=np.where(fg); ax,ay=80,100
 # On the world chart the elevated tree crown naturally projects slightly to the southwest.
 # Select the smallest left tilt keeping every generated root and leaf off the exact river mask.
 for tilt in range(3,19):
  ty=ay-(tile[1]-1)+sy;tx=ax-(tile[0]//2)+sx-np.rint(tilt*(1-sy/(tile[1]-1))).astype(int)
  if not (wetlands[ty,tx]|~t[ty,tx]).any():break
 else:raise AssertionError('Tree must not cover the river')
 out[ty,tx]=np.rint(np.clip(rgb[sy,sx],0,255)).astype(np.uint8)
 return out, {'Reverie_Town':{'ancre_racines_atlas':[150,551], 'dessin':'arbre-village de la génération rapprochée, détouré et placé hors du cours d’eau', 'dimensions_du_sprite_px':list(tile)}}


def fix_waters(col,t,exact,old,k):
 """Replace the river/lake footprint, preserving the image generator's tones and glints when possible."""
 if not exact.any():return col,{}
 a=col.copy();r,g,b=np.moveaxis(col.astype(np.int16),-1,0)
 # On Séracine, pale stone is cool too; the saturated blue-green pools are separated from stone.
 sat=42 if k==2 else 20; base=t&(g-r>=sat)&(b-r>=sat+4)&(b>=g-8)
 closed=nd.binary_closing(base,structure=shape3,iterations=2)|base
 Q,nq=nd.label(closed&t,structure=shape3); full=np.bincount(Q.ravel());over=np.bincount(Q[exact].ravel(),minlength=full.size)
 good=np.fromiter((i for i in range(1,nq+1) if over[i]>=min(20,max(4,full[i]*.10))),int)
 gen=np.isin(Q,good)
 # Clear all shifted water (and its ink fringe) at the old painted location. Adjacent ground
 # comes from the artwork itself, sampled just beyond that fringe, not from an EoS tile.
 shape=nd.binary_fill_holes(gen)&t
 fringe=nd.binary_dilation(shape,iterations=2)&t
 remove=~exact&fringe
 outside=~exact&~fringe&t
 if outside.any() and remove.any():
  near=closest(outside); a[remove]=col[near[0][remove],near[1][remove]]
 # The established footprint supplies steps, white foam and bank pixels. Tint it toward the
 # actual painted water, and conserve the generated color inside where the two drawings agree.
 sample=base&gen&exact
 interior=nd.distance_transform_edt(exact)>1.4
 wet_paint=old.astype(np.float32).copy()
 if sample.any():
  pool=np.median(col[sample],axis=0); ref_pool=np.median(old[sample],axis=0)
  shift=np.clip(pool-ref_pool,[-19,-19,-19],[19,19,32])*.48
  wet_paint+=shift
  reuse=sample&interior;wet_paint[reuse]=.47*wet_paint[reuse]+.53*col[reuse]
 ref_luma=np.dot(old,[.299,.587,.114]);glint=exact&(ref_luma>178);wet_paint[glint]=.82*old[glint]+.18*wet_paint[glint]
 a[exact]=np.rint(np.clip(wet_paint[exact],0,255)).astype(np.uint8)
 return a,{'pixels_eau_geographie':count(exact),'pixels_peints_preserves_dans_eau':count(sample&interior),'raccords_anciens_chenaux':count(remove),'forme_eaux_livree_identique':True}

# All artwork uses a single image generator's painting to keep scale and palette coherent.
w0=np.zeros((H,W,3),np.uint8); wstat={};stat=[]; tstat={}
for k,box in enumerate(tb,1):
 component=TL==k; t=part(component,box); iw=part(wet,box)&t; ic=part(water,box); kind=int(np.unique(idx[component]).item())
 if k in paired: sid=paired[k];sx=sb[sid-1]
 else: sid,sx=replacement[k]
 z,ast=mount(t,sid,sx)
 if kind==5: z,tstat=tree_town(z,t,iw)
 z,ws=fix_waters(z,t,iw,ic,kind)
 if ws:wstat[kind]=ws
 part(w0,box)[t]=z[t]
 stat.append({'indice_geographie':kind,'rectangle_atlas':list(box),'rectangle_generation':list(sx),'decoupe_du_brut':sid,'ilots_bruts_en_contact':k in replacement,**ast})

# Set artwork on the DS-like logical pixel grid, with the exact coast and water in the existing
# twice-as-large placement grid. The coastline follows the native ink shade, not the uneven key.
near=closest(land);fill=w0[near[0],near[1]]
lo=resize(fill,(W//2,H//2),BOX).astype(np.float32)*.85+resize(fill,(W//2,H//2),N).astype(np.float32)*.15
# Recover one-pixel edges hidden by the artboard downsample, without adding a noise or texture layer.
brush=lo-nd.gaussian_filter(lo,(.66,.66,0.))
lo+=np.clip(brush*.55,-12,12)
body=resize(quant5(lo),(W,H))
edge=nd.distance_transform_edt(land)<=1.42; dry_edge=edge&land&~wet; bnd=body[dry_edge].astype(np.float32)
blue_edge=(bnd[:,2]>bnd[:,0]+4)&(bnd[:,1]>bnd[:,0])
ink=np.where(blue_edge[:,None],np.array([95,109,113]),np.array([143,91,44]));body[dry_edge]=quant5(bnd*.47+ink*.53)
# Restrict cyan downsampling bleed to the exact water boundary; no 2x2 chroma mix outside it.
near_wet=nd.binary_dilation(wet,structure=shape3,iterations=2)&land
body[near_wet]=quant5(w0[near_wet].astype(float))
# A few antialias pixels can fall back into chroma range after quantization; heal them locally.
spill=is_pink(body)&land
for i in np.unique(idx[spill]):
 reg=idx==i; bad=spill&reg
 near=closest(reg&~spill);body[bad]=body[near[0][bad],near[1][bad]]
assert not (is_pink(body)&land).any(), 'Chroma spill on terrain'

def paint(mask,clr=body):
 alpha=np.zeros((H,W,4),np.uint8);alpha[mask,:3]=clr[mask];alpha[mask,3]=255
 mag=np.empty((H,W,3),np.uint8);mag[...]=key;mag[mask]=clr[mask]
 assert np.array_equal(np.all(mag==key,axis=2),~mask)
 return alpha,mag
alpha,mag=paint(land)
save(mag,D/'Destiny-Style-DS-Magenta-1112x732.png'); save(alpha,D/'Destiny-Style-DS-Transparent-1112x732.png')
save(resize(mag,(W*5,H*5)),D/'Destiny-Style-DS-Magenta-5560x3660.png')
# The validated water and coastline accompany the layer as game-integration data.
save(wet.astype(np.uint8)*255,C/'Masque-eaux-1112x732.png');save(idx,C/'Index-terres-1112x732.png')
assert np.array_equal(alpha[...,3]>0,land) and np.array_equal(alpha[land,:3],mag[land])

names={1:'Orival',2:'Seracine',3:'Estrel',4:'Torselune',5:'Reverie',6:'Les-Haltes'}
labels={1:'Orival',2:'Séracine',3:'Estrel',4:'Torselune',5:'Île de Réverie',6:'Les Haltes'}
entries=[]; rec=np.zeros_like(alpha)
def export(name,mask,folder,nom, kind, add=False):
 box=bounds(mask);x,y,u,v=box; ap,mg=paint(mask); fn=folder/(name+'-Transparent.png');fm=folder/(name+'-Magenta.png')
 save(part(ap,box),fn);save(part(mg,box),fm)
 actual=np.array(Image.open(fn));assert np.array_equal(actual,part(alpha,box)*(part(mask,box)[...,None]))
 if add: assert not (rec[...,3][mask]>0).any(); rec[mask]=ap[mask]
 entries.append({'nom':nom,'id':name,'type':kind,'origine_xy':[x,y],'boite_xyxy':list(box),'taille':[u-x,v-y],
                 'transparent':str(fn.relative_to(D)),'magenta':str(fm.relative_to(D))})
for k in range(1,7):export(names[k],idx==k,A,labels[k],'continent' if k<5 else 'ile' if k==5 else 'archipel',True)
export('Ilots-satellites',idx>=101,A,'Îlots satellites','groupe',True)
assert np.array_equal(rec,alpha)
mask_ids=[i for i,box in enumerate(tb,1) if int(np.unique(idx[TL==i]).item())==6]
for k,nm in zip(sorted(mask_ids,key=lambda k:tb[k-1][1]),['Nacre','Voiles','Jusant']):export(nm,TL==k,A/'Haltes',nm,'composante_archipel')
for k in range(101,119):export(f'Ilot-{k}',idx==k,A/'Satellites',f'Îlot {k}','ilot')
assert len(entries)==28
mp=Image.open(A/'Reverie-Magenta.png').convert('RGB'); border=Image.new('RGB',(mp.width+14,mp.height+14),tuple(key));border.paste(mp,(7,7))
save(border.resize((border.width*4,border.height*4),N),D/'Reverie-Style-DS-Apercu.png')
jsonout({'canvas_px':[W,H],'unite_artistique_px':[W//2,H//2],'ordre_coordonnees':'x y (origine dans l’angle supérieur gauche, maxima exclusifs)',
         'cle_magenta_hex':'#FF00FF','pieces':entries,'lieux':place['sites'],'ancres_de_rendu':tstat,
         'statut_lieux':'Les huit noms connus sont marqués par existe_dans_le_projet ; les positions restent des propositions. Le terrain ne comporte pas de calque de repères ni de libellés.'},'Replacer-les-terres.json')
assert (U/'Sources'/'Geographie.json').read_bytes()==geography
jsonout({'statut':'PASS','canvas_px':[W,H],'composantes_exactes':m,'fonctions_alpha_sans_trou':True,'planche_magenta_fond_uniforme':True,
         'sources_art':'Génération guidée à l’échelle atlas ; quelques détails d’une génération rapprochée pour Réverie.',
         'regions':stat,'eaux':wstat,'ancres_de_rendu':tstat,'nombre_exports_individuels':len(entries),
         'sha256_geo_avant_apres':sha256(geography).hexdigest(),'sha256_brut_genere':sha256((S/'Destiny-DS-genere.png').read_bytes()).hexdigest(),
         'recomposition_des_7_groupes_pixel_a_pixel':True},'Verification.json')
print('PASS —', m,'masses exactes,',len(entries),'paires magenta/alpha,',count(wet),'px eau, clé et recomposition contrôlées.')
