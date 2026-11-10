#!/usr/bin/env python3
"""Build an incremental Windows update ZIP from a previous release ZIP and a new full ZIP."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import struct
import sys
import urllib.request
import zipfile
import zlib


@dataclass(frozen=True)
class ZipEntryMeta:
    crc: int
    usize: int
    csize: int
    method: int
    lhoff: int


def is_ignored_runtime_entry(name: str, include_engine: bool) -> bool:
    """Ignore per-run logs, and ignore Destiny.exe/.pdb when engine C# sources did not change."""
    if name.endswith('/'):
        return True
    if name.startswith('PMDO-Destiny/LOG/') or name == 'LOG' or name.startswith('LOG/'):
        return True
    if not include_engine:
        rel = name[len('PMDO-Destiny/'):] if name.startswith('PMDO-Destiny/') else name
        if rel == 'Destiny.exe':
            return True
        if '/' not in rel and rel.endswith('.pdb'):
            return True
    return False


def local_zip_index(path: Path) -> dict[str, ZipEntryMeta]:
    entries: dict[str, ZipEntryMeta] = {}
    with zipfile.ZipFile(path, 'r') as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            entries[info.filename] = ZipEntryMeta(
                crc=info.CRC & 0xFFFFFFFF,
                usize=info.file_size,
                csize=info.compress_size,
                method=info.compress_type,
                lhoff=info.header_offset,
            )
    return entries


def _fetch_range(url: str, start: int, end: int) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={'Range': f'bytes={start}-{end}'})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read(), resp.headers.get('Content-Range', '')


def remote_zip_index(url: str) -> dict[str, ZipEntryMeta]:
    """Read only the ZIP Central Directory from an HTTP Range-capable URL."""
    _, content_range = _fetch_range(url, 0, 0)
    if '/' not in content_range:
        raise RuntimeError(f'Remote server did not return Content-Range for {url}')
    total_size = int(content_range.split('/')[-1])

    tail_start = max(0, total_size - 65536)
    tail, _ = _fetch_range(url, tail_start, total_size - 1)
    eocd_pos = tail.rfind(b'PK\x05\x06')
    if eocd_pos == -1:
        raise RuntimeError('ZIP End of Central Directory not found')
    _, _, _, _, cd_size, cd_offset, _ = struct.unpack('<HHHHIIH', tail[eocd_pos + 4:eocd_pos + 22])

    z64_loc = tail.rfind(b'PK\x06\x07')
    if z64_loc != -1 and (cd_offset == 0xFFFFFFFF or cd_size == 0xFFFFFFFF):
        _, z64_eocd_off, _ = struct.unpack('<IQI', tail[z64_loc + 4:z64_loc + 20])
        z64, _ = _fetch_range(url, z64_eocd_off, z64_eocd_off + 55)
        if z64[:4] != b'PK\x06\x06':
            raise RuntimeError('Invalid Zip64 EOCD record')
        cd_size, cd_offset = struct.unpack('<QQ', z64[40:56])

    cd, _ = _fetch_range(url, cd_offset, cd_offset + cd_size - 1)
    pos = 0
    entries: dict[str, ZipEntryMeta] = {}
    while pos < len(cd):
        if cd[pos:pos + 4] != b'PK\x01\x02':
            raise RuntimeError(f'Invalid Central Directory signature at offset {pos}')
        method, _, _, crc, csize, usize, fn_len, ex_len, cm_len = struct.unpack(
            '<HHHIIIHHH', cd[pos + 10:pos + 34]
        )
        lhoff, = struct.unpack('<I', cd[pos + 42:pos + 46])
        name = cd[pos + 46:pos + 46 + fn_len].decode('utf-8', errors='replace')
        ex = cd[pos + 46 + fn_len:pos + 46 + fn_len + ex_len]
        if 0xFFFFFFFF in (usize, csize, lhoff):
            ep = 0
            while ep + 4 <= len(ex):
                tag, sz = struct.unpack('<HH', ex[ep:ep + 4])
                if tag == 0x0001:
                    off = ep + 4
                    if usize == 0xFFFFFFFF:
                        usize, = struct.unpack('<Q', ex[off:off + 8])
                        off += 8
                    if csize == 0xFFFFFFFF:
                        csize, = struct.unpack('<Q', ex[off:off + 8])
                        off += 8
                    if lhoff == 0xFFFFFFFF:
                        lhoff, = struct.unpack('<Q', ex[off:off + 8])
                        off += 8
                    break
                ep += 4 + sz
        if not name.endswith('/'):
            entries[name] = ZipEntryMeta(
                crc=crc,
                usize=usize,
                csize=csize,
                method=method,
                lhoff=lhoff,
            )
        pos += 46 + fn_len + ex_len + cm_len
    return entries


def _safe_rel_windows_path(arcname: str) -> str | None:
    p = PurePosixPath(arcname)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        return None
    if p.parts[0] == 'PMDO-Destiny':
        p = PurePosixPath(*p.parts[1:])
    if not p.parts:
        return None
    return '\\'.join(p.parts)


def build_update_zip(
    new_zip: Path,
    prev_entries: dict[str, ZipEntryMeta],
    output_zip: Path,
    prev_version: str,
    new_version: str,
    include_engine: bool = False,
) -> dict[str, object]:
    new_entries = local_zip_index(new_zip)
    added: list[str] = []
    changed: list[str] = []
    removed: list[str] = []

    for name in sorted(new_entries):
        if is_ignored_runtime_entry(name, include_engine=include_engine):
            continue
        prev = prev_entries.get(name)
        cur = new_entries[name]
        if prev is None:
            added.append(name)
        elif (cur.crc, cur.usize) != (prev.crc, prev.usize):
            changed.append(name)

    for name in sorted(prev_entries):
        if is_ignored_runtime_entry(name, include_engine=include_engine):
            continue
        if name not in new_entries:
            removed.append(name)

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()

    to_pack = added + changed
    with zipfile.ZipFile(new_zip, 'r') as src_zf, zipfile.ZipFile(
        output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True
    ) as out_zf:
        for name in to_pack:
            info = src_zf.getinfo(name)
            data = src_zf.read(name)
            new_info = zipfile.ZipInfo(filename=info.filename, date_time=info.date_time)
            new_info.compress_type = zipfile.ZIP_DEFLATED
            new_info.external_attr = info.external_attr
            out_zf.writestr(new_info, data)

        note_lines = [
            f'POKÉMON MYSTERY DUNGEON: DESTINY — MISE À JOUR {prev_version} -> {new_version}',
            '=' * 64,
            '',
            f'Fichiers ajoutés  : {len(added)}',
            f'Fichiers modifiés : {len(changed)}',
            f'Fichiers retirés  : {len(removed)}',
            f'Moteur inclus     : {"oui" if include_engine else "non (aucun changement C#)"}',
            '',
            'INSTALLATION :',
            '1. Fermez le jeu s’il est ouvert et sauvegardez votre dossier SAVE si souhaité.',
            '2. Extrayez ce ZIP dans le même dossier parent qui contient déjà « PMDO-Destiny »',
            '   (les dossiers PMDO-Destiny/Data, Content, etc. fusionnent), puis acceptez de',
            '   REMPLACER les fichiers existants.',
        ]
        if removed:
            note_lines += [
                f'3. Double-cliquez sur PMDO-Destiny/NETTOYER_ANCIENS_FICHIERS_{new_version}.bat',
                '   pour supprimer les fichiers devenus obsolètes dans votre dossier PMDO-Destiny.',
                '4. Lancez normalement JOUER_A_DESTINY.bat.',
            ]
        else:
            note_lines += ['3. Lancez normalement JOUER_A_DESTINY.bat.']
        note_bytes = ('\r\n'.join(note_lines) + '\r\n').encode('utf-8')
        out_zf.writestr(f'PMDO-Destiny/LISEZ_MOI_MISE_A_JOUR_{new_version}.txt', note_bytes)

        if removed:
            bat_lines = [
                '@echo off',
                'cd /d "%~dp0"',
            ]
            for name in removed:
                win_rel = _safe_rel_windows_path(name)
                if win_rel:
                    bat_lines.append(f'if exist "{win_rel}" del /f /q "{win_rel}"')
            bat_lines.append('echo Nettoyage termine.')
            bat_bytes = ('\r\n'.join(bat_lines) + '\r\n').encode('utf-8')
            out_zf.writestr(f'PMDO-Destiny/NETTOYER_ANCIENS_FICHIERS_{new_version}.bat', bat_bytes)

    with zipfile.ZipFile(output_zip, 'r') as check_zf:
        bad = check_zf.testzip()
        if bad is not None:
            raise RuntimeError(f'Update ZIP integrity check failed on {bad}')

    return {
        'prev_version': prev_version,
        'new_version': new_version,
        'output': str(output_zip),
        'size_bytes': output_zip.stat().st_size,
        'added_count': len(added),
        'changed_count': len(changed),
        'removed_count': len(removed),
        'include_engine': include_engine,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--new-zip', type=Path, required=True, help='Path to the newly built full Windows ZIP')
    prev_group = parser.add_mutually_exclusive_group(required=True)
    prev_group.add_argument('--prev-zip', type=Path, help='Path to the previous release full Windows ZIP')
    prev_group.add_argument('--prev-url', type=str, help='HTTP Range-capable URL to the previous release full Windows ZIP')
    parser.add_argument('--prev-version', required=True, help='Previous version string (e.g. 0.5.9)')
    parser.add_argument('--new-version', required=True, help='New version string (e.g. 0.6.0)')
    parser.add_argument('--output', type=Path, required=True, help='Destination path for the update-only ZIP')
    parser.add_argument('--include-engine', action='store_true', help='Include Destiny.exe and .pdb changes')
    parser.add_argument('--summary-file', type=Path, help='Optional JSON summary output path')
    args = parser.parse_args(argv)

    if args.prev_zip is not None:
        prev_entries = local_zip_index(args.prev_zip)
    else:
        prev_entries = remote_zip_index(args.prev_url)

    summary = build_update_zip(
        new_zip=args.new_zip,
        prev_entries=prev_entries,
        output_zip=args.output,
        prev_version=args.prev_version,
        new_version=args.new_version,
        include_engine=args.include_engine,
    )
    if args.summary_file is not None:
        args.summary_file.parent.mkdir(parents=True, exist_ok=True)
        args.summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
