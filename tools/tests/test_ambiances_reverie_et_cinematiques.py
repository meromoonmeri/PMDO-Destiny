#!/usr/bin/env python3
"""Vérifie le filtrage LUT 4 ambiances sur Réverie Town et les sprites en cinématique."""
from __future__ import annotations

from pathlib import Path
from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def main() -> None:
    # 1. C# GroundMap : LUTs, enum DestinyAmbiance, API SetDestinyAmbiance et état runtime non sérialisé
    gm = _read('engine/RogueEssence/RogueEssence/Ground/Maps/GroundMap.cs')
    for token in (
        'public enum DestinyAmbiance',
        'AubeTint = new Color(224, 203, 212)',
        'CrepusculeTint = new Color(179, 146, 173)',
        'NuitWorldTint = new Color(97, 118, 159)',
        'public static GroundMap CurrentRenderMap;',
        'private DestinyAmbiance? runtimeCharacterAmbiance;',
        'private DestinyAmbiance? runtimeWorldAmbiance;',
        'public void SetDestinyAmbiance(string ambiance)',
        'public void SetDestinyAmbiance(string ambiance, bool applyToWorld)',
        'public DestinyAmbiance CharacterAmbiance =>',
        'public DestinyAmbiance WorldAmbiance =>',
        'public bool FilterNightCharacters => CharacterAmbiance == DestinyAmbiance.Nuit;',
        'BlankBG.DrawBlank(spriteBatch, drawPos, noise.Get2DUInt64((ulong)mapPos.X, (ulong)mapPos.Y), WorldAmbianceTint);',
        'layer.Tiles[loc.X][loc.Y].Draw(spriteBatch, drawPos, tint);',
        'if (BlankBG == null)',
        'if (rand == null)',
    ):
        assert token in gm, f'Jeton manquant dans GroundMap.cs : {token}'

    # 2. Portée CurrentRenderMap dans BaseGroundScene.DrawGame et propagation sur sprites/décors/fonds
    bgs = _read('engine/RogueEssence/RogueEssence/Ground/BaseGroundScene.cs')
    assert 'GroundMap.CurrentRenderMap = ZoneManager.Instance.CurrentGround;' in bgs
    assert 'finally\n            {\n                GroundMap.CurrentRenderMap = prevRenderMap;' in bgs

    gchar = _read('engine/RogueEssence/RogueEssence/Ground/GroundChar.cs')
    assert 'GroundMap ground = Map as GroundMap ?? GroundMap.CurrentRenderMap;' in gchar
    assert 'sheet = sheet.GetDestinyNightCopy();' in gchar
    assert 'tint = GroundMap.GetAmbianceTint(charAmbiance);' in gchar
    assert 'currentCharAction.Draw(spriteBatch, offset, sheet, tint);' in gchar

    gact = _read('engine/RogueEssence/RogueEssence/Ground/GroundAction.cs')
    assert 'public virtual void Draw(SpriteBatch spriteBatch, Loc offset, CharSheet sheet, Microsoft.Xna.Framework.Color tint)' in gact
    assert 'public override void Draw(SpriteBatch spriteBatch, Loc offset, CharSheet sheet, Microsoft.Xna.Framework.Color tint)' in gact

    cai = _read('engine/RogueEssence/RogueEssence/Content/Animation/CharAfterImage.cs')
    assert 'GroundMap ground = GroundMap.CurrentRenderMap;' in cai
    assert 'sheet = sheet.GetDestinyNightCopy();' in cai

    ganim = _read('engine/RogueEssence/RogueEssence/Ground/Maps/GroundAnim.cs')
    assert 'GroundMap.CurrentRenderMap.WorldAmbianceTint' in ganim

    gobj = _read('engine/RogueEssence/RogueEssence/Ground/Maps/GroundObject.cs')
    assert 'GroundMap.CurrentRenderMap.WorldAmbianceTint' in gobj

    auto_cs = _read('engine/RogueEssence/RogueEssence/Dungeon/Tiles/AutoTile.cs')
    assert 'public void Draw(SpriteBatch spriteBatch, Loc pos, Color color)' in auto_cs
    assert 'public void DrawBlank(SpriteBatch spriteBatch, Loc pos, ulong randCode, Color color)' in auto_cs
    assert 'anim.Draw(spriteBatch, pos, GraphicsManager.TotalFrameTick, color);' in auto_cs

    mapbg = _read('engine/RogueEssence/RogueEssence/Content/Animation/Backgrounds/MapBG.cs')
    assert 'GroundMap.CurrentRenderMap.WorldAmbianceTint' in mapbg

    tilebg = _read('engine/RogueEssence/RogueEssence/Content/Animation/Backgrounds/TileBG.cs')
    assert 'Tile.DrawBlank(spriteBatch, new Loc(x, y), ulong.MaxValue, tint);' in tilebg

    # 3. Les portraits UI (SpeakerPortrait) restent strictement non teintés
    sp_path = ROOT / 'engine/RogueEssence/RogueEssence/Menu/Dialogue/SpeakerPortrait.cs'
    assert sp_path.is_file(), f'Fichier attendu introuvable : {sp_path}'
    sp_txt = sp_path.read_text(encoding='utf-8')
    for forbidden in ('WorldAmbiance', 'CharacterAmbiance', 'CurrentRenderMap', 'GetDestinyNightCopy'):
        assert forbidden not in sp_txt, f'{forbidden} ne doit pas affecter SpeakerPortrait.cs'

    # 4. meteo_reverie.lua remplace 'dark' par le filtrage LUT et couvre tous les extérieurs de Réverie
    meteo = _read('game/Data/Script/destiny/meteo_reverie.lua')
    assert "GROUND:RemoveMapStatus('dark')" in meteo
    assert "GROUND:AddMapStatus('dark')" not in meteo
    assert 'map:SetDestinyAmbiance(moment, true)' in meteo

    # 5. Exécution Lua des tests meteo_reverie
    run(ROOT / 'tools/tests/test_meteo_reverie.lua', ROOT)
    print('TEST AMBIANCES REVERIE ET CINEMATIQUES OK')


if __name__ == '__main__':
    main()
