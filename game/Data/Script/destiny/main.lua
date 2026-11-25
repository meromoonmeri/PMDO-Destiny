--[[
  main.lua — namespace `destiny`

  Charge de facon persistante par le moteur (LuaEngine : ModDoFile "main") ;
  les require d'ici s'ajoutent a ceux de la base (base/Data/Script/origin/main.lua).
  C'est ici qu'on enregistre les services Lua persistants propres a Destiny.
]]--

--------------------------------------------------------------------------------------------------------------
-- Services Destiny
--------------------------------------------------------------------------------------------------------------
-- Fond anime du menu-titre : mer/ciel JOUR ou NUIT (24 poses) selon l'heure locale,
-- + animation d'ouverture du blason Oeuf Aile une fois par session. Voir docs/MENU_TITRE.md.
require 'destiny.services.destiny_title_anim'
-- Les objets Statue_Kangourex posés dans l'éditeur ouvrent le stockage.
require 'destiny.services.statue_kangourex'
-- Nilo observe le duel de la Fosse Cascade, hors de la simulation de combat.
require 'destiny.services.nilo_temoin'
-- Vestiaire : le quiz fournit exactement les mêmes couples espèce/forme.
require('destiny.rubans').installer()
