--[[
    debugger.lua — surcharge Destiny sécurisée lorsque la bibliothèque native 'socket.core'
    (ZeroBrane / LuaSocket C) est absente de l'environnement d'exécution PMDO.
]]--
DEBUG =
{
  EnableDbgCoro = function() end,
  IsDevMode = function()
    return RogueEssence ~= nil and RogueEssence.DiagManager ~= nil
      and RogueEssence.DiagManager.Instance ~= nil
      and RogueEssence.DiagManager.Instance.DevMode
  end,
  IsDevLua = function()
    return RogueEssence ~= nil and RogueEssence.DiagManager ~= nil
      and RogueEssence.DiagManager.Instance ~= nil
      and RogueEssence.DiagManager.Instance.DebugLua
  end,
  GroundAIShowDebugInfo = false,
}

local function socket_core_disponible()
  if package ~= nil and package.preload ~= nil and package.preload['socket.core'] ~= nil then
    return true
  end
  if package ~= nil and package.searchpath ~= nil and type(package.cpath) == 'string' and package.cpath ~= '' then
    local ok, chemin = pcall(package.searchpath, 'socket.core', package.cpath)
    if ok and chemin ~= nil then
      return true
    end
  end
  return false
end

if DEBUG.IsDevLua() and socket_core_disponible() then
  local ok, mob = pcall(require, 'mobdebug')
  if ok and mob ~= nil then
    ___mobdebug = mob
    ___mobdebug.coro()
    ___mobdebug.checkcount = 1
    ___mobdebug.verbose = true
    ___mobdebug.start()
    DEBUG.EnableDbgCoro = function() ___mobdebug.on() end
  end
end
