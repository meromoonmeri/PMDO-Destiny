-- Réverie Town : arrivée après Lost Wood et présentation des lieux existants.
-- La carte et ses calques restent ceux de l'utilisateur ; les habitants sont
-- créés à l'exécution pour ne pas réécrire le ground d'origine.
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'

local ville = {}
local ENTREE_X, ENTREE_Y = 800, 1320
local PLACE_X, PLACE_Y = 800, 1160

local function habitant(nom, espece, genre, x, y)
  local acteur = CH(nom)
  if acteur == nil then
    local donnees = RogueEssence.Dungeon.CharData()
    donnees.BaseForm = RogueEssence.Dungeon.MonsterID(espece, 0, 'normal', genre)
    donnees.Nickname = nom
    donnees.Level = 5
    acteur = GROUND:CreateCharacterFromCharData(nom, RogueEssence.Dungeon.Character(donnees), x, y, Direction.Down)
  end
  AI:DisableCharacterAI(acteur)
  acteur:ReloadEvents()
  return acteur
end

local function partenaire_pour(hero)
  local partenaire = CH('Teammate1')
  if partenaire == nil and hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    partenaire = equipe_scene.Partenaire(hero.Position.X + 24, hero.Position.Y, Direction.Down)
  end
  return partenaire
end

function ville.Init(map)
  map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  habitant('Kecleon', 'kecleon', Gender.Male, 616, 948)
  habitant('Kangourex', 'kangaskhan', Gender.Female, 936, 964)
  partenaire_pour(CH('PLAYER'))
end

local function parler(personnage, emotion, texte)
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion(emotion)
  UI:WaitShowDialogue(texte)
end

local function penser_heros(personnage, emotion, texte)
  UI:SetSpeaker(personnage, false)
  UI:SetSpeakerEmotion(emotion)
  UI:WaitShowDialogue(texte)
end

local function retour_au_joueur(hero, partenaire)
  if hero ~= nil then hero.CollisionDisabled = false end
  GAME:MoveCamera(0, 0, 45, true)
  if hero ~= nil and partenaire ~= nil then equipe_scene.Suivre(partenaire, hero) end
  GAME:CutsceneMode(false)
end

function ville.Visite()
  local hero = CH('PLAYER')
  local partenaire = partenaire_pour(hero)
  if hero == nil or partenaire == nil then
    -- Ne pas marquer la visite comme terminée si l'équipe est incomplète.
    GAME:FadeIn(20)
    print('[Destiny] Visite de la ville suspendue : partenaire absent de l’équipe.')
    return
  end
  local kecleon, kangourex = CH('Kecleon'), CH('Kangourex')
  GAME:CutsceneMode(true)
  hero.CollisionDisabled = true
  AI:DisableCharacterAI(partenaire)
  GROUND:TeleportTo(hero, ENTREE_X - 8, ENTREE_Y, Direction.Up)
  GROUND:TeleportTo(partenaire, ENTREE_X + 12, ENTREE_Y - 20, Direction.Up)
  GAME:MoveCamera(ENTREE_X, ENTREE_Y - 30, 1, false)
  SOUND:PlayBGM('Base Town.ogg', true)
  GAME:FadeIn(45)

  parler(partenaire, 'Happy', 'Nous y voilà ! Bienvenue à [color=#F5D27A]Réverie Town[color].')
  parler(partenaire, 'Normal', 'Le jour se lève. Reste avec moi : je vais te montrer les endroits importants.')
  penser_heros(hero, 'Normal', '(Après cette nuit mouvementée, je suis content de ne pas arriver ici tout seul.)')

  -- Le partenaire guide le héros vers la place, tous deux à pied ; la caméra
  -- les accompagne plutôt que de téléporter les personnages au milieu du plan.
  local avance_partenaire = TASK:BranchCoroutine(function()
    GROUND:MoveToPosition(partenaire, PLACE_X + 12, PLACE_Y - 8, false, 1.5)
  end)
  local avance_hero = TASK:BranchCoroutine(function()
    GAME:WaitFrames(12)
    GROUND:MoveToPosition(hero, PLACE_X - 8, PLACE_Y + 12, false, 1.5)
  end)
  local suivi = TASK:BranchCoroutine(function() GAME:MoveCamera(PLACE_X, PLACE_Y + 20, 100, false) end)
  TASK:JoinCoroutines({avance_partenaire, avance_hero, suivi})
  GROUND:CharAnimateTurnTo(partenaire, Direction.Up, 8)
  GROUND:CharAnimateTurnTo(hero, Direction.Up, 8)
  parler(partenaire, 'Happy', 'Voici la place. Les chemins, les ponts et les boutiques se rejoignent ici.')

  GAME:MoveCamera(616, 925, 90, false)
  parler(partenaire, 'Normal', 'Là-bas, c’est la boutique de Kecleon. On peut y acheter des provisions pour les expéditions.')
  if kecleon ~= nil then parler(kecleon, 'Happy', 'Bienvenue ! Une pomme ou une baie peut toujours être utile en chemin.') end
  penser_heros(hero, 'Happy', '(Je penserai à vérifier notre sac avant de repartir.)')

  GAME:MoveCamera(936, 940, 100, false)
  parler(partenaire, 'Happy', 'Et voici Tatie Kangourex, dont je te parlais sur la falaise ! Elle garde aussi nos affaires en sécurité.')
  if kangourex ~= nil then parler(kangourex, 'Happy', 'Te voilà de retour ! Confiez-moi vos affaires et revenez les chercher quand vous voudrez.') end
  penser_heros(hero, 'Normal', '(Comme ça, nous n’avons pas besoin de tout porter dans le donjon.)')

  GAME:MoveCamera(1100, 950, 75, false)
  parler(partenaire, 'Happy', 'Juste à côté, il y a aussi cet étal aux couleurs vives. Le quartier du marché est plein de surprises !')
  GAME:MoveCamera(500, 1010, 110, false)
  parler(partenaire, 'Normal', 'Et de l’autre côté de la place, d’autres comptoirs nous attendent. Nous aurons le temps de les découvrir ensemble.')
  GAME:MoveCamera(530, 2350, 200, false)
  parler(partenaire, 'Happy', 'Plus au sud, les chemins passent devant les maisons. C’est un coin tranquille, entouré d’arbres.')
  GAME:MoveCamera(800, 530, 240, false)
  parler(partenaire, 'Normal', 'Regarde les ponts et les cascades : ils relient les différents quartiers de la ville.')
  GAME:MoveCamera(1425, 320, 135, false)
  parler(partenaire, 'Happy', 'Et ce grand bâtiment, là-haut… un jour, nous irons voir ce qui nous attend de ce côté !')
  GAME:MoveCamera(PLACE_X, PLACE_Y, 135, false)
  penser_heros(hero, 'Happy', '(Je ne me souviens toujours pas de mon passé, mais je crois que je commence à trouver mes repères.)')
  parler(partenaire, 'Happy', 'Tu n’as pas besoin de tout retenir d’un coup. On explorera la ville et les alentours à notre rythme.')
  parler(partenaire, 'Normal', 'Pour l’instant, reposons-nous. Notre prochaine aventure commencera quand nous serons prêts.')

  SV.Destiny.VisiteVille = 'terminee'
  UI:ResetSpeaker()
  retour_au_joueur(hero, partenaire)
end

local function entrer()
  SV.Destiny = SV.Destiny or {}
  if SV.Destiny.VisiteVille == 'en_route' then
    ville.Visite()
    return
  end
  local hero = CH('PLAYER')
  if hero ~= nil and hero.Position.X == 0 and hero.Position.Y == 0 then
    -- Le ground natif ne contient pas de marqueur d'entrée.
    GROUND:TeleportTo(hero, PLACE_X, PLACE_Y, Direction.Up)
  end
  local partenaire = partenaire_pour(hero)
  SOUND:PlayBGM('Base Town.ogg', true)
  GAME:FadeIn(20)
  retour_au_joueur(hero, partenaire)
end

function ville.Enter(map) entrer() end
function ville.GameLoad(map) entrer() end
function ville.Exit(map) end
function ville.Update(map, time) end

-- Les habitants sont visibles pendant la visite et restent utilisables après.
function ville.Kangourex_Action(personnage, activator)
  COMMON.ShowTeamStorageMenu()
end

-- Petit assortiment de départ : menus, argent et sac sont ceux de PMDO.
local articles = {
  {nom = 'Pomme', id = 'food_apple', prix = 50},
  {nom = 'Baie Oran', id = 'berry_oran', prix = 80},
  {nom = 'Baie Mepo', id = 'berry_leppa', prix = 80},
}
function ville.Kecleon_Action(personnage, activator)
  UI:SetSpeaker(personnage)
  UI:SetSpeakerEmotion('Happy')
  while true do
    local choix = {}
    for _, article in ipairs(articles) do choix[#choix + 1] = article.nom .. ' — ' .. article.prix .. ' Poké' end
    choix[#choix + 1] = 'Quitter'
    UI:BeginChoiceMenu('Bienvenue ! Que souhaitez-vous acheter ?', choix, 1, #choix)
    UI:WaitForChoice()
    local selection = UI:ChoiceResult()
    local article = articles[selection]
    if article == nil then break end
    if GAME:GetPlayerMoney() < article.prix then
      UI:WaitShowDialogue('Il vous manque un peu d’argent pour cet objet.')
    elseif GAME:GetPlayerBagCount() >= GAME:GetPlayerBagLimit() then
      UI:WaitShowDialogue('Votre sac est plein. Faites un peu de place avant de revenir.')
    else
      UI:ChoiceMenuYesNo('Acheter ' .. article.nom .. ' pour ' .. article.prix .. ' Poké ?', true)
      UI:WaitForChoice()
      if UI:ChoiceResult() then
        GAME:GivePlayerItem(article.id, 1)
        GAME:RemoveFromPlayerMoney(article.prix)
        UI:WaitShowDialogue('Merci ! Prenez soin de vous sur les chemins.')
      end
    end
  end
  UI:ResetSpeaker()
end

return ville
