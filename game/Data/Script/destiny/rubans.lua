-- Atelier des deux pièces : un profil anatomique, pas un filtre de déblocage.
-- Les clés « espèce:forme » priment sur l'espèce. Un futur starter conserve
-- une pose par défaut et reste éligible même avant sa retouche dédiée.
local pool = require 'destiny.starter_pool'
local M = {}
local profils = {}
local function groupe(coupe, liste)
  for espece in liste:gmatch('%S+') do
    assert(profils[espece] == nil, 'Profil répété : ' .. espece)
    profils[espece] = coupe
  end
end

groupe('debout', [[
  pikachu meowth charmander larvitar sneasel treecko ralts gible
  buneary chimchar riolu minccino axew golett oshawott pawniard snivy
  froakie chespin pancham espurr noibat scorbunny sobble grookey charcadet
  fuecoco tinkatink
]])
groupe('kaiminus', [[totodile]])
groupe('cou_court', [[squirtle snorunt wooper]])
groupe('quadrupede', [[
  growlithe vulpix chikorita cyndaquil mudkip skitty shinx
  turtwig tepig zorua fennekin jangmo_o litten stufful rockruff
  salandit nickit sprigatito pawmi
]])
groupe('criniere', [[eevee growlithe:1]])
groupe('plumes', [[murkrow torchic swablu piplup rookidee quaxly]])
groupe('aile', [[rowlet]])
groupe('long', [[dratini popplio dreepy]])
groupe('flanc', [[phanpy fidough bulbasaur mareep sandile]])
groupe('carapace', [[snom joltik wimpod larvesta]])
groupe('coque_metal', [[beldum]])
groupe('tronc_bas', [[togepi budew litwick goomy phantump pumpkaboo hatenna]])
groupe('nuage', [[cosmog]])
groupe('pomme', [[applin]])
groupe('branchies', [[wooper:1]])

-- Face, ¾ gauche, profil gauche, dos ¾ gauche, dos. Le moteur projette
-- l'autre côté. Les coordonnées sont des retouches en pixels de sprite.
local coutures = {
  -- Tour de cou : on remonte du poitrail vers la gorge, sans gagner le museau.
  totodile     = '0,0;0,0;0,0;0,0;0,0',
  vulpix       = '0,-4;1,-3;4,-2;0,-1;0,0',
  ['vulpix:1'] = '0,-4;1,-3;4,-2;0,-1;0,0',
  growlithe    = '0,-1;1,-1;2,0;0,0;0,0',
  ['growlithe:1'] = '0,-1;2,-1;3,0;0,0;0,1',
  eevee        = '0,0;1,0;2,0;0,0;0,1',
  skitty       = '0,0;1,0;3,1;2,2;0,3',
  shinx        = '0,0;2,0;3,-1;0,0;0,0',
  nickit       = '0,-1;1,0;2,0;0,0;0,1',
  pawmi        = '0,0;2,-2;1,0;0,0;0,1',
  jangmo_o     = '0,-2;0,-1;1,-1;0,0;0,1',
  turtwig      = '0,0;1,0;2,0;2,2;0,1',
  sprigatito   = '0,0;1,1;1,0;0,0;0,0',
  -- Le décor reste sur le tissu/la coque ; ni sur les yeux ni sur la cire basse.
  bulbasaur    = '1,-3;0,-2;0,-2;0,-1;0,-1',
  mareep       = '0,-2;0,-1;1,0;0,0;0,0',
  sandile      = '0,-1;0,0;1,0;0,0;0,0',
  litwick      = '0,-6;0,-6;0,-6;0,-2;0,-1',
  hatenna      = '0,1;-2,1;-3,1;0,2;0,2',
  golett       = '0,-5;0,-5;0,-1;-2,-3;0,-3',
  ['wooper:1'] = '0,-1;0,0;0,0;0,0;0,0',
}
function M.couture(espece, forme)
  return coutures[espece .. ':' .. tostring(forme)] or coutures[espece] or ''
end

function M.profil(espece, forme)
  return profils[espece .. ':' .. tostring(forme)] or profils[espece]
end

function M.installer()
  local ok, moteur = pcall(luanet.import_type, 'RogueEssence.Content.DestinyRibbon')
  if not ok or moteur == nil then return end
  for _, s in ipairs(pool.construire(nil)) do
    moteur.RegisterStarter(s.espece, s.forme, M.profil(s.espece,s.forme) or 'debout', M.couture(s.espece,s.forme))
  end
end

return M
