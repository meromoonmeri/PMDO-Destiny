-- Valeurs ajoutées par Destiny après les valeurs PMDO de base.
-- Ne pas réinitialiser SV ici : la base origin l'a déjà créé.
SV.checkpoint = {
  Zone = 'destiny_hub', Segment = -1,
  Map = 0, Entry = 0,
}
SV.destiny = {
  Welcomed = false,
}

-- Drapeaux du scénario (arena/64113588) : les scripts testent toujours `SV.Destiny ~= nil`,
-- la table est simplement pré-créée ici.
SV.Destiny = SV.Destiny or {
  PartenaireParti = false, RetourAccompli = false, LostWoodTrip = nil,
  LostWoodTutorialDone = false, HeroAssemblyIndex = nil, FinaleDestiny = false,
  PrologueHeros = nil, TeamDazzlingRencontree = false,
  LostWoodRetry = nil, LostWoodCause = nil,
  LostWoodEchecsAller = 0, LostWoodEchecsRetour = 0,
  PenseesReveilVues = false, JourneeVille = 0, StocksKecleon = {},
  MomentScenario = nil, MomentReverie = nil,
  -- Recrutement et Noigrumes restent indisponibles jusqu’à l’Assemblée /
  -- la boutique des Zones d’Accueil (voir destiny.recrutement).
  RecrutementDebloque = false,
}
