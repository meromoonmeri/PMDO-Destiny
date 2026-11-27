from pathlib import Path
import sys,shutil
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';B=H/('.cache/destiny-test/backup-'+sys.argv[1]+'-v3')
for q in B.rglob('*'):
 if q.is_file() and q.name!='ajouts.txt':
  p=G/q.relative_to(B);p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,p);assert p.read_bytes()==q.read_bytes()
for rel in (B/'ajouts.txt').read_text().splitlines():
 p=G/rel
 if p.exists():p.unlink()
print('Restauré et comparé',sys.argv[1])
