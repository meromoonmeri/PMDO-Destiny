-- Statut « none » neutre modifié uniquement dans le banc isolé ; l'intégration
-- nécessitera un statut visuel dédié, proprement enregistré dans le jeu.
local patati_hp_avant = nil
local patati_cible = nil
local function masquer(ch)
 if not ch.StatusEffects:ContainsKey('none') then
  ch.StatusEffects:Add('none',RogueEssence.Dungeon.StatusEffect('none'))
  ch:UpdateFrame()
  return true
 end
 return false
end
local function reveler(ch,ajoute)
 if ajoute then ch.StatusEffects:Remove('none');ch:UpdateFrame() end
end
function BATTLE_SCRIPT.Patati_Charge(owner,ownerChar,context,args)
 local c=context.User
 local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('Charm',1),1)
 a:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(a,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Charm');GAME:WaitFrames(24)
end
function BATTLE_SCRIPT.PatatiV3_Abysse(owner,ownerChar,context,args)
 local user,target=context.User,context.Target
 patati_hp_avant=target.HP;patati_cible=target
 local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('PatatiV3_Abysse',1),1)
 a:SetupEmitted(RogueElements.Loc(target.CharLoc.X*24+12,target.CharLoc.Y*24+12),0,target.CharDir)
 DUNGEON:PlayVFXAnim(a,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Shadow_Force');GAME:WaitFrames(20)
 local ht=masquer(target);local hu=masquer(user)
 GAME:WaitFrames(65)
 -- La cible ressort visuellement ; les dégâts ne sont pas annulés.
 reveler(target,ht);GAME:WaitFrames(15);reveler(user,hu)
 GAME:WaitFrames(20)
end
function BATTLE_SCRIPT.PatatiV3_ChanceKO(owner,ownerChar,context,args)
 local target=context.Target
 if target==patati_cible and patati_hp_avant and target.HP>0 and target.HP<patati_hp_avant then
  local jet=_DATA.Save.Rand:Next(1000)
  PrintInfo('[PATATI V3 KO] tirage='..jet..'/1000')
  if jet==0 then
   PrintInfo('[PATATI V3 KO] DECLENCHE')
   TASK:WaitTask(target:InflictDamage(-1,true,false))
  end
 end
 patati_hp_avant=nil;patati_cible=nil
end
