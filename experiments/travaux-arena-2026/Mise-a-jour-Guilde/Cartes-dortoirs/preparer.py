from PIL import Image
import numpy as np, math,json
from pathlib import Path
p=Path(__file__).resolve().parent;items=[]
for name,label in [('continent','Carte des terres · style PMD'),('iles','Carte des îles · style PMD')]:
 im=Image.open(p/f'carte-{name}-generation.png').convert('RGBA');a=np.array(im);rgb=a[:,:,:3].astype('int16');r,g,b=rgb.transpose(2,0,1);bg=np.median([rgb[2,2],rgb[-3,2],rgb[2,-3],rgb[-3,-3]],axis=0);d=np.max(np.abs(rgb-bg),axis=2);key=(d<45)|((r>110)&(b>80)&(r-g>55)&(b-g>40));a[key]=[0,0,0,0];im=Image.fromarray(a);im=im.crop(im.getbbox()).resize((30,22),Image.Resampling.NEAREST)
 for side in ['gauche','droite']:
  h=22+math.ceil(.5*29)
  # y_out = y + .5 * (29-x) for left, + .5*x for right
  matrix=(1,0,0,.5,1,-.5*29) if side=='gauche' else (1,0,0,-.5,1,0)
  skew=im.transform((30,h),Image.Transform.AFFINE,matrix,resample=Image.Resampling.NEAREST)
  filename=f'carte-{name}-{side}.png';skew.save(p/filename);skew.resize((300,h*10),Image.Resampling.NEAREST).save(p/f'carte-{name}-{side}-zoom.png')
  items.append({'id':f'carte-dortoir-{name}-{side}','label':f'{label} · mur {side}','file':filename,'w':30,'h':h})
(p/'index.json').write_text(json.dumps(items,ensure_ascii=False,indent=2));print(items)
