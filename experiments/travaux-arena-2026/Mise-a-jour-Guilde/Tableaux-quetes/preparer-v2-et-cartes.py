from PIL import Image,ImageDraw
import numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent
# Sauvegarde de la V1 : elle reste intacte et les PNG de génération originaux sont conservés.
for nom,box in [('secours',(211,224,985,689)),('exploration',(177,220,1020,692))]:
 im=Image.open(p/(nom+'-mural-generation.png')).convert('RGBA');ed=Image.open(p/(nom+'-papiers-eos-generation.png')).convert('RGBA');assert im.size==ed.size
 im.paste(ed.crop(box),box[:2]);im.save(p/(nom+'-mural-v2-composition.png'))
 a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');mask=(r>155)&(b>130)&(g<100)&(r-g>90)&(b-g>75);a[mask,3]=0
 im=Image.fromarray(a);im=im.crop(im.getbbox());im.thumbnail((64,46),Image.Resampling.LANCZOS);a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');bad=(r>135)&(b>100)&(r-g>65)&(b-g>50);a[bad,3]=0;a[:,:,3]=np.where(a[:,:,3]>=140,255,0).astype('uint8');a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a)
 im.save(p/(nom+'-mural-v2-sprite.png'));im.resize((im.width*6,im.height*6),Image.Resampling.NEAREST).save(p/(nom+'-mural-v2-zoom.png'))
# Deux cartes épinglées indépendantes, basées sur les planches existantes de l'atlas Destiny.
base=Path('/home/user/PMDO-Destiny-guilde/Atlas-des-Continents-Destiny')
for name,src,size in [('monde','Carte-des-Continents-Destiny-5560x3660.png',(76,52)),('reverie','Ile-de-Reverie.png',(54,54))]:
 w,h=size; canvas=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(canvas)
 # Bords irréguliers du parchemin, silhouettes franches en pixels.
 d.polygon([(3,3),(w-5,3),(w-3,5),(w-3,h-4),(w-5,h-2),(4,h-2),(2,h-4),(2,5)],fill='#72502c')
 d.polygon([(3,2),(w-5,2),(w-3,4),(w-4,h-4),(w-7,h-3),(4,h-3),(2,h-5),(3,5)],fill='#e2ba75')
 d.rectangle((4,4,w-5,h-5),fill='#f5d9a1')
 im=Image.open(base/src).convert('RGB');im=im.resize((w-10,h-11),Image.Resampling.LANCZOS).quantize(colors=48,method=Image.Quantize.MEDIANCUT).convert('RGBA');canvas.alpha_composite(im,(5,6))
 d=ImageDraw.Draw(canvas);d.line((4,4,w-5,4),fill='#ac7d43');d.line((4,h-5,w-5,h-5),fill='#ba8c4e')
 for x in (8,w-9):
  d.point((x+1,5),fill='#4e3421');d.point((x,3),fill='#f5daa0');d.point((x,4),fill='#755031')
 canvas.save(p/('carte-'+name+'-sprite.png'));canvas.resize((w*6,h*6),Image.Resampling.NEAREST).save(p/('carte-'+name+'-zoom.png'))
 print(name,size)
