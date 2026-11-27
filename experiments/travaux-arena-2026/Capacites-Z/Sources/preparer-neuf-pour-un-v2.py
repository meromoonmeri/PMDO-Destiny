#!/usr/bin/env python3
"""Prototype Neuf pour Un : création uniquement, pas d'installation dans le jeu."""
from pathlib import Path
from PIL import Image,ImageDraw
import io,struct,math,json,copy
import numpy as np
H=Path.home(); G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Neuf-pour-Un/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
names=[(134,'Aquali',(70,180,255)),(135,'Voltali',(255,224,55)),(136,'Pyroli',(255,125,55)),(196,'Mentali',(213,135,255)),(197,'Noctali',(247,212,90)),(470,'Phyllali',(137,224,90)),(471,'Givrali',(126,235,255)),(700,'Nymphali',(255,153,208))]
sprites=[]
for num,name,col in names:
 b=(G/'Content/Chara'/f'{num}.chara').read_bytes();pos=b.find(b'\x89PNG\r\n\x1a\n');assert pos>7
 size=struct.unpack_from('<q',b,pos-8)[0];im=Image.open(io.BytesIO(b[pos:pos+size])).convert('RGBA');w,h,_,_=struct.unpack_from('<iiii',b,pos+size)
 im=im.crop((0,0,w,h));im=im.crop(im.getbbox());im.thumbnail((27,28),Image.Resampling.NEAREST);sprites.append(im)
# L'image IA retenue par l'utilisateur : uniquement la seconde, étoile rayonnante.
def chroma_key(path):
 im=Image.open(path).convert('RGB');arr=np.asarray(im).astype('float32');r,g,b=arr[:,:,0],arr[:,:,1],arr[:,:,2]
 score=np.maximum(r,b)
 opacity=np.where(g>score,1-(g-score)/255,1)
 opacity=np.clip((opacity-.14)/.86,0,1)
 # Retire la contamination du fond vert sur les contours partiellement transparents.
 safe=np.maximum(opacity,1/255);out=arr.copy();out[:,:,1]=np.minimum(np.clip((g-255*(1-opacity))/safe,0,255),score+18)
 out=np.dstack([np.clip(out,0,255).astype('uint8'),(opacity*255).astype('uint8')]);res=Image.fromarray(out,'RGBA')
 return res.crop(res.getbbox())
star=chroma_key(P/'source-ia-energie-centrale.png')
star.thumbnail((150,150),Image.Resampling.LANCZOS)
star.save(P/'etoile-ia-detouree.png')
# Deux couches séparées : l'étoile IA et les rayons derrière Évoli ; ses évolutions devant.
N=160;T=72;backs=[];fronts=[]
for t in range(T):
 bg=Image.new('RGBA',(N,N));fg=Image.new('RGBA',(N,N));d=ImageDraw.Draw(bg);cx=80;cy=79
 fade=min(1,(T-t)/8)
 if t>=19:
  appear=min(1,(t-19)/14)*fade;scale=.78+.22*min(1,(t-19)/14);sz=max(1,round(134*scale))
  aura=star.resize((sz,sz),Image.Resampling.LANCZOS)
  aura.putalpha(aura.getchannel('A').point(lambda v:round(v*appear*.62)))
  bg.alpha_composite(aura,(cx-sz//2,cy-sz//2));d=ImageDraw.Draw(bg)
 for j,((num,name,col),sprite) in enumerate(zip(names,sprites)):
  a=-math.pi/2+j*math.tau/8;x=cx+58*math.cos(a);y=cy+46*math.sin(a)+math.sin(t*.13+j)*1.2
  reveal=max(0,min(1,(t-j*3)/6))*fade
  if not reveal:continue
  if t>=32:
   beam=min(1,(t-32)/10);sx=x+(cx-x)*.16;sy=y+(cy-y)*.16;ex=sx+(cx-sx)*beam;ey=sy+(cy-sy)*beam
   d.line((sx,sy,ex,ey),fill=(*col,int(120*reveal)),width=3);d.line((sx,sy,ex,ey),fill=(255,255,239,int(210*reveal)),width=1)
  temp=sprite.copy();temp.putalpha(temp.getchannel('A').point(lambda v:int(v*reveal)))
  fg.alpha_composite(temp,(round(x-temp.width/2),round(y-temp.height/2)))
 backs.append(bg);fronts.append(fg)
def bank(name,frames):
 sheet=Image.new('RGBA',(N*T,N*8))
 for r in range(8):
  for i,im in enumerate(frames):sheet.alpha_composite(im,(N*i,N*r))
 b=io.BytesIO();sheet.save(b,format='PNG');raw=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,T))
bank('NeufPourUnV2_Rayons',backs);bank('NeufPourUnV2_Evolitions',fronts)
preview=Image.new('RGBA',(N*9,N),(25,26,35,255))
for i,t in enumerate([0,9,18,27,36,45,54,63,71]):
 preview.alpha_composite(backs[t],(N*i,0));preview.alpha_composite(fronts[t],(N*i,0))
preview.convert('RGB').save(P/'progression-neuf-pour-un-v2.png')
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
orig=read('extreme_evoboost');assert not orig['Object']['Released'], 'Le jeu de référence doit rester intact'
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1
act=copy.deepcopy(read('quiver_dance')['Object']['HitboxAction']);act['PreActions']=[];act['CharAnimData']['ActionType']=5;act['ActionFX']['Sound']='DUN_Wish';a['HitboxAction']=act
a['Explosion']['TargetAlignments']=1
sample=copy.deepcopy(read('quiver_dance')['Object']['Data']['OnHits'][0]);a['Data']['OnHits']=[]
for key in ['mod_attack','mod_defense','mod_special_attack','mod_special_defense','mod_speed']:
 e=copy.deepcopy(sample);e['Value']['Stack']=2;e['Value']['StatusID']=key;a['Data']['OnHits'].append(e)
a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'NeufPourUnV2_Visuel','ArgTable':'{}'}}]
a['Data']['HitFX']=copy.deepcopy(read('quiver_dance')['Object']['Data']['HitFX'])
(P/'extreme_evoboost-v2-test-only.json').write_text(json.dumps(z,indent=2,ensure_ascii=False))
print('Neuf pour Un : huit sprites PMDO, 72 images, fiche self + cinq boosts ; aucun jeu modifié.')
