from PIL import Image,ImageDraw
import numpy as np
from pathlib import Path
import base64,json
p=Path(__file__).resolve().parent;r=p.parent;b=r/'Marche-bras';ref=r/'refs-spritecollab';old=r/'Reprise-levitation'
right=r/'revision-corpulence/repos-trois-quart-01.png'; left=r/'Huit-directions/avant-gauche.png'
paths={1:[right,old/'essai-manuel-jambe-1.png',right,old/'essai-manuel-jambe-2.png'],7:[left,b/'pas-gauche-02-retouche.png',left,b/'pas-gauche-04-retouche.png']}
source=Image.open(ref/'Walk-Anim.png').convert('RGBA'); sheet=Image.new('RGBA',(128,448))
def alpha(im):
 a=np.array(im.convert('RGB')); bg=a[0,0].astype(int); v=a.astype(int); d=np.sqrt(((v-bg)**2).sum(axis=2));m=(d>38)|(v[:,:,2]<150); return Image.fromarray(np.dstack([a,m.astype('uint8')*255]),'RGBA')
for row,frames in paths.items():
 ims=[alpha(Image.open(f)) for f in frames]; assert len({im.size for im in ims})==1
 boxes=[im.getbbox() for im in ims]; box=(min(x[0] for x in boxes),min(x[1] for x in boxes),max(x[2] for x in boxes),max(x[3] for x in boxes)); sw=box[2]-box[0];sh=box[3]-box[1]
 sboxes=[source.crop((k*32,row*56,(k+1)*32,(row+1)*56)).getbbox() for k in range(4)];width=min(26,max(v[2]-v[0] for v in sboxes));height=max(v[3]-v[1] for v in sboxes);x=max(0,min(32-width,round((sboxes[0][0]+sboxes[0][2]-width)/2)));y=sboxes[0][3]-height
 factor=min(width/sw,height/sh);nw=round(sw*factor);nh=round(sh*factor)
 for i,im in enumerate(ims):
  o=im.crop(box).resize((nw,nh),Image.Resampling.NEAREST); sheet.alpha_composite(o,(i*32+x+(width-nw)//2,row*56+y+height-nh))
sheet.save(p/'Walk-Anim-PARTIEL.png')
# Inspection enlarged at real PMD resolution
control=Image.new('RGB',(4*32*5,2*56*5),(202,219,190));
for idx,row in enumerate((1,7)):
 for f in range(4):
  tile=sheet.crop((f*32,row*56,(f+1)*32,(row+1)*56)).resize((160,280),Image.Resampling.NEAREST);control.paste(tile,(f*160,idx*280),tile)
control.save(p/'controle-marche.png')
assert sheet.size==(128,448)
for row in range(8):
 empty=sheet.crop((0,row*56,128,(row+1)*56)).getbbox() is None
 assert empty==(row not in paths)
print('Planches vérifiées 128x448, lignes présentes 1 et 7 ; autres transparentes')
# standalone viewer, only walking
images={ 'mega':'data:image/png;base64,'+base64.b64encode((p/'Walk-Anim-PARTIEL.png').read_bytes()).decode(), 'normal':'data:image/png;base64,'+base64.b64encode((ref/'Walk-Anim.png').read_bytes()).decode()}
html='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Marche en lévitation · Méga-Tsareena</title><style>body{margin:0;background:#111f19;color:#eef4e9;font:16px system-ui}main{max-width:1050px;margin:auto;padding:24px}h1{font-size:28px}.notice{background:#453b25;border-left:4px solid #ecc57b;padding:15px;line-height:1.5}button,select{font:inherit;padding:10px;border:0;border-radius:7px;background:#d9edcf;color:#15231c;margin:4px}section{display:grid;grid-template-columns:1fr 1fr;gap:14px}.box{background:#263b2f;padding:14px;border-radius:10px}canvas{width:100%;height:300px;background:#cbdcc1;image-rendering:pixelated}a{color:#d3f4b9}.small{font-size:14px}@media(max-width:650px){section{grid-template-columns:1fr}}</style><main><h1>Marche en lévitation</h1><p class="notice"><strong>Planche de travail partielle :</strong> avant-droite et avant-gauche. Les six autres directions ne sont pas intégrées : leurs essais de design doivent être corrigés. Les bras restent fixes et les jambes / raccords sont à valider. Aucun offset ni ombre PMDO.</p><label>Direction <select id="direction"><option value="1">Avant-droite</option><option value="7">Avant-gauche</option></select></label><button id="pause">Pause</button><button id="next">Image suivante</button><section><div class="box"><h2>Tsareena normale · référence</h2><canvas id="normal" width="400" height="300"></canvas></div><div class="box"><h2>Méga · essai</h2><canvas id="mega" width="400" height="300"></canvas></div></section><p>4 images · 8 / 10 / 8 / 10 ticks à 60 Hz. L’ombre dans l’aperçu sert seulement à montrer la lévitation.</p><p><a download="Walk-Anim-PARTIEL.png" href="__MEGA__">Télécharger la planche Walk partielle</a></p><p class="small">Référence SpriteCollab : Tsareena, baronessfaron. Ce n’est pas un pack prêt à importer.</p></main><script>const data=__DATA__,img={};for(const k in data){img[k]=new Image();img[k].src=data[k]};let playing=true,t=0,old=performance.now(),step=0;const dur=[8,10,8,10];function frame(t){let v=(t/1000*60)%36;for(let i=0;i<4;i++){if(v<dur[i])return i;v-=dur[i]}return 0}document.querySelector('#pause').onclick=()=>{playing=!playing;document.querySelector('#pause').textContent=playing?'Pause':'Reprendre';old=performance.now()};document.querySelector('#next').onclick=()=>{playing=false;document.querySelector('#pause').textContent='Reprendre';step=(step+1)%4};function draw(now){if(playing){t+=now-old;step=frame(t)}old=now;let row=+document.querySelector('#direction').value;for(let k of ['normal','mega']){let c=document.querySelector('#'+k).getContext('2d');c.clearRect(0,0,400,300);c.imageSmoothingEnabled=false;c.fillStyle='rgba(25,45,31,.22)';c.beginPath();c.ellipse(200,260,48,9,0,0,Math.PI*2);c.fill();if(img[k].complete&&img[k].naturalWidth)c.drawImage(img[k],32*step,56*row,32,56,120,2,160,280)}requestAnimationFrame(draw)}requestAnimationFrame(draw)</script></html>'''.replace('__DATA__',json.dumps(images)).replace('__MEGA__',images['mega'])
(p/'index.html').write_text(html,encoding='utf8')
