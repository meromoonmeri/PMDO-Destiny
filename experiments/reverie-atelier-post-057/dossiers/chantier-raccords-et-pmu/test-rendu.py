from pathlib import Path
from PIL import Image
import gzip,json,sys,numpy as np
R=Path('/home/user/chantier-raccords-et-pmu');D=Path('/home/user/chantier-deplacement-arbres-bassin');F=Path('/home/user/chantier-corrections-bassin-55');P=Path('/home/user/chantier-corrections-bassin-53-54');sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
j=json.loads(gzip.decompress((R/'candidat/payload/reverie_etang.rsground.gz').read_bytes()).decode('utf-8-sig'))['Object'];layers=j['Layers'];sheets={}
def get(f):
 n=f.get('Sheet','');
 if not n:return None
 if n not in sheets:
  ps=[x/'banques'/f'{n}.tile' for x in (R,D,F,P)];p=next((p for p in ps if p.exists()),None);assert p,n;sheets[n]=SheetReader(p)
 t=f['TexLoc'];return sheets[n].get_tile(t['X'],t['Y'])
def render(box,phase):
 x0,y0,x1,y1=box;im=Image.new('RGBA',((x1-x0)*8,(y1-y0)*8))
 for l in layers:
  for x in range(x0,x1):
   for y in range(y0,y1):
    for sub in l['Tiles'][x][y].get('Layers',[]):
     f=sub.get('Frames',[])
     if f:
      t=get(f[phase%len(f)])
      if t:im.alpha_composite(t,((x-x0)*8,(y-y0)*8))
 return np.array(im)
ref=np.array(Image.open('/home/user/apercu-global-reverie/reverie-etang-candidat-global.png').convert('RGBA'));arr=ref.copy();cl=np.array(Image.open('/home/user/chantier-defauts-46-52/calques/02_Cliffs.png').convert('RGBA'))[:,:,3];met=np.array(Image.open('/home/user/chantier-chemins-reverie/metano-reference-sol-falaises.png').convert('RGBA'));src=ref[1074:1118,764:844];xx=np.arange(80);src=src[:,np.where(xx<40,xx+8,xx-8),:];mask=cl[586:630,1412:1492]==0;arr[586:630,1412:1492][mask]=src[mask]
for (x0,y0,x1,y1),(dx,dy) in [((1380,604,1440,648),(187,14)),((1466,604,1544,648),(186,30))]:arr[y0:y1,x0:x1]=met[y0-dy:y1-dy,x0-dx:x1-dx]
arr[628:648,1430:1474]=met[595:615,1248:1292];arr[1752:1784,664:696]=met[640:672,584:616]
for b in [(172,73,193,81),(83,219,87,223)]:
 x0,y0,x1,y1=b;expect=arr[y0*8:y1*8,x0*8:x1*8]
 for phase in range(4):
  out=render(b,phase);assert np.array_equal(out,expect),(b,phase,np.count_nonzero(np.any(out!=expect,axis=2)))
 print('rendu 4 phases PASS',b)
