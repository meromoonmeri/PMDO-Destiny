#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exécute les suites Lua de tools/tests/ via lupa (Lua 5.4).

Usage : python3 tools/tests/run_lua_tests.py [fichier.lua ...]
Sans argument : tous les tools/tests/*.lua.
Chaque test est lancé depuis la racine du dépôt dans un runtime isolé.
"""
import pathlib
import sys

from lupa import lua54

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def run(path: pathlib.Path) -> None:
    code = path.read_text(encoding='utf-8')
    rt = lua54.LuaRuntime(unpack_returned_tuples=True)
    loader = rt.eval('function(code, name) local f, e = load(code, name) return f, e end')
    fn, err = loader(code, path.name)
    if fn is None:
        raise RuntimeError(f'{path.name} : erreur de syntaxe : {err}')
    fn()


def main() -> None:
    tests = [pathlib.Path(a) for a in sys.argv[1:]] or sorted((ROOT / 'tools' / 'tests').glob('*.lua'))
    echec = False
    for test in tests:
        try:
            run(test)
            print(f'PASS {test.name}')
        except Exception as exc:
            print(f'FAIL {test.name} : {exc}')
            echec = True
    sys.exit(1 if echec else 0)


if __name__ == '__main__':
    main()
