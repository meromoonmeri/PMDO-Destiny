#!/usr/bin/env python3
"""Les cartes d'édition conservent les 37 couches sans toucher au jeu.

Test structurel uniquement : ne remplace pas l'ouverture de l'éditeur.
"""
from pathlib import Path
import gzip,ijson
ROOT=Path(__file__).resolve().parents[2]
NAMES={'centre':'reverie_centre','nord':'reverie_nord','residentiel':'reverie_residentiel','etang':'reverie_etang'}
def interp(x,pts):
 for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
  if x<=x1:return y0+(y1-y0)*(x-x0)/(x1-x0)
 return pts[-1][1]
def owner(x,y):
 if y<interp(x,[(0,920),(135,920),(400,880),(785,840),(1213,840),(1600,730)]):return 'nord'
 if x<840:return 'centre' if y<1944 else 'residentiel'
 if y<1872:return 'centre'
 return 'etang' if y<interp(x,[(840,2392),(1128,2392),(1250,2360),(1600,2220)]) else 'residentiel'
def sections(raw):
 a=raw.index(b'"Layers":')+len(b'"Layers":');b=raw.index(b'"AssetName":');assert raw[b-1:b]==b','
 return raw[:a],raw[b-1:]
def items(path):
 f=path.open('rb');assert f.read(3)==b'\xef\xbb\xbf';return f,ijson.items(f,'Object.Layers.item')
source=ROOT/'game/Data/Ground/WaterfallVillageCapital_Dev.rsground'
owners=[[owner(x*8+4,y*8+4) for y in range(500)] for x in range(200)]
for sector,name in NAMES.items():
 orig=ROOT/'game/Data/Ground'/f'{name}.rsground';edit=ROOT/'game/Data/Ground'/f'{name}_Dev.rsground'
 old=orig.read_bytes();new=edit.read_bytes();before,after=sections(old);got_before,got_after=sections(new)
 assert before==got_before,'collisions ou autres données précédant les couches altérées'
 assert got_after==after.replace(f'"AssetName":"{name}"'.encode(),f'"AssetName":"{name}_Dev"'.encode(),1),'décorations ou entités altérées'
 del old,new,before,after,got_before,got_after
 integral=[[0]*501 for _ in range(201)]
 for x in range(200):
  n=0
  for y in range(500):
   n+=owners[x][y]==sector;integral[x+1][y+1]=integral[x][y+1]+n
 mask=[]
 for x in range(200):
  a=max(0,x-176);b=min(200,x+177);row=bytearray(500)
  for y in range(500):
   c=max(0,y-176);d=min(500,y+177);row[y]=bool(integral[b][d]-integral[a][d]-integral[b][c]+integral[a][c])
  mask.append(row)
 f,g=items(source);h,j=items(edit);count=kept=removed=0
 try:
  for base,current in zip(g,j):
   count+=1;assert {k:v for k,v in base.items() if k!='Tiles'}=={k:v for k,v in current.items() if k!='Tiles'}
   assert len(base['Tiles'])==len(current['Tiles'])==200
   for x in range(200):
    assert len(base['Tiles'][x])==len(current['Tiles'][x])==500
    for y,(oldtile,newtile) in enumerate(zip(base['Tiles'][x],current['Tiles'][x])):
     if mask[x][y]:assert oldtile==newtile,(sector,count,x,y);kept+=bool(oldtile)
     else:assert not newtile,(sector,count,x,y);removed+=bool(oldtile)
  assert count==37 and next(g,None) is None and next(j,None) is None and kept and removed
 finally:f.close();h.close()
 assert (ROOT/'game/Data/Script/destiny/ground'/f'{name}_Dev'/'init.lua').is_file()
 print('PASS',name+'_Dev : 37 couches, données de quartier intactes,',kept,'tuiles conservées,',removed,'distantes masquées')
