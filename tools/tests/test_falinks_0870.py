#!/usr/bin/env python3
"""Vérifie l'intégration complète de Falinks (#0870 / Hexadron) dans PMDO-Destiny."""
from __future__ import annotations

import io
import json
import struct
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "base"
GAME = ROOT / "game"
sys.path.insert(0, str(ROOT / "tools"))

from ajouter_pose_chara import parse_blob
from fusionner_conteneurs_pmd import fallback, load_container, node_at, read_node, walk


def _assert_same_node_tree(a, b, path=()):
    assert a.pos == b.pos, (path, a.pos, b.pos)
    assert set(a.kids) == set(b.kids), (path, set(a.kids), set(b.kids))
    for k in a.kids:
        _assert_same_node_tree(a.kids[k], b.kids[k], path + (k,))


def main() -> None:
    # 1. Sources archivées et crédits
    art = ROOT / "art/sprites/falinks_0870"
    assert (art / "README.md").is_file()
    assert (art / "sprite/AnimData.xml").is_file()
    assert (art / "sprite/credits.txt").is_file()
    assert (art / "portrait/planche_spritebot.png").is_file()
    assert (art / "portrait/credits.txt").is_file()

    # 2. Conteneur Chara 870 : Forme 0 escouade 6 unités + Formes 1/2 base préservées
    base_c = load_container(BASE / "Content/Chara/870.chara", "Chara")
    game_c = load_container(GAME / "Content/Chara/870.chara", "Chara")
    for gender in (0, 1, 2):
        blob = fallback(game_c, 0, 0, gender)
        assert blob is not None
        parsed = parse_blob(blob)
        assert parsed["shadow"] == 2, parsed["shadow"]
        assert parsed["tw"] <= 2048 and parsed["th"] <= 2048
        assert sorted(parsed["groups"]) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 40, 41, 42, 43]
        assert len(parsed["groups"][3]["seqs"]) == 1   # Sleep (1 direction)
        assert len(parsed["groups"][1]["seqs"]) == 8   # Idle (8 directions)
        assert parsed["groups"][8]["copy"] == 5        # Strike -> Attack
    for preserved_path in ((1,), (1, 1), (2,), (2, 1)):
        assert node_at(game_c, preserved_path).payload == node_at(base_c, preserved_path).payload

    # 3. Conteneur Portrait 870 : 16 émotions + 16 miroirs en Forme 0 + base préservée
    base_p = load_container(BASE / "Content/Portrait/870.portrait", "Portrait")
    game_p = load_container(GAME / "Content/Portrait/870.portrait", "Portrait")
    expected_emotes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17]
    for gender in (0, 1, 2):
        pblob = fallback(game_p, 0, 0, gender)
        assert pblob is not None
        ln = struct.unpack_from("<q", pblob, 0)[0]
        im = Image.open(io.BytesIO(pblob[8 : 8 + ln]))
        im.verify()
        pw, ph, cnt = struct.unpack_from("<iii", pblob, 8 + ln)
        assert (pw, ph) == (40, 40)
        emotes = [struct.unpack_from("<ii?", pblob, 8 + ln + 12 + i * 9) for i in range(cnt)]
        assert [e[0] for e in emotes] == expected_emotes
        assert all(e[2] is True for e in emotes)
    for preserved_path in ((0, 1), (1,), (1, 1), (2,), (2, 1)):
        assert node_at(game_p, preserved_path).payload == node_at(base_p, preserved_path).payload

    # 4. Index profonds Chara et Portrait synchronisés avec tous les fichiers sur disque
    idx_c, _ = read_node((GAME / "Content/Chara/index.idx").read_bytes())
    chara_files = {int(p.stem): p for p in (GAME / "Content/Chara").glob("*.chara")}
    assert 870 in chara_files and set(idx_c.kids) == set(chara_files)
    _assert_same_node_tree(idx_c.kids[870], game_c, (870,))

    idx_p, _ = read_node((GAME / "Content/Portrait/index.idx").read_bytes())
    portrait_files = {int(p.stem): p for p in (GAME / "Content/Portrait").glob("*.portrait")}
    assert 870 in portrait_files and set(idx_p.kids) == set(portrait_files)
    _assert_same_node_tree(idx_p.kids[870], game_p, (870,))

    # 5. Monster falinks.json & index.idx débloqués (Released: true)
    falinks = json.loads((GAME / "Data/Monster/falinks.json").read_text(encoding="utf-8-sig"))["Object"]
    assert falinks["IndexNum"] == 870
    assert falinks["Released"] is True
    assert falinks["Forms"][0]["Released"] is True
    assert falinks["Name"]["LocalTexts"]["fr"] == "Hexadron"

    mon_idx = json.loads((GAME / "Data/Monster/index.idx").read_text(encoding="utf-8-sig"))["Object"]
    assert "falinks" in mon_idx
    assert mon_idx["falinks"]["Released"] is True
    assert mon_idx["falinks"]["Forms"][0]["Released"] is True
    assert mon_idx["falinks"]["SortOrder"] == 870

    print("TEST FALINKS 0870 OK")


if __name__ == "__main__":
    main()
