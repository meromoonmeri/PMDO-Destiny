#!/usr/bin/env python3
"""Vérifie le placement HD de la Grande Guilde (4 ambiances), PorteGuilde, obstacles et enrôlement."""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
AMBIANCES = [
    ('jour', 'Jour'),
    ('aube', 'Aube'),
    ('crepuscule', 'Crepuscule'),
    ('nuit', 'Nuit'),
]


def main() -> None:
    for amb, cap in AMBIANCES:
        stem = f'guilde_cliff_{amb}'
        doc = json.loads((ROOT / 'game/Data/Ground' / f'{stem}.rsground').read_text(encoding='utf-8-sig'))['Object']
        decos = doc['Decorations']
        names = [d['Name'] for d in decos]
        assert names == ['Ombres_Nuages_Cliff', 'BatimentGuildeOmbre', 'BatimentGuilde', 'BatimentGuildeOuverte'], (stem, names)
        for d in decos:
            assert d['Layer'] == 0, (stem, d['Name'], d['Layer'])
        expected_anims = {
            'BatimentGuildeOmbre': (f'Guilde_HD_Ombre_{cap}', True),
            'BatimentGuilde': (f'Guilde_HD_{cap}', True),
            'BatimentGuildeOuverte': (f'Guilde_HD_Porte_Ouverte_{cap}', False),
        }
        for d in decos[1:]:
            anim_idx, vis = expected_anims[d['Name']]
            assert d['Visible'] is vis, (stem, d['Name'], d['Visible'])
            a = d['Anims'][0]
            assert a['MapLoc'] == {'X': 109, 'Y': 24}, (stem, d['Name'], a['MapLoc'])
            assert a['ObjectAnim']['AnimIndex'] == anim_idx, (stem, d['Name'], a['ObjectAnim']['AnimIndex'])
            assert a['ObjectAnim']['AnimDir'] == 0
            assert (ROOT / 'game/Content/Object' / f'{anim_idx}.dir').is_file()

        gos = {g['EntName']: g for g in doc['Entities'][0]['GroundObjects']}
        assert 'PorteGuilde' in gos, (stem, gos)
        pg = gos['PorteGuilde']
        assert pg['triggerType'] == 2 and pg['Passable'] is False
        assert pg['Collider'] == {'X': 224, 'Y': 256, 'Width': 32, 'Height': 16}

        obs = doc['obstacles']
        for ty in range(20, 31):
            for tx in range(16, 44):
                assert obs[tx][ty]['Tags'] != 0, (stem, tx, ty)
        for tx in range(27, 33):
            for ty in (31, 32, 33, 34):
                assert obs[tx][ty]['Tags'] == 0, (stem, tx, ty)

        def free16(px: int, py: int) -> bool:
            if px < 0 or py < 0 or px + 16 > 480 or py + 16 > 520:
                return False
            return all(
                obs[cx][cy]['Tags'] == 0
                for cx in range(px // 8, (px + 15) // 8 + 1)
                for cy in range(py // 8, (py + 15) // 8 + 1)
            )
        q = deque([(232, 464)])
        seen = {(232, 464)}
        while q and (232, 264) not in seen:
            px, py = q.popleft()
            for nx, ny in ((px + 4, py), (px - 4, py), (px, py + 4), (px, py - 4)):
                if (nx, ny) not in seen and free16(nx, ny):
                    seen.add((nx, ny))
                    q.append((nx, ny))
        assert (232, 264) in seen, f'{stem}: PorteGuilde inaccessible'

        # Vérifier que falaise_promontoire_* reste intacte (Decorations == [])
        prom = json.loads((ROOT / 'game/Data/Ground' / f'falaise_promontoire_{amb}.rsground').read_text(encoding='utf-8-sig'))['Object']
        assert prom['Decorations'] == []

    run(ROOT / 'tools/tests/test_guilde_enrolement.lua', ROOT)
    print('PASS Guilde HD (4 ambiances) : calques Layer 0, porte animée, accès escalier et enrôlement.')


if __name__ == '__main__':
    main()
