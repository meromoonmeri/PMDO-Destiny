#!/usr/bin/env python3
"""Analyse légère (streaming/regex) de fichiers .rsground / .rsmap PMDO.

Pour chaque fichier : sha256, octets, Version, TexSize, AssetName, Name,
dimensions (obstacles), nb de calques, feuilles (Sheet), fonds (AnimIndex),
musique, marqueurs, espèces, et callbacks script.
Ne charge pas le JSON complet en mémoire (fichiers jusqu'à 300 Mo).
"""
import re, sys, json, hashlib, os, collections

RX_SHEET = re.compile(rb'"Sheet":\s*"((?:[^"\\]|\\.)*)"')
RX_ANIM = re.compile(rb'"AnimIndex":\s*"((?:[^"\\]|\\.)*)"')
RX_MUSIC = re.compile(rb'"Music":\s*"((?:[^"\\]|\\.)*)"')
RX_VERSION = re.compile(rb'"Version":\s*"([^"]*)"')
RX_TEX = re.compile(rb'"TexSize":\s*(\d+)')
RX_ASSET = re.compile(rb'"AssetName":\s*"((?:[^"\\]|\\.)*)"')
RX_LAYER = re.compile(rb'\{\s*"Name":\s*"((?:[^"\\]|\\.)*)",\s*"Layer":\s*(\d+),\s*"Visible":\s*(true|false),\s*"Tiles"')
RX_MARKER = re.compile(rb'"\$type":\s*"RogueEssence\.Ground\.GroundMarker, RogueEssence"[^}]*?"EntName":\s*"((?:[^"\\]|\\.)*)"', re.S)
RX_ENTNAME = re.compile(rb'"EntName":\s*"((?:[^"\\]|\\.)*)"')
RX_SPECIES = re.compile(rb'"Species":\s*"((?:[^"\\]|\\.)*)"')
RX_SCRIPT = re.compile(rb'"Script":\s*"((?:[^"\\]|\\.)*)"')
RX_STATUS = re.compile(rb'"Status":\s*\{([^}]*)\}')
RX_OBJSPRITE = re.compile(rb'"ObjectAnim":\s*\{\s*"AnimIndex":\s*"((?:[^"\\]|\\.)*)"')
RX_TYPE = re.compile(rb'"\$type":\s*"([^"]*)"')


def dims_from_obstacles(data):
    """Dimensions logiques depuis le tableau obstacles [x][y] (compte les lignes)."""
    i = data.find(b'"obstacles":')
    if i < 0:
        return None
    # Première colonne : compter les objets jusqu'à la fermeture ']'
    j = data.find(b'[', i)
    j2 = data.find(b'[', j + 1)
    k = data.find(b']', j2)
    first_col = data[j2:k]
    h = first_col.count(b'"Tags"')
    # Nombre de colonnes : compter les '[' de premier niveau entre j et la fin du tableau obstacles
    # On parcourt en profondeur
    depth = 0
    cols = 0
    pos = j
    end = None
    n = len(data)
    while pos < n:
        c = data[pos:pos + 1]
        if c == b'[':
            depth += 1
            if depth == 2:
                cols += 1
        elif c == b']':
            depth -= 1
            if depth == 0:
                end = pos
                break
        elif c == b'"':
            # sauter la chaîne
            pos += 1
            while pos < n and data[pos:pos + 1] != b'"':
                if data[pos:pos + 1] == b'\\':
                    pos += 1
                pos += 1
        pos += 1
    return [cols, h]


def dims_from_rsmap(data):
    m = re.search(rb'"Width":\s*(\d+),\s*"Height":\s*(\d+)', data)
    if m:
        return [int(m.group(1)), int(m.group(2))]
    return None


def scan(path):
    with open(path, 'rb') as f:
        data = f.read()
    res = {
        'path': path,
        'bytes': len(data),
        'sha256': hashlib.sha256(data).hexdigest(),
    }
    m = RX_VERSION.search(data[:200])
    res['version'] = m.group(1).decode() if m else None
    m = RX_TEX.search(data[:400])
    res['texSize'] = int(m.group(1)) if m else None
    m = RX_TYPE.search(data[:300])
    res['type'] = m.group(1).decode().split(',')[0] if m else None
    m = RX_ASSET.search(data)
    res['assetName'] = m.group(1).decode('utf-8', 'replace') if m else None
    # Name (DefaultText) juste après "Name": {
    m = re.search(rb'"Name":\s*\{\s*"DefaultText":\s*"((?:[^"\\]|\\.)*)"', data[:2000])
    if m:
        res['title'] = m.group(1).decode('utf-8', 'replace')
    else:
        m = re.search(rb'"Name":\s*"((?:[^"\\]|\\.)*)"', data[:2000])
        res['title'] = m.group(1).decode('utf-8', 'replace') if m else None
    m = re.search(rb'"LocalTexts":\s*\{\s*"fr":\s*"((?:[^"\\]|\\.)*)"', data[:3000])
    res['title_fr'] = m.group(1).decode('utf-8', 'replace') if m else None
    sheets = collections.Counter(s.decode('utf-8', 'replace') for s in RX_SHEET.findall(data))
    res['sheets'] = dict(sheets)
    res['anims'] = sorted(set(s.decode('utf-8', 'replace') for s in RX_ANIM.findall(data) if s))
    res['music'] = sorted(set(s.decode('utf-8', 'replace') for s in RX_MUSIC.findall(data) if s))
    res['scripts'] = sorted(set(s.decode('utf-8', 'replace') for s in RX_SCRIPT.findall(data) if s))
    res['species'] = sorted(set(s.decode('utf-8', 'replace') for s in RX_SPECIES.findall(data) if s))
    layers = RX_LAYER.findall(data)
    res['layers'] = [l[0].decode('utf-8', 'replace') for l in layers]
    if res['type'] and 'GroundMap' in res['type']:
        res['dims'] = dims_from_obstacles(data)
    else:
        res['dims'] = dims_from_rsmap(data)
    # markers : EntName dans la section Entities (après "Entities")
    ei = data.find(b'"Entities":')
    ents = data[ei:] if ei >= 0 else b''
    res['entNames'] = sorted(set(s.decode('utf-8', 'replace') for s in RX_ENTNAME.findall(ents)))
    res['hasEntities'] = ei >= 0
    m = re.search(rb'"MapChars":\s*\[\s*\]', ents)
    res['mapCharsEmpty'] = bool(m)
    st = RX_STATUS.search(data)
    res['status'] = [s.decode() for s in re.findall(rb'"([^"]+)":\s*\{', st.group(1))] if st else []
    return res


def main():
    out = {}
    paths = sys.argv[1:]
    for p in paths:
        try:
            out[p] = scan(p)
        except Exception as e:
            out[p] = {'path': p, 'error': repr(e)}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
