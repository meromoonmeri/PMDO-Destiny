from pathlib import Path
import shutil,json,struct
R=Path('/home/user/chantier-grand-cap-nuit/candidat');G=Path('/home/user/.cache/lostwood-moteur/PMDO-Destiny');assert str(G).startswith('/home/user/.cache/')
for f in R.rglob('*'):
 if f.is_file():
  dst=G/f.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dst)
# Ajouter les 3 nœuds d'index uniquement dans cette copie provisoire.
index=G/'Content/Tile/index.idx';data=index.read_bytes();count=struct.unpack_from('<i',data)[0]
def node(p):
 with p.open('rb') as f:
  h=f.read(8);size,n=struct.unpack('<ii',h);return h+f.read(n*16)
def enc(s):
 b=s.encode();n=len(b);return bytes([n])+b if n<128 else bytes([(n&127)|128,n>>7])+b
names=['GrandCap_Couverture_Bord_Nuit','GrandCap_Bordure_Nord_Nuit','Metano_Town_Base_Night']
assert all(name.encode() not in data for name in names), 'copie déjà indexée'
index.write_bytes(struct.pack('<i',count+len(names))+data[4:]+b''.join(enc(s)+node(G/'Content/Tile'/f'{s}.tile') for s in names))
# La zone et son index sont changés uniquement pour l’essai ; numéros existants stables.
for path,field in [(G/'Data/Zone/destiny_cliff_tests.json','GroundMaps'),(G/'Data/Zone/index.idx','Grounds')]:
 doc=json.loads(path.read_text(encoding='utf-8-sig'));obj=doc['Object']; obj=obj if field=='GroundMaps' else obj['destiny_cliff_tests'];assert 'grand_cap_panoramique_nuit' not in obj[field];obj[field].append('grand_cap_panoramique_nuit');path.write_text(json.dumps(doc,ensure_ascii=False,indent=2))
# Entrée directe : saut technique du quiz, exclusivement dans la copie isolée.
p=G/'Data/Script/destiny/ground/intro_halo/init.lua';s=p.read_text();old="GAME:EnterDungeon('lost_wood', 0, 0, 0, RogueEssence.Data.GameProgress.DungeonStakes.Risk, true, false)";new="GAME:EnterGroundMap('destiny_cliff_tests', 'grand_cap_panoramique_nuit', 'Entrance')";assert s.count(old)==2;p.write_text(s.replace(old,new))
# Supprimer uniquement la sauvegarde jetable produite par les essais précédents.
(G/'SAVE/SAVE.rssv').unlink(missing_ok=True)
print('Copie préparée ; index de tuiles',count,'→',count+3)
