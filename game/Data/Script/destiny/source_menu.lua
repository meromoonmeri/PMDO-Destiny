-- Menu partagé entre les deux Sources Destiny ; aucune géométrie n'est remplacée.
require 'origin.menu.team.AssemblySelectMenu'
local qi = require 'destiny.qi'
local mega = require 'destiny.mega'
local M = {}

local function selectionner()
  UI:WaitShowDialogue('Quel Pokémon souhaite approcher de la Source ?')
  return AssemblySelectMenu.run(nil, false)
end

local function confirmer(texte)
  UI:ChoiceMenuYesNo(texte, true)
  UI:WaitForChoice()
  return UI:ChoiceResult()
end

local function afficher_resultat(pokemon, ok, raison, texte_succes)
  if ok then
    GROUND:RefreshPlayer()
    UI:WaitShowDialogue(texte_succes)
  else
    UI:WaitShowDialogue(raison)
  end
end

function M.action(visite)
  GAME:CutsceneMode(true)
  UI:ResetSpeaker()
  local continuer = true
  local visiter = false
  while continuer do
    local menus = { 'Mégaévoluer', 'Retrouver sa forme', 'Consulter le QI' }
    if visite then table.insert(menus, 'Rejoindre la Source irisée') end
    table.insert(menus, 'Partir')
    UI:BeginChoiceMenu('La Source lumineuse scintille...', menus, 1, #menus)
    UI:WaitForChoice()
    local choix = UI:ChoiceResult()
    if choix == 1 then
      local pokemon = selectionner()
      if pokemon then
        local options = mega.choix(pokemon)
        if #options == 0 then
          UI:WaitShowDialogue("Ce Pokémon ne dispose pas d'une forme Méga reconnue ici.")
        elseif qi.lire(pokemon) < qi.SEUIL_MEGA then
          UI:WaitShowDialogue(pokemon:GetDisplayName(true) .. ' a ' .. qi.lire(pokemon) .. ' points de QI. Il en faut 410.')
        else
          local option = options[1]
          if #options > 1 then
            local labels = {}
            for _, e in ipairs(options) do table.insert(labels, e.nom) end
            table.insert(labels, 'Annuler')
            UI:BeginChoiceMenu('Quelle Mégaévolution ?', labels, 1, #labels)
            UI:WaitForChoice()
            local idx = UI:ChoiceResult()
            option = idx and options[idx] or nil
          end
          if option and confirmer('Faire Mégaévoluer ' .. pokemon:GetDisplayName(true) .. ' en ' .. option.nom .. ' ?') then
            local nom = pokemon:GetDisplayName(true)
            local ok, raison = mega.evoluer(pokemon, option.forme)
            afficher_resultat(pokemon, ok, raison, nom .. ' a Mégaévolué en ' .. option.nom .. ' !')
          end
        end
      end
    elseif choix == 2 then
      local pokemon = selectionner()
      if pokemon and confirmer('Rendre à ' .. pokemon:GetDisplayName(true) .. ' sa forme précédente ?') then
        local nom = pokemon:GetDisplayName(true)
        local ok, raison = mega.revenir(pokemon)
        afficher_resultat(pokemon, ok, raison, nom .. ' a retrouvé sa forme précédente.')
      end
    elseif choix == 3 then
      local pokemon = selectionner()
      if pokemon then
        UI:WaitShowDialogue(pokemon:GetDisplayName(true) .. ' possède ' .. qi.lire(pokemon) .. ' points de QI. La Source demande 410 points pour Mégaévoluer.')
      end
    elseif choix == 4 and visite then
      visiter = true
      continuer = false
    else
      continuer = false
    end
  end
  GAME:CutsceneMode(false)
  if visiter then visite() end
end

return M
