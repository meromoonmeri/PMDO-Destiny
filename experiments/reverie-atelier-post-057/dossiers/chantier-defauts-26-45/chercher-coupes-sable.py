from PIL import Image,ImageDraw,ImageFont
import numpy as np,collections,json
im=np.asarray(Image.open('reverie-055-phase0.png').convert('RGB'));h,w=im.shape[:2];R,G,B=[im[:,:,i].astype(np.int16) for i in range(3)];sand=(R==248)&(G==216)&(B==152);grass=(G>=R)&(G>170)&(B<130)&(R>140)
hits=[]
for y in range(2,h-2):
 # Bas plat de sable directement adjacent à de l'herbe homogène, dans les deux sens.
 for d in (-1,1):
  v=sand[y]&grass[y+d];v=np.r_[False,v,False];edges=np.flatnonzero(v[1:]!=v[:-1]);
  for a,b in zip(edges[::2],edges[1::2]):
   if b-a<16:continue
   # Exclure limites écran et objets/sable isolé : conserver segments continus.
   if a<8 or b>w-8:continue
   hits.append((b-a,a,y,d))
hits.sort(reverse=True);chosen=[]
for n,x,y,d in hits:
 if any(abs(x-xx)<64 and abs(y-yy)<48 for _,xx,yy,_ in chosen):continue
 chosen.append((n,x,y,d))
 if len(chosen)>=64:break
print('lignes horizontales',len(hits),'groupes',len(chosen));print(chosen)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13);board=Image.new('RGB',(4*276,((len(chosen)+3)//4)*168),'#1f2420');draw=ImageDraw.Draw(board)
for i,(n,x,y,d) in enumerate(chosen):
 cx=x+n//2; crop=Image.fromarray(im[max(0,y-20):y+32,max(0,cx-44):cx+44]);crop=crop.resize((264,156),Image.Resampling.NEAREST);bx=(i%4)*276;by=(i//4)*168;board.paste(crop,(bx,by+12));draw.text((bx,by),f'{x},{y} longueur {n} sens {d}',font=font,fill='white')
board.save('candidats-coupes-sable.png');open('candidats-coupes-sable.json','w').write(json.dumps(chosen,indent=2))
