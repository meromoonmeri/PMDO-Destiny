from pathlib import Path
from PIL import Image
import numpy as np, math, zipfile
p=Path(__file__).resolve().parent
# Use the generated fountain phase 03: retain its silhouette, basin, roots and jet.
original=np.array(Image.open(p/'Generee-assemblage-03.png').convert('RGBA'))
r,g,b=original[:,:,:3].transpose(2,0,1).astype('int16')
# Remove residual dark magenta from the source background, not brown wood outlines.
fringe=(r>65)&(b>55)&(g<55)&(r-g>40)&(b-g>35)&(b>r*.65)
original[fringe]=[0,0,0,0]
r,g,b=original[:,:,:3].transpose(2,0,1).astype('int16'); yy,xx=np.indices((72,72))
water=(original[:,:,3]>0)&(b>r*1.10)&(g>r*1.10)&(yy>=29)&(yy<=50)
# Keep the jet and its central splash untouched; this avoids jumps in height.
jet=(xx>=31)&(xx<=41)&(yy<=35)
surface=water & ~jet
base=original.copy(); base[surface,:3]=(128,216,224)
# Fade ripple at pool edges to keep the line from popping as it reaches the border.
dist=np.sqrt((xx-36)**2+((yy-36)*2.15)**2)
frames=[]
for i in range(16):
 a=base.copy(); phase=i*16/16
 wave=np.mod(dist-phase,16)
 closeness=np.minimum(wave,16-wave)
 envelope=np.clip((16-dist)/5,0,1)*np.clip(dist/3,0,1)
 intensity=np.clip((1.5-closeness)/1.5,0,1)*envelope
 # Four subtle shades derived from the Reverie water palette, quantized for pixel art.
 for threshold,col in [(.15,(133,219,227)),(.40,(140,224,231)),(.70,(152,232,240))]:
  mask=surface & (intensity>=threshold);a[mask,:3]=col
 # One soft, cycling highlight in the unchanged jet silhouette.
 for y in range(23,34):
  for x in range(34,39):
   if jet[y,x] and original[y,x,3] and original[y,x,2]>original[y,x,0]*1.1:
    wave2=(y-i*.5)%8
    if wave2<1.3: a[y,x,:3]=(175,238,243)
 f=Image.fromarray(a);f.save(p/f'Polish-frame-{i+1:02}.png');frames.append(f)
sheet=Image.new('RGBA',(72*16,72));pv=[]
for i,f in enumerate(frames):
 sheet.alpha_composite(f,(i*72,0)); bg=Image.new('RGBA',(72,72),(31,29,55,255));bg.alpha_composite(f);pv.append(bg.convert('RGB').resize((432,432),Image.Resampling.NEAREST))
sheet.save(p/'Fontaine-polish-16-frames.png')
pv[0].save(p/'Fontaine-polish-boucle.gif',save_all=True,append_images=pv[1:],duration=80,loop=0,disposal=2,optimize=False)
with zipfile.ZipFile(p/'Fontaine-polish-frames.zip','w',zipfile.ZIP_DEFLATED) as z:
 for i in range(16): z.write(p/f'Polish-frame-{i+1:02}.png',f'frame-{i+1:02}.png')
 z.write(p/'Fontaine-polish-16-frames.png','planche-16-frames.png')
 z.write(p/'Fontaine-polish-boucle.gif','apercu-animation.gif')
print('16 frames 72x72, 80ms; 1.28 s loop')
