from pathlib import Path
import json,struct,io,sys,hashlib
from PIL import Image
sys.path.insert(0,'/home/user/PMU-Destiny-module');import pmu_core as c
T=Path('/home/user/chantier-apercu-reverie/travail');M=json.loads((T/'art/pmu/objets-source/fleurs-animees.json').read_text());ground=json.loads((T/'game/Data/Ground/pmu_fleurs_animees_dev.rsground').read_text(encoding='utf-8-sig'))['Object'];assert len(M)==10;decos=ground['Decorations'][0]['Anims'];assert len(decos)==10
for m,d in zip(M,decos):
 name=m['nom'];data=(T/'game/Content/Object'/f'{name}.dir').read_bytes();n=struct.unpack_from('<q',data)[0];assert len(data)==n+24 and struct.unpack_from('<iiii',data,n+8)==(32,32,0,2); assert hashlib.sha256(data).hexdigest()==m['sha256_dir']
 im=Image.open(io.BytesIO(data[8:8+n])).convert('RGBA');assert im.size==(64,32)
 inp=Image.open(T/'art/pmu/objets-source'/f'{name}.2.png').convert('RGBA');assert inp.size==(64,32)
 for i,num in enumerate([m['base_tile'],m['anim_tile']]):
  native=c.image_tile(m['source_set'],num);raw=inp.crop((i*32,0,(i+1)*32,32));assert raw.tobytes()==native.tobytes()
  expect=bytes(v for r,g,b,a in raw.getdata() for v in (r*a//255,g*a//255,b*a//255,a));assert im.crop((i*32,0,(i+1)*32,32)).tobytes()==expect
 anim=d['ObjectAnim'];assert anim['AnimIndex']==name and anim['FrameTime']==15 and anim['StartFrame']==-1 and anim['EndFrame']==-1
 print('PASS',name,'deux trames natives ; durée terrain',anim['FrameTime'])
assert len(ground['Layers'])==1 and len(ground['obstacles'])==40 and len(ground['obstacles'][0])==30
print('PASS 10 objets, PNG et .dir ; Ground dédié : données statiques cohérentes, pas de test moteur')
