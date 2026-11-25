from pathlib import Path
import gzip,ijson,struct,io,json,hashlib,collections
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;B=R/'base';W=R/'corrections-alpha-en-cours';O=R/'audit-pixel-integral';refs=R/'reference-metano/Content/Tile';digests=set();names=[]
def it(p):
 b=p.read_bytes();s,n=struct.unpack_from('<ii',b);assert s==8
 for i in range(n):
  x,y,o=struct.unpack_from('<iiq',b,8+16*i);sz=struct.unpack_from('<q',b,o)[0];yield (x,y),np.asarray(Image.open(io.BytesIO(b[o+8:o+8+sz])).convert('RGBA'))
for path in refs.glob('*.tile'):
 count=0
 for xy,a in it(path):digests.add(hashlib.sha256(a.tobytes()).digest());count+=1
 names.append([path.name,count]);print('Origine',path.name,count,flush=True)
refs_count=collections.Counter();sequences=0
with gzip.open(W/'payload/reverie_centre.rsground.gz','rb') as f:
 f.read(3)
 for l in ijson.items(f,'Object.Layers.item'):
  for x,col in enumerate(l['Tiles']):
   for y,c in enumerate(col):
    for anim in c.get('Layers',[]):
     fs=anim.get('Frames',[]);sequences+=bool(fs)
     for fr in fs:
      q=fr.get('TexLoc',{});refs_count[(fr.get('Sheet',''),q.get('X'),q.get('Y'))]+=1
print('Images référencées',sum(refs_count.values()),'références distinctes',len(refs_count),flush=True)
groups=collections.defaultdict(lambda:collections.Counter());want=collections.defaultdict(dict)
for (name,x,y),n in refs_count.items():
 if not name:groups['(image transparente intentionnelle)']['references']+=n;groups['(image transparente intentionnelle)']['pixels_alpha0']+=64*n
 else:want[name][x,y]=n
for name,targets in want.items():
 p=W/'game/Content/Tile'/f'{name}.tile';p=p if p.exists() else B/'game/Content/Tile'/f'{name}.tile';seen=0
 for xy,a in it(p):
  if xy not in targets:continue
  n=targets[xy];seen+=1;alpha=a[:,:,3];g=groups[name];g['references']+=n;g['tuiles_distinctes']+=1;g['pixels_alpha0']+=int((alpha==0).sum())*n;g['pixels_alpha_partiel']+=int(((alpha>0)&(alpha<255)).sum())*n;g['pixels_opaques']+=int((alpha==255).sum())*n
  if hashlib.sha256(a.tobytes()).digest() in digests:g['references_tuiles_identiques_metano']+=n;g['tuiles_distinctes_identiques_metano']+=1
 assert seen==len(targets),(name,seen,len(targets));print('Banque auditée',name,seen,flush=True)
total=collections.Counter()
for a in groups.values():total.update(a)
assert total['pixels_alpha0']+total['pixels_alpha_partiel']+total['pixels_opaques']==sum(refs_count.values())*64
result={'references_ponderees':sum(refs_count.values()),'sequences':sequences,'pixels_images_references_ponderees':sum(refs_count.values())*64,'banques_metano':names,'tuiles_metano_distinctes':len(digests),'total':dict(total),'banques':{k:dict(v) for k,v in groups.items()},'note':'Comptage par référence de trame (y compris répétitions et trames vides), pas positions finales visibles. Correspondance exacte d\'une tuile complète, non nécessaire pour valider un montage ; les banques composites et ressources propres à Réverie ne sont pas automatiquement des erreurs.'}
(O/'inventaire-pixels-images-animees.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('PASS toutes les images référencées examinées',result['pixels_images_references_ponderees'],'pixels de trame',flush=True)
