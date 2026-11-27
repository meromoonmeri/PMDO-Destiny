#!/usr/bin/env python3
"""Corrige le format de la sphère : projectile PMDO = banque .dir, pas .beam."""
from pathlib import Path
from PIL import Image
import io,json,struct
P=Path.home()/'Capacites-Z/Prototypes/Symphonie-des-Ondines/Generation-PMDO'
b=(P/'OndinesV2_Sphere.beam').read_bytes();n=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+n])).convert('RGBA');off=8+n;count=struct.unpack_from('<i',b,off)[0];off+=4;rects=[struct.unpack_from('<iiii',b,off+16*j) for j in range(count)];frames=struct.unpack_from('<i',b,off+16*count)[0];assert count==frames*3
w,h=rects[0][2:];sheet=Image.new('RGBA',(w*frames,h*8))
for i,(x,y,rw,rh) in enumerate(rects[:frames]):
 assert (rw,rh)==(w,h);f=im.crop((x,y,x+w,y+h))
 for d in range(8):sheet.alpha_composite(f,(w*i,h*d))
o=io.BytesIO();sheet.save(o,format='PNG');png=o.getvalue();(P/'OndinesV3_Sphere.dir').write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',w,h,4,frames))
z=json.loads((P/'oceanic_operetta-v2-test-only.json').read_text());z['Object']['HitboxAction']['Anim']['AnimIndex']='OndinesV3_Sphere';(P/'oceanic_operetta-v3-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Banque .dir créée :',w,h,frames,'images, huit orientations.')
