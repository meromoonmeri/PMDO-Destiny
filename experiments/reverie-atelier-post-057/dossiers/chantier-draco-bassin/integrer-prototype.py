from pathlib import Path
root=Path('/home/user/chantier-apercu-reverie/travail/game/Data/Script/destiny/ground')
main=root/'WaterfallVillageCapital/init.lua'; dev=root/'WaterfallVillageCapital_Dev/init.lua'
s=main.read_text(); assert dev.read_text()==s
anchor="local function partenaire_pour(hero)\n"
insert="""-- Prototype local : Draco garde son identité propre, distincte du Doyen Grodrive.
-- La case est dans l'eau ; on ne change ni le terrain ni les autres habitants.
local function installer_doyen_draco(map)
  if map == nil or map.AssetName ~= 'reverie_etang' then return end
  local acteur = habitant('Doyen_Draco', 'dragonair', Gender.Male, 1120, 2080)
  if acteur.Data ~= nil then acteur.Data.Nickname = 'Doyen Draco' end
  acteur.HideShadow = true -- NonSerialized : à réappliquer au chargement.
  GROUND:EntTurn(acteur, Direction.Left)
end

"""
assert s.count(anchor)==1;s=s.replace(anchor,insert+anchor)
anchor="  installer_luxray_attente(map)\n"
assert s.count(anchor)==2;s=s.replace(anchor,anchor+'  installer_doyen_draco(map)\n')
anchor='local dialogues_habitants = {\n'
insert="""local dialogues_habitants = {
  Doyen_Draco = {
    {{'Normal', 'Les eaux de ce bassin ont vu passer bien des saisons. Prenez le temps de les écouter.'}},
  },
"""
assert s.count(anchor)==1;s=s.replace(anchor,insert)
main.write_text(s);dev.write_text(s)
print('PASS prototype local écrit dans les deux scripts ; pas de modification de Ground')
