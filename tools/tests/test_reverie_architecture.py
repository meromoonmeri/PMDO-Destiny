#!/usr/bin/env python3
"""Contrôle 11 calques, index de tuiles et compilation non destructive."""
from pathlib import Path
import hashlib,ijson,json,sys,tempfile,gzip
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'));import compiler_carte_reverie as compiler
GAME=ROOT/'game';dev=GAME/'Data/Ground/WaterfallVillageCapital_Dev.rsground';jeu=GAME/'Data/Ground/WaterfallVillageCapital.rsground';tiles=GAME/'Content/Tile'
assert dev.is_file() and jeu.is_file();assert (GAME/'Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_bytes()==(GAME/'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_bytes()
assert len(list(tiles.glob('Reverie_Geo_*.tile')))==14 and (tiles/'Reverie_Corrections_Audit.tile').is_file()
lot=json.loads((ROOT/'tools/reverie_polish_manifest.json').read_text(encoding='utf-8'))
names=[];water=0;seq=[];durations={}
with dev.open('rb') as f:
 assert f.read(3)==b'\xef\xbb\xbf'
 for i,layer in enumerate(ijson.items(f,'Object.Layers.item')):
  names.append(layer['Name']);seq.append(0);assert layer['Visible'] and layer['Layer']==(4 if i==10 else 0)
  for col in layer['Tiles']:
   for cell in col:
    for anim in cell.get('Layers',[]):
     seq[i]+=1
     subset=[fr for fr in anim['Frames'] if fr['Sheet']=='Reverie_Geo_11_Cascades_frames']
     if subset:
      assert all(not fr['Sheet'] or fr in subset for fr in anim['Frames']);assert len(anim['Frames'])==4 and anim['FrameLength'] in (6,10);water+=1;durations[anim['FrameLength']]=durations.get(anim['FrameLength'],0)+1
assert names==['Base','Cliffs','River','Layer 4','Objects Under','Objects Under Anim','Objects','Objects Anim','Objects Over','Objects Over Anim','Fringe']
assert water==736 and durations=={10:704,6:32},(water,durations)
# Interdire toute dérive de calque hors Base (aplats statiques composés) et Objects (arbres).
avant,apres=lot['pistes']['avant'],lot['pistes']['apres']
assert seq==apres and sum(avant)==177423
assert [i for i,(a,b) in enumerate(zip(avant,apres)) if a!=b]==[0,6]
assert avant[0]-apres[0]==sum(z['pistes_statiques_regroupees'] for z in lot['chemins'])
assert apres[6]-avant[6]==76*len(lot['arbres'])-sum(a['cellules_rognées'] for a in lot['arbres'])
with gzip.open(ROOT/'tools/reverie_reference_0.4.19/WaterfallVillageCapital_Dev.rsground.gz','rb') as f:
 assert f.read(3)==b'\xef\xbb\xbf';assert sum(1 for _ in ijson.items(f,'Object.Layers.item'))==37
with tempfile.TemporaryDirectory() as tmp:
 dst=Path(tmp)/'test.rsground';compiler.compile_map(dev,tiles,dst)
 assert hashlib.sha256(dst.read_bytes()).digest()==hashlib.sha256(jeu.read_bytes()).digest()
 existing=Path(tmp)/'personnel.rsground';existing.write_bytes(b'proteger')
 try:compiler.compile_map(dev,tiles,existing);raise AssertionError('Destination existante non protégée')
 except ValueError:pass
 assert existing.read_bytes()==b'proteger'
print('PASS 11 calques, cascades, compilation exacte et protection des fichiers ; témoin historique 37 calques.')
