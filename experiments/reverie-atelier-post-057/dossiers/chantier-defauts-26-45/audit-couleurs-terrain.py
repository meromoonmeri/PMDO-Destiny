from pathlib import Path
import io,struct,json,collections
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image
R=Path(__file__).resolve().parent;O=R/'audit-pixel-integral';refs=['Metano_Town_Base','Metano_Town_Trimmed','Metano_Town_Cliffs','Metano_Town_River','Metano_Town_River_Animation_1','Metano_Town_River_Animation_2','Metano_Town_River_Animation_3','Metano_Town_River_Animation_4'];S=set()
for name in refs:
 b=(R/'reference-metano/Content/Tile'/f'{name}.tile').read_bytes();_,n=struct.unpack_from('<ii',b)
 for i in range(n):
  x,y,o=struct.unpack_from('<iiq',b,8+16*i);ln=struct.unpack_from('<q',b,o)[0];a=np.array(Image.open(io.BytesIO(b[o+8:o+8+ln])).convert('RGBA'));S.update(map(tuple,a[a[:,:,3]>0,:3].tolist()))
ref=np.array(sorted(S),dtype=np.uint8);tree=cKDTree(ref);terrain=np.array(Image.open(O/'terrain-phase0.png').convert('RGBA'));scene=np.array(Image.open(O/'rendu-phase0.png').convert('RGBA'));visible=(terrain[:,:,3]>0)&np.all(terrain==scene,axis=2);rgb=terrain[:,:,:3];v=rgb.astype(np.uint32);ids=(v[:,:,0]<<16)|(v[:,:,1]<<8)|v[:,:,2];colors,counts=np.unique(ids[visible],return_counts=True);q=np.column_stack(((colors>>16)&255,(colors>>8)&255,colors&255));dist,ix=tree.query(q,k=1,p=np.inf);hist=collections.Counter();entries=[]
for col,n,d,j in zip(q,counts,dist,ix):
 hist[int(d)]+=int(n)
 if d>0:entries.append({'rgb':col.tolist(),'pixels':int(n),'distance_max_rgb':int(d),'plus_proche_metano':ref[j].tolist()})
entries.sort(key=lambda x:x['pixels'],reverse=True);badcols=colors[dist>=16];# signale des écarts, pas des défauts prouvés.
flag=visible&np.isin(ids,badcols);pix=np.zeros((4000,1600),dtype=np.uint8);pix[flag]=255;Image.fromarray(pix).save(O/'couleurs-ecart-16-candidats.png')
H=[]
for y in range(0,4000,64):
 for x in range(0,1600,64):
  c=int(flag[y:y+64,x:x+64].sum())
  if c:H.append([x,y,c])
H.sort(key=lambda z:z[2],reverse=True)
info={'terrain_pixels_phase0_visibles_non_recouverts':int(visible.sum()),'terrain_visible_couleurs_distinctes':len(colors),'palette_metano_couleurs':len(ref),'distance_max_canal_histogramme':dict(sorted(hist.items())),'pixels_distance_au_moins_16':int(flag.sum()),'zones_64px_les_plus_touchees':H[:100],'couleurs_atypiques':entries,'note':'Palette non spatiale : aucun test ne garantit qu’un pixel est à la bonne place. Écart peut être une ressource non-Métano, un mélange alpha ou un effet voulu ; rendu terrain Base/Cliffs/River phase 0, personnages non modélisés.'}
(O/'comparaison-couleurs-metano.json').write_text(json.dumps(info,ensure_ascii=False,indent=2));print('Terrain visible',int(visible.sum()),'palette',len(ref),'histogramme',dict(sorted(hist.items())),'>=16',int(flag.sum()),flush=True)
