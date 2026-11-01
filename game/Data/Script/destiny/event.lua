-- Les tables d'événements sont créées par le moteur et alimentées par origin.
-- Conserver les événements de combat existants sans réinitialiser BATTLE_SCRIPT.
require 'destiny.event_battle'

-- Au retour en duo (7F -> 1F), les escaliers deviennent des escaliers montants
-- ramenant à l'étage précédent ; au 1er étage (ID 0 + (-1) < 0), ils font sortir
-- l'équipe avec ResultType.Cleared.
function DestinyInverserEscaliersLostWood(carte)
  if carte == nil or RogueElements == nil or RogueEssence == nil or PMDC == nil then return end
  if RogueEssence.Dungeon == nil or PMDC.Dungeon == nil then return end
  for xx = 0, carte.Width - 1 do
    for yy = 0, carte.Height - 1 do
      local loc = RogueElements.Loc(xx, yy)
      local tl = carte:GetTile(loc)
      if tl ~= nil and tl.Effect ~= nil and (tl.Effect.ID == 'stairs_go_down' or tl.Effect.ID == 'stairs_go_up') then
        local sec_loc = RogueEssence.Dungeon.SegLoc(0, -1)
        local dest_state = PMDC.Dungeon.DestState(sec_loc, true)
        dest_state.PreserveMusic = true
        tl.Effect.TileStates:Set(dest_state)
        tl.Effect.ID = 'stairs_back_up'
      end
    end
  end
end

require 'destiny.mapgen_lost_wood'

local function touche(index, defaut)
  if STRINGS ~= nil and STRINGS.LocalKeyString ~= nil then
    local ok, val = pcall(function() return STRINGS:LocalKeyString(index) end)
    if ok and val ~= nil and val ~= '' then return val end
  end
  return defaut
end

local function construire_lecons_aller()
  return {
    [1] = {
      "Cherchez les escaliers pour progresser dans [color=#69D98C]Lost Wood[color] ! L'exploration se déroule au tour par tour : les ennemis n'agissent que lorsque vous bougez ou agissez.",
      "Appuyez sur " .. touche(2, "[Attaque]") .. " pour lancer une attaque directe devant vous, " .. touche(0, "[Confirmer]") .. " pour valider vos choix et " .. touche(1, "[Annuler]") .. " pour annuler."
    },
    [2] = {
      "Pour remporter des points d'expérience face à un ennemi, utilisez au moins une capacité plutôt que la seule attaque de base (" .. touche(2, "[Attaque]") .. ").",
      "Maintenez " .. touche(4, "[Capacités]") .. " pour utiliser vos raccourcis, ou ouvrez le menu des capacités avec " .. touche(11, "[Menu Capacités]") .. " (ou via " .. touche(9, "[Menu]") .. "). Surveillez vos PP !"
    },
    [3] = {
      "Vous pouvez transporter divers objets aux effets variés (soin, lancer, soutien…) dans le sac de l'équipe.",
      "Appuyez sur " .. touche(12, "[Sac]") .. " pour accéder directement à vos objets, ou passez par l'option Objets du menu principal (" .. touche(9, "[Menu]") .. ")."
    },
    [4] = {
      "Votre estomac se vide peu à peu au fil des pas. S'il tombe à zéro, vous perdrez progressivement des PV jusqu'à manger ou tomber KO !",
      "Pensez à manger une Pomme ou une Gelée depuis votre sac dès que la faim se fait sentir."
    },
    [5] = {
      "Maintenez " .. touche(3, "[Courir]") .. " pour courir : cela ne consomme pas moins de tours, mais accélère vos déplacements dans les couloirs.",
      "Maintenez " .. touche(5, "[Tourner]") .. " pour regarder autour de vous sans passer votre tour, ou " .. touche(6, "[Diagonale]") .. " pour ne bouger qu'en diagonale."
    },
    [6] = {
      "Certains ennemis peuvent infliger des altérations d'état. Profitez des couloirs, gardez vos distances ou utilisez une baie adaptée pour vous soigner.",
      "En cas de KO ou d'abandon depuis le menu (" .. touche(9, "[Menu]") .. "), vous regagnerez l'entrée de la forêt et pourrez réessayer."
    },
    [7] = {
      "Dernier étage de cette première traversée ! Vérifiez vos PV, vos PP et votre estomac avant d'avancer.",
      "Trouvez l'escalier pour atteindre la sortie de [color=#69D98C]Lost Wood[color] !"
    },
  }
end

local function construire_lecons_retour()
  return {
    [7] = {
      "Vous retraversez [color=#69D98C]Lost Wood[color] en sens inverse, du 7e jusqu'au 1er étage : empruntez les escaliers montants pour regagner la sortie !",
      "Surveillez les PV des deux coéquipiers en haut de l'écran : si l'un de vous deux tombe KO, toute l'équipe est renvoyée hors du donjon."
    },
    [6] = {
      "Toute l'équipe reçoit des points d'expérience lorsqu'un ennemi est vaincu. Avec assez d'expérience, un Pokémon monte de niveau !",
      "Chaque montée de niveau renforce les PV et les statistiques, et permet parfois d'apprendre une nouvelle capacité."
    },
    [5] = {
      "Votre partenaire agit de lui-même selon sa tactique actuelle.",
      "Appuyez sur " .. touche(13, "[Tactiques]") .. " (ou ouvrez " .. touche(9, "[Menu]") .. " puis Tactiques) pour ajuster le comportement de votre coéquipier."
    },
    [4] = {
      "Avancer vers un coéquipier permet d'échanger votre place avec lui, très pratique dans les couloirs étroits.",
      "Si vous préférez le pousser devant vous sans échanger de place, maintenez " .. touche(1, "[Annuler]") .. " en avançant dans sa direction."
    },
    [3] = {
      "Le saviez-vous ? Vous pouvez choisir vous-même l'action de chaque membre de l'équipe à chaque tour grâce au Mode Équipe !",
      "Appuyez sur " .. touche(7, "[Mode Équipe]") .. " pour activer ou désactiver le Mode Équipe à tout moment."
    },
    [2] = {
      "Appuyez sur " .. touche(10, "[Journal]") .. " pour consulter l'historique des dernières actions en combat.",
      "Vous pouvez aussi changer le mode de la mini-carte avec " .. touche(8, "[Mini-carte]") .. " et inspecter l'état de l'équipe avec " .. touche(14, "[Équipe]") .. "."
    },
    [1] = {
      "Pour modifier les touches, la vitesse de jeu ou l'affichage de la fenêtre, ouvrez " .. touche(9, "[Menu]") .. " puis le menu Autres.",
      "Premier étage atteint : prenez ce dernier escalier pour sortir de [color=#69D98C]Lost Wood[color] !"
    },
  }
end

-- La table SINGLE_CHAR_SCRIPT est créée par le moteur : ne pas la remplacer.
-- Tutoriel neutre façon Halcyon : aucun personnage ne parle (UI:ResetSpeaker),
-- jingle Fanfare/Note, conseils à l'aller (1F->7F) puis au retour en duo (7F->1F).
function SINGLE_CHAR_SCRIPT.DestinyLostWoodLesson(owner, ownerChar, context, args)
  if context == nil or context.User == nil or args == nil then return end
  if context.User ~= GAME:GetPlayerPartyMember(GAME:GetTeamLeaderIndex()) then return end
  if not SV.Destiny then return end

  local trajet = SV.Destiny.LostWoodTrip
  if trajet == 'retour' and _ZONE ~= nil and _ZONE.CurrentMap ~= nil then
    DestinyInverserEscaliersLostWood(_ZONE.CurrentMap)
  end

  local etage = tonumber(args.Etage)
  if etage == nil then return end

  local pages, cle
  if trajet == 'aller' then
    pages = construire_lecons_aller()[etage]
    cle = tostring(etage)
  elseif trajet == 'retour' then
    pages = construire_lecons_retour()[etage]
    cle = 'retour_' .. tostring(etage)
  else
    return
  end
  if pages == nil then return end

  SV.Destiny.LostWoodLessonsSeen = SV.Destiny.LostWoodLessonsSeen or {}
  if SV.Destiny.LostWoodLessonsSeen[cle] then return end

  -- OnMapStarts est déclenché pour chaque personnage ; on ne programme qu'une
  -- seule coroutine pour le meneur.
  GAME:QueueLeaderEvent(function()
    if SV.Destiny.LostWoodLessonsSeen[cle] then return end
    GAME:WaitFrames(15)
    UI:ResetSpeaker()
    if SOUND ~= nil and SOUND.PlayFanfare ~= nil then
      SOUND:PlayFanfare('Fanfare/Note')
    end
    for _, texte in ipairs(pages) do UI:WaitShowDialogue(texte) end
    UI:ResetSpeaker()
    -- Marquer après la dernière page : une interruption ne perd pas la leçon.
    SV.Destiny.LostWoodLessonsSeen[cle] = true
    if trajet == 'aller' and etage == 7 then SV.Destiny.LostWoodTutorialDone = true end
    if trajet == 'retour' and etage == 1 then SV.Destiny.LostWoodReturnTutorialDone = true end
    GAME:WaitFrames(15)
  end)
end
