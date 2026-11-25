#!/usr/bin/env python3
"""Tests for tools/build_update_zip.py."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))

import build_update_zip  # noqa: E402


def _make_zip(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)


class TestBuildUpdateZip(unittest.TestCase):
    def test_delta_without_engine_ignores_exe_pdb_and_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            prev_zip = td / 'prev.zip'
            new_zip = td / 'new.zip'
            out_zip = td / 'update.zip'

            _make_zip(prev_zip, {
                'PMDO-Destiny/Destiny.exe': b'exe-v1',
                'PMDO-Destiny/PMDC.pdb': b'pdb-v1',
                'PMDO-Destiny/LOG/2026-11-01.txt': b'log-1',
                'PMDO-Destiny/Data/Script/a.lua': b'same',
                'PMDO-Destiny/Data/Script/b.lua': b'old-b',
                'PMDO-Destiny/Data/Ground/old.rsground': b'remove-me',
            })
            _make_zip(new_zip, {
                'PMDO-Destiny/Destiny.exe': b'exe-v2-timestamp',
                'PMDO-Destiny/PMDC.pdb': b'pdb-v2-timestamp',
                'PMDO-Destiny/LOG/2026-11-10.txt': b'log-2',
                'PMDO-Destiny/Data/Script/a.lua': b'same',
                'PMDO-Destiny/Data/Script/b.lua': b'new-b',
                'PMDO-Destiny/Data/Script/c.lua': b'added-c',
            })

            summary = build_update_zip.build_update_zip(
                new_zip=new_zip,
                prev_entries=build_update_zip.local_zip_index(prev_zip),
                output_zip=out_zip,
                prev_version='0.5.9',
                new_version='0.6.0',
                include_engine=False,
            )
            self.assertEqual(summary['added_count'], 1)
            self.assertEqual(summary['changed_count'], 1)
            self.assertEqual(summary['removed_count'], 1)

            with zipfile.ZipFile(out_zip) as zf:
                names = set(zf.namelist())
                self.assertIn('PMDO-Destiny/Data/Script/b.lua', names)
                self.assertIn('PMDO-Destiny/Data/Script/c.lua', names)
                self.assertIn('PMDO-Destiny/LISEZ_MOI_MISE_A_JOUR_0.6.0.txt', names)
                self.assertIn('PMDO-Destiny/NETTOYER_ANCIENS_FICHIERS_0.6.0.bat', names)
                self.assertNotIn('PMDO-Destiny/Data/Script/a.lua', names)
                self.assertNotIn('PMDO-Destiny/Destiny.exe', names)
                self.assertNotIn('PMDO-Destiny/PMDC.pdb', names)
                self.assertNotIn('PMDO-Destiny/LOG/2026-11-10.txt', names)
                bat = zf.read('PMDO-Destiny/NETTOYER_ANCIENS_FICHIERS_0.6.0.bat').decode('utf-8')
                self.assertIn(r'Data\Ground\old.rsground', bat)

    def test_delta_with_engine_includes_exe_and_pdb(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            prev_zip = td / 'prev.zip'
            new_zip = td / 'new.zip'
            out_zip = td / 'update.zip'

            _make_zip(prev_zip, {
                'PMDO-Destiny/Destiny.exe': b'exe-v1',
                'PMDO-Destiny/PMDC.pdb': b'pdb-v1',
                'PMDO-Destiny/Data/Script/a.lua': b'same',
            })
            _make_zip(new_zip, {
                'PMDO-Destiny/Destiny.exe': b'exe-v2',
                'PMDO-Destiny/PMDC.pdb': b'pdb-v2',
                'PMDO-Destiny/Data/Script/a.lua': b'same',
            })

            summary = build_update_zip.build_update_zip(
                new_zip=new_zip,
                prev_entries=build_update_zip.local_zip_index(prev_zip),
                output_zip=out_zip,
                prev_version='0.6.0',
                new_version='0.6.1',
                include_engine=True,
            )
            self.assertEqual(summary['changed_count'], 2)
            with zipfile.ZipFile(out_zip) as zf:
                names = set(zf.namelist())
                self.assertIn('PMDO-Destiny/Destiny.exe', names)
                self.assertIn('PMDO-Destiny/PMDC.pdb', names)
                self.assertNotIn('PMDO-Destiny/NETTOYER_ANCIENS_FICHIERS_0.6.1.bat', names)


if __name__ == '__main__':
    unittest.main()
