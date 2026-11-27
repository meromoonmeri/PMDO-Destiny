#!/usr/bin/env python3
"""Banques V3 Giga-Tonnerre et Électro-Surf : génération seule, sans installation."""
from pathlib import Path
from PIL import Image,ImageDraw
import math,io,struct,json,copy
H=Path.home(); R=H/'Capacites-Z'; G=H/'.cache/destiny-test/game/PMDO-Destiny'
GP=R/'Prototypes/Giga-Tonnerre/Generation-PMDO'; EP=R/'Prototypes/Electro-Surf-Survolte/Generation-PMDO'
for p in (GP,EP):p.mkdir(parents=True,exist_ok=True)
def rgba(c,a=255):return (*c,a)
def part_bank(P,name,frames,N,frame_time=2):
 sheet=Image.new('RGBA',(N*len(frames),N*8));preview=Image.new('RGBA',(N*len(frames),N),(22,25,34,255))
 for r in range(8):
  for i,im in enumerate(frames):sheet.alpha_composite(im,(N*i,N*r))
 for i,im in enumerate(frames):preview.alpha_composite(im,(N*i,0))
 b=io.BytesIO();sheet.save(b,format='PNG');data=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(data))+data+struct.pack('<iiii',N,N,4,len(frames)));preview.convert('RGB').save(P/(name+'-progression.png'))
def beam_bank(P,name,heads,bodies,tails):
 n=len(heads);assert len(bodies)==len(tails)==n
 hw,hh=heads[0].size;bw,bh=bodies[0].size;tw,th=tails[0].size
 W=max(hw,bw,tw)*n;tex=Image.new('RGBA',(W,hh+bh+th));rect=[]
 for frames,w,h,y in ((heads,hw,hh,0),(bodies,bw,bh,hh),(tails,tw,th,hh+bh)):
  for i,f in enumerate(frames):
   tex.alpha_composite(f,(w*i,y));rect.append((w*i,y,w,h))
 b=io.BytesIO();tex.save(b,format='PNG');png=b.getvalue();raw=struct.pack('<q',len(png))+png+struct.pack('<i',len(rect))+b''.join(struct.pack('<iiii',*r) for r in rect)+struct.pack('<i',n);(P/(name+'.beam')).write_bytes(raw)
 # ColonneAnim.SetUp interroge aussi GetAttackSheet : même nom, nombre de frames identique.
 if name.startswith('Giga'):
  N=max(hw,hh);part_bank(P,name,heads,N)
 heads_preview=Image.new('RGBA',(hw*n,hh),(25,28,36,255))
 for i,f in enumerate(heads):heads_preview.alpha_composite(f,(i*hw,0))
 heads_preview.convert('RGB').save(P/(name+'-tetes.png'))

# Giga : corps répétable verticalement, jusqu'au haut du cadre. Les traits
# périodiques partagent leurs coordonnées en haut et en bas de chaque cellule.
N=48;heads=[];bodies=[];tails=[]
cols=[(255,76,130),(255,175,42),(255,244,93),(89,237,168),(61,194,255),(191,115,255)]
for t in range(N):
 ph=math.tau*t/N
 h=Image.new('RGBA',(96,96));d=ImageDraw.Draw(h)
 # éclats de toutes les couleurs autour de la cible, animés en rotation douce
 for j,col in enumerate(cols):
  a=math.tau*j/6+0.35*math.sin(ph); r=17+2*math.sin(ph+j);pts=[]
  for k in range(7):
   q=r+k*3.3;side=2.6*math.sin(k*math.pi*.72+ph+j);pts.append((round(48+q*math.cos(a)-side*math.sin(a)),round(50+q*math.sin(a)+side*math.cos(a))))
  d.line(pts,fill=rgba(col,235),width=2)
  if j%2==0:
   x,y=pts[4];d.line((x,y,x+round(4*math.cos(a+1)),y+round(4*math.sin(a+1))),fill=rgba(col,210),width=1)
 # halo de l'impact, le centre se trouve sur la cible
 r=10+round(2*math.sin(ph));d.ellipse((48-r,51-r//2,48+r,51+r//2),outline=(255,251,194,230),width=2)
 heads.append(h)
 b=Image.new('RGBA',(48,24));d=ImageDraw.Draw(b)
 def wave_path(base,amp,phase):return [(round(base+amp*math.sin(math.tau*y/24+phase)),y) for y in range(25)]
 d.line(wave_path(24,3,ph),(255,172,36,180),width=15)
 d.line(wave_path(24,3,ph),(255,236,87,235),width=9)
 d.line(wave_path(24,3,ph),(255,255,233,255),width=4)
 for j,col in enumerate(cols):
  # positions align at both ends of the repeating 24-pixel tile
  x=12+j*5;d.line(wave_path(x,2.2,ph+j*.8),rgba(col,210),width=2)
 bodies.append(b);tails.append(Image.new('RGBA',(1,1)))
beam_bank(GP,'GigaV3_Colonne',heads,bodies,tails)

# Sphère opaque, surface animée par couches et arcs tournants ; forme ronde
# donc la rotation des huit orientations reste cohérente.
def sphere(t,n=48,rad=20,canvas=80):
 ph=math.tau*t/n;im=Image.new('RGBA',(canvas,canvas));d=ImageDraw.Draw(im);c=canvas//2
 d.ellipse((c-rad-5,c-rad-5,c+rad+5,c+rad+5),fill=(255,207,39,55))
 d.ellipse((c-rad,c-rad,c+rad,c+rad),fill=(237,154,5,255),outline=(255,247,146,255),width=2)
 d.ellipse((c-rad+3,c-rad+3,c+rad-3,c+rad-3),fill=(255,210,31,255))
 d.ellipse((c-rad+7,c-rad+5,c+rad-7,c+rad-7),fill=(255,232,79,255))
 d.ellipse((c-rad+8,c-rad+6,c-rad+15,c-rad+12),fill=(255,252,183,255))
 # Electric filaments move continuously over the opaque sphere's surface.
 electric=Image.new('RGBA',(canvas,canvas));ed=ImageDraw.Draw(electric)
 for j in range(5):
  a=j*math.tau/5+0.3*math.sin(ph);px,py=0.,0.;pts=[]
  for k in range(8):
   along=-rad+4+k*(2*rad-8)/7;side=(j-2)*4+2.3*math.sin(k*1.6+ph+j)
   pts.append((round(c+along*math.cos(a)-side*math.sin(a)),round(c+along*math.sin(a)+side*math.cos(a))))
  ed.line(pts,fill=(255,252,195,190),width=1)
 mask=Image.new('L',(canvas,canvas));ImageDraw.Draw(mask).ellipse((c-rad+3,c-rad+3,c+rad-3,c+rad-3),fill=255)
 electric.putalpha(Image.composite(electric.getchannel('A'),Image.new('L',(canvas,canvas)),mask));im.alpha_composite(electric);d=ImageDraw.Draw(im)
 for j in range(8):
  a=math.tau*j/8+0.35*math.sin(ph);rr=rad+1;pts=[]
  for k in range(5):
   dist=rr+k*2.8;side=2*math.sin(k*1.8+ph+j);pts.append((round(c+dist*math.cos(a)-side*math.sin(a)),round(c+dist*math.sin(a)+side*math.cos(a))))
  d.line(pts,fill=(255,234,94,245),width=3);d.line(pts,fill=(255,255,218,255),width=1)
 return im
heads=[sphere(t) for t in range(N)];empty=[Image.new('RGBA',(1,1)) for _ in range(N)]
beam_bank(EP,'ElectroSurfV3_Sphere',heads,empty,empty)
# Chargement de foudre autour du Pokémon, puis sphère opaque qui grandit.
frames=[];S=96
for step in range(114):
 t=step/2
 f=Image.new('RGBA',(S,S));d=ImageDraw.Draw(f);ph=math.tau*t/24
 if t<34:
  fade=min(1,(t+1)/6,(40-t)/8)
  for j in range(7):
   a=math.tau*j/7+ph*.4;r=17+4*math.sin(ph+j);p=[]
   for k in range(6):
    dis=r+k*2;side=2.5*math.sin(k*1.7+ph+j);p.append((round(48+dis*math.cos(a)-side*math.sin(a)),round(48+dis*math.sin(a)+side*math.cos(a))))
   d.line(p,fill=(255,220,72,round(220*fade)),width=2);d.line(p,fill=(255,255,219,round(225*fade)),width=1)
  d.ellipse((30,40,66,58),outline=(255,227,88,round(150*fade)),width=2)
 if t>=29:
  s=sphere(step);size=int(16+64*min(1,(t-29)/13));s=s.resize((size,size),Image.Resampling.NEAREST);f.alpha_composite(s,(48-size//2,48-size//2))
 frames.append(f)
part_bank(EP,'ElectroSurfV3_Charge',frames,S)
# Décharges brèves à chaque cible touchée.
frames=[];S=80
for step in range(32):
 t=step/2
 f=Image.new('RGBA',(S,S));d=ImageDraw.Draw(f);fade=min(1,(t+1)/3,(16-t)/6)
 for j in range(6):
  a=j*math.tau/6+t*.15;pts=[]
  for k in range(5):
   r=5+k*5;z=2*math.sin(k*2+t*.3+j);pts.append((round(40+r*math.cos(a)-z*math.sin(a)),round(40+r*math.sin(a)+z*math.cos(a))))
  d.line(pts,fill=(255,228,76,int(230*fade)),width=2)
 frames.append(f)
part_bank(EP,'ElectroSurfV3_Impact',frames,S)

def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
# Giga : colonne native, attachée aux cibles plutôt qu'image dont le haut est visible.
a=json.loads((GP/'ten_million_volt_thunderbolt-test-only.json').read_text(encoding='utf-8-sig'));fx=a['Object']['Data']['HitFX'];fx['Emitter']['Anim']['$type']='RogueEssence.Content.ColumnAnim, RogueEssence';fx['Emitter']['Anim'].pop('FrameOffset',None);fx['Emitter']['Anim']['Anim']['AnimIndex']='GigaV3_Colonne';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx['Emitter']['Anim']['Cycles']=1;fx['Delay']=42;fx['AbsoluteDelay']=True
(GP/'ten_million_volt_thunderbolt-v3-test-only.json').write_text(json.dumps(a,indent=2,ensure_ascii=False))
# Électro-Surf : tête de rayon sphérique animée, corps de rayon transparent ;
# vraie zone balayée de trois cases de large (WaveMotionAction.Wide).
a=json.loads((EP/'stoked_sparksurfer-original.json').read_text(encoding='utf-8-sig'));z=a['Object'];z['Released']=True;z['BaseCharges']=1;z['Data']['OnHits'].append(copy.deepcopy(read('thunder_wave')['Object']['Data']['OnHits'][0]))
act=copy.deepcopy(read('solar_beam')['Object']['HitboxAction']);act['Anim']['AnimIndex']='ElectroSurfV3_Sphere';act['Anim']['FrameTime']=1;act.update(Wide=True,Speed=2,Linger=0,Range=3,StopAtHit=False,StopAtWall=True,TargetAlignments=4,HitTiles=False);act['CharAnimData']['ActionType']=5;act['PreActions']=[];act['ActionFX']['Sound']='DUN_Shock_Wave';act['ActionFX']['ScreenMovement']={'MinShake':0,'MaxShake':0,'MaxShakeTime':0};z['HitboxAction']=act
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='ElectroSurfV3_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx['Delay']=0;fx['AbsoluteDelay']=False;fx['Sound']='DUN_Paralyzed';z['Data']['HitFX']=fx
z['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'ElectroSurfV3_Charge','ArgTable':'{}'}}]
(EP/'stoked_sparksurfer-v3-test-only.json').write_text(json.dumps(a,indent=2,ensure_ascii=False))
print('Banques V3 et fiches prêtes ; aucun jeu modifié.')
