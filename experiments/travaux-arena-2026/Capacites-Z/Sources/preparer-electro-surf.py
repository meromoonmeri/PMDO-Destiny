#!/usr/bin/env python3
"""Produit les banques et une fiche d'essai, sans rien installer dans le jeu."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, math, io, struct, json, copy
H=Path.home(); R=H/'Capacites-Z'; G=H/'.cache/destiny-test/game/PMDO-Destiny'; P=R/'Prototypes/Electro-Surf-Survolte/Generation-PMDO'; P.mkdir(parents=True,exist_ok=True)
def cut(name,n):
 im=Image.open(P/name).convert('RGB'); im.thumbnail((n,n),Image.Resampling.NEAREST); a=np.array(im); b=a.astype('int16'); bg=(b[:,:,1]>125)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45); v=Image.fromarray(np.dstack((a,np.where(bg,0,255).astype('uint8'))),'RGBA'); return v.crop(v.getbbox())
def paste(dst,p,w,h,x,y,a=255):
 if a<=0:return
 w=max(1,int(w));h=max(1,int(h)); s=p.resize((w,h),Image.Resampling.NEAREST);s.putalpha(s.getchannel('A').point(lambda v:v*a//255));dst.alpha_composite(s,(round(x-w/2),round(y-h/2)))
def bank(name,frames,N):
 sheet=Image.new('RGBA',(N*len(frames),N*8));control=Image.new('RGBA',(N*len(frames),N),(35,33,40,255))
 for row in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(N*i,N*row))
 for i,f in enumerate(frames):control.alpha_composite(f,(N*i,0))
 sheet.save(P/(name+'.Dir8.png'));control.convert('RGB').save(P/(name+'-progression.png'));b=io.BytesIO();sheet.save(b,format='PNG');raw=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,len(frames)))
wave=cut('source-vague-electrique.png',110);hit=cut('source-impact-foudre.png',100)
# Onde basse qui laisse le Pokémon et sa queue visibles pendant le déplacement.
N=96;frames=[]
for t in range(12):
 f=Image.new('RGBA',(N,N));w=48+3*math.sin(t*math.tau/12);paste(f,wave,w,26,48,60+math.sin(t*.6)*2,205);d=ImageDraw.Draw(f)
 for j in range(4):
  x=23+((j*13+t*4)%51);y=68+(j%2)*3;d.line((x,y,x-5,y+1),fill=(255,231,114,190),width=1)
 frames.append(f)
bank('ElectroSurf_Vague',frames,N)
# Aura précédant la glissade : VFX en arrière du porteur.
N=96;frames=[]
for t in range(27):
 f=Image.new('RGBA',(N,N));a=int(220*min(1,(t+1)/5,(27-t)/4));paste(f,wave,48+4*math.sin(t*.7),30,48,61,a);d=ImageDraw.Draw(f)
 for j in range(8):
  angle=(math.tau*j/8+t*.16);x=round(48+24*math.cos(angle));y=round(47+18*math.sin(angle));d.line((x,y-2,x,y+2),fill=(255,244,161,a),width=1);d.line((x-2,y,x+2,y),fill=(255,244,161,a),width=1)
 frames.append(f)
bank('ElectroSurf_Charge',frames,N)
# Déflagration dorée et anneau au sol.
N=128;frames=[]
for t in range(28):
 f=Image.new('RGBA',(N,N));k=t;size=[6,14,24,34,46,56,65,72,76,78,76,72,68,62,56,49,42,35,28,20,12,5][min(k,21)];a=255 if k<12 else max(0,255-(k-11)*25)
 if k<22:paste(f,hit,size,size,64,64,a)
 if 3<=k<25:
  d=ImageDraw.Draw(f);q=k-3;r=min(51,7+q*3);d.ellipse((64-r,72-r//3,64+r,72+r//3),outline=(255,228,100,max(0,200-q*9)),width=2)
 frames.append(f)
bank('ElectroSurf_Impact',frames,N)
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
orig=P/'stoked_sparksurfer-original.json'
if not orig.exists():orig.write_text(json.dumps(read('stoked_sparksurfer'),ensure_ascii=False,indent=2))
a=copy.deepcopy(json.loads(orig.read_text(encoding='utf-8-sig')));z=a['Object'];z['Released']=True;z['BaseCharges']=1
# Conserve puissance 175 et catégorie spéciale ; paralyse via l'événement de PMDO,
# qui consulte normalement l'immunité Électrik du statut.
z['Data']['OnHits'].append(copy.deepcopy(read('thunder_wave')['Object']['Data']['OnHits'][0]))
act=copy.deepcopy(read('wild_charge')['Object']['HitboxAction']);act.update(Range=3,StopAtHit=True,StopAtWall=True,TargetAlignments=4,HitTiles=False,SnapBack=True,AppearanceMod=0,CharAnim=5);act['Anim']['AnimIndex']='ElectroSurf_Vague';act['Anim']['FrameTime']=2;act['Emitter']={'$type':'RogueEssence.Content.EmptyAttachEmitter, RogueEssence'};act['PreActions']=[];act['ActionFX']['Sound']='DUN_Shock_Wave';z['HitboxAction']=act
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='ElectroSurf_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=2;fx['Delay']=38;fx['AbsoluteDelay']=True;fx['Sound']='DUN_Thunder';z['Data']['HitFX']=fx
z['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'ElectroSurf_Charge','ArgTable':'{}'}}]
(P/'stoked_sparksurfer-test-only.json').write_text(json.dumps(a,ensure_ascii=False,indent=2));print('Banques et fiche test générées sans installation.')
# Ralentir la ruée uniquement pour le banc : bornes rush/impact/retour de
# l'animation 5 de la forme Alola, sans toucher aux sprites ni aux index.
raw=bytearray((G/'Content/Chara/26.chara').read_bytes());pos=226276
length=struct.unpack_from('<q',raw,pos)[0];cursor=pos+8+length
w,h,shadow,count=struct.unpack_from('<iiii',raw,cursor);cursor+=16+32*count
num=struct.unpack_from('<i',raw,cursor)[0];cursor+=4;found=False
for _ in range(num):
 kind,internal,copied=struct.unpack_from('<iii',raw,cursor);cursor+=12
 if copied>-1:continue
 rush,impact,ret,nseq=struct.unpack_from('<iiii',raw,cursor)
 if kind==5:
  assert (rush,impact,ret,nseq)==(1,2,7,8)
  struct.pack_into('<iii',raw,cursor,1,8,10);found=True
 cursor+=16
 for _ in range(nseq):
  count=struct.unpack_from('<i',raw,cursor)[0];cursor+=4+count*29
assert found
(P/'26-banc-rythme-surf.chara').write_bytes(raw)
print('Animation 5 Alola : déplacement allongé dans une copie de sprite de banc.')
