#!/usr/bin/env python3
"""Indépendance des nouvelles planches et conservation de toute la ville.
Tests structurels et pixel-identiques, pas un test de gameplay/éditeur.
"""
from pathlib import Path
import json,gzip,re,hashlib,struct
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'tools/reverie_geographie_manifest.json').read_text(encoding='utf8'))
with gzip.open(ROOT/'tools/reverie_geographie_correspondance.json.gz','rt',encoding='utf8') as f:trans=json.load(f)
assert len(trans)==manifest['tuiles_distinctes']==39091
def addr(entry):
 sheet,x,y=entry;return f'"Sheet":"{sheet}","TexLoc":{{"X":{x},"Y":{y}}}'.encode()
reverse={addr(e['nouvelle']):addr(e['source']) for e in trans}
assert len(reverse)==len({addr(e['source']) for e in trans})==len(trans)
pattern=re.compile(rb'"Sheet":"Reverie_Geo_[A-Za-z0-9_]+","TexLoc":\{"X":-?\d+,"Y":-?\d+\}')
for name,d in manifest['cartes'].items():
 raw=(ROOT/'game/Data/Ground'/f'{name}.rsground').read_bytes();assert len(raw)==d['size'] and hashlib.sha256(raw).hexdigest()==d['sha256'];assert b'Reverie_WV_' not in raw and b'Metano_Town' not in raw
 count=0
 def replace(m):
  global count
  count+=1;assert m.group() in reverse,m.group();return reverse[m.group()]
 old=pattern.sub(replace,raw);assert count==d['references_converties'] and hashlib.sha256(old).hexdigest()==d['sha256_avant'],name
 print('PASS',name,count,'frames, carte initiale exactement reconstituée')
def load(name):
 b=(ROOT/'game/Content/Tile'/f'{name}.tile').read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8
 idx={(x,y):off for x,y,off in (struct.unpack_from('<iiq',b,8+16*i) for i in range(n))};assert len(idx)==n
 return b,idx
cache={}
def tile(triple):
 name,x,y=triple
 if name not in cache:cache[name]=load(name)
 b,idx=cache[name];off=idx[(x,y)];ln=struct.unpack_from('<q',b,off)[0];assert ln>0 and off+8+ln<=len(b)
 return b[off:off+8+ln]
for item in trans:assert tile(item['source'])==tile(item['nouvelle']),item
expected={x['banque'] for x in manifest['planches']};assert len(expected)==14
assert {p.stem for p in (ROOT/'game/Content/Tile').glob('Reverie_Geo_*.tile')}==expected
for entry in manifest['planches']:
 name=entry['banque'];data,idx=cache[name];assert len(idx)==entry['tuiles'] and hashlib.sha256(data).hexdigest()==entry['sha256_tile']
 assert (ROOT/'art/reverie/tilesheets'/f'{name}.png').exists()
print('PASS 14 nouvelles planches, 39091 tuiles identiques à la source, toutes frames préservées')
