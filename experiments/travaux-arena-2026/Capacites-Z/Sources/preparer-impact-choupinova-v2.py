#!/usr/bin/env python3
"""Prototype V2 : dimension féerique et impacts centrés, en copie PMDO uniquement."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,json,copy,shutil,math
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Impact-Choupinova/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
def cut(name,n):
 im=Image.open(P/name).convert('RGB');im.thumbnail((n,n),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');m=(b[:,:,1]>125)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45);o=Image.fromarray(np.dstack((a,np.where(m,0,255).astype('uint8'))),'RGBA');return o.crop(o.getbbox())
def scaled(im,w,h):return im.resize((max(1,w),max(1,h)),Image.Resampling.NEAREST)
def bank(name,frames,N):
 sheet=Image.new('RGBA',(N*len(frames),N*8));control=Image.new('RGBA',(N*len(frames),N),(33,31,45,255))
 for row in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
 for i,f in enumerate(frames):control.alpha_composite(f,(N*i,0))
 control.convert('RGB').save(P/(name+'-progression.png'));sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');raw=b.getvalue();file=P/(name+'.dir');file.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(file,G/'Content/Particle'/file.name)
ring=cut('aura-feerique-source.png',80);heart=cut('v2-coeur-etoile-source.png',40);boom=cut('explosion-feerique-source.png',64)
# Couronne discrète, centrée sur les pieds du lanceur, dessinée derrière les personnages.
N=96;aur=[]
for i in range(24):
 im=Image.new('RGBA',(N,N));factor=min(1,(i+1)/5)*min(1,(24-i)/5);w=int(55+3*math.sin(i*.5));h=round(w*.59);piece=scaled(ring,w,h);piece.putalpha(piece.getchannel('A').point(lambda x:x*int(210*factor)//255));im.alpha_composite(piece,((N-w)//2,(N-h)//2+8));d=ImageDraw.Draw(im)
 for k in range(6):
  angle=k*math.tau/6+i*.22;x=int(48+31*math.cos(angle));y=int(56+17*math.sin(angle));v=int(230*factor);d.line((x-2,y,x+2,y),fill=(255,226,253,v));d.line((x,y-2,x,y+2),fill=(255,226,253,v))
 aur.append(im)
bank('ChoupinovaV2_Aura',aur,N)
# Cadre 96×96 centré : tous les cœurs arrivent sur le centre de la cible.
# Petite variation horizontale seulement, pour que les éclats ne touchent pas visuellement le lanceur voisin.
N=96;frames=[];meteor=scaled(heart,22,34)
for t in range(32):
 im=Image.new('RGBA',(N,N));d=ImageDraw.Draw(im)
 for j,(off,dx) in enumerate([(0,0),(6,-5),(12,5)]):
  q=t-off
  if 0<=q<9:
   y=-35+round(q*6.125);im.alpha_composite(meteor,(48+dx-11,y))
  if 9<=q<21:
   k=q-9;size=[9,15,23,31,38,42,40,35,30,24,17,9][k];piece=scaled(boom,size,size);opacity=255 if k<5 else max(0,255-(k-4)*34);piece.putalpha(piece.getchannel('A').point(lambda a:a*opacity//255));im.alpha_composite(piece,(48+dx-size//2,48-size//2))
   for h in range(4):
    angle=h*math.pi/2+j*.6;rad=5+k;x=round(48+dx+rad*math.cos(angle));y=round(48+rad*math.sin(angle));d.point((x,y),fill=(255,235,255,max(0,255-k*21)))
 frames.append(im)
bank('ChoupinovaV2_Coeurs_Impact',frames,N)
# Voile de particules transparent et répétable : même mécanisme plein écran que Vent Argenté.
# Traînées légères, étoiles et losanges roses/lilas ; pas de décor opaque.
import random
rng=random.Random(713)
tex=Image.new('RGBA',(256,144));draw=ImageDraw.Draw(tex)
colors=[(255,189,235,125),(246,216,255,150),(165,223,255,125),(255,238,255,170)]
for i in range(48):
 x=rng.randrange(256);y=rng.randrange(144);col=colors[i%len(colors)]; r=rng.choice([1,1,2,3])
 draw.line((x-r,y,x+r,y),fill=col);draw.line((x,y-r,x,y+r),fill=col)
 if i%4==0:
  for k in range(1,10):
   xx=(x-k*2)%256; yy=(y+k//4)%144
   draw.point((xx,yy),fill=(*col[:3],max(0,col[3]-k*12)))
name='ChoupinovaV2_VentFeerique';tex.save(P/(name+'.png'));b=io.BytesIO();tex.save(b,format='PNG');raw=b.getvalue();path=P/(name+'.dir');path.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',256,144,0,1));shutil.copy2(path,G/'Content/BG'/path.name)
z=json.loads((P/'twinkle_tackle-test-only.json').read_text());a=z['Object'];a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'ChoupinovaV2_Rotation','ArgTable':'{}'}}]
a['Data']['HitFX']['Emitter']['Anim']['Anim']['AnimIndex']='ChoupinovaV2_Coeurs_Impact';a['Data']['HitFX']['Emitter']['Anim']['Anim']['FrameTime']=2;a['Data']['HitFX']['Delay']=42
fx=a['HitboxAction']['ActionFX'];other=json.loads((R/'Prototypes/Appel-des-Ombres-Eternelles/Generation-PMDO/never_ending_nightmare-immersif-test-only.json').read_text())['Object']['HitboxAction']['ActionFX']['Emitter'];fx['Emitter']=copy.deepcopy(other);fx['Emitter']['Anim']['AnimIndex']=name;fx['Emitter']['Anim']['Alpha']=200;fx['Emitter']['Movement']={'X':160,'Y':-28};fx['Emitter']['FadeIn']=12;fx['Emitter']['FadeOut']=25;fx['Emitter']['TotalTime']=190;fx['Emitter']['Layer']=4;fx['Sound']='DUN_Moonlight'
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'twinkle_tackle-v2-test-only.json').write_text(s);(G/'Data/Skill/twinkle_tackle.json').write_text(s)
e=G/'Data/Script/origin/event_battle.lua';bak=Path.home()/'.cache/destiny-test/event-battle-avant-choupinova-v2.lua'
if not bak.exists():shutil.copy2(e,bak)
shutil.copy2(bak,e)
with e.open('a') as f:f.write('\n'+(R/'Sources/impact-choupinova-v2-rotation.lua').read_text())
print('Aura 24 poses ; cœurs centrés 32 poses ; vent féerique global BG ; fiche test-only')
