from pathlib import Path
import json,zipfile,hashlib
R=Path('/home/user/chantier-grand-cap-nuit');G=Path('/home/user/.cache/lostwood-moteur/PMDO-Destiny');C=R/'candidat';Z=R/'sauvegarde-raccord-057.zip'
# Sources de l'installation isolée v0.5.7 : scripts ville intacts ; zone depuis l'archive d'origine.
archive=zipfile.ZipFile(R.parent/'.cache/lostwood-moteur/destiny.zip')
paths=archive.namelist();prefix=next(x[:-len('Data/Zone/town02_waterfallvillage.json')] for x in paths if x.endswith('Data/Zone/town02_waterfallvillage.json'))
originals={}
for rel in ['Data/Zone/town02_waterfallvillage.json','Data/Zone/index.idx']:
 originals[rel]=archive.read(prefix+rel)
rel='Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'; originals[rel]=(G/rel).read_bytes()
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED) as z:
 for rel,data in originals.items():z.writestr(rel,data)
assert zipfile.ZipFile(Z).testzip() is None
# Ajouter une carte, sans renuméroter les Ground antérieurs.
for rel,key in [('Data/Zone/town02_waterfallvillage.json','GroundMaps'),('Data/Zone/index.idx','Grounds')]:
 d=json.loads(originals[rel].decode('utf-8-sig'));o=d['Object'];o=o if key=='GroundMaps' else o['town02_waterfallvillage'];assert 'grand_cap_panoramique_nuit' not in o[key];o[key].append('grand_cap_panoramique_nuit');p=C/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
s=originals['Data/Script/destiny/ground/WaterfallVillageCapital/init.lua'].decode('utf-8-sig').replace('\r\n','\n')
old="local function installer_portes(map)\n"; assert s.count(old)==1
new='''-- Grand escalier nord de Réverie, au bord supérieur de la carte fusionnée.
-- Capteur de transition, sans changer le dessin ni les collisions d'origine.
local function installer_sortie_grand_cap(map)
  if map == nil then return end
  local actifs = {reverie_centre=true, reverie_nord=true, WaterfallVillageCapital=true}
  if not actifs[map.AssetName] then
    if map:FindObject('SortieGrandCap') then GROUND:RemoveObject('SortieGrandCap') end
    return
  end
  if map:FindObject('SortieGrandCap') then return end
  local sortie = RogueEssence.Ground.GroundObject()
  sortie.EntName = 'SortieGrandCap'
  sortie.Collider = RogueElements.Rect(736, 0, 72, 8)
  sortie.Passable = false
  sortie:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  sortie:OnMapInit()
  map:AddObject(sortie)
end

local function installer_portes(map)
  installer_sortie_grand_cap(map)
''';s=s.replace(old,new)
old='function ville.SortieCarrefour_Touch(obj, activator)\n';assert s.count(old)==1
new='''function ville.SortieGrandCap_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if changement_quartier then return end
  changement_quartier = true
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('town02_waterfallvillage', 'grand_cap_panoramique_nuit', 'Entrance', true)
end

function ville.SortieCarrefour_Touch(obj, activator)
''';s=s.replace(old,new)
p=C/'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
print('Sauvegarde CRC PASS ; copie candidate, destination ajoutée en fin de liste ; scripts originaux conservés')
