#!/usr/bin/env python3
"""Contrôle 11 calques, index de tuiles et compilation non destructive."""
from pathlib import Path
import hashlib,ijson,sys,tempfile,gzip
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'));import compiler_carte_reverie as compiler
GAME=ROOT/'game';dev=GAME/'Data/Ground/WaterfallVillageCapital_Dev.rsground';jeu=GAME/'Data/Ground/WaterfallVillageCapital.rsground';tiles=GAME/'Content/Tile'
assert dev.is_file() and jeu.is_file();assert (GAME/'Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_bytes()==(GAME/'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_bytes()
assert len(list(tiles.glob('Reverie_Geo_*.tile')))==14 and (tiles/'Reverie_Corrections_Audit.tile').is_file()
names=[];water=0;seq=0
with dev.open('rb') as f:
 assert f.read(3)==b'\xef\xbb\xbf'
 for i,layer in enumerate(ijson.items(f,'Object.Layers.item')):
  names.append(layer['Name']);assert layer['Visible'] and layer['Layer']==(4 if i==10 else 0)
  for col in layer['Tiles']:
   for cell in col:
    for anim in cell.get('Layers',[]):
     seq+=1
     subset=[fr for fr in anim['Frames'] if fr['Sheet']=='Reverie_Geo_11_Cascades_frames']
     if subset:
      assert all(not fr['Sheet'] or fr in subset for fr in anim['Frames']);assert len(anim['Frames'])==4 and anim['FrameLength']==10;water+=1
assert names==['Base','Cliffs','River','Layer 4','Objects Under','Objects Under Anim','Objects','Objects Anim','Objects Over','Objects Over Anim','Fringe'];assert water==736 and seq==177101,(water,seq)
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
