#!/usr/bin/env python3
"""Ébauche isolée Dracacophonie : ondes PMD natives + discret complément IA.
Ce fichier ne modifie ni le jeu ni l'intégration. Le bonus conditionnel reste à implémenter.
"""
from pathlib import Path
from PIL import Image
import json,copy,io,struct
import numpy as np
H=Path.home(); G=H/'.cache/destiny-test/game/PMDO-Destiny'; P=H/'Capacites-Z/Prototypes/Dracacophonie-Flamboyante/Generation-PMDO'
def read(n): return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
# Découpe de la petite onde IA. Pixelisation, pas de grande illustration plaquée.
a=np.array(Image.open(P/'source-ia-vague-pmd-v2.png').convert('RGB')); mask=(a[:,:,2]>a[:,:,1]*1.15)&(a[:,:,2]>60)
y,x=np.where(mask); crop=a[y.min():y.max()+1,x.min():x.max()+1]; m=mask[y.min():y.max()+1,x.min():x.max()+1]
r=Image.fromarray(np.dstack((crop,m.astype('uint8')*255)),'RGBA').resize((32,32),Image.Resampling.NEAREST)
frames=[]
for i in range(12):
 s=max(3,round(3+29*i/11)); f=Image.new('RGBA',(32,32)); v=r.resize((s,s),Image.Resampling.NEAREST)
 if i>=9:v.putalpha(v.getchannel('A').point(lambda x: x*(12-i)//3))
 f.alpha_composite(v,((32-s)//2,(32-s)//2));frames.append(f)
sheet=Image.new('RGBA',(32*len(frames),32*8))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(32*i,32*row))
b=io.BytesIO();sheet.save(b,format='PNG'); raw=b.getvalue();(P/'Dracaco_Onde_IA.dir').write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',32,32,4,len(frames)))
# Une ébauche de fiche isolée : mise en forme et ciblage, pas de bonus non vérifié.
z=read('clangorous_soulblaze');a=z['Object'];a['Released']=True;a['BaseCharges']=1
states=a['Data']['SkillStates'];states.append({'$type':'PMDC.Dungeon.SoundState, PMDC'})
act=copy.deepcopy(read('clanging_scales')['Object']['HitboxAction']);act.update(Range=1,TargetAlignments=4,HitTiles=False,Speed=5)
# Les ondes bleues restent natives ; la petite onde IA complète plutôt que remplacer.
native=act['Emitter']; ia=copy.deepcopy(native);ia['Anims'][0]['Anim']['AnimIndex']='Dracaco_Onde_IA';ia['Anims'][0]['Anim']['FrameTime']=2;ia['ParticlesPerTile']=0.35
act['Emitter']={'$type':'RogueEssence.Content.MultiCircleSquareEmitter, RogueEssence','LocHeight':0,'finished':False,'Emitters':[native,ia]}
act['ActionFX']['Sound']='DUN_Dragon_Pulse';a['HitboxAction']=act
# Réemploie l'impact et les particules Dragon de Dracochoc.
a['Data']['HitFX']=copy.deepcopy(read('dragon_pulse')['Object']['Data']['HitFX'])
a['Data']['AfterActions']=[]
(P/'clangorous_soulblaze-ebauche-pmd-non-testee.json').write_text(json.dumps(z,ensure_ascii=False,indent=2))
print('Ébauche isolée enregistrée. Aucun test et aucun bonus réalisés.')
