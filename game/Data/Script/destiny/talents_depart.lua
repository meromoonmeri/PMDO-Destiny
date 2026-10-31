-- Choix des talents à la création du héros et du partenaire.
-- Les données viennent de la forme choisie dans la Quest et dans le jeu de base.
local M = {}

-- Ne proposer qu'une fois chaque talent existant et jouable. Le troisième
-- emplacement correspond au talent caché ; il reste disponible dès le départ.
function M.candidats(espece, forme)
  local fiche = _DATA:GetMonster(espece).Forms[forme]
  local ids = { fiche.Intrinsic1 or '', fiche.Intrinsic2 or '', fiche.Intrinsic3 or '' }
  local candidats, vus = {}, {}
  local indisponibles = 0
  for slot, id in ipairs(ids) do
    if id ~= '' and id ~= 'none' and not vus[id] then
      vus[id] = true
      local talent = _DATA:GetIntrinsic(id)
      if talent ~= nil and talent.Released then
        table.insert(candidats, { id = id, info = talent, cache = slot == 3 })
      else
        indisponibles = indisponibles + 1
      end
    end
  end
  return candidats, indisponibles
end

function M.choisir(espece, forme, nom, role)
  local candidats, indisponibles = M.candidats(espece, forme)
  if indisponibles > 0 then
    UI:WaitShowVoiceOver("Un talent de ce Pokémon n'est pas encore jouable ;\nil ne sera pas proposé.", -1)
  end
  if #candidats == 0 then
    -- Aucun des choix de départ actuels n'est dans ce cas. Garder le jeu
    -- jouable si une future fiche n'a aucun talent valide, sans en inventer.
    UI:WaitShowVoiceOver("Aucun talent jouable n'est défini pour ce Pokémon.", -1)
    return 'none'
  end

  local etiquettes = {}
  for _, candidat in ipairs(candidats) do
    local nom_talent = candidat.info:GetColoredName()
    if candidat.cache then nom_talent = nom_talent .. ' (caché)' end
    table.insert(etiquettes, nom_talent)
  end

  -- Même un talent unique est montré : le choix n'est jamais silencieux.
  -- Refuser la confirmation ramène au menu, sans changer de Pokémon.
  local dernier = 1
  while true do
    UI:BeginChoiceMenu('Choisis le talent du ' .. role .. ' :\n' .. nom, etiquettes, dernier, -1)
    UI:WaitForChoice()
    dernier = UI:ChoiceResult()
    local candidat = candidats[dernier]
    UI:ChoiceMenuYesNo('Choisir ' .. candidat.info:GetColoredName() .. ' pour\n' .. nom .. ' ?', false)
    UI:WaitForChoice()
    if UI:ChoiceResult() then return candidat.id end
  end
end

return M
