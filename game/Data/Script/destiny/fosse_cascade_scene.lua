-- Les deux cartes partagent la terrasse. Le ground positionne un collider
-- 16×16 ; le sprite témoin de l’arène est ancré sur le centre correspondant.
local fosse = {SALLE_X = 48, NILO_TERRASSE = {x = 304, y = 152}}
fosse.ARENE = 'end_grotte_verdoyante'
fosse.NILO_ARENE = {
  x = fosse.NILO_TERRASSE.x + 8 - fosse.SALLE_X,
  y = fosse.NILO_TERRASSE.y + 8,
}
return fosse
