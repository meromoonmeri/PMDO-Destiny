from pathlib import Path
from PIL import Image
import io, struct
R=Path(__file__).resolve().parents[2]
for name in ("PMU_Table_bois_01", "PMU_Lampe_sur_pied_01"):
 b=(R/"game/Content/Object"/(name+".dir")).read_bytes()
 n=struct.unpack_from("<q",b)[0]; assert len(b)==8+n+16
 im=Image.open(io.BytesIO(b[8:8+n])).convert("RGBA")
 w,h,d,f=struct.unpack("<iiii",b[8+n:]);assert d==0 and f==1 and im.size==(w,h)
 raw=Image.open(R/"art/reverie/objets_pmu"/(name+".1.png")).convert("RGBA");assert raw.size==im.size
 expected=bytes(v for r,g,b,a in raw.getdata() for v in (r*a//255,g*a//255,b*a//255,a))
 assert im.tobytes()==expected
print("PASS deux objets PMU statiques : format et pixels")
