#!/usr/bin/env python3
"""Banc expérimental : aura et pluie de cœurs étoilés, sources IA recomposées."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,json,copy,shutil,math
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Impact-Choupinova/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
def cut(name,limit):
 im=Image.open(P/name).convert('RGB');im.thumbnail((limit,limit),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');m=(b[:,:,1]>125)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45)
 result=Image.fromarray(np.dstack((a,np.where(m,0,255).astype('uint8'))),'RGBA');return result.crop(result.getbbox())
def scaled(im,w,h):return im.resize((max(1,w),max(1,h)),Image.Resampling.NEAREST)
def bank(name,frames,N):
 sheet=Image.new('RGBA',(N*len(frames),N*8));control=Image.new('RGBA',(N*len(frames),N),(32,27,36,255))
 for row in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
 for i,f in enumerate(frames):control.alpha_composite(f,(N*i,0))
 control.convert('RGB').save(P/(name+'-progression.png'));sheet.save(P/(name+'.Dir8.png'));out=io.BytesIO();sheet.save(out,format='PNG');b=out.getvalue();path=P/(name+'.dir');path.write_bytes(struct.pack('<q',len(b))+b+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(path,G/'Content/Particle'/path.name)
heart=cut('coeur-etoile-source.png',64);aura=cut('aura-feerique-source.png',96);boom=cut('explosion-feerique-source.png',100)
# Aura de rotation : couronne radiale sans masquer le personnage, étincelles tournantes.
N=128;aur=[]
for i in range(24):
 im=Image.new('RGBA',(N,N));factor=min(1,(i+1)/5)*min(1,(24-i)/5);w=int(68+factor*25+math.sin(i*.5)*3);h=int(w*.65);ring=scaled(aura,w,h);ring.putalpha(ring.getchannel('A').point(lambda x:x*int(225*factor)//255));im.alpha_composite(ring,((N-w)//2,(N-h)//2+8));d=ImageDraw.Draw(im)
 for k in range(8):
  ang=k*math.tau/8+i*.18;x=int(64+43*math.cos(ang));y=int(69+23*math.sin(ang));r=1+(k+i)%3;col=(255,218,244,int(220*factor));d.line((x-r,y,x+r,y),fill=col);d.line((x,y-r,x,y+r),fill=col)
 aur.append(im)
bank('Choupinova_Aura',aur,N)
# 3 cœurs séparés tombent l'un après l'autre au même impact, chacun explose.
# L'ensemble de l'effet est ancré à la cible. Un seul calcul de dégâts par cible.
N=192;frames=[];meteor=scaled(heart,29,48)
for t in range(38):
 im=Image.new('RGBA',(N,N));d=ImageDraw.Draw(im);ground=105
 for j,(offset,xoff) in enumerate([(0,-19),(5,20),(10,0)]):
  q=t-offset
  if 0<=q<9:
   # Départ haut dans l'image, chute vers la case cible.
   y=ground-115+int(q*11);im.alpha_composite(meteor,(96+xoff-14,y))
  if 9<=q<21:
   k=q-9;sz=int([17,33,50,65,69,72,68,63,57,47,36,21][k]);b=scaled(boom,sz,sz);alpha=255 if k<6 else max(0,255-(k-5)*39);b.putalpha(b.getchannel('A').point(lambda a:a*alpha//255));im.alpha_composite(b,(96+xoff-sz//2,ground-sz//2))
   for z in range(4):
    ang=z*math.pi/2+j*.8;rad=7+k*2;x=round(96+xoff+rad*math.cos(ang));y=round(ground+rad*math.sin(ang)*.7);d.point((x,y),fill=(255,220,255,max(0,255-k*18)))
 frames.append(im)
bank('Choupinova_Pluie_Impact',frames,N)
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
original=read('twinkle_tackle');op=P/'twinkle_tackle-original.json'
if not op.exists():op.write_text(json.dumps(original,indent=2,ensure_ascii=False))
else:original=json.loads(op.read_text())
z=copy.deepcopy(original);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=1
for state in a['Data']['SkillStates']:
 if state.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):state['Power']=85
# Zone testable : Full rayon 2, ciblage ennemis. Pas de conversion ni de règle Z.
act=copy.deepcopy(json.loads((R/'Prototypes/Eruption-Geo-Sismique/Generation-PMDO/tectonic_rage-test-only.json').read_text())['Object']['HitboxAction']);act['PreActions']=[];act['ActionFX']['Sound']='DUN_Healing_Wish';act['ActionFX']['ScreenMovement']={'MinShake':0,'MaxShake':0,'MaxShakeTime':0}
hit=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']='Choupinova_Pluie_Impact';hit['Emitter']['Anim']['Anim']['FrameTime']=2;hit['Emitter']['LocHeight']=0;hit['Delay']=46;hit['AbsoluteDelay']=True;hit['Sound']='DUN_Sweet_Kiss';a['HitboxAction']=act;a['Data']['HitFX']=hit
a['Data']['BeforeActions'].append({'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'Choupinova_Rotation','ArgTable':'{}'}})
text=json.dumps(z,indent=2,ensure_ascii=False);(P/'twinkle_tackle-test-only.json').write_text(text);(G/'Data/Skill/twinkle_tackle.json').write_text(text)
event=G/'Data/Script/origin/event_battle.lua';bak=Path.home()/'.cache/destiny-test/event-battle-avant-choupinova.lua'
if not bak.exists():shutil.copy2(event,bak)
shutil.copy2(bak,event)
with event.open('a') as f:f.write('\n'+(R/'Sources/impact-choupinova-rotation.lua').read_text())
print('24 poses aura, 38 poses chute + explosions ; fiche + événement temporaires')
