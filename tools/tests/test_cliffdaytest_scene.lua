-- Accès direct à la falaise de nuit et début de la scène en duo, avec doublures.
local chemin = arg[1] .. '/game/Data/Script/destiny/ground/cliffdaytest_nuit/init.lua'
for _, nom in ipairs({'origin.common', 'destiny.equipe_scene', 'destiny.cinematique',
                       'destiny.recrutement', 'destiny.meteo_reverie'}) do
  package.preload[nom] = function() return {} end
end

local nombre, fade, lit_partenaire, spawn_char, masque, coupe, indisponible
local partenaire, acteur = {}, {}
GAME = {
  GetPlayerPartyCount = function() return nombre end,
  GetPlayerPartyMember = function(_, i)
    assert(i == 1 and nombre >= 2, 'lecture hors équipe')
    lit_partenaire = true
    return partenaire
  end,
  FadeIn = function() fade = true end,
  CutsceneMode = function(_, mode) coupe = mode end,
}
GROUND = {
  Hide = function(_, nom) assert(nom == 'PLAYER'); masque = true end,
  SpawnerSetSpawn = function(_, nom, perso) assert(nom == 'Adagio'); spawn_char = perso end,
  SpawnerDoSpawn = function(_, nom) assert(nom == 'Adagio'); if not indisponible then return acteur end end,
}
UI = {ResetSpeaker = function() end}
local debut_marche = {}
AI = {DisableCharacterAI = function(_, personnage)
  assert(personnage == acteur, 'la scène doit animer le partenaire instancié')
  error(debut_marche) -- arrêter le banc avant la chorégraphie native
end}
local falaise = assert(loadfile(chemin))()

local function initialiser(n)
  nombre, fade, lit_partenaire, spawn_char, masque, coupe, indisponible = n
  SV = {Destiny = {}}
end

initialiser(1)
falaise.ScenePartenaire()
assert(fade and not lit_partenaire and not spawn_char, 'solo : afficher la carte sans chercher un partenaire')
assert(not masque and not coupe and next(SV.Destiny) == nil, 'solo : rendre la main sans changer la progression')

initialiser(2)
indisponible = true
falaise.ScenePartenaire()
assert(fade and spawn_char == partenaire, 'spawner indisponible : afficher la carte')
assert(not masque and not coupe and next(SV.Destiny) == nil)

initialiser(2)
local ok, err = pcall(falaise.ScenePartenaire)
assert(not ok and err == debut_marche, 'le duo doit atteindre la scène')
assert(lit_partenaire and spawn_char == partenaire and masque and coupe)
assert(SV.Destiny.PrologueHeros == 'termine')
print('PASS falaise nuit : solo jouable, spawner indisponible, partenaire correct en duo')
