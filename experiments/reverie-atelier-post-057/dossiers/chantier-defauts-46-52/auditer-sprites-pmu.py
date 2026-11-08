"""Lit les sprites PMU historiques selon GraphicsManager.cs et SpriteSheet.cs.
Inventaire, pas une conversion PMDO ni une garantie des droits des images.
"""
import hashlib,io,json,struct,zipfile
from collections import Counter
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent; archive=R/'pmu_reference/sprites-pmu-2014-original.zip'
anims=['Idle','Walk','Attack','AttackArm','AltAttack','SpAttack','SpAttackCharge','SpAttackShoot','Hurt','Sleep']
directions=['Down','Left','Up','Right','DownLeft','UpLeft','UpRight','DownRight']
def i32(b,o):return struct.unpack_from('<i',b,o)[0]
def string(b,o):
 n=0;s=0
 while True:
  v=b[o];o+=1;n|=(v&127)<<s
  if not v&128:break
  s+=7;assert s<=28
 return b[o:o+n].decode('utf8'),o+n
all=[];hashes=Counter();errors=[]
with zipfile.ZipFile(archive) as z:
 names=sorted([n for n in z.namelist() if n.startswith('Sprites/') and n.endswith('.sprite')]);assert len(names)==751
 for name in names:
  b=z.read(name);sha=hashlib.sha256(b).hexdigest();hashes[sha]+=1
  try:
   count=i32(b,0);o=4;forms=[]
   for _ in range(count):
    nm,o=string(b,o);pos=i32(b,o);size=i32(b,o+4);o+=8;forms.append((nm,pos,size))
   head=o;result=[]
   for nm,pos,size in forms:
    off=head+pos;end=off+size;assert 0<=off<=end<=len(b)
    strips=[]
    for anim in anims:
     for direction in (directions if anim!='Sleep' else ['Down']):
      n=i32(b,off);ln=i32(b,off+4);off+=8;assert n>=0 and ln>=0 and off+ln<=end
      if ln:
       assert n>0
       image=Image.open(io.BytesIO(b[off:off+ln]));image.load();assert image.width%n==0
       strips.append({'animation':anim,'direction':direction,'frames':n,'frame_size':[image.width//n,image.height],'sha256_png':hashlib.sha256(b[off:off+ln]).hexdigest()})
      else:assert n==0
      off+=ln
    assert off==end,(off,end)
    result.append({'nom':nm,'strips':strips})
   all.append({'id':Path(name).stem,'sha256_source':sha,'taille_source':len(b),'formes':result})
  except Exception as e:errors.append({'nom':name,'erreur':str(e)})
summary={'source':'PMUniverse/PMU-Client c25c01f9879369647cd5a19731b2e4e5acd33e67','fichiers':len(names),'lus':len(all),'echecs':errors,'binaires_distincts':len(hashes),'taille_du_binaire_le_plus_repete':hashes.most_common(1)[0][1], 'formes':sum(len(x['formes']) for x in all),'bandes_png':sum(len(y['strips']) for x in all for y in x['formes']),'types_et_directions':dict(Counter(s['animation']+'/'+s['direction'] for x in all for y in x['formes'] for s in y['strips']))}
(R/'inventaire-sprites-pmu-2014.json').write_text(json.dumps({'resume':summary,'sprites':all},ensure_ascii=False,separators=(',',':')))
print(json.dumps(summary,ensure_ascii=False,indent=2));assert not errors
