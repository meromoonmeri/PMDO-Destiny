#!/usr/bin/env python3
"""Relais vers le correctif cumulatif, pour éviter de publier la scène sans ses autres corrections."""
import runpy
from pathlib import Path
p=Path('/home/user/chantier-accueil-luxray/pousser-cumulatif.py')
if not p.exists(): raise SystemExit('Script cumulatif manquant ; aucune publication.')
runpy.run_path(str(p),run_name='__main__')
