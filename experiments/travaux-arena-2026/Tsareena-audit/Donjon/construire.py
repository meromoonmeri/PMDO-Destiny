from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET
import base64,json
p=Path(__file__).parent;root=p.parent;ref=root/'refs-spritecollab'
def enc(path):return 'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()
names=['Idle','Walk','Attack','Sleep','Hurt','Swing','Double','Hop','Charge','Rotate','Kick'];anims={};imgs={}
xml=ET.parse(ref/'AnimData.xml').getroot()
for a in xml.find('Anims'):
 n=a.findtext('Name')
 if n not in names:continue
 w=int(a.findtext('FrameWidth'));h=int(a.findtext('FrameHeight'));d=[int(v.text) for v in a.find('Durations')];im=Image.open(ref/(n+'-Anim.png')).convert('RGBA');assert im.width==w*len(d) and im.height%h==0
 rows=im.height//h;boxes=[]
 for r in range(rows):
  boxes.append([im.crop((i*w,r*h,(i+1)*w,(r+1)*h)).getbbox() for i in range(len(d))])
 anims[n]={'w':w,'h':h,'durations':d,'rows':rows,'hit':int(a.findtext('HitFrame') or 0),'boxes':boxes};imgs['ref-'+n]=enc(ref/(n+'-Anim.png'))
imgs['enemy']=enc(ref/'ennemi-Idle.png')
for d in ['face','avant-droite','droite','arriere-droite','dos','arriere-gauche','gauche','avant-gauche']:imgs['dir-'+d]=enc(root/'derivees'/(d+'.png'))
for n in ['idle1','idle2','sleep1','sleep2']:imgs[n]=enc(root/'derivees-pmd'/(n+'.png'))
imgs['hurt']=enc(root/'derivees'/'blessure.png')
for n in ['prepare','retour']:imgs[n]=enc(p/(n+'.png'))
text=(p/'modele.html').read_text().replace('__DATA__',json.dumps({'anims':anims,'images':imgs},separators=(',',':')))
(p/'Donjon-Mega-Tsareena.html').write_text(text)
print('Fichier créé',len(text),'octets,',len(anims),'planches de référence,',len(imgs),'images')
