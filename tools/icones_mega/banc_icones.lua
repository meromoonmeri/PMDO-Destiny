-- Instrumentation du banc PMDO, jamais installée dans Destiny.
local rows, pages = __ROWS__, __PAGES__
local addon, destiny, riddle, lang = __ADDON__, __DESTINY__, __RIDDLE__, __LANG__
local q = {}
local graphics = luanet.import_type('RogueEssence.Content.GraphicsManager')
local path = luanet.import_type('RogueEssence.PathMod')
local text = luanet.import_type('RogueEssence.Text')
local data = luanet.import_type('RogueEssence.Data.DataManager')
local types = luanet.import_type('RogueEssence.Data.DataManager+DataType')
local function log(s) PrintInfo('QA_ICONE '..s) end
local function clean()
  for i=GAME:GetPlayerBagCount()-1,0,-1 do GAME:TakePlayerBagItem(i,true) end
end
local function go()
  GAME:CutsceneMode(false)
  GAME:FadeIn(10)
  GAME:WaitFrames(20)
  local font = text.ModLangPath(path.ModPath('Content/Font/text.font'))
  local file = lang=='zh-hans' and 'text.zh-hans.font' or 'text.font'
  assert(font:sub(-#file)==file,font)
  local priority = addon and 'Mega_Stones_Reverie' or 'Destiny'
  assert(font:find('MODS/'..priority..'/Content/Font/',1,true),font)
  log('FONT '..priority..'/'..file..' lang='..lang)
  local index=data.Instance.DataIndices[types.Item]
  assert(index:Get('food_apple').Icon==2 and index:Get('berry_oran').Icon==3 and index:Get('gummi_blue').Icon==6,'index stock/gummis')
  if not addon then assert(not index:ContainsKey('mega_venusaurite')) end
  if not destiny then assert(index:Get('berry_pecha').Icon==3 and data.Instance:GetItem('berry_pecha').Sprite=='') end
  for _,v in ipairs(rows) do
    local id, icon, name, w, h=v[1],v[2],v[3],v[4],v[5]
    local datum=data.Instance:GetItem(id)
    local display=tostring(RogueEssence.Dungeon.InvItem(id):GetDisplayName())
    local glyph=utf8.char(0xe0a0+icon)
    assert(index:Get(id).Icon==icon and datum.Icon==icon and datum.Sprite==name,id)
    assert(display:sub(1,#glyph)==glyph and tostring(datum:GetIconName()):sub(1,#glyph)==glyph,id)
    assert(graphics.TextFont:SubstringWidth(glyph)==11,id..' glyph width')
    local source=path.ModPath('Content/Item/'..name..'.dir')
    local folder=id:sub(1,5)=='mega_' and 'Mega_Stones_Reverie' or 'Destiny'
    assert(source:find('MODS/'..folder..'/Content/Item/',1,true),source)
    local sheet=graphics.GetItem(name)
    assert(sheet.TileWidth==w and sheet.TileHeight==h and sheet.TotalFrames==1,id..' dir')
    if v[6] then
      -- Même méthode que le panneau de description du vrai ItemSummary.
      local description = tostring(datum.Desc:ToLocal())
      assert(description==v[6],id..' description '..lang..' : '..description)
      log('DESCRIPTION '..id..' '..description)
    end
    log(string.format('ITEM %s Icon=%d %s %dx%d Released=%s',id,icon,name,w,h,tostring(datum.Released)))
  end
  local native=UI
  if riddle then
    clean()
    SV.Destiny={FoyersReverie={}}
    local actor=RogueEssence.Dungeon.CharData()
    actor.BaseForm=RogueEssence.Dungeon.MonsterID('geodude',0,'normal',Gender.Female)
    actor.Nickname='Miette'
    actor.Level=5
    local hero=CH('PLAYER')
    local miette=GROUND:CreateCharacterFromCharData('Foyer_Miette',RogueEssence.Dungeon.Character(actor),hero.Position.X+32,hero.Position.Y,Direction.Left)
    AI:DisableCharacterAI(miette)
    local mdl=require 'destiny.reverie_foyers'
    local foyer=mdl.Carte('pierre')
    local ui = setmetatable({}, {__index=function(_,k)
      return function(_,...) return native[k](native,...) end
    end})
    function ui:WaitShowDialogue(s)
      if s:sub(1,#'Reçu : ')=='Reçu : ' then log('RECIPIENT '..s);else log('DIALOG') end
      return native:WaitShowDialogue(s)
    end
    function ui:BeginChoiceMenu(...) log('CHOICE');return native:BeginChoiceMenu(...) end
    UI=ui
    local before=GAME:GetPlayerBagCount()
    foyer.Foyer_Miette_Action(miette,hero)
    assert(SV.Destiny.FoyersReverie.pierre.EnigmeResolue and SV.Destiny.FoyersReverie.pierre.EnigmeCadeau=='berry_pecha','devinette/état')
    assert(GAME:GetPlayerBagCount()==before+1 and GAME:GetPlayerBagItem(before).ID=='berry_pecha','objet donné')
    log('GIFT_ONE berry_pecha')
    foyer.Foyer_Miette_Action(miette,hero)
    assert(GAME:GetPlayerBagCount()==before+1,'cadeau en double')
    log('GIFT_ONCE berry_pecha')
    UI=native
  end
  for i,page in ipairs(pages) do
    clean()
    for _,id in ipairs(page) do GAME:GivePlayerItem(id,1,false,'') end
    assert(GAME:GetPlayerBagCount()==#page)
    UI:SetCustomMenu(RogueEssence.Menu.ItemMenu(-2,0))
    log('BAG '..i)
    UI:WaitForChoice()
    GAME:WaitFrames(14)
  end
  log('DONE '..#rows..' '..#pages)
end
function q.GameLoad(map)
  if q.once then return end
  q.once=true
  local ok,err=pcall(go)
  if not ok then log('FAIL '..tostring(err)) end
end
q.Enter=q.GameLoad
return q
