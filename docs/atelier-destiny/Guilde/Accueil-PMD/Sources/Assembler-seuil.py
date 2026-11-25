#!/usr/bin/env python3
"""Add a reversible Accueil fixture to the active offline preview, without changing the game."""
import hashlib
import json
from pathlib import Path

import Seuil

HERE = Path(__file__).resolve().parent


def swap(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new, 1)


def insert(s, anchor, name, raw, wrap):
    left, right = [wrap.format(f'Accueil/{name}/{k}') for k in ('debut', 'fin')]
    block = left + '\n' + raw.rstrip() + '\n' + right + '\n'
    if left in s:
        before, content = s.split(left, 1)
        _, after = content.split(right + '\n', 1)
        return before + block + after
    return swap(s, anchor, block + anchor)


def main():
    path = Seuil.SOURCE
    head, d, tail = Seuil.read_page(path)
    assert 'verdure' in d, 'Appliquer d’abord la retouche de verdure.'
    assert len(d['rooms']) == 15 and sum(len(r['gates']) for r in d['rooms']) == 29
    assert sum(bool((r['south'] or {}).get('band')) for r in d['rooms']) == 7
    first = 'seuil_accueil' not in d
    before = hashlib.sha256(json.dumps({k:v for k,v in d.items() if k != 'seuil_accueil'}, ensure_ascii=False).encode()).hexdigest()
    d['seuil_accueil'], report = Seuil.build(d)
    assert before == hashlib.sha256(json.dumps({k:v for k,v in d.items() if k != 'seuil_accueil'}, ensure_ascii=False).encode()).hexdigest()
    if first:
        head = swap(head, '<title>Destiny · Bourgeons — verdure ajustée</title>', '<title>Destiny · Bourgeons — le seuil de l’Accueil</title>')
        head = swap(head, 'En mode Nuit, la lueur part des bourgeons. Les lianes ajustées suivent le bois des poteaux, avec quelques ronces courtes au pied. Les bourgeons gardent la lumière tamisée inspirée de la falaise de Grodoudou.', 'Le halo de Grodoudou et le tapis PMU sont posés sur le seuil de l’Accueil. Dans les salles, les bourgeons conservent leur lumière tamisée en mode Nuit.')
        tail = swap(tail, "const s={page:'atlas',room:data.rooms[0],phase:3,", "const s={page:'atlas',room:data.rooms[0],phase:0,seuil:true,")
        tail = swap(tail, '  const vines=lianesAt(r,p,lianes);', '  const vines=lianesAt(r,p,lianes), doorstep=seuilAt(r,p);')
        tail = swap(tail, '  if(vines.length)drawPicture(c,vines[0],0,0);', '  if(vines.length)drawPicture(c,vines[0],0,0);\n  for(const [x,y,b] of doorstep)drawPicture(c,b,x,y);')
        tail = swap(tail, '...nightBits(r,p,lianes),...items.map', '...nightBits(r,p,lianes),...doorstep.map(q=>q[2]),...items.map')
        tail = swap(tail, '...nightBits(r,i,lianes),...items.map', '...nightBits(r,i,lianes),...seuilAt(r,i).map(q=>q[2]),...items.map')
        tail = swap(tail, "  $('editor').hidden=!atelier;$('atlas-page').hidden=atelier;updateFilm();", "  $('editor').hidden=!atelier;$('atlas-page').hidden=atelier;updateFilm();updateSeuil();")
        tail = swap(tail, "  const rows=s.page==='sud'?southPairs:atlasCards;", "  if(s.page==='atlas')paintSeuil();\n  const rows=s.page==='sud'?southPairs:atlasCards;")
        tail = swap(tail, '    if(s.phase!==3||!s.lianes)return;\n    for(const [r,c,v]', "    if(s.phase!==3||!s.lianes)return;\n    if(s.page==='atlas')paintSeuil(true);\n    for(const [r,c,v]")
        tail = swap(tail, '    open.append(scene,label,meta);panel.append(open);', "    if(r.id===seuil.id)meta.append(make('span','badges-seuil','Halo au seuil'));\n    open.append(scene,label,meta);panel.append(open);")
        tail = swap(tail, 'Les cartes « Verdure ajustée » indiquent les poteaux repris. En Nuit, seuls les bourgeons émettent.', 'Les cartes « Verdure ajustée » indiquent les poteaux repris. Les bourgeons s’animent en Nuit ; le halo du seuil reste fixe.')
        tail = swap(tail, 'Objets d’origine seulement · n’inclut pas les lianes ni la lumière.', 'Objets d’origine seulement · n’inclut pas les lianes, la lumière ni l’habillage du seuil.')
        tail = swap(tail, 'setupAtlas();updatePalette();refresh();setupMotion();', 'setupSeuil();setupAtlas();updatePalette();refresh();setupMotion();')
    head = insert(head, '</style>', 'style', (HERE / 'Panneau.css').read_text(encoding='utf-8'), '/* {} */')
    head = insert(head, '  <section class="panel video-demo"', 'section', (HERE / 'Panneau.html').read_text(encoding='utf-8'), '<!-- {} -->')
    tail = insert(tail, 'setupSeuil();setupAtlas();', 'script', (HERE / 'Panneau.js').read_text(encoding='utf-8'), '// {}')
    html = head + Seuil.MARK + json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</','<\\/') + '</script>' + tail
    tmp = path.with_suffix('.part')
    tmp.write_text(html, encoding='utf-8'); tmp.replace(path)
    report['donnees_heritees_sha256'] = before
    Seuil.write_report('Index-seuil.json', report)
    print(f'PASS · halo de G01P02A et tapis PMU placés à l’Accueil · {path.name} · {path.stat().st_size:,} o')


if __name__ == '__main__':
    main()
