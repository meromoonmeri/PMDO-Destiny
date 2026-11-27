from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2,numpy as np
p=Path('/home/user/Capacites-Z/Prototypes/Appel-des-Ombres-Eternelles/Generation-PMDO')
frames=[Image.open(p/f'pose-{i:02}-transparent-64.png').resize((384,384),Image.Resampling.NEAREST) for i in range(1,9)]
out=cv2.VideoWriter(str(p/'apercu-sans-son-temp.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),30,(960,540))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
for t in range(180):
 im=Image.new('RGB',(960,540),(21,19,29));d=ImageDraw.Draw(im)
 d.text((28,24),'APPEL DES OMBRES ÉTERNELLES — BROUILLON',font=font,fill=(213,204,230))
 d.text((28,490),'Étude des poses • hors jeu • pas un test en donjon',font=font,fill=(165,151,184))
 j=t%60;idx=min(7,j//4) if j<32 else None
 if idx is not None:im.paste(frames[idx],(288,74),frames[idx])
 out.write(cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR))
out.release()
