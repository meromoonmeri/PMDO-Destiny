-- Règle Destiny inspirée de Halcyon : la perte d'un protagoniste met fin à
-- l'expédition, mais une réanimation réussie (priorité précédente) la sauve.
-- Ne modifie ni la sortie des zones ni le comportement des recrues ordinaires.
local function indispensable(membre)
  if membre.IsPartner or membre.IsFounder then return true end
  local donnees = LTBL(membre)
  return donnees ~= nil and (donnees.Importance == 'Hero' or donnees.Importance == 'Partner')
end

function SINGLE_CHAR_SCRIPT.DestinyVerifierKO(owner, ownerChar, context, args)
  if context == nil or context.User == nil or not context.User.Dead then return end
  local nb = GAME:GetPlayerPartyCount()
  local invites = GAME:GetPlayerGuestCount()
  if nb == 0 then return end

  -- Parcourir les personnages réels plutôt que supposer un ordre dans l'équipe.
  -- Les morts ennemies ne comptent pas : seuls joueurs et invités sont examinés.
  local concerne = false
  for i = 0, nb - 1 do
    local membre = GAME:GetPlayerPartyMember(i)
    if membre.Dead and indispensable(membre) then concerne = true; break end
  end
  if not concerne then
    for i = 0, invites - 1 do
      local membre = GAME:GetPlayerGuestMember(i)
      if membre.Dead and indispensable(membre) then concerne = true; break end
    end
  end
  if not concerne then return end

  -- Comme Halcyon, évacuer les survivants puis laisser le moteur détecter la
  -- défaite normale. Les scripts propres aux zones décident de la suite.
  local function evacuer(membre)
    if not membre.Dead then
      GAME:WaitFrames(60)
      TASK:WaitTask(_DUNGEON:ProcessBattleFX(membre, membre, _DATA.SendHomeFX))
      membre.Dead = true
    end
  end
  for i = 0, nb - 1 do evacuer(GAME:GetPlayerPartyMember(i)) end
  for i = 0, invites - 1 do evacuer(GAME:GetPlayerGuestMember(i)) end
end
