-- Recrutement Destiny : verrouillé tant que l’Assemblée / la boutique des
-- Zones d’Accueil n’est pas disponible dans le scénario.
--
-- Le moteur PMDO possède déjà le verrou global adapté : NoRecruiting.
-- Il bloque les recrutements par Noigrume, les recrutements après K.O.
-- et la liste des recrues. Destiny le pilote uniquement depuis le drapeau
-- de sauvegarde `RecrutementDebloque`, faux par défaut. Aucun contenu
-- actuel n’appelle `debloquer()` : le futur point de déblocage n’aura qu’à
-- appeler cette fonction.

local recrutement = {}

function recrutement.debloque()
  return SV ~= nil and SV.Destiny ~= nil
    and SV.Destiny.RecrutementDebloque == true
end

function recrutement.synchroniser()
  local autorise = recrutement.debloque()
  if GAME ~= nil and GAME.SetCanRecruit ~= nil then
    GAME:SetCanRecruit(autorise)
  elseif _DATA ~= nil and _DATA.Save ~= nil then
    _DATA.Save.NoRecruiting = not autorise
  end
  return autorise
end

function recrutement.debloquer()
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.RecrutementDebloque = true
  return recrutement.synchroniser()
end

return recrutement
