-- Présentation inspirée du BoardMenu/JobMenu d'Halcyon ; données Destiny.
-- Propose les donjons effectivement débloqués à Réverie (Bois Perdus, puis Grotte Verdoyante).
local interface = {}

local LIBELLES_ZONES = {
  lost_wood = {titre = 'Traverser les Bois Perdus', lieu = 'Bois Perdus'},
  grotte_verdoyante = {titre = 'Explorer la Grotte Verdoyante', lieu = 'Grotte Verdoyante'},
}

function interface.Ouvrir(missions)
  local board, fiche = nil, nil
  local function infos_zone()
    local m = missions.Actuelle()
    local zone = (m and m.Zone) or (missions.ZoneOffre and missions.ZoneOffre()) or 'lost_wood'
    return LIBELLES_ZONES[zone] or LIBELLES_ZONES.lost_wood
  end
  local function etat()
    local m = missions.Actuelle()
    if m ~= nil then return m.Etat end
    if missions.OffreDisponible() then return 'disponible' end
    return 'vide'
  end
  local function texte(menu, valeur, x, y)
    menu.Elements:Add(RogueEssence.Menu.MenuText(valeur, RogueElements.Loc(x, y)))
  end
  local function separer(menu, y)
    menu.Elements:Add(RogueEssence.Menu.MenuDivider(RogueElements.Loc(8, y), 240))
  end
  local function dessiner()
    board.Elements:Clear()
    texte(board, 'Tableau des missions', 16, 8)
    separer(board, 20)
    local e = etat()
    if e == 'vide' then
      texte(board, 'Aucune mission disponible.', 16, 32)
    else
      local info = infos_zone()
      texte(board, STRINGS:Format('\\uE110'), 12, 33)
      texte(board, info.titre, 28, 28)
      texte(board, e == 'disponible' and info.lieu or (e == 'reussie' and (info.lieu .. ' - Réussie') or (info.lieu .. ' - Acceptée')), 28, 44)
      separer(board, 60)
    end
    separer(board, 148)
    local nb = (e == 'en_cours' or e == 'reussie') and 1 or 0
    texte(board, 'Missions acceptées : ' .. tostring(nb) .. '/1', 16, 156)
  end
  local function fermer_fiche()
    _MENU:RemoveMenu()
    fiche = nil
    dessiner()
  end
  local function ouvrir_fiche()
    local e = etat()
    if e == 'vide' then _GAME:SE('Menu/Cancel'); return end
    local info = infos_zone()
    fiche = RogueEssence.Menu.ScriptableMenu('DESTINY_MISSION_FICHE', 32, 32, 256, 176, function(input)
      if input:JustPressed(RogueEssence.FrameInput.InputType.Cancel) or input:JustPressed(RogueEssence.FrameInput.InputType.Menu) then
        _GAME:SE('Menu/Cancel'); fermer_fiche()
      elseif input:JustPressed(RogueEssence.FrameInput.InputType.Confirm) then
        if e == 'disponible' then missions.Accepter()
        elseif e == 'reussie' then missions.Reclamer() end
        _GAME:SE('Menu/Confirm'); fermer_fiche()
      end
    end)
    texte(fiche, 'Mission : exploration', 16, 8)
    separer(fiche, 20)
    texte(fiche, 'Objectif : traverser le donjon', 16, 34)
    texte(fiche, 'Lieu : ' .. info.lieu, 16, 52)
    texte(fiche, 'Récompense : 300 Poké', 16, 70)
    texte(fiche, e == 'disponible' and 'Statut : disponible' or (e == 'reussie' and 'Statut : réussie' or 'Statut : acceptée'), 16, 88)
    separer(fiche, 130)
    texte(fiche, e == 'disponible' and 'Confirmer : accepter' or (e == 'reussie' and 'Confirmer : récompense' or 'Confirmer : retour'), 16, 140)
    texte(fiche, 'Annuler : retour', 16, 156)
    _MENU:AddMenu(fiche, false)
  end
  board = RogueEssence.Menu.ScriptableMenu('DESTINY_TABLEAU_MISSIONS', 32, 32, 256, 176, function(input)
    if input:JustPressed(RogueEssence.FrameInput.InputType.Confirm) then
      _GAME:SE('Menu/Confirm'); ouvrir_fiche()
    elseif input:JustPressed(RogueEssence.FrameInput.InputType.Cancel) or input:JustPressed(RogueEssence.FrameInput.InputType.Menu) then
      _GAME:SE('Menu/Cancel'); _MENU:RemoveMenu()
    end
  end)
  dessiner()
  UI:SetCustomMenu(board)
  UI:WaitForChoice()
end
return interface
