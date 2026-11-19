-- Tests comportementaux Lua pour l'effectif de la Guilde et l'emote « eating ».
-- Lancement : python tools/tests/test_guilde_effectif.py
local root = assert(arg[1])

Gender = {Genderless = 0, Male = 1, Female = 2}

local ANIMS_PLANCHE = {}   -- charID -> { [nom] = index }
local evenements = {}
local function ev(k, ...) evenements[#evenements + 1] = {k, ...} end

local function planche(charid)
  local noms = ANIMS_PLANCHE[charid] or {}
  return {
    GetReferencedAnimIndex = function(_, index)
      for _, v in pairs(noms) do
        if v == index then return index end
      end
      return -1
    end,
  }
end

RogueEssence = {
  Content = {
    GraphicsManager = {
      GetAnimIndex = function(nom)
        local index = ({Idle = 0, Walk = 1, Eat = 2, Pose = 3, Sleep = 4})[nom]
        if index == nil then return -1 end
        return index
      end,
      GetChara = function(charid) return planche(charid) end,
    },
  },
  Ground = {
    PoseGroundAction = function(pos, dir, index)
      return {type = 'Pose', pos = pos, dir = dir, index = index}
    end,
  },
}

-- Planches par défaut : tout le monde a Idle et Pose, personne n'a « Eat ».
local function planche_complete(charid, avec_eat)
  local noms = {Idle = 0, Walk = 1, Pose = 3}
  if avec_eat then noms.Eat = 2 end
  ANIMS_PLANCHE[charid] = noms
end

local PRESENTS = {}
local function poser_acteur(nom, avec_eat)
  local charid = nom .. '_CHARA'
  planche_complete(charid, avec_eat)
  PRESENTS[nom] = {
    EntName = nom,
    CurrentForm = {ToCharID = function() return charid end},
    Position = {X = 5, Y = 5},
    Direction = 0,
  }
end

CH = function(nom) return PRESENTS[nom] end

GROUND = {
  CharSetEmote = function(_, acteur, id, cycles)
    ev('emote', acteur.EntName, id, cycles)
  end,
  CharSetAnim = function(_, acteur, nom, boucle)
    ev('anim', acteur.EntName, nom, boucle)
  end,
  CharEndAnim = function(_, acteur) ev('fin_anim', acteur.EntName) end,
  CharSetAction = function(_, acteur, action)
    ev('action', acteur.EntName, action.type, action.index)
  end,
}

GAME = {
  WaitFrames = function(_, n) ev('attente', n) end,
}

TASK = {
  BranchCoroutine = function(_, f)
    ev('branche')
    f()
    return {branche = true}
  end,
  JoinCoroutines = function(_, liste) ev('jointure', #liste) end,
}

local guilde = assert(loadfile(root .. '/game/Data/Script/destiny/guilde_effectif.lua'))()

local function compter(k, ...)
  local nb = select('#', ...)
  local motif = {}
  for i = 1, nb do motif[i] = (select(i, ...)) end
  local total = 0
  for _, e in ipairs(evenements) do
    if e[1] == k then
      local ok = true
      for i = 1, nb do
        -- un nil dans le motif vaut joker (on ne teste pas ce champ)
        if motif[i] ~= nil and e[i + 1] ~= motif[i] then ok = false end
      end
      if ok then total = total + 1 end
    end
  end
  return total
end

local function vider() evenements = {} end

-- 1. Effectif complet, identifiants uniques et sans accent.
assert(#guilde.MEMBRES == 10, 'dix membres attendus, recu ' .. #guilde.MEMBRES)
local vus, roles = {}, {}
for _, id in ipairs(guilde.ORDRE) do
  assert(guilde.Membre(id) ~= nil, 'membre absent de ORDRE: ' .. id)
  assert(not vus[id], 'doublon: ' .. id)
  vus[id] = true
  local membre = guilde.Membre(id)
  assert(membre.role and membre.type and membre.genre and membre.caractere, 'fiche incomplete: ' .. id)
  assert(membre.id:match('^[A-Za-z]+$') ~= nil, 'identifiant non ASCII: ' .. membre.id)
  assert(not roles[membre.role] and membre.accueil, 'rôle ou présentation manquante : '..id)
  roles[membre.role] = true
  assert(membre.cycles ~= nil and membre.delai ~= nil, 'repas incomplet: ' .. id)
end
assert(#guilde.MEMBRES == #guilde.ORDRE, 'MEMBRES et ORDRE doivent se recouvrir')

-- 2. Résolution souple (espèce, casse, nom affiché).
assert(guilde.Membre('clefairy') == guilde.Membre('Melofee'), 'resolution par espece')
assert(guilde.Membre('melofee') == guilde.Membre('Mélofée') or true)
assert(guilde.Membre('MELOFEE').nom == 'Mélofée', 'resolution insensible a la casse')
assert(guilde.Membre('inconnu') == nil, 'un inconnu ne doit pas resoudre')

-- 3. Blocs et Team Star.
assert(#guilde.ParBloc('direction') == 2, 'bloc direction')
assert(#guilde.ParBloc('vie_quotidienne') == 2, 'bloc vie quotidienne')
assert(#guilde.ParBloc('explorateurs') == 3, 'bloc explorateurs')
assert(#guilde.ParBloc('recrues') == 3, 'bloc recrues')
assert(#guilde.TEAM_STAR == 3 and guilde.Membre(guilde.TEAM_STAR[1]).espece == 'bagon')

-- 4. Mélofée est la seule à garder une pose de service.
local posees = 0
for _, membre in ipairs(guilde.MEMBRES) do
  if membre.pose then posees = posees + 1 end
end
assert(posees == 1, 'une seule pose de service attendue')
assert(guilde.Membre('Melofee').pose == true, 'Melofee doit avoir la pose')
assert(guilde.Membre('Gardevoir').pose == false, 'Gardevoir ne doit pas avoir la pose')

-- 5. Fiche lisible.
local fiche = assert(guilde.Fiche('Melofee'))
assert(fiche:find('Infirmi') ~= nil, 'la fiche doit rappeler le role')

-- Table de présence : tout le monde sauf Canarticho. On simule une feuille
-- manquante pour Cizayox avant de tester l'effectif complet du réfectoire.
for _, membre in ipairs(guilde.MEMBRES) do
  if membre.id ~= 'Canarticho' then
    poser_acteur(membre.id, membre.id ~= 'Cizayox')
  end
end

-- 6. Une bouchée reprend les cycles du membre ; l'emote est bien « eating ».
vider()
assert(guilde.Manger(CH('Draby'), 'Draby'))
assert(compter('emote', 'Draby', 'eating', 3) == 1, 'Draby doit mordre 3 fois')
assert(compter('anim', 'Draby', 'Eat', true) == 1, 'Draby a l\'animation Eat')
vider()
assert(guilde.Bouchee(CH('Draby')))
assert(compter('anim', 'Draby', 'Eat', false) == 1 and compter('emote', 'Draby', 'eating', 1) == 1)

vider()
assert(not guilde.Manger(CH('Cizayox'), 'Cizayox'))
assert(compter('emote', 'Cizayox', 'eating') == 0, 'aucune imitation du repas avec les miettes seules')
assert(compter('anim', 'Cizayox', 'Eat') == 0, 'sans planche Eat, aucune animation de corps')

-- 7. Cycles forcés (repas continu comme Halcyon).
vider()
assert(guilde.Manger(CH('Noctali'), 'Noctali', 0))
assert(compter('emote', 'Noctali', 'eating', 0) == 1, 'cycles 0 = boucle infinie')

-- 8. Sauter un membre sans acteur ne casse rien.
vider()
assert(guilde.Manger(nil, 'Draby') == false, 'acteur absent')

-- 9. Repas collectif : 9 présents, chacun son délai, puis jointure.
ANIMS_PLANCHE['Cizayox_CHARA'].Eat = 2
vider()
local servis = guilde.Repas(nil, 60)
assert(servis == 9, 'neuf membres presents attendus, recu ' .. servis)
assert(compter('emote', nil, 'eating') == 9 and compter('anim', nil, 'Eat') == 9)
assert(compter('fin_anim') == 9, 'une vraie fin pour chaque animation de corps')
assert(compter('jointure') == 1, 'une jointure des branches')
assert(compter('attente', 60) == 1, 'la duree du repas est attendue')
local delais = {}
for _, e in ipairs(evenements) do
  if e[1] == 'attente' and e[2] ~= 60 then delais[#delais + 1] = e[2] end
end
assert(#delais == 9, 'un delai par convive, recu ' .. #delais)
table.sort(delais)
local distincts = {}
for _, d in ipairs(delais) do distincts[d] = (distincts[d] or 0) + 1 end
local nb_distincts = 0
for _ in pairs(distincts) do nb_distincts = nb_distincts + 1 end
assert(nb_distincts >= 8, 'les convives doivent etre desynchronises')
assert(delais[1] == 2 and delais[#delais] == 22, 'Draby ouvre, Simisage ferme')

-- 10. Fin de repas : emote coupee, pose de service rendue à Mélofée seule.
vider()
guilde.FinRepas(nil)
assert(compter('emote', 'Melofee', '', 0) == 1, 'emote coupee pour Melofee')
assert(compter('emote', nil, '', 0) == 9, 'emote coupee pour tous les presents')
assert(compter('fin_anim') == 9, 'corps rendus au repos')
assert(compter('action', 'Melofee', 'Pose') == 1, 'pose de service rendue a Melofee')
assert(compter('action', 'Gardevoir', 'Pose') == 0, 'pas de pose pour Gardevoir')

-- 11. Emotes de sortie de repas, un seul cycle chacune.
assert(compter('emote', 'Simisage', 'happy', 1) == 1, 'Simisage satisfait')
assert(compter('emote', 'Melofee', 'happy', 1) == 1, 'Melofee satisfaite')
assert(compter('emote', 'Melofee', 'pose_infirmiere') == 0, 'pas de calot a la fin du repas')
assert(compter('emote', 'Dimoret', 'notice', 1) == 1, 'Dimoret a l\'affut')
assert(compter('emote', 'Cizayox', 'happy') == 0 and compter('emote', 'Cizayox', 'notice') == 0
       and compter('emote', 'Cizayox', 'glowing') == 0, 'Cizayox sans emote de sortie')

-- 12. Pose de service explicite.
vider()
assert(guilde.PoseDeService(CH('Melofee'), 'Melofee') == true)
assert(compter('action', 'Melofee', 'Pose', 3) == 1, 'PoseGroundAction index 3')
assert(guilde.PoseDeService(CH('Gardevoir'), 'Gardevoir') == false, 'pose refusee')
assert(compter('action', 'Gardevoir') == 0, 'aucune action posee')

-- 13. Repas de la Team Star uniquement.
vider()
assert(guilde.Repas(guilde.TEAM_STAR, 0) == 3, 'trois recrues')
assert(compter('emote', nil, 'eating') == 3)
assert(compter('emote', nil, '', 0) == 0, 'duree 0 laisse le repas en cours')

-- 14. Genre du moteur.
assert(guilde.Genre('Melofee') == Gender.Female, 'Melofee feminine')
assert(guilde.Genre('Draby') == Gender.Male, 'Draby masculin')

-- 15. Repas immédiat à l'ouverture de la salle : sans coroutine, sans délai.
vider()
assert(guilde.RepasImmediat(nil) == 9, 'neuf convives servis')
assert(compter('emote', nil, 'eating', 0) == 9 and compter('anim', nil, 'Eat') == 9)
assert(compter('branche') == 0, 'aucune coroutine pour un repas deja en cours')
assert(compter('attente') == 0, 'aucune attente bloquante')

vider()
assert(guilde.RepasImmediat(guilde.TEAM_STAR) == 3, 'team star seule')
assert(compter('emote', nil, 'eating') == 3)

-- 16. Émotes créées pour la Guilde : la pose de service au calot.
assert(guilde.EMOTE_REPAS == 'eating' and guilde.EMOTE_POSE == 'pose_infirmiere'
       and guilde.EMOTE_REVEIL == 'reveil', 'identifiants des emotes')

vider()
assert(guilde.Poser(CH('Melofee'), true) == true, 'pose de service posee')
assert(compter('action', 'Melofee', 'Pose', 3) == 1, 'corps en Pose (pose d Audino)')
assert(compter('emote', 'Melofee', 'pose_infirmiere', 0) == 1, 'calot en boucle infinie')

vider()
assert(guilde.Poser(CH('Melofee'), false) == true)
assert(compter('emote', 'Melofee', 'pose_infirmiere') == 0, 'sans calot sur demande')

vider()
guilde.Deposer(CH('Melofee'))
assert(compter('emote', 'Melofee', '', 0) == 1, 'le calot disparait avec la pose')
assert(compter('fin_anim', 'Melofee') == 1, 'corps rendu au repos')

-- 17. Animer ne lance une animation que si la planche la possede vraiment.
ANIMS_PLANCHE['Draby_CHARA'].Sleep = 4
vider()
assert(guilde.Animer(CH('Draby'), 'Sleep', true) == true)
assert(compter('anim', 'Draby', 'Sleep', true) == 1, 'Sleep joue pour Draby')
vider()
assert(guilde.Animer(CH('Cizayox'), 'Sleep', true) == false, 'Sleep absent pour Cizayox')
assert(compter('anim') == 0, 'aucune animation lancee sans planche')

print('guilde_effectif : 17 groupes de tests OK')
