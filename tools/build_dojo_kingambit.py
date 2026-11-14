#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère l'intérieur pixel-art du Dojo Kingambit (dojo_kingambit.rsground + Kingambit_Dojo_Interieur.tile).

Style fidèle à la façade extérieure de Réverie Town (KINGAMBIT DOJO.tile) :
  - Murs en pierre ocre taillée, soubassements sombres et piliers en bois d'acajou sombre ;
  - Bannières samouraï cramoisies et or frappées de l'emblème de lame de Scalpereur ;
  - Grande arène centrale d'entraînement en ardoise noire sertie d'ocre, de laque rouge
    et du blason doré (kuwagata + lame frontale) ;
  - Estrade nord pour Maître Kaito (Kingambit) sous une arche torii-kabuto en avant-plan
    (DrawLayer.Top) aux moustaches-lames obsidienne/cramoisi ;
  - Braseros samouraï (kagaribi) animés sur 4 phases + lanternes murales andon ;
  - Tapis d'accueil rouge et blanc fidèle au seuil extérieur au sud.

Préserve intégralement les entités sérialisées (Kingambit, MarowakDojoExit,
MarowakDojoDungeonEntrance, MarowakDojoExitMarker, MarowakDojoDungeonEntranceMarker,
TEAMMATE_1, TEAMMATE_2), TexSize=1, EdgeView=1 et les 9 calques.
"""
from __future__ import annotations

import io
import json
import math
import struct
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
TILE_OUT = GAME / "Content/Tile/Kingambit_Dojo_Interieur.tile"
GROUND_PATH = GAME / "Data/Ground/dojo_kingambit.rsground"
SHEET_NAME = "Kingambit_Dojo_Interieur"

MAP_W, MAP_H = 512, 512
TS = 8
GW, GH = MAP_W // TS, MAP_H // TS  # 64 x 64

# Palette PMD DS fidèle à KINGAMBIT DOJO.tile
VOID = (18, 12, 16, 255)
INK = (26, 16, 20, 255)

# Pierre ocre taillée
ST_HI = (238, 204, 138, 255)
ST_LT = (214, 170, 100, 255)
ST_MD = (180, 132, 68, 255)
ST_DK = (136, 92, 46, 255)
ST_SH = (92, 58, 30, 255)
ST_OUT = (54, 32, 18, 255)

# Bois sombre / acajou charpente
WD_HI = (132, 74, 52, 255)
WD_MD = (98, 50, 36, 255)
WD_DK = (66, 31, 24, 255)
WD_SH = (40, 18, 16, 255)

# Plancher cyprès ambré du dojo
FL_HI = (210, 162, 98, 255)
FL_LT = (192, 143, 82, 255)
FL_MD = (173, 124, 67, 255)
FL_DK = (146, 100, 52, 255)
FL_SEAM = (118, 76, 38, 255)

# Ardoise / fer noir Kingambit
SL_HI = (92, 94, 110, 255)
SL_LT = (68, 70, 84, 255)
SL_MD = (48, 50, 62, 255)
SL_DK = (34, 35, 45, 255)
SL_SH = (22, 22, 30, 255)

# Cramoisi impérial & laque samouraï
CR_HI = (226, 72, 76, 255)
CR_LT = (198, 48, 54, 255)
CR_MD = (158, 32, 41, 255)
CR_DK = (114, 21, 30, 255)
CR_SH = (74, 13, 20, 255)

# Or shogun (kuwagata & lame frontale)
GD_SP = (255, 244, 168, 255)
GD_HI = (244, 204, 82, 255)
GD_MD = (204, 152, 44, 255)
GD_DK = (146, 100, 24, 255)

# Ivoire / papier shoji / paille makiwara
IV_HI = (248, 242, 228, 255)
IV_MD = (224, 212, 190, 255)
IV_DK = (186, 170, 144, 255)
STW_HI = (230, 198, 120, 255)
STW_MD = (196, 158, 84, 255)
STW_DK = (148, 112, 52, 255)


def h2(x: int, y: int, seed: int = 0) -> int:
    n = (x * 374761393 + y * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return (n ^ (n >> 16)) & 0xFFFFFFFF


def put(im: Image.Image, x: int, y: int, c: tuple[int, int, int, int]) -> None:
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), c)


def fill_rect(im: Image.Image, x0: int, y0: int, x1: int, y1: int, c: tuple[int, int, int, int]) -> None:
    for y in range(max(0, y0), min(im.height, y1)):
        for x in range(max(0, x0), min(im.width, x1)):
            im.putpixel((x, y), c)


def draw_stone_wall_face(im: Image.Image, x0: int, y0: int, x1: int, y1: int) -> None:
    """Maçonnerie en pierre ocre taillée à joints décalés (style PMD DS)."""
    brick_h = 12
    brick_w = 24
    for y in range(y0, y1):
        ry = y - y0
        row = ry // brick_h
        by = ry % brick_h
        offset = (row % 2) * (brick_w // 2)
        for x in range(x0, x1):
            rx = x - x0 + offset
            bx = rx % brick_w
            v = h2(rx // brick_w, row, 11) % 5
            if by == 0 or by == brick_h - 1 or bx == 0:
                c = ST_SH if by == brick_h - 1 else ST_DK
            elif by == 1 and 1 <= bx <= brick_w - 2:
                c = ST_HI if v >= 2 else ST_LT
            elif by == brick_h - 2 or bx == brick_w - 1:
                c = ST_DK
            else:
                if v == 0:
                    c = ST_LT
                elif v in (1, 2):
                    c = ST_MD
                else:
                    c = ST_LT if ((x + y) % 4 == 0) else ST_MD
                # Légère patine pixel-art
                if h2(x, y, 29) % 23 == 0:
                    c = ST_HI if by < 5 else ST_DK
            put(im, x, y, c)
    # Plinthe sombre en bois/pierre au pied du mur
    fill_rect(im, x0, y1 - 6, x1, y1 - 4, WD_HI)
    fill_rect(im, x0, y1 - 4, x1, y1 - 1, WD_DK)
    fill_rect(im, x0, y1 - 1, x1, y1, ST_OUT)
    # Corniche supérieure moulurée
    fill_rect(im, x0, y0, x1, y0 + 2, ST_OUT)
    fill_rect(im, x0, y0 + 2, x1, y0 + 5, WD_MD)
    fill_rect(im, x0, y0 + 5, x1, y0 + 7, GD_MD)
    fill_rect(im, x0, y0 + 7, x1, y0 + 8, ST_SH)


def draw_stone_wall_top(im: Image.Image, x0: int, y0: int, x1: int, y1: int) -> None:
    """Couronnement épais des murs en gros blocs de grès ocre biseautés + poutre d'acajou."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            dx_edge = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
            if dx_edge == 0:
                c = INK
            elif dx_edge in (1, 2):
                c = WD_SH
            elif dx_edge in (3, 4):
                c = WD_HI if (x - x0 <= 4 or y - y0 <= 4) and dx_edge == 3 else WD_MD
            elif dx_edge == 5:
                c = GD_MD if (x + y) % 8 in (0, 1) else WD_DK
            else:
                # Maçonnerie de grès ocre organique à assises décalées (fidèle à KINGAMBIT DOJO.tile)
                course_h = 10
                ry = y // course_h
                by = y % course_h
                w_var = 18 if (ry % 2 == 0) else 22
                off = (ry * 11) % w_var
                bx = (x + off) % w_var
                bid = (x + off) // w_var
                tone = h2(bid, ry, 17) % 4
                # Coins arrondis de chaque pierre taillée
                corner = (by in (1, course_h - 2)) and (bx in (1, w_var - 2))
                if by == 0 or bx == 0 or corner:
                    c = ST_SH
                elif by == course_h - 1 or bx == w_var - 1:
                    c = ST_DK
                elif by == 1 or bx == 1:
                    c = ST_HI if (by == 1 and bx < w_var - 3 and tone != 3) else ST_LT
                elif by == course_h - 2 or bx == w_var - 2:
                    c = ST_DK if tone >= 2 else ST_MD
                else:
                    c = ST_LT if tone == 0 else (ST_MD if tone in (1, 2) else ST_DK)
                    if h2(x, y, 61) % 19 == 0:
                        c = ST_HI if by <= 3 else ST_DK
            put(im, x, y, c)


def draw_pillar(im: Image.Image, x0: int, y0: int, w: int, h: int) -> None:
    """Pilier samouraï en bois d'acajou sombre cerclé de ferrures dorées (kanagu)."""
    for y in range(y0, y0 + h):
        ry = y - y0
        for x in range(x0, x0 + w):
            rx = x - x0
            if rx == 0 or rx == w - 1 or ry == 0 or ry == h - 1:
                c = ST_OUT
            elif ry in (6, 7, h - 10, h - 9):
                # Bagues dorées kanagu
                c = GD_HI if 2 <= rx <= w - 4 else GD_DK
            elif ry in (8, h - 8):
                c = WD_SH
            elif ry >= h - 6:
                # Socle en pierre noire taillée
                c = SL_HI if rx in (2, 3) else (SL_MD if rx < w - 3 else SL_DK)
            else:
                if rx in (1, 2):
                    c = WD_DK
                elif rx in (3, 4):
                    c = WD_HI
                elif rx < w - 3:
                    c = WD_MD
                else:
                    c = WD_SH
            put(im, x, y, c)


def draw_wood_floor(im: Image.Image, x0: int, y0: int, x1: int, y1: int) -> None:
    """Plancher du dojo en lattes de cyprès ambré poli."""
    plank_h = 8
    plank_w = 32
    for y in range(y0, y1):
        row = y // plank_h
        py = y % plank_h
        off = (row * 13) % plank_w
        for x in range(x0, x1):
            px = (x + off) % plank_w
            pid = (x + off) // plank_w
            tone = h2(pid, row, 41) % 4
            if py == 0:
                c = FL_SEAM
            elif px == 0:
                c = FL_DK if py > 1 else FL_SEAM
            elif py == 1:
                c = FL_HI if tone in (0, 1) else FL_LT
            elif py == plank_h - 1:
                c = FL_DK
            else:
                base = FL_LT if tone == 0 else (FL_MD if tone in (1, 2) else FL_DK)
                # Veinage horizontal discret
                if py in (3, 5) and (h2(x // 4, row, 99) % 7 == 0):
                    base = FL_HI if base == FL_LT else FL_LT
                c = base
            put(im, x, y, c)


def draw_slate_passage(im: Image.Image, x0: int, y0: int, x1: int, y1: int) -> None:
    """Dallage d'ardoise sombre pour le couloir nord et le seuil."""
    for y in range(y0, y1):
        row = y // 12
        by = y % 12
        off = (row % 2) * 10
        for x in range(x0, x1):
            bx = (x + off) % 20
            if by == 0 or bx == 0:
                c = SL_SH
            elif by == 1:
                c = SL_LT
            else:
                c = SL_MD if h2((x + off) // 20, row, 53) % 2 == 0 else SL_DK
            put(im, x, y, c)


def draw_dais(im: Image.Image, x0: int, y0: int, x1: int, y1: int) -> None:
    """Estrade surélevée nord de Maître Kaito (pierre ocre + tatami bordé + escalier)."""
    step_y = y1 - 12
    # Plateau de l'estrade
    for y in range(y0, step_y):
        for x in range(x0, x1):
            dx = min(x - x0, x1 - 1 - x)
            dy = min(y - y0, step_y - 1 - y)
            if dx == 0 or y == y0:
                c = ST_OUT
            elif dx < 6 or dy < 5:
                # Bordure en bois laqué sombre & clous dorés
                if (dx == 3 and y % 16 == 8) or (dy == 2 and x % 16 == 8):
                    c = GD_HI
                else:
                    c = WD_HI if (dy == 1 or dx == 1) else WD_DK
            else:
                # Dalles d'ocre clair / tatami doré
                tx = (x - x0 - 6) % 24
                ty = (y - y0 - 5) % 16
                if tx == 0 or ty == 0:
                    c = ST_MD
                elif ty % 2 == 0:
                    c = ST_HI if (x + y) % 4 != 0 else ST_LT
                else:
                    c = ST_LT
            put(im, x, y, c)
    # Contremarche sculptée sur toute la largeur + marches centrales et latérales
    for y in range(step_y, y1):
        ry = y - step_y
        for x in range(x0, x1):
            if x == x0 or x == x1 - 1 or ry == 11:
                c = ST_OUT
            elif ry in (0, 5):
                c = ST_HI
            elif ry in (1, 2, 6, 7):
                c = ST_LT
            elif ry in (3, 8, 9):
                c = ST_MD
            else:
                c = ST_DK
            put(im, x, y, c)
    # Chemin de tapis impérial cramoisi & or au centre (x = 228..284) avec plis sur les marches
    rx0, rx1 = 228, 284
    for y in range(0, y1):
        in_step = y >= step_y
        sry = y - step_y
        for x in range(rx0, rx1):
            dx = min(x - rx0, rx1 - 1 - x)
            if dx == 0:
                c = CR_SH
            elif dx in (1, 2):
                if in_step and sry in (4, 10):
                    c = GD_DK
                elif in_step and sry in (0, 5):
                    c = GD_SP
                else:
                    c = GD_HI if (y % 4 != 0) else GD_MD
            elif dx == 3:
                c = CR_DK
            else:
                if in_step and sry in (0, 5):
                    c = CR_HI
                elif in_step and sry in (4, 10, 11):
                    c = CR_SH if sry == 11 else CR_DK
                else:
                    c = CR_MD if ((x // 2 + y // 2) % 3 != 0) else CR_LT
                if dx in (6, 7) and y % 8 in (2, 3, 4, 5) and not (in_step and sry in (4, 10, 11)):
                    c = GD_SP if (in_step and sry in (0, 5)) else GD_MD
            put(im, x, y, c)


def draw_sparring_arena(im: Image.Image, x0: int, y0: int, x1: int, y1: int) -> None:
    """Arène centrale d'entraînement en ardoise noire + blason doré Kingambit."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            dx = min(x - x0, x1 - 1 - x)
            dy = min(y - y0, y1 - 1 - y)
            d = min(dx, dy)
            if d == 0:
                c = ST_OUT
            elif d in (1, 2, 3):
                # Bordure extérieure en pierre ocre biseautée
                c = ST_HI if (x - x0 < 4 or y - y0 < 4) and d == 1 else (ST_LT if d == 2 else ST_MD)
            elif d == 4:
                c = ST_SH
            elif d in (5, 6, 7):
                # Liseré intérieur en laque cramoisie & or aux coins
                if dx < 14 and dy < 14:
                    c = GD_HI if d == 6 else GD_MD
                else:
                    c = CR_LT if d == 5 else (CR_MD if d == 6 else CR_DK)
            elif d == 8:
                c = SL_SH
            else:
                # Sol d'ardoise noire polie en dalles 16x16 biseautées sans rayures parasites
                tx = (x - x0) // 16
                ty = (y - y0) // 16
                gx = (x - x0) % 16
                gy = (y - y0) % 16
                tid = h2(tx, ty, 77) % 4
                if gx == 0 or gy == 0:
                    c = SL_SH
                elif (gx == 1 and gy < 14) or (gy == 1 and gx < 14):
                    c = SL_LT if tid in (0, 1) else SL_MD
                elif gx == 15 or gy == 15:
                    c = SL_DK if tid == 0 else SL_SH
                else:
                    c = SL_MD if tid in (0, 1) else SL_DK
                    # Micro-éclats minéraux discrets d'obsidienne
                    if h2(x, y, 131) % 47 == 0:
                        c = SL_LT if tid == 0 else SL_MD
            put(im, x, y, c)

    # Lignes de garde (shikiri-sen) gauche et droite en ivoire & or
    cy = (y0 + y1) // 2
    for sx in (x0 + 54, x1 - 56):
        fill_rect(im, sx, cy - 26, sx + 3, cy + 26, GD_MD)
        fill_rect(im, sx + 1, cy - 25, sx + 2, cy + 25, IV_HI)

    # Blason central doré de Scalpereur (cercle octogonal + kuwagata en V + lame centrale)
    cx = (x0 + x1) // 2  # 256
    for y in range(cy - 44, cy + 45):
        for x in range(cx - 44, cx + 45):
            rx = x - cx
            ry = y - cy
            dist = math.hypot(rx, ry)
            # Anneau double doré
            if 35.5 <= dist <= 38.5 or 30.5 <= dist <= 32.2:
                c = GD_HI if (rx + ry) < 0 else GD_MD
                put(im, x, y, c)
            elif 32.2 < dist < 35.5:
                put(im, x, y, CR_DK)

    # Lame centrale verticale dorée (fidèle à l'éperon doré du toit extérieur)
    for ry in range(-34, 28):
        half_w = 1 if ry < -26 else (2 if ry < -16 else (3 if ry < 18 else max(1, 3 - (ry - 17) // 3)))
        for rx in range(-half_w, half_w + 1):
            if rx == 0:
                c = GD_SP
            elif rx < 0:
                c = GD_HI
            else:
                c = GD_MD if abs(rx) < half_w else GD_DK
            put(im, cx + rx, cy + ry, c)

    # Croissant en V (kuwagata) + moustaches latérales stylisées
    for rx in range(-28, 29):
        arx = abs(rx)
        # Courbe du V doré kuwagata
        vy_center = int(14 - (arx * 0.85) + (arx * arx) * 0.008)
        if 3 <= arx <= 24:
            for dy in range(-2, 3):
                c = GD_SP if dy == -1 else (GD_HI if dy <= 0 else GD_MD)
                put(im, cx + rx, cy + vy_center + dy, c)
        # Moustache-lame horizontale incurvée
        by_center = int(17 - (arx * arx) * 0.015)
        if 5 <= arx <= 28:
            for dy in range(-1, 2):
                c = CR_HI if arx > 20 and dy <= 0 else (GD_MD if dy == -1 else CR_MD)
                put(im, cx + rx, cy + by_center + dy, c)

    # Gemme rivet centrale à la croisée des lames
    for ry in range(12, 19):
        for rx in range(-3, 4):
            if abs(rx) + abs(ry - 15) <= 4:
                put(im, cx + rx, cy + ry, GD_SP if rx <= 0 and ry <= 15 else GD_HI)


def draw_welcome_mat(im: Image.Image, x0: int, y0: int, x1: int, y1: int) -> None:
    """Tapis d'accueil rouge et blanc fidèle au seuil de KINGAMBIT DOJO.tile."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            dx = min(x - x0, x1 - 1 - x)
            dy = min(y - y0, y1 - 1 - y)
            d = min(dx, dy)
            if d == 0:
                c = INK
            elif 1 <= d <= 4:
                # Bordure rayée rouge et blanc caractéristique de l'extérieur !
                stripe = ((x - x0) // 3 if dy <= dx else (y - y0) // 3) % 2
                c = IV_HI if stripe == 0 else CR_LT
            elif d == 5:
                c = CR_SH
            elif d == 6:
                c = GD_MD
            else:
                c = CR_MD if (x + y) % 2 == 0 else CR_DK
                # Double motif d'écusson cramoisi clair (comme sur le tapis extérieur)
                for mcx in ((x0 + x1) // 2 - 14, (x0 + x1) // 2 + 14):
                    mcy = (y0 + y1) // 2 + 2
                    rx, ry = x - mcx, y - mcy
                    if abs(rx) <= 8 and -6 <= ry <= 7:
                        # Silhouette de couronne / kuwagata sur le tapis
                        if ry >= 2 or (abs(rx) >= 5 and ry >= -5) or (abs(rx) <= 2 and ry >= -6):
                            c = CR_LT if ry < 4 else CR_HI
            put(im, x, y, c)


def draw_banner(im: Image.Image, x0: int, y0: int) -> None:
    """Bannière murale rouge et or (24x44) fidèle aux deux bannières de KINGAMBIT DOJO.tile."""
    w, h = 24, 44
    # Tringle horizontale en bois sombre et embouts dorés
    fill_rect(im, x0 - 2, y0, x0 + w + 2, y0 + 3, WD_SH)
    fill_rect(im, x0 - 3, y0, x0 - 1, y0 + 3, GD_HI)
    fill_rect(im, x0 + w + 1, y0, x0 + w + 3, y0 + 3, GD_HI)
    for y in range(y0 + 3, y0 + h):
        ry = y - (y0 + 3)
        for x in range(x0, x0 + w):
            rx = x - x0
            # Découpe bas de bannière à franges dorées
            if ry >= h - 6:
                c = GD_HI if rx % 2 == 0 else GD_DK
                put(im, x, y, c)
                continue
            if rx == 0 or rx == w - 1:
                c = GD_MD
            elif rx == 1 or rx == w - 2 or ry in (0, h - 7):
                c = GD_HI if ry % 3 != 0 else GD_MD
            else:
                c = CR_LT if ry < 14 else (CR_MD if ry < 28 else CR_DK)
                # Motifs horizontaux & blason doré inspirés des bannières de la façade
                cx = w // 2
                dx = abs(rx - cx)
                if ry in (6, 7) and 4 <= rx <= w - 5:
                    c = GD_HI
                elif 11 <= ry <= 22:
                    # Kuwagata + lame dorée au coeur de la bannière
                    if dx <= 1 and 10 <= ry <= 22:
                        c = GD_SP
                    elif ry == 19 - dx // 2 and 2 <= dx <= 7:
                        c = GD_HI
                    elif ry == 20 - dx // 2 and 2 <= dx <= 7:
                        c = GD_MD
                elif ry in (26, 33) and 3 <= rx <= w - 4:
                    c = GD_HI
                elif 27 <= ry <= 32 and rx in (5, 9, 14, 18):
                    c = GD_MD
            put(im, x, y, c)


def draw_wall_lantern(im: Image.Image, cx: int, cy: int) -> None:
    """Lanterne japonaise murale (andon) en bois sombre et papier chaud."""
    fill_rect(im, cx - 5, cy - 8, cx + 5, cy + 8, WD_SH)
    fill_rect(im, cx - 6, cy - 8, cx + 6, cy - 6, WD_MD)
    fill_rect(im, cx - 6, cy + 6, cx + 6, cy + 8, WD_MD)
    for y in range(cy - 6, cy + 6):
        for x in range(cx - 4, cx + 4):
            if y == cy or x == cx:
                c = WD_DK
            else:
                d = abs(x - cx) + abs(y - cy)
                c = GD_SP if d <= 3 else (GD_HI if d <= 5 else IV_MD)
            put(im, x, y, c)


def draw_katana_rack(im: Image.Image, x0: int, y0: int) -> None:
    """Râtelier cérémoniel à katanas (katanakake) 36x24 en bois laqué, acier et garde d'or."""
    # Montants verticaux
    fill_rect(im, x0 + 6, y0 + 2, x0 + 10, y0 + 22, WD_SH)
    fill_rect(im, x0 + 7, y0 + 2, x0 + 9, y0 + 21, WD_MD)
    fill_rect(im, x0 + 26, y0 + 2, x0 + 30, y0 + 22, WD_SH)
    fill_rect(im, x0 + 27, y0 + 2, x0 + 29, y0 + 21, WD_MD)
    fill_rect(im, x0 + 3, y0 + 20, x0 + 33, y0 + 24, WD_DK)
    fill_rect(im, x0 + 4, y0 + 20, x0 + 32, y0 + 21, GD_MD)
    # Deux sabres horizontaux (fourreau cramoisi/noir + poignée tressée + tsuba d'or)
    for sy in (y0 + 6, y0 + 13):
        fill_rect(im, x0 + 1, sy, x0 + 35, sy + 3, INK)
        fill_rect(im, x0 + 2, sy + 1, x0 + 11, sy + 2, CR_HI if (sy % 2 == 0) else SL_HI)
        # Garde tsuba dorée
        fill_rect(im, x0 + 11, sy - 1, x0 + 13, sy + 4, GD_HI)
        # Fourreau laqué rouge sombre avec reflets
        fill_rect(im, x0 + 13, sy + 1, x0 + 34, sy + 2, CR_MD)
        put(im, x0 + 18, sy + 1, GD_HI)
        put(im, x0 + 33, sy + 1, GD_HI)


def draw_calligraphy_plaque(im: Image.Image, x0: int, y0: int) -> None:
    """Tablette de calligraphie en bois encadrée (écho direct à la plaque droite extérieure)."""
    w, h = 18, 34
    fill_rect(im, x0, y0, x0 + w, y0 + h, ST_OUT)
    fill_rect(im, x0 + 1, y0 + 1, x0 + w - 1, y0 + h - 1, WD_MD)
    fill_rect(im, x0 + 2, y0 + 2, x0 + w - 2, y0 + h - 2, ST_LT)
    fill_rect(im, x0 + 3, y0 + 3, x0 + w - 3, y0 + 5, GD_MD)
    # Idéogrammes pixel-art stylisés à l'encre noire
    glyph_rows = [
        (7, [6, 7, 8, 9, 10, 11]),
        (8, [8, 9]),
        (9, [5, 6, 7, 8, 9, 10, 11, 12]),
        (10, [6, 11]),
        (11, [6, 7, 8, 9, 10, 11]),
        (15, [5, 8, 9, 12]),
        (16, [6, 7, 8, 9, 10, 11]),
        (17, [8, 9]),
        (18, [5, 6, 8, 9, 11, 12]),
        (19, [7, 10]),
        (23, [6, 7, 8, 9, 10, 11]),
        (24, [8, 9]),
        (25, [5, 6, 7, 8, 9, 10, 11, 12]),
        (26, [7, 10]),
        (27, [6, 11]),
    ]
    for gy, xs in glyph_rows:
        for gx in xs:
            put(im, x0 + gx, y0 + gy, INK)
    # Sceau rouge vermillon en bas à droite
    fill_rect(im, x0 + 11, y0 + 28, x0 + 14, y0 + 31, CR_LT)


def draw_makiwara(im: Image.Image, cx: int, base_y: int) -> None:
    """Mannequin d'entraînement en paille tressée ceinturé de corde cramoisie."""
    # Socle bois
    fill_rect(im, cx - 9, base_y - 5, cx + 9, base_y, ST_OUT)
    fill_rect(im, cx - 8, base_y - 4, cx + 8, base_y - 1, WD_MD)
    # Poteau central
    fill_rect(im, cx - 3, base_y - 30, cx + 3, base_y - 4, WD_DK)
    # Manchon de paille tressée + bande de frappe cramoisie
    for y in range(base_y - 26, base_y - 7):
        for x in range(cx - 7, cx + 7):
            if x in (cx - 7, cx + 6) or y in (base_y - 26, base_y - 8):
                c = ST_OUT
            elif base_y - 20 <= y <= base_y - 14:
                c = CR_HI if x < cx - 2 else (CR_LT if x < cx + 2 else CR_DK)
                if y in (base_y - 20, base_y - 14):
                    c = GD_HI if x % 2 == 0 else GD_DK
            else:
                c = STW_HI if x < cx - 2 else (STW_MD if (x + y) % 2 == 0 else STW_DK)
            put(im, x, y, c)


def draw_zabuton(im: Image.Image, cx: int, cy: int) -> None:
    """Coussin de méditation samouraï (zabuton) 20x16 en soie cramoisie et glands dorés."""
    for y in range(cy - 8, cy + 8):
        for x in range(cx - 10, cx + 10):
            dx = abs(x - cx)
            dy = abs(y - cy)
            if dx >= 9 and dy >= 7:
                # Pompons d'or aux 4 coins
                put(im, x, y, GD_HI)
            elif dx == 9 or dy == 7:
                put(im, x, y, CR_SH)
            elif dx == 8 or dy == 6:
                put(im, x, y, GD_MD if (x + y) % 2 == 0 else CR_DK)
            else:
                c = CR_HI if (x < cx and y < cy and dx + dy < 9) else (CR_LT if dx + dy < 10 else CR_MD)
                if dx <= 2 and dy <= 1:
                    c = GD_HI
                put(im, x, y, c)


def draw_bench(im: Image.Image, x0: int, y0: int, w: int, h: int) -> None:
    """Banc bas en cyprès pour le repos entre les combats."""
    fill_rect(im, x0, y0, x0 + w, y0 + h, ST_OUT)
    for y in range(y0 + 1, y0 + h - 1):
        for x in range(x0 + 1, x0 + w - 1):
            if (x - x0) % 5 == 0:
                c = WD_DK
            elif y < y0 + 4:
                c = ST_HI
            else:
                c = ST_LT if (x + y) % 3 != 0 else ST_MD
            put(im, x, y, c)


def draw_armor_stand(im: Image.Image, cx: int, base_y: int) -> None:
    """Présentoir d'armure samouraï (kabuto cramoisi & cornes d'or Scalpereur)."""
    # Coffre-socle karabitsu noir & or
    fill_rect(im, cx - 11, base_y - 12, cx + 11, base_y, ST_OUT)
    fill_rect(im, cx - 10, base_y - 11, cx + 10, base_y - 1, SL_DK)
    fill_rect(im, cx - 10, base_y - 7, cx + 10, base_y - 5, GD_MD)
    # Plastron do cramoisi & noir
    for y in range(base_y - 24, base_y - 12):
        for x in range(cx - 8, cx + 8):
            if x in (cx - 8, cx + 7) or y == base_y - 24:
                c = INK
            elif (y - base_y) % 3 == 0:
                c = GD_MD
            else:
                c = CR_MD if x < cx else CR_DK
            put(im, x, y, c)
    # Casque kabuto cramoisi avec kuwagata doré
    for y in range(base_y - 34, base_y - 23):
        for x in range(cx - 8, cx + 8):
            dist = math.hypot(x - cx, (y - (base_y - 27)) * 1.2)
            if dist <= 7.2:
                put(im, x, y, INK if dist > 6.0 else (CR_HI if x < cx - 1 else CR_MD))
    # Cornes en V et lame frontale dorée
    for dy in range(-38, -26):
        put(im, cx, base_y + dy, GD_SP)
        put(im, cx - 1, base_y + dy + 1, GD_HI)
    for dx in range(2, 8):
        put(im, cx - dx, base_y - 27 - dx // 2, GD_HI)
        put(im, cx + dx, base_y - 27 - dx // 2, GD_MD)


def draw_brazier_stand(im: Image.Image, cx: int, cy: int) -> None:
    """Vasque de brasero en fer noir & cerclage d'or sur trépied (24x24)."""
    # Pieds en fer forgé
    for dx in (-7, 0, 7):
        fill_rect(im, cx + dx - 1, cy + 3, cx + dx + 2, cy + 10, INK)
        put(im, cx + dx, cy + 4, SL_LT)
    # Vasque octogonale
    for y in range(cy - 6, cy + 5):
        ry = y - cy
        hw = 10 if ry <= -1 else max(5, 10 - (ry + 1) * 2)
        for x in range(cx - hw, cx + hw + 1):
            rx = x - cx
            if abs(rx) == hw or ry in (-6, 4):
                c = INK
            elif ry in (-4, -3):
                c = GD_HI if rx < 0 else GD_MD
            elif ry < -4:
                # Braises ardentes
                c = CR_HI if (rx + ry) % 2 == 0 else GD_MD
            else:
                c = SL_HI if rx < -3 else (SL_MD if rx < 4 else SL_DK)
            put(im, x, y, c)


def draw_brazier_flame(im: Image.Image, cx: int, cy: int, phase: int) -> None:
    """Flamme pixel-art animée sur 4 phases au-dessus du brasero (cx, cy)."""
    sway = [0, 1, 0, -1][phase % 4]
    stretch = [0, 2, 1, -1][phase % 4]
    top_y = cy - 18 - stretch
    for y in range(top_y, cy - 3):
        t = (y - top_y) / max(1, (cy - 3 - top_y))  # 0 en haut -> 1 à la base
        shift = sway if t < 0.55 else 0
        hw = max(1, int(math.sin(min(1.0, t * 1.15) * math.pi * 0.85) * 7.2))
        for rx in range(-hw, hw + 1):
            x = cx + shift + rx
            ar = abs(rx) / max(1.0, hw)
            # Découpe crénelée vivante sur les langues de feu
            if t < 0.35 and abs(rx) == hw and (y + phase) % 2 == 0:
                continue
            if ar < 0.35 and t > 0.35:
                c = (255, 252, 210, 255)
            elif ar < 0.62 and t > 0.2:
                c = GD_SP
            elif ar < 0.85:
                c = (252, 152, 44, 255)
            else:
                c = (214, 68, 36, 235)
            put(im, x, y, c)
    # Étincelles montantes décalées selon la phase
    sparks = [
        (cx - 3, top_y - 2),
        (cx + 2, top_y - 4),
        (cx - 1, top_y - 5),
        (cx + 3, top_y - 2),
    ]
    sx, sy = sparks[phase % 4]
    put(im, sx, sy, GD_SP)
    put(im, sx, sy + 1, (252, 152, 44, 220))


def draw_kabuto_torii_over(im: Image.Image, cx: int, y_base: int) -> None:
    """Arche supérieure monumentale (DrawLayer.Top) au-dessus du passage nord :
    poutre acajou, moustaches-lames obsidienne/cramoisi et kuwagata doré Kingambit !
    Les personnages marchant vers MarowakDojoDungeonEntrance passent SOUS ce linteau.
    """
    # Poutre transversale kasagi/nuki (x = cx - 72 .. cx + 72, y = y_base - 14 .. y_base)
    for y in range(y_base - 12, y_base + 2):
        for x in range(cx - 68, cx + 68):
            if y in (y_base - 12, y_base + 1) or x in (cx - 68, cx + 67):
                c = INK
            elif y in (y_base - 11, y_base - 10):
                c = CR_LT
            elif y == y_base - 9:
                c = GD_HI
            else:
                c = WD_HI if y < y_base - 5 else WD_DK
            put(im, x, y, c)

    # Dôme central kabuto cramoisi au-dessus du linteau
    for y in range(y_base - 30, y_base - 6):
        for x in range(cx - 24, cx + 25):
            dist = math.hypot((x - cx) * 0.9, (y - (y_base - 10)) * 1.05)
            if dist <= 20.5:
                if dist > 18.8:
                    c = INK
                elif dist > 16.5:
                    c = SL_DK
                else:
                    c = CR_HI if (x < cx - 3 and y < y_base - 16) else (CR_MD if x < cx + 5 else CR_DK)
                put(im, x, y, c)

    # Grandes moustaches-lames incurvées (noir obsidienne -> pointes cramoisies, comme la façade !)
    for rx in range(-78, 79):
        arx = abs(rx)
        t = arx / 78.0
        curve_y = int((y_base - 6) - (t * t) * 22.0)
        thick = max(2, int(6.5 * (1.0 - t * 0.68)))
        for dy in range(-thick, thick + 1):
            y = curve_y + dy
            if abs(dy) == thick:
                c = INK
            elif t > 0.68:
                # Pointes ardentes cramoisies comme sur KINGAMBIT DOJO.tile !
                c = CR_HI if dy < 0 else CR_MD
            elif dy == -thick + 1:
                c = SL_HI
            elif dy < 0:
                c = SL_MD
            elif dy == thick - 1:
                c = CR_MD
            else:
                c = SL_DK
            put(im, cx + rx, y, c)

    # Croissant en V doré (kuwagata) + grande lame centrale dorée
    for ry in range(-52, -4):
        hw = 1 if ry < -44 else (2 if ry < -32 else 3)
        for rx in range(-hw, hw + 1):
            c = GD_SP if rx == 0 else (GD_HI if rx < 0 else (GD_MD if rx < hw else INK))
            put(im, cx + rx, y_base + ry, c)
    for rx in range(-20, 21):
        arx = abs(rx)
        if 3 <= arx <= 19:
            vy = int((y_base - 7) - arx * 0.72)
            for dy in range(-2, 3):
                c = INK if abs(dy) == 2 else (GD_SP if dy == -1 else (GD_HI if dy == 0 else GD_MD))
                put(im, cx + rx, vy + dy, c)


def add_glow_circle(im: Image.Image, cx: int, cy: int, radius: int, rgb: tuple[int, int, int], max_alpha: int) -> None:
    """Halo de lumière chaude quantifié en paliers pixel-art propres (sans bruit mou)."""
    r, g, b = rgb
    for y in range(max(0, cy - radius), min(im.height, cy + radius + 1)):
        for x in range(max(0, cx - radius), min(im.width, cx + radius + 1)):
            d = math.hypot(x - cx, y - cy) / radius
            if d >= 1.0:
                continue
            # Quantification en 4 couronnes franches style GBA/DS
            band = int((1.0 - d) * 4.99) / 4.0
            a = int(max_alpha * band * band)
            if a <= 0:
                continue
            pr, pg, pb, pa = im.getpixel((x, y))
            if pa == 0:
                im.putpixel((x, y), (r, g, b, a))
            else:
                na = min(255, pa + a)
                im.putpixel((x, y), ((pr * pa + r * a) // na, (pg * pa + g * a) // na, (pb * pa + b * a) // na, na))


def build() -> int:
    # Conserver les métadonnées et entités sérialisées exactes du fichier original
    orig_doc = json.loads(GROUND_PATH.read_text(encoding="utf-8-sig"))
    orig_obj = orig_doc["Object"]

    # 9 calques de rendu :
    # L0..L5 statiques sous personnages (Layer=0)
    # L6 animé 4 phases sous personnages (Layer=0)
    # L7..L8 statiques avant-plan au-dessus des personnages (Layer=4 = DrawLayer.Top)
    L0_sol = Image.new("RGBA", (MAP_W, MAP_H), VOID)
    L1_arene = Image.new("RGBA", (MAP_W, MAP_H), (0, 0, 0, 0))
    L2_ombres = Image.new("RGBA", (MAP_W, MAP_H), (0, 0, 0, 0))
    L3_murs = Image.new("RGBA", (MAP_W, MAP_H), (0, 0, 0, 0))
    L4_mobilier = Image.new("RGBA", (MAP_W, MAP_H), (0, 0, 0, 0))
    L5_bannieres = Image.new("RGBA", (MAP_W, MAP_H), (0, 0, 0, 0))
    L6_flammes = [Image.new("RGBA", (MAP_W, MAP_H), (0, 0, 0, 0)) for _ in range(4)]
    L7_linteau_top = Image.new("RGBA", (MAP_W, MAP_H), (0, 0, 0, 0))
    L8_cadre_top = Image.new("RGBA", (MAP_W, MAP_H), (0, 0, 0, 0))

    # --- L0 : Sol principal en cyprès, couloir nord en ardoise et seuil sud ---
    draw_wood_floor(L0_sol, 80, 136, 432, 432)
    draw_slate_passage(L0_sol, 208, 0, 304, 144)
    draw_wood_floor(L0_sol, 200, 416, 312, 512)

    # --- L1 : Estrade nord, arène d'ardoise noire + blason doré, tapis rouge/blanc sud ---
    draw_dais(L1_arene, 176, 140, 336, 212)
    draw_sparring_arena(L1_arene, 144, 224, 368, 376)
    draw_welcome_mat(L1_arene, 216, 452, 296, 502)

    # --- L3 : Murs en pierre ocre taillée & piliers acajou ---
    # Couronnement épais nord-ouest & nord-est
    draw_stone_wall_top(L3_murs, 56, 48, 216, 84)
    draw_stone_wall_top(L3_murs, 296, 48, 456, 84)
    # Parois du couloir nord (vers l'entrée d'entraînement)
    draw_stone_wall_top(L3_murs, 184, 0, 216, 84)
    draw_stone_wall_top(L3_murs, 296, 0, 328, 84)
    # Façade intérieure du mur nord (y = 80..144)
    draw_stone_wall_face(L3_murs, 88, 80, 216, 144)
    draw_stone_wall_face(L3_murs, 296, 80, 424, 144)

    # Murs latéraux ouest et est (couronnements épais)
    draw_stone_wall_top(L3_murs, 56, 80, 88, 432)
    draw_stone_wall_top(L3_murs, 424, 80, 456, 432)

    # Murs sud-ouest et sud-est encadrant le vestibule d'entrée (x = 208..304)
    draw_stone_wall_top(L3_murs, 56, 416, 208, 464)
    draw_stone_wall_top(L3_murs, 304, 416, 456, 464)
    # Bajoyers du vestibule sud (y = 448..512)
    draw_stone_wall_top(L3_murs, 176, 448, 208, 512)
    draw_stone_wall_top(L3_murs, 304, 448, 336, 512)

    # Grands piliers samouraï en acajou & or scandant le mur nord et les portiques
    for px in (88, 148, 204, 296, 352, 412):
        draw_pillar(L3_murs, px, 76, 12, 68)
    # Piliers latéraux encadrant la salle
    for py in (188, 284, 380):
        draw_pillar(L3_murs, 80, py, 10, 36)
        draw_pillar(L3_murs, 422, py, 10, 36)
    # Piliers d'entrée sud
    draw_pillar(L3_murs, 198, 412, 12, 44)
    draw_pillar(L3_murs, 302, 412, 12, 44)

    # --- L4 : Mobilier d'entraînement, armes, armure, makiwara, zabuton & vasques braseros ---
    draw_katana_rack(L4_mobilier, 106, 118)
    draw_armor_stand(L4_mobilier, 384, 146)
    draw_makiwara(L4_mobilier, 108, 248)
    draw_makiwara(L4_mobilier, 108, 336)
    draw_zabuton(L4_mobilier, 398, 240)
    draw_zabuton(L4_mobilier, 398, 284)
    draw_bench(L4_mobilier, 390, 324, 20, 40)

    braziers = [(164, 176), (348, 176), (184, 400), (328, 400)]
    for bx, by in braziers:
        draw_brazier_stand(L4_mobilier, bx, by)

    # --- L5 : Bannières cramoisies & or Kingambit, tablette kanji & lanternes andon ---
    draw_banner(L5_bannieres, 172, 86)
    draw_banner(L5_bannieres, 316, 86)
    draw_calligraphy_plaque(L5_bannieres, 360, 88)
    draw_calligraphy_plaque(L5_bannieres, 122, 84)
    lanterns = [(96, 104), (416, 104), (85, 202), (427, 202), (85, 298), (427, 298)]
    for lx, ly in lanterns:
        draw_wall_lantern(L5_bannieres, lx, ly)

    # --- L6 : Flammes animées 4 phases sur les 4 braseros kagaribi ---
    for ph in range(4):
        for bx, by in braziers:
            draw_brazier_flame(L6_flammes[ph], bx, by, (ph + (1 if bx > 256 else 0)) % 4)

    # --- L2 : Ombres portées murales + halos dorés des braseros/lanternes + lumière seuil sud ---
    sh_draw = ImageDraw.Draw(L2_ombres, "RGBA")
    # Ombre douce au pied du mur nord, des murs latéraux et de l'estrade
    sh_draw.rectangle([88, 144, 176, 154], fill=(20, 10, 12, 72))
    sh_draw.rectangle([336, 144, 424, 154], fill=(20, 10, 12, 72))
    sh_draw.rectangle([88, 144, 96, 416], fill=(20, 10, 12, 60))
    sh_draw.rectangle([416, 144, 424, 416], fill=(20, 10, 12, 44))
    sh_draw.rectangle([176, 212, 336, 218], fill=(20, 10, 12, 68))
    # Halos chauds ambrés autour des 4 braseros, des lanternes et du seuil sud ensoleillé
    for bx, by in braziers:
        add_glow_circle(L2_ombres, bx, by - 4, 44, (255, 188, 76), 54)
    for lx, ly in lanterns:
        add_glow_circle(L2_ombres, lx, ly + 8, 28, (255, 204, 108), 38)
    add_glow_circle(L2_ombres, 256, 504, 56, (255, 232, 168), 64)

    # --- L7 (DrawLayer.Top = 4) : Arche supérieure Kabuto-Torii au-dessus du passage nord ---
    draw_kabuto_torii_over(L7_linteau_top, 256, 86)

    # --- L8 (DrawLayer.Top = 4) : Poutres d'avant-plan au-dessus du seuil sud ---
    for y in range(444, 454):
        for x in range(184, 212):
            put(L8_cadre_top, x, y, INK if y in (444, 453) else (GD_MD if y == 448 else WD_DK))
        for x in range(300, 328):
            put(L8_cadre_top, x, y, INK if y in (444, 453) else (GD_MD if y == 448 else WD_DK))

    # --- Construction de la banque Kingambit_Dojo_Interieur.tile dédupliquée ---
    unique_tiles: dict[bytes, tuple[int, int, bytes]] = {}
    ordered_entries: list[tuple[int, int, bytes]] = []
    COLS_SHEET = 32

    def register_tile(crop: Image.Image) -> tuple[int, int] | None:
        raw_rgba = crop.tobytes()
        # Ignorer les tuiles 100 % transparentes
        if all(raw_rgba[i] == 0 for i in range(3, len(raw_rgba), 4)):
            return None
        hit = unique_tiles.get(raw_rgba)
        if hit is not None:
            return hit[0], hit[1]
        idx = len(ordered_entries)
        tx, ty = idx % COLS_SHEET, idx // COLS_SHEET
        buf = io.BytesIO()
        crop.save(buf, format="PNG", optimize=False)
        png_bytes = buf.getvalue()
        entry = (tx, ty, png_bytes)
        unique_tiles[raw_rgba] = entry
        ordered_entries.append(entry)
        return tx, ty

    layer_defs = [
        ("01_sol_plancher", 0, [L0_sol], 60),
        ("02_arene_tapis", 0, [L1_arene], 60),
        ("03_ombres_lueurs", 0, [L2_ombres], 60),
        ("04_murs_pierre_ocre", 0, [L3_murs], 60),
        ("05_mobilier_entrainement", 0, [L4_mobilier], 60),
        ("06_bannieres_armoiries", 0, [L5_bannieres], 60),
        ("07_braseros_animes", 0, L6_flammes, 8),
        ("08_arche_kabuto_top", 4, [L7_linteau_top], 60),
        ("09_charpente_sud_top", 4, [L8_cadre_top], 60),
    ]

    rs_layers = []
    total_frame_refs = 0
    for lname, draw_layer, frames_imgs, frame_len in layer_defs:
        cols = []
        for gx in range(GW):
            col = []
            for gy in range(GH):
                box = (gx * TS, gy * TS, (gx + 1) * TS, (gy + 1) * TS)
                locs = [register_tile(im.crop(box)) for im in frames_imgs]
                if any(loc is not None for loc in locs):
                    # Pour un calque animé où une frame serait vide sur le bord, poser une tuile transparente dédiée si besoin
                    if any(loc is None for loc in locs):
                        empty_key = b"\x00" * (TS * TS * 4)
                        if empty_key not in unique_tiles:
                            idx = len(ordered_entries)
                            tx, ty = idx % COLS_SHEET, idx // COLS_SHEET
                            buf = io.BytesIO()
                            Image.new("RGBA", (TS, TS), (0, 0, 0, 0)).save(buf, format="PNG")
                            ent = (tx, ty, buf.getvalue())
                            unique_tiles[empty_key] = ent
                            ordered_entries.append(ent)
                        etx, ety, _ = unique_tiles[empty_key]
                        locs = [(etx, ety) if l is None else l for l in locs]
                    frames_json = [
                        {"Sheet": SHEET_NAME, "TexLoc": {"X": lx, "Y": ly}}
                        for (lx, ly) in locs  # type: ignore[misc]
                    ]
                    total_frame_refs += len(frames_json)
                    col.append({
                        "AutoTileset": "",
                        "Associates": [],
                        "Layers": [{"FrameLength": frame_len, "Frames": frames_json}],
                        "NeighborCode": -1,
                    })
                else:
                    col.append({
                        "AutoTileset": "",
                        "Associates": [],
                        "Layers": [],
                        "NeighborCode": -1,
                    })
            cols.append(col)
        rs_layers.append({
            "Name": lname,
            "Layer": draw_layer,
            "Visible": True,
            "Tiles": cols,
        })

    # Écriture binaire de Kingambit_Dojo_Interieur.tile (<ii header + table <iiq + blocs <q + PNG)
    cnt = len(ordered_entries)
    header_size = 8 + 16 * cnt
    blobs = bytearray()
    table = bytearray()
    cur_ptr = header_size
    for tx, ty, png_bytes in ordered_entries:
        table += struct.pack("<iiq", tx, ty, cur_ptr)
        blobs += struct.pack("<q", len(png_bytes)) + png_bytes
        cur_ptr += 8 + len(png_bytes)
    TILE_OUT.write_bytes(struct.pack("<ii", TS, cnt) + bytes(table) + bytes(blobs))

    # --- Grille de collisions (64x64 de 8x8 px) propre et testée ---
    def is_walkable_cell(gx: int, gy: int) -> bool:
        x0, y0 = gx * TS, gy * TS
        cx, cy = x0 + 4, y0 + 4
        # 1. Couloir nord d'entraînement (MarowakDojoDungeonEntrance 224..288, y=0..144)
        if 216 <= x0 and x0 + 8 <= 296 and 0 <= y0 < 144:
            return True
        # 2. Vestibule sud & seuil de sortie (MarowakDojoExitMarker 248,440 + TEAMMATES + Exit 224,496)
        if 208 <= x0 and x0 + 8 <= 304 and 416 <= y0 < 504:
            return True
        # 3. Grande salle principale (x = 88..424, y = 144..416)
        if not (88 <= x0 and x0 + 8 <= 424 and 144 <= y0 < 416):
            return False
        # Obstacles intérieurs (mobilier solide) :
        # - Râtelier katanas nord-ouest
        if 104 <= cx < 148 and 144 <= cy < 152:
            return False
        # - Présentoir d'armure nord-est
        if 368 <= cx < 400 and 144 <= cy < 152:
            return False
        # - 2 mannequins makiwara à gauche
        if 96 <= cx < 120 and (236 <= cy < 252 or 324 <= cy < 340):
            return False
        # - Banc de repos à droite (les coussins zabuton 240/284 restent marchables !)
        if 388 <= cx < 412 and 324 <= cy < 364:
            return False
        # - Rebords latéraux surélevés de l'estrade nord (on monte par l'escalier avant y=200..212)
        if (176 <= cx < 184 or 328 <= cx < 336) and 144 <= cy < 200:
            return False
        # - 4 vasques de braseros samouraï
        for bx, by in braziers:
            if (bx - 12) <= cx < (bx + 12) and (by - 8) <= cy < (by + 12):
                return False
        return True

    obstacles = []
    for gx in range(GW):
        col = []
        for gy in range(GH):
            tags = 0 if is_walkable_cell(gx, gy) else 1
            col.append({
                "Bounds": {"X": gx * TS, "Y": gy * TS, "Width": TS, "Height": TS},
                "Tags": tags,
            })
        obstacles.append(col)

    orig_obj["Comment"] = "Dojo Kingambit : intérieur samouraï pierre ocre, bois sombre et cramoisi/or raccordé à Réverie Town."
    orig_obj["TexSize"] = 1
    orig_obj["EdgeView"] = 1
    orig_obj["Layers"] = rs_layers
    orig_obj["obstacles"] = obstacles

    raw_bytes = GROUND_PATH.read_bytes()
    has_bom = raw_bytes.startswith(b"\xef\xbb\xbf")
    out_json = json.dumps(orig_doc, ensure_ascii=False, separators=(",", ":"))
    GROUND_PATH.write_bytes((b"\xef\xbb\xbf" if has_bom else b"") + out_json.encode("utf-8"))

    print(f"Kingambit_Dojo_Interieur.tile : {cnt} tuiles uniques ({TILE_OUT.stat().st_size} octets)")
    print(f"dojo_kingambit.rsground : 9 calques, {total_frame_refs} références de frames")
    return total_frame_refs


if __name__ == "__main__":
    build()
