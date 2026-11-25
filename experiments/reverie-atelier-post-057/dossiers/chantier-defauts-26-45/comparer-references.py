from pathlib import Path
import struct,io,collections,hashlib,json
from PIL import Image
R=Path(__file__).resolve().parent;allfiles=list((R/'reference-metano/Content/Tile').glob('*.tile'));groups=collections.defaultdict(list)
def get(path):
 data=path.read_bytes();size,n=struct.unpack_from('<ii',data);assert size==8
 for k in range(n):
  x,y,o=struct.unpack_from('<iiq',data,8+16*k);n2=struct.unpack_from('<q',data,o)[0];im=Image.open(io.BytesIO(data[o+8:o+8+n2])).convert('RGBA');assert im.size==(8,8);yield x,y,im
for path in allfiles:
 for x,y,im in get(path):groups[im.tobytes()].append((path.stem,x,y))
print('tuiles originales',sum(map(len,groups.values())),'uniques',len(groups))
for path,wanted in [(R/'base/game/Content/Tile/Reverie_Geo_14_Paysages_composites.tile',{(91,112),(91,113)}),(R/'base/game/Content/Tile/Reverie_Geo_12_Eaux_frames.tile',{(172,157),(173,157),(200,157)})]:
 for x,y,im in get(path):
  if (x,y) in wanted:print(path.stem,x,y,'égalités exactes :',groups.get(im.tobytes(),[])[:20])
# Reconstruire des atlas complets pour inspection visuelle des groupes natifs.
for name in ['Metano_Town_River','Metano_Town_River_Animation_1','Metano_Town_River_Animation_2','Metano_Town_River_Animation_3','Metano_Town_River_Animation_4','Metano_Town_Animation_Tileset','Metano_Town_Animated','Metano_Town_Base','Metano_Town_Trimmed']:
 path=R/'reference-metano/Content/Tile'/f'{name}.tile';items=list(get(path));width=max(x for x,y,im in items)+1;height=max(y for x,y,im in items)+1;sheet=Image.new('RGBA',(width*8,height*8));
 for x,y,im in items:sheet.paste(im,(x*8,y*8))
 sheet.save(R/f'reference-{name}.png');print(name,sheet.size,flush=True)
