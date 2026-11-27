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
 local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('PatatiV5_Yeux',1),1)
 a:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(a,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Charm');GAME:WaitFrames(60)
end
function BATTLE_SCRIPT.PatatiV5_Sac(owner,ownerChar,context,args)
 local user,target=context.User,context.Target
 patati_hp_avant=target.HP;patati_cible=target
 local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('PatatiV5_Sac',1),1)
 a:SetupEmitted(RogueElements.Loc(target.CharLoc.X*24+12,target.CharLoc.Y*24+12),0,target.CharDir)
 DUNGEON:PlayVFXAnim(a,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Shadow_Force')
 local ht=masquer(target);local hu=masquer(user)
 PrintInfo('[PATATI V5 VISUEL] debut cible_masquee='..tostring(target.StatusEffects:ContainsKey('none'))..' mimiqui_masque='..tostring(user.StatusEffects:ContainsKey('none')))
 GAME:WaitFrames(100)
 PrintInfo('[PATATI V5 VISUEL] fin_costume cible_masquee='..tostring(target.StatusEffects:ContainsKey('none'))..' mimiqui_masque='..tostring(user.StatusEffects:ContainsKey('none')))
 GAME:WaitFrames(20)
 reveler(target,ht);reveler(user,hu)
 PrintInfo('[PATATI V5 VISUEL] reapparition cible='..tostring(not target.StatusEffects:ContainsKey('none'))..' mimiqui='..tostring(not user.StatusEffects:ContainsKey('none')))

end
function BATTLE_SCRIPT.PatatiV5_ChanceKO(owner,ownerChar,context,args)
 local target=context.Target
 if target==patati_cible and patati_hp_avant and target.HP>0 and target.HP<patati_hp_avant then
  local jet=_DATA.Save.Rand:Next(1000)
  PrintInfo('[PATATI V5 KO] tirage='..jet..'/1000')
  if jet==0 then
   PrintInfo('[PATATI V5 KO] DECLENCHE')
   TASK:WaitTask(target:InflictDamage(-1,true,false))
  end
 end
 patati_hp_avant=nil;patati_cible=nil
end
