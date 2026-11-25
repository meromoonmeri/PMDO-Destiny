#!/usr/bin/env python3
"""A small video vignette using the exact lighting fields and animated flag frames from the atelier."""
from pathlib import Path
import importlib.util,subprocess
from PIL import Image,ImageDraw,ImageFont
import numpy as np

S=Path(__file__).resolve().parent;O=S.parent
spec=importlib.util.spec_from_file_location('relief',S/'Enrouler-et-eclairer.py');fx=importlib.util.module_from_spec(spec);spec.loader.exec_module(fx)
F=Path('/usr/share/fonts/truetype/dejavu');BOX=(66,10,510,252); SIZE=(1280,720); FPS=12; DUREE=12

def ft(f,size):return ImageFont.truetype(str(F/f),size)

def main():
 r=fx.data_base();b=r['rooms'][2];calques=O/'Calques-nuit/03-grand_salon';B,Fo,lut=fx.old.image_layers(b,r,3)
 base=Image.fromarray(B);base.alpha_composite(Image.fromarray(Fo));layer=np.array(Image.open(calques/'Lianes-tous-poteaux.png'))
 for c in range(3):layer[:,:,c]=lut[c,layer[:,:,c]]
 base.alpha_composite(Image.fromarray(layer));core=np.asarray(base.crop(BOX));empty=np.zeros_like(core)
 def mask(name):return np.array(Image.open(calques/name).convert('RGBA').crop(BOX))
 ll=[mask(f'{i}-Halo-Ecran.png') for i in range(1,5)];gg=[mask(f'{i}-Bourgeons-Normal.png') for i in range(1,5)];ss=[mask(f'Ombre-{i}-Produit.png') for i in range(1,3)]
 stage=Image.new('RGB',SIZE,(22,28,27));draw=ImageDraw.Draw(stage);mono='DejaVuSansMono.ttf';sans='DejaVuSans.ttf';serif='DejaVuSerif.ttf'
 draw.text((37,28),'D E S T I N Y   /   É D I T I O N   0 . 7 . 7',font=ft(mono,15),fill='#9cbea8');draw.text((32,54),'Nuit vivante',font=ft(serif,48),fill='#f6e8d0');draw.text((35,118),'GRAND SALON  /  DÉTAIL DES POTEAUX',font=ft(mono,14),fill='#d6be9b')
 draw.rounded_rectangle((33,149,927,639),radius=5,fill='#79533b',outline='#6b715e',width=2)
 draw.text((967,113),'É T O F F E S',font=ft(mono,16),fill='#cbd4bd')
 draw.text((967,135),'Aperçu hors placement',font=ft(sans,13),fill='#a5b8ad')
 draw.text((35,663),'Halos doux · lianes en spirale · ombres mouvantes sur le bois',font=ft(sans,17),fill='#e3cab1');draw.text((995,668),'3 BOUCLES / 4 PALETTES',font=ft(mono,13),fill='#b7b69f')
 toys=[]
 for j,(name,label,d) in enumerate([('02-hampe-grenat','Drapeau sur hampe',128),('03-gonfanon-miel','Gonfanon',184),('04-fanions-sauge','Guirlande de fanions',161)]):
  image=Image.open(O/'Etoffes-animees/Planche-par-variante'/(name+'.png'));w,h=image.width//4,image.height//4;imgs=[image.crop((i%4*w,i//4*h,(i%4+1)*w,(i//4+1)*h)).convert('RGBA') for i in range(16)];top=166+j*156
  draw.rounded_rectangle((960,top,1244,top+139),radius=8,fill='#252c28',outline='#47564b',width=1);draw.text((975,top+110),label,font=ft(sans,16),fill='#f2e0be');toys.append((imgs,d,top,j))
 dest=O/'Extrait-Nuit-Vivante.mp4';command=['ffmpeg','-loglevel','error','-y','-threads','2','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
 proc=subprocess.Popen(command,stdin=subprocess.PIPE)
 assert proc.stdin
 for n in range(FPS*DUREE):
  t=n*1000/FPS;v=fx.visual(core,empty,1,1,ll,gg,ss,t,None,None,b['n']);view=Image.fromarray(v).resize((888,484),Image.Resampling.NEAREST);im=stage.copy();im.paste(view,(36,152))
  for frames,d,top,j in toys:
   p=frames[(int(t/d)+j*4)%len(frames)];scale=2 if j==2 else 1
   if scale==2:p=p.resize((p.width*scale,p.height*scale),Image.Resampling.NEAREST)
   im.paste(p,(1102-p.width//2,top+53-p.height//2),p)
  proc.stdin.write(im.tobytes())
  if n==0:im.save(fx.W/'Extrait-controle.png')
 proc.stdin.close();assert proc.wait()==0;print('PASS · Extrait Nuit vivante,',dest.stat().st_size,'octets ·',DUREE,'secondes',flush=True)
if __name__=='__main__':main()
