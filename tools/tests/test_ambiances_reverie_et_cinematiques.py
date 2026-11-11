#!/usr/bin/env python3
"""Vérifie le filtrage LUT 4 ambiances sur Réverie Town et les sprites en cinématique."""
from __future__ import annotations

import io
import json
from pathlib import Path
import struct
from PIL import Image
from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def _decode_tile_sheet(path: Path) -> dict[tuple[int, int], Image.Image]:
    raw = path.read_bytes()
    _, cnt = struct.unpack_from('<ii', raw, 0)
    out: dict[tuple[int, int], Image.Image] = {}
    cache: dict[int, Image.Image] = {}
    for i in range(cnt):
        tx, ty, off = struct.unpack_from('<iiq', raw, 8 + i * 16)
        if off not in cache:
            (plen,) = struct.unpack_from('<q', raw, off)
            cache[off] = Image.open(io.BytesIO(raw[off + 8 : off + 8 + plen])).convert('RGBA')
        out[(tx, ty)] = cache[off]
    return out


def _verify_zrv2_sea_and_moon() -> None:
    docs: dict[str, dict] = {}
    sheets: dict[str, dict[tuple[int, int], Image.Image]] = {}
    for amb, sfx in (('jour', 'J'), ('aube', 'A'), ('crepuscule', 'C'), ('nuit', 'N')):
        stem = f'zrv2_zone_reveil_{amb}'
        doc = json.loads((ROOT / f'game/Data/Ground/{stem}.rsground').read_text(encoding='utf-8-sig'))['Object']
        assert doc['AssetName'] == stem and doc['EdgeView'] == 1, stem
        docs[amb] = doc
        by_name = {lyr['Name']: lyr for lyr in doc['Layers']}
        for hidden_key in ('07 ondes', '08 scintillement', '09 houle', '10 reflet', '11 ecume'):
            matches = [lyr for name, lyr in by_name.items() if hidden_key in name]
            for lyr in matches:
                assert lyr.get('Visible') is False, (stem, lyr['Name'])
                assert all(not c.get('Layers') for col in lyr['Tiles'] for c in col), (stem, lyr['Name'])
        if amb in ('aube', 'crepuscule'):
            ast_layers = [lyr for name, lyr in by_name.items() if '03 astre' in name]
            assert ast_layers and ast_layers[0].get('Visible') is False, stem
            assert all(not c.get('Layers') for col in ast_layers[0]['Tiles'] for c in col), stem
        mer = next(lyr for name, lyr in by_name.items() if '06 mer' in name)
        assert mer.get('Visible') is True, stem
        mer_sheet = f'ZRV2{sfx}_06_MER'
        sheets[mer_sheet] = _decode_tile_sheet(ROOT / f'game/Content/Tile/{mer_sheet}.tile')
        sea_tiles = 0
        for col in mer['Tiles']:
            for cell in col:
                for tl in cell.get('Layers', []):
                    frs = tl.get('Frames', [])
                    if frs:
                        assert len(frs) == 12 and isinstance(tl.get('FrameLength'), int) and tl['FrameLength'] > 0
                        for fr in frs:
                            assert fr['Sheet'] == mer_sheet
                            assert (fr['TexLoc']['X'], fr['TexLoc']['Y']) in sheets[mer_sheet]
                        sea_tiles += 1
        assert sea_tiles == 96 * 23, (stem, sea_tiles)

    # Jour : scintillement stationnaire à l'horizon (py=118) sans dérive R->L
    jour_mer = next(lyr for lyr in docs['jour']['Layers'] if '06 mer' in lyr['Name'])['Tiles']
    sh_j = sheets['ZRV2J_06_MER']
    hz_f0 = []
    hz_f1 = []
    quiet_f0 = []
    quiet_f5 = []
    for tx in range(96):
        loc0 = jour_mer[tx][14]['Layers'][0]['Frames'][0]['TexLoc']
        loc1 = jour_mer[tx][14]['Layers'][0]['Frames'][1]['TexLoc']
        im0 = sh_j[(loc0['X'], loc0['Y'])]
        im1 = sh_j[(loc1['X'], loc1['Y'])]
        hz_f0.extend(im0.getpixel((dx, 6))[:3] for dx in range(8))
        hz_f1.extend(im1.getpixel((dx, 6))[:3] for dx in range(8))
        q0 = jour_mer[tx][17]['Layers'][0]['Frames'][0]['TexLoc']
        q5 = jour_mer[tx][17]['Layers'][0]['Frames'][5]['TexLoc']
        qm0 = sh_j[(q0['X'], q0['Y'])]
        qm5 = sh_j[(q5['X'], q5['Y'])]
        quiet_f0.extend(qm0.getpixel((dx, 2))[:3] for dx in range(8))
        quiet_f5.extend(qm5.getpixel((dx, 2))[:3] for dx in range(8))
    assert hz_f0 != hz_f1
    for sx in range(1, 24):
        assert hz_f1 != hz_f0[sx:] + hz_f0[:sx], f'Dérive R->L horizon détectée (sx={sx})'
    assert quiet_f0 == quiet_f5, 'La bande calme d horizon ne doit pas glisser horizontalement'

    # Nuit : lune PMU_01 centrée derrière le sommet (x=384), halo saphir et reflet fuselé dans l'eau
    nuit_by = {lyr['Name']: lyr for lyr in docs['nuit']['Layers']}
    sh_sky = _decode_tile_sheet(ROOT / 'game/Content/Tile/ZRV2N_01_CIEL.tile')
    sh_moon = _decode_tile_sheet(ROOT / 'game/Content/Tile/ZRV2N_03_ASTRE.tile')
    sh_n = sheets['ZRV2N_06_MER']
    ast_l = next(lyr for name, lyr in nuit_by.items() if '03 astre' in name)
    assert ast_l.get('Visible') is True
    # Centre lune (x=384, y=8 -> tx=48, ty=1) opaque jaune-or
    m_loc = ast_l['Tiles'][48][1]['Layers'][0]['Frames'][0]['TexLoc']
    mr, mg, mb, ma = sh_moon[(m_loc['X'], m_loc['Y'])].getpixel((0, 0))
    assert ma == 255 and mr >= 200 and mg >= 180 and mb < 210, (mr, mg, mb, ma)
    # Halo saphir autour du pic (tx=44, ty=3 -> x=352, y=28) plus bleu que le ciel lointain (tx=12, ty=3 -> x=96, y=28)
    ciel_l = next(lyr for name, lyr in nuit_by.items() if '01 ciel' in name)['Tiles']
    h_loc = ciel_l[44][3]['Layers'][0]['Frames'][0]['TexLoc']
    f_loc = ciel_l[12][3]['Layers'][0]['Frames'][0]['TexLoc']
    hr, hg, hb, _ = sh_sky[(h_loc['X'], h_loc['Y'])].getpixel((0, 4))
    fr, fg, fb, _ = sh_sky[(f_loc['X'], f_loc['Y'])].getpixel((0, 4))
    assert hb > fb + 20 and hg >= fg, ((hr, hg, hb), (fr, fg, fb))
    # Reflet centré dans l'eau (x=384, ty=16 -> y=132) brillant vs mer éloignée (x=96, ty=16), puis effacé avant la berge (ty=28)
    mer_n = next(lyr for name, lyr in nuit_by.items() if '06 mer' in name)['Tiles']
    rl_loc = mer_n[48][16]['Layers'][0]['Frames'][0]['TexLoc']
    rn_loc = mer_n[12][16]['Layers'][0]['Frames'][0]['TexLoc']
    rb_loc = mer_n[48][28]['Layers'][0]['Frames'][0]['TexLoc']
    rl_px = sh_n[(rl_loc['X'], rl_loc['Y'])].getpixel((0, 4))[:3]
    rn_px = sh_n[(rn_loc['X'], rn_loc['Y'])].getpixel((0, 4))[:3]
    rb_px = sh_n[(rb_loc['X'], rb_loc['Y'])].getpixel((0, 4))[:3]
    assert sum(rl_px) > sum(rn_px) + 120, (rl_px, rn_px)
    assert sum(rb_px) < sum(rl_px) - 100, (rb_px, rl_px)


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

    # 5. Mer Sharpedo + Lune PMU_01 sur zrv2_zone_reveil_{jour,aube,crepuscule,nuit}
    _verify_zrv2_sea_and_moon()

    # 6. Exécution Lua des tests meteo_reverie
    run(ROOT / 'tools/tests/test_meteo_reverie.lua', ROOT)
    print('TEST AMBIANCES REVERIE ET CINEMATIQUES OK')


if __name__ == '__main__':
    main()
