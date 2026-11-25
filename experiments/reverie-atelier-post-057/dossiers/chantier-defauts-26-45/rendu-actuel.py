from pathlib import Path
import gzip,ijson,struct,io,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;D=R/'base';cache={};sheets={}
def tile(f):
 name=f.get('Sheet','');pos=f['TexLoc'];key=(name,pos['X'],pos['Y'])
 if not name:return None
 if key in cache:return cache[key]
 if name not in sheets:
  p=(R/'corrections-berge-en-cours/game/Content/Tile'/f'{name}.tile');p=p if p.exists() else (D/'game/Content/Tile'/f'{name}.tile');b=p.read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8
  ix={struct.unpack_from('<iiq',b,8+16*i)[:2]:struct.unpack_from('<iiq',b,8+16*i)[2] for i in range(n)};sheets[name]=(b,ix)
 b,ix=sheets[name];off=ix[(pos['X'],pos['Y'])];length=struct.unpack_from('<q',b,off)[0];out=Image.open(io.BytesIO(b[off+8:off+8+length])).convert('RGBA');cache[key]=out;return out
regions={'pierres':(608,224,928,464),'berge_boutique':(448,862,550,1000),'pont':(988,1070,1200,1160),'guilde':(690,880,880,1000),'bassin':(920,1942,1232,2178)}
frames={name:[Image.new('RGBA',(r[2]-r[0],r[3]-r[1])) for _ in range(4)] for name,r in regions.items()};stats=[]
with gzip.open(R/'corrections-berge-en-cours/payload/reverie_centre.rsground.gz','rb') as f:
 if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
 for li,l in enumerate(ijson.items(f,'Object.Layers.item')):
  for name,(x0,y0,x1,y1) in regions.items():
   for x in range(x0//8,(x1+7)//8):
    for y in range(y0//8,(y1+7)//8):
     for a in l['Tiles'][x][y].get('Layers',[]):
      fr=a.get('Frames',[])
      if not fr:continue
      if len(fr)>1:stats.append([name,li,l['Name'],x*8,y*8,len(fr),a.get('FrameLength'),[i.get('Sheet') for i in fr]])
      for i in range(4):
       im=tile(fr[i%len(fr)]);
       if im:frames[name][i].alpha_composite(im,(x*8-x0,y*8-y0))
  print('couche',li,l['Name'],flush=True)
for name,fs in frames.items():
 out=Image.new('RGBA',(fs[0].width*2,fs[0].height*2))
 for i,im in enumerate(fs):out.alpha_composite(im,((i%2)*im.width,(i//2)*im.height))
 out.save(R/f'actuel-phases-{name}.png')
(R/'references-animees-actuel.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False))
print('Animations',len(stats))
