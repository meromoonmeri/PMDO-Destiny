-- Repères en pixels monde du *hall* (pas le sceau de l'arène annexe).
-- Les sprites ground ont une emprise de 16×16 ; le point des pieds est +8,+12.
local M = {X=384, Y=270}
local PAS, TAILLE = 8, 16
local directions = {{0,8}, {-8,0}, {8,0}, {0,-8}}

function M.Place(cote)
  return {X=M.X-8+cote*12, Y=M.Y-12}
end

local function chevauche(x, y, r)
  return r and math.abs(x-r.X) < TAILLE and math.abs(y-r.Y) < TAILLE
end

function M.Libre(map, x, y, kaito, autre)
  -- Le parcours ne peut emprunter ni les seuils nord ni la sortie sud.
  if x < 0 or x+TAILLE > map.TexWidth*PAS or y < 152 or y+TAILLE > math.min(560,map.TexHeight*PAS) then
    return false
  end
  if chevauche(x,y,kaito) or chevauche(x,y,autre) then return false end
  for a = math.floor(x/PAS), math.floor((x+TAILLE-1)/PAS) do
    for b = math.floor(y/PAS), math.floor((y+TAILLE-1)/PAS) do
      if map:GetObstacle(a,b) ~= 0 then return false end
    end
  end
  return true
end

-- MoveToPosition est cinématique et ignore les collisions moteur. On vérifie
-- le couloir entier (y compris le raccord hors grille) avant de lancer la marche.
function M.Trajet(map, depart, but, kaito, autre)
  if chevauche(depart.X,depart.Y,autre) then autre=nil end -- un suiveur passable peut partir du même point
  local function relier(x,y,a,b)
    local n = math.max(math.abs(a-x), math.abs(b-y))
    for p = 1, math.max(1,n) do
      local t = n == 0 and 0 or p/n
      local xx,yy=x+(a-x)*t,y+(b-y)*t
      for u=math.floor(xx),math.ceil(xx) do
        for v=math.floor(yy),math.ceil(yy) do
          if not M.Libre(map,u,v,kaito,autre) then return false end
        end
      end
    end
    return true
  end
  if not M.Libre(map,but.X,but.Y,kaito,autre) then return nil end
  if relier(depart.X,depart.Y,but.X,but.Y) then return {but} end
  local file, vus = {{X=depart.X,Y=depart.Y}}, {}
  local function cle(x,y) return x+y*(map.TexWidth*PAS) end
  vus[cle(depart.X,depart.Y)] = true
  local i = 1
  while i <= #file do
    local p = file[i]; i = i+1
    if math.abs(but.X-p.X)<PAS and math.abs(but.Y-p.Y)<PAS and relier(p.X,p.Y,but.X,but.Y) then
      local chemin = {but}
      while p.Precedent do
        local q, r = p.Precedent, chemin[1]
        -- Fusionner les pas successifs en lignes droites.
        if not ((q.X==p.X and p.X==r.X) or (q.Y==p.Y and p.Y==r.Y)) then
          table.insert(chemin,1,{X=p.X,Y=p.Y})
        end
        p=q
      end
      return chemin
    end
    for _, d in ipairs(directions) do
      local x,y = p.X+d[1],p.Y+d[2]
      local id = cle(x,y)
      if not vus[id] and relier(p.X,p.Y,x,y) then
        vus[id] = true
        file[#file+1] = {X=x,Y=y,Precedent=p}
      end
    end
  end
  return nil
end

return M
