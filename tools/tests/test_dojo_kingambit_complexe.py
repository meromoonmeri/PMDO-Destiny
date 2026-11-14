#!/usr/bin/env python3
"""Tests structurels et comportementaux du complexe Dojo Kingambit (accueil, arène, reliques)."""
import json
import os
from pathlib import Path
from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / "game"

z = json.loads((GAME / "Data/Zone/dojo_kingambit_salles.json").read_text(encoding="utf-8-sig"))["Object"]["GroundMaps"]
idx = json.loads((GAME / "Data/Zone/index.idx").read_text(encoding="utf-8-sig"))["Object"]["dojo_kingambit_salles"]["Grounds"]
assert z == idx == ["dojo_kingambit_arene", "dojo_kingambit_reliques"]

acc = json.loads((GAME / "Data/Ground/dojo_kingambit.rsground").read_text(encoding="utf-8-sig"))["Object"]
assert len(acc["Layers"]) == 15
assert [acc["Layers"][i]["Visible"] for i in range(8, 14)] == [True, False, False, True, False, False]

for room in ("dojo_kingambit_arene", "dojo_kingambit_reliques"):
    g = json.loads((GAME / f"Data/Ground/{room}.rsground").read_text(encoding="utf-8-sig"))["Object"]
    assert g["AssetName"] == room and g["TexSize"] == 1 and g["EdgeView"] == 1 and len(g["Layers"]) == 9

os.chdir(ROOT)
run(ROOT / "tools/tests/test_dojo_kingambit_complexe.lua", ROOT)
print("PASS complexe Dojo Kingambit : zone, 3 GroundMaps, 15+9+9 calques et simulation Lua validés.")
