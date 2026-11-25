from pathlib import Path
import gzip,ijson,struct,io,json,hashlib,collections,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;B=R/'base';W=R/'corrections-chemin30-en-cours';O=R/'audit-pixel-integral';O.mkdir(exist_ok=True)
refnames=['Metano_Town_Base','Metano_Town_Trimmed','Metano_Town_Cliffs','Metano_Town_River','Metano_Town_River_Animation_1','Metano_Town_River_Animation_2','Metano_Town_River_Animation_3','Metano_Town_River_Animation_4']
palette=np.zeros(1<<24,dtype=np.bool_);numref=0
for name in refnames:
 p=R/'reference-metano/Content/Tile'/f'{name}.tile';b=p.read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8
 for i in range(n):
  x,y,o=struct.unpack_from('<iiq',b,8+16*i);ln=struct.unpack_from('<q',b,o)[0];a=np.asarray(Image.open(io.BytesIO(b[o+8:o+8+ln])).convert('RGBA'));v=a[a[:,:,3]>0,:3].astype(np.uint32);ids=(v[:,0]<<16)|(v[:,1]<<8)|v[:,2];palette[ids]=True;numref+=len(v)
 print('Palette native',name,n,'tuiles',flush=True)
banks={};cache={};missing=collections.Counter();bad=collections.Counter()
def get(fr):
 name=fr.get('Sheet','');pos=fr.get('TexLoc',{});x=pos.get('X');y=pos.get('Y');key=(name,x,y)
 if not name:return None
 if key in cache:return cache[key]
 if name not in banks:
  p=W/'game/Content/Tile'/f'{name}.tile';p=p if p.exists() else B/'game/Content/Tile'/f'{name}.tile'
  if not p.exists():missing[name]+=1;cache[key]=None;return None
  b=p.read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8,(name,size);ix={}
  for i in range(n):
   tx,ty,off=struct.unpack_from('<iiq',b,8+16*i);assert (tx,ty) not in ix and 0<=off<len(b);ix[tx,ty]=off
  banks[name]=(b,ix)
 b,ix=banks[name]
 if (x,y) not in ix:bad[name,x,y]+=1;cache[key]=None;return None
 off=ix[x,y];length=struct.unpack_from('<q',b,off)[0];assert 0<=length<=len(b)-off-8
 im=Image.open(io.BytesIO(b[off+8:off+8+length])).convert('RGBA');assert im.size==(8,8);cache[key]=im;return im
stats=[];im=Image.new('RGBA',(1600,4000));terrain=Image.new('RGBA',(1600,4000));fl=collections.Counter();sheets=collections.Counter();variations=collections.Counter();samples=[]
with gzip.open(W/'payload/reverie_centre.rsground.gz','rb') as f:
 if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
 for li,l in enumerate(ijson.items(f,'Object.Layers.item')):
  count=framecount=occ=0;assert len(l['Tiles'])==200
  for x,col in enumerate(l['Tiles']):
   assert len(col)==500,(l['Name'],x,len(col))
   for y,cell in enumerate(col):
    for anim in cell.get('Layers',[]):
     frames=anim.get('Frames',[]);count+=bool(frames);framecount+=len(frames)
     if len(frames)>1:
      dur=anim.get('FrameLength');fl[(l['Name'],len(frames),dur)]+=1
      pix=[get(z) for z in frames];raw=[v.tobytes() if v else None for v in pix];variations[(l['Name'],len(frames),len(set(raw)))]+=1
     if frames:
      for fr in frames:
       sheets[fr.get('Sheet','')]+=1;get(fr)
      p=get(frames[0]);
      if p is not None:
       im.alpha_composite(p,(x*8,y*8));occ+=1
       if li<3:terrain.alpha_composite(p,(x*8,y*8))
  stats.append({'layer':l['Name'],'cells':200*500,'nonempty_animations':count,'frame_references':framecount,'drawn_phase0':occ});print('Calque audité',l['Name'],count,framecount,flush=True)
arr=np.asarray(im);ground=np.asarray(terrain);assert arr.shape==(4000,1600,4)
im.save(O/'rendu-phase0.png');terrain.save(O/'terrain-phase0.png')
v=ground[:,:,:3].astype(np.uint32);ids=(v[:,:,0]<<16)|(v[:,:,1]<<8)|v[:,:,2];opaque=ground[:,:,3]>0;outside=(~palette[ids])&opaque
# Source alpha et couches peuvent produire de nouveaux RGB à la composition ; ce n'est PAS un verdict.
heat=np.asarray(im.convert('RGB')).copy();heat[outside]=(255,0,255);Image.fromarray(heat).save(O/'palette-terrain-candidats.png')
colors,counts=np.unique(v[outside],axis=0,return_counts=True);rank=sorted(zip(counts.tolist(),colors.tolist()),reverse=True)
# Détection exhaustive des 6,4 millions pixels du rendu, sans resampling ni requalification artistique.
summary={'dimensions':[1600,4000],'pixels_total':6400000,'pixels_alpha_nul':int((arr[:,:,3]==0).sum()),'pixels_alpha_partiel':int(((arr[:,:,3]>0)&(arr[:,:,3]<255)).sum()),'pixels_opacite_totale':int((arr[:,:,3]==255).sum()),'pixels_terrain_visibles':int(opaque.sum()),'pixels_terrain_rgb_hors_palette_metano_brute':int(outside.sum()),'couleurs_palette_metano':int(palette.sum()),'pixels_sources_metano_examines':numref,'couleurs_hors_palette_les_plus_frequentes':rank[:40], 'layers':stats,'sequences_animees':[{'layer':k[0],'frames':k[1],'duree':k[2],'count':v} for k,v in fl.items()], 'variation_graphique':[{'layer':k[0],'frames':k[1],'images_distinctes':k[2],'count':v} for k,v in variations.items()],'banques_utilisees':dict(sheets),'references_invalides':[{ 'bank':k[0],'x':k[1],'y':k[2],'count':v} for k,v in bad.items()],'banques_manquantes':dict(missing),'tuiles_uniques_lues':len(cache),'note':'Les comparaisons de couleurs se rapportent au terrain composite Base/Cliffs/River phase 0 ; mélanges alpha, provenance différente légitime, bâtiments ou variantes peuvent produire des faux positifs. Examen artistique nécessaire.'}
(O/'inventaire-pixel-et-references.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print('PIXELS',summary['pixels_total'],'alpha 0',summary['pixels_alpha_nul'],'terrain hors palette',summary['pixels_terrain_rgb_hors_palette_metano_brute'],'references invalides',len(bad),'banques manquantes',len(missing),flush=True)
