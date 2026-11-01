-- Les tables d'événements sont créées par le moteur et alimentées par origin.
-- Conserver les événements de combat existants sans réinitialiser BATTLE_SCRIPT.
require 'destiny.event_battle'
require 'destiny.mapgen_lost_wood'

-- La table SINGLE_CHAR_SCRIPT est créée par le moteur : ne pas la remplacer.
local lecons = {
  {
    "Premier étage de [color=#69D98C]Lost Wood[color] ! Je me déplace avec les directions et je cherche l'escalier.",
    "Chaque déplacement ou action prend un tour : les autres Pokémon peuvent agir aussi. Par défaut, je me déplace avec les flèches."
  },
  {
    "Un adversaire ! Pour attaquer tout près, j'utilise la commande d'attaque : X par défaut. Q ouvre le menu des capacités.",
    "Mes capacités consomment des PP. Mieux vaut garder assez de force pour la suite ! Les touches peuvent être modifiées dans les options."
  },
  {
    "Si je ramasse un objet, je le retrouve dans mon sac. W ouvre le menu des objets par défaut ; je peux ensuite choisir quoi utiliser.",
    "Une baie peut me soigner ; d'autres objets ont des effets différents. Je lis leur description avant de les employer."
  },
  {
    "Je dois aussi surveiller mon ventre : il se vide pendant l'exploration.",
    "Si je trouve de la nourriture, comme une pomme, je peux la manger depuis le sac pour tenir plus longtemps."
  },
  {
    "Un ennemi peut m'infliger un changement d'état. Je fais attention à mes PV et aux effets qui apparaissent.",
    "Je peux profiter des couloirs, garder mes distances ou contourner un combat au lieu de foncer."
  },
  {
    "Si je suis en difficulté, je peux me soigner ou utiliser un objet avant qu'il ne soit trop tard.",
    "En cas de KO ou d'abandon, je reviendrai à l'entrée. Je pourrai reprendre mon souffle et réessayer."
  },
  {
    "C'est le septième étage ! Je cherche encore l'escalier pour atteindre le fond de la forêt.",
    "Je surveille mes PV, mon ventre et mes PP… et je garde mes objets utiles à portée de main. En avant !"
  }
}

function SINGLE_CHAR_SCRIPT.DestinyLostWoodLesson(owner, ownerChar, context, args)
  if context == nil or context.User == nil or args == nil then return end
  if context.User ~= GAME:GetPlayerPartyMember(GAME:GetTeamLeaderIndex()) then return end
  if not SV.Destiny or SV.Destiny.LostWoodTrip ~= 'aller' then return end
  local etage = tonumber(args.Etage)
  if etage == nil or lecons[etage] == nil then return end
  SV.Destiny.LostWoodLessonsSeen = SV.Destiny.LostWoodLessonsSeen or {}
  local cle = tostring(etage)
  if SV.Destiny.LostWoodLessonsSeen[cle] then return end

  -- OnMapStarts est déclenché pour chaque personnage ; comme dans le modèle
  -- de leçons, on ne programme qu'une seule coroutine pour le meneur.
  GAME:QueueLeaderEvent(function()
    if SV.Destiny.LostWoodLessonsSeen[cle] then return end
    GAME:WaitFrames(15)
    UI:SetSpeaker(context.User)
    UI:SetSpeakerEmotion('Normal')
    for _, texte in ipairs(lecons[etage]) do UI:WaitShowDialogue(texte) end
    UI:ResetSpeaker()
    -- Marquer après la dernière page : une interruption ne perd pas la leçon.
    SV.Destiny.LostWoodLessonsSeen[cle] = true
    if etage == 7 then SV.Destiny.LostWoodTutorialDone = true end
    GAME:WaitFrames(10)
  end)
end
