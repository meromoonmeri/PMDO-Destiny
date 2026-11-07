#!/usr/bin/env python3
"""Vérifie les PNJ natifs, leur fusion et la visite sans perte de dialogue."""
from pathlib import Path
import gzip,json,shutil,subprocess
R=Path(__file__).resolve().parents[2];ref=R/'tools/reverie_reference_0.4.19';new=R/'payload'
def chars(root,name):
 data=gzip.decompress((root/(name+'.rsground.gz')).read_bytes());a=data.index(b'"MapChars":')+len(b'"MapChars":');b=data.index(b',"GroundObjects":',a);return json.loads(data[a:b])
base_c=chars(ref,'reverie_centre');base_n=chars(ref,'reverie_nord');union={x['EntName']:x for x in base_c+base_n};assert len(union)==len(base_c)+len(base_n)==21
for name in ['reverie_centre','reverie_nord']:
 actuel=chars(new,name);assert {x['EntName']:x for x in actuel}==union,name;print('PASS',name,len(actuel),'habitants natifs')
for name in ['reverie_residentiel','reverie_etang']:
 assert chars(new,name)==chars(ref,name),name;print('PASS',name,len(chars(new,name)),'habitants natifs')
p=R/'game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua';s=p.read_text(encoding='utf8');assert s==(R/'game/Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_text(encoding='utf8');scene=s[s.index('function ville.Visite()'):s.index('local function position_partenaire_retour')]
for txt in ['Bienvenue à [color=#F5D27A]Réverie Town','Tu ne te souviens toujours pas de ton passé','Notre prochaine aventure commencera quand nous serons prêts','GROUND:MoveToPosition(dracaufeu, 827, 1214','GROUND:MoveToPosition(dracaufeu, 900, 1214','parler_accueil(lombre,','parler_accueil(ludicolo,']:assert txt in scene,txt
from executer_lua import run
run(R/'tools/tests/test_habitants_quartiers.lua', R)
print('PASS habitants, accueil et visite ; pas de validation en jeu.')
