#!/usr/bin/env python3
"""One exact 10×10 atlas, from 20 native PMU silhouettes and 5 generated Halcyon-style rugs."""
from pathlib import Path
from io import BytesIO
from collections import Counter
import base64,csv,hashlib,json,struct,zipfile
import numpy as np
from PIL import Image
from scipy import ndimage as nd

H=Path.home();S=Path(__file__).resolve().parent; O=S.parent; W=H/'.cache/guilde-objets'; B=W/'bruts';T=H/'.cache/fenetres-jeu-destiny/runtime-077/Content/Object'
SLOTS=(192,128); RAMP=[12,40,78,118,159,203,248]

def ramp(s):return np.array([tuple(bytes.fromhex(c)) for c in s.split()],dtype=float)
PALETTES=[
 ('miel','Chêne & miel',ramp('24150e 543018 85502a b87b3c d49f53 edc27b ffe2a8'),ramp('2a1a13 684322 956530 c48a3e e0ae58 f1cc85 ffe5b2')),
 ('grenat','Noyer & grenat',ramp('221216 472927 673f32 926048 b6825e d9a77d f2d0a8'),ramp('29151f 602c3d 86374b b05056 cb7264 e59b78 f6c7a2')),
 ('sauge','Châtaigne & sauge',ramp('241810 523523 795337 a47850 c5996a d9b48c f9dfae'),ramp('222820 3e4934 617150 81906b a0ab78 c6c99e eee3ba')),
 ('ardoise','Bois fumé & ardoise',ramp('17171b 373035 5c4b44 826550 a88666 cda987 ecd0a4'),ramp('17232b 2e4150 486073 657e90 8d9fa9 b4c1c2 e6dfc8')),
]
PMU=[
 ('banquet','Table de banquet','meubles','Guilde_Imm_pmu_table_banquet_seule','wood'),
 ('table_rondin','Grande table en rondin','meubles','Guilde_Imm_pmu_table_rondin_grand','wood'),
 ('banc','Banc de taverne','meubles','Guilde_PMU_Mob_030','wood'),
 ('fauteuil','Fauteuil capitonné','meubles','Guilde_PMU_Mob_083','cloth'),
 ('canape','Canapé arrondi','meubles','Guilde_PMU_Mob_004','cloth'),
 ('trone','Trône de racines','meubles','Guilde_PMU_Mob_123','cloth'),
 ('lit_fourrure','Lit de fourrure','meubles','Guilde_Imm_pmu_lit_fourrure','cloth'),
 ('lit_draperie','Lit à draperie','meubles','Guilde_PMU_Mob_098','cloth'),
 ('bibliotheque','Bibliothèque','meubles','Guilde_PMU_Mob_017','wood'),
 ('commode','Commode de chêne','meubles','Guilde_PMU_Mob_072','wood'),
 ('caisse','Caisse de réserve','meubles','Guilde_Imm_pmu_caisse_acajou','wood'),
 ('coffre','Coffre à ferrures','meubles','Guilde_Imm_pmu_coffre_bois_rouge','cloth'),
 ('table_service','Table de service','meubles','Guilde_PMU_Mob_038','wood'),
 ('cheminee','Cheminée et manteau','meubles','Guilde_PMU_Mob_001','wood'),
 ('fourneau','Fourneau','meubles','Guilde_Imm_pmu_fourneau_cuisine','wood'),
 ('desserte','Desserte de cuisine','meubles','Guilde_PMU_Mob_034','wood'),
 ('tableau','Tableau des missions','panneaux','Guilde_Imm_pmu_tableau_quetes_toit','wood'),
 ('banniere','Bannière parchemin','panneaux','Guilde_Imm_pmu_banniere_parchemin_1','cloth'),
 ('lampe','Lampe haute','meubles','PMU_Lampe_sur_pied_01','cloth'),
 ('miroir','Miroir doré','panneaux','Guilde_PMU_Mob_099','trim'),
]
RUGS=[
 ('salon','Grand tapis du Salon','T01-Salon',(176,108)),
 ('couloir','Long tapis de passage','T02-Runner',(176,60)),
 ('medaillon','Grand tapis médaillon','T03-Medaillon',(152,104)),
 ('tresse','Grande tresse ovale','T04-Tresse',(160,100)),
 ('quetes','Tapis des missions','T05-Quetes',(144,112)),
]
VINES=[('L01-Corniche',(152,34)),('L02-Poutre',(30,78)),('L03-Rive',(96,25)),('L04-Arche',(76,58))]

def hashbytes(a):return hashlib.sha256(a).hexdigest()
def write_json(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def png(a):
 b=BytesIO();Image.fromarray(a).save(b,'PNG',optimize=True);return b.getvalue()
def encoded(a):return base64.b64encode(png(a)).decode('ascii')

def dir_image(p):
 raw=p.read_bytes();size,=struct.unpack_from('<q',raw);w,h,z,n=struct.unpack('<iiii',raw[8+size:]);assert z==0 and n==1
 a=np.array(Image.open(BytesIO(raw[8:8+size])).convert('RGBA'));assert a.shape==(h,w,4)
 al=a[:,:,3].astype(float); keep=al>0
 if np.all(a[keep,:3]<=al[keep,None]):a[keep,:3]=np.clip(np.rint(a[keep,:3].astype(float)*255/al[keep,None]),0,255)
 a[~keep]=0;y,x=np.where(keep);x0,y0,x1,y1=int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)
 return a[y0:y1,x0:x1].copy(),dict(type='PMU dans Destiny 0.7.7',nom=p.stem,sha256=hashbytes(raw),coupe=[x0,y0,x1-x0,y1-y0],taille_source=[w,h])

def key(name,cap):
 f=B/(name+'.png');raw=Image.open(f).convert('RGB');a=np.array(raw);r,g,b=a.astype(np.int16).transpose(2,0,1)
 magenta=(r>24)&(b>g+6)&(r>g+14)&(2*b>r)
 if name=='L02-Poutre':magenta|=(r>g+33)&(b>g-13)  # The generator tinted its reference-room silhouette magenta as well.
 lab,_=nd.label(~magenta,np.ones((3,3)));sizes=np.bincount(lab.ravel());sizes[0]=0;main=lab==sizes.argmax();assert sizes.max()>5000
 if name.startswith('L'):
  # Retain nearby detached leaves/buds only, not key noise or stray distant clusters.
  near=nd.distance_transform_edt(~main)<=max(9,round(.028*max(a.shape[:2])))
  nearby=np.unique(lab[near&~magenta]);keep=main.copy()
  for i in nearby:
   if sizes[i]>=18:keep|=lab==i
 else:keep=main
 yy,xx=np.where(keep);x0,y0,x1,y1=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1);
 rgb=np.zeros((*a.shape[:2],4),np.uint8);rgb[keep,:3]=a[keep];rgb[keep,3]=255
 im=Image.fromarray(rgb[y0:y1,x0:x1]);k=min(cap[0]/im.width,cap[1]/im.height);im=im.resize((round(im.width*k),round(im.height*k)),Image.Resampling.BOX);out=np.array(im)
 inside=out[:,:,3]>=110;out[inside,3]=255;out[~inside]=0
 ys,xs=np.where(inside);out=out[ys.min():ys.max()+1,xs.min():xs.max()+1].copy();assert out.shape[0]<=cap[1] and out.shape[1]<=cap[0]
 return out,dict(type='création générée',nom=name,brut_sha256=hashbytes(f.read_bytes()),cadre_source=[x0,y0,x1-x0,y1-y0],dimensions_brut=list(raw.size))

def recolor(a,palette,mat):
 palette_id,_,wood,cloth=palette
 q=a.copy();rgb=a[:,:,:3].astype(float);r,g,b=rgb.transpose(2,0,1);y=.299*r+.587*g+.114*b; saturated=rgb.max(2)-rgb.min(2);depth=a[:,:,3]>0
 # Keep native ink/metal/paper detail. Pigments use ordered lightness ramps, not flat washes.
 color=depth&(y>19);timber=color&(r>=g-3)&(g>=b-4)&((r-b)>12)
 fabric=color&(((r-g)>24)&((r-g)>(g-b)*1.38))|(color&(b>g+13))|(color&(g>r+14))|(color&(r>b+12)&(saturated<46)&(y>=146))
 if mat=='tapis':
  fabric=color&(y<204);timber=color&~fabric
 elif mat=='cloth':
  # Restrained secondary colour on the upholstery; dark timber and metal stay legible.
  fabric &= (y<238);timber &=~fabric
  if np.count_nonzero(fabric)<12:fabric=color&(y>80)&(y<186)&(b>g-25);timber&=~fabric
 elif mat=='trim':
  fabric=color&(saturated<65)&(y>68);timber&=~fabric
 else:
  fabric=color&((g>r+20)|(b>g+24))&(y>58)&(y<213);timber&=~fabric
 n=0
 for mask,std,opacity in [(timber,wood,.90),(fabric,cloth,.92)]:
  if not mask.any():continue
  n+=int(mask.sum());tones=np.stack([np.interp(y[mask],RAMP,std[:,c]) for c in range(3)],1)
  q[mask,:3]=np.clip(np.rint(rgb[mask]*(1-opacity)+tones*opacity),0,255)
 if not n:
  rgb2=np.stack([np.interp(y[color],RAMP,wood[:,c]) for c in range(3)],1);q[color,:3]=np.rint(.2*rgb[color]+.8*rgb2)
 assert np.array_equal(q[:,:,3],a[:,:,3]);assert (q!=a).any();return q

def main():
 for p in (O/'Modeles-generes',W/'normalises',W/'PNG'):p.mkdir(parents=True,exist_ok=True)
 # The walnut mid-tones were auditioned on the generated chest, but retain the native PMU silhouette.
 trial,gen_info=key('PMU-Coffre-Noyer',(80,70));t=trial[:,:,:3].astype(int);r,g,b=t.transpose(2,0,1);q=(trial[:,:,3]>0)&(r>=g+7)&(g>=b-6)&(r<165)&(r>43);chest=np.median(t[q],axis=0)
 assert q.sum()>60
 nominal=PALETTES[1][2];nominal[2]=np.rint(.70*nominal[2]+.30*chest)
 sources=[];generated=[]
 for ident,titre,cat,src,mat in PMU:
  a,provenance=dir_image(T/(src+'.dir'));sources.append((ident,titre,cat,a,mat,provenance))
 for ident,titre,src,cap in RUGS:
  a,provenance=key(src,cap);(O/'Modeles-generes'/(src+'.png')).write_bytes(png(a));sources.append(('tapis_'+ident,titre,'tapis',a,'tapis',provenance));generated.append(provenance)
 for name,size in VINES:
  a,provenance=key(name,size);(O/'Modeles-generes'/(name+'.png')).write_bytes(png(a));(W/'normalises'/(name+'.png')).write_bytes(png(a));generated.append(provenance)
 assert len(sources)==25
 atlas=Image.new('RGBA',(SLOTS[0]*10,SLOTS[1]*10));records=[];entities=[];all_hash=set()
 artists=[]
 for j, (ident,title,cat,base,mat,origin) in enumerate(sources):
  for pi,palette in enumerate(PALETTES):
   code,label,_,_=palette; r=(j//5)*2+pi//2;c=(j%5)*2+pi%2; number=r*10+c+1
   a=recolor(base,palette,mat);h,w=a.shape[:2];assert w<=SLOTS[0]-16 and h<=SLOTS[1]-16,(ident,w,h)
   x=c*SLOTS[0]+(SLOTS[0]-w)//2;y=r*SLOTS[1]+(SLOTS[1]-h)//2;atlas.paste(Image.fromarray(a),(x,y))
   identite='pmu100_'+ident+'_'+code;name=f'{number:02d}-{ident}-{code}.png';asset=png(a);digest=hashbytes(asset);assert digest not in all_hash,(ident,code);all_hash.add(digest)
   (W/'PNG'/name).write_bytes(asset);red=dict(numero=number,id=identite,modele=ident,nom=title,palette=code,palette_nom=label,categorie=cat,fichier='PNG/'+name,cellule=[c*SLOTS[0],r*SLOTS[1],*SLOTS],rectangle=[x,y,w,h],ancre=[w//2,max(0,h-3)],sha256=digest,source=origin);records.append(red)
   entities.append(dict(n=number,id=identite,label=title+' · '+label,category=cat,wall=ident in ('banniere','miroir'),w=w,h=h,palette=code,collection='pmu100',previewOnly=True,m=[base64.b64encode(asset).decode('ascii')]))
 records.sort(key=lambda x:x['numero']);entities.sort(key=lambda x:x['n']);assert [r['numero'] for r in records]==list(range(1,101))
 path=O/'Tilesheet-PMU-Halcyon-100.png';atlas.save(path,optimize=True);data=np.asarray(atlas);mask=np.zeros(data.shape[:2],bool)
 for q in records:
  x,y,w,h=q['rectangle'];a=np.asarray(Image.open(W/q['fichier']).convert('RGBA'));assert np.array_equal(data[y:y+h,x:x+w],a) and not mask[y:y+h,x:x+w].any()
  mask[y:y+h,x:x+w]=True
 assert not data[~mask,3].any()
 write_json(O/'Index-100.json',dict(total=100,modeles=25,palettes=[dict(id=p[0],nom=p[1],bois=p[2].astype(int).tolist(),textile=p[3].astype(int).tolist()) for p in PALETTES],taille_px=list(atlas.size),grille=[10,10],cellule_px=list(SLOTS),tuile_logique_px=8,objets=records,source_palette_noyer=gen_info,generations=generated))
 with (O/'Index-100.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f,delimiter=';');w.writerow(['Numero','Modele','Palette','x','y','Largeur','Hauteur','PNG']);w.writerows([r['numero'],r['nom'],r['palette_nom'],*r['rectangle'],r['fichier']] for r in records)
 write_json(W/'Catalogue.json',entities)
 print('PASS · 100 PNG distincts ; 25 modèles × 4 ; atlas 1920×1280, alpha vérifié dans les 100 cases.',flush=True)

if __name__=='__main__':main()
