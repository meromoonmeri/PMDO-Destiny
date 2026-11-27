#!/usr/bin/env python3
# Montage expérimental cohérent à partir d'une pose générée : même paire animée par transformation.
from pathlib import Path
from PIL import Image,ImageDraw
import json,copy,io,struct,shutil
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Appel-des-Ombres-Eternelles/Generation-PMDO'; P.mkdir(parents=True,exist_ok=True)
S=80;src=Image.open(P/'pose-04-transparent-64.png').convert('RGBA')
left=src.crop((0,0,32,53));right=src.crop((32,0,64,53))
# (hauteur des mains, écart). 14 poses : portail, surgissement, étreinte, retrait.
poses=[(0,5),(0,5),(10,5),(18,5),(28,5),(38,5),(53,5),(53,3),(53,1),(53,1),(45,2),(28,4),(12,5),(0,5),(0,5)]
backs=[];fronts=[]
for i,(h,gap) in enumerate(poses):
 b=Image.new('RGBA',(S,S));f=Image.new('RGBA',(S,S));db=ImageDraw.Draw(b);df=ImageDraw.Draw(f)
 # Sol et bord avant du portail, dimensions progressives.
 radius=([8,19]+[28]*12+[14])[i];db.ellipse((40-radius,57,40+radius,69),fill=(28,13,39,245),outline=(109,61,145,255),width=2)
 if h:
  for sprite,x,side in [(left,8-gap,'left'),(right,40+gap,'right')]:
   hand=sprite.resize((32,h),Image.Resampling.NEAREST);layer=Image.new('RGBA',(S,S));layer.alpha_composite(hand,(x,62-h));mask=layer.getchannel('A')
   # Pointes internes devant, reste derrière : le centre reste majoritairement libre.
   tip=Image.new('L',(S,S));dt=ImageDraw.Draw(tip)
   dt.rectangle((x+25 if side=='left' else x, max(0,62-h),x+31 if side=='left' else x+6, 62),fill=255)
   import PIL.ImageChops
   fm=PIL.ImageChops.multiply(mask,tip);bm=PIL.ImageChops.subtract(mask,fm)
   bl=layer.copy();bl.putalpha(bm);fl=layer.copy();fl.putalpha(fm);b.alpha_composite(bl);f.alpha_composite(fl)
 df.arc((40-radius,57,40+radius,69),0,180,fill=(131,78,165,255),width=2)
 backs.append(b);fronts.append(f)
for label,frames in [('Arriere',backs),('Avant',fronts)]:
 name='Ombres_Zone_'+label;sheet=Image.new('RGBA',(S*len(frames),S*8))
 for row in range(8):
  for col,img in enumerate(frames):sheet.alpha_composite(img,(col*S,row*S))
 sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',S,S,4,len(frames)));shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
# Planche de contrôle lisible hors jeu.
sheet=Image.new('RGBA',(S*len(poses),S),(26,23,34,255))
for i,(b,f) in enumerate(zip(backs,fronts)):sheet.alpha_composite(b,(i*S,0));sheet.alpha_composite(f,(i*S,0))
sheet.convert('RGB').resize((S*len(poses)*2,S*2),Image.Resampling.NEAREST).save(P/'progression-multicibles-controle.png')
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
orig=json.loads((P/'never_ending_nightmare-original.json').read_text());z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=2
for state in a['Data']['SkillStates']:
 if state.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):state['Power']=100
act=copy.deepcopy(read('petal_blizzard')['Object']['HitboxAction']);act['Range']=2;act['Speed']=10;act['HitTiles']=False;act['TargetAlignments']=4;act['ActionFX']['Sound']='DUN_Night_Shade_3'
# On enlève l'effet de zone générique de Petal Blizzard : seules les cibles touchées reçoivent les mains.
act['Emitter']={'$type':'RogueEssence.Content.EmptyCircleSquareEmitter, RogueEssence','LocHeight':0}
act['TileEmitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0}
hit=copy.deepcopy(read('head_smash')['Object']['Data']['HitFX']);hit['Delay']=0;hit['Sound']='DUN_Night_Shade_2';hit['Emitter']['HeightBack']=4;hit['Emitter']['HeightFront']=4
for key,side in [('AnimBack','Arriere'),('AnimFront','Avant')]:hit['Emitter'][key]['Anim']['AnimIndex']='Ombres_Zone_'+side;hit['Emitter'][key]['Anim']['FrameTime']=4
a['HitboxAction']=act;a['Data']['HitFX']=hit
text=json.dumps(z,indent=2,ensure_ascii=False);(P/'never_ending_nightmare-zone-test-only.json').write_text(text);(G/'Data/Skill/never_ending_nightmare.json').write_text(text)
print('AreaAction Full rayon 2, HitFX BetweenEmitter par cible, 15 poses transformées.')
