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
  IntroReveilHerosFait = false, ProvisionsDepartDonnees = false,
  PartenaireParti = false, RetourAccompli = false, LostWoodTrip = nil,
  LostWoodTutorialDone = false, LostWoodReturnTutorialDone = false,
  HeroAssemblyIndex = nil, FinaleDestiny = false,
}
