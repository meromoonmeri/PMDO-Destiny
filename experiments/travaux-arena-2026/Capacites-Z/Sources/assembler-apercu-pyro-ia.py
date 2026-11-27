from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, subprocess, tempfile
R=Path('/home/user/Capacites-Z/Prototypes/Pyro-Explosion-Cataclysmique/Generation-PMDO')
names=['image-01.png','image-02.png','image-02b.png','image-03.png','image-04.png']
frames=[]
for name in names:
    im=Image.open(R/name).convert('RGB').resize((64,64),Image.Resampling.NEAREST)
    a=np.array(im); mask=(a[:,:,0]>180)&(a[:,:,2]>130)&(a[:,:,1]<115)
    rgba=np.concatenate([a,np.where(mask,0,255).astype('uint8')[:,:,None]],axis=2)
    frames.append(Image.fromarray(rgba,'RGBA'))
    frames[-1].save(R/(name.replace('.png','-transparent-64.png')))
sheet=Image.new('RGBA',(64*len(frames),64))
for i,f in enumerate(frames):sheet.alpha_composite(f,(64*i,0))
sheet.save(R/'Pyro-IA-explosion.None.png')
bg=Image.open('/home/user/.cache/destiny-test/fond-illustration.png').convert('RGBA')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
# Video repeats a single illustrative composition; this is not a game recording.
with tempfile.TemporaryDirectory() as tmp:
    index=0
    sequence=[(None,9),(0,3),(1,4),(2,4),(3,5),(4,5),(None,20)]
    for rep in range(3):
        for k,count in sequence:
            canvas=bg.copy()
            if k is not None:
                v=frames[k].resize((128,128),Image.Resampling.NEAREST)
                canvas.alpha_composite(v,(256,214))
            d=ImageDraw.Draw(canvas)
            d.rectangle((0,0,640,28),fill=(9,19,24,230))
            d.text((10,6),'MAQUETTE : effet IA sur capture fixe — pas en jeu',font=font,fill=(255,241,205))
            for _ in range(count):
                canvas.convert('RGB').save(Path(tmp)/f'{index:04d}.png');index+=1
    subprocess.run(['ffmpeg','-v','error','-framerate','30','-i',str(Path(tmp)/'%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-movflags','+faststart','-y',str(R/'apercu-pyro-poses-ia.mp4')],check=True)
print('done',len(frames),'generated frames')
