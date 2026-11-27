#!/usr/bin/env python3
"""Brouillon Gare au Ronflex : fiche test-only, sans modifier le jeu.

L'effet reprend les textures natives de Giga Impact (type Normal), l'attaque de
base de la capacité Z. Les deux images IA expérimentales ne sont pas utilisées.
"""
from pathlib import Path
import copy
import json

H = Path.home()
G = H / '.cache/destiny-test/game/PMDO-Destiny'
P = H / 'Capacites-Z/Prototypes/Gare-au-Ronflex/Generation-PMDO'
P.mkdir(parents=True, exist_ok=True)

def lire(nom):
    return json.loads((G / 'Data/Skill' / (nom + '.json')).read_text(encoding='utf-8-sig'))

fiche = lire('pulverizing_pancake')
assert not fiche['Object']['Released'], 'La fiche source doit être la version non publiée.'
capacite = fiche['Object']
capacite['Released'] = True  # uniquement pour une future copie de banc
capacite['BaseCharges'] = 1
# La fiche native a déjà la puissance 210, la catégorie physique et le type Normal.
assert capacite['Data']['Element'] == 'normal' and capacite['Data']['Category'] == 1
assert any(x.get('Power') == 210 for x in capacite['Data']['SkillStates'])
capacite['Data']['SkillStates'].insert(0, {'$type':'PMDC.Dungeon.ContactState, PMDC'})
# Dash de Rebond : saut jusqu'à la première cible ou au mur ; l'amplitude
# et la lisibilité de la chute doivent encore être vérifiées visuellement.
action = copy.deepcopy(lire('bounce')['Object']['HitboxAction'])
action['Range'] = 3
action['StopAtHit'] = True
action['StopAtWall'] = True
action['HitTiles'] = False
action['TargetAlignments'] = 4
action['ActionFX']['Sound'] = 'DUN_Giga_Impact'
capacite['HitboxAction'] = action
# Uniquement le visuel de Giga Impact, sans sa zone ni sa destruction de murs.
impact = copy.deepcopy(lire('giga_impact')['Object']['Explosion']['ExplodeFX'])
impact['Sound'] = 'EVT_Tackle'
capacite['Data']['HitFX'] = impact
for nom in ('Giga_Impact_Back.dir', 'Giga_Impact_Front.dir'):
    assert (G / 'Content/Particle' / nom).is_file(), nom
(P / 'pulverizing_pancake-brouillon-test-only.json').write_text(json.dumps(fiche, ensure_ascii=False, indent=2), encoding='utf-8')
print('Brouillon créé ; aucune installation ni aucun test effectués.')
