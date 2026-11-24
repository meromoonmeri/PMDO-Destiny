#!/usr/bin/env python3
"""Filme la variante dans un clone PMDO, jamais dans le worktree validé.
Dépend du banc du lot précédent (même dossier parent). Sous xvfb-run.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sys

SOURCES=Path(__file__).resolve().parent
sys.path.insert(0,str(SOURCES.parents[1]/'Kingambit-Prebatailles/Sources'))
from texturer_wooshes_pmd import NAME
import filmer_prebatailles_pmdo as qa


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--banques',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--type',nargs='+')
    a=ap.parse_args();assert os.getenv('DISPLAY'),'lancer sous xvfb-run'
    a.out.mkdir(parents=True,exist_ok=True)
    qa.QA=a.banques
    rep={r['id']:r for r in json.loads((a.banques/'Index-Illustrations.json').read_text())}
    rs=qa.rows()
    if a.type:rs=[next(x for x in rs if x['id']==k) for k in a.type]
    c,p=qa.prepare(a.out,rs)
    for r in rs:
        k=r['id']; path=c/'Content/BG'/(NAME+k+'.dir')
        assert sha256(path.read_bytes()).hexdigest()==rep[k]['sha256'],k
    shutil.copyfile(SOURCES/'dojo_kingambit_prebatailles.lua',c/'Data/Script/origin/dojo_kingambit_prebatailles.lua')
    qa.capture(a.out,c,p,rs,True)
    full=qa.tail(p)
    assert not any(q in full for q in ('[ERROR]', 'LuaScriptException', 'System.Exception','[WARN]')),full[-3500:]


if __name__=='__main__':main()
