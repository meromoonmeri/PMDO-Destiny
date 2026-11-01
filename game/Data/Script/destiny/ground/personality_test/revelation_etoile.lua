-- revelation_etoile.lua — animation de fin du quiz de personnalité.
--
-- Après les 20 questions, le joueur est plongé dans le noir et doit
-- MAINTENIR LE CLIC DROIT de sa souris (ou la touche d'action, en
-- secours) : une lumière pixel-art converge et forge une étoile qui
-- s'illumine aux couleurs du type du starter destiné. L'étoile terminée
-- est affichée via les DirSheet game/Content/BG/quiz_star_*.dir
-- (générées par tools/generer_etoile_quiz.py), puis la révélation
-- « Quelqu'un comme toi serait [Nom en couleur du type] ! » s'affiche
-- avec le portrait du Pokémon.
--
-- Aucune modification C# : ShowBG/WaitShowBG (BGFadeFX), TextPopUp,
-- SetSpeaker (portrait), PlayFanfare et GAME:IsInputDown suffisent.
local quiz_data = require 'destiny.ground.personality_test.quiz_data'

local M = {}

-- FrameInput.InputType (engine FrameInput.cs) : Confirm = 0,
-- LeftMouse = 29, RightMouse = 30. GAME:IsInputDown lit
-- MetaInputManager, mis à jour chaque frame par GameBase.Update.
M.INPUT_ACTION = 0       -- Confirm (repli clavier, accessibilité)
M.INPUT_CLIC_DROIT = 30  -- RightMouse : le maintien demandé au joueur

-- Charge nécessaire (en frames maintenues) et secours anti-blocage.
M.CHARGE_PAR_FRAME = 2
M.BESOIN_DEFAUT = 150    -- ~2,5 s de clic droit maintenu
M.SECOURS_DEFAUT = 3600  -- 60 s sans maintien : on finit l'animation

-- Type primaire (Element1) du starter, lu sur la fiche du jeu.
function M.type_du_starter(starter)
  local ok, elt = pcall(function()
    return _DATA:GetMonster(starter.espece).Forms[starter.forme].Element1
  end)
  if ok and type(elt) == 'string' and quiz_data.couleurs_types[elt] then
    return elt
  end
  return 'normal'
end

-- « Bulbizarre » coloré par la couleur conventionnelle de son type.
function M.nom_colore(nom, element)
  local info = quiz_data.couleurs_types[element] or quiz_data.couleurs_types.normal
  return '[color=' .. info.hex .. ']' .. nom .. '[color]'
end

-- Le maintien demandé : clic droit de la souris (repli : touche d'action).
function M.maintien()
  return GAME:IsInputDown(M.INPUT_CLIC_DROIT) or GAME:IsInputDown(M.INPUT_ACTION)
end

-- Barre de progression ASCII de la lumière (popup non bloquante).
function M.barre(charge, besoin)
  local pleins = math.floor(charge * 10 / besoin + 0.5)
  return 'Lumière de l\'étoile : ['
    .. string.rep('#', pleins)
    .. string.rep('-', 10 - pleins)
    .. ']'
end

-- Déroule toute la séquence de révélation (appelé par
-- personality_test/init.lua après le calcul de la nature).
-- opts : { element = ..., besoin = ..., delai_secours = ... } (tests).
function M.derouler(starter, opts)
  opts = opts or {}
  local besoin = opts.besoin or M.BESOIN_DEFAUT
  local delai_secours = opts.delai_secours or M.SECOURS_DEFAUT
  local element = opts.element or M.type_du_starter(starter)

  -- 1. La scène du rêve s'éteint : la lumière pixel reste seule au noir.
  GAME:FadeOut(false, 30)
  GAME:WaitFrames(30)
  UI:WaitShowVoiceOver(
    'Une lumière pixel apparaît dans le noir...\n'
    .. 'Maintiens le clic droit pour forger ton étoile !\n'
    .. '(Ou maintiens la touche d\'action.)', -1)
  UI:WaitShowBG('quiz_star_lumiere_1', 4, 20)

  -- 2. Le joueur maintient le clic droit : la charge fait converger la
  --    lumière (3 paliers d'animation) jusqu'à la naissance de l'étoile.
  local charge, palier, derniere_barre, frames = 0, 1, -1, 0
  while charge < besoin do
    GAME:WaitFrames(1)
    frames = frames + 1
    if M.maintien() then
      charge = math.min(besoin, charge + M.CHARGE_PAR_FRAME)
    else
      charge = math.max(0, charge - 1)
      if frames >= delai_secours then
        charge = besoin
      end
    end
    local nouveau = charge < besoin / 3 and 1 or (charge < besoin * 2 / 3 and 2 or 3)
    if nouveau ~= palier then
      palier = nouveau
      UI:WaitShowBG('quiz_star_lumiere_' .. palier, 4, 6)
    end
    if charge - derniere_barre >= 20 or charge == besoin then
      derniere_barre = charge
      UI:TextPopUp(M.barre(charge, besoin), 60, -1, -1, -1, -1, true, true)
    end
  end

  -- 3. L'étoile forgée s'illumine aux couleurs du type du starter.
  UI:WaitHideBG(6)
  UI:WaitShowBG('quiz_star_' .. element, 4, 8)
  SOUND:PlayFanfare('Fanfare/JoinTeam')
  GAME:WaitFrames(60)

  -- 4. La révélation : nom du Pokémon coloré par son type, avec portrait.
  UI:SetSpeaker(starter.nom, false, starter.espece, starter.forme, '', Gender.Unknown)
  UI:WaitShowDialogue('Quelqu\'un comme toi serait\n'
    .. M.nom_colore(starter.nom, element) .. ' !')
  UI:ResetSpeaker()

  -- 5. La lumière retombe : la scène du rêve revient.
  UI:WaitHideBG(12)
  GAME:FadeIn(30)
  GAME:WaitFrames(30)
end

return M
