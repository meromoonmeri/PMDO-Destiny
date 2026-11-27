from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, math
r=Path(__file__).parent;p=r.parent
f=p/'Design-unifie/Reprise-vues-POLISH-ESSAI.png';a=np.array(Image.open(f).convert('RGBA'));alpha=a[:,:,3];rgb=a[:,:,:3];pixels=rgb[alpha>0];side=int(math.ceil(math.sqrt(len(pixels))));samples=np.zeros((side,side,3),dtype=np.uint8);samples.reshape(-1,3)[:len(pixels)]=pixels;samples.reshape(-1,3)[len(pixels):]=pixels[:side*side-len(pixels)]
for n in [15,24,48,64,96]:
 pal=Image.fromarray(samples).quantize(colors=n,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
 quant=Image.fromarray(rgb,'RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGB');arr=np.array(quant);out=np.dstack((arr,alpha));Image.fromarray(out).save(r/f'Walk-nettete-{n}-ESSAI.png')
 colors=out[out[:,:,3]>0,:3];e=np.abs(colors.astype(int)-pixels.astype(int));print(n,'couleurs',len(np.unique(colors,axis=0)),'erreur rgb moyenne',round(e.mean(),2),'max',int(e.max()),'alpha identique',np.array_equal(out[:,:,3],alpha))
ims=[Image.open(f),*[Image.open(r/f'Walk-nettete-{n}-ESSAI.png') for n in [15,24,48,96]]]
out=Image.new('RGB',(5*256,4*448),'#c7d9bf');d=ImageDraw.Draw(out)
for y,row in enumerate([0,1,4,7]):
 for x,im in enumerate(ims):
  a=im.crop((64,row*112,128,(row+1)*112)).resize((256,448),Image.Resampling.NEAREST);out.paste(a,(x*256,y*448),a)
out.save(r/'controle-nettete.png')
