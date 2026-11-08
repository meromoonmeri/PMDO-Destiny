from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
r=Path('/home/user/chantier-defauts-46-52/audit-chemins-global');O=Path(__file__).resolve().parent
im=Image.new('RGB',(1600,4000))
for row in range(5):
 for half in range(2):
  a=Image.open(r/f'vue-{row}-{half}.png').convert('RGB')
  for yy in range(2):
   for xx in range(2):im.paste(a.crop((xx*400,yy*420+20,xx*400+400,yy*420+420)),(half*800+xx*400,row*800+yy*400))
scale=.375;w=600; mh=1500; head=112; bottom=120; H=head+mh+bottom; gap=48; margin=26
out=Image.new('RGB',(margin*2+w*2+gap,H),'#f4f4ea');d=ImageDraw.Draw(out)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';F=ImageFont.truetype(font,17);FB=ImageFont.truetype(bold,21);FS=ImageFont.truetype(font,15)
x1=margin;x2=x1+w+gap
for x,title in [(x1,'Carte actuelle : 1 600 × 4 000'),(x2,'Proposition : deux sections, sud raccourci')]:d.text((x,50),title,font=FB,fill='#173e37')
d.text((margin,12),'RÉVERIE · APERÇU DE PRINCIPE — AUCUNE CARTE MODIFIÉE',font=FB,fill='#173e37')
a=im.resize((600,1500),Image.Resampling.NEAREST);out.paste(a,(x1,head))
b=im.crop((0,0,1600,3000)).resize((600,1125),Image.Resampling.NEAREST);out.paste(b,(x2,head))
# Zone à retirer superposée seulement sur la vue actuelle.
shade=Image.new('RGBA',(600,375),(142,39,39,145));out.paste(shade,(x1,head+1125),shade)
d=ImageDraw.Draw(out)
for x in (x1,x2):
 y=head+720 # vers y 1920 sur le canevas d'origine
 for i in range(0,w,24):d.line((x+i,y,x+min(i+14,w),y),fill='#204bd5',width=4)
 d.rectangle((x+8,y-30,x+304,y-8),fill='#e4ecff');d.text((x+12,y-28),'Transition indicative : à affiner',font=FS,fill='#132878')
 y2=head+1125
 d.line((x,y2,x+w,y2),fill='#d6212c',width=4)
 d.rectangle((x+8,y2-29,x+290,y2-7),fill='#fff0e8');d.text((x+12,y2-27),'Limite sud proposée : y ≈ 3000',font=FS,fill='#8a1119')
# La légende est placée hors carte, sans prétendre à une limite de collision.
d.rectangle((x2,head+1150,x2+w,head+1352),fill='#e8ede1',outline='#9dac91',width=2)
d.multiline_text((x2+18,head+1168),'SECTION 1  ·  nord et centre\nSECTION 2  ·  autel, habitations et ponts\n\nMaison isolée conservée ; forêt plus au sud retirée.\nTracé de transition et raccords à valider avant modification.',font=F,fill='#24372e',spacing=10)
d.text((x1+10,head+1150),'ZONE PROPOSÉE À RETIRER',font=FB,fill='white',stroke_width=2,stroke_fill='#632127')
d.multiline_text((margin,head+mh+22),'Maquette réalisée à partir du rendu v0.5.7, sans modifier les maps ni les sauvegardes.\nLes traits indiquent une intention : la transition réelle doit respecter les ponts, cascades et passages.',font=F,fill='#24372e',spacing=6)
out.save(O/'apercu-reverie-deux-sections.png')
