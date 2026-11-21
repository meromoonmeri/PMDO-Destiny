#!/usr/bin/env python3
"""Produit le terrain fixe du duel à partir de l'arène au sol du Dojo Kingambit.

python tools/build_duel_reverie.py --source . --out /copie/duel
L'animation 12 phases est conservée en tuiles donjon 24×24 ; ni la carte
au sol, ni les planches d'origine, ni les zones existantes ne sont modifiées.
"""
from copy import deepcopy
import argparse
import json
from pathlib import Path

from lib_tiles import write_tilesheet
import render_ground_moteur as render

MAP = 'reverie_duel_liane'
BANK = 'Reverie_Duel_Liane_24'
ZONE = 'reverie_duel'


def lire(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def ecrire(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, separators=(',', ':'))
        f.write('\n')


def cellule(pistes):
    return {'AutoTileset': '', 'Associates': [], 'Layers': pistes, 'NeighborCode': -1}


def convertir(source, out):
    render.ROOT = source
    render.Planches._slots.clear()
    render.Planches._tiles.clear()
    data = source/'game/Data'
    ground = lire(data/'Ground/dojo_kingambit_arene.rsground')['Object']
    modele = lire(data/'Map/end_grotte_verdoyante.rsmap')
    zone = lire(data/'Zone/dazzling_fight.json')
    carte, z = modele['Object'],zone['Object']
    banque, uniques = {}, {}

    def frame(tuile):
        if tuile.getbbox() is None:
            return {'Sheet': '', 'TexLoc': {'X': 0, 'Y': 0}}
        pixels = tuile.tobytes()
        if pixels not in uniques:
            n = len(banque)
            xy = n%48, n//48
            uniques[pixels] = xy
            banque[xy] = tuile
        x, y = uniques[pixels]
        return {'Sheet': BANK, 'TexLoc': {'X': x, 'Y': y}}

    def calque(nom, haut):
        g = dict(ground, Layers=[l for l in ground['Layers'] if (l['Layer'] == 4) == haut])
        plan = render.prepare(g)
        assert (plan['W'], plan['H']) == (768, 576)
        phases = 1 if haut else 12
        images = []
        for i in range(phases):
            im, erreurs = render.rendu(plan,i*6*120)
            assert erreurs == 0
            images.append(im)
        tiles = []
        for x in range(32):
            col = []
            for y in range(24):
                rect = (x*24,y*24,(x+1)*24,(y+1)*24)
                fr = [frame(i.crop(rect)) for i in images]
                if all(f == fr[0] for f in fr): fr = fr[:1]
                col.append(cellule([{'Frames': fr, 'FrameLength': 6 if len(fr) > 1 else 60}]
                                   if any(f['Sheet'] for f in fr) else []))
            tiles.append(col)
        return {'Name': nom, 'Layer': 4 if haut else 0, 'Visible': True, 'Tiles': tiles}

    carte['Layers'] = [calque('Arène du Dojo — sol et flammes',False),calque('Arène du Dojo — avant-plan',True)]
    assert not [nom for (nom,x,y), tuile in render.Planches._tiles.items() if nom and tuile is None]
    obstacles = ground['obstacles']

    def libre(x,y):
        return (0 < x < 31 and 0 < y < 23
                and not any(obstacles[x*3+dx][y*3+dy]['Tags'] for dx in range(3) for dy in range(3)))

    carte['Tiles'] = [[{'Data': {'ID': 'floor' if libre(x,y) else 'unbreakable',
                                'TileTex': cellule([]), 'StableTex': False},
                         'Effect': {'TileLoc': {'X': x, 'Y': y}, 'ID': '', 'Revealed': False,
                                    'Owner': 0, 'TileStates': []}}
                        for y in range(24)] for x in range(32)]
    carte['DiscoveryArray'] = [[2]*24 for _ in range(32)]
    assert all(libre(x,y) for x,y in ((16,10),(16,14),(15,14),(17,14),(16,15)))
    carte['EntryPoints'] = [{'Loc': {'X': 16, 'Y': 14}, 'Dir': 4}]
    name = {'DefaultText': 'Kingambit Dojo — Liane’s challenge', 'LocalTexts': {'fr': 'Dojo Kingambit — Duel de Liane'}}
    carte.update(Name=name, AssetName=MAP, Music='Marowak Dojo.ogg', Released=False,
                 Comment='Arène fixe de démonstration ; un seul adversaire. Géométrie du dojo convertie de 8 px en 24 px.',
                 Element='none', HideMinimap=True)
    team = carte['MapTeams'][0]
    ennemi = team['Players'][0]
    team.update(Players=[ennemi], Guests=[], Name='Liane', LeaderIndex=0)
    carte['MapTeams'] = [team]
    forme = {'Species': 'mienfoo','Form': 0,'Skin': 'normal','Gender': 2}
    # Kungfouine Nv. 10 : 27 PV de base + 25 PV d’entraînement.
    # Le bonus (43 × 152 // 256) garde le maximum cohérent avec les 52 PV courants.
    ennemi.update(BaseForm=forme, CurrentForm=deepcopy(forme), Nickname='Liane', Level=10,
                  Element1='fighting', Element2='none', HP=52, MaxHPBonus=43, DefBonus=0, MDefBonus=0,
                  serializationLoc={'X': 16,'Y': 10}, serializationDir=0, Unrecruitable=True)
    capacites = [('pound',25),('meditate',20),('detect',14),('fake_out',19)]
    ennemi['BaseSkills'] = [{'SkillNum': id, 'Charges': pp, 'CanForget': True} for id,pp in capacites]
    ennemi['Skills'] = [{'Element': dict(SkillNum=id, Charges=pp, Enabled=True, Sealed=False), 'BackRef': i}
                        for i,(id,pp) in enumerate(capacites)]
    ennemi['BaseIntrinsics'] = ['inner_focus']
    ennemi['Intrinsics'] = [{'Element': {'ID': 'inner_focus'},'BackRef': 0}]

    z.update(Name=name, Comment='Entraînement facultatif de Liane. Un seul segment fixe, pas d’EXP ni de secours.')
    z['Segments'][0]['Comment'] = 'Manche unique dans le Dojo Kingambit.'
    z['Segments'][0]['Floors'][0]['GenSteps'][0]['Value']['MapID'] = MAP

    fichiers = {
        'map': out/f'game/Data/Map/{MAP}.rsmap',
        'zone': out/f'game/Data/Zone/{ZONE}.json',
        'banque': out/f'game/Content/Tile/{BANK}.tile',
    }
    if any(p.exists() for p in fichiers.values()):
        raise SystemExit('Destination existante : aucun écrasement.')
    for p in fichiers.values(): p.parent.mkdir(parents=True, exist_ok=True)
    ecrire(fichiers['map'],modele)
    ecrire(fichiers['zone'],zone)
    count = write_tilesheet(fichiers['banque'],banque,tile_size=24)
    print(f'{MAP} : 32×24 cellules, {count} tuiles de 24 px, 12 phases animées, adversaire {ennemi["Nickname"]}.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--out',type=Path,required=True)
    a = p.parse_args()
    convertir(a.source,a.out)
