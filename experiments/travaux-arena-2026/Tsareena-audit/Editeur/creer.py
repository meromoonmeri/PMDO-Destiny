from pathlib import Path
import base64
p=Path(__file__).parent;r=p.parent
url=lambda f:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode()
s=(p/'modele.html').read_text().replace('__SHEET__',url(r/'Polish-nettete/Walk-palette15-ESSAI.png')).replace('__REFERENCE__',url(r/'refs-spritecollab/Walk-Anim.png'))
(r/'Apercu-actuel/index.html').write_text(s);(p/'Editeur-Mega-Tsareena.html').write_text(s)
print('Editeur autonome construit, spritesheets incluses')
