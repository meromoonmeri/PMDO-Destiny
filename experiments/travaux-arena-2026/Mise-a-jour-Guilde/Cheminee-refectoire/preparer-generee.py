from pathlib import Path
from PIL import Image
import numpy as np, math
p=Path(__file__).resolve().parent
files=['cheminee-generee.png','cheminee-generee-flammes-02.png','cheminee-generee-flammes-03.png']
a=[];masks=[]
yy,xx=np.indices((56,48));zone=(((xx>=15)&(xx<=23)&(yy>=37)&(yy<=46))|((xx>=29)&(xx<=37)&(yy>=33)&(yy<=42)))
for f in files:
 ar=np.array(Image.open(p/f).convert('RGBA').resize((48,56),Image.Resampling.NEAREST));rgb=ar[:,:,:3].astype('int16');r,g,b=rgb.transpose(2,0,1);key=((r>130)&(b>105)&(r-g>60)&(b-g>45))|((r>65)&(b>55)&(g<75)&(r-g>35)&(b-g>30)&(b>r*.65));ar[key]=[0,0,0,0];fire=zone & (r>105)&(r>g*1.3)&(b<100)&(g<210);a.append(ar);masks.append(fire)
# Only the generated flame pixels change, the generated masonry stays fixed.
base=a[1].copy();union=np.logical_or.reduce(masks);base[union]=[34,25,20,255]
frames=[]
for i in [0,1,0,2]:
 ar=base.copy();ar[masks[i]]=a[i][masks[i]];im=Image.fromarray(ar)
 # Correct the remaining ~0.3 slope difference: facade rises with the wall, uprights stay vertical.
 slope=.30;h=56+math.ceil(47*slope);im=im.transform((48,h),Image.Transform.AFFINE,(1,0,0,slope,1,-slope*47),resample=Image.Resampling.NEAREST)
 frames.append(im)
w,h=frames[0].size
for i,im in enumerate(frames,1): im.save(p/f'generee-image-{i:02}.png')
s=Image.new('RGBA',(w*len(frames),h));pv=[]
for i,im in enumerate(frames):
 s.alpha_composite(im,(i*w,0));bg=Image.new('RGBA',(w,h),(31,29,55,255));bg.alpha_composite(im);pv.append(bg.convert('RGB').resize((w*6,h*6),Image.Resampling.NEAREST))
s.save(p/'generee-tilesheet.png');pv[0].save(p/'generee-animation.gif',save_all=True,append_images=pv[1:],loop=0,duration=170,disposal=2,optimize=False)
print('size',w,h)
