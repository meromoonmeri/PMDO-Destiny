#!/usr/bin/env python3
"""Intègre Falinks (#0870 / Hexadron) dans PMDO-Destiny.

Convertit les sources SpriteCollab de l'escouade 6 unités et la planche
SpriteBot 16 émotions (+ miroirs) vers les conteneurs PMDO 0.8.12
`game/Content/Chara/870.chara` et `game/Content/Portrait/870.portrait` en
préservant toutes les formes/skins existantes de `base/`, reconstruit les
index profonds `Chara/index.idx` et `Portrait/index.idx`, et débloque
`game/Data/Monster/falinks.json` + `game/Data/Monster/index.idx` (`Released: true`).
"""
from __future__ import annotations

import io
import json
import math
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from ajouter_pose_chara import premultiply
from fusionner_conteneurs_pmd import (
    Node,
    copy_node,
    ensure,
    fallback,
    load_container,
    node_at,
    walk,
    write_container,
    write_node,
)

FALINKS_SPECIES = "falinks"
FALINKS_DEX = 870
ART_DIR = ROOT / "art/sprites/falinks_0870"
SPRITE_SRC = ART_DIR / "sprite"
PORTRAIT_SHEET = ART_DIR / "portrait/planche_spritebot.png"


def load_gfx_params(root: Path = ROOT) -> tuple[dict[str, int], list[str]]:
    gfx = ET.fromstring((root / "base/Base/GFXParams.xml").read_text(encoding="utf-8-sig"))
    actions = {a.findtext("Name"): i for i, a in enumerate(gfx.findall("./Actions/Action"))}
    emotions = [e.findtext("Name") for e in gfx.findall("./Emotions/Emotion")]
    return actions, emotions


def _center_bounds(left: int, top: int, right: int, bottom: int) -> tuple[int, int]:
    min_x = min(left, -right)
    min_y = min(top, -bottom)
    max_x = max(-left, right)
    max_y = max(-top, bottom)
    return max_x - min_x, max_y - min_y


def build_chara_blob(sprite_dir: Path, actions: dict[str, int]) -> bytes:
    """Reproduit CharSheet.Import(AnimData.xml) + CharSheet.Save de PMDO 0.8.12."""
    tree = ET.parse(sprite_dir / "AnimData.xml").getroot()
    shadow_size = int(tree.findtext("ShadowSize"))
    cutscene_idle = tree.find("CutsceneIdle") is not None

    seq_specs: dict[int, dict] = {}
    for anim in tree.findall("./Anims/Anim"):
        name = anim.findtext("Name")
        if name not in actions:
            raise ValueError(f"Action inconnue dans GFXParams.xml: {name}")
        anim_idx = actions[name]
        idx_el = anim.find("Index")
        internal = int(idx_el.text) if idx_el is not None else -1
        copy_el = anim.find("CopyOf")
        if copy_el is not None:
            seq_specs[anim_idx] = {
                "name": name,
                "internal": internal,
                "copy": actions[copy_el.text],
            }
            continue
        fw = int(anim.findtext("FrameWidth"))
        fh = int(anim.findtext("FrameHeight"))
        rush = int(anim.findtext("RushFrame", "-1"))
        hit = int(anim.findtext("HitFrame", "-1"))
        ret = int(anim.findtext("ReturnFrame", "-1"))
        durs = [int(x.text) for x in anim.findall("./Durations/Duration")]
        seq_specs[anim_idx] = {
            "name": name,
            "internal": internal,
            "copy": -1,
            "fw": fw,
            "fh": fh,
            "rush": rush,
            "hit": hit,
            "ret": ret,
            "durs": durs,
        }

    frames: list[tuple[Image.Image, tuple[int, ...]]] = []
    frame_to_seq: list[tuple[int, int, int]] = []
    anim_groups: dict[int, dict] = {}
    max_w = 0
    max_h = 0

    for kk, spec in seq_specs.items():
        if spec["copy"] > -1:
            anim_groups[kk] = {
                "internal": spec["internal"],
                "copy": spec["copy"],
                "rush": -1,
                "hit": -1,
                "ret": -1,
                "seqs": [],
            }
            continue

        name = spec["name"]
        fw, fh, durs = spec["fw"], spec["fh"], spec["durs"]
        im_a = premultiply(Image.open(sprite_dir / f"{name}-Anim.png").convert("RGBA"))
        im_s = Image.open(sprite_dir / f"{name}-Shadow.png").convert("RGBA")
        im_o = Image.open(sprite_dir / f"{name}-Offsets.png").convert("RGBA")
        if not (im_a.size == im_s.size == im_o.size):
            raise ValueError(f"Tailles incohérentes pour {name}")
        if im_a.width % fw != 0 or im_a.height % fh != 0:
            raise ValueError(f"Dimensions non divisibles par {fw}x{fh} pour {name}")
        cols, rows = im_a.width // fw, im_a.height // fh
        if cols != len(durs) or rows not in (1, 8):
            raise ValueError(f"Grille invalide ({cols}x{rows}) pour {name}")

        seqs = []
        for eng_dir in range(8):
            sheet_idx = (8 - eng_dir) % 8
            if sheet_idx >= rows:
                continue
            seq = []
            for col in range(cols):
                box = (col * fw, sheet_idx * fh, (col + 1) * fw, (sheet_idx + 1) * fh)
                cell_a = im_a.crop(box)
                cell_s = im_s.crop(box)
                cell_o = im_o.crop(box)
                bbox = cell_a.getbbox()
                if bbox is None:
                    bbox = (fw // 2, fh // 2, fw // 2 + 1, fh // 2 + 1)
                cw, ch = bbox[2] - bbox[0], bbox[3] - bbox[1]
                crop = cell_a.crop(bbox)
                max_w = max(max_w, cw)
                max_h = max(max_h, ch)
                bx, by = bbox[0] + cw // 2, bbox[1] + ch // 2

                opx = cell_o.load()
                black = red = green = blue = None
                for yy in range(fh):
                    for xx in range(fw):
                        r, g, b, a = opx[xx, yy]
                        if a == 255 and r == 0 and g == 0 and b == 0:
                            black = (xx, yy)
                        if a == 255 and r == 255:
                            red = (xx, yy)
                        if a == 255 and g == 255:
                            green = (xx, yy)
                        if a == 255 and b == 255:
                            blue = (xx, yy)
                if red is not None and green is not None and blue is not None:
                    c_pt = green
                    h_pt = black if black is not None else c_pt
                    l_pt = red
                    r_pt = blue
                else:
                    if any(x is not None for x in (black, red, green, blue)):
                        raise ValueError(f"Offsets incomplets pour {name} dir={sheet_idx} col={col}")
                    c_pt = h_pt = l_pt = r_pt = (bx, by)

                off = (
                    c_pt[0] - bx, c_pt[1] - by,
                    h_pt[0] - bx, h_pt[1] - by,
                    l_pt[0] - bx, l_pt[1] - by,
                    r_pt[0] - bx, r_pt[1] - by,
                )
                o_left = min(off[0], off[2], off[4], off[6])
                o_top = min(off[1], off[3], off[5], off[7])
                o_right = max(off[0], off[2], off[4], off[6]) + 1
                o_bot = max(off[1], off[3], off[5], off[7]) + 1
                cow, coh = _center_bounds(o_left, o_top, o_right, o_bot)
                max_w = max(max_w, cow)
                max_h = max(max_h, coh)

                spx = cell_s.load()
                white = None
                for yy in range(fh):
                    for xx in range(fw):
                        if spx[xx, yy] == (255, 255, 255, 255):
                            white = (xx, yy)
                sx, sy = (white[0] - fw // 2, white[1] - fh // 2) if white is not None else (0, 0)

                frames.append((crop, off))
                frame_to_seq.append((kk, len(seqs), col))
                seq.append([0, 0, durs[col], False, bx - fw // 2, by - fh // 2, sx, sy])
            seqs.append(seq)
        anim_groups[kk] = {
            "internal": spec["internal"],
            "copy": -1,
            "rush": spec["rush"],
            "hit": spec["hit"],
            "ret": spec["ret"],
            "seqs": seqs,
        }

    max_w = ((max_w - 1) // 2 + 1) * 2
    max_h = ((max_h - 1) // 2 + 1) * 2

    def flip_off(o: tuple[int, ...], odd_w: bool) -> tuple[int, ...]:
        dx = 1 if odd_w else 0
        return (
            -o[0] - 1 + dx, o[1],
            -o[2] - 1 + dx, o[3],
            -o[4] - 1 + dx, o[5],
            -o[6] - 1 + dx, o[7],
        )

    final_frames = []
    frame_map = []
    for crop, off in frames:
        sz = crop.size
        raw = crop.tobytes()
        odd_w = (sz[0] % 2 == 1)
        hit_idx = None
        hit_flip = False
        for yy, (_fcrop, foff, fraw, fflip_raw, fsz) in enumerate(final_frames):
            if fsz == sz and fraw == raw and foff == off:
                hit_idx, hit_flip = yy, False
                break
            if fsz == sz and fflip_raw == raw and flip_off(foff, odd_w) == off:
                hit_idx, hit_flip = yy, True
                break
        if hit_idx is None:
            hit_idx = len(final_frames)
            hit_flip = False
            fc = crop.transpose(Image.FLIP_LEFT_RIGHT).tobytes()
            final_frames.append((crop, off, raw, fc, sz))
        frame_map.append((hit_idx, hit_flip))

    atlas_cols = math.ceil(math.sqrt(len(final_frames)))
    atlas = Image.new("RGBA", (atlas_cols * max_w, atlas_cols * max_h), (0, 0, 0, 0))
    offsets_out = []
    for ii, (crop, off, *_rest) in enumerate(final_frames):
        dx = max_w // 2 - crop.width // 2
        dy = max_h // 2 - crop.height // 2
        tx = (ii % atlas_cols) * max_w + dx
        ty = (ii // atlas_cols) * max_h + dy
        atlas.alpha_composite(crop, (tx, ty))
        offsets_out.append(off)

    for ii, (kk, dir_i, col_i) in enumerate(frame_to_seq):
        f_idx, is_flip = frame_map[ii]
        fr = anim_groups[kk]["seqs"][dir_i][col_i]
        fr[0] = f_idx % atlas_cols
        fr[1] = f_idx // atlas_cols
        fr[3] = is_flip
        if is_flip and frames[ii][0].width % 2 == 1:
            fr[4] += 1

    idle_id = actions["Idle"]
    while anim_groups[idle_id]["copy"] > -1:
        idle_id = anim_groups[idle_id]["copy"]
    if cutscene_idle:
        anim_groups[0] = {"internal": -1, "copy": idle_id, "rush": -1, "hit": -1, "ret": -1, "seqs": []}
    else:
        none_seqs = []
        for s in anim_groups[idle_id]["seqs"]:
            f0 = list(s[0])
            f0[2] = 1
            none_seqs.append([tuple(f0)])
        anim_groups[0] = {"internal": -1, "copy": -1, "rush": -1, "hit": -1, "ret": -1, "seqs": none_seqs}

    png_buf = io.BytesIO()
    atlas.save(png_buf, format="PNG")
    png_bytes = png_buf.getvalue()
    out = io.BytesIO()
    out.write(struct.pack("<q", len(png_bytes)))
    out.write(png_bytes)
    out.write(struct.pack("<iiii", max_w, max_h, shadow_size, len(offsets_out)))
    for off in offsets_out:
        out.write(struct.pack("<iiiiiiii", *off))
    ordered_keys = sorted(anim_groups)
    out.write(struct.pack("<i", len(ordered_keys)))
    for kk in ordered_keys:
        g = anim_groups[kk]
        out.write(struct.pack("<iii", kk, g["internal"], g["copy"]))
        if g["copy"] > -1:
            continue
        out.write(struct.pack("<iiii", g["rush"], g["hit"], g["ret"], len(g["seqs"])))
        for s in g["seqs"]:
            out.write(struct.pack("<i", len(s)))
            for fx, fy, dur, flp, ox, oy, sx, sy in s:
                out.write(struct.pack("<iii", fx, fy, dur))
                out.write(struct.pack("?", bool(flp)))
                out.write(struct.pack("<iiii", ox, oy, sx, sy))
    return out.getvalue()


def build_portrait_blob(sheet_path: Path, emotions: list[str]) -> bytes:
    """Reproduit PortraitSheet.Import(Sheet.png) + PortraitSheet.Save de PMDO 0.8.12."""
    sheet = Image.open(sheet_path).convert("RGBA")
    if sheet.width % 40 != 0 or sheet.height % 40 != 0:
        raise ValueError(f"Dimensions de planche portrait invalides: {sheet.size}")
    tw = sheet.width // 40
    th = sheet.height // 40
    sheets = []
    emote_map = []
    n_emo = len(emotions)
    for ii in range(n_emo):
        xx, yy = ii % tw, ii // tw
        tile = sheet.crop((xx * 40, yy * 40, (xx + 1) * 40, (yy + 1) * 40))
        if tile.getbbox() is not None:
            r_idx = ii + n_emo
            has_rev = False
            rtile = None
            if r_idx < tw * th:
                rxx, ryy = r_idx % tw, r_idx // tw
                cand = sheet.crop((rxx * 40, ryy * 40, (rxx + 1) * 40, (ryy + 1) * 40))
                if cand.getbbox() is not None:
                    has_rev = True
                    rtile = cand
            emote_map.append((ii, len(sheets), has_rev))
            sheets.append(premultiply(tile.copy()))
            if has_rev:
                sheets.append(premultiply(rtile.copy()))
    if not sheets:
        raise ValueError("Planche portrait vide")
    full_w = math.ceil(math.sqrt(len(sheets)))
    atlas = Image.new("RGBA", (full_w * 40, full_w * 40), (0, 0, 0, 0))
    for idx, tile in enumerate(sheets):
        atlas.alpha_composite(tile, ((idx % full_w) * 40, (idx // full_w) * 40))
    png_buf = io.BytesIO()
    atlas.save(png_buf, format="PNG")
    png_bytes = png_buf.getvalue()
    out = io.BytesIO()
    out.write(struct.pack("<q", len(png_bytes)))
    out.write(png_bytes)
    out.write(struct.pack("<iii", 40, 40, len(emote_map)))
    for emo_i, pos_i, has_rev in emote_map:
        out.write(struct.pack("<ii?", emo_i, pos_i, has_rev))
    return out.getvalue()


def rebuild_container_index(content_dir: Path, kind: str, ext: str) -> None:
    index = Node()
    for p in sorted(content_dir.glob(f"*.{ext}"), key=lambda item: int(item.stem)):
        index.kids[int(p.stem)] = load_container(p, kind)
    buf = io.BytesIO()
    write_node(index, buf)
    (content_dir / "index.idx").write_bytes(buf.getvalue())


def integrate(root: Path = ROOT) -> None:
    actions, emotions = load_gfx_params(root)

    # 1. Conteneur .chara (Forme 0 + fallback racine ; Formes 1/2/shinies de base/ conservées)
    chara_blob = build_chara_blob(SPRITE_SRC, actions)
    base_chara = load_container(root / f"base/Content/Chara/{FALINKS_DEX}.chara", "Chara")
    merged_chara = copy_node(base_chara)
    for path in ((), (0,), (0, 0), (0, 0, 0), (0, 0, 1), (0, 0, 2)):
        ensure(merged_chara, path).payload = chara_blob
    out_chara = root / f"game/Content/Chara/{FALINKS_DEX}.chara"
    write_container(out_chara, merged_chara)
    reloaded_chara = load_container(out_chara, "Chara")
    for path, node in walk(base_chara):
        if node.payload is not None:
            assert node_at(reloaded_chara, path).payload == node.payload
    for gender in (0, 1, 2):
        assert fallback(reloaded_chara, 0, 0, gender) == chara_blob

    # 2. Conteneur .portrait (Forme 0 + fallback racine ; (0,1) shiny & Formes 1/2 conservées)
    portrait_blob = build_portrait_blob(PORTRAIT_SHEET, emotions)
    base_portrait = load_container(root / f"base/Content/Portrait/{FALINKS_DEX}.portrait", "Portrait")
    merged_portrait = copy_node(base_portrait)
    for path in ((), (0,), (0, 0), (0, 0, 0), (0, 0, 1), (0, 0, 2)):
        ensure(merged_portrait, path).payload = portrait_blob
    out_portrait = root / f"game/Content/Portrait/{FALINKS_DEX}.portrait"
    write_container(out_portrait, merged_portrait)
    reloaded_portrait = load_container(out_portrait, "Portrait")
    for path, node in walk(base_portrait):
        if path != () and node.payload is not None:
            assert node_at(reloaded_portrait, path).payload == node.payload
    for gender in (0, 1, 2):
        assert fallback(reloaded_portrait, 0, 0, gender) == portrait_blob

    # 3. Index profonds Chara et Portrait
    rebuild_container_index(root / "game/Content/Chara", "Chara", "chara")
    rebuild_container_index(root / "game/Content/Portrait", "Portrait", "portrait")

    # 4. Fiche espèce Monster + Monster/index.idx (Released: true)
    monster = json.loads((root / f"base/Data/Monster/{FALINKS_SPECIES}.json").read_text(encoding="utf-8-sig"))
    monster["Object"]["Released"] = True
    monster["Object"]["Forms"][0]["Released"] = True
    (root / f"game/Data/Monster/{FALINKS_SPECIES}.json").write_text(
        json.dumps(monster, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    base_mon_idx = json.loads((root / "base/Data/Monster/index.idx").read_text(encoding="utf-8-sig"))
    game_mon_idx = json.loads((root / "game/Data/Monster/index.idx").read_text(encoding="utf-8-sig"))
    falinks_summary = json.loads(json.dumps(base_mon_idx["Object"][FALINKS_SPECIES], ensure_ascii=False))
    falinks_summary["Released"] = True
    falinks_summary["Forms"][0]["Released"] = True
    game_mon_idx["Object"][FALINKS_SPECIES] = falinks_summary
    (root / "game/Data/Monster/index.idx").write_text(
        json.dumps(game_mon_idx, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    print(
        f"Falinks #{FALINKS_DEX} intégré : "
        f"{out_chara.relative_to(root)} ({out_chara.stat().st_size} o), "
        f"{out_portrait.relative_to(root)} ({out_portrait.stat().st_size} o), "
        f"game/Data/Monster/{FALINKS_SPECIES}.json + index.idx"
    )


if __name__ == "__main__":
    integrate()
