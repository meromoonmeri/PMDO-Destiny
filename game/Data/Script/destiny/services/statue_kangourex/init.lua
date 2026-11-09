-- Une statue choisie dans les objets de l'éditeur devient un stockage sans
-- script de carte à écrire. Les callbacks déjà présents restent utilisables.
require 'origin.common'
require 'origin.services.baseservice'

local StatueKangourex = Class('StatueKangourex', BaseService)
local ASSET = 'Statue_Kangourex'

function StatueKangourex:initialize()
  BaseService.initialize(self)
  -- Sert à reconnaître nos propres enveloppes en cas de réinitialisation.
  self.wrappers = setmetatable({}, { __mode = 'k' })
  self.serial = 0
end

-- LuaEngine résout les noms d'entités point par point (CURMAPSCR.nom_Action).
-- Conserver aussi les noms contenant des points, sans modifier la carte.
local function emplacement(nom, evenement)
  if type(nom) ~= 'string' or nom == '' or nom:sub(1, 1) == '.'
      or nom:sub(-1) == '.' or nom:find('..', 1, true) then return nil end
  local morceaux = {}
  for morceau in nom:gmatch('[^.]+') do morceaux[#morceaux + 1] = morceau end
  local table_courante = CURMAPSCR
  for i = 1, #morceaux - 1 do
    local morceau = morceaux[i]
    if table_courante[morceau] == nil then table_courante[morceau] = {} end
    if type(table_courante[morceau]) ~= 'table' then return nil end
    table_courante = table_courante[morceau]
  end
  return table_courante, morceaux[#morceaux] .. '_' .. evenement
end

function StatueKangourex:Installer(objet, carte)
  if objet.ObjectAnim == nil or objet.ObjectAnim.AnimIndex ~= ASSET then return end
  if CURMAPSCR == nil then CURMAPSCR = {} end -- carte sans script

  local triggers = RogueEssence.Ground.GroundEntity.EEntityTriggerTypes
  local type_declencheur = objet:GetTriggerType()
  if type_declencheur == triggers.None then
    -- L'éditeur crée par défaut les objets avec le déclencheur « Aucun ».
    objet:SetTriggerType(triggers.Action)
    type_declencheur = triggers.Action
  end
  local evenement = type_declencheur == triggers.Action and 'Action' or 'Touch'
  local table_action, cle = emplacement(objet.EntName, evenement)
  -- Un nom vide ou impossible à résoudre ne peut pas avoir de callback moteur.
  -- Donner uniquement à cette instance un nom de secours pour la session.
  if table_action == nil or (table_action[cle] ~= nil and type(table_action[cle]) ~= 'function') then
    local nom_auto
    repeat
      self.serial = self.serial + 1
      nom_auto = 'DestinyKangourexAuto' .. tostring(self.serial)
    until CURMAPSCR[nom_auto .. '_' .. evenement] == nil and carte:GetObj(nom_auto) == nil
    objet.EntName = nom_auto
    table_action, cle = emplacement(nom_auto, evenement)
  end

  local precedent = table_action[cle]
  if not self.wrappers[precedent] then
    local wrapper = function(cible, activator)
      -- Si une autre entité partage ce nom, son ancien comportement reste
      -- intact. Si la statue possédait déjà un script, il s'exécute aussi.
      if precedent ~= nil then precedent(cible, activator) end
      if cible:GetEntityType() == RogueEssence.Ground.GroundEntity.EEntTypes.Object
          and cible.ObjectAnim ~= nil and cible.ObjectAnim.AnimIndex == ASSET then
        COMMON.ShowTeamStorageMenu()
      end
    end
    table_action[cle] = wrapper
    self.wrappers[wrapper] = true
  end

  -- Recharger après avoir ajouté le callback, sans réglage manuel.
  objet:ReloadEvents()
end

function StatueKangourex:OnGroundMapInit(carte)
  if carte == nil then return end
  for i = 0, carte.Entities.Count - 1 do
    local objets = carte.Entities[i].GroundObjects
    for j = 0, objets.Count - 1 do self:Installer(objets[j], carte) end
  end
end

function StatueKangourex:Subscribe(med)
  med:Subscribe('StatueKangourex', EngineServiceEvents.GroundMapInit, function(_, args)
    if args ~= nil then self:OnGroundMapInit(args[1]) end
  end)
end

function StatueKangourex:UnSubscribe(med)
  med:UnSubscribe('StatueKangourex', EngineServiceEvents.GroundMapInit)
end

local instance = StatueKangourex:new()
SCRIPT:AddService('StatueKangourex', instance)
return instance
