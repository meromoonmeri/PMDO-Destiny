from pathlib import Path
import gzip,json,sys,collections
from PIL import Image
R=Path('/home/user/chantier-corrections-bassin-53-54');sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
j=json.loads(gzip.decompress((R/'original-jeu.rsground.gz').read_bytes()).decode('utf-8-sig'))['Object'];layers=j['Layers'];cache={};counts=collections.Counter();
def tile(f):
 name=f.get('Sheet','');
 if not name:return None
 if name not in cache:cache[name]=SheetReader(R/'banques'/(name+'.tile'))
 xy=f['TexLoc'];return cache[name].get_tile(xy['X'],xy['Y'])
def render(box,sel=None,phase=0):
 x1,y1,x2,y2=box;im=Image.new('RGBA',((x2-x1)*8,(y2-y1)*8));
 for lay in layers:
  if sel is not None and lay['Name'] not in sel:continue
  for x in range(x1,x2):
   for y in range(y1,y2):
    v=lay['Tiles'][x][y]
    for sub in v.get('Layers',[]):
     fr=sub.get('Frames',[])
     if not fr:continue
     t=tile(fr[phase%len(fr)])
     if t:im.alpha_composite(t,(8*(x-x1),8*(y-y1)))
 return im
# Full selection matching earlier 800..1400,1850..2550; 8px aligned
box=(100,231,175,319)
im=render(box);im.resize((1200,1408),Image.Resampling.NEAREST).save(R/'avant-base-v057.png')
spots={'arbre-est':(162,241,174,255),'ombre-falaise-est':(162,264,174,279),'ombre-falaise-gauche-haut':(99,253,109,266),'ombre-falaise-gauche-milieu':(102,264,112,279),'ombre-falaise-gauche-bas':(102,278,112,293),'arbre-sud':(126,305,139,318),'eau':(139,258,145,264),'rive-droite':(147,249,158,264),'chemin-sud':(129,271,141,281)}
for name,box in spots.items():
 im=render(box);im.resize((im.width*5,im.height*5),Image.Resampling.NEAREST).save(R/(name+'-avant.png'))
 for lay in layers:
  records=[]
  for x in range(box[0],box[2]):
   for y in range(box[1],box[3]):
    v=lay['Tiles'][x][y]
    if v.get('Layers'):records.append([x,y,[(f.get('Sheet'),f.get('TexLoc')) for a in v['Layers'] for f in a.get('Frames',[])]])
  if records:(R/(name+'-'+lay['Name'].replace(' ','_')+'.json')).write_text(json.dumps(records,ensure_ascii=False))
print('rendu 15 banques, 9 détails')
for v in cache.values():v.close()
