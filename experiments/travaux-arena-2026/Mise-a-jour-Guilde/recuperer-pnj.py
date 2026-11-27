import concurrent.futures,requests,xml.etree.ElementTree as ET,json
from pathlib import Path
R=Path(__file__).parent/'personnages-sources';chars=[(40,'Grodoudou'),(441,'Pijako'),(399,'Keunotor'),(294,'Ramboum'),(341,'Écrapince'),(192,'Héliatronc'),(453,'Cradopaud'),(50,'Taupiqueur'),(51,'Triopikeur'),(358,'Éoko'),(25,'Pikachu'),(158,'Kaiminus'),(133,'Évoli'),(447,'Riolu')]
def fetch(a):
 num,name=a;out=R/f'{num:04d}';out.mkdir(exist_ok=True)
 base=f'https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/sprite/{num:04d}/'
 try:
  for fn in ['AnimData.xml','Idle-Anim.png','credits.txt']:
   r=requests.get(base+fn,timeout=30);r.raise_for_status();(out/fn).write_bytes(r.content)
  e=ET.parse(out/'AnimData.xml').getroot();node=next(x for x in e.find('Anims') if x.findtext('Name')=='Idle');
  return {'id':num,'label':name,'w':int(node.findtext('FrameWidth')),'h':int(node.findtext('FrameHeight')),'durations':[int(x.text) for x in node.findall('Durations/Duration')],'copy':node.findtext('CopyOf')}
 except Exception as e:return {'id':num,'label':name,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:a=list(ex.map(fetch,chars))
(R/'index.json').write_text(json.dumps(a,ensure_ascii=False,indent=2));print(json.dumps(a,ensure_ascii=False,indent=2))
