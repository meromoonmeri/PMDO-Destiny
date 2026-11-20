-- Les deux cartes partagent la terrasse. Le ground positionne un collider
-- 16×16 ; le sprite témoin de l’arène est ancré sur le centre correspondant.
local fosse = {SALLE_X = 48, NILO_TERRASSE = {x = 304, y = 152}}
fosse.ARENE = 'end_grotte_verdoyante'
fosse.NILO_ARENE = {
  x = fosse.NILO_TERRASSE.x + 8 - fosse.SALLE_X,
  y = fosse.NILO_TERRASSE.y + 8,
}
-- Les cases sont celles de MapTeams dans end_grotte_verdoyante.rsmap.
-- Laisser libres les quatre départs natifs de l'équipe, même avec des recrues.
-- Les directions sont les noms Dir8 ; la carte utilise leurs valeurs natives.
fosse.GARDE = {
  {nom='Kabuto_Flanc_G', x=8,  y=11, face='DownRight', depart={220,244}, pas={230,254}, delai=3,  signal=true},
  {nom='Kabuto_Flanc_D', x=11, y=11, face='DownLeft',  depart={340,244}, pas={331,253}, delai=17},
  {nom='Kabuto_Arriere_G', x=9,  y=14, face='Up', depart={268,366}, pas={268,355}, delai=42, signal=true},
  {nom='Kabuto_Arriere_D', x=10, y=14, face='Up', depart={292,369}, pas={292,358}, delai=54},
}

function fosse.AncreAuSol(case)
  -- Centre de la case (24 px), décalage de la salle haute, demi-collider.
  return case.x * 24 + 12 + fosse.SALLE_X - 8, case.y * 24 + 12 - 8
end

return fosse
