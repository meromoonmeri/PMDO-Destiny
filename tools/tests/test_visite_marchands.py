#!/usr/bin/env python3
"""Préserve la visite au centre et vérifie les réponses de chaque marchand."""
from pathlib import Path
import shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
city=(ROOT/'game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf8')
dev=(ROOT/'game/Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_text(encoding='utf8')
assert city==dev
scene=city[city.index('function ville.Visite()'):city.index('local function position_partenaire_retour')]
assert "CH('NewObject_4'), CH('NewObject_3'), CH('NewObject_24')" in scene
for name in ['kecleon','kangourex','alakazam','mordudor','forgelina']:
 assert f'if {name} ~= nil then' in scene and f'parler({name},' in scene,name
for coordinate in ['GAME:MoveCamera(1104, 992','GAME:MoveCamera(360, 1100','GAME:MoveCamera(504, 1040']:assert coordinate in scene
# Les répliques originales restent dans le même ordre et l’équipe garde la fin.
previous=['Nous y voilà ! Bienvenue','Le jour se lève. Reste avec moi','Après cette nuit, tu n’arrives pas ici tout seul','Voici la place. Les chemins','Là-bas, c’est la boutique de','Bienvenue ! Une pomme ou une baie','C’est ça : on vérifiera notre sac','Et voici ','Confiez-moi vos affaires','Exactement : ce que nous laissons','Juste à côté, il y a aussi cet étal','Et de l’autre côté de la place','Tu ne te souviens toujours pas de ton passé','Tu n’as pas besoin de tout retenir','Pour l’instant, reposons-nous']
pos=-1
for text in previous:
 pos=scene.index(text,pos+1)
assert "SV.Destiny.VisiteVille = 'terminee'" in scene and 'retour_au_joueur(hero, partenaire)' in scene
assert all(s not in scene for s in ['530, 2350','800, 530','1425, 320'])
lua=shutil.which('lua5.4')
if lua:subprocess.run([lua,str(ROOT/'tools/tests/test_visite_marchands.lua'),str(ROOT)],check=True)
else:print('Lua 5.4 absent : simulation à lancer séparément.')
print('PASS visite au centre, cinq commerçants et dialogue d’origine préservé')
