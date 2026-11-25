from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,gzip,json,sys,copy,hashlib,gc,shutil
R=Path('/home/user/chantier-raccords-et-pmu');D=Path('/home/user/chantier-deplacement-arbres-bassin');P=Path('/home/user/chantier-defauts-46-52/reprise-arrondie-27-51-52');sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
N='Reverie_Raccords_Arrondis_27_51_52_058';ref=np.array(Image.open('/home/user/apercu-global-reverie/reverie-etang-candidat-global.png').convert('RGBA'));cl=np.array(Image.open('/home/user/chantier-defauts-46-52/calques/02_Cliffs.png').convert('RGBA'))[:,:,3];met=np.array(Image.open('/home/user/chantier-chemins-reverie/metano-reference-sol-falaises.png').convert('RGBA'));arr=ref.copy()
src=ref[1074:1118,764:844];xx=np.arange(80);src=src[:,np.where(xx<40,xx+8,xx-8),:];mask=cl[586:630,1412:1492]==0;arr[586:630,1412:1492][mask]=src[mask]
for (x0,y0,x1,y1),(dx,dy) in [((1380,604,1440,648),(187,14)),((1466,604,1544,648),(186,30))]:
 assert not np.any(cl[y0:y1,x0:x1]);arr[y0:y1,x0:x1]=met[y0-dy:y1-dy,x0-dx:x1-dx]
arr[628:648,1430:1474]=met[595:615,1248:1292];arr[1752:1784,664:696]=met[640:672,584:616]
reader=SheetReader(P/(N+'.tile'));lookup={}
for xy in reader.positions:
 t=reader.get_tile(*xy)
 if t:lookup[t.tobytes()]=xy
patch={};zones={}
for tag,x0,y0,x1,y1 in [('escalier51',1376,584,1544,648),('chemin27',664,1752,696,1784)]:
 count=0
 for cy in range(y0//8,(y1+7)//8):
  for cx in range(x0//8,(x1+7)//8):
   old=ref[cy*8:cy*8+8,cx*8:cx*8+8];new=arr[cy*8:cy*8+8,cx*8:cx*8+8];m=np.any(old!=new,axis=2)
   if m.any():
    p=np.zeros((8,8,4),np.uint8);p[m]=new[m];key=p.tobytes();assert key in lookup,('not previous native patch',tag,cx,cy);patch[cx,cy]=lookup[key];count+=1
 zones[tag]=count
print('Raccords correspondent aux tuiles antérieures:',zones);assert zones=={'escalier51':134,'chemin27':13};shutil.copy2(P/(N+'.tile'),R/'banques'/f'{N}.tile')
logs=[]
for name in ('reverie_etang.rsground.gz','reverie_etang_Dev.rsground.gz'):
 orig=json.loads(gzip.decompress((R/'sauvegarde'/('v057-'+name)).read_bytes()).decode('utf-8-sig'));doc=json.loads(gzip.decompress((D/'candidat/payload'/name).read_bytes()).decode('utf-8-sig'));lo=orig['Object']['Layers'];lc=doc['Object']['Layers'];assert [x['Name'] for x in lo]==[x['Name'] for x in lc]
 # Prior pixel work at these cells must not be overwritten; all 11 layers match original.
 for x,y in patch:
  for a,b in zip(lo,lc):assert a['Tiles'][x][y]==b['Tiles'][x][y],(name,a['Name'],x,y)
 changed=[];base=next(l['Tiles'] for l in lc if l['Name']=='Base')
 for (x,y),(ix,iy) in sorted(patch.items()):
  old=copy.deepcopy(base[x][y]);new=copy.deepcopy(old)
  if not new:new={'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1}
  new.setdefault('Layers',[]).append({'Frames':[{'Sheet':N,'TexLoc':{'X':ix,'Y':iy}}],'FrameLength':60});base[x][y]=new;changed.append({'x':x,'y':y,'avant':old,'apres':new})
 raw=b'\xef\xbb\xbf'+json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode()
 with (R/'candidat/payload'/name).open('wb') as f:
  with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:z.write(raw)
 logs.append({'carte':name,'modifications':changed});del doc,orig,lo,lc,base,raw;gc.collect()
(R/'journal-raccords.json').write_text(json.dumps({'zones':zones,'cartes':logs},ensure_ascii=False,indent=2))
for tag,(x0,y0,x1,y1) in {'chemin27':(635,1728,770,1845),'escalier51':(1368,565,1560,665)}.items():
 a=Image.fromarray(ref[y0:y1,x0:x1]);b=Image.fromarray(arr[y0:y1,x0:x1]);scale=3;a=a.resize((a.width*scale,a.height*scale),Image.Resampling.NEAREST);b=b.resize(a.size,Image.Resampling.NEAREST);im=Image.new('RGB',(a.width*2,a.height+28),'white');d=ImageDraw.Draw(im);d.text((5,6),'Avant',fill='black');d.text((a.width+5,6),'Candidat',fill='black');im.paste(a,(0,28),a);im.paste(b,(a.width,28),b);im.save(R/(tag+'-avant-apres.png'))
reader.close();print('Sauvegarde et candidats créés')
