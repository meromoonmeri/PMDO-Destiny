from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,json,math
im=np.array(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGBA'));alpha=im[:,:,3];mask=(alpha==0).astype('uint8');n,l,stats,_=cv2.connectedComponentsWithStats(mask,8);out=[]
for x,y,w,h,sz in stats[1:]:
 if not(1<=sz<=200 and w<=32 and h<=32 and x>3 and y>3 and x+w+3<1600 and y+h+3<4000):continue
 surround=im[y-3:y+h+3,x-3:x+w+3,:3];r=surround[:,:,0].astype(int);g=surround[:,:,1].astype(int);b=surround[:,:,2].astype(int);rock=(r>=115)&(r>g+5)&(g>90)&(g>b+5)&(b>40)&(b<180)
 out.append([int(x),int(y),int(w),int(h),int(sz),round(float(rock.mean()),2)])
out.sort(key=lambda q:(-q[5],q[1],q[0]));print('trous',len(out),'entourés falaise',sum(x[-1]>.45 for x in out));json.dump(out,open('trous-alpha-candidats.json','w'),indent=2)
base=Image.fromarray(im);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for page in range(math.ceil(len(out)/50)):
 o=Image.new('RGB',(5*200,10*174),'#202a2a');d=ImageDraw.Draw(o)
 for i,(x,y,w,h,n,score) in enumerate(out[page*50:(page+1)*50]):
  ox=i%5*200;oy=i//5*174;d.text((ox,oy),f'{page*50+i+1}: {x},{y} ({w}x{h})',font=f,fill='white');crop=base.crop((x-20,y-20,x+30,y+30));bg=Image.new('RGBA',crop.size,(255,0,255));bg.alpha_composite(crop);o.paste(bg.convert('RGB').resize((150,150),Image.Resampling.NEAREST),(ox,oy+20))
 o.save(f'trous-alpha-{page+1:02}.png')
