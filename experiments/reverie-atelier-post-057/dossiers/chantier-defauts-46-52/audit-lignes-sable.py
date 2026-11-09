from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
im=np.asarray(Image.open('reverie-057-phase0.png').convert('RGB'));h,w=im.shape[:2];r,g,b=[im[:,:,i].astype(np.int16) for i in range(3)];sand=(r>=232)&(g>=175)&(g<225)&(b>=112)&(b<175)&(r>g+15);grass=(g>=r)&(g>170)&(r>140)&(b<125)
upper=np.zeros((h,w),bool)
for n in ['02_Cliffs','03_River','05_Objects_Under','07_Objects','08_Objects_Anim','09_Objects_Over']:
 upper|=np.asarray(Image.open('calques/'+n+'.png').convert('RGBA'))[:,:,3]>0
cand=[]
for axis in ['v','h']:
 if axis=='v':
  a=(grass[:,:-1]&sand[:,1:])|(sand[:,:-1]&grass[:,1:]);a &= ~(upper[:,:-1]|upper[:,1:]); a=a.T
 else:
  a=(grass[:-1,:]&sand[1:,:])|(sand[:-1,:]&grass[1:,:]);a &= ~(upper[:-1,:]|upper[1:,:])
 for fixed,line in enumerate(a):
  edges=np.flatnonzero(np.diff(np.r_[False,line,False].astype(np.int8)))
  for lo,hi in zip(edges[::2],edges[1::2]):
   n=hi-lo
   if n>=10:
    x,y=(fixed,lo) if axis=='v' else (lo,fixed)
    if 48<x<w-48 and 48<y<h-48:cand.append((int(n),int(x),int(y),axis))
cand.sort(reverse=True);out=[]
for n,x,y,axis in cand:
 if any(abs(x-X)<70 and abs(y-Y)<70 for _,X,Y,_ in out):continue
 out.append((n,x,y,axis))
 if len(out)==45:break
Path('audit-nouveaux-candidats.json').write_text(json.dumps({'methode':'rupture herbe/sable direct >=10px, indices sans preuve artistique','candidats':out},ensure_ascii=False,indent=2))
W,H=210,190;board=Image.new('RGB',(W*5,((len(out)+4)//5)*H),'#151b18');d=ImageDraw.Draw(board)
for i,(n,x,y,axis) in enumerate(out):
 X=(i%5)*W;Y=(i//5)*H;d.text((X+3,Y+3),f'{i+1}: {x},{y} {axis} {n}px',fill='white');p=Image.fromarray(im[y-26:y+42,x-36:x+36]).resize((180,170),Image.Resampling.NEAREST);board.paste(p,(X,Y+18))
board.save('audit-nouveaux-candidats.png');print('segments',len(cand),'groupes',len(out));print(out)
