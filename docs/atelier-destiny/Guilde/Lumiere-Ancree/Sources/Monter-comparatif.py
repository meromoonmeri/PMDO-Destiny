#!/usr/bin/env python3
"""Silent video of the original Grodoudou APNG beside Destiny's actual anchored-light frames."""
from pathlib import Path
from io import BytesIO
import base64,importlib.util,json,os,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont

import Lueur

S=Path(__file__).resolve().parent;O=S.parent;G=O.parent
W=Path.home()/'.cache/lumiere-braseros';F=Path(os.environ.get('DESTINY_ATLAS_STAGE',W/'Lueur-Tamisee-sans-video.html'));OUT=O/'Grodoudou-et-Destiny.webm';POSTER=O/'Grodoudou-et-Destiny.webp'
MARK='<script id="donnees" type="application/json">';FPS=20;N=192;SIZE=(1120,560);REGION=(84,42,494,299)
spec=importlib.util.spec_from_file_location('light',S/'Calibrer-depuis-Grodoudou.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def rgba(s):return Image.open(BytesIO(base64.b64decode(s.rsplit(',',1)[1]))).convert('RGBA')
def font(name,n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVu'+name+'.ttf',n)

def main():
 d=json.loads(F.read_text(encoding='utf8').split(MARK,1)[1].split('</script>',1)[0]);r=d['rooms'][2];l=d['lianes'][r['id']];phase=mod.old.image_layers(r,d,3);b,f,lut=phase;im=Image.fromarray(b)
 def shade(s):
  a=np.array(rgba(s));
  for c in range(3):a[:,:,c]=lut[c,a[:,:,c]]
  return Image.fromarray(a)
 im.alpha_composite(shade(l['s']));im.alpha_composite(Image.fromarray(f));im.alpha_composite(shade(l['t']));base=np.asarray(im.crop(REGION),dtype=np.float32)[:,:,:3]
 def crop(bit):
  x,y,s=bit;n=Image.new('RGBA',(r['w'],r['h']));n.paste(rgba(s),(x,y));a=np.asarray(n.crop(REGION),dtype=np.float32)/255;return a[:,:,:3],a[:,:,3:]
 lamps=[(crop(q['l']),crop(q['b']),q) for q in l['points']];small,amt=crop(l['reflets']);ap=Image.open(BytesIO(base64.b64decode(d['reference']['apng'].rsplit(',',1)[1])));braseros=[]
 for i in range(ap.n_frames):ap.seek(i);braseros.append(ap.convert('RGB'))
 assert len(braseros)==4
 canvas=Image.new('RGB',SIZE,'#151e1b');draw=ImageDraw.Draw(canvas);serif=font('Serif',33);mono=font('SansMono',13);smallf=font('Sans',14)
 draw.text((30,15),'RÉFÉRENCE   /   MODE NUIT',font=mono,fill='#a8c1af')
 draw.text((29,37),'Des braseros à une lueur tamisée',font=serif,fill='#f8ead1')
 draw.rounded_rectangle((28,89,543,505),radius=8,fill='#10112b',outline='#50574c',width=1)
 draw.rounded_rectangle((561,89,1091,505),radius=8,fill='#34261d',outline='#6a513c',width=1)
 draw.text((30,519),'GRODOUDOU  /  Deux braseros · boucle originale',font=smallf,fill='#f5dab0');draw.text((565,519),'DESTINY  /  Grand Salon · lueur à faible opacité',font=smallf,fill='#f5dab0')
 draw.text((579,468),'DÉTAIL DES POTEAUX PRÈS DES FENÊTRES',font=mono,fill='#d9bd9a')
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{SIZE[0]}x{SIZE[1]}','-framerate',str(FPS),'-i','-','-an','-c:v','libvpx-vp9','-threads','2','-row-mt','1','-deadline','good','-cpu-used','5','-crf','17','-b:v','0','-pix_fmt','yuv420p',str(OUT)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE);assert p.stdin is not None
 for n in range(N):
  t=n*1000/FPS;rgb=base.copy();g=[]
  for ((al,alpha),(cl,ca),q) in lamps:
   v=Lueur.level(t,q,d['lueur']);g.append(v);rgb+=(255-rgb)*al*alpha*v
  rgb=rgb*(1-amt)+255*small*amt
  for v,(_, (cl,ca),q) in zip(g,lamps):rgb+=(255-rgb)*cl*ca*v
  scene=canvas.copy();scene.paste(braseros[(n//2)%4],(82,105))
  detail=Image.fromarray(np.rint(rgb).astype(np.uint8)).resize((500,313),Image.Resampling.NEAREST)
  scene.paste(detail,(576,130))
  if n==0:scene.save(POSTER,'WEBP',lossless=True,method=5)
  p.stdin.write(scene.tobytes())
 p.stdin.close();assert p.wait()==0 and OUT.stat().st_size>50000
 print(f'PASS · vidéo de {N/FPS:g} s, {OUT.stat().st_size:,} o · APNG original et reflets Destiny',flush=True)
if __name__=='__main__':main()
