#!/usr/bin/env python3
"""Forge le catalogue Lua, la zone et les 18 finales en cellules DTEF natives de PMDO.

python tools/build_dedales_kingambit.py --donnees /jeu/PMDO-Destiny/Data --out /copie/vide
`--source` désigne le dépôt qui fournit les modèles du duel et de la Fosse.
Les ressources DTEF restent dans le jeu de base ; seules les références sont écrites.
"""
from copy import deepcopy
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from dojo_reverie_types import TYPES
from dojo_dtef import Dtef, WIDTH, HEIGHT, START, libre, loc, cell
from dojo_kingambit_troupes import TROUPES, FORMATION, departs

ZONE = 'dojo_kingambit_dedales'
NS = 'RogueEssence.LevelGen.'
ROOT = Path(__file__).resolve().parents[1]


def lire(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def ecrire(p, j):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(j, f, separators=(',', ':'), ensure_ascii=False)
        f.write('\n')



def texte(fr, en=None):
    return {'DefaultText': en or fr, 'LocalTexts': {'fr': fr}}


class Forgeron:
    def __init__(self, source, data, out):
        self.out, self.data = out, data
        d = source/'game/Data'
        self.zone_doc = lire(d/'Zone/reverie_duel.json')
        self.map_doc = lire(d/'Map/reverie_duel_liane.rsmap')
        fosse = d/'Zone/grotte_verdoyante.json'
        if not fosse.is_file():
            fosse = data/'Zone/grotte_verdoyante.json'
        self.model = lire(fosse)['Object']['Segments'][0]
        self.dtef = Dtef(data)
        self.max_level = int(ET.parse(data/'StartParams.xml').getroot().findtext('MaxLevel'))

    def contenu(self, group, name):
        return lire(self.data/group/f'{name}.json')['Object']

    def monstre(self, mon, typ):
        r = self.contenu('Monster',mon)['Forms'][0]
        assert r['Released'] and typ in (r['Element1'],r['Element2']), (mon,typ)
        if r['Intrinsic1'] != 'none': self.contenu('Intrinsic',r['Intrinsic1'])
        return r

    def lignee(self, mon):
        vus = {mon}
        while True:
            parent = self.contenu('Monster',mon)['PromoteFrom']
            if not parent: return
            assert parent not in vus, (mon,parent)
            assert mon in {p['Result'] for p in self.contenu('Monster',parent)['Promotions']}, (parent,mon)
            yield parent
            vus.add(parent)
            mon = parent

    def combattant(self, modele, mon, moves, pos, niveau, bonus):
        c = deepcopy(modele)
        f = self.contenu('Monster',mon)['Forms'][0]
        assert f['Released'], mon
        talent = f['Intrinsic1']
        if talent != 'none': self.contenu('Intrinsic',talent)
        apprises = {sk['Skill'] for esp in (mon,*self.lignee(mon))
                    for key,val in self.contenu('Monster',esp)['Forms'][0].items() if key.endswith('Skills')
                    for sk in val}
        assert not set(moves)-apprises, (mon,set(moves)-apprises)
        gender = 1 if f['MaleWeight'] else (2 if f['FemaleWeight'] else 0)
        form = {'Species': mon, 'Form': 0, 'Skin': 'normal', 'Gender': gender}
        # PMDC MonsterFormData.GetStat : cohérence HP/MaxHP dès l'entrée.
        base = f['BaseHP']
        if base > 1:
            cap = 1536*base//sum(f['Base'+s] for s in ('HP','Atk','Def','MAtk','MDef','Speed'))
            hp = (base+130)*niveau//self.max_level+10 + bonus*(cap-base)//256
        else:
            hp = niveau//10+1 + bonus*(self.max_level//5-self.max_level//10)//256
        c.update(BaseForm=form, CurrentForm=deepcopy(form), Nickname='',
                 Level=niveau, HP=hp, MaxHPBonus=bonus, Element1=f['Element1'], Element2=f['Element2'],
                 serializationLoc=loc(*pos), Unrecruitable=True)
        c['BaseIntrinsics'] = [talent]
        c['Intrinsics'] = [{'Element': {'ID': talent}, 'BackRef': 0}]
        skills = []
        for m in moves:
            skill = self.contenu('Skill',m)
            assert skill['Released'] and skill['BaseCharges']>0, (mon,m)
            skills.append((m,skill['BaseCharges']))
        skills.extend([('',0)]*(4-len(skills)))
        c['BaseSkills'] = [{'SkillNum': m, 'Charges': n, 'CanForget': True} for m,n in skills]
        c['Skills'] = [{'Element': dict(SkillNum=m, Charges=n, Enabled=bool(m), Sealed=False), 'BackRef': i}
                       for i,(m,n) in enumerate(skills)]
        return c

    def finale(self, typ, title, theme):
        doc = deepcopy(self.map_doc)
        o = doc['Object']
        name = f'{ZONE}_{typ}'
        o['Layers'] = list(self.dtef.arene(typ,theme))
        o['BlankBG'] = self.dtef.case(theme,'wall',255,0,0)
        o['TextureMap'] = {}
        o['Tiles'] = [[{'Data': {'ID': 'floor' if libre(x,y,typ) else 'unbreakable',
                                'TileTex': cell(), 'StableTex': False},
                       'Effect': {'TileLoc': loc(x,y), 'ID': '', 'Revealed': False,
                                  'Owner': 0, 'TileStates': []}}
                      for y in range(HEIGHT)] for x in range(WIDTH)]
        o['DiscoveryArray'] = [[2]*HEIGHT for _ in range(WIDTH)]
        o['EntryPoints'] = [{'Loc': loc(*START), 'Dir': 4}]
        o.update(AssetName=name, Name=texte(f'Dédale {title}\nSalle du maître'),
                 Element=typ, HideMinimap=False, Comment='Finale de lignée. Victoire après toute la troupe.')
        casting, scene, pose, mode = TROUPES[typ]
        chef = casting[0][0]
        self.monstre(chef,typ)
        assert all(esp in set(self.lignee(chef)) for esp,*_ in casting[1:]), (typ,casting)
        origines = departs(typ)
        assert len(set(FORMATION))==len(set(origines))==3
        assert all(libre(x,y,typ) and y <= 4 for x,y in (*FORMATION,*origines)), typ
        team = o['MapTeams'][0]; modele = team['Players'][0]
        team['Name'] = 'Dojo Kingambit'
        team['Players'] = [self.combattant(modele, mon, moves, pos, niv, bonus)
                           for (mon,*moves),pos,niv,bonus in zip(casting,FORMATION,(12,8,7),(10,0,0))]
        origines_lua = '{'+','.join('{'+str(x)+','+str(y)+'}' for x,y in origines)+'}'
        on_start = o['MapEffect']['OnMapStarts']
        for i,(pr,phase) in enumerate(((-11,'Masquer'),(-9,'Jouer')),1):
            on_start.insert(i, {'Key': {'str':[pr]}, 'Value': {
                '$type':'RogueEssence.Dungeon.SingleCharScriptEvent, RogueEssence',
                'Script':'DestinyDojoTroupe'+phase,
                'ArgTable':f'{{ Type = "{typ}", Mode = "{mode}", Pose = {pose}, Origines = {origines_lua} }}'}})
        ecrire(self.out/f'game/Data/Map/{name}.rsmap', doc)
        return name

    def exploration(self, typ, theme, tier, variant):
        model = self.model['Floors'][0]
        keep = ('MapDataStep','InitGridPlanStep','GridPathBranch','DrawGridToFloorStep',
                'DrawFloorToTileStep','UnbreakableBorderStep','MobSpawnSettingsStep',
                'FloorStairsStep','MapDictTextureStep','PlaceRandomMobsStep','DetectIsolatedStairsStep')
        floor = {'$type': model['$type'], 'GenSteps': []}
        noms = []
        for a in model['GenSteps']:
            t = a['Value']['$type'].split('`')[0].rsplit('.',1)[-1]
            if t not in keep: continue
            noms.append(t)
            b = deepcopy(a); s = b['Value']
            if t == 'MapDataStep':
                s.update(Music='Marowak Dojo.ogg', TimeLimit=650 if not tier else 850, TileSight=0, CharSight=1)
            elif t == 'InitGridPlanStep':
                # 3 types de tracés, des cellules de 7×7 pour garantir les pièces.
                s.update(CellX=(3,4,3)[variant] + (variant==2 and tier==1),
                         CellY=(3,2,4)[variant] + (variant in (0,1) and tier==1),
                         CellWidth=7,CellHeight=7)
            elif t == 'GridPathBranch':
                s.update(RoomRatio={'Min': 82,'Max': 95},
                         BranchRatio={'Min': 12+variant*12,'Max': 28+variant*12})
            elif t == 'MobSpawnSettingsStep':
                s['Respawn'].update(MaxFoes=6, RespawnTime=42 if not tier else 34)
            elif t == 'FloorStairsStep':
                s['MinDistance'] = 2
            elif t == 'MapDictTextureStep':
                f,w = theme+'_floor',theme+'_wall'
                for key in (f,w): self.contenu('AutoTile',key)
                s.update(TextureMap={'floor': f, 'wall': w, 'unbreakable': w},
                         BlankBG=w,GroundElement=typ)
            elif t == 'PlaceRandomMobsStep':
                s['Spawn']['Amount'] = {'Min': 3+tier, 'Max': 5+tier}
                s['ClumpFactor'] = 0
            floor['GenSteps'].append(b)
        assert set(noms) == set(keep)
        return floor

    def monter(self):
        zone = self.zone_doc['Object']
        model_segment = deepcopy(zone['Segments'][0])
        zone.update(Name=texte('Dédales du Dojo Kingambit','Kingambit Dojo Mazes'), Released=True,
                    NoEXP=False, ExpPercent=175,
                    Comment='18 types : deux étages générés, puis le maître et sa troupe. EXP conservée, aucune mise.',
                    Segments=[])
        labels = ["-- Généré par tools/build_dedales_kingambit.py ; même ordre que les segments.", 'return {']
        for i,(typ,label,title,theme,accent,glyph,foes) in enumerate(TYPES):
            final = self.finale(typ,title,theme)
            seg = deepcopy(model_segment)
            f = seg['Floors'][0]; f['GenSteps'][0]['Value']['MapID'] = final
            seg['Floors'][:0] = [self.exploration(typ,theme,tier,i%3) for tier in range(2)]
            drop = deepcopy(next(s for s in self.model['ZoneSteps'] if 'FloorNameDrop' in s['$type']))
            drop['Name'] = texte(f'Dédale {title}\n{{0}}F')
            pop = {'$type': NS+'TeamSpawnZoneStep, RogueEssence', 'Priority': {'str': [1,2]},
                   'TeamSizes': [{'Spawn': 1, 'Rate': 10, 'Range': {'Min':0,'Max':2}}], 'Spawns': []}
            for j,(mon,move) in enumerate(foes):
                fdata = self.monstre(mon,typ); self.contenu('Skill',move)
                for tier in ((0,1) if j == 1 else (j//2,)):
                    a = {'BaseForm': {'Species':mon,'Form':0,'Skin':'normal','Gender':-1},
                         'Level': {'Min':7+2*tier, 'Max':9+2*tier},
                         'SpecifiedSkills':[move], 'Intrinsic':fdata['Intrinsic1'], 'Tactic':'wander_dumb',
                         'SpawnConditions':[], 'SpawnFeatures':[{'$type':'PMDC.LevelGen.MobSpawnUnrecruitable, PMDC'}]}
                    pop['Spawns'].append({'Spawn':{'Spawn':a,'Role':0}, 'Rate':10,
                                          'Range':{'Min':tier,'Max':tier+1}})
            seg['ZoneSteps'] = [drop,pop]
            seg.update(Comment=typ+' — '+title)
            zone['Segments'].append(seg)
            labels.append('  {' + ', '.join(json.dumps(x,ensure_ascii=False) for x in (typ,label,title,accent)) + '},')
        assert len(zone['Segments']) == 18
        ecrire(self.out/f'game/Data/Zone/{ZONE}.json', self.zone_doc)
        lua = self.out/'game/Data/Script/destiny/dojo_kingambit_types.lua'
        lua.parent.mkdir(parents=True,exist_ok=True)
        with lua.open('x', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(labels+['}', '']))
        print(f'{len(TYPES)} dédales, 54 étages dont 18 finales en tuiles DTEF du jeu de base.')


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--source',type=Path,default=ROOT)
    a.add_argument('--donnees',type=Path,required=True)
    a.add_argument('--out',type=Path,required=True)
    args = a.parse_args()
    Forgeron(args.source,args.donnees,args.out).monter()
