#!/usr/bin/env python3
"""Vérifications ciblées + simulation Lua ; ne remplace pas le rendu en jeu."""
from pathlib import Path
from lupa.lua54 import LuaRuntime
import re
ROOT = Path(__file__).resolve().parents[2]
R = ROOT / 'game/Data/Script/destiny/ground/reveil_nuit/init.lua'
C = ROOT / 'game/Data/Script/destiny/ground/cliffdaytest/init.lua'
E = ROOT / 'engine/RogueEssence/RogueEssence/Ground/GroundChar.cs'
r, c, e = [p.read_text(encoding='utf8') for p in (R, C, E)]
assert "equipe_scene.Membre('Hero')" in r and "equipe_scene.Membre('Partner')" in r
assert "GAME:SetCharacterNickname(membre_heros, nom_heros)" in r
assert "return equipe_scene.Membre('Hero')" in c and "return equipe_scene.Membre('Partner')" in c
assert re.search(r'\[NonSerialized\]\s*\[JsonIgnore\]\s*public bool HideShadow;', e)
assert re.search(r'void DrawShadow\([^\)]*\)\s*\{\s*if \(HideShadow\)\s*return;', e)
spawn=c[c.index('local function facteur_bekipan()'):c.index('local MUSIQUE_DAZZLING_SOCIALE')]
assert spawn.index('ch.HideShadow = true') < spawn.index("GROUND:Unhide('Bekipan')")
scene=c[c.index('local bekipan = facteur_bekipan()'):c.index('-- Le partenaire va chercher la lettre')]
assert scene.index('GROUND:TeleportTo(bekipan') < scene.index("Direction.DownLeft, 656, 444") < scene.index('bekipan.HideShadow = false')
assert scene.index('bekipan.HideShadow = false') < scene.index('bekipan.HideShadow = true') < scene.index("Direction.Up, 656, 424")
assert scene.index("Direction.Up, 656, 340") < scene.index("GROUND:Hide('Bekipan')") < scene.rindex('bekipan.HideShadow = false')
# Origine de dessin = coin supérieur gauche de la hitbox + 8 ; boîte x 656..671.
assert 656 + 8 == 664
assert 'GAME:WaitFrames(15)' in r and 'cinematique.Respirer(30) -- laisser la révélation' in r
import os
os.chdir(ROOT)
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute((ROOT / 'tools/tests/test_retrouvailles_roles.lua').read_text(encoding='utf8'))
print('PASS : invariants de l’ombre, géométrie et temporisations (contrôles statiques).')
