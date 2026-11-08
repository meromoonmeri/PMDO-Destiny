from PIL import Image,ImageDraw,ImageFont
import json,math
im=Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB');dat=json.load(open('/home/user/chantier-audit-chemins-quetes/coutures-sable-candidates-0.5.0.json'))
items=[]
for ori,arr in dat.items():
 for a in arr:
  x=a['x'];y=a['y'];n=a['longueur'];cx=x if ori=='vertical' else x+n//2;cy=y+n//2 if ori=='vertical' else y
  score=n*max(a['delta']-10,0);items.append((score,ori,x,y,n,cx,cy))
items.sort(reverse=True);keep=[]
for v in items:
 if all((v[5]-p[5])**2+(v[6]-p[6])**2>35**2 for p in keep):keep.append(v)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for page in range(math.ceil(len(keep)/40)):
 out=Image.new('RGB',(5*224,8*204),'#202a2a');d=ImageDraw.Draw(out)
 for i,(score,ori,x,y,n,cx,cy) in enumerate(keep[page*40:(page+1)*40]):
  ox=i%5*224;oy=i//5*204; crop=im.crop((cx-40,cy-35,cx+40,cy+35)).resize((208,182),Image.Resampling.NEAREST);out.paste(crop,(ox,oy+19));d.text((ox+2,oy+2),f'{page*40+i+1} ({cx},{cy}) {ori[0]}',font=f,fill='white')
 out.save(f'coutures-ordre-{page+1:02}.png')
print('total',len(items),'regroupés',len(keep));json.dump([{'id':i+1,'score':round(v[0],1),'sens':v[1],'x':v[2],'y':v[3],'longueur':v[4],'centre':[v[5],v[6]]} for i,v in enumerate(keep)],open('coutures-regroupees.json','w'),indent=2)
