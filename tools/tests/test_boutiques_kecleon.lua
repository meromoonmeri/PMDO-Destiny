local root = assert(arg[1])
local shop = assert(loadfile(root .. '/game/Data/Script/destiny/boutiques_kecleon.lua'))()
local argent, limite, sac, equipes, journal, choix, derniere_liste
local function item_data(id)
  if id:match('^wand_') or id:match('^ammo_') then return {Released=true, MaxStack=9, Price=5} end
  return {Released=true, MaxStack=0, Price=id == 'food_apple' and 10 or 50}
end
local function objet(id, maudit, nombre)
  return {ID=id, Amount=nombre, Cursed=maudit, GetSellValue=function(self)
    local data = item_data(self.ID)
    return data.Price * (data.MaxStack > 1 and self.Amount or 1)
  end}
end
RogueEssence = {Dungeon={InvItem=objet}}
_DATA = {
  GetItem=function(_, id) return item_data(id) end,
  Save={ActiveTeam={GetMaxInvSlots=function(_, zone) assert(zone == 'reverie'); return limite end}},
}
_ZONE = {CurrentZone='reverie'}
GAME = {
  GetPlayerMoney=function() return argent end,
  AddToPlayerMoney=function(_, n) argent=argent+n end,
  RemoveFromPlayerMoney=function(_, n) argent=argent-n end,
  GetPlayerBagCount=function() return #sac end,
  GetPlayerEquippedCount=function() local n=0; for _ in pairs(equipes) do n=n+1 end; return n end,
  GetPlayerBagItem=function(_, slot) return sac[slot+1] end,
  GetPlayerEquippedItem=function(_, slot) return equipes[slot] end,
  TakePlayerBagItem=function(_, slot, tout) assert(tout); table.remove(sac,slot+1) end,
  TakePlayerEquippedItem=function(_, slot, tout) assert(tout); equipes[slot]=nil end,
  GivePlayerItem=function(_, id, n, maudit)
    local data=item_data(id)
    if data.MaxStack > 1 then
      for _, o in ipairs(sac) do
        if o.ID==id and o.Cursed==maudit then
          local q=math.min(n,data.MaxStack-o.Amount)
          o.Amount=o.Amount+q; n=n-q
        end
      end
    end
    if n>0 then assert(#sac < limite and n <= math.max(data.MaxStack, 1)); sac[#sac+1]=objet(id,maudit,n) end
  end,
}
local function event(s) journal[#journal+1] = s end
UI = {
  SetSpeaker=function() end, ResetSpeaker=function() end, SetSpeakerEmotion=function() end,
  WaitShowDialogue=function(_, s) event(s) end, WaitForChoice=function() end,
  BeginChoiceMenu=function(_, _, options, defaut, annuler)
    assert(options[1]=='Acheter' and options[2]=='Vendre' and options[3]=='Infos' and options[4]=='Quitter')
    assert(defaut==1 and annuler==4); event('choix')
  end,
  ChoiceMenuYesNo=function(_, t, defaut) assert(defaut==false); event(t) end,
  ShopMenu=function(_, catalogue) assert(#catalogue>0); derniere_liste=catalogue; event('ShopMenu') end,
  SellMenu=function() event('SellMenu') end,
  ChoiceResult=function() assert(#choix>0,'sortie de boutique non atteinte'); return table.remove(choix,1) end,
}
SOUND = {PlayBattleSE=function(_, s) event(s) end}
local function jouer(cle, actions)
  choix, journal = actions, {}
  shop.Ouvrir({},cle)
  assert(#choix==0,'choix non consommés')
end
local function vu(motif)
  for _, ligne in ipairs(journal) do if ligne:find(motif, 1, true) then return true end end
  return false
end
local function copie(o)
  if type(o)~='table' then return o end
  local t={}; for k,v in pairs(o) do t[k]=copie(v) end; return t
end
local function signature(s)
  local t={}; for _,a in ipairs(s.Articles) do t[#t+1]=a.Index end; return table.concat(t,',')
end

-- Migration du vieux catalogue sans changer Joliflor ; étals indépendants.
local joliflor={Jour=0,Articles={{Index='gummi_green',Amount=1,Price=350}}}
SV={Destiny={StocksKecleon={vert={Jour=0,Articles={}},violet={Jour=0,Articles={{Index='food_apple'}}},bellossom=joliflor}}}
local v,z=shop.Stock('vert'),shop.Stock('violet')
assert(v.Jour==0 and z.Jour==0 and #v.Articles==8 and #z.Articles==6)
assert(SV.Destiny.StocksKecleon.bellossom==joliflor)
local sv0=copie(SV)
for jour=1,16 do
  local avant, apres = signature(shop.Stock('violet')), signature(shop.Stock('vert'))
  SV.Destiny.JourneeVille=jour
  z,v=shop.Stock('violet'),shop.Stock('vert')
  assert(v.Articles[1].Index=='food_apple' and v.Articles[1].Price==50)
  assert(v.Articles[3].Index=='berry_oran' and v.Articles[7].Amount==9)
  assert(#v.Articles==8 and signature(v)~=apres and #z.Articles==6 and signature(z)~=avant)
  assert(z.Articles[1].Index:match('^tm_'))
  for i=2,4 do assert(z.Articles[i].Index:match('^orb_')) end
  for i=5,6 do
    local lot=z.Articles[i]; assert(lot.Index:match('^wand_') and lot.Amount==4 and lot.Price==100)
  end
end
SV=copie(sv0); v,z=shop.Stock('vert'),shop.Stock('violet')

-- Refuser, manquer de Poké, puis avoir un sac trop petit ne retire rien.
argent,limite,sac,equipes=10000,12,{},{}
local prix=v.Articles[1].Price+v.Articles[2].Price
jouer('vert',{1,{2,1},false,4}); assert(argent==10000 and #sac==0 and #v.Articles==8)
argent=prix-1
jouer('vert',{1,{2,1},4}); assert(vu('manque des Poké') and argent==prix-1 and #v.Articles==8)
argent,limite=10000,1
jouer('vert',{1,{2,1},4}); assert(vu('place dans votre sac') and argent==10000 and #v.Articles==8 and #sac==0)

-- Le panier natif peut revenir dans le désordre : retirer les bons indices.
limite=12
local id2=v.Articles[2].Index
jouer('vert',{1,{2,1},true,4})
assert(vu('DUN_Money') and argent==10000-prix and #sac==2 and #v.Articles==6 and #z.Articles==6)
assert(sac[1].ID==id2 and sac[2].ID=='food_apple' and v.Articles[1].Index=='berry_oran')
SV=copie(SV); v=shop.Stock('vert'); assert(#v.Articles==6 and v.Articles[1].Index=='berry_oran')

-- Un lot de baguettes peut compléter une pile sans place libre.
local lot=z.Articles[5]; sac={objet(lot.Index,false,5)}; limite=1
jouer('violet',{1,{5},true,4}); assert(#sac==1 and sac[1].Amount==9)
z=shop.Stock('violet'); assert(#z.Articles==5)

-- Vente d'une pile complète et de son équipement en une seule transaction.
sac[2]=objet('food_apple',false,1); sac[3]=objet('berry_oran',false,1)
equipes[0]=objet('held_cover_band',false,1)
local demandes={{Slot=0,IsEquipped=false},{Slot=2,IsEquipped=false},{Slot=0,IsEquipped=true}}
local a=argent
jouer('violet',{2,demandes,false,4}); assert(argent==a and #sac==3 and equipes[0])
jouer('violet',{2,demandes,true,4})
assert(vu('SellMenu') and argent==a+45+50+50 and #sac==1 and sac[1].ID=='food_apple' and not equipes[0])
assert(#z.Articles==5, 'une vente ne remet pas de stock')

-- Rupture de stock persistée, avec accès aux infos et vente maintenu.
local indices={1,2,3,4,5}; limite=12
jouer('violet',{1,indices,true,1,3,4})
assert(#z.Articles==0 and vu('étal est épuisé') and vu('Café Spinda'))
SV=copie(SV); assert(#shop.Stock('violet').Articles==0)
assert(#shop.Stock('vert').Articles==6)
SV.Destiny.JourneeVille=1
assert(#shop.Stock('violet').Articles==6 and #shop.Stock('vert').Articles==8)
assert(SV.Destiny.StocksKecleon.bellossom.Articles[1].Price==350)
print('PASS Zig / Zag : lots, achats, ventes, sauvegarde, rupture, réassort et Joliflor isolé')
