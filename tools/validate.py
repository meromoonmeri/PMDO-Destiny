#!/usr/bin/env python3
"""Validate the standalone, no-LFS Destiny source repository."""
from __future__ import annotations

import json
from pathlib import Path
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
        if path.is_file() and path.stat().st_size > GITHUB_LIMIT:
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
        if start.find('StartMap/Zone').text != 'destiny_hub' or start.find('StartMap/ID').text != '0':
            errors.append('StartMap does not target destiny_hub ground 0')
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
        for stem in grounds_on_disk:
            if stem not in declared:
                errors.append(f'Undeclared ground on disk: {stem}')
        zindex = json.loads((zone_dir / 'index.idx').read_text(encoding='utf-8-sig'))['Object']
        for zid, zone in zone_docs.items():
            if zid not in zindex:
                errors.append(f'Zone missing from index.idx: {zid}')
            elif zindex[zid]['Grounds'] != zone['Object']['GroundMaps']:
                errors.append(f'Zone index Grounds mismatch: {zid}')
        for stem, path in sorted(grounds_on_disk.items()):
            doc = json.loads(path.read_text(encoding='utf-8-sig'))
            if doc.get('Object', {}).get('AssetName') != stem:
                errors.append(f'Ground AssetName mismatch: {stem}')
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
