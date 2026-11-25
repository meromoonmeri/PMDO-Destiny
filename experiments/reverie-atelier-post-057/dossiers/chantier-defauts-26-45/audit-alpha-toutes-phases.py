from pathlib import Path
import gzip,ijson,struct,io,json,math,collections
from PIL import Image
import numpy as np,cv2
R=Path(__file__).resolve().parent;B=R/'base';W=R/'corrections-chemin30-en-cours';O=R/'audit-pixel-integral';full=(1<<64)-1;guaranteed=np.zeros((200,500),dtype=np.uint64);variable=collections.defaultdict(list);banks={};cache={};missing=[]
def mask(fr):
 name=fr.get('Sheet','');pos=fr.get('TexLoc',{});key=(name,pos.get('X'),pos.get('Y'))
 if not name:return 0
 if key in cache:return cache[key]
 if name not in banks:
  p=W/'game/Content/Tile'/f'{name}.tile';p=p if p.exists() else B/'game/Content/Tile'/f'{name}.tile';b=p.read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8
  banks[name]=(b,{struct.unpack_from('<iiq',b,8+16*i)[:2]:struct.unpack_from('<iiq',b,8+16*i)[2] for i in range(n)})
 b,ix=banks[name];o=ix[key[1:]];n=struct.unpack_from('<q',b,o)[0];a=np.asarray(Image.open(io.BytesIO(b[o+8:o+8+n])).convert('RGBA'));v=(a[:,:,3].ravel()>0).astype('uint8');cache[key]=int.from_bytes(np.packbits(v,bitorder='little').tobytes(),'little');return cache[key]
with gzip.open(W/'payload/reverie_centre.rsground.gz','rb') as f:
 f.read(3)
 for layer in ijson.items(f,'Object.Layers.item'):
  for x,col in enumerate(layer['Tiles']):
   for y,c in enumerate(col):
    for anim in c.get('Layers',[]):
     frames=anim.get('Frames',[])
     if not frames:continue
     masks=[mask(fr) for fr in frames];inter=full
     for m in masks:inter&=m
     guaranteed[x,y]|=np.uint64(inter)
     if len(set(masks))>1:
      dur=anim.get('FrameLength',60);assert isinstance(dur,int) and dur>0,(layer['Name'],x,y,dur)
      variable[x,y].append((dur,masks))
  print('Analyse alpha',layer['Name'],'cellules à couverture variable',len(variable),flush=True)
possible=np.zeros((4000,1600),dtype=np.uint8);permanent=possible.copy();phase0=possible.copy();examined=0;maxperiod=0;periods=collections.Counter();uncertain=[]
def bitmap(m):return np.unpackbits(np.frombuffer(int(m).to_bytes(8,'little'),dtype=np.uint8),bitorder='little').reshape((8,8))
for x in range(200):
 for y in range(500):
  base=int(guaranteed[x,y]);
  if base==full:continue
  seq=variable.get((x,y),[]);cycle=1;g=0
  for duration,frames in seq:cycle=math.lcm(cycle,duration*len(frames));g=math.gcd(g,duration)
  if not seq:g=1
  maxperiod=max(maxperiod,cycle);periods[cycle]+=1;maybe=0;always=full;zero=0
  for t in range(0,cycle,g):
   coverage=base
   for duration,frames in seq:coverage|=frames[(t//duration)%len(frames)]
   hole=full^coverage;maybe|=hole;always&=hole
   if t==0:zero=hole
  examined+=1
  if maybe:
   q=(y*8,x*8);possible[q[0]:q[0]+8,q[1]:q[1]+8]=bitmap(maybe)*255
   permanent[q[0]:q[0]+8,q[1]:q[1]+8]=bitmap(always)*255
   phase0[q[0]:q[0]+8,q[1]:q[1]+8]=bitmap(zero)*255
   uncertain.append({'cell':[x,y],'pixels_possibles':maybe.bit_count(),'pixels_permanents':always.bit_count(),'cycle_frames':cycle,'durations':[z[0] for z in seq]})
Image.fromarray(possible).save(O/'alpha-transparent-au-moins-une-phase.png');Image.fromarray(permanent).save(O/'alpha-transparent-toutes-phases.png')
orig=np.asarray(Image.open(O/'rendu-phase0.png').convert('RGBA'))[:,:,3];assert np.array_equal(phase0>0,orig==0),'calque de phase 0 non équivalent'
n,l,stats,c=cv2.connectedComponentsWithStats((possible>0).astype('uint8'),8);components=[]
for i in range(1,n):
 x,y,w,h,npx=map(int,stats[i]);components.append({'x':x,'y':y,'w':w,'h':h,'pixels':npx,'boundary':x==0 or y==0 or x+w==1600 or y+h==4000})
info={'pixels_phase0':int((phase0>0).sum()),'pixels_transparents_au_moins_une_phase':int((possible>0).sum()),'pixels_transparents_toutes_phases':int((permanent>0).sum()),'cellules_incomplete_coverage_examined':examined,'cellules_avec_trous':len(uncertain),'periode_max_locale_frames':maxperiod,'periodes_locales':dict(periods),'composantes_union':components,'cells':uncertain,'method':'Couverture alpha par séquence, intersection sur toutes les images, union par calques ; chaque cycle local exact sur les instants de transition, en tenant compte des durées. Aucun déplacement de personnage ou état de jeu modélisé. Définition : alpha=0 ; alpha partiel non compris.'}
(O/'alpha-toutes-phases.json').write_text(json.dumps(info,ensure_ascii=False,indent=2));print('PASS phase0 identique ; pixels alpha0 quelque phase',info['pixels_transparents_au_moins_une_phase'],'permanents',info['pixels_transparents_toutes_phases'],'cellules',info['cellules_avec_trous'],'max cycle',maxperiod,flush=True)
