#!/usr/bin/env python3
"""Patati V3 : abîme de 120 poses et fiche de banc."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,struct,io,math,json
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Patati-Patattrape/Generation-PMDO';V=P/'V3';N=128;T=120
im=Image.open(V/'Sources/abysse.png').convert('RGB');a=np.asarray(im);r,g,b=[a[:,:,i].astype('int16') for i in range(3)];m=(g>50)&(g>r*1.2)&(g>b*1.2);hole=Image.fromarray(np.dstack((a,(~m).astype('uint8')*255)),'RGBA');hole=hole.crop(hole.getbbox()).resize((100,43),Image.Resampling.NEAREST)
def native(n):
 data=(G/'Content/Particle'/f'{n}.dir').read_bytes();l=struct.unpack_from('<q',data)[0];s=Image.open(io.BytesIO(data[8:8+l])).convert('RGBA');w,h,_,c=struct.unpack_from('<iiii',data,8+l);return [s.crop((i*w,0,(i+1)*w,h)) for i in range(c)]
smoke=native('Smoke_Purple');spark=native('Dark_Pulse_Particle')
def paste(f,i,x,y,alpha=1):
 i=i.copy()
 if alpha<1:i.putalpha(i.getchannel('A').point(lambda a:round(a*max(0,alpha))))
 f.alpha_composite(i,(round(x-i.width/2),round(y-i.height/2)))
frames=[]
for t in range(T):
 f=Image.new('RGBA',(N,N));phase=min(1,(t+1)/15);end=min(1,(T-t)/15);pulse=1+.04*math.sin(t*.3);w=round((20+80*phase)*pulse);h=round(10+33*phase);v=hole.resize((w,h),Image.Resampling.NEAREST);paste(f,v,64,78,end)
 # Un rideau noir naît dans l'ouverture et descend, masquant visuellement l'aspiration.
 if 10<=t<96:
  rise=min(1,(t-10)/16);fade=min(1,(96-t)/10);d=ImageDraw.Draw(f);top=round(78-48*rise);bottom=77
  d.polygon([(39,78),(42,top+10),(47,top+6),(49,top+round(4*math.sin(t*.32))),(55,top+9),(61,top),(67,top+7),(73,top+2),(77,top+11),(85,top+8),(89,78)],fill=(7,3,15,round(236*fade)))
  for j in range(4):
   x=45+j*13+round(3*math.sin(t*.27+j));d.line([(x,76),(x+3,60),(x-1,45+round(3*math.sin(t*.25+j)))],fill=(101,42,149,round(225*fade)),width=2)
 for j in range(8):
  age=(t-j*8)%48
  if t>=j*3 and t<108:
   angle=j*math.tau/8+age*.16;rad=36-age*.47;x=64+math.cos(angle)*rad;y=73+math.sin(angle)*rad*.35-age*.36
   v=spark[(age//4)%len(spark)].resize((9,9),Image.Resampling.NEAREST);paste(f,v,x,y,end*.85)
 if 14<=t<100:
  for j in range(3):
   age=(t-14+j*7)%32;v=smoke[min(len(smoke)-1,age//3)].resize((22,22),Image.Resampling.NEAREST);paste(f,v,45+j*19+math.sin(t*.3+j)*4,71-age*.6,min(1,(100-t)/12)*.72)
 frames.append(f)
s=Image.new('RGBA',(N*T,N*8));sheet=Image.new('RGBA',(N*8,N*15))
for row in range(8):
 for i,f in enumerate(frames):s.alpha_composite(f,(i*N,row*N))
for i,f in enumerate(frames):sheet.alpha_composite(f,((i%8)*N,(i//8)*N))
sheet.save(V/'Patati-V3-abysse-120images.png',optimize=True);b=io.BytesIO();s.save(b,format='PNG',optimize=True);data=b.getvalue();(V/'PatatiV3_Abysse.dir').write_bytes(struct.pack('<q',len(data))+data+struct.pack('<iiii',N,N,4,T))
z=json.loads((P/'V2/lets_snuggle_forever-v2-test-only.json').read_text());d=z['Object']['Data'];d['HitFX']['Delay']=0;d['HitFX']['Sound']='';d['HitFX']['Emitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0}
d['BeforeHits']=[{'Key':{'str':[-20]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'PatatiV3_Abysse','ArgTable':'{}'}}]
d['OnHits'].append({'Key':{'str':[1]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'PatatiV3_ChanceKO','ArgTable':'{}'}})
(V/'lets_snuggle_forever-v3-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2))
# Statut neutre détourné uniquement dans la copie de test, pour masquer sans toucher aux actions.
none=json.loads((G/'Data/Status/none.json').read_text(encoding='utf-8-sig'));none['Object']['DrawEffect']=4;(V/'none-visuel-temporaire.json').write_text(json.dumps(none,ensure_ascii=False,indent=2))
print('120 images, fiche et statut visuel de banc préparés.')
