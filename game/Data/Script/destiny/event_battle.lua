local qi = require 'destiny.remixed_iq'

-- Ajouté après l'effet natif des gelées : l'effet d'origine n'est pas écrasé.
function BATTLE_SCRIPT.DestinyGeleeQI(owner, ownerChar, context, args)
  local cible = context.Target
  if not cible or not args or not args.element then return end
  local gain = qi.gelee(cible, args.element)
  if gain > 0 then
    _DUNGEON:LogMsg(cible:GetDisplayName(true) .. ' gagne ' .. tostring(gain) .. ' point(s) de QI.')
  end
end
