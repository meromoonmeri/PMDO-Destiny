from PIL import Image
import numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent
names=['frame-generee-01.png','fontaine-classique-reverie-generation.png','frame-generee-03.png','frame-generee-02.png','frame-generee-03.png','fontaine-classique-reverie-generation.png']
frames=[]
for i,name in enumerate(names):
 im=Image.open(p/name).convert('RGBA').crop((85,55,940,895)).resize((72,72),Image.Resampling.NEAREST)
 a=np.array(im); r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16'); mag=(r>130)&(b>100)&(r-g>70)&(b-g>60);a[mag]=[0,0,0,0]
 if i==0:
  # Correct hue of generated water to the Reverie Town blues, retaining its light/dark pattern.
  r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16'); yy=np.indices(a.shape[:2])[0];water=(a[:,:,3]>0)&(yy>20)&(yy<55)&(g>r*1.25)&(b>r*1.25)
  for mask,col in [((r<60)&water,(88,176,200)),((r>=60)&(r<155)&water,(128,216,224)),((r>=155)&water,(152,232,240))]: a[mask,:3]=col
 f=Image.fromarray(a);f.save(p/f'Generee-assemblage-{i+1:02}.png');frames.append(f)
sheet=Image.new('RGBA',(72*len(frames),72));preview=[]
for i,f in enumerate(frames):
 sheet.alpha_composite(f,(72*i,0));bg=Image.new('RGBA',f.size,(31,29,55,255));bg.alpha_composite(f);preview.append(bg.convert('RGB').resize((432,432),Image.Resampling.NEAREST))
sheet.save(p/'Generee-planche-brouillon.png');preview[0].save(p/'Generee-animation-brouillon.gif',save_all=True,append_images=preview[1:],duration=180,loop=0,disposal=2,optimize=False)
