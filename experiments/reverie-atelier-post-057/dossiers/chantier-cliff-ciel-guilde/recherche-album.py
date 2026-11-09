import requests,concurrent.futures,json,io
from bs4 import BeautifulSoup
from PIL import Image,ImageDraw
from pathlib import Path
R=Path('/home/user/chantier-cliff-ciel-guilde');base='https://projectpokemon.org/home/gallery/album/878-map-backgrounds/'
items={}
for page in range(1,8):
 r=requests.get(base,params={'page':page},timeout=30);s=BeautifulSoup(r.text,'html.parser');
 for a in s.select('a.ipsImageBlock__main[href*="/gallery/image/"]'):
  im=a.find('img');
  if im and im.get('src') and im.get('alt'):items[im['alt']]={'url':a['href'].split('?')[0],'thumb':im['src']}
 print('page',page,'found',len(items))
items={k:v for k,v in items.items() if k.startswith(('V','T'))}; (R/'index-fonds.json').write_text(json.dumps(items,indent=2))
def pull(item):
 name,d=item
 try:
  r=requests.get(d['thumb'],timeout=20);r.raise_for_status(); im=Image.open(io.BytesIO(r.content)).convert('RGB');return name,im
 except Exception as e:return name,None
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex: data=list(ex.map(pull,items.items()))
data=[(n,i) for n,i in data if i];print('downloaded',len(data));
for offset in range(0,len(data),60):
 sub=data[offset:offset+60];out=Image.new('RGB',(5*170,((len(sub)+4)//5)*118),'#19212b');d=ImageDraw.Draw(out)
 for i,(n,im) in enumerate(sub):
  x=(i%5)*170;y=(i//5)*118; im.thumbnail((160,91),Image.Resampling.NEAREST);out.paste(im,(x,y+20));d.text((x+1,y+2),n,fill='white')
 out.save(R/f'planche-recherche-{offset//60+1}.jpg',quality=92)
