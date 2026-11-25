from pathlib import Path
from PIL import Image
import gzip,json,sys
P=Path('/home/user/chantier-corrections-bassin-53-54');F=Path('/home/user/chantier-corrections-bassin-55');sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
o=json.loads(gzip.decompress((F/'candidat/payload/reverie_etang.rsground.gz').read_bytes()).decode('utf-8-sig'))['Object'];L={l['Name']:l['Tiles'] for l in o['Layers']};rs={}
def get(f):
 n=f.get('Sheet','');
 if not n:return None
 if n not in rs:rs[n]=SheetReader((F/'banques' if (F/'banques'/(n+'.tile')).exists() else P/'banques')/(n+'.tile'))
 p=f['TexLoc'];return rs[n].get_tile(p['X'],p['Y'])
def imcell(layer,x,y):
 out=Image.new('RGBA',(8,8))
 for s in L[layer][x][y].get('Layers',[]):
  if s.get('Frames'):
   im=get(s['Frames'][0]);
   if im:out.alpha_composite(im)
 return out
r=SheetReader(P/'banques/Reverie_Geo_08_Batiments_objets.tile');colors={(128,112,88,255),(152,176,40,255),(128,152,40,255),(104,136,32,255)}
trees=[('ouest-haut',97,253),('ouest-milieu',97,262),('ouest-bas',98,272),('est',158,263)]
for label,x0,y0 in trees:
 print('\n',label,'pos',x0,y0)
 for dx,dy in [(0,0),(-1,-1),(-2,-1),(-3,-1),(0,-2),(0,-3),(-1,-3)]:
  n=0
  for sx in range(124,134):
   for sy in range(15,24):
    t=r.get_tile(sx,sy)
    if t is None:continue
    x=x0+(sx-124)+dx;y=y0+(sy-15)+dy;cl=imcell('Cliffs',x,y)
    for a,b in zip(t.get_flattened_data(),cl.get_flattened_data()):
     if a in colors and b[3]==255:n+=1
  print((dx,dy),n,end='; ')
 print()
