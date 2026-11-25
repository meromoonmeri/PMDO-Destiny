#!/usr/bin/env python3
"""Reconstruit les images et les données à partir des captures de la v0.7.7."""
from pathlib import Path
import io
import json
import re
import subprocess
from PIL import Image

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
OUT = HERE / 'public' / 'media'
ARCHIVE = PROJECT / 'Kingambit-Icones-Mega'
VIDEO = PROJECT / 'Kingambit-Mise-a-jour' / 'Apercu-18-wooshes-PMD.mp4'
OUT.mkdir(parents=True, exist_ok=True)


def frame(source, second, target):
    png = subprocess.check_output([
        'ffmpeg', '-nostdin', '-v', 'error', '-ss', str(second), '-i', str(source),
        '-frames:v', '1', '-threads', '1', '-f', 'image2pipe', '-vcodec', 'png', 'pipe:1',
    ])
    with Image.open(io.BytesIO(png)) as im:
        im.convert('RGB').save(OUT / target, 'WEBP', lossless=True)


frame(PROJECT / 'Les-dojos-de-Reverie' / 'La-trappe-de-Kingambit.mp4', 1.1, 'hall.webp')
frame(VIDEO, 53.60, 'dojo-poster.webp')

captures = {
    'berry_pecha': 'Recompense-Pecha',
    'mega_charizardite_x': 'Description-Dracaufeu-X',
    'mega_charizardite_y': 'Description-Dracaufeu-Y',
    'mega_mewtwonite_x': 'Description-Mewtwo-X',
    'mega_mewtwonite_y': 'Description-Mewtwo-Y',
}
for asset in captures.values():
    with Image.open(ARCHIVE / 'Captures' / (asset + '.png')) as im:
        im.convert('RGB').save(OUT / (asset.lower() + '.webp'), 'WEBP', lossless=True)

source = (ARCHIVE / 'Les-gemmes-de-Reverie.html').read_text(encoding='utf-8')
images = re.findall(r'<article class="card"([^>]+)>(.*?)</article>', source, flags=re.S)
original = json.loads((ARCHIVE / 'Registre-icones.json').read_text(encoding='utf-8'))['items']
assert len(images) == len(original) == 54
items = []
for obj, (attrs, body) in zip(original, images):
    key = obj['id']
    assert key in attrs
    visuals = {}
    for name in ('small', 'ground'):
        m = re.search(r'<img class="' + name + r'" src="(data:image/png;base64,[A-Za-z0-9+/=]+)"', body)
        assert m, (key, name)
        visuals[name] = m.group(1)
    items.append(dict(
        id=key, name=obj['nom'], pokemon=obj.get('pokemon'),
        category=obj['genre'], description=obj['description_fr'],
        motif=obj.get('motif'), color=obj['palette'][0], variant=key.endswith(('_x', '_y')),
        icon=visuals['small'], ground=visuals['ground'],
        screenshot=f'media/{captures[key].lower()}.webp' if key in captures else None,
    ))

chapters = json.loads(subprocess.check_output([
    'ffprobe', '-v', 'error', '-show_chapters', '-of', 'json', str(VIDEO),
]))['chapters']
assert len(chapters) == 19
parts = []
for n, ch in enumerate(chapters):
    label, pokemon = ch['tags']['title'].split('. ', 1)[1].split(' — ', 1)
    parts.append(dict(i=n, label=label, pokemon=pokemon, start=float(ch['start_time']), end=float(ch['end_time'])))
(OUT / 'apercu.json').write_text(json.dumps(dict(chapters=parts, items=items), ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'{len(parts)} chapitres, {len(items)} objets et {len(captures)+2} images de jeu exportées.')
