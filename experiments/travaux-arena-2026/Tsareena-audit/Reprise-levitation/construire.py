from pathlib import Path
from PIL import Image
from collections import deque
import json,base64,xml.etree.ElementTree as ET,hashlib
r=Path(__file__).resolve().parent; root=r.parent; refs=root/'refs-spritecollab'; data={}
for a in ET.parse(refs/'AnimData.xml').getroot().find('Anims'):
 n=a.findtext('Name');copy=a.findtext('CopyOf')
 if copy: data[n]={'copy':copy};continue
 path=refs/(n+'-Anim.png'); im=Image.open(path)
 w,h=int(a.findtext('FrameWidth')),int(a.findtext('FrameHeight'));dur=[int(z.text) for z in a.findall('Durations/Duration')]
 assert im.size[0]==w*len(dur) and im.size[1] in (h,h*8),(n,im.size)
 data[n]={'w':w,'h':h,'dur':dur,'dirs':im.height//h,'src':'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()}
for src,name in [(root/'revision-corpulence/repos-trois-quart-01.png','avant-droite-detoure.png'),(root/'Huit-directions/avant-gauche.png','avant-gauche-detoure.png')]:
 im=Image.open(src).convert('RGB');pix=im.load();w,h=im.size; bg=pix[0,0]; seen=bytearray(w*h); todo=deque()
 for x in range(w): todo.append((x,0));todo.append((x,h-1))
 for y in range(h): todo.append((0,y));todo.append((w-1,y))
 def isbg(c):return sum((c[i]-bg[i])**2 for i in range(3))<30**2
 while todo:
  x,y=todo.popleft();i=y*w+x
  if seen[i]:continue
  seen[i]=1
  if not isbg(pix[x,y]):continue
  pix[x,y]=(255,0,255)
  if x:todo.append((x-1,y))
  if x+1<w:todo.append((x+1,y))
  if y:todo.append((x,y-1))
  if y+1<h:todo.append((x,y+1))
 rgba=im.convert('RGBA'); rgba.putdata([(0,0,0,0) if c==(255,0,255) else (*c,255) for c in im.getdata()]); box=rgba.getbbox(); rgba=rgba.crop(box);rgba.save(r/name)
 print(name, 'bbox',box,'source sha256',hashlib.sha256(src.read_bytes()).hexdigest())
for key,filename in [('right','avant-droite-detoure.png'),('left','avant-gauche-detoure.png')]:data[key]='data:image/png;base64,'+base64.b64encode((r/filename).read_bytes()).decode()
template='''<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Méga-Tsareena · reprise lévitation</title><style>
*{box-sizing:border-box}body{margin:0;background:#101d19;color:#e9f2e9;font:16px system-ui}main{max-width:1100px;margin:auto;padding:25px}h1{margin-bottom:8px}.notice{background:#4b3824;border-left:5px solid #eab66c;padding:14px;line-height:1.5}.controls{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}label{font-size:14px}select,button{display:block;margin-top:5px;background:#243d30;color:white;border:1px solid #73927b;border-radius:7px;padding:9px;font:inherit}.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}article{background:#20352a;border-radius:12px;padding:16px}h2{font-size:17px;margin:0 0 10px}.stage{height:300px;display:flex;align-items:center;justify-content:center;background:repeating-linear-gradient(90deg,#56745b 0 50px,#607e62 50px 100px);border-radius:8px;position:relative;overflow:hidden}.stage canvas{width:100%;height:100%;image-rendering:pixelated}.meta{color:#c4dcc7;line-height:1.5;font-size:14px}.badge{color:#ffd296;font-weight:bold}a{color:#b0e8af}@media(max-width:650px){.grid{grid-template-columns:1fr}}</style></head><body><main>
<h1>Méga-Tsareena · reprise lévitation</h1><p>Comparateur de travail : animations originales à gauche, sprite validé à droite quand la vue existe.</p><p class="notice"><strong>Important :</strong> à droite, seule une oscillation de lévitation de la pose immobile est simulée pour la marche. Ce n’est pas une animation des membres, ni un pack PMDO terminé. Les six autres vues et toutes les actions Méga restent à dessiner et vérifier. Détourage automatique provisoire sur copies.</p>
<div class="controls"><label>Animation<select id="anim"></select></label><label>Direction<select id="dir"></select></label><label>Lecture<button id="pause">Pause</button></label></div>
<div class="grid"><article><h2>Tsareena de base · SpriteCollab</h2><div class="stage"><canvas id="base" width="440" height="300"></canvas></div><p class="meta" id="baseinfo"></p></article><article><h2>Méga-Tsareena · référence validée</h2><div class="stage"><canvas id="mega" width="440" height="300"></canvas></div><p class="meta" id="megainfo"></p></article></div><p class="meta">Référence : SpriteCollab, Tsareena (baronessfaron). AnimData.xml : durées en soixantièmes de seconde ; Shoot reprend Charge. Le sommeil original n’a qu’une direction. Aperçu hors moteur : ni offsets, ni ombres PMDO définitifs.</p></main><script>
const data=__DATA__,names=['Face','Avant-droite','Droite','Arrière-droite','Dos','Arrière-gauche','Gauche','Avant-gauche'],sel=document.querySelector('#anim'),dir=document.querySelector('#dir');for(const n of Object.keys(data).filter(k=>!['right','left'].includes(k)))sel.add(new Option(n,n));names.forEach((n,i)=>dir.add(new Option(n,i)));sel.value='Walk';dir.value='1';let cache={};for(const [k,v] of Object.entries(data)){const src=typeof v==='string'?v:v.src;if(src){const i=new Image();i.src=src;cache[k]=i}}let paused=false,start=performance.now(),elapsed=0;const base=document.querySelector('#base').getContext('2d'),mega=document.querySelector('#mega').getContext('2d');base.imageSmoothingEnabled=false;mega.imageSmoothingEnabled=false;document.querySelector('#pause').onclick=()=>{paused=!paused;document.querySelector('#pause').textContent=paused?'Reprendre':'Pause';if(!paused)start=performance.now()-elapsed};for(let el of [sel,dir])el.onchange=()=>{start=performance.now();elapsed=0};
function frameAt(ms,d){let total=d.reduce((a,b)=>a+b,0),ticks=(ms*60/1000)%total;for(let i=0;i<d.length;i++){if(ticks<d[i])return i;ticks-=d[i]}return 0}
function run(now){if(!paused)elapsed=now-start;let n=sel.value,k=data[n].copy||n,a=data[k],d=+dir.value,f=frameAt(elapsed,a.dur),row=a.dirs===1?0:d;base.clearRect(0,0,440,300);mega.clearRect(0,0,440,300);if(cache[k].complete){let sc=Math.min(4,245/a.h,300/a.w),w=a.w*sc,h=a.h*sc;base.drawImage(cache[k],f*a.w,row*a.h,a.w,a.h,(440-w)/2,260-h,w,h)}document.querySelector('#baseinfo').textContent=`${n}${data[n].copy?' (copie de '+k+')':''} · image ${f+1}/${a.dur.length} · durée ${a.dur[f]} ticks · ${a.dirs===1?'unique direction':names[d]}`;
let key=d===1?'right':d===7?'left':null;if(key&&cache[key].complete){let im=cache[key],scale=Math.min(210/im.height,220/im.width),w=im.width*scale,h=im.height*scale;let bob=n==='Walk'?[0,3,1,3][f%4]:0;mega.fillStyle='rgba(0,0,0,.25)';mega.beginPath();mega.ellipse(220,262,42,8,0,0,6.283);mega.fill();mega.drawImage(im,220-w/2,248-h-bob,w,h);document.querySelector('#megainfo').innerHTML='<span class="badge">Pose statique, non validée comme animation.</span> '+(n==='Walk'?'Oscillation de lévitation simulée uniquement ; jambes et bras non animés.':'Cette action Méga reste à créer.')}else{mega.fillStyle='#e9f2e9';mega.font='16px system-ui';mega.textAlign='center';mega.fillText('Vue Méga validée non disponible',220,145);document.querySelector('#megainfo').innerHTML='<span class="badge">Non réalisé.</span> Aucune vue inventée ou retournée par miroir.'}requestAnimationFrame(run)}requestAnimationFrame(run);
</script></body></html>'''
(r/'Apercu-reprise-levitation.html').write_text(template.replace('__DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':'))),encoding='utf8')
print('animations',[(k,len(v.get('dur',[])),v.get('dirs')) for k,v in data.items() if isinstance(v,dict)])
