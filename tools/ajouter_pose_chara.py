#!/usr/bin/env python3
"""Ajoute l'animation Pose au payload normal d'un .chara PMDO.

Attention aux deux indices distincts : dans le .chara, la clé du groupe est
le FrameType global du moteur (Pose = 50 dans GFXParams.xml), tandis que
l'<Index> SpriteCollab (13 pour les sources Dazzling) est seulement
l'InternalIndex conservé dans le groupe.

Le conteneur et toutes ses autres formes/animations sont conservés.  La
méthode suit RogueEssence.Content.CharSheet.Import pour AnimData.xml :
recadrage au contenu, centre de boîte, marqueurs Offsets/Shadow, atlas
prémultiplié et conversion des lignes SpriteCollab vers l'ordre Dir8 moteur.
"""
from __future__ import annotations

import argparse
import io
import math
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fusionner_conteneurs_pmd import load_container, node_at, read_node, walk, write_container, write_node

POSE_FRAME_TYPE = 50  # GraphicsManager.GetAnimIndex('Pose') dans GFXParams.xml
ANCIEN_MAUVAIS_FRAME_TYPE = 13  # Slice : ancienne Pose rangée sous la mauvaise clé


def rd(fmt, data, pos):
    size = struct.calcsize(fmt)
    vals = struct.unpack_from(fmt, data, pos)
    return (vals[0] if len(vals) == 1 else vals), pos + size


def parse_blob(blob):
    pos = 0
    length, pos = rd('<q', blob, pos)
    png = blob[pos:pos + length]
    pos += length
    image = Image.open(io.BytesIO(png)).convert('RGBA')
    (tile_w, tile_h), pos = rd('<ii', blob, pos)
    (shadow, offset_count), pos = rd('<ii', blob, pos)
    offsets = []
    for _ in range(offset_count):
        vals, pos = rd('<iiiiiiii', blob, pos)
        offsets.append(tuple(vals))
    key_count, pos = rd('<i', blob, pos)
    groups = {}
    for _ in range(key_count):
        (frame_type, internal, copy_of), pos = rd('<iii', blob, pos)
        group = {'internal': internal, 'copy': copy_of, 'rush': -1, 'hit': -1,
                 'return': -1, 'seqs': []}
        if copy_of <= -1:
            (group['rush'], group['hit'], group['return'], seq_count), pos = rd('<iiii', blob, pos)
            for _ in range(seq_count):
                frame_count, pos = rd('<i', blob, pos)
                frames = []
                for _ in range(frame_count):
                    (fx, fy, duration), pos = rd('<iii', blob, pos)
                    flip, pos = rd('?', blob, pos)
                    (ox, oy, sx, sy), pos = rd('<iiii', blob, pos)
                    frames.append((fx, fy, duration, bool(flip), ox, oy, sx, sy))
                group['seqs'].append(frames)
        groups[frame_type] = group
    if pos != len(blob):
        raise ValueError(f'blob .chara mal terminé: {pos}/{len(blob)}')
    return {'image': image, 'tw': tile_w, 'th': tile_h, 'shadow': shadow,
            'offsets': offsets, 'groups': groups}


def serialize_blob(data):
    out = io.BytesIO()
    png = io.BytesIO()
    data['image'].save(png, format='PNG', optimize=False)
    png = png.getvalue()
    out.write(struct.pack('<q', len(png)))
    out.write(png)
    out.write(struct.pack('<ii', data['tw'], data['th']))
    out.write(struct.pack('<ii', data['shadow'], len(data['offsets'])))
    for vals in data['offsets']:
        out.write(struct.pack('<iiiiiiii', *vals))
    out.write(struct.pack('<i', len(data['groups'])))
    for frame_type, group in data['groups'].items():
        out.write(struct.pack('<iii', frame_type, group['internal'], group['copy']))
        if group['copy'] > -1:
            continue
        out.write(struct.pack('<iiii', group['rush'], group['hit'], group['return'], len(group['seqs'])))
        for seq in group['seqs']:
            out.write(struct.pack('<i', len(seq)))
            for fx, fy, duration, flip, ox, oy, sx, sy in seq:
                out.write(struct.pack('<iii', fx, fy, duration))
                out.write(struct.pack('?', bool(flip)))
                out.write(struct.pack('<iiii', ox, oy, sx, sy))
    return out.getvalue()


def premultiply(image):
    px = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r * a // 255, g * a // 255, b * a // 255, a)
    return image


def last_exact(image, rgb):
    found = None
    px = image.load()
    for y in range(image.height):
        for x in range(image.width):
            if px[x, y][:3] == rgb and px[x, y][3] == 255:
                found = (x, y)
    return found


def last_channel(image, channel):
    found = None
    px = image.load()
    for y in range(image.height):
        for x in range(image.width):
            pixel = px[x, y]
            if pixel[3] == 255 and pixel[channel] == 255:
                found = (x, y)
    return found


def marker_offsets(offset_cell, bounds_center):
    black = last_exact(offset_cell, (0, 0, 0))
    red = last_exact(offset_cell, (255, 0, 0)) or last_channel(offset_cell, 0)
    green = last_exact(offset_cell, (0, 255, 0)) or last_channel(offset_cell, 1)
    blue = last_exact(offset_cell, (0, 0, 255)) or last_channel(offset_cell, 2)
    if red is None or green is None or blue is None:
        raise ValueError('marqueurs Offsets rouge/vert/bleu incomplets')
    center = green
    head = black or center
    points = (center, head, red, blue)  # Center, Head, LeftHand, RightHand
    return tuple(c for point in points for c in (point[0] - bounds_center[0], point[1] - bounds_center[1]))


def add_pose(blob, sprite_dir):
    data = parse_blob(blob)
    if (POSE_FRAME_TYPE in data['groups']
            and data['groups'][POSE_FRAME_TYPE]['copy'] <= -1
            and data['groups'][POSE_FRAME_TYPE]['seqs']):
        raise ValueError('une vraie animation Pose existe déjà dans ce payload')

    root = ET.parse(sprite_dir / 'AnimData.xml').getroot()
    pose_node = None
    for anim in root.findall('./Anims/Anim'):
        if anim.findtext('Name') == 'Pose':
            pose_node = anim
            break
    if pose_node is None:
        raise ValueError('AnimData.xml sans Pose')
    fw = int(pose_node.findtext('FrameWidth'))
    fh = int(pose_node.findtext('FrameHeight'))
    durations = [int(x.text) for x in pose_node.findall('./Durations/Duration')]
    internal = int(pose_node.findtext('Index', '13'))

    anim_sheet = Image.open(sprite_dir / 'Pose-Anim.png').convert('RGBA')
    shadow_sheet = Image.open(sprite_dir / 'Pose-Shadow.png').convert('RGBA')
    offset_sheet = Image.open(sprite_dir / 'Pose-Offsets.png').convert('RGBA')
    cols = anim_sheet.width // fw
    rows = anim_sheet.height // fh
    if cols != len(durations) or rows != 8:
        raise ValueError(f'Pose inattendue: {cols} colonnes, {rows} lignes')

    atlas = data['image']
    atlas_cols = atlas.width // data['tw']
    if atlas_cols <= 0:
        raise ValueError('atlas sans colonne')
    # Les offsets existants correspondent aux tuiles uniques déjà packées ;
    # les nouvelles tuiles commencent donc à cet indice séquentiel.
    next_index = len(data['offsets'])
    additions = []  # (index, image recadrée prémultipliée, offsets)
    dedupe = {}
    sequences = []

    for engine_dir in range(8):
        sheet_row = (8 - engine_dir) % 8
        seq = []
        for col in range(cols):
            box = (col * fw, sheet_row * fh, col * fw + fw, sheet_row * fh + fh)
            anim_cell = anim_sheet.crop(box)
            shadow_cell = shadow_sheet.crop(box)
            offset_cell = offset_sheet.crop(box)
            bbox = anim_cell.getbbox()
            if bbox is None:
                bbox = (fw // 2, fh // 2, fw // 2 + 1, fh // 2 + 1)
            crop = anim_cell.crop(bbox)
            if crop.width > data['tw'] or crop.height > data['th']:
                raise ValueError(f'frame Pose {crop.size} plus grande que la tuile atlas {(data["tw"], data["th"])}')
            bounds_center = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
            offdata = marker_offsets(offset_cell, bounds_center)
            crop = premultiply(crop.copy())
            key = (crop.tobytes(), crop.width, crop.height, offdata)
            if key in dedupe:
                tile_index = dedupe[key]
            else:
                tile_index = next_index
                next_index += 1
                dedupe[key] = tile_index
                additions.append((tile_index, crop, offdata))
            frame_offset = (bounds_center[0] - fw // 2, bounds_center[1] - fh // 2)
            white = last_exact(shadow_cell, (255, 255, 255))
            shadow_offset = (white[0] - fw // 2, white[1] - fh // 2) if white else (0, 0)
            seq.append((tile_index % atlas_cols, tile_index // atlas_cols, durations[col], False,
                        frame_offset[0], frame_offset[1], shadow_offset[0], shadow_offset[1]))
        sequences.append(seq)

    needed_rows = int(math.ceil(next_index / atlas_cols)) if next_index else atlas.height // data['th']
    new_h = max(atlas.height, needed_rows * data['th'])
    if new_h != atlas.height:
        new_atlas = Image.new('RGBA', (atlas.width, new_h), (0, 0, 0, 0))
        new_atlas.alpha_composite(atlas, (0, 0))
        atlas = new_atlas
    # Les OffsetData sont indexés par y * colonnes + x ; compléter jusqu'au
    # nouvel indice maximum (les additions sont séquentielles, donc sans trou).
    while len(data['offsets']) < next_index:
        data['offsets'].append((0, 0, 0, 0, 0, 0, 0, 0))
    for tile_index, crop, offdata in additions:
        tx = (tile_index % atlas_cols) * data['tw'] + data['tw'] // 2 - crop.width // 2
        ty = (tile_index // atlas_cols) * data['th'] + data['th'] // 2 - crop.height // 2
        atlas.alpha_composite(crop, (tx, ty))
        data['offsets'][tile_index] = offdata
    data['image'] = atlas
    data['groups'][POSE_FRAME_TYPE] = {
        'internal': internal, 'copy': -1, 'rush': -1, 'hit': -1,
        'return': -1, 'seqs': sequences}
    return serialize_blob(data), {'frames': cols * 8, 'tuiles_ajoutees': len(additions),
                                   'atlas': atlas.size, 'tuile': (data['tw'], data['th'])}



def migrate_pose(blob):
    """Déplace l’ancienne Pose de la clé Slice (13) vers Pose (50).

    L’InternalIndex SpriteCollab (13) et toutes les frames sont conservés.
    Retourne (blob, True) si une migration a eu lieu, sinon (blob, False).
    """
    data = parse_blob(blob)
    if POSE_FRAME_TYPE in data['groups']:
        return blob, False
    group = data['groups'].get(ANCIEN_MAUVAIS_FRAME_TYPE)
    if group is None or group['copy'] > -1 or not group['seqs']:
        raise ValueError('ancienne Pose introuvable sous la clé 13')
    if group['internal'] != ANCIEN_MAUVAIS_FRAME_TYPE:
        raise ValueError(
            f"groupe 13 inattendu (InternalIndex {group['internal']}), migration refusée")
    data['groups'][POSE_FRAME_TYPE] = data['groups'].pop(ANCIEN_MAUVAIS_FRAME_TYPE)
    return serialize_blob(data), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chara', type=Path, required=True)
    ap.add_argument('--sprites', type=Path)
    ap.add_argument('--migrer', action='store_true',
                    help='déplacer une ancienne Pose de la clé 13 vers la clé 50')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    container = load_container(args.chara, 'Chara')
    if container.payload is None:
        raise ValueError('payload normal absent à la racine du conteneur')
    if args.migrer:
        new_payload, migre = migrate_pose(container.payload)
        info = {'migré': migre}
    else:
        if args.sprites is None:
            ap.error('--sprites est requis sans --migrer')
        new_payload, info = add_pose(container.payload, args.sprites)
    container.payload = new_payload
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_container(args.out, container)
    reloaded = load_container(args.out, 'Chara')
    parsed = parse_blob(reloaded.payload)
    assert POSE_FRAME_TYPE in parsed['groups']
    assert len(parsed['groups'][POSE_FRAME_TYPE]['seqs']) == 8
    print(args.out, info, 'groupes', sorted(parsed['groups']))


if __name__ == '__main__':
    main()
