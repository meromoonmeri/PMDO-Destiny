-- Stockage Kangourex (statue-relais), à la manière du rocher Kangourex de Halcyon.
--
-- Un seul point d'entrée pour les deux façons de poser une statue :
--   * le script de carte (ewc3_entree_waterfall_cave) appelle OuvrirStockage()
--     après son éventuelle explication ;
--   * le service destiny.services.statue_kangourex raccorde les statues posées
--     dans l'éditeur puis appelle OuvrirStockage() si la carte ne l'a pas fait.
--
-- Le drapeau deja_ouvert garantit qu'une interaction n'ouvre qu'un menu, même
-- quand les deux chemins se superposent (le service appelle d'abord le script
-- de carte, qui peut avoir déjà ouvert le stockage).
local statue = {}

statue.deja_ouvert = false

-- Ouvre le stockage PMDO : entreposer un objet, retirer un objet, tout
-- entreposer, gérer l'argent de l'équipe. Le menu boucle jusqu'à « Annuler ».
function statue.OuvrirStockage()
  statue.deja_ouvert = true
  UI:ResetSpeaker()
  COMMON.ShowTeamStorageMenu()
  return true
end

-- Appelé au début de chaque interaction par le service.
function statue.Reinitialiser()
  statue.deja_ouvert = false
end

return statue
