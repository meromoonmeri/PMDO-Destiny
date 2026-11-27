from PIL import Image,ImageDraw
import numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent
for nom in ['cafe-spinda','accueil-missions','reserve-guilde']:
 im=Image.open(p/(nom+'-generation.png')).convert('RGBA'); a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');mask=(r>155)&(b>130)&(g<110)&(r-g>80)&(b-g>70);a[mask,3]=0
 im=Image.fromarray(a);im=im.crop(im.getbbox());im.thumbnail((112,104),Image.Resampling.LANCZOS);a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');bad=(r>135)&(b>100)&(r-g>65)&(b-g>50);a[bad,3]=0;a[:,:,3]=np.where(a[:,:,3]>=140,255,0).astype('uint8');a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a);im.save(p/(nom+'-sprite.png'));im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(p/(nom+'-zoom.png'));print(nom,im.size)
# Grande carte murale de l'atlas existant : géographie respectée, aucune redessinée par IA.
w,h=132,92;can=Image.new('RGBA',(w,h));d=ImageDraw.Draw(can)
d.polygon([(3,4),(w-4,4),(w-2,7),(w-3,h-4),(w-7,h-2),(4,h-2),(2,h-5),(2,7)],fill='#654529');d.polygon([(3,3),(w-5,3),(w-3,5),(w-4,h-4),(w-7,h-3),(4,h-3),(2,h-5)],fill='#d5a85f');d.rectangle((5,5,w-6,h-6),fill='#f4d7a1')
src=Image.open('/home/user/PMDO-Destiny-guilde/Atlas-des-Continents-Destiny/Carte-des-Continents-Destiny-5560x3660.png').convert('RGB');src=src.resize((w-14,h-15),Image.Resampling.LANCZOS).quantize(colors=64).convert('RGBA');can.alpha_composite(src,(7,7));d=ImageDraw.Draw(can)
for x in [10,w-11]:
 d.rectangle((x-1,3,x+1,5),fill='#775238');d.point((x-1,3),fill='#ffebae');d.point((x+1,6),fill='#4f3423')
can.save(p/'carte-monde-grande-sprite.png');can.resize((w*4,h*4),Image.Resampling.NEAREST).save(p/'carte-monde-grande-zoom.png');print('carte',can.size)
