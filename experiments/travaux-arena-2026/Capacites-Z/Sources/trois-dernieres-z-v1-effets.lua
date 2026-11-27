-- Prototype séquentiel isolé. Suspension temporaire des talents ; non sûre à intégrer.
local sauve={}
local function lance(c,nom,layer,frames)
 local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData(nom,1),1)
 a:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir);DUNGEON:PlayVFXAnim(a,layer);GAME:WaitFrames(frames)
end
local function charge(context,tag,son)
 assert(sauve[tag]==nil,'Suspension précédente non nettoyée')
 SOUND:PlayBattleSE(son);lance(context.User,tag..'V1_Charge',RogueEssence.Content.DrawLayer.Front,54)
end
local function ignore(context,tag,breche)
 local t=context.Target;sauve[tag]={cible=t,etat=t.IntrinsicDisabled};t.IntrinsicDisabled=true
 PrintInfo('['..tag..' TALENT] suspendu='..tostring(t.IntrinsicDisabled))
 if breche then SOUND:PlayBattleSE('DUN_Flash_Cannon');lance(t,'HelioV1_Breche',RogueEssence.Content.DrawLayer.Front,54) end
end
local function restaure(tag)
 local s=sauve[tag];if s then s.cible.IntrinsicDisabled=s.etat;PrintInfo('['..tag..' TALENT] restaure='..tostring(s.cible.IntrinsicDisabled));sauve[tag]=nil end
end
function BATTLE_SCRIPT.SeleneV1_Charge(o,c,ctx,a) charge(ctx,'Selene','DUN_Shadow_Ball') end
function BATTLE_SCRIPT.SeleneV1_Ignore(o,c,ctx,a) ignore(ctx,'Selene',true) end
function BATTLE_SCRIPT.SeleneV1_Restaure(o,c,ctx,a) restaure('Selene') end
function BATTLE_SCRIPT.ApocalypseV1_Charge(o,c,ctx,a) charge(ctx,'Apocalypse','DUN_Charge_Beam') end
function BATTLE_SCRIPT.ApocalypseV1_Ignore(o,c,ctx,a) ignore(ctx,'Apocalypse',false) end
function BATTLE_SCRIPT.ApocalypseV1_Restaure(o,c,ctx,a) restaure('Apocalypse') end
function BATTLE_SCRIPT.FaucheV1_Charge(o,c,ctx,a) charge(ctx,'Fauche','DUN_Shadow_Force') end
function BATTLE_SCRIPT.ApocalypseV1_Categorie(o,c,ctx,a)
 -- Approximation testable : statistiques affichées sans paliers ni talents modificateurs.
 local kind=luanet.import_type('RogueEssence.Data.BattleData+SkillCategory')
 if ctx.User.Atk>ctx.User.MAtk then ctx.Data.Category=kind.Physical else ctx.Data.Category=kind.Magical end
 PrintInfo('[Apocalypse CATEGORIE] atk='..ctx.User.Atk..' matk='..ctx.User.MAtk..' categorie='..tostring(ctx.Data.Category))
end
