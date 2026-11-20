-- Les deux cartes partagent la terrasse. Le ground positionne un collider
-- 16×16 ; le sprite témoin de l’arène est ancré sur le centre correspondant.
local fosse = {SALLE_X = 48, NILO_TERRASSE = {x = 304, y = 152}}
fosse.ARENE = 'end_grotte_verdoyante'
fosse.NILO_ARENE = {
  x = fosse.NILO_TERRASSE.x + 8 - fosse.SALLE_X,
  y = fosse.NILO_TERRASSE.y + 8,
}
-- Implantation de la confrontation au centre de la salle haute, deux cases
-- au nord de la version précédente. Les quatre départs alliés restent libres.
fosse.DUEL = {
  boss={x=10,y=8}, hero={x=10,y=10}, partenaire={x=9,y=10},
}

-- Cases et directions de MapTeams. Le premier déplacement longe le duo ;
-- le second coupe vers lui. Les arrière-gardes pivotent pour fermer le passage.
fosse.GARDE = {
  {nom='Kabuto_Flanc_G', x=8,  y=9, face='DownRight', avance='DownRight',
    depart={205,202}, passage={212,224}, menace={226,224}, delai=4, attente=48, recul={-6,-4}, signal=true},
  {nom='Kabuto_Flanc_D', x=11, y=9, face='DownLeft', avance='DownLeft',
    depart={362,200}, passage={352,225}, menace={338,224}, delai=23, attente=43, recul={6,-4}},
  {nom='Kabuto_Arriere_G', x=9,  y=12, face='Up', avance='UpRight',
    depart={242,293}, passage={259,306}, menace={263,301}, delai=69, attente=24, recul={-3,7}, signal=true},
  {nom='Kabuto_Arriere_D', x=10, y=12, face='Up', avance='UpLeft',
    depart={320,293}, passage={301,306}, menace={297,301}, delai=84, attente=20, recul={3,7}},
}

function fosse.AncreAuSol(case)
  -- Centre de la case (24 px), décalage de la salle haute, demi-collider.
  return case.x * 24 + 12 + fosse.SALLE_X - 8, case.y * 24 + 12 - 8
end

return fosse
