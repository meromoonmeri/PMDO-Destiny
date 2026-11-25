import cv2,numpy as np,json
from PIL import Image,ImageDraw,ImageFont
im=np.array(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB')); target=im[2928:2944,76:124];print('match',flush=True)
res=cv2.matchTemplate(im,target,cv2.TM_SQDIFF_NORMED)
# grass fraction underneath at offsets y+20..30 using color mask and integral.
g=im[:,:,1].astype('int16');r=im[:,:,0].astype('int16');b=im[:,:,2].astype('int16');grass=((g>r+2)&(g>170)&(b<160)&(r>120)).astype('uint8');integ=cv2.integral(grass)
ys=np.arange(res.shape[0]-34);xs=np.arange(res.shape[1]);counts=integ[ys[:,None]+34,xs[None,:]+48]-integ[ys[:,None]+22,xs[None,:]+48]-integ[ys[:,None]+34,xs[None,:]]+integ[ys[:,None]+22,xs[None,:]]
score=res[:len(ys)].copy();score[counts<300]=1
out=[]
for _ in range(24):
 v,_,loc,_=cv2.minMaxLoc(score)
 if v>.1:break
 x,y=loc;out.append((x,y,round(v,6),int(counts[y,x])));cv2.rectangle(score,(max(0,x-60),max(0,y-60)),(min(score.shape[1]-1,x+60),min(score.shape[0]-1,y+60)),1,-1)
print(out)
can=Image.new('RGB',(4*260,((len(out)+3)//4)*280),'#1e2620');d=ImageDraw.Draw(can)
for i,(x,y,score,g) in enumerate(out):
 bx=(i%4)*260;by=(i//4)*280;crop=Image.fromarray(im[max(0,y-8):y+56,max(0,x-8):x+56]);crop=crop.resize((240,240),Image.Resampling.NEAREST);can.paste(crop,(bx,by+28));d.text((bx,by+3),f'{i+1}: {x},{y} e={score:.4f}',fill='white')
can.save('candidats-terminaisons.png')
