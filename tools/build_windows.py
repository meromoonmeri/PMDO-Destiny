#!/usr/bin/env python3
"""Compile PMDO, merge the Destiny quest, and package a standalone Windows build."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MERGED_DIRS = ('Base', 'Content', 'Controls', 'Data', 'Editor', 'Licenses', 'Strings')


def run(command: list[str], cwd: Path) -> None:
    print('+', ' '.join(str(part) for part in command), flush=True)
    subprocess.run([str(part) for part in command], cwd=cwd, check=True)


def unpack_payload() -> None:
    # Reconstitue la ville depuis payload/ et l'index des planches depuis les .tile.
    run([sys.executable, str(ROOT / 'tools' / 'unpack_payload.py')], ROOT)


def install_quest(directory: Path) -> None:
    unpack_payload()
    quest = directory / 'MODS' / 'Destiny'
    if quest.exists():
        shutil.rmtree(quest)
    quest.parent.mkdir(exist_ok=True)
    shutil.copytree(ROOT / 'game', quest)


def publish(runtime: str, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    run([
        'dotnet', 'publish', ROOT / 'engine' / 'PMDC' / 'PMDC.csproj',
        '-c', 'Release', '-r', runtime, '--self-contained', 'true', '-o', destination,
    ], ROOT)


def merge_quest(publish_dir: Path, helper_dir: Path | None, skip_helper_publish: bool) -> Path:
    if os.name == 'nt':
        helper = publish_dir
        executable = helper / 'PMDC.exe'
    else:
        helper = helper_dir or (ROOT / 'build' / 'linux-merge')
        executable = helper / 'PMDC'
        if not executable.exists():
            if skip_helper_publish:
                raise SystemExit(f'Linux merge helper not found: {executable}')
            publish('linux-x64', helper)
    install_quest(helper)
    if not executable.exists():
        raise SystemExit(f'Merge executable not found: {executable}')
    run([executable, '-quest', 'Destiny', '-build'], helper)
    merged = helper / 'BUILD' / 'Destiny'
    if not (merged / 'Data' / 'StartParams.xml').is_file():
        raise SystemExit('PMDO did not produce the standalone Destiny build.')

    # PMDC 0.8.12's MergeQuest omits Data/Misc. Without these universal
    # indices, the standalone exits its data bootstrap with a NullReferenceException.
    # Restore the base files, then apply any quest-specific overrides.
    for source in (helper / 'Data' / 'Misc', helper / 'MODS' / 'Destiny' / 'Data' / 'Misc'):
        if source.is_dir():
            shutil.copytree(source, merged / 'Data' / 'Misc', dirs_exist_ok=True)
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-publish', action='store_true', help='Reuse the existing Windows and helper publish directories.')
    parser.add_argument('--publish-dir', type=Path, default=ROOT / 'build' / 'windows')
    parser.add_argument('--merge-dir', type=Path, help='Existing non-Windows PMDO publish directory used for the headless quest merge.')
    parser.add_argument('--no-zip', action='store_true', help='Do not create the distributable ZIP.')
    args = parser.parse_args()

    publish_dir = args.publish_dir.resolve()
    if not args.skip_publish:
        publish('win-x64', publish_dir)
    if not (publish_dir / 'PMDC.exe').is_file():
        raise SystemExit(f'PMDC.exe not found in {publish_dir}. Run without --skip-publish first.')

    merged = merge_quest(publish_dir, args.merge_dir.resolve() if args.merge_dir else None, args.skip_publish)

    # Replace the generic runtime data by PMDO's merged standalone output.
    for name in MERGED_DIRS:
        destination = publish_dir / name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(merged / name, destination)
    # The final game no longer needs a quest selector. The UI color themes
    # are native content under Content/UI/Themes/, selected from the game's
    # own settings menu; no separate UI mods are shipped.
    if (publish_dir / 'MODS').exists():
        shutil.rmtree(publish_dir / 'MODS')
    if (publish_dir / 'BUILD').exists():
        shutil.rmtree(publish_dir / 'BUILD')

    # Conserver la carte native du dépôt et alléger uniquement sa copie de jeu.
    # Les cellules vides utilisent les valeurs par défaut du moteur PMDO 0.8.12.
    from compacter_ville import compact
    compact(ROOT / 'game/Data/Ground/WaterfallVillageCapital.rsground',
            publish_dir / 'Data/Ground/WaterfallVillageCapital.rsground')

    exe = publish_dir / 'PMDC.exe'
    destiny_exe = publish_dir / 'Destiny.exe'
    if destiny_exe.exists():
        destiny_exe.unlink()
    exe.rename(destiny_exe)
    shutil.copy2(ROOT / 'art' / 'destiny_icon.png', publish_dir / 'Destiny.png')
    shutil.copy2(ROOT / 'art' / 'destiny_icon.png', publish_dir / 'PMDO.png')

    def create_launcher(name: str, options: str = '') -> None:
        # write_bytes évite que Windows ne transforme CRLF en CR-CR-LF.
        script = f'@echo off\r\ncd /d "%~dp0"\r\nstart "" "Destiny.exe"{options}\r\n'
        (publish_dir / name).write_bytes(script.encode('ascii'))

    create_launcher('JOUER_A_DESTINY.bat')
    create_launcher('JOUER_A_DESTINY_WASAPI.bat', ' -audiodriver:wasapi')
    # Le dev.bat de la base vise PMDO.exe, mais l'exécutable s'appelle Destiny.exe ici.
    create_launcher('dev.bat', ' -dev')
    shutil.copy2(ROOT / 'docs' / 'LISEZ_MOI_WINDOWS.txt', publish_dir / 'LISEZ_MOI.txt')

    # Vérifier la présence dans le build de toutes les cartes de la Quest et en
    # donner la liste : le build contient aussi des cartes de base du moteur.
    source_grounds = sorted(path.stem for path in (ROOT / 'game/Data/Ground').glob('*.rsground'))
    if not source_grounds:
        raise SystemExit('No Destiny ground maps found in game/Data/Ground.')
    missing_grounds = [name for name in source_grounds
                       if not (publish_dir / 'Data' / 'Ground' / f'{name}.rsground').is_file()]
    if missing_grounds:
        raise SystemExit('Destiny ground maps missing from package: ' + ', '.join(missing_grounds))
    listing = f'CARTES DESTINY : {len(source_grounds)}\n\n' + '\n'.join(source_grounds) + '\n'
    (publish_dir / 'LISTE_CARTES_DESTINY.txt').write_bytes(listing.replace('\n', '\r\n').encode('utf-8'))
    print(f'Destiny ground maps in package: {len(source_grounds)}')

    # Structural checks on the actual package.
    required = [
        'Destiny.exe', 'Base/PathParams.xml', 'Content/UI/Title.png',
        'Content/UI/Themes/Blue/MenuBorder.png',
        'Content/UI/Themes/Violet/MenuBorder.png',
        'Content/UI/Themes/PastelPink/MenuBorder.png',
        'Content/UI/Themes/PastelYellow/MenuBorder.png',
        'Data/Ground/destiny_hub.rsground', 'Data/Zone/destiny_hub.json',
        'Data/Script/destiny/ground/destiny_hub/init.lua', 'Data/StartParams.xml',
        'Data/Misc/Index.json', 'Data/Misc/MonsterFeature.json', 'Data/Misc/Rarity.json',
    ]
    for rel in required:
        if not (publish_dir / rel).is_file():
            raise SystemExit(f'Packaged file missing: {rel}')
    file_count = sum(1 for path in publish_dir.rglob('*') if path.is_file())
    print(f'Standalone Windows build ready: {publish_dir} ({file_count} files)')
    print('Launch: JOUER_A_DESTINY.bat (no quest argument required)')

    if not args.no_zip:
        dist = ROOT / 'dist'
        dist.mkdir(exist_ok=True)
        archive = dist / 'PMDO-Destiny-Windows-x64.zip'
        if archive.exists():
            archive.unlink()
        print(f'Creating {archive}...', flush=True)
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as zf:
            for path in sorted(publish_dir.rglob('*')):
                if path.is_file():
                    arcname = Path('PMDO-Destiny') / path.relative_to(publish_dir)
                    zf.write(path, arcname.as_posix())
        with zipfile.ZipFile(archive) as zf:
            bad = zf.testzip()
            if bad:
                raise SystemExit(f'ZIP integrity failure: {bad}')
        print(f'ZIP verified: {archive} ({archive.stat().st_size / 1048576:.1f} MiB)')


if __name__ == '__main__':
    main()
