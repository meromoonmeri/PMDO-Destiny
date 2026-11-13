--[[ init.lua — Intro « halo arc-en-ciel » (map intro_halo)
     Chaîne de démarrage de la quest PMD Destiny, après le choix de la
     langue puis « Nouvelle partie » :
       Data/StartParams.xml → zone personality_test, ground 1 = intro_halo ;
       cette map (fonds Halo_Destiny_*.dir) joue l'intro : le fond, les
       anneaux, les rayons et les particules reprennent les textures de
       l'aperçu retrouvé. Un voile anime la respiration sur 240 images
       pendant les titres en voix-off blanche ; puis le fondu blanc
       conduit à personality_test (le quiz). La cinématique et la
       transition ont été vérifiées dans le moteur PMDO 0.8.12.
]]

require 'origin.common'

local intro_halo = {}

-- ------------------------------------------------------------- map callbacks

local tick_halo = 0
local generation_halo = 0
local function regler_halo(map)
  if map == nil or map.Background == nil then return end
  local couches = map.Background.Layers
  if couches == nil or couches.Count < 4 then return end
  local pulse = 0.5 - 0.5 * math.cos(2 * math.pi * tick_halo / 240)
  local entree = tick_halo < 60 and (1 - tick_halo / 60) or 0
  local voile = math.max(entree, 1 - pulse)
  couches[3].BG.BGAnim.Alpha = math.floor(255 * voile + 0.5)
  couches[2].BG.BGAnim.Alpha = math.floor(math.min(255, tick_halo * 8 / 3) + 0.5)
end
local function demarrer_halo(map)
  generation_halo = generation_halo + 1
  local generation = generation_halo
  tick_halo = 0
  regler_halo(map)
  -- Update(map) n'est pas appelé pendant une cinématique bloquée sur une
  -- voix-off : cette coroutine anime donc le halo même pendant les textes.
  TASK:BranchCoroutine(function()
    while generation == generation_halo do
      tick_halo = tick_halo + 1
      regler_halo(map)
      GAME:WaitFrames(1)
    end
  end)
end
function intro_halo.Init(map)
  tick_halo = 0
  regler_halo(map)
end

function intro_halo.Enter(map)
  demarrer_halo(map)
  intro_halo.Scene()
end

function intro_halo.Exit(map)
  generation_halo = generation_halo + 1
end

function intro_halo.Update(map)
end

function intro_halo.GameSave(map)
end

function intro_halo.GameLoad(map)
  demarrer_halo(map)
  intro_halo.Scene()
end

-- --------------------------------------------------------------- scène

function intro_halo.Scene()
  GAME:CutsceneMode(true)
  -- Le personnage technique de la nouvelle partie ne doit pas apparaître
  -- sur le texte ni au milieu du halo. La carte suivante recrée son joueur.
  GROUND:Hide('PLAYER')
  UI:ResetSpeaker()
  GAME:FadeOut(false, 1)
  GAME:WaitFrames(30)

  -- Le halo respire continuellement sous les textes, comme dans l’aperçu.
  GAME:FadeIn(60)
  UI:WaitShowVoiceOver("Bienvenue dans le monde des Pokémon !", -1)

  UI:WaitShowVoiceOver("Devant toi s'étend un monde rempli d'aventures\npalpitantes et de mystères à découvrir !", -1)
  UI:WaitShowVoiceOver("Avant de partir, tu dois prendre\nd'importantes décisions.", -1)

  UI:WaitShowVoiceOver("Réfléchis bien avant de choisir !", -1)
  UI:WaitShowVoiceOver("À toi de faire tes choix !", -1)
  GAME:WaitFrames(40)

  -- transition dans le halo : fondu blanc (aspiré par la lumière),
  -- puis arrivée sur le test de personnalité (fond « dream »)
  GAME:FadeOut(true, 60)
  GAME:WaitFrames(20)
  generation_halo = generation_halo + 1
  GAME:CutsceneMode(false)
  GAME:EnterGroundMap('personality_test', 'Main_Entrance_Marker')
end

return intro_halo
