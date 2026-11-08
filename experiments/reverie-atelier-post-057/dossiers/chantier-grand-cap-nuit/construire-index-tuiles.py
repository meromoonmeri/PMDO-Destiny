"""Préparation reproductible, hors installation : index Destiny v0.5.7 -> copie candidate.
Usage : python construire-index-tuiles.py /chemin/vers/index.idx /chemin/vers/nouvel-index.idx
Ne jamais écraser l'index d'une installation ; intégration et tests encore nécessaires.
"""
import hashlib,struct,sys
from pathlib import Path
assert len(sys.argv)==3, 'indiquer un index de départ et un chemin de sortie séparé'
src,dst=map(Path,sys.argv[1:]);assert src.resolve()!=dst.resolve(), 'ne pas écraser l’original'
a=src.read_bytes();sha=hashlib.sha256(a).hexdigest()
assert sha=='e964f9871ad0f55a2109cceac61f8d9795a56c50217790375e8efe836064e8a4', 'index différent de Destiny v0.5.7 : fusion manuelle nécessaire'
root=Path(__file__).parent/'candidat/Content/Tile'; names=['GrandCap_Couverture_Bord_Nuit','GrandCap_Bordure_Nord_Nuit','Metano_Town_Base_Night']
def enc(s):
 b=s.encode();n=len(b);return bytes([n])+b if n<128 else bytes([(n&127)|128,n>>7])+b
def node(path):
 with path.open('rb') as f:
  h=f.read(8);_,n=struct.unpack('<ii',h);return h+f.read(n*16)
assert not any(n.encode() in a for n in names)
count=struct.unpack_from('<i',a)[0];out=struct.pack('<i',count+len(names))+a[4:]+b''.join(enc(n)+node(root/(n+'.tile')) for n in names)
dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(out)
print('Original confirmé ; index candidat,',count,'+',len(names),'SHA256',hashlib.sha256(out).hexdigest())
