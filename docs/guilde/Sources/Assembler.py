#!/usr/bin/env python3
"""Réassemble la page autonome à partir du gabarit, du CSS et du JS.

Sans argument, réutilise les données graphiques exactes déjà embarquées dans
Guilde-Destiny.html. --donnees accepte un nouveau JSON compact compatible.
"""
import argparse
from pathlib import Path

P=Path(__file__).resolve().parent
F=next((q/'Guilde-Destiny.html' for q in (P.parent,P.parent.parent) if (q/'Guilde-Destiny.html').is_file()),P.parent/'Guilde-Destiny.html')
OPEN='<script id="donnees" type="application/json">'
CLOSE='</script>'

def main():
 a=argparse.ArgumentParser(description=__doc__)
 a.add_argument('--donnees',type=Path)
 a.add_argument('--sortie',type=Path,default=F)
 x=a.parse_args()
 if x.donnees is not None:
  d=x.donnees.read_text(encoding='utf-8')
 else:
  d=F.read_text(encoding='utf-8').split(OPEN,1)[1].split(CLOSE,1)[0]
 template=(P/'Atelier.gabarit.html').read_text(encoding='utf-8')
 for token,body in {'CSS':(P/'Atelier.css').read_text(encoding='utf-8'),'JS':(P/'Atelier.js').read_text(encoding='utf-8'),'DONNEES':d}.items():
  tag=f'/*@{token}@*/'
  assert template.count(tag)==1
  template=template.replace(tag,body)
 temp=x.sortie.with_suffix('.tmp');temp.write_text(template,encoding='utf-8');temp.replace(x.sortie)
 print(f'{x.sortie.name} · {x.sortie.stat().st_size:,} octets · autonome')

if __name__=='__main__':main()
