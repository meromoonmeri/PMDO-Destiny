from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path('/home/user/chantier-deplacement-arbres-bassin');F=Path('/home/user/chantier-corrections-bassin-55');P=Path('/home/user/chantier-corrections-bassin-53-54');code=(F/'audit-calques.py').read_text().split('regions=')[0];code=code.replace("sheets[n]=SheetReader(P/'banques'/(n+'.tile'))", "sheets[n]=SheetReader((N/'banques' if (N/'banques'/(n+'.tile')).exists() else (F/'banques' if (F/'banques'/(n+'.tile')).exists() else P/'banques'))/(n+'.tile'))")
def context(path):
 c={'F':F,'N':R};exec(code.replace("p=P/'candidat/payload/reverie_etang.rsground.gz'",f"p=Path({str(path)!r})"),c);return c
old=context(F/'candidat/payload/reverie_etang.rsground.gz');new=context(R/'candidat/payload/reverie_etang.rsground.gz');
for n,box in [('ouest',(89,248,113,285)),('est',(153,254,175,275))]:
 a=old['render'](box);b=new['render'](box);scale=4;w,h=a.size;im=Image.new('RGB',(w*2*scale,h*scale+36),'#192a22');d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16);d.text((5,6),'Avant — candidat 55',font=font,fill='white');d.text((w*scale+5,6),'Après — déplacement',font=font,fill='white');im.paste(a.resize((w*scale,h*scale),Image.Resampling.NEAREST),(0,36));im.paste(b.resize((w*scale,h*scale),Image.Resampling.NEAREST),(w*scale,36));im.save(R/f'avant-apres-{n}.png')
