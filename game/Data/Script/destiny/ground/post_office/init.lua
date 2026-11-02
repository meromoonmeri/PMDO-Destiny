-- Intérieur town02 raccordé à Réverie Town (Destiny).
-- La sortie sérialisée de la carte ramène devant le bâtiment utilisé.
require 'origin.common'

local post_office = {}
local sortie_en_cours = false

local function sortir()
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.ArriveeVille = 'batiment'
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)
end

function post_office.Init(map) end
function post_office.Enter(map) GAME:FadeIn(20) end
function post_office.GameLoad(map) GAME:FadeIn(20) end
function post_office.Update(map, time) end
function post_office.South_Exit_Touch(obj, activator) sortir() end

local function parler(acteur, texte)
  if acteur == nil then return end
  UI:SetSpeaker(acteur); UI:SetSpeakerEmotion('Normal'); UI:WaitShowDialogue(texte); UI:ResetSpeaker()
end
function post_office.Connect_Owner_Action(chara, activator)
  parler(chara, 'Bienvenue au bureau de poste Bekipan ! Nous portons les lettres et les nouvelles des équipes par-delà les cascades.')
end
function post_office.Rescue_Owner_Action(chara, activator)
  parler(chara, 'Si une équipe appelle au secours dans un donjon, son message finit toujours par arriver jusqu’à ce comptoir.')
end
function post_office.Main_Desk_Action(obj, activator) post_office.Connect_Owner_Action(CH('Connect_Owner'), activator) end
function post_office.Side_Desk_Action(obj, activator) post_office.Rescue_Owner_Action(CH('Rescue_Owner'), activator) end

return post_office
