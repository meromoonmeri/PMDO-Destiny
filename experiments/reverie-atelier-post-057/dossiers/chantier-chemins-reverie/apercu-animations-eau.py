from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import ijson,gzip,struct,io,json,hashlib
R=Path('.');B=R/'base';O=R/'correctif-falaises-eau-0.5.0';name='reverie_centre.rsground.gz';areas=[('Kecleon',(544,800,680,912)),('Cascade sud',(248,1864,384,2048))];cache={};banks={}
def tile(f):
 n=f.get('Sheet','');loc=f['TexLoc'];k=(n,loc['X'],loc['Y'])
 if not n:return None
 if k in cache:return cache[k]
 if n not in banks:
  p=O/'game/Content/Tile'/f'{n}.tile'
  if not p.exists():p=B/'game/Content/Tile'/f'{n}.tile'
  data=p.read_bytes();size,count=struct.unpack_from('<ii',data);assert size==8;d={}
  for i in range(count):x,y,off=struct.unpack_from('<iiq',data,8+16*i);d[x,y]=off
  banks[n]=(data,d)
 data,d=banks[n];off=d[(loc['X'],loc['Y'])];length=struct.unpack_from('<q',data,off)[0];im=Image.open(io.BytesIO(data[off+8:off+8+length])).convert('RGBA');cache[k]=im;return im

def read(path):
 all_layers=[[] for _ in areas]
 with gzip.open(path,'rb') as f:
  if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
  for l in ijson.items(f,'Object.Layers.item'):
   for idx,(_,box) in enumerate(areas):
    x1,y1,x2,y2=box;records=[]
    for x in range(x1//8,(x2+7)//8):
     for y in range(y1//8,(y2+7)//8):
      for a in l['Tiles'][x][y].get('Layers',[]):
       if a.get('Frames'):records.append((x*8-x1,y*8-y1,a))
    all_layers[idx].append(records)
 return all_layers
old=read(B/'payload'/name);new=read(O/'payload'/name)
def render(loaded,idx,tick):
 _,box=areas[idx];im=Image.new('RGBA',(box[2]-box[0],box[3]-box[1]))
 for layer in loaded[idx]:
  for x,y,a in layer:
   fr=a['Frames'];f=fr[(tick//a['FrameLength'])%len(fr)];t=tile(f)
   if t:im.alpha_composite(t,(x,y))
 return im
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15);frames=[]
for tick in range(0,360,4):
 can=Image.new('RGB',(592,722),'#1c2624');d=ImageDraw.Draw(can);d.text((12,6),'Cadence PMDO simulée • rendu sans PNJ',font=font,fill='white')
 for idx,(title,box) in enumerate(areas):
  row=30+idx*335;d.text((12,row),title+' — avant',font=font,fill='#ffcf77');d.text((300,row),title+' — après',font=font,fill='#ffcf77')
  for px,loaded in [(12,old),(300,new)]:
   im=render(loaded,idx,tick);im.thumbnail((272,300),Image.Resampling.NEAREST);im=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST) if im.width<=136 and im.height<=150 else im
   # Image du sud 136x184 : redimensionner à 1,5× ne serait pas pixel-exact ; conserver x1.
   if im.height>300:im=im.resize((im.width//2,im.height//2),Image.Resampling.NEAREST)
   bg=Image.new('RGBA',im.size,(25,32,30,255));bg.alpha_composite(im);can.paste(bg.convert('RGB'),(px,row+22))
 frames.append(can)
frames[0].save(R/'avant-apres-cascades-anime.gif',save_all=True,append_images=frames[1:],duration=67,loop=0,optimize=True,disposal=2)
print('GIF :',len(frames),'phases, cadence simulée ~15 fps, cycle 6 secondes',flush=True)
