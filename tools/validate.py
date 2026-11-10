#!/usr/bin/env python3
"""Validate the standalone, no-LFS Destiny source repository."""
from __future__ import annotations

import json
from pathlib import Path
import re
import struct
import sys
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GITHUB_LIMIT = 100 * 1024 * 1024


def main() -> None:
    errors: list[str] = []
    def generated(rel: Path) -> bool:
        if '.git' in rel.parts or rel.parts[0] in {'build', 'dist'}:
            return True
        return rel.parts[0] == 'engine' and any(part in {'bin', 'obj', 'obj_core', 'publish'} for part in rel.parts)

    files = [p for p in ROOT.rglob('*') if p.is_file() and not generated(p.relative_to(ROOT))]
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if generated(rel):
            continue
        if path.is_symlink():
            errors.append(f'Symlink forbidden: {rel}')
        if path.name == '.gitmodules':
            errors.append(f'Submodule metadata remains: {rel}')
        generated_large = {
            'game/Data/Ground/WaterfallVillageCapital.rsground',
            'game/Content/Tile/index.idx',
        }
        if path.is_file() and path.stat().st_size > GITHUB_LIMIT and str(rel) not in generated_large:
            # (Ces deux fichiers sont ignorés par git et reconstitués localement :
            # la ville depuis payload/, l'index depuis les en-têtes des .tile.)
            errors.append(f'File exceeds GitHub limit: {rel} ({path.stat().st_size} bytes)')

    for path in files:
        if path.suffix == '.gitattributes' and 'filter=lfs' in path.read_text(encoding='utf-8', errors='replace'):
            errors.append(f'Git LFS rule found: {path.relative_to(ROOT)}')
        if path.stat().st_size < 1024:
            prefix = path.read_bytes()[:100]
            if prefix.startswith(b'version https://git-lfs.github.com/spec/'):
                errors.append(f'Git LFS pointer found: {path.relative_to(ROOT)}')

    required = [
        'engine/PMDC/PMDC.csproj', 'engine/RogueEssence/RogueEssence/RogueEssence.csproj',
        'base/Data/StartParams.xml', 'base/Content/ContentParams.xml',
        'game/Mod.xml', 'game/Data/StartParams.xml',
        'game/Data/Ground/destiny_hub.rsground', 'game/Data/Zone/destiny_hub.json',
        'game/Data/Zone/index.idx', 'game/Data/Script/destiny/ground/destiny_hub/init.lua',
        'game/Content/UI/Title.png', 'art/destiny_title_background.png',
        'docs/SOURCE_LOCK.json',
    ]
    for rel in required:
        if not (ROOT / rel).is_file():
            errors.append(f'Missing required file: {rel}')

    for rel in ['game/Data/Ground/destiny_hub.rsground', 'game/Data/Zone/destiny_hub.json', 'game/Data/Zone/index.idx', 'docs/SOURCE_LOCK.json']:
        try:
            json.loads((ROOT / rel).read_text(encoding='utf-8-sig'))
        except Exception as exc:
            errors.append(f'Invalid JSON {rel}: {exc}')
    for rel in ['game/Mod.xml', 'game/Data/StartParams.xml', 'game/Strings/strings.resx', 'game/Strings/strings.fr.resx']:
        try:
            ET.parse(ROOT / rel)
        except Exception as exc:
            errors.append(f'Invalid XML {rel}: {exc}')

    try:
        ground = json.loads((ROOT / 'game/Data/Ground/destiny_hub.rsground').read_text(encoding='utf-8-sig'))
        if ground['Object']['AssetName'] != 'destiny_hub':
            errors.append('Ground AssetName mismatch')
        if ground['Version'] != '0.8.12.0':
            errors.append(f"Unexpected Ground version: {ground['Version']}")
        zone = json.loads((ROOT / 'game/Data/Zone/destiny_hub.json').read_text(encoding='utf-8-sig'))
        if zone['Object']['GroundMaps'] != ['destiny_hub']:
            errors.append('destiny_hub is not the first GroundMap')
        index = json.loads((ROOT / 'game/Data/Zone/index.idx').read_text(encoding='utf-8-sig'))
        if 'destiny_hub' not in index['Object']:
            errors.append('destiny_hub missing from zone index')
        start = ET.parse(ROOT / 'game/Data/StartParams.xml').getroot()
        # Depuis l'unification (scénario arena/64113588), la partie démarre sur intro_halo :
        # zone personality_test, carte d'index 1. L'ancien départ destiny_hub reste accepté.
        sz, sid = start.find('StartMap/Zone').text, start.find('StartMap/ID').text
        if (sz, sid) not in (('destiny_hub', '0'), ('personality_test', '1')):
            errors.append('StartMap does not target destiny_hub ground 0 nor personality_test ground 1')
        else:
            szone = json.loads((ROOT / f'game/Data/Zone/{sz}.json').read_text(encoding='utf-8-sig'))
            if len(szone['Object']['GroundMaps']) <= int(sid):
                errors.append('StartMap ID out of range')
        with Image.open(ROOT / 'game/Content/UI/Title.png') as image:
            if image.size != (320, 240):
                errors.append(f'PMDO title must be 320x240, got {image.size}')
    except Exception as exc:
        errors.append(f'Structural validation failed: {exc}')

    # ----- Contenu importé (atelier guilde-treehouse-pmd) -----
    # Toute carte au sol sur disque doit être déclarée dans exactement une zone,
    # l'index des zones doit refléter les fichiers de zones, et l'index binaire
    # des tuiles doit correspondre octet pour octet aux en-têtes des .tile
    # (même construction que ImportHelper.BuildTileIndex du moteur).
    def _read_dotnet_string(buf, off):
        length, shift = 0, 0
        while True:
            b = buf[off]
            off += 1
            length |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
        return buf[off:off + length].decode('utf-8'), off + length

    def _tile_guide(path):
        buf = path.read_bytes()
        off = 0
        (count,) = struct.unpack_from('<i', buf, off)
        off += 4
        nodes = {}
        for _ in range(count):
            name, off = _read_dotnet_string(buf, off)
            start = off
            _, n = struct.unpack_from('<ii', buf, off)
            off += 8 + n * 16
            nodes[name] = buf[start:off]
        if off != len(buf):
            raise ValueError(f'tile guide size mismatch in {path}')
        return nodes

    # Fichiers volumineux non versionnés : la ville est livrée compressée dans
    # payload/ et l'index des planches est régénéré depuis les .tile.
    try:
        import subprocess as _sp
        generated_missing = [
            ROOT / 'game/Data/Ground/WaterfallVillageCapital.rsground',
            ROOT / 'game/Data/Ground/WaterfallVillageCapital_Dev.rsground',
            ROOT / 'game/Data/Ground/reverie_centre.rsground',
            ROOT / 'game/Data/Ground/reverie_nord.rsground',
            ROOT / 'game/Data/Ground/reverie_residentiel.rsground',
            ROOT / 'game/Data/Ground/reverie_etang.rsground',
            ROOT / 'game/Data/Ground/reverie_centre_Dev.rsground',
            ROOT / 'game/Data/Ground/reverie_nord_Dev.rsground',
            ROOT / 'game/Data/Ground/reverie_residentiel_Dev.rsground',
            ROOT / 'game/Data/Ground/reverie_etang_Dev.rsground',
            ROOT / 'game/Content/Tile/index.idx',
        ]
        if any(not path.is_file() for path in generated_missing) and (ROOT / 'tools/unpack_payload.py').is_file():
            _sp.run([sys.executable, str(ROOT / 'tools/unpack_payload.py')], check=False)
    except Exception as exc:
        errors.append(f'unpack_payload failed: {exc}')

    try:
        ground_dir = ROOT / 'game/Data/Ground'
        zone_dir = ROOT / 'game/Data/Zone'
        grounds_on_disk = {p.stem: p for p in ground_dir.glob('*.rsground')}
        declared = {}
        zone_docs = {}
        for zone_path in sorted(zone_dir.glob('*.json')):
            zone = json.loads(zone_path.read_text(encoding='utf-8-sig'))
            zone_docs[zone_path.stem] = zone
            for g in zone['Object']['GroundMaps']:
                if g in declared:
                    errors.append(f'Ground declared twice: {g}')
                declared[g] = zone_path.stem
                if g not in grounds_on_disk:
                    errors.append(f'Zone {zone_path.stem} declares missing ground: {g}')
        # Une seule copie d’édition, volontairement absente des zones jouables.
        editor_only_grounds = {'WaterfallVillageCapital_Dev', 'reverie_centre_Dev', 'reverie_nord_Dev', 'reverie_residentiel_Dev', 'reverie_etang_Dev'}
        for stem in grounds_on_disk:
            if stem not in declared and stem not in editor_only_grounds:
                errors.append(f'Undeclared ground on disk: {stem}')
        for stem in editor_only_grounds & declared.keys():
            errors.append(f'Editor-only ground declared in playable zone: {stem}')
        zindex = json.loads((zone_dir / 'index.idx').read_text(encoding='utf-8-sig'))['Object']
        for zid, zone in zone_docs.items():
            if zid not in zindex:
                errors.append(f'Zone missing from index.idx: {zid}')
            elif zindex[zid]['Grounds'] != zone['Object']['GroundMaps']:
                errors.append(f'Zone index Grounds mismatch: {zid}')
        for stem, path in sorted(grounds_on_disk.items()):
            doc = json.loads(path.read_text(encoding='utf-8-sig'))
            obj = doc.get('Object', {})
            if obj.get('AssetName') != stem:
                errors.append(f'Ground AssetName mismatch: {stem}')
            for req_key in ('BlankBG', 'rand', 'Background', 'Layers', 'Decorations', 'Entities', 'obstacles', 'Status'):
                if obj.get(req_key) is None:
                    errors.append(f'Ground {stem} missing or null required field: {req_key}')
            bad_fl = 0
            for layer in obj.get('Layers', []):
                for col in layer.get('Tiles', []):
                    for cell in col:
                        for tl in cell.get('Layers', []):
                            if tl.get('Frames') and (not isinstance(tl.get('FrameLength'), int) or tl['FrameLength'] <= 0):
                                bad_fl += 1
            for tl in obj.get('BlankBG', {}).get('Layers', []):
                if tl.get('Frames') and (not isinstance(tl.get('FrameLength'), int) or tl['FrameLength'] <= 0):
                    bad_fl += 1
            if bad_fl:
                errors.append(f'Ground {stem} has {bad_fl} TileLayer(s) with non-positive FrameLength')
            script = ROOT / 'game/Data/Script/destiny/ground' / stem / 'init.lua'
            if not script.is_file():
                errors.append(f'Missing ground script: game/Data/Script/destiny/ground/{stem}/init.lua')
        tile_files = {p.stem: p for p in (ROOT / 'game/Content/Tile').glob('*.tile')}
        tile_index_path = ROOT / 'game/Content/Tile/index.idx'
        if tile_files:
            if not tile_index_path.is_file():
                errors.append('game/Content/Tile/index.idx missing')
            else:
                guide = _tile_guide(tile_index_path)
                if set(guide) != set(tile_files):
                    errors.append('Tile index does not match game/Content/Tile/*.tile files')
                else:
                    for stem, path in tile_files.items():
                        with open(path, 'rb') as handle:
                            raw = handle.read(8)
                            _, n = struct.unpack('<ii', raw)
                            raw += handle.read(n * 16)
                        if raw != guide[stem]:
                            errors.append(f'Tile index node mismatch: {stem}')
        map_dir = ROOT / 'game/Data/Map'
        if map_dir.is_dir():
            for path in sorted(map_dir.glob('*.rsmap')):
                json.loads(path.read_text(encoding='utf-8-sig'))
    except Exception as exc:
        errors.append(f'Imported content validation failed: {exc}')

    # ----- Menu-titre anime (service destiny_title_anim) -----
    # Les trois DirSheet du titre doivent etre presents et structurellement valides
    # (format DirSheet.Save : [int64 png_len][PNG][int32 tileW, tileH, rotate, frames]),
    # le service doit etre enregistre par destiny/main.lua, et les valeurs de
    # game/Content/ContentParams.xml doivent pointer sur des fichiers existants.
    def _check_dirsheet(path, expected_tile=(320, 240)):
        raw = path.read_bytes()
        (png_len,) = struct.unpack_from('<q', raw, 0)
        if 8 + png_len + 16 != len(raw):
            raise ValueError(f'DirSheet size mismatch: {path}')
        tile_w, tile_h, _rot, frames = struct.unpack_from('<iiii', raw, 8 + png_len)
        if (tile_w, tile_h) != expected_tile or frames < 1:
            raise ValueError(f'DirSheet trailer unexpected in {path}: {(tile_w, tile_h, frames)}')

    try:
        for rel in ['game/Content/BG/Title_Screen_Background_Jour.dir',
                    'game/Content/BG/Title_Screen_Background_Nuit.dir',
                    'game/Content/Object/Destiny_Logo_Anime_Opening.dir']:
            path = ROOT / rel
            if not path.is_file():
                errors.append(f'Title DirSheet missing: {rel}')
            else:
                _check_dirsheet(path)
        main_lua = ROOT / 'game/Data/Script/destiny/main.lua'
        if not main_lua.is_file() or 'destiny.services.destiny_title_anim' not in main_lua.read_text(encoding='utf-8-sig'):
            errors.append('destiny/main.lua must require destiny.services.destiny_title_anim')
        if not (ROOT / 'game/Data/Script/destiny/services/destiny_title_anim/init.lua').is_file():
            errors.append('Title service missing: game/Data/Script/destiny/services/destiny_title_anim/init.lua')
        params_path = ROOT / 'game/Content/ContentParams.xml'
        if params_path.is_file():
            params = ET.parse(params_path).getroot()
            title_bg = params.findtext('TitleBG')
            bg_found = any((ROOT / base_rel / f'{title_bg}.dir').is_file()
                           for base_rel in ['game/Content/BG', 'base/Content/BG'])
            if not bg_found:
                errors.append(f'ContentParams TitleBG not found as .dir: {title_bg}')
            for tag in ['TitleBGM', 'MonsterBGM']:
                music = params.findtext(tag)
                if not any((ROOT / base_rel / music).is_file()
                           for base_rel in ['game/Content/Music', 'base/Content/Music']):
                    errors.append(f'ContentParams {tag} not found: {music}')
    except Exception as exc:
        errors.append(f'Title menu validation failed: {exc}')

    # ----- Quiz de personnalite (20 questions + etoile au clic droit) -----
    try:
        quiz_config = json.loads((ROOT / 'game/Data/quiz_personnalite_config.json').read_text(encoding='utf-8-sig'))['Object']
        quiz_questions = quiz_config.get('Questions', [])
        if len(quiz_questions) != 20:
            errors.append(f'Personality quiz must contain exactly 20 questions: {len(quiz_questions)}')
        counts = [len(q.get('Choix', [])) for q in quiz_questions]
        if counts and (min(counts) < 2 or max(counts) > 5):
            errors.append(f'Personality quiz choices must stay between 2 and 5: {counts}')
        visible_quiz = '\n'.join(
            [q.get('Texte', '') for q in quiz_questions]
            + [c.get('Texte', '') for q in quiz_questions for c in q.get('Choix', [])]
        )
        if re.search(r'(?<!\d)(?:\(?\s*\d+\s*/\s*(?:15|20)\s*\)?)(?!\d)', visible_quiz):
            errors.append('Personality quiz must not display a question counter')

        quiz_starters = {s['Id']: s for s in quiz_config.get('Starters', [])}
        for item in quiz_config.get('Mapping', []):
            starter = quiz_starters.get(item.get('Starter'))
            if starter is None:
                errors.append(f"Personality quiz mapped starter missing: {item}")
                continue
            fluid_assets = [
                (f"game/Content/Particle/Quiz_Etoile_Particule_{starter.get('EtoileType')}.dir", (24, 24)),
                (f"game/Content/Object/Quiz_Etoile_Halo_{starter.get('EtoileType')}.dir", (192, 192)),
                (f"game/Content/Object/Quiz_Etoile_Ondes_{starter.get('EtoileType')}.dir", (224, 224)),
                (f"game/Content/Object/Quiz_Etoile_Forme_{starter.get('EtoileType')}.dir", (192, 216)),
            ]
            for rel, tile in fluid_assets:
                path = ROOT / rel
                if not path.is_file():
                    errors.append(f'Quiz fluid DirSheet missing: {rel}')
                else:
                    _check_dirsheet(path, tile)

        quiz_init_path = ROOT / 'game/Data/Script/destiny/ground/personality_test/init.lua'
        quiz_init = quiz_init_path.read_text(encoding='utf-8-sig') if quiz_init_path.is_file() else ''
        for needle in ['INPUT_RIGHT_MOUSE = 30', 'GAME:IsInputDown',
                       'MetaInputManager.MouseLoc', 'GraphicsManager.WindowZoom',
                       'RogueEssence.Menu.ScriptableMenu', 'FLUIDE_CONVERGENCE = 0.70',
                       'Quelqu’un comme toi serait ', "UI:SetSpeaker('', false, starter.espece"]:
            if needle not in quiz_init:
                errors.append(f'Personality quiz reveal is incomplete: missing {needle!r}')
        if 'UI:BeginChoiceMenu(q.texte' not in quiz_init:
            errors.append('Personality quiz questions must be shown without a progress prefix')
        for forbidden in ['UI:WaitShowBG', 'UI:WaitHideBG', 'UI:TextPopUp']:
            if forbidden in quiz_init:
                errors.append(f'Personality quiz reveal must keep its base background and dialogue-only prompt: {forbidden}')
        if list((ROOT / 'game/Content/BG').glob('Quiz_Etoile*.dir')):
            errors.append('Legacy full-screen quiz star backgrounds must not be shipped')
    except Exception as exc:
        errors.append(f'Personality quiz validation failed: {exc}')

    total = sum(path.stat().st_size for path in files)
    largest = max(files, key=lambda path: path.stat().st_size)
    print(f'Files checked: {len(files)}')
    print(f'Source size: {total / 1048576:.1f} MiB')
    print(f'Largest file: {largest.relative_to(ROOT)} ({largest.stat().st_size / 1048576:.2f} MiB)')
    print('Git LFS: none')
    print('Submodules: none')
    if errors:
        print('\nVALIDATION FAILED:', file=sys.stderr)
        for error in errors:
            print('-', error, file=sys.stderr)
        raise SystemExit(1)
    print('VALIDATION OK')


if __name__ == '__main__':
    main()
