#!/usr/bin/env python3
"""Vérifie les identifiants actifs et l'index natif de la banque Réverie."""
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'game' / 'Data'
TILES = ROOT / 'game' / 'Content' / 'Tile'
OLD = re.compile(rb'metano|m\xc3\xa9tano|m\xc3\x89tano', re.IGNORECASE)


def inspect(path: Path) -> None:
    tail = b''
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            block = tail + chunk
            assert not OLD.search(block), f'ancien nom dans {path}'
            tail = block[-16:]


assert (DATA / 'Ground' / 'WaterfallVillageCapital.rsground').is_file(), 'ville non reconstituée'
for path in DATA.rglob('*'):
    if path.is_file():
        assert 'metano' not in str(path.relative_to(DATA)).casefold()
        assert 'métano' not in str(path.relative_to(DATA)).casefold()
        inspect(path)

files = list(TILES.glob('*.tile'))
assert files, 'aucune planche'
names = [p.stem for p in files]
assert len(names) == len({n.casefold() for n in names}), 'noms de planches en collision'
assert all('metano' not in n.casefold() and 'métano' not in n.casefold() for n in names)
index = TILES / 'index.idx'
assert index.is_file(), 'index des planches absent'


def read_dotnet_length(f):
    result = shift = 0
    for _ in range(5):
        b = f.read(1)
        assert b, 'index tronqué'
        value = b[0]
        result |= (value & 127) << shift
        if value < 128:
            return result
        shift += 7
    raise AssertionError('longueur .NET invalide')


with index.open('rb') as f:
    head = f.read(4)
    assert len(head) == 4
    count = struct.unpack('<i', head)[0]
    assert count == len(names), (count, len(names))
    indexed = []
    for _ in range(count):
        length = read_dotnet_length(f)
        name = f.read(length).decode('utf-8')
        indexed.append(name)
        hdr = f.read(8)
        assert len(hdr) == 8
        _, nodes = struct.unpack('<ii', hdr)
        assert nodes >= 0
        f.seek(nodes * 16, 1)
    assert f.tell() == index.stat().st_size, 'index tronqué ou octets supplémentaires'
assert indexed == sorted(names), 'index des planches désynchronisé'
print(f'OK : données actives sans ancien nom et index conforme pour {len(names)} planches.')
