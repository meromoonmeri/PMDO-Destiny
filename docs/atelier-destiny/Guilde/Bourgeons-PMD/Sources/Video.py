#!/usr/bin/env python3
"""Show the genuine outside and the same four rendered phases used by the atlas."""
import subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

O=Path(__file__).resolve().parents[1]
VIDEO=O/'Falaise-et-Bourgeons.webm';MP4=VIDEO.with_suffix('.mp4');POSTER=VIDEO.with_suffix('.webp')
S=(1120,560);FPS=24;FRAMES=240


def font(name,sz):
 return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVu'+name+'.ttf',sz)


def stage(src,dst,zoom,verdure=False):
 base=Image.new('RGB',S,'#17201c');d=ImageDraw.Draw(base);micro=font('SansMono',13);label=font('Sans',14)
 d.text((24,13),'EXPLORATEURS DU CIEL   /   G01P01C   /   NUIT',font=micro,fill='#b5c9b7')
 d.text((24,35),'De la lumière sur la pierre à la lueur des bourgeons',font=font('Serif',29),fill='#f6e7ce')
 for x,bg in [(24,'#111638'),(574,'#392a20')]:
  d.rounded_rectangle((x,84,x+522,502),radius=8,fill=bg,outline='#6b6453')
 d.text((24,520),'GRODOUDOU    /    Falaise et braseros d’origine',font=label,fill='#efd9b1')
 d.text((574,520),'DESTINY    /    Seuls les bourgeons émettent',font=label,fill='#efd9b1')
 if not zoom:
  base.paste(src,(46,89))
  large=dst.crop((58,30,518,313)).resize((500,308),Image.Resampling.NEAREST)
  base.paste(large,(585,132));d.text((592,466),'GRAND SALON · LUEUR TAMISÉE',font=micro,fill='#e0caa7')
 else:
  a=src.crop((121,83,218,178)).resize((388,380),Image.Resampling.NEAREST)
  base.paste(a,(91,94))
  if verdure:
   b=dst.crop((43,74,183,201)).resize((420,381),Image.Resampling.NEAREST);base.paste(b,(625,94))
   text='DÉTAIL  ·  ENROULEMENTS ET RONCE AU PIED'
  else:
   b=dst.crop((113,95,210,190)).resize((388,380),Image.Resampling.NEAREST);base.paste(b,(641,94))
   text='DÉTAIL  ·  REFLET SUR LA LIANE ET LE BOIS'
  d.text((42,484),'DÉTAIL  ·  REFLET SUR LA PIERRE',font=micro,fill='#d8c7a6')
  d.text((591,484),text,font=micro,fill='#e0caa7')
 return base


def build(archive,interior,verdure=False):
 p0=[Image.fromarray(a) for a in archive];p1=[Image.fromarray(a) for a in interior]
 frames=[[stage(a,b,zoom,verdure) for a,b in zip(p0,p1,strict=True)] for zoom in [False,True]]
 frames[0][2].save(POSTER,'WEBP',lossless=True,method=4)
 exe=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1120x560','-framerate',str(FPS),'-i','-']
 opts=['-map','0:v:0','-an','-pix_fmt','yuv420p']
 dll=exe+opts+['-c:v','libvpx-vp9','-threads','3','-row-mt','1','-cpu-used','6','-deadline','good','-crf','19','-b:v','0',str(VIDEO)]+opts+['-c:v','libx264','-threads','2','-preset','fast','-crf','18','-movflags','+faststart',str(MP4)]
 with subprocess.Popen(dll,stdin=subprocess.PIPE) as p:
  for n in range(FRAMES):
   p.stdin.write(frames[int(n>=96)][(n//4)%4].tobytes())
  p.stdin.close();assert p.wait()==0
 print('Vidéo intégrée : 10 s, 24 i/s · 4 images sources à 6 i/s · détail à 4 s.',flush=True)
