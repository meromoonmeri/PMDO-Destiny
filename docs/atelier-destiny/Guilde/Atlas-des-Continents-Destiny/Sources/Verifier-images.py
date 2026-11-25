#!/usr/bin/env python3
"""Check that assets align exactly, the parchment is untouched and map data are self-consistent."""
from pathlib import Path
from PIL import Image,ImageChops
from hashlib import sha256
from io import BytesIO
from math import dist
import json,re,base64
import numpy as np

R=Path(__file__).resolve().parents[1];m=json.loads((R/'Calques/Atlas.json').read_text()); report=R/'Verification-carte.json'
base=json.loads(report.read_text());z=5;W,H=m['size'];big=R/f'Carte-des-Continents-Destiny-{W*z}x{H*z}.png'; checks=[]
def ck(value,desc):
    assert value,desc
    checks.append(desc)
def im(name):
    with Image.open(R/name) as f:return f.copy()

def eq(a,b):return a.mode==b.mode and a.size==b.size and ImageChops.difference(a,b).getbbox(alpha_only=False) is None

ck(sha256((R/m['couche_originale']['fichier']).read_bytes()).hexdigest()==m['couche_originale']['sha256'],'Fond source intact')
raw=im(m['couche_originale']['fichier']).convert('RGB');paper=im(m['layers']['parchemin']);ck(eq(raw.resize((W,H),Image.Resampling.NEAREST),paper),'Parchemin agrandi par pixel, sans retouche')
flat=im(m['natif']);res=paper.convert('RGBA'); changed=np.zeros((H,W),bool)
ck('sentiers' not in m['ordre'],'Sentiers réservés au gros plan')
for k in m['ordre'][1:]:
    a=im(m['layers'][k]);ck(a.size==(W,H) and a.mode=='RGBA','Alignement du calque '+k);res.alpha_composite(a);changed|=np.asarray(a.getchannel('A'))>0
ck(eq(flat,res.convert('RGB')),'Composition exactement identique au PNG de travail')
ck(np.array_equal(np.asarray(paper)[~changed],np.asarray(flat)[~changed]),'Pixels de papier exposés inchangés')
export=im(big);ck(eq(flat.resize((W*z,H*z),Image.Resampling.NEAREST),export),'Export 5560 × 3660 : tous les blocs ×5 sont nets et à leur place')
ck(sha256(big.read_bytes()).hexdigest()==base['plan_sha256'],'Empreinte du grand PNG')
ck(len(m['regions'])==9 and len({p['id'] for p in m['regions']})==9 and m['continents']==8 and m['ilots']==25,'Huit continents, Réverie et 25 îlots')
ck(len(m['sites'])==30 and len({p['id'] for p in m['sites']})==30,'Trente repères uniques')
pins={p['id']:p for p in m['sites']};isle=[p for p in m['sites'] if p['region']=='reve'];known=[p for p in m['sites'] if p['existe_dans_le_projet']]
ck(len(known)==8 and len(isle)==6 and all(p['existe_dans_le_projet'] for p in isle),'Huit noms du projet, dont les six repères de Réverie')
x,y,u,v=m['reverie_box'];bx,by,bu,bv=next(r['bounds'] for r in m['regions'] if r['id']=='reve')
ck(x+7<bx and y+7<by and u-7>bu and v-7>bv,'Île entière avec marges dans le gros plan')
ck(im('Ile-de-Reverie.png').size==((u-x)*z,(v-y)*z),'Taille du gros plan')
ck(all(dist(pins['reverie']['position'],p['position'])<60 for p in isle),'Lieux de départ voisins du village')
for p in m['sites']:
    a,b,c,d=p['boite'];image=im(p['image']);ck(image.mode=='RGBA' and image.size==(c-a,d-b)==tuple(p['taille']) and 0<=a<c<=W and 0<=b<d<=H,'Ancre et dimensions : '+p['id'])
html=(R/'Explorer-Atlas-Destiny.html').read_text();v=json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>',html,re.S)[1]);main=base64.b64decode(v['image'].partition(',')[2]);ck(main==(R/m['natif']).read_bytes(),'Carte intégrée à l’atlas autonome pixel-identique')
ck(len(v['sites'])==len(m['sites']) and len(v['regions'])==len(m['regions']),'Index complet dans la version autonome')
base['controle_final']={'tests':len(checks),'details':checks};report.write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');print(f'{len(checks)} PASS : planche, calques et intégration')
