from pathlib import Path
import shutil,sys
p=Path(__file__).resolve().parent
source=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else p.parent/'Walk-frame-par-frame'
page=source/'index.html'
if not page.is_file(): raise SystemExit(f'Page introuvable : {page}')
# Copies do not alter the source or the image originals. Copy latest HTML to a fixed address.
tmp=p/'index.tmp';shutil.copy2(page,tmp);tmp.replace(p/'index.html')
print('Aperçu unique actualisé depuis',source)
