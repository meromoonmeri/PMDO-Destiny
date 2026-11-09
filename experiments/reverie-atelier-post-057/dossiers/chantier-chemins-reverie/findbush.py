import numpy as np,cv2
from PIL import Image,ImageDraw
im=np.array(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB'));tpl=im[568:575,80:87];r=cv2.matchTemplate(im,tpl,cv2.TM_SQDIFF_NORMED);m=(r<0.00001);ys,xs=np.where(m);out=[]
for x,y in zip(xs,ys):
 if all((int(x)-a)**2+(int(y)-b)**2>100 for a,b in out):out.append((int(x),int(y)))
print(out[:100],len(out));o=Image.new('RGB',(6*150,((len(out)+5)//6)*154),'#202a2a');d=ImageDraw.Draw(o)
for i,(x,y) in enumerate(out):
 if i>=60:break
 ox=i%6*150;oy=i//6*154;d.text((ox,oy),f'{i+1} {x},{y}',fill='white');o.paste(Image.fromarray(im[y-12:y+20,x-12:x+20]).resize((128,128),Image.Resampling.NEAREST),(ox,oy+18))
o.save('herbes-correspondances.png')
