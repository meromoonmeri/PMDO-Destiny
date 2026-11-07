#!/usr/bin/env python3
"""Exécute un contrôle et publie son erreur comme annotation CI lisible."""
import subprocess,sys
result=subprocess.run([sys.executable,*sys.argv[1:]],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
print(result.stdout,end='',flush=True)
if result.stderr:print(result.stderr,end='',file=sys.stderr,flush=True)
if result.returncode:
 message=(result.stderr or result.stdout or f'Exit {result.returncode}')[-7000:]
 message=message.replace('%','%25').replace('\r','%0D').replace('\n','%0A')
 print('::error title=Échec du contrôle::'+message,flush=True)
raise SystemExit(result.returncode)
