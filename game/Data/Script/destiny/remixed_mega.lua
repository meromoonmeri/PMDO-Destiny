-- Mégaévolution persistante et réversible à la Source de Destiny.
-- La forme est changée avec Character:Promote (pas Transform, qui est temporaire).
-- Les noms / identifiants proviennent de la ROM privée et des fiches fusionnées.
local qi = require 'destiny.remixed_iq'
local donnees = require 'destiny.remixed_mega_data'
local M = {}

local function contient(tab, val)
  for _, v in ipairs(tab) do if v == val then return true end end
  return false
end

function M.choix(pokemon)
  if not pokemon then return {} end
  local base = pokemon.BaseForm
  local entree = donnees[base.Species]
  if not entree or not contient(entree.bases, base.Form) then return {} end
  return entree.megas
end

function M.evoluer(pokemon, forme)
  if not pokemon then return false, 'Aucun Pokémon sélectionné.' end
  if qi.lire(pokemon) < qi.SEUIL_MEGA then
    return false, 'Il faut au moins 410 points de QI.'
  end
  local base = pokemon.BaseForm
  if base.Skin ~= 'normal' then
    return false, 'Cette apparence spéciale ne possède pas encore de sprite Méga vérifié.'
  end
  local valide = false
  for _, option in ipairs(M.choix(pokemon)) do
    if option.forme == forme then valide = true; break end
  end
  if not valide then return false, 'Aucune Mégaévolution disponible pour cette forme.' end
  local table_perso = LTBL(pokemon)
  if not table_perso then return false, 'Données personnelles indisponibles.' end

  local original_forme, original_espece = base.Form, base.Species
  local original_slot = pokemon.FormIntrinsicSlot
  local original_talents = {}
  for i = 0, pokemon.BaseIntrinsics.Count - 1 do
    table.insert(original_talents, pokemon.BaseIntrinsics[i])
  end
  local destination = RogueEssence.Dungeon.MonsterID(base.Species, forme, base.Skin, base.Gender)
  pokemon:Promote(destination)
  -- Ne mettre les métadonnées qu'une fois la promotion effectuée.
  table_perso.DestinyMegaEspece = original_espece
  table_perso.DestinyMegaForme = original_forme
  table_perso.DestinyMegaSlot = original_slot
  table_perso.DestinyMegaTalents = original_talents
  return true
end

function M.revenir(pokemon)
  if not pokemon then return false, 'Aucun Pokémon sélectionné.' end
  local table_perso = LTBL(pokemon)
  local base = pokemon.BaseForm
  if not table_perso or table_perso.DestinyMegaEspece ~= base.Species or
     table_perso.DestinyMegaForme == nil then
    return false, "Cette forme n'a pas été créée par la Source de Destiny."
  end
  local entree = donnees[base.Species]
  local est_mega = false
  if entree then
    for _, option in ipairs(entree.megas) do
      if option.forme == base.Form then est_mega = true; break end
    end
  end
  if not est_mega then return false, "Ce Pokémon n'est pas sous une forme Méga reconnue." end

  local original_forme = table_perso.DestinyMegaForme
  local talents = table_perso.DestinyMegaTalents
  local slot = table_perso.DestinyMegaSlot
  local destination = RogueEssence.Dungeon.MonsterID(base.Species, original_forme, base.Skin, base.Gender)
  pokemon:Promote(destination)
  -- Préserver aussi les éventuels talents personnalisés de la forme précédente.
  if talents and #talents > 0 then
    pokemon.BaseIntrinsics:Clear()
    for _, talent in ipairs(talents) do pokemon.BaseIntrinsics:Add(talent) end
    pokemon.FormIntrinsicSlot = slot or -1
    pokemon:RestoreForm()
  end
  table_perso.DestinyMegaEspece = nil
  table_perso.DestinyMegaForme = nil
  table_perso.DestinyMegaSlot = nil
  table_perso.DestinyMegaTalents = nil
  return true
end

return M
