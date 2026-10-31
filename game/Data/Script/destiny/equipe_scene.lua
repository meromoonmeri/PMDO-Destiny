-- Acteurs de cinématique sans ajouter de spawners aux cartes originales.
-- Les cartes du panorama ne possèdent pas les spawners TEAMMATE_1 de COMMON.
local equipe_scene = {}

function equipe_scene.RestaurerHeros()
  -- Si une sauvegarde a été faite après la réunion, ne pas dupliquer le héros.
  for i = 0, GAME:GetPlayerPartyCount() - 1 do
    local membre = GAME:GetPlayerPartyMember(i)
    local donnees = LTBL(membre)
    if donnees ~= nil and donnees.Importance == 'Hero' then
      if GAME:GetTeamLeaderIndex() ~= i then GAME:SetTeamLeaderIndex(i) end
      SV.Destiny.HeroAssemblyIndex = nil
      return true
    end
  end
  local idx, candidat_fondateur, nb_fondateurs = nil, nil, 0
  for i = 0, GAME:GetPlayerAssemblyCount() - 1 do
    local candidat = GAME:GetPlayerAssemblyMember(i)
    local donnees = LTBL(candidat)
    if donnees ~= nil and donnees.Importance == 'Hero' then
      idx = i
      break
    end
    if candidat.IsFounder and (donnees == nil or donnees.Importance ~= 'Partner') then
      candidat_fondateur, nb_fondateurs = i, nb_fondateurs + 1
    end
  end
  -- Anciennes sauvegardes sans marqueur : accepter un fondateur unique seulement.
  if idx == nil and nb_fondateurs == 1 then idx = candidat_fondateur end
  if idx == nil then
    print('[Destiny] Héros introuvable ou ambigu dans la réserve : équipe inchangée.')
    return false
  end
  local heros = GAME:GetPlayerAssemblyMember(idx)
  GAME:RemovePlayerAssembly(idx)
  GAME:AddPlayerTeam(heros)
  GAME:SetTeamLeaderIndex(GAME:GetPlayerPartyCount() - 1)
  SV.Destiny.HeroAssemblyIndex = nil
  return true
end

function equipe_scene.Partenaire(x, y, direction)
  local present = CH('Teammate1')
  if present ~= nil then GROUND:RemoveCharacter('Teammate1') end
  local leader = GAME:GetTeamLeaderIndex()
  local candidat = nil
  for i = 0, GAME:GetPlayerPartyCount() - 1 do
    if i ~= leader then
      local membre = GAME:GetPlayerPartyMember(i)
      local donnees = LTBL(membre)
      if donnees ~= nil and donnees.Importance == 'Partner' then
        candidat = membre
        break
      end
      candidat = candidat or membre
    end
  end
  if candidat == nil then
    print('[Destiny] Partenaire absent de l’équipe : scène non démarrée.')
    return nil
  end
  local acteur = GROUND:CreateCharacterFromCharData('Teammate1', candidat, x, y, direction)
  acteur.CollisionDisabled = true
  AI:DisableCharacterAI(acteur)
  return acteur
end

function equipe_scene.Suivre(acteur, joueur)
  if acteur == nil or joueur == nil then return end
  AI:SetCharacterAI(acteur, 'origin.ai.ground_partner', joueur, acteur.Position)
  AI:EnableCharacterAI(acteur)
end

return equipe_scene
