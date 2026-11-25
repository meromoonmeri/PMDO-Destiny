from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import gzip,json,sys
R=Path('/home/user/chantier-corrections-bassin-55'); P=Path('/home/user/chantier-corrections-bassin-53-54');sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
p=P/'candidat/payload/reverie_etang.rsground.gz';o=json.loads(gzip.decompress(p.read_bytes()).decode('utf-8-sig'))['Object'];layers=o['Layers'];sheets={}
def get(f):
 n=f.get('Sheet','');
 if not n:return None
 if n not in sheets:sheets[n]=SheetReader(P/'banques'/(n+'.tile'))
 loc=f['TexLoc'];return sheets[n].get_tile(loc['X'],loc['Y'])
def render(rect,include=None):
 x0,y0,x1,y1=rect;img=Image.new('RGBA',((x1-x0)*8,(y1-y0)*8))
 for layer in layers:
  if include is not None and layer['Name'] not in include:continue
  for x in range(x0,x1):
   for y in range(y0,y1):
    for sub in layer['Tiles'][x][y].get('Layers',[]):
     frames=sub.get('Frames',[])
     if frames:
      t=get(frames[0]);
      if t:img.alpha_composite(t,((x-x0)*8,(y-y0)*8))
 return img
regions={'souche':(165,260,177,269),'fleurs':(145,279,156,292),'bas':(107,305,119,317),'ouest':(98,255,112,283),'est':(162,264,173,279)}
for name,box in regions.items():
 for sel in [None,['Base'],['Cliffs'],['Objects'],['Objects Over']]:
  im=render(box,sel);scaled=im.resize((im.width*6,im.height*6),Image.Resampling.NEAREST);d=ImageDraw.Draw(scaled);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',9)
  for x in range(box[2]-box[0]):d.line((x*48,0,x*48,scaled.height),fill=(255,0,255,110),width=1);d.text((x*48+2,1),str(x+box[0]),font=font,fill='white',stroke_width=1,stroke_fill='black')
  for y in range(box[3]-box[1]):d.line((0,y*48,scaled.width,y*48),fill=(255,0,255,110),width=1);d.text((1,y*48+13),str(y+box[1]),font=font,fill='white',stroke_width=1,stroke_fill='black')
  scaled.save(R/(name+'-'+('total' if sel is None else sel[0].replace(' ','_'))+'.png'))
print('rendu calques')
