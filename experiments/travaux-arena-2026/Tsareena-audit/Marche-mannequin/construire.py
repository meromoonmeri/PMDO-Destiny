from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import binary_propagation
import xml.etree.ElementTree as ET
import base64,json
p=Path(__file__).parent;project=p.parent;raw=project/'revision-corpulence';ref=project/'refs-spritecollab';assets={}
def data(f):return 'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode()
def alpha(name):
 a=np.array(Image.open(raw/name).convert('RGB')).astype('int16');bgcol=np.median(a[:20,-20:].reshape(-1,3),axis=0);mask=np.sqrt(((a-bgcol)**2).sum(axis=2))<35;seed=np.zeros(mask.shape,bool);seed[0,:]=mask[0,:];seed[-1,:]=mask[-1,:];seed[:,0]=mask[:,0];seed[:,-1]=mask[:,-1];bg=binary_propagation(seed,mask=mask,structure=np.ones((3,3)));return Image.fromarray(np.dstack((a.astype('uint8'),np.where(bg,0,255).astype('uint8'))),'RGBA')
standing={'base':'repos-trois-quart-01.png','idle2':'Anime-Idle-02.png','walk1':'Mannequin-pas-gauche.png','walk3':'Walk-reprise-03.png','attackPrep':'repos-trois-quart-01.png','attackHit':'Attaque-fidele-impact.png'}
for key,name in standing.items():
 im=alpha(name); assert im.size==(912,1147),(name,im.size); im=im.resize((160,201),Image.Resampling.NEAREST);can=Image.new('RGBA',(220,220));can.alpha_composite(im,(30,14));f=p/(key+'.png');can.save(f);assets[key]=data(f)
sleep=[alpha('Sommeil-fidele-00.png'),alpha('Sommeil-fidele-00-suite.png')];b=[im.getbbox() for im in sleep];box=(min(x[0] for x in b),min(x[1] for x in b),max(x[2] for x in b),max(x[3] for x in b));print('sleep union',box)
for i,im in enumerate(sleep):
 im=im.crop(box);im=im.resize((round(im.width*160/912),round(im.height*201/1147)),Image.Resampling.NEAREST);can=Image.new('RGBA',(220,220));can.alpha_composite(im,((220-im.width)//2,215-im.height));f=p/f'sleep{i}.png';can.save(f);assets[f'sleep{i}']=data(f)
meta={};xml=ET.parse(ref/'AnimData.xml').getroot()
for a in xml.find('Anims'):
 n=a.findtext('Name')
 if n not in ['Idle','Walk','Attack','Sleep']:continue
 w=int(a.findtext('FrameWidth'));h=int(a.findtext('FrameHeight'));dur=[int(v.text) for v in a.find('Durations')];row=0 if n=='Sleep' else 1;im=Image.open(ref/(n+'-Anim.png')).convert('RGBA');boxes=[im.crop((i*w,row*h,(i+1)*w,(row+1)*h)).getbbox() for i in range(len(dur))];meta[n]={'w':w,'h':h,'row':row,'dur':dur,'boxes':boxes};assets[n]=data(ref/(n+'-Anim.png'))
html=(p/'modele.html').read_text().replace('__DATA__',json.dumps({'assets':assets,'meta':meta},separators=(',',':')));(p/'Apercu-marche-levitation-et-sommeil.html').write_text(html);print('OK assets',len(assets),'bytes',len(html))
