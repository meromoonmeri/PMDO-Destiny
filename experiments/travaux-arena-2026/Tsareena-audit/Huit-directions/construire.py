from pathlib import Path
from PIL import Image
from scipy.ndimage import binary_propagation
import numpy as np,base64,json,xml.etree.ElementTree as ET
p=Path(__file__).parent;root=p.parent;derive=p/'copies-apercu';derive.mkdir(exist_ok=True)
def image(path,name):
 im=Image.open(path).convert('RGB');a=np.array(im,dtype=np.int32);bg=np.median(np.concatenate([a[:5].reshape(-1,3),a[-5:].reshape(-1,3),a[:,:5].reshape(-1,3),a[:,-5:].reshape(-1,3)]),axis=0);mask=np.sum((a-bg)**2,axis=2)<45**2;seeds=np.zeros(mask.shape,bool);seeds[0,:]=mask[0,:];seeds[-1,:]=mask[-1,:];seeds[:,0]=mask[:,0];seeds[:,-1]=mask[:,-1];back=binary_propagation(seeds,mask=mask,structure=np.ones((3,3)));im=Image.fromarray(np.dstack([a.astype('uint8'),(~back*255).astype('uint8')]),'RGBA');box=(40,40,970,940) if name in ('s0','s1') else im.getbbox();im=im.crop(box); im.thumbnail((142,166),Image.Resampling.NEAREST);can=Image.new('RGBA',(180,190));can.alpha_composite(im,((180-im.width)//2,178-im.height));f=derive/(name+'.png');can.save(f);return 'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode()
items={'d0':p/'face.png','d1':root/'revision-corpulence/repos-trois-quart-01.png','d2':p/'profil-droite.png','d3':p/'dos-droite.png','d4':p/'dos.png','d5':p/'dos-gauche.png','d6':p/'profil-gauche.png','d7':p/'avant-gauche.png','w01':p/'face-pas1.png','w03':p/'face-pas2.png','w11':root/'revision-corpulence/Mannequin-pas-gauche.png','w13':root/'revision-corpulence/Walk-reprise-03.png','w21':p/'profil-pas1.png','s0':root/'revision-corpulence/Sommeil-fidele-00.png','s1':root/'revision-corpulence/Sommeil-fidele-00-suite.png','hit':root/'revision-corpulence/Attaque-fidele-impact.png'}
assets={k:image(v,k) for k,v in items.items()};refs=root/'refs-spritecollab';xml=ET.parse(refs/'AnimData.xml').getroot();meta={}
for anim in xml.find('Anims'):
 n=anim.findtext('Name')
 if n not in ['Idle','Walk','Attack','Sleep']:continue
 meta[n]={'w':int(anim.findtext('FrameWidth')),'h':int(anim.findtext('FrameHeight')),'dur':[int(x.text) for x in anim.find('Durations')]};assets[n]='data:image/png;base64,'+base64.b64encode((refs/(n+'-Anim.png')).read_bytes()).decode()
(p/'Huit-directions-apercu.html').write_text((p/'modele.html').read_text().replace('__DATA__',json.dumps({'assets':assets,'meta':meta},separators=(',',':'))));print('images',len(items))
