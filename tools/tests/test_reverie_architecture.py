#!/usr/bin/env python3
"""Contrôle les deux cartes Réverie et la reconstruction non destructive."""
from pathlib import Path
import hashlib,ijson,json,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import compiler_carte_reverie as compiler
GAME=ROOT/'game';dev=GAME/'Data/Ground/WaterfallVillageCapital_Dev.rsground';jeu=GAME/'Data/Ground/WaterfallVillageCapital.rsground';tiles=GAME/'Content/Tile';manifest=json.loads((ROOT/'tools/reverie_tiles_manifest.json').read_text(encoding='utf-8'))
assert dev.is_file() and jeu.is_file();assert (GAME/'Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_bytes()==(GAME/'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_bytes()
assert len(list(tiles.glob('Reverie_Geo_*.tile')))==14
water=0;layers=0;names=[];allframes=0
with dev.open('rb') as f:
 if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
 for layer in ijson.items(f,'Object.Layers.item'):
  names.append(layer['Name']);assert layer['Layer']==0 and layer['Visible'];layers+=1
  for column in layer['Tiles']:
   for tile in column:
    for anim in tile.get('Layers',[]):
     frames=anim['Frames'];allframes+=sum(1 for t in frames if t['Sheet'])
     subset=[fr for fr in frames if fr['Sheet']=='Reverie_Geo_11_Cascades_frames']
     if subset:
      assert all(not fr['Sheet'] or fr in subset for fr in frames);assert len(frames)==4 and anim['FrameLength']==10;water+=1
assert layers==37 and 'WaterfallVillage-base' in names and 'cascade' in names
assert water==736 and allframes==201661,(layers,water,allframes)
with tempfile.TemporaryDirectory() as tmp:
 dst=Path(tmp)/'test.rsground';compiler.compile_map(dev,tiles,dst)
 assert hashlib.sha256(dst.read_bytes()).digest()==hashlib.sha256(jeu.read_bytes()).digest(),'La carte 11 calques ne correspond pas à la source édition.'
 existing=Path(tmp)/'personnel.rsground';existing.write_bytes(b'proteger')
 try:compiler.compile_map(dev,tiles,existing);raise AssertionError('Destination existante non protégée')
 except ValueError:pass
 assert existing.read_bytes()==b'proteger'
print('OK : 14 banques, 37 calques éditables, compilation à 11, cascades choisies et protection des fichiers.')
