"""Import the actual DS-edge artwork without replacing a single old Destiny terrain pixel."""
import json
from pathlib import Path
from PIL import Image
from scipy import ndimage as nd
import numpy as np

D=Path(__file__).resolve().parents[1]; C=D/'Calques'/'Extension-EoS'; S=D/'Sources'/'Extension-EoS'
W,H=3216,1808; OFFSET=(464,272); N=Image.Resampling.NEAREST; M=4
Z={
 'nacrebrune':('Grande Île de Nacrebrune','île',(56,490)),
 'sillons':('Archipel des Sillons','archipel',(458,93)),
 'aube':('Îles de l’Aube','archipel',(1305,107)),
 'grand-frimas':('Île du Grand-Frimas','île',(2130,80)),
 'cendres':('Île des Cendres d’Or','île',(218,1242)),
 'cuivre':('Archipel des Caps de Cuivre','archipel',(2452,1292)),
 'sylverive':('Grande Île de Sylverive','île',(1303,1383)),
 'jade':('Couronne de Jade','archipel',(2690,599)),
}
ORDER=['etang-saules','cap-cisail','pierres-olivine','grotte-frimas','verger-aube','terrasses-orge','lac-veilles','vestiges-braises']
CIRCUIT=['lac-veilles','terrasses-orge','verger-aube','grotte-frimas','pierres-olivine','cap-cisail','etang-saules','vestiges-braises']

def load(p):return json.loads(p.read_text())

def elargir(terr,labels,owners,atlas_sites,placements,add_area,area_id):
 spec=load(S/'Lieux.json');src=load(C/'Placements.json');assert set(spec)==set(src)==set(Z)
 ox,oy=OFFSET;sw,sh=terr.size
 original=np.asarray(terr)
 rendered=Image.new('RGBA',(W,H));rendered.alpha_composite(terr,OFFSET);layer=Image.new('RGBA',(W,H))
 lands=np.zeros((H,W),dtype=np.int32);wide=np.zeros((H,W),dtype=np.int16)
 z=np.s_[oy:oy+sh,ox:ox+sw];lands[z]=labels;wide[z]=owners;last=int(lands.max());tail=[]
 for v in placements.values():v['origine']=[v['origine'][0]+ox,v['origine'][1]+oy]
 for s in atlas_sites:
  for field in ('point','loc'):s[field]=[s[field][0]+ox,s[field][1]+oy]
 for area,(name,kind,(x0,y0)) in Z.items():
  add_area(area,name,'Grand Large')
  art=Image.open(C/(area+'.png')).convert('RGBA'); im=art.resize((art.width*M,art.height*M),N);iw,ih=im.size; m=np.asarray(im)[...,3]>0
  distance=nd.distance_transform_edt(np.asarray(rendered)[...,3]==0)
  moves=sorted((dx*dx+dy*dy,dx,dy) for dx in range(-60,61,4) for dy in range(-64,65,4))
  for _,dx,dy in moves:
   x,y=x0+dx,y0+dy
   if x<36 or y<36 or x+iw>W-36 or y+ih>H-36:continue
   if float(distance[y:y+ih,x:x+iw][m].min())>=30:break
  else:raise ValueError(f'No berth for {area}')
  chunk=np.s_[y:y+ih,x:x+iw]
  p,n=nd.label(m,structure=np.ones((3,3),bool)); ids=np.arange(last,last+n+1,dtype='int32');ids[0]=0;idx=ids[p];last+=n
  lands[chunk][m]=idx[m];wide[chunk][m]=area_id[area];rendered.alpha_composite(im,(x,y));layer.alpha_composite(im,(x,y))
  record=src[area];assert n==record['silhouettes'],(area,n,record['silhouettes']);placements[area]={**record,'origine':[x,y],'dimensions':[iw,ih],'origine_EoS':record['position'],'dimensions_EoS':record['dimensions'],'type':kind}
  for id,nom,cat,(u,v),text in spec[area]:
   ax,ay=u*M+M//2,v*M+M//2;assert m[ay,ax],(area,id,(u,v))
   pos=[x+ax,y+ay]; tail.append({'id':id,'name':nom,'area':area,'island':int(idx[ay,ax]),'category':cat,'region':name,'text':text,'loc':pos.copy(),'point':pos.copy(),'new':True,'realm':'Grand Large','motif_ds':[record['position'][0]+u,record['position'][1]+v]})
 assert len(tail)==50 and len({s['id'] for s in tail})==50
 atlas_sites.extend(tail)
 old_mask=original[...,3]>0; assert np.array_equal(np.asarray(rendered)[z][old_mask],original[old_mask])
 layer.save(D/'Calques/03-Grand-Large.png',optimize=True)
 placements['noyau_origine']={'origine':list(OFFSET),'dimensions':[sw,sh],'pixels_terrain_identiques':int(old_mask.sum())}
 return rendered,lands,wide,tail
