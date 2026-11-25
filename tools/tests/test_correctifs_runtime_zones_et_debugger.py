#!/usr/bin/env python3
"""Tests de non-régression des 3 erreurs runtime du journal PMDO 0.8.12.0 :
  1. game/Data/Script/debugger.lua : absence de 'socket.core' en mode DebugLua=true sans exception LuaScriptException.
  2. game/Data/Zone/grotte_verdoyante.json : tous les $type résolvent vers le bon assembly C# (RogueEssence vs RogueElements).
  3. game/Data/Zone/passage_aquatique.json : GenSteps (liste) + ZoneSteps + tous les $type résolvent à 100% contre engine/.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / "game"


def test_debugger_without_socket_core() -> None:
    lua = LuaRuntime(unpack_returned_tuples=True)
    dbg_src = (GAME / "Data/Script/debugger.lua").read_text(encoding="utf-8")
    lua.execute(
        """
        RogueEssence = { DiagManager = { Instance = { DevMode = true, DebugLua = true } } }
        package.preload['socket.core'] = nil
        package.cpath = ''
        """
    )
    lua.execute(dbg_src)
    assert lua.eval("DEBUG ~= nil and type(DEBUG.EnableDbgCoro) == 'function'")
    assert lua.eval("___mobdebug == nil")
    print("[PASS] debugger.lua : aucune erreur lorsque DebugLua=true et socket.core est absent.")


def test_all_zones_against_csharp_engine() -> None:
    ns_re = re.compile(r"^\s*namespace\s+([A-Za-z0-9_.]+)", re.M)
    cls_re = re.compile(
        r"\b(?:public|internal)\s+(?:abstract\s+|sealed\s+|partial\s+|static\s+)*(?:class|struct|interface|enum)\s+([A-Za-z0-9_]+)(?:<([^>{;]+)>)?",
        re.M,
    )
    cs_types: dict[str, set[str]] = {}
    for cs in (ROOT / "engine").rglob("*.cs"):
        rel = cs.relative_to(ROOT / "engine").parts
        if rel[0] == "PMDC":
            asm = "PMDC"
        elif len(rel) >= 2 and rel[0] == "RogueEssence" and rel[1] in {"RogueElements", "RogueEssence"}:
            asm = rel[1]
        else:
            continue
        txt = cs.read_text(encoding="utf-8", errors="ignore")
        m_ns = ns_re.search(txt)
        if not m_ns:
            continue
        ns = m_ns.group(1)
        for m_c in cls_re.finditer(txt):
            cname, tparams = m_c.group(1), m_c.group(2)
            full = f"{ns}.{cname}`{len([p for p in tparams.split(',') if p.strip()])}" if tparams else f"{ns}.{cname}"
            cs_types.setdefault(full, set()).add(asm)

    def split_comma(s: str) -> tuple[str, str]:
        d = 0
        for i in range(len(s) - 1, -1, -1):
            if s[i] == "]":
                d += 1
            elif s[i] == "[":
                d -= 1
            elif s[i] == "," and d == 0:
                return s[:i].strip(), s[i + 1 :].strip()
        raise AssertionError(f"$type malformé : {s}")

    def check_expr(expr: str, zf_name: str) -> None:
        tpart, asm = split_comma(expr)
        if "[[" in tpart:
            base_name, rest = tpart.split("[[", 1)
            assert rest.endswith("]]")
            inner = rest[:-2]
            d, start, i = 0, 0, 0
            args = []
            while i < len(inner):
                if d == 0 and inner[i : i + 3] == "],[":
                    args.append(inner[start:i])
                    start = i + 3
                    i += 3
                    continue
                if inner[i] == "[":
                    d += 1
                elif inner[i] == "]":
                    d -= 1
                i += 1
            args.append(inner[start:])
            for a in args:
                check_expr(a, zf_name)
        else:
            base_name = tpart
        if asm in {"System.Private.CoreLib", "mscorlib", "System"}:
            return
        assert base_name in cs_types, f"{zf_name}: classe C# introuvable {base_name}"
        assert asm in cs_types[base_name], f"{zf_name}: assembly invalide '{asm}' pour {base_name} (attendu {cs_types[base_name]})"

    checked = 0
    for zf in sorted((GAME / "Data/Zone").glob("*.json")):
        doc = json.loads(zf.read_text(encoding="utf-8-sig"))
        stack = [doc]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                if "$type" in cur:
                    check_expr(cur["$type"], zf.name)
                    checked += 1
                stack.extend(cur.values())
            elif isinstance(cur, list):
                stack.extend(cur)

    # Specific structural checks on passage_aquatique.json & grotte_verdoyante.json
    pa = json.loads((GAME / "Data/Zone/passage_aquatique.json").read_text(encoding="utf-8-sig"))["Object"]
    assert len(pa["Segments"][0]["Floors"]) == 10
    for fl in pa["Segments"][0]["Floors"]:
        assert isinstance(fl["GenSteps"], list), "GenSteps de GridFloorGen doit être une liste JSON"

    gv = json.loads((GAME / "Data/Zone/grotte_verdoyante.json").read_text(encoding="utf-8-sig"))["Object"]
    assert sum(len(s.get("Floors", [])) for s in gv["Segments"]) == 9
    print(f"[PASS] {checked} expressions $type validées sur l'ensemble des fichiers Zone/*.json (grotte_verdoyante + passage_aquatique inclus).")


if __name__ == "__main__":
    test_debugger_without_socket_core()
    test_all_zones_against_csharp_engine()
