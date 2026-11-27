#!/usr/bin/env python3
"""Retire le rectangle étiré du rayon V2 sans modifier sa charge ou son impact."""
from pathlib import Path
from PIL import Image
import io,struct,json,shutil
P=Path(__file__).resolve().parent;V=P.parent/'V2'
b=(V/'CanonBlindeV2_Rayon.beam').read_bytes();n=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+n])).convert('RGBA');off=8+n;count=struct.unpack_from('<i',b,off)[0];rects=[struct.unpack_from('<iiii',b,off+4+i*16) for i in range(count)];N=struct.unpack_from('<i',b,off+4+16*count)[0];assert count==3*N
for x,y,w,h in rects[N:2*N]:
 assert h==1
 im.paste((0,0,0,0),(x,y,x+w,y+h))
assert all(im.crop((x,y,x+w,y+h)).getbbox() is None for x,y,w,h in rects[N:2*N])
s=io.BytesIO();im.save(s,format='PNG',optimize=True);raw=s.getvalue();(P/'CanonBlindeV2C_Rayon.beam').write_bytes(struct.pack('<q',len(raw))+raw+b[off:]);im.save(P/'CanonBlindeV2C_Rayon-planche.png')
for name in ['CanonBlindeV2_Charge.dir','CanonBlindeV2_DestructionFeu.dir','canon-blinde-effet.lua','test-canon-blinde.lua']:shutil.copy2(V/name,P/name)
z=json.loads((V/'armor_cannon-v2-test-only.json').read_text());z['Object']['HitboxAction']['Anim']['AnimIndex']='CanonBlindeV2C_Rayon';(P/'armor_cannon-v2-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2))
s=(V/'banc-v2.py').read_text().replace("P=H/'Capacites-de-base/Canon-Blinde/V2'", "P=H/'Capacites-de-base/Canon-Blinde/V2-corrige'").replace('backup-canon-blinde-v2','backup-canon-blinde-v2-corrige').replace('CanonBlindeV2_Rayon.beam','CanonBlindeV2C_Rayon.beam');(P/'banc-correction.py').write_text(s)
print('Corps rectangulaire rendu entièrement transparent ; tête, queue et flammes natives conservées.')
