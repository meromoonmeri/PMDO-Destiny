-- Module préparatoire : message de réussite pour la Méga-Évolution.
-- Non branché au jeu : appeler uniquement après une promotion réussie.
local M = {}

local function melanger(a, b, t)
  return math.floor(a + (b - a) * t + 0.5)
end

function M.degrade(texte)
  local caracteres = {}
  for car in texte:gmatch('[%z\1-\127\194-\244][\128-\191]*') do
    caracteres[#caracteres + 1] = car
  end
  local n = 0
  for _, car in ipairs(caracteres) do
    if car ~= ' ' and car ~= '-' then n = n + 1 end
  end
  local resultat, rang = {}, 0
  for _, car in ipairs(caracteres) do
    if car == ' ' or car == '-' then
      resultat[#resultat + 1] = car
    else
      local t = n > 1 and rang / (n - 1) or 0
      -- Bleu clair vers violet, en passant par le bleu électrique.
      local a, b, u
      if t < 0.5 then a, b, u = {135, 232, 255}, {67, 135, 255}, t * 2
      else a, b, u = {67, 135, 255}, {208, 137, 255}, (t - 0.5) * 2 end
      local couleur = string.format('#%02X%02X%02X', melanger(a[1], b[1], u), melanger(a[2], b[2], u), melanger(a[3], b[3], u))
      resultat[#resultat + 1] = '[color=' .. couleur .. ']' .. car .. '[color]'
      rang = rang + 1
    end
  end
  return table.concat(resultat)
end

function M.message_dracaufeu_x()
  return 'Vous avez Méga-Évolué en\n' .. M.degrade('Méga-Dracaufeu X') .. ' !'
end

function M.afficher_dracaufeu_x()
  UI:ResetSpeaker()
  UI:WaitShowDialogue(M.message_dracaufeu_x())
end

return M
