#!/usr/bin/env python3
"""Rebuild historical material and the active firefly DTEF outside the source tree."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from preview_maps import SheetReader


def main():
    with tempfile.TemporaryDirectory(prefix='destiny-lostwood-') as temp:
        temp = Path(temp)
        env = os.environ.copy()
        env['DESTINY_AUTOTILE_OUT'] = str(temp / 'tiles')
        env['DESTINY_DTEF_OUT'] = str(temp / 'dtef')
        for script in ('generer_autotiles_lost_wood.py', 'generer_dtef_lost_wood.py'):
            subprocess.run([sys.executable, str(ROOT / 'tools' / script)], cwd=ROOT, env=env, check=True)

        for name in ('LostWoodFloor.tile', 'LostWoodWall.tile'):
            expected = SheetReader(ROOT / 'game/Content/Tile' / name)
            actual = SheetReader(temp / 'tiles' / name)
            try:
                assert expected.tile_size == actual.tile_size
                assert expected.positions == actual.positions
                for xy in expected.positions:
                    assert expected.get_tile(*xy).tobytes() == actual.get_tile(*xy).tobytes(), (name, xy)
            finally:
                expected.close()
                actual.close()

        original = ROOT / 'art/dtef/LostWoodLucioles'
        rebuilt = temp / 'dtef'
        # Le README documente la provenance ; il n'est pas un export DTEF.
        expected_names = {p.name for p in original.iterdir() if p.is_file() and p.suffix in {'.png', '.xml'}}
        actual_names = {p.name for p in rebuilt.iterdir() if p.is_file()}
        assert expected_names == actual_names, (expected_names - actual_names, actual_names - expected_names)
        for name in expected_names:
            if name.endswith('.png'):
                with Image.open(original / name) as a, Image.open(rebuilt / name) as b:
                    assert a.size == b.size and a.convert('RGBA').tobytes() == b.convert('RGBA').tobytes(), name
            else:
                assert (original / name).read_text(encoding='utf-8') == (rebuilt / name).read_text(encoding='utf-8'), name
    print('Reconstruction Lost Wood : anciennes matières préservées et DTEF actif identique.')


if __name__ == '__main__':
    main()
