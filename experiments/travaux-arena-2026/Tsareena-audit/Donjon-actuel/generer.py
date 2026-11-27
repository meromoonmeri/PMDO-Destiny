from pathlib import Path
from PIL import Image
import base64,json,xml.etree.ElementTree as ET,html
p=Path(__file__).parent;r=p.parent;refs=r/'refs-spritecollab';data={}
def url(p):return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
root=ET.parse(refs/'AnimData.xml').getroot()
for x in root.find('Anims'):
 n=x.findtext('Name');c=x.findtext('CopyOf')
 if c:data[n]={'copy':c};continue
 f=refs/(n+'-Anim.png');im=Image.open(f);w=int(x.findtext('FrameWidth'));h=int(x.findtext('FrameHeight'));data[n]={'w':w,'h':h,'rows':im.height//h,'ticks':[int(e.text) for e in x.findall('Durations/Duration')],'src':url(f)}
for n,a in data.items():
 if 'copy' in a:
  c=a['copy'];data[n]={**data[c],'copy':c}
page=(p/'modele.html').read_text().replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__MEGA__',url(r/'Polish-nettete/Walk-palette15-ESSAI.png')).replace('__AVANT__',url(r/'Design-unifie/Reprise-vues-POLISH-ESSAI.png')).replace('__ART__',url(r/'Design-unifie/reference-artiste-cadre.png')).replace('__EDITOR__',html.escape((r/'Editeur/Editeur-Mega-Tsareena.html').read_text(),quote=True))
(r/'Apercu-actuel/index.html').write_text(page,encoding='utf-8');(p/'Donjon-et-editeur.html').write_text(page,encoding='utf-8');print('Aperçu carte et éditeur mis à jour')
