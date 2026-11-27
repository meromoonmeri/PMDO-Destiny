from pathlib import Path
from PIL import Image,ImageDraw
import math
p=Path(__file__).resolve().parent
ref=p/'reference-fire-house';frames=[]
for i in range(1,7):
 im=Image.open(ref/f'cheminee-source-{i:02}.png').convert('RGBA');w,h=im.size
 mask=Image.new('L',im.size);d=ImageDraw.Draw(mask)
 # Two original flues and the hood/hearth only: remove the original room behind.
 d.rectangle((16,3,29,44),fill=255);d.rectangle((40,3,52,44),fill=255)
 d.polygon([(6,38),(13,37),(55,37),(61,39),(65,45),(66,74),(64,76),(2,76),(1,74),(1,46),(3,41)],fill=255)
 old=im.getchannel('A');import PIL.ImageChops as C
 im.putalpha(C.multiply(old,mask))
 # Wall runs upward to the right. This preserves vertical uprights and tilts horizontal edges.
 slope=.55; out_h=h+math.ceil(slope*(w-1));shear=im.transform((w,out_h),Image.Transform.AFFINE,(1,0,0,slope,1,-slope*(w-1)),resample=Image.Resampling.NEAREST)
 shear=shear.resize((48,83),Image.Resampling.NEAREST);shear.save(p/f'cheminee-frame-{i:02}.png');frames.append(shear)
sheet=Image.new('RGBA',(48*6,83))
for i,im in enumerate(frames):sheet.alpha_composite(im,(i*48,0))
sheet.save(p/'cheminee-tilesheet.png')
# neutral display only
pre=[]
for im in frames:
 bg=Image.new('RGBA',(48,83),(31,29,55,255));bg.alpha_composite(im);pre.append(bg.convert('RGB').resize((288,498),Image.Resampling.NEAREST))
pre[0].save(p/'cheminee-animation.gif',save_all=True,append_images=pre[1:],duration=167,loop=0,disposal=2,optimize=False)
print('6 frames, 10 ticks 60Hz, 48x83')
