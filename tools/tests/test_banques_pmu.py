#!/usr/bin/env python3
"""Vérifie les 40 banques PMU ajoutées à Destiny, sans toucher aux autres."""
from pathlib import Path
import struct,hashlib,json
R=Path(__file__).resolve().parents[2];pages=json.loads((R/'tools/pmu_banques_manifest.json').read_text(encoding='utf-8'))['pages'];assert len(pages)==40 and len({p['nom'] for p in pages})==40
count=0
for p in pages:
 file=R/'game/Content/Tile'/(p['nom']+'.tile');data=file.read_bytes();assert hashlib.sha256(data).hexdigest()==p['sha256_tile'],p['nom'];size,n=struct.unpack_from('<ii',data);assert size==8 and n==p['cases_8px_enregistrees'];seen=set()
 for i in range(n):
  x,y,offset=struct.unpack_from('<iiq',data,8+16*i);assert 0<=x<p['largeur_px']//8 and 0<=y<p['hauteur_px']//8 and (x,y) not in seen;seen.add((x,y));assert 8+16*n<=offset<=len(data)-8
  length=struct.unpack_from('<q',data,offset)[0];assert 0<length<=len(data)-offset-8 and data[offset+8:offset+16]==b'\x89PNG\r\n\x1a\n'
 assert (p['largeur_px']//8-1,p['hauteur_px']//8-1) in seen
 count+=n
assert count==467399
print('PASS : 40 banques PMU,',count,'positions, signatures PNG et offsets. Test éditeur et gameplay nécessaires.')
