from PIL import Image,ImageDraw
from pathlib import Path
import math,json,hashlib
p=Path(__file__).resolve().parent
base=Image.open(p/'fontaine-base.png').convert('RGBA');w,h=base.size
frames=[];overlays=[]
# 8 états en boucle : reflets et gouttes uniquement sur la surface d'eau ;
# la pierre, racines et plantes restent pixel-identiques.
for t in range(8):
 over=Image.new('RGBA',(w,h));d=ImageDraw.Draw(over)
 # Anneau s'élargit, puis recommence. Dessiner des arcs fragmentés comme des reflets de pixel art.
 radius=5+(t%4)*2; cx,cy=56,43
 for j in range(-radius,radius+1):
  if (j+t)%4==0:continue
  v=1-(j/radius)**2
  if v<0:continue
  yy=round(math.sqrt(v)*radius*.28)
  for xx,y in [(cx+j,cy+yy),(cx+j,cy-yy)]:
   rr,gg,bb,aa=base.getpixel((xx,y))
   if aa and gg>rr+5 and bb>rr+4:d.point((xx,y),fill=(155,219,218,230))
 for x,y in [(35+(t%4)*2,45),(78-(t%4)*2,39),(29+t,35),(73+t,48)]:
  r,g,b,a=base.getpixel((x,y))
  if a and g>r+5 and b>r+4:d.line((x,y,x+2,y),fill=(138,213,211,235))
 # petites gouttes de chaque côté du jet, sans variation du bassin.
 for x,y in [(48,27+(t%4)),(63,30+((t+2)%4))]:
  r,g,b,a=base.getpixel((x,y))
  if a and g>r+8 and b>r+8:d.point((x,y),fill=(207,248,244,255))
 im=Image.alpha_composite(base,over);frames.append(im);overlays.append(over)
 (p/f'Fontaine-image-{t+1:02}.png').write_bytes(b'')
 im.save(p/f'Fontaine-image-{t+1:02}.png')
assert len({im.tobytes() for im in frames})==8
strip=Image.new('RGBA',(w*8,h));overstrip=Image.new('RGBA',(w*8,h));vertical=Image.new('RGBA',(w,h*8))
for i,(im,ov) in enumerate(zip(frames,overlays)):
 strip.alpha_composite(im,(i*w,0));overstrip.alpha_composite(ov,(i*w,0));vertical.alpha_composite(im,(0,i*h))
strip.save(p/'Tilesheet-Fontaine-8-images.png');overstrip.save(p/'Tilesheet-Reflets-8-images.png');vertical.save(p/'Tilesheet-Fontaine-8px-vertical.png')
# Aperçu animé agrandi entier et non lissé.
frames[0].resize((w*4,h*4),Image.Resampling.NEAREST).save(p/'Fontaine-animation.gif',save_all=True,append_images=[x.resize((w*4,h*4),Image.Resampling.NEAREST) for x in frames[1:]],duration=160,loop=0,disposal=2,transparency=0)
(p/'Lisez-moi.txt').write_text('Fontaine de la salle des missions – proposition d’aperçu\n8 images de 112 × 80 px, durée 160 ms par image, boucle 1,28 s.\nTilesheet-Fontaine-8-images.png : bande horizontale, 8 cellules ; dimensions 896 × 80 px.\nTilesheet-Reflets-8-images.png : mêmes cellules, reflets transparents seuls à superposer au sprite de base.\nTilesheet-Fontaine-8px-vertical.png : 8 cellules verticales, chacune multiple de 8 px.\nFontaine-image-01.png à 08.png : images séparées. Fontaine-base.png : eau de base sans les reflets ajoutés.\nLes images animées sont dérivées de la même génération et retouchées localement. Non intégrées ni testées dans le moteur du jeu.\n')
print('8 frames,',w,h,'changed counts',[sum(1 for q in ov.getdata() if q[3]) for ov in overlays])
