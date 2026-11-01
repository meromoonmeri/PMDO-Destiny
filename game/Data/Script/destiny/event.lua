-- Les tables d'événements sont créées par le moteur et alimentées par origin.
-- Conserver les événements de combat existants sans réinitialiser BATTLE_SCRIPT.
require 'destiny.event_battle'
require 'destiny.mapgen_lost_wood'

-- La table SINGLE_CHAR_SCRIPT est créée par le moteur : ne pas la remplacer.
-- Les repères ci-dessous sont des pages d'aide neutres : aucun personnage
-- ne les prononce et aucun portrait ne les accompagne. Les libellés de
-- touches sont relus au moment de l'affichage afin de suivre les réglages
-- du joueur plutôt qu'une disposition de clavier supposée.
local function touche(index, defaut)
  local libelle = defaut
  local ok, resultat = pcall(function() return STRINGS:LocalKeyString(index) end)
  if ok and type(resultat) == 'string' and resultat ~= '' then
    libelle = resultat
  end
  return '[color=#FFE16A]' .. libelle .. '[color]'
end

local function lecon(etage)
  local confirmer = touche(0, 'Confirmer')
  local annuler = touche(1, 'Annuler')
  local attaque = touche(2, 'Attaque')
  local orientation = touche(5, 'Orientation')
  local diagonale = touche(6, 'Diagonale')
  local minicarte = touche(8, 'Minicarte')
  local journal = touche(10, 'Journal')
  local capacites = touche(11, 'Capacités')
  local objets = touche(12, 'Objets')
  local equipe = touche(14, 'Équipe')
  local pages = {
    [1] = {
      "[color=#8FE3FF]Repère d’exploration[color] — Objectif : atteindre l’escalier. Chaque pas, chaque attaque et chaque objet employé consomme un tour ; les Pokémon sauvages n’agissent qu’ensuite.",
      "Déplacez-vous dans les huit directions et observez la salle avant d’agir. Tant qu’aucune action n’est choisie, le donjon demeure en suspens. " .. confirmer .. " valide ; " .. annuler .. " annule."
    },
    [2] = {
      "[color=#8FE3FF]Repère d’exploration[color] — À une case d’un adversaire, " .. attaque .. " lance l’attaque ordinaire. " .. capacites .. " ouvre les techniques, avec leur portée, leurs effets et leurs PP restants.",
      "Une capacité puissante dépensée trop tôt peut manquer dans la salle suivante. Choisissez l’outil juste pour chaque rencontre et ménagez vos PP pour les passages délicats."
    },
    [3] = {
      "[color=#8FE3FF]Repère d’exploration[color] — Les objets ramassés rejoignent le sac. " .. objets .. " permet de les examiner, puis de les utiliser, les donner, les lancer ou les déposer selon leur nature.",
      "Baies, graines, orbes, baguettes et projectiles ne répondent pas au même besoin. Leur description dit l’essentiel : la lire avant d’agir évite de gaspiller une ressource rare."
    },
    [4] = {
      "[color=#8FE3FF]Repère d’exploration[color] — La satiété diminue au fil des tours. Lorsqu’elle atteint zéro, les PV s’épuisent peu à peu jusqu’au repas ou jusqu’au K.O.",
      "Une pomme ou tout autre aliment consommé depuis le sac prolonge l’expédition. Manger avant l’urgence laisse le choix du moment ; attendre le dernier tour le retire."
    },
    [5] = {
      "[color=#8FE3FF]Repère d’exploration[color] — Poison, sommeil, paralysie et autres altérations peuvent renverser un affrontement. Surveillez les effets annoncés autant que la jauge de PV.",
      "Le terrain est une défense : un couloir limite les assaillants qui peuvent vous atteindre. " .. orientation .. " change de direction sans avancer ; " .. diagonale .. " restreint le déplacement aux diagonales."
    },
    [6] = {
      "[color=#8FE3FF]Repère d’exploration[color] — PV bas, PP rares et satiété presque vide sont des signaux concordants. " .. equipe .. " permet de relire l’état de l’expédition avant de décider.",
      "Soignez, mangez ou employez un objet pendant qu’il reste une marge. Un K.O. ramène à l’entrée ; savoir interrompre une tentative, c’est aussi préparer la suivante."
    },
    [7] = {
      "[color=#8FE3FF]Repère d’exploration[color] — Dernier étage. Avant de quitter une salle, vérifiez PV, PP, satiété et objets décisifs ; le fond de la forêt ne récompense ni la précipitation ni l’oubli.",
      minicarte .. " change l’affichage de la carte et " .. journal .. " rouvre les actions récentes. Cherchez l’escalier méthodiquement : une salle relue vaut mieux qu’un couloir traversé au hasard."
    },
  }
  return pages[etage]
end

function SINGLE_CHAR_SCRIPT.DestinyLostWoodLesson(owner, ownerChar, context, args)
  if context == nil or context.User == nil or args == nil then return end
  if context.User ~= GAME:GetPlayerPartyMember(GAME:GetTeamLeaderIndex()) then return end
  if not SV.Destiny or SV.Destiny.LostWoodTrip ~= 'aller' then return end
  local etage = tonumber(args.Etage)
  if etage == nil or lecon(etage) == nil then return end
  SV.Destiny.LostWoodLessonsSeen = SV.Destiny.LostWoodLessonsSeen or {}
  local cle = tostring(etage)
  if SV.Destiny.LostWoodLessonsSeen[cle] then return end

  -- OnMapStarts est déclenché pour chaque personnage ; comme dans le modèle
  -- de leçons, on ne programme qu'une seule coroutine pour le meneur.
  GAME:QueueLeaderEvent(function()
    if SV.Destiny.LostWoodLessonsSeen[cle] then return end
    GAME:WaitFrames(15)
    -- Aucun locuteur : la page d'aide appartient au donjon, pas au meneur.
    UI:ResetSpeaker()
    for _, texte in ipairs(lecon(etage)) do UI:WaitShowDialogue(texte) end
    UI:ResetSpeaker()
    -- Marquer après la dernière page : une interruption ne perd pas la leçon.
    SV.Destiny.LostWoodLessonsSeen[cle] = true
    if etage == 7 then SV.Destiny.LostWoodTutorialDone = true end
    GAME:WaitFrames(10)
  end)
end
