#!/usr/bin/env python3
"""Use the unmodified DS pixels as the centre of the outpainting canvas.
The blank sea tiles and both friezes are also sampled losslessly from S01P01A.
The chroma areas of the briefs are temporary extraction windows, not atlas colours.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw

D=Path(__file__).resolve().parents[1]; S=D/'Sources'/'Extension-EoS'; R=D/'Sources'/'References-Grand-Large'
DS=R/'DS-Carte-echelle-native.png'; N=Image.Resampling.NEAREST
EO=288; W,H=1080,336
PANELS = {
 'Ouest-nord': {'cadre':[0,0,456,168],'fenetre':[0,23,288,168],'terres':[
   ['nacrebrune','Nacrebrune',[32,36,113,114]],['sillons','Archipel des Sillons',[156,63,113,73]]]},
 'Ouest-sud': {'cadre':[0,168,456,336],'fenetre':[0,168,288,313],'terres':[
   ['aube','Îles de l’Aube',[24,193,108,69]],['grand-frimas','Grand-Frimas',[139,225,130,77]]]},
 'Est-nord': {'cadre':[624,0,1080,168],'fenetre':[792,23,1080,168],'terres':[
   ['cendres','Cendres d’Or',[810,58,125,82]],['cuivre','Caps de Cuivre',[945,36,120,82]]]},
 'Est-sud': {'cadre':[624,168,1080,336],'fenetre':[792,168,1080,313],'terres':[
   ['sylverive','Sylverive',[808,214,126,73]],['jade','Couronne de Jade',[951,183,114,113]]]},
}
GUIDES={
 'nacrebrune':'Nacrebrune','sillons':'Archipel-des-Sillons','aube':'Iles-de-l-Aube','grand-frimas':'Grand-Frimas',
 'cendres':'Cendres-d-Or','cuivre':'Caps-de-Cuivre','sylverive':'Sylverive','jade':'Couronne-de-Jade'}

def fond():
 ds=Image.open(DS).convert('RGB'); assert ds.size==(504,336)
 base=Image.new('RGB',(W,H));main=ds.crop((0,24,24,48));rare=ds.crop((0,72,24,96))
 for l in (0,EO+504):
  for col,x in enumerate(range(l,l+EO,24)):
   for row,y in enumerate(range(24,312,24)):
    base.paste(rare if (col*37+row*31+int(l>0)*11)%17 in (4,13) else main,(x,y))
  for x in range(l,l+EO,72):
   base.paste(ds.crop((432,0,504,24)),(x,0));base.paste(ds.crop((0,312,72,336)),(x,312))
 base.paste(ds,(EO,0));assert base.crop((EO,0,EO+504,336)).tobytes()==ds.tobytes()
 return base

def preparations():
 S.mkdir(exist_ok=True);base=fond();base.save(S/'Toile-EoS-native.png',optimize=True)
 (S/'Panneaux.json').write_text(json.dumps(PANELS,ensure_ascii=False,indent=2)+'\n')
 for k,conf in PANELS.items():
  brief=base.copy();d=ImageDraw.Draw(brief);l,y,r,b=conf['fenetre'];d.rectangle((l,y,r-1,b-1),fill='#ff00ff')
  for id,_,(x,y,w,h) in conf['terres']:
   p=Image.open(R/f'{GUIDES[id]}-Silhouette.png').convert('RGB');a=np.asarray(p);m=Image.fromarray((a[...,1]>35).astype('uint8')*255);m=m.crop(m.getbbox()).resize((w,h),N)
   ink={'grand-frimas':'#adc2c4','cendres':'#a98654','jade':'#b7a477'}.get(id,'#c6a255');brief.paste(ink,(x,y,x+w,y+h),m)
  im=brief.crop(conf['cadre']);im.resize((im.width*3,im.height*3),N).save(S/f'Toile-{k}.png',optimize=True)
if __name__=='__main__':preparations()
